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

METADATA_SCHEMA = """
[메타데이터 스키마]
- '고유번호': 각 사용자의 고유 식별 번호 (문자열)
- '성별': 사용자의 성별 (예: '남성', '여성')
- '나이': 사용자의 만 나이 (숫자)
- '지역_시도': 거주 지역 (시/도) (예: '서울', '경기')
- '지역_시군구': 거주 지역 (시/군/구) (예: '영등포구')
- '결혼여부': 결혼 상태 (예: '기혼', '미혼')
- '자녀수': 자녀의 수 (숫자)
- '자녀유무': 자녀 유무 (예: '있음', '없음')
- '가족수': 총 가족 인원 (예: '1명', '2명')
- '최종학력': 최종 학력 (예: '대학교 졸업')
- '직업': 사용자의 직업 (예: '사무직', '전업주부')
- '직무': 사용자의 직무 (예: 'IT', '마케팅/광고/홍보/조사')
- '월평균_개인소득': 월평균 개인 소득 (예: '월 200~299만원')
- '월평균_가구소득': 월평균 가구 소득
- '보유휴대폰단말기_브랜드': 사용 중인 휴대폰 브랜드 (예: '삼성전자 (갤럭시, 노트)')
- '보유전자제품_요약': 보유 중인 전자제품 요약 (예: '노트북, 태블릿PC, 스마트워치')
- '보유휴대폰모델명': 사용 중인 휴대폰 모델명 (예: '갤럭시 S21', '아이폰 13')
- '자동차모델': 보유 중인 자동차 모델명 (예: '싼타페', '모닝')
- '보유차량여부': 차량 보유 여부 (예: '있다', '없다')
- '자동차제조사': 보유 차량의 제조사 (예: '현대', '기아')
- '흡연경험_요약': 흡연 경험 요약 (예: '과거에 피운 적 있음', '현재 피우고 있음')
- '흡연경험_담배브랜드_요약': 흡연 경험 담배 브랜드 요약 (예: '에쎄', '말보로')
- '궐련형_전자담배_경험': 궐련형 전자담배 사용 경험 (예: '사용해본 경험 있음', '사용해본 경험 없음')
- '음용경험_술_요약': 술 음용 경험 요약 (예: '과거에 음용한 적 있음', '현재 음용하고 있음')
- '기억에_남는_일': 기억에 남는 일 (예: '겨울방학 숙제를 하던 순간')
- '기분_좋아지는_소비_요약': 기분 좋아지는 소비 유형 요약
- '반려동물_경험유무': 반려동물 양육 경험 유무 (1.0 = 경험 있음)
- '반려동물_경험': 반려동물 양육 경험 (예: '현재 키우고 있음', '과거에 키워본 경험 있음')
- '이사_스트레스_요인': 이사 시 스트레스 요인
- '이사_스트레스_여부': 이사 시 스트레스 여부 (1.0 = 스트레스 받음)
- '많이사용하는앱': 가장 많이 사용하는 앱 (예: '쇼핑/중고거래 앱')
- '운동': 현재 하고 있는 운동 (예: '헬스', '달리기/걷기', '없음')
- '카테고리': 선호하는 운동
- '체력_관리_유무': 헬스/운동 등을 통한 체력 관리 여부 (예: '있다', '없다')
- 'ott사용개수': 현재 이용 중인 유료 OTT 개수 (예: '1개', '2개', '없다')
- 'ott사용중': OTT 서비스 이용 여부 (예: '사용중이다', '사용하지않는다')
- '방문빈도': 전통시장 방문 빈도 (예: '주1회 이상')
- '전통시장_방문': 전통시장 방문 여부 (예: '방문함')
- '선호선물': 선호하는 선물 종류
- '설 선호선물있음': 설에 선호하는 선물 유무 (예: '있다')
- '여행스타일': 본인의 여행 스타일
- '노력_유형_요약': 환경 보호를 위한 노력 유형 요약
- '친환경_노력_여부': 일회용품 줄이기 노력 여부 (예: '노력함')
- '포인트_신경쓰는_정도': 포인트/적립금 신경쓰는 정도 (예: '매우 꼼꼼하게 챙긴다')
- '초콜릿_섭취_상황': 초콜릿 섭취 상황 (예: '스트레스를 받을 때', '기분이 좋을 때')
- '초콜릿_섭취_여부': 초콜릿 섭취 여부 (1.0 = 섭취함)
- '보호_습관_요약': 개인정보 보호 습관 요약 (예: '비밀번호 주기적 변경', '2단계 인증 사용')
- '개인정보보호_노력여부': 개인정보보호 노력 여부 (예: '노력함')
- '여름패션필수템_요약': 여름철 패션 필수 아이템 요약 (예: '반팔티, 샌들')
- '비올때_대처방법': 우산이 없을 때 비에 대처하는 방법
- '주요_저장_사진': 휴대폰 갤러리에 가장 많은 사진 종류
- '선호_물놀이_장소': 여름철 선호하는 물놀이 장소 (예: '계곡', '워터파크')
- '물놀이_선호여부': 물놀이 선호 여부 (1.0 = 선호함)
- '여름철_걱정거리': 여름철 걱정거리 (예: '더위와 땀', '냉방병')
- '걱정있음': 여름철 걱정거리 유무 (1.0 = 있음)
- '처리방법_요약': 버리기 아까운 물건 처리 방법 (예: '중고로 판매')
- '알람_방식': 아침 기상 시 알람 설정 방식
- '혼밥_빈도': 혼자 식사하는 빈도 (예: '주 2~3회 정도', '거의 하지 않음')
- '혼밥_여부': 혼밥 여부 (1.0 = 혼밥함)
- '행복한_노년의_조건': 행복한 노년을 위해 중요하다고 생각하는 조건
- '땀_불편함_요약": 여름철 땀으로 인한 불편함 요약
- '효과적인_다이어트_방법': 효과적인 다이어트 방법
- '아침식사_방식': 아침 식사 방식 (예: '배달 주문', '직접 조리')
- '여름철_최애_간식': 여름철 최애 간식 종류
- '최애간식_있음': 여름철 최애 간식 유무 (1.0 = 있음)
- '최대_지출처': 최근 가장 지출을 많이 한 곳 (예: '배달비')
- 'AI_활용_분야_요약': AI를 활용하는 분야 요약
- 'AI_사용여부': AI 서비스 사용 여부 (예: '사용함', '사용 안 함')
- '소비성향': 본인의 소비 성향 (예: '미니멀리스트')
- '스트레스_요인': 주요 스트레스 요인
- '스트레스_해소법': 스트레스 해소 방법 (예: '수면', '명상/휴식')
- '피부만족도_요약': 현재 피부 상태 만족도 (예: '보통이다', '불만족한다')
- '스킨케어_한달_소비금액': 스킨케어 월 소비 금액
- '구매_고려_요소': 스킨케어 제품 구매 시 고려 요소
- '사용_경험_요약': AI 챗봇 사용 경험 요약
- '주요_사용_챗봇': 주로 사용하는 AI 챗봇 (예: 'ChatGPT', '사용해본 경험 없음')
- '활용_용도': AI 챗봇 활용 용도 (예: '개인 비서 (일정 관리, 메모)')
- '선호_서비스': 선호하는 AI 챗봇
- '희망_여행지_요약': 희망하는 여행지 유형 요약
- '해외여행_희망여부': 해외여행 희망 여부 (예: '희망함')
- '빠른배송_이용제품': 빠른 배송 서비스로 주로 이용하는 제품 유형
- '빠른배송_이용여부': 빠른 배송 서비스 이용 여부 (예: '이용함')
"""

# (★★★ 시스템 프롬프트 (쿼리 분석용) 전역 정의 ★★★)
system_prompt = f"""
당신은 사용자의 자연어 쿼리를 분석하여 ChromaDB에서 사용할 수 있는 JSON 필터와 의미 검색어로 분리하는 '쿼리 분석 전문가'입니다.

[규칙]
1.  쿼리를 분석할 때, 반드시 아래 [메타데이터 스키마]를 참고하여 정확한 '필터 키'(key)와 '정확히 일치하는 값'(value)을 매핑하세요.
    (예: "남성" -> {{"성별": "남성"}}, "30대" -> 나이 필터)
{METADATA_SCHEMA}
2.  '나이' 필터는 항상 $gte(이상), $lt(미만) 2개로 분리하여 '$and' 리스트에 포함시키세요.
3.  '지역_시도'나 '직업' 등 여러 값이 '$in'으로 묶일 수 있습니다.
4.  (수정) 필터 조건이 2개 이상일 때만 ChromaDB의 '$and' 연산자 리스트로 묶으세요.
5.  (수정) 필터 조건이 1개일 경우, '$and' 없이 딕셔너리만 사용하세요. (예: {{"직업": "사무직"}})
6.  (수정) 만약 필터 조건이 없다면 "filters" 키의 값은 반드시 null 로 응답하세요.
7.  (수정) 사용자가 "30명", "10개" 등 명시적인 개수를 언급하면 "limit" 키로 해당 숫자를 추출하세요. "모두", "전체" 등을 언급하면 "limit"를 "all"로 설정하세요. 개수 언급이 없으면 "all"을 기본값으로 하세요.
8.  'semantic_query'는 **[메타데이터 스키마]의 '키'에 정확히 매핑되는 단어(예: '남성', '30대', '서울', '사무직')를 제외한, 사용자의 모든 핵심 의도**를 포함해야 합니다.
    (예: "던힐을 펴본", "소주 마셔본", "노트북 보유한", "TV를 소유한", "담배 아이코스를 펴본" 등)
9.  오직 JSON 객체 형식으로만 응답해야 합니다.
10. [중요] 응답은 반드시 "{" 로 시작하고 "}" 로 끝나야 합니다. 어떤 설명이나 인사말도 JSON 앞뒤에 붙이지 마세요.

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

[예시 2] (★★★ 수정 ★★★)
입력: "서울, 경기에 사는 전업주부"
출력: {{
    "filters": {{
        "$and": [
            {{"지역_시도": {{"$in": ["서울", "경기"]}}}},
            {{"직업": "전업주부"}}
        ]
    }},
    "semantic_query": "서울 또는 경기에 거주하는 전업주부",
    "limit": "all"
}}

[예시 3] (★★★ 수정 ★★★)
입력: "40대 남성"
출력: {{
    "filters": {{
        "$and": [
            {{"나이": {{"$gte": 40}}}},
            {{"나이": {{"$lt": 50}}}},
            {{"성별": "남성"}}
        ]
    }},
    "semantic_query": "40대 남성",
    "limit": "all"
}}

[예시 4] (★★★ 수정 ★★★)
입력: "환경 보호에 관심 있는 사람"
출력: {{
    "filters": null,
    "semantic_query": "환경 보호에 관심 있는 사람",
    "limit": "all"
}}

[예시 5]
입력: "자동차를 소유하고 있는 10명"
출력: {{
    "filters": {{"보유차량여부": "있다"}},
    "semantic_query": "자동차를 소유하고 있는 사람",
    "limit": 10
}}

[예시 6]
입력: "운동하는 20대 남성 모두 뽑아줘"
출력: {{
    "filters": {{
        "$and": [
            {{"나이": {{"$gte": 20}}}},
            {{"나이": {{"$lt": 30}}}},
            {{"성별": "남성"}},
            {{"체력_관리_유무": "있다"}}
        ]
    }},
    "semantic_query": "운동하는 20대 남성",
    "limit": "all"
}}

[예시 7]
입력: "아이폰 쓰는 50대 남성 10명"
출력: {{
    "filters": {{   
        "$and": [
            {{"나이": {{"$gte": 50}}}},
            {{"나이": {{"$lt": 60}}}},
            {{"성별": "남성"}},
            {{"보유휴대폰단말기_브랜드": "애플(아이폰)"}}
        ]
    }},
    "semantic_query": "아이폰을 사용하는 50대 남성",
    "limit": 10
}}  

[예시 8]
입력: "소주를 마셔본 경험이 있는 남성 5명"
출력: {{
    "filters": {{"성별": "남성"}},
    "semantic_query": "소주를 마셔본 경험이 있는 사람",
    "limit": 5
}}
"""

# --- 1. "엔진" 3가지 로드 (서버가 켜질 때 1번만 실행) ---
try:
    # 1-1. LLM (Sonnet)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
    llm_client = anthropic.Anthropic(api_key=api_key)
    LLM_MODEL = "claude-sonnet-4-5" 
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
    
    # (★★★ 1. 질문 분석 - LLM 1차 호출 ★★★)
    print("⏳ 1. LLM으로 쿼리 분석 중...")
    
    try:
        analysis_message = llm_client.messages.create(
            model=LLM_MODEL,
            max_tokens=800,
            temperature=0.0, 
            system=system_prompt, # (수정된 프롬프트 사용)
            messages=[{"role": "user", "content": f"입력: \"{user_query}\""}]
        )
        analysis_text = analysis_message.content[0].text
        
        print(f"   - LLM 원본 응답: {analysis_text}") 
        json_start = analysis_text.find('{')
        json_end = analysis_text.rfind('}')
        if json_start != -1 and json_end != -1:
            analysis_json_str = analysis_text[json_start:json_end+1]
        else:
            raise ValueError("LLM 응답에서 JSON 객체를 찾을 수 없습니다.")

        analysis_result = json.loads(analysis_json_str)
        filters = analysis_result.get("filters") 
        semantic_query = analysis_result.get("semantic_query", user_query)
        # (★★★ 수정: 기본값을 "all"로 변경 ★★★)
        limit = analysis_result.get("limit", "all") 
        
        if filters and "$and" in filters and len(filters["$and"]) == 1:
            print("   - (Info) $and 래퍼 제거: 단일 필터입니다.")
            filters = filters["$and"][0]
        elif not filters: 
            filters = None
        
        print(f"   - (수정된) 추출된 필터: {filters}")
        print(f"   - 의미 검색어: {semantic_query}")
        print(f"   - 요청 개수 (limit): {limit}") 

    except Exception as e:
        print(f"   ❌ 쿼리 분석 실패: {e}. 필터 없이 의미 검색만 시도합니다.")
        filters = None 
        semantic_query = user_query
        limit = "all" # (★★★ 수정: 기본값을 "all"로 변경 ★★★)
    
    # (★★★ 2. 검색어 벡터화 ★★★)
    print("⏳ 2. 검색어 벡터화 중 (KURE-v1)...")
    query_vector = embedding_model.encode([semantic_query])[0].tolist()

    # (★★★ 3. DB 검색 - "limit" 값에 따라 분기 ★★★)
    if limit == "all":
        # --- 3A: "모두" 검색 (전체 검색 + 유사도 임계값) ---
        print(f"⏳ 3. ChromaDB 하이브리드 검색 중 (전체 대상)...")
        try:
            total_items_in_db = collection.count()
            if total_items_in_db == 0:
                raise ValueError("DB에 데이터가 없습니다.")
            
            print(f"   - DB의 총 {total_items_in_db}개 항목을 대상으로 검색합니다.")
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=total_items_in_db, 
                where=filters,
                include=["metadatas", "documents", "ids", "distances"]
            )
            
            SIMILARITY_THRESHOLD = 0.5 
            
            final_docs = []
            final_metadatas = []
            final_ids = []
            
            if results.get('ids', [[]])[0]: 
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i]
                    if distance <= SIMILARITY_THRESHOLD:
                        final_docs.append(results['documents'][0][i])
                        final_metadatas.append(results['metadatas'][0][i])
                        final_ids.append(results['ids'][0][i])

            print(f"   - DB 검색 결과 (필터 만족): {len(results['ids'][0])}개")
            print(f"   - 최종 결과 (유사도 {SIMILARITY_THRESHOLD} 이하): {len(final_docs)}개 찾음.")
            
            found_docs = final_docs
            found_metadatas = final_metadatas
            found_ids = final_ids

        except Exception as e:
            print(f"   ⚠️ DB 검색 오류 발생 (include='ids' 실패 추정): {e}. 'ids' 없이 재시도합니다.")
            try:
                results = collection.query(
                    query_embeddings=[query_vector],
                    n_results=total_items_in_db, 
                    where=filters,
                    include=["metadatas", "documents", "distances"] # (ids 제거)
                )
                SIMILARITY_THRESHOLD = 0.5 
                final_docs = []
                final_metadatas = []
                final_ids = []
                if results.get('ids', [[]])[0]: 
                    for i in range(len(results['ids'][0])):
                        distance = results['distances'][0][i]
                        if distance <= SIMILARITY_THRESHOLD:
                            final_docs.append(results['documents'][0][i])
                            final_metadatas.append(results['metadatas'][0][i])
                            final_ids.append(results['ids'][0][i])
                print(f"   - DB 검색 재시도 (필터 만족): {len(results['ids'][0])}개")
                print(f"   - 최종 결과 (유사도 {SIMILARITY_THRESHOLD} 이하): {len(final_docs)}개 찾음.")
                found_docs = final_docs
                found_metadatas = final_metadatas
                found_ids = final_ids
            except Exception as e2:
                print(f"   ❌ DB 검색 재시도 실패: {e2}")
                raise HTTPException(status_code=500, detail=f"DB 검색 오류: {e2}")
    
    else:
        # --- 3B: "상위 N개" 검색 (limit 숫자 사용) ---
        print(f"⏳ 3. ChromaDB 하이브리드 검색 중 (상위 {limit}개)...")
        try:
            try:
                n_limit = int(limit)
            except ValueError:
                print(f"   ⚠️ (경고) LLM이 반환한 limit 값 '{limit}'가 숫자가 아니므로 5로 고정합니다.")
                n_limit = 5
                
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=n_limit, 
                where=filters,
                include=["metadatas", "documents", "ids"] 
            )
            found_docs = results.get('documents', [[]])[0]
            found_metadatas = results.get('metadatas', [[]])[0]
            found_ids = results.get('ids', [[]])[0] 
            print(f"   - DB 검색 결과 (필터 만족 & 유사도 상위): {len(found_docs)}개 찾음.")

        except Exception as e:
            print(f"   ⚠️ DB 검색 오류 발생 (include='ids' 실패 추정): {e}. 'ids' 없이 재시도합니다.")
            try:
                results = collection.query(
                    query_embeddings=[query_vector],
                    n_results=n_limit,
                    where=filters,
                    include=["metadatas", "documents"] # (ids 제거)
                )
                found_docs = results.get('documents', [[]])[0]
                found_metadatas = results.get('metadatas', [[]])[0]
                found_ids = results.get('ids', [[]])[0] 
                print(f"   - DB 검색 재시도 성공 (상위 {len(found_docs)}개) 찾음.")
            except Exception as e2:
                print(f"   ❌ DB 검색 재시도 실패: {e2}")
                raise HTTPException(status_code=500, detail=f"DB 검색 오류: {e2}")

    # (★★★ 3.5. '고유번호' 및 1/0 값 텍스트 변환 ★★★)
    print("⏳ 3.5. 메타데이터 변환 중...")
    
    binary_to_text_map = {
        '반려동물_경험유무': {1: '있음', 0: '없음'},
        '이사_스트레스_여부': {1: '스트레스 받음', 0: '스트레스 안 받음'},
        '초콜릿_섭취_여부': {1: '섭취함', 0: '섭취 안 함'},
        '물놀이_선호여부': {1: '선호함', 0: '선호 안 함'},
        '걱정있음': {1: '있음', 0: '없음'},
        '혼밥_여부': {1: '혼밥함', 0: '혼밥 안 함'},
        '최애간식_있음': {1: '있음', 0: '없음'},
        '설 선호선물있음': {1: '있음', 0: '없음'}
    }
    
    transformed_metadatas = []
    for i in range(len(found_ids)):
        new_meta = found_metadatas[i].copy() 
        new_meta['고유번호'] = found_ids[i] 

        for key, mapping in binary_to_text_map.items():
            if key in new_meta:
                value = new_meta[key]
                if value == 1 or value == 1.0:
                    new_meta[key] = mapping[1]
                elif value == 0 or value == 0.0:
                    new_meta[key] = mapping[0]
        transformed_metadatas.append(new_meta)
    
    found_metadatas = transformed_metadatas 
    print("   - 메타데이터 변환 완료.")

    # (★★★ 4. 답변 생성 - LLM 2차 호출 (RAG) ★★★)
    print("⏳ 4. LLM으로 최종 답변 생성 중 (Sonnet)...")
    if not found_docs:
        final_answer = "해당 조건에 맞는 사용자를 찾지 못했습니다."
        print(f"   - 최종 답변: {final_answer}")
    else:
        try:
            MAX_CONTEXT_ITEMS = 20 
            if len(found_docs) > MAX_CONTEXT_ITEMS:
                print(f"   ⚠️ 검색 결과({len(found_docs)}개)가 너무 많아 {MAX_CONTEXT_ITEMS}개만 요약에 사용합니다.")
                found_docs_for_context = found_docs[:MAX_CONTEXT_ITEMS]
                found_metadatas_for_context = found_metadatas[:MAX_CONTEXT_ITEMS]
            else:
                found_docs_for_context = found_docs
                found_metadatas_for_context = found_metadatas
            
            context_items = []
            for i in range(len(found_docs_for_context)):
                doc_text = found_docs_for_context[i]
                meta_text = json.dumps(found_metadatas_for_context[i], ensure_ascii=False) 
                user_id = found_metadatas_for_context[i].get('고유번호', 'ID정보없음')
                context_items.append(
                    f"문서 {i+1}:\n"
                    f"- 고유번호: {user_id}\n"
                    f"- 요약문: {doc_text}\n"
                    f"- 메타데이터: {meta_text}"
                )
            context_str = "\n\n".join(context_items)
            
            final_prompt = f"""당신은 검색 결과를 요약하여 답변하는 어시스턴트입니다.
사용자의 질문은 '{user_query}'였습니다.
이 질문에 대해 DB에서 찾은 {len(found_docs)}개의 참고 자료는 다음과 같습니다.

[참고 자료]
{context_str}

[지시]
위 [참고 자료]를 바탕으로 사용자의 질문에 대해 자연스러운 문장으로 요약하여 답변해주세요.
총 몇 명을 찾았는지 반드시 언급하세요. (예: "'{user_query}' 조건에 맞는 {len(found_docs)}명의 사용자를 찾았습니다. 이들은 주로...")
각 인물을 설명할 때, **반드시 '고유번호'를 (고유번호: [번호]) 형식으로 먼저 언급**해주세요.
절대로 참고 자료에 없는 내용을 지어내지 마세요.
"""
            message = llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=1500,
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