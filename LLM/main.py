import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import anthropic
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path
import json
import numpy as np

# --- 0. .env 로드 및 기본 설정 ---
load_dotenv()
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 

print("--- 1. 엔진 로드 시작 ---")

# (★★★ 2단계와 동일하게 "필터 재료" 목록 정의 ★★★)
METADATA_COLUMNS_LIST = [
    '성별', '나이', '지역_시도', '지역_시군구', '결혼여부', '자녀수', '자녀유무', 
    '가족수', '최종학력', '직업', '직무', '월평균_개인소득', '월평균_가구소득', 
    '보유휴대폰단말기_브랜드', '보유차량여부', '자동차제조사', '반려동물_경험', 
    '반려동물_경험유무', '이사_스트레스_여부', '많이사용하는앱', '운동', '카테고리', 
    '체력_관리_유무', 'ott사용개수', 'ott사용중', '방문빈도', '전통시장_방문', 
    '설 선호선물있음', '여행스타일', '친환경_노력_여부', '포인트_신경쓰는_정도', 
    '초콜릿_섭취_여부', '개인정보보호_노력여부', '비올때_대처방법', '주요_저장_사진', 
    '선호_물놀이_장소', '물놀이_선호여부', '걱정있음', '처리방법_요약', '알람_방식', 
    '혼밥_빈도', '혼밥_여부', '행복한_노년의_조건', '아침식사_방식', 
    '최애간식_있음', '최대_지출처', 'AI_사용여부', '소비성향', '스트레스_해소법', 
    '피부만족도_요약', '스킨케어_한달_소비금액', '구매_고려_요소', '주요_사용_챗봇', 
    '선호_서비스', '해외여행_희망여부', '빠른배송_이용여부'
]

# --- 1. "엔진" 3가지 로드 (서버가 켜질 때 1번만 실행) ---
try:
    # 1-1. LLM (Sonnet)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
    llm_client = anthropic.Anthropic(api_key=api_key)
    LLM_MODEL = "claude-sonnet-4-5" # (사용 가능한 최신 Sonnet 모델 ID)
    print(f"✅ LLM ({LLM_MODEL}) 클라이언트 초기화 완료.")

    # 1-2. 임베딩 모델 (KURE-v1)
    model_name = 'nlpai-lab/KURE-v1' 
    embedding_model = SentenceTransformer(model_name)
    print(f"✅ 임베딩 모델 '{model_name}' 로드 완료.")

    # 1-3. 벡터 DB (ChromaDB)
    db_path = str(base_dir / 'panel_vector_db') 
    if not os.path.exists(db_path):
         raise FileNotFoundError(f"'{db_path}' 폴더를 찾을 수 없습니다. 2단계(embed) 스크립트를 먼저 실행하세요.")
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_collection(name="panel_collection")
    print(f"✅ ChromaDB '{db_path}' 연결 완료 (총 {collection.count()}개 데이터).")

except Exception as e:
    print(f"❌ 엔진 로드 중 치명적 오류 발생: {e}")
    exit()

print("--- 2. API 서버 설정 ---")

app = FastAPI()

# --- 2. API 입출력 모델 정의 ---
class SearchQuery(BaseModel):
    query: str 

class SearchResponse(BaseModel):
    answer: str  
    source_documents: list 
    source_metadata: list 

# --- 3. "하이브리드 검색" RAG API 엔드포인트 ---
@app.post("/search", response_model=SearchResponse)
def hybrid_search(search_query: SearchQuery):
    user_query = search_query.query
    print(f"\n--- 쿼리 접수: {user_query} ---")
    
    # (★★★ 1. 질문 분석 - LLM 1차 호출 (프롬프트 강화) ★★★)
    print("⏳ 1. LLM으로 쿼리 분석 중...")
    
    valid_keys = ", ".join(METADATA_COLUMNS_LIST)
    
    # (★★★ 프롬프트 대폭 수정 ★★★)
    system_prompt = f"""
당신은 사용자의 자연어 쿼리를 분석하여 ChromaDB에서 사용할 수 있는 JSON 필터, 의미 검색어, 검색 결과 개수(limit)로 분리하는 '쿼리 분석 전문가'입니다.

[규칙]
1.  사용 가능한 필터 키는 다음 리스트로 엄격히 제한됩니다: [{valid_keys}]
2.  '나이' 필터는 항상 $gte(이상), $lt(미만) 2개로 분리하여 '$and' 리스트에 포함하세요. (예: 30대 -> {{"나이": {{"$gte": 30}}}}, {{"나이": {{"$lt": 40}}}})
3.  '지역_시도'나 '직업' 등 여러 값이 '$in'으로 묶일 수 있습니다. (예: 서울, 경기 -> {{"지역_시도": {{"$in": ["서울", "경기"]}}}})
4.  'OTT 이용'은 'ott사용중' 키를 '사용중이다'로 필터링하세요.
5.  사용자가 "30명", "10개" 등 개수를 명시하면 "limit" 키로 추출하세요. 없으면 5를 기본값으로 하세요.
6.  'semantic_query'는 필터링 키워드를 제외한, 사용자의 핵심 의도를 나타내는 문장으로 생성하세요.
7.  오직 JSON 형식으로만 응답해야 합니다.

[예시 1]
입력: "운동 좋아하고 OTT 보는 30대 남성 사무직 10명"
출력: {{
    "filters": {{
        "$and": [
            {{"나이": {{"$gte": 30}}}},
            {{"나이": {{"$lt": 40}}}},
            {{"성별": "남성"}},
            {{"직업": "사무직"}},
            {{"ott사용중": "사용중이다"}}
        ]
    }},
    "semantic_query": "운동을 좋아하고 OTT를 시청하는 사람",
    "limit": 10
}}

[예시 2]
입력: "서울, 경기에 사는 전업주부"
출력: {{
    "filters": {{
        "$and": [
            {{"지역_시도": {{"$in": ["서울", "경기"]}}}},
            {{"직업": "전업주부"}}
        ]
    }},
    "semantic_query": "서울 또는 경기에 거주하는 전업주부",
    "limit": 5
}}
"""
    
    try:
        analysis_message = llm_client.messages.create(
            model=LLM_MODEL,
            max_tokens=500,
            temperature=0.0, 
            system=system_prompt,
            messages=[{"role": "user", "content": f"입력: \"{user_query}\""}]
        )
        analysis_text = analysis_message.content[0].text
        
        # (★★★ 수정: LLM 응답에서 JSON만 추출 ★★★)
        print(f"   - LLM 원본 응답: {analysis_text}") 
        json_start = analysis_text.find('{')
        json_end = analysis_text.rfind('}')
        if json_start != -1 and json_end != -1:
            analysis_json_str = analysis_text[json_start:json_end+1]
        else:
            raise ValueError("LLM 응답에서 JSON 객체를 찾을 수 없습니다.")

        analysis_result = json.loads(analysis_json_str)
        filters = analysis_result.get("filters", {})
        semantic_query = analysis_result.get("semantic_query", user_query)
        limit = analysis_result.get("limit", 5) # (★★★ 수정: limit 값 추출 ★★★)
        
        if not filters: 
            filters = None 
        
        print(f"   - 추출된 필터: {filters}")
        print(f"   - 의미 검색어: {semantic_query}")
        print(f"   - 요청 개수: {limit}")

    except Exception as e:
        print(f"   ❌ 쿼리 분석 실패: {e}. 필터 없이 의미 검색만 시도합니다.")
        filters = None 
        semantic_query = user_query
        limit = 5 # (★★★ 수정: 실패 시 기본 limit ★★★)
    
    # (★★★ 2. 검색어 벡터화 ★★★)
    print("⏳ 2. 검색어 벡터화 중 (KURE-v1)...")
    query_vector = embedding_model.encode([semantic_query])[0].tolist()

    # (★★★ 3. DB 검색 - ChromaDB 하이브리드 쿼리 (수정) ★★★)
    print(f"⏳ 3. ChromaDB 하이브리드 검색 중 (상위 {limit}개)...")
    try:
        # (★★★ 수정: n_results에 limit 사용, 유사도 임계값 제거 ★★★)
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=limit, # LLM이 추출한 'limit' 개수만큼만 검색
            where=filters    # (1번에서 추출한 필터 적용!)
        )
        found_docs = results.get('documents', [[]])[0]
        found_metadatas = results.get('metadatas', [[]])[0]
        print(f"   - DB 검색 결과 (필터 만족 & 유사도 상위): {len(found_docs)}개 찾음.")

    except Exception as e:
        print(f"   ❌ DB 검색 오류: {e}")
        raise HTTPException(status_code=500, detail=f"DB 검색 오류: {e}")

    # (★★★ 4. 답변 생성 - LLM 2차 호출 (RAG) ★★★)
    print("⏳ 4. LLM으로 최종 답변 생성 중 (Sonnet)...")
    if not found_docs:
        final_answer = "해당 조건에 맞는 사용자를 찾지 못했습니다."
        print(f"   - 최종 답변: {final_answer}")
    else:
        try:
            # (★★★ 수정: 이제 found_docs는 'limit' 개수만큼만 들어옴 ★★★)
            context_str = "\n\n".join([f"문서 {i+1}:\n{doc}" for i, doc in enumerate(found_docs)])
            
            final_prompt = f"""당신은 검색 결과를 요약하여 답변하는 어시스턴트입니다.
사용자의 질문은 '{user_query}'였습니다.
이 질문에 대해 DB에서 찾은 {len(found_docs)}명의 참고 자료는 다음과 같습니다.

[참고 자료]
{context_str}

[지시]
위 [참고 자료]를 바탕으로 사용자의 질문에 대해 자연스러운 문장으로 요약하여 답변해주세요.
(예: "총 {len(found_docs)}명의 관련자를 찾았습니다. 이들은 주로...")
절대로 참고 자료에 없는 내용을 지어내지 마세요.
"""
            message = llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=500,
                temperature=0.1, 
                messages=[{"role": "user", "content": final_prompt}]
            )
            final_answer = message.content[0].text
        except Exception as e:
            print(f"   ❌ 답변 생성 실패: {e}")
            final_answer = f"답변 생성 중 오류 발생: {e}"
    
    print(f"   - 최종 답변: {final_answer}")

    return SearchResponse(
        answer=final_answer,
        source_documents=found_docs,
        source_metadata=found_metadatas
    )

# --- 5. 서버 실행 ---
if __name__ == "__main__":
    print("🚀 FastAPI 서버를 http://127.0.0.1:8000 에서 실행합니다.")
    print("   API 테스트 주소: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)