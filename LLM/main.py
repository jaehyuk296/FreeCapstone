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
from typing import Optional, List, Dict, Any, Union

# ============================================================================
# Configuration
# ============================================================================

class Config:
    """애플리케이션 설정"""
    LLM_MODEL = "claude-sonnet-4-5"
    EMBEDDING_MODEL = "nlpai-lab/KURE-v1"
    DB_COLLECTION_NAME = "panel_collection"
    SIMILARITY_THRESHOLD = 0.5
    MAX_CONTEXT_ITEMS = 20
    DEFAULT_LIMIT = "all"
    
    # LLM 파라미터
    ANALYSIS_MAX_TOKENS = 800
    ANALYSIS_TEMPERATURE = 0.0
    ANSWER_MAX_TOKENS = 1500
    ANSWER_TEMPERATURE = 0.1

# ============================================================================
# Schema Definitions
# ============================================================================

METADATA_FILTER_SCHEMA = """
[필터링 가능한 메타데이터 스키마 (정확히 일치)]
- '고유번호': 각 사용자의 고유 식별 번호 (문자열)
- '성별': 사용자의 성별 (예: '남성', '여성')
- '나이': 사용자의 만 나이 (숫자, $gte/$lt 사용)
- '지역_시도': 거주 지역 (시/도) (예: '서울', '경기', '$in' 사용 가능)
- '지역_시군구': 거주 지역 (시/군/구) (예: '영등포구')
- '결혼여부': 결혼 상태 (예: '기혼', '미혼')
- '자녀유무': 자녀 유무 (예: '있음', '없음')
- '가족수': 총 가족 인원 (예: '1명', '2명')
- '최종학력': 최종 학력 (예: '대학교 졸업')
- '직업': 사용자의 직업 (예: '사무직', '전업주부', '$in' 사용 가능)
- '월평균_개인소득': 월평균 개인 소득 (예: '월 200~299만원')
- '월평균_가구소득': 월평균 가구 소득
- '보유휴대폰단말기_브랜드': 사용 중인 휴대폰 브랜드 (예: '애플(아이폰)')
- '보유차량여부': 차량 보유 여부 (예: '있다', '없다')
- '자동차제조사': 보유 차량의 제조사 (예: '현대', '기아')
- '체력_관리_유무': 헬스/운동 등을 통한 체력 관리 여부 (예: '있다', '없다')
- 'ott사용개수': 현재 이용 중인 유료 OTT 개수 (예: '1개', '2개', '없다')
- 'ott사용중': OTT 서비스 이용 여부 (예: '사용중이다', '사용하지않는다')
- '전통시장_방문': 전통시장 방문 여부 (예: '방문함')
- '친환경_노력_여부': 일회용품 줄이기 노력 여부 (예: '노력함')
- '개인정보보호_노력여부': 개인정보보호 노력 여부 (예: '노력함')
- '물놀이_선호여부': 물놀이 선호 여부 (1.0 = 선호함, 0.0 = 선호 안 함)
- '혼밥_여부': 혼밥 여부 (1.0 = 혼밥함, 0.0 = 혼밥 안 함)
- 'AI_사용여부': AI 서비스 사용 여부 (예: '사용함', '사용 안 함')
- '빠른배송_이용여부': 빠른 배송 서비스 이용 여부 (예: '이용함')
- '반려동물_경험유무': 반려동물 양육 경험 유무 (1.0 = 경험 있음)
- '이사_스트레스_여부': 이사 시 스트레스 여부 (1.0 = 스트레스 받음)
- '설 선호선물있음': 설에 선호하는 선물 유무 (예: '있다')
- '초콜릿_섭취_여부': 초콜릿 섭취 여부 (1.0 = 섭취함)
- '걱정있음': 여름철 걱정거리 유무 (1.0 = 있음)
- '혼밥_여부': 혼밥 여부 (1.0 = 혼밥함)
- '최애간식_있음': 여름철 최애 간식 유무 (1.0 = 있음)
- '해외여행_희망여부': 해외여행 희망 여부 (예: '희망함')
"""

METADATA_SEMANTIC_SCHEMA = """
[메타데이터 스키마]
[의미 검색으로 찾아야 할 메타데이터 스키마 (유사도)]
- '직무': 사용자의 직무 (예: 'IT', '마케팅/광고/홍보/조사')
- '보유전자제품_요약': 보유 중인 전자제품 요약 (예: '노트북, 태블릿PC, 스마트워치')
- '보유휴대폰모델명': 사용 중인 휴대폰 모델명 (예: '갤럭시 S21', '아이폰 13')
- '자동차모델': 보유 중인 자동차 모델명 (예: '싼타페', '모닝')
- '흡연경험_요약': 흡연 경험 요약 (예: '과거에 피운 적 있음', '현재 피우고 있음')
- '흡연경험_담배브랜드_요약': 흡연 경험 담배 브랜드 요약 (예: '에쎄', '말보로')
- '궐련형_전자담배_경험': 궐련형 전자담배 사용 경험 (예: '사용해본 경험 있음', '사용해본 경험 없음')
- '음용경험_술_요약': 술 음용 경험 요약 (예: '과거에 음용한 적 있음', '현재 음용하고 있음')
- '기억에_남는_일': 기억에 남는 일 (예: '겨울방학 숙제를 하던 순간')
- '기분_좋아지는_소비_요약': 기분 좋아지는 소비 유형 요약
- '반려동물_경험': 반려동물 양육 경험 (예: '현재 키우고 있음', '과거에 키워본 경험 있음')
- '이사_스트레스_요인': 이사 시 스트레스 요인
- '많이사용하는앱': 가장 많이 사용하는 앱 (예: '쇼핑/중고거래 앱')
- '운동': 현재 하고 있는 운동 (예: '헬스', '달리기/걷기', '없음')
- '카테고리': 선호하는 운동
- '방문빈도': 전통시장 방문 빈도 (예: '주1회 이상')
- '선호선물': 선호하는 선물 종류
- '여행스타일': 본인의 여행 스타일
- '노력_유형_요약': 환경 보호를 위한 노력 유형 요약
- '친환경_노력_여부': 일회용품 줄이기 노력 여부 (예: '노력함')
- '포인트_신경쓰는_정도': 포인트/적립금 신경쓰는 정도 (예: '매우 꼼꼼하게 챙긴다')
- '초콜릿_섭취_상황': 초콜릿 섭취 상황 (예: '스트레스를 받을 때', '기분이 좋을 때')
- '보호_습관_요약': 개인정보 보호 습관 요약 (예: '비밀번호 주기적 변경', '2단계 인증 사용')
- '여름패션필수템_요약': 여름철 패션 필수 아이템 요약 (예: '반팔티, 샌들')
- '비올때_대처방법': 우산이 없을 때 비에 대처하는 방법
- '주요_저장_사진': 휴대폰 갤러리에 가장 많은 사진 종류
- '선호_물놀이_장소': 여름철 선호하는 물놀이 장소 (예: '계곡', '워터파크')
- '여름철_걱정거리': 여름철 걱정거리 (예: '더위와 땀', '냉방병')
- '처리방법_요약': 버리기 아까운 물건 처리 방법 (예: '중고로 판매')
- '알람_방식': 아침 기상 시 알람 설정 방식
- '혼밥_빈도': 혼자 식사하는 빈도 (예: '주 2~3회 정도', '거의 하지 않음')
- '행복한_노년의_조건': 행복한 노년을 위해 중요하다고 생각하는 조건
- '땀_불편함_요약': 여름철 땀으로 인한 불편함 요약
- '효과적인_다이어트_방법': 효과적인 다이어트 방법
- '아침식사_방식': 아침 식사 방식 (예: '배달 주문', '직접 조리')
- '여름철_최애_간식': 여름철 최애 간식 종류
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
- '빠른배송_이용제품': 빠른 배송 서비스로 주로 이용하는 제품 유형
"""

BINARY_FIELD_MAPPING = {
    '반려동물_경험유무': {1: '있음', 0: '없음'},
    '이사_스트레스_여부': {1: '스트레스 받음', 0: '스트레스 안 받음'},
    '초콜릿_섭취_여부': {1: '섭취함', 0: '섭취 안 함'},
    '물놀이_선호여부': {1: '선호함', 0: '선호 안 함'},
    '걱정있음': {1: '있음', 0: '없음'},
    '혼밥_여부': {1: '혼밥함', 0: '혼밥 안 함'},
    '최애간식_있음': {1: '있음', 0: '없음'},
    '설 선호선물있음': {1: '있음', 0: '없음'}
}

# ============================================================================
# Prompt Templates
# ============================================================================

def create_query_analysis_prompt() -> str:
    """쿼리 분석용 시스템 프롬프트 생성"""
    return f"""
당신은 사용자의 자연어 쿼리를 분석하여 ChromaDB에서 사용할 수 있는 JSON 필터와 의미 검색어로 분리하는 '쿼리 분석 전문가'입니다.

[규칙]
1.  쿼리를 분석할 때, 아래 [필터링 가능한 메타데이터 스키마]를 참고하여 **'정확히 일치'**하는 조건만 'filters'로 추출하세요.
{METADATA_FILTER_SCHEMA}
2.  (★★★ 중요 ★★★) 쿼리에 [의미 검색으로 찾아야 할 메타데이터 스키마]에 해당하는 내용(예: '에쎄', '소주', '노트북')이 포함된 경우,
    해당 내용은 'filters'로 만들지 말고, **반드시 'semantic_query' (의미 검색어)에 포함**시키세요.
{METADATA_SEMANTIC_SCHEMA}
3.  '나이' 필터는 항상 $gte(이상), $lt(미만) 2개로 분리하여 '$and' 리스트에 포함시키세요.
4.  '지역_시도'나 '직업' 등 여러 값이 '$in'으로 묶일 수 있습니다.
5.  "고소득자", "저소득자", "젊은 층" 같은 추상적인 개념은 [메타데이터 스키마]를 참고하여 적절한 $gte, $lt, $in 필터로 변환하세요.
    - "젊은 층": '나이' 20대~30대 ({{"$gte": 20}}, {{"$lt": 40}})
    - "고소득자": '월평균_개인소득' (예: {{"월평균_개인소득": {{"$in": ["월 600~699만원", "월 700~799만원", "월 800~899만원", "월 900~999만원", "월 1,000만원 이상"]}}}})
6.  필터 조건이 2개 이상일 때만 ChromaDB의 '$and' 연산자 리스트로 묶으세요.
7.  필터 조건이 1개일 경우, '$and' 없이 딕셔너리만 사용하세요. (예: {{"직업": "사무직"}})
8.  만약 필터 조건이 없다면 "filters" 키의 값은 반드시 null 로 응답하세요.
9.  사용자가 "30명", "10개" 등 명시적인 개수를 언급하면 "limit" 키로 해당 숫자를 추출하세요. "모두", "전체" 등을 언급하면 "limit"를 "all"로 설정하세요. 개수 언급이 없으면 "all"을 기본값으로 하세요.
10.  'semantic_query'는 필터링 키워드를 제외한, 사용자의 모든 핵심 의도를 나타내는 문장으로 생성하세요. 만약 의미 검색어가 없다면 "semantic_query"는 원본 쿼리 텍스트를 그대로 사용하세요.
11.  오직 JSON 객체 형식으로만 응답해야 합니다.
12. [중요] 응답은 반드시 "{" 로 시작하고 "}" 로 끝나야 합니다. 어떤 설명이나 인사말도 JSON 앞뒤에 붙이지 마세요.

[예시 1: 하이브리드 (필터 + 의미 + 개수)]
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

[예시 2: 필터 + 의미]
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

[예시 3: 필터만]
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

[예시 4: 의미만]
입력: "환경 보호에 관심 있는 사람"
출력: {{
    "filters": null,
    "semantic_query": "환경 보호에 관심 있는 사람",
    "limit": "all"
}}

[예시 5: 필터 + 의미]
입력: "노트북을 보유한 남성 10명"
출력: {{
    "filters": {{"성별": "남성"}},
    "semantic_query": "노트북을 보유한 사람",
    "limit": 10
}}

[예시 6: 필터 + 의미]
입력: "스트레스받을 때 초콜릿을 먹는 5명"
출력: {{
    "filters": {{"초콜릿_섭취_여부": 1.0}},
    "semantic_query": "스트레스받을 때 초콜릿을 먹는 사람",
    "limit": 5
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

[예시 9: (개념 매핑 + 의미 검색)]
입력: "데스크톱을 가진 고소득자 남성"
출력: {{
    "filters": {{
        "$and": [
            {{"성별": "남성"}},
            {{"월평균_개인소득": {{"$in": ["월 600~699만원", "월 700~799만원", "월 800~899만원", "월 900~999만원", "월 1,000만원 이상"]}}}}
        ]
    }},
    "semantic_query": "데스크톱(PC)을 보유한 사람",
    "limit": "all"
}}

[예시 10: (복합 의미 검색)]
입력: "소주나 에쎄를 즐기는 20대 남성 모두"
출력: {{
    "filters": {{
        "$and": [
            {{"나이": {{"$gte": 20}}}},
            {{"나이": {{"$lt": 30}}}},
            {{"성별": "남성"}}
        ]
    }},
    "semantic_query": "소주를 마시거나 에쎄 담배를 피우는 사람",
    "limit": "all"
}}

"""

def create_answer_generation_prompt(
    user_query: str,
    found_count: int,
    context_str: str
) -> str:
    """답변 생성용 프롬프트 생성"""
    return f"""당신은 검색 결과를 요약하여 답변하는 어시스턴트입니다.
사용자의 질문은 '{user_query}'였습니다.
이 질문에 대해 DB에서 찾은 {found_count}개의 참고 자료는 다음과 같습니다.

[참고 자료]
{context_str}

[지시]
위 [참고 자료]를 바탕으로 사용자의 질문에 대해 자연스러운 문장으로 요약하여 답변해주세요.
총 몇 명을 찾았는지 반드시 언급하세요. (예: "'{user_query}' 조건에 맞는 {found_count}명의 사용자를 찾았습니다. 이들은 주로...")
각 인물을 설명할 때, **반드시 '고유번호'를 (고유번호: [번호]) 형식으로 먼저 언급**해주세요.
절대로 참고 자료에 없는 내용을 지어내지 마세요.
"""

# ============================================================================
# API Models
# ============================================================================

class SearchQuery(BaseModel):
    query: str

class SearchResponse(BaseModel):
    answer: str
    source_documents: List[str]
    source_metadata: List[Dict[str, Any]]

class CompareRequest(BaseModel):
    caseA: str    # 메인질의
    caseB: str    # 서브질의
    countA: int  # 메인질의 인원

class ComparisonRequest(BaseModel): # 비교 요청 모델
    caseA: Dict[str, Any]
    caseB: Dict[str, Any]

# ============================================================================
# Core Services
# ============================================================================

class EngineManager:
    """LLM, 임베딩 모델, ChromaDB 관리"""
    
    def __init__(self):
        self.llm_client: Optional[anthropic.Anthropic] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.collection: Optional[Any] = None
    
    def initialize(self) -> None:
        """엔진 초기화"""
        print("--- 1. 엔진 로드 시작 ---")
        
        # 환경 변수 로드
        load_dotenv()
        try:
            base_dir = Path(__file__).parent
        except NameError:
            base_dir = Path.cwd()
        
        # LLM 초기화
        self._initialize_llm()
        
        # 임베딩 모델 초기화
        self._initialize_embedding_model()
        
        # ChromaDB 초기화
        self._initialize_chromadb(base_dir)
        
        print("✅ 모든 엔진 로드 완료")
    
    def _initialize_llm(self) -> None:
        """LLM 클라이언트 초기화"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
        
        self.llm_client = anthropic.Anthropic(api_key=api_key)
        print(f"✅ LLM ({Config.LLM_MODEL}) 클라이언트 초기화 완료.")
    
    def _initialize_embedding_model(self) -> None:
        """임베딩 모델 초기화"""
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        print(f"✅ 임베딩 모델 '{Config.EMBEDDING_MODEL}' 로드 완료.")
    
    def _initialize_chromadb(self, base_dir: Path) -> None:
        """ChromaDB 초기화"""
        db_path = str(base_dir / 'panel_vector_db')
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"'{db_path}' 폴더를 찾을 수 없습니다. "
                "2단계(embed) 스크립트를 먼저 실행하세요."
            )
        
        chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = chroma_client.get_collection(
            name=Config.DB_COLLECTION_NAME
        )
        print(
            f"✅ ChromaDB '{db_path}' 연결 완료 "
            f"(총 {self.collection.count()}개 데이터)."
        )


class QueryAnalyzer:
    """쿼리 분석 서비스"""
    
    def __init__(self, llm_client: anthropic.Anthropic):
        self.llm_client = llm_client
        self.system_prompt = create_query_analysis_prompt()
    
    def analyze(self, user_query: str) -> Dict[str, Any]:
        """쿼리를 분석하여 필터와 의미 검색어 추출"""
        print("⏳ 1. LLM으로 쿼리 분석 중...")
        
        try:
            analysis_message = self.llm_client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=Config.ANALYSIS_MAX_TOKENS,
                temperature=Config.ANALYSIS_TEMPERATURE,
                system=self.system_prompt,
                messages=[{"role": "user", "content": f"입력: \"{user_query}\""}]
            )
            
            analysis_text = analysis_message.content[0].text
            print(f"   - LLM 원본 응답: {analysis_text}")
            
            # JSON 추출
            json_str = self._extract_json(analysis_text)
            analysis_result = json.loads(json_str)
            
            # 필터 정규화
            filters = self._normalize_filters(analysis_result.get("filters"))
            semantic_query = analysis_result.get("semantic_query", user_query)
            limit = analysis_result.get("limit", Config.DEFAULT_LIMIT)
            
            print(f"   - 추출된 필터: {filters}")
            print(f"   - 의미 검색어: {semantic_query}")
            print(f"   - 요청 개수 (limit): {limit}")
            
            return {
                "filters": filters,
                "semantic_query": semantic_query,
                "limit": limit
            }
            
        except Exception as e:
            print(f"   ❌ 쿼리 분석 실패: {e}. 필터 없이 의미 검색만 시도합니다.")
            return {
                "filters": None,
                "semantic_query": user_query,
                "limit": Config.DEFAULT_LIMIT
            }
    
    def _extract_json(self, text: str) -> str:
        """텍스트에서 JSON 문자열 추출"""
        json_start = text.find('{')
        json_end = text.rfind('}')
        if json_start == -1 or json_end == -1:
            raise ValueError("LLM 응답에서 JSON 객체를 찾을 수 없습니다.")
        return text[json_start:json_end+1]
    
    def _normalize_filters(self, filters: Optional[Dict]) -> Optional[Dict]:
        """필터 정규화 (단일 $and 래퍼 제거)"""
        if not filters:
            return None
        
        if "$and" in filters and len(filters["$and"]) == 1:
            print("   - (Info) $and 래퍼 제거: 단일 필터입니다.")
            return filters["$and"][0]
        
        return filters


class VectorSearcher:
    """벡터 검색 서비스"""
    
    def __init__(
        self,
        embedding_model: SentenceTransformer,
        collection: Any
    ):
        self.embedding_model = embedding_model
        self.collection = collection
    
    def search(
        self,
        semantic_query: str,
        filters: Optional[Dict],
        limit: Union[str, int]
    ) -> tuple[List[str], List[Dict], List[str]]:
        """하이브리드 검색 수행"""
        # 벡터화
        query_vector = self._vectorize_query(semantic_query)
        
        # limit에 따라 검색 방식 분기
        if limit == "all":
            return self._search_all(query_vector, filters)
        else:
            return self._search_top_n(query_vector, filters, limit)
    
    def _vectorize_query(self, query: str) -> List[float]:
        """검색어 벡터화"""
        print("⏳ 2. 검색어 벡터화 중 (KURE-v1)...")
        return self.embedding_model.encode([query])[0].tolist()
    
    def _search_all(
        self,
        query_vector: List[float],
        filters: Optional[Dict]
    ) -> tuple[List[str], List[Dict], List[str]]:
        """전체 검색 (유사도 임계값 적용)"""
        print("⏳ 3. ChromaDB 하이브리드 검색 중 (전체 대상)...")
        
        try:
            total_items = self.collection.count()
            if total_items == 0:
                raise ValueError("DB에 데이터가 없습니다.")
            
            print(f"   - DB의 총 {total_items}개 항목을 대상으로 검색합니다.")
            
            results = self._query_collection(
                query_vector,
                total_items,
                filters,
                include_ids=True
            )
            
            # 유사도 임계값 필터링
            docs, metadatas, ids = self._filter_by_similarity(results)
            
            print(f"   - DB 검색 결과 (필터 만족): {len(results['ids'][0])}개")
            print(f"   - 최종 결과 (유사도 {Config.SIMILARITY_THRESHOLD} 이하): {len(docs)}개 찾음.")
            
            return docs, metadatas, ids
            
        except Exception as e:
            print(f"   ⚠️ DB 검색 오류 발생: {e}. 'ids' 없이 재시도합니다.")
            return self._search_all_without_ids(query_vector, filters, total_items)
    
    def _search_top_n(
        self,
        query_vector: List[float],
        filters: Optional[Dict],
        limit: Union[str, int]
    ) -> tuple[List[str], List[Dict], List[str]]:
        """상위 N개 검색"""
        try:
            n_limit = int(limit)
        except ValueError:
            print(f"   ⚠️ (경고) limit 값 '{limit}'가 숫자가 아니므로 5로 고정합니다.")
            n_limit = 5
        
        print(f"⏳ 3. ChromaDB 하이브리드 검색 중 (상위 {n_limit}개)...")
        
        try:
            results = self._query_collection(
                query_vector,
                n_limit,
                filters,
                include_ids=True
            )
            
            docs = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            ids = results.get('ids', [[]])[0]
            
            print(f"   - DB 검색 결과 (필터 만족 & 유사도 상위): {len(docs)}개 찾음.")
            
            return docs, metadatas, ids
            
        except Exception as e:
            print(f"   ⚠️ DB 검색 오류 발생: {e}. 'ids' 없이 재시도합니다.")
            return self._search_top_n_without_ids(query_vector, filters, n_limit)
    
    def _query_collection(
        self,
        query_vector: List[float],
        n_results: int,
        filters: Optional[Dict],
        include_ids: bool = True
    ) -> Dict:
        """ChromaDB 쿼리 실행"""
        include_list = ["metadatas", "documents", "distances"]
        if include_ids:
            include_list.append("ids")
        
        return self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=filters,
            include=include_list
        )
    
    def _filter_by_similarity(
        self,
        results: Dict
    ) -> tuple[List[str], List[Dict], List[str]]:
        """유사도 임계값으로 필터링"""
        docs, metadatas, ids = [], [], []
        
        if results.get('ids', [[]])[0]:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i]
                if distance <= Config.SIMILARITY_THRESHOLD:
                    docs.append(results['documents'][0][i])
                    metadatas.append(results['metadatas'][0][i])
                    ids.append(results['ids'][0][i])
        
        return docs, metadatas, ids
    
    def _search_all_without_ids(
        self,
        query_vector: List[float],
        filters: Optional[Dict],
        total_items: int
    ) -> tuple[List[str], List[Dict], List[str]]:
        """ids 없이 전체 검색 재시도"""
        results = self._query_collection(
            query_vector,
            total_items,
            filters,
            include_ids=False
        )
        
        docs, metadatas, ids = self._filter_by_similarity(results)
        print(f"   - DB 검색 재시도 성공: {len(docs)}개 찾음.")
        return docs, metadatas, ids
    
    def _search_top_n_without_ids(
        self,
        query_vector: List[float],
        filters: Optional[Dict],
        n_limit: int
    ) -> tuple[List[str], List[Dict], List[str]]:
        """ids 없이 상위 N개 검색 재시도"""
        results = self._query_collection(
            query_vector,
            n_limit,
            filters,
            include_ids=False
        )
        
        docs = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        ids = results.get('ids', [[]])[0]
        
        print(f"   - DB 검색 재시도 성공: {len(docs)}개 찾음.")
        return docs, metadatas, ids


class MetadataTransformer:
    """메타데이터 변환 서비스"""
    
    @staticmethod
    def transform(
        metadatas: List[Dict],
        ids: List[str]
    ) -> List[Dict]:
        """메타데이터 변환 (고유번호 추가 및 1/0 값 텍스트 변환)"""
        print("⏳ 3.5. 메타데이터 변환 중...")
        
        transformed = []
        for i in range(len(ids)):
            new_meta = metadatas[i].copy()
            new_meta['고유번호'] = ids[i]
            
            # 바이너리 필드 변환
            for key, mapping in BINARY_FIELD_MAPPING.items():
                if key in new_meta:
                    value = new_meta[key]
                    if value in [1, 1.0]:
                        new_meta[key] = mapping[1]
                    elif value in [0, 0.0]:
                        new_meta[key] = mapping[0]
            
            transformed.append(new_meta)
        
        print("   - 메타데이터 변환 완료.")
        return transformed


class AnswerGenerator:
    """답변 생성 서비스"""
    
    def __init__(self, llm_client: anthropic.Anthropic):
        self.llm_client = llm_client
    
    def generate(
        self,
        user_query: str,
        docs: List[str],
        metadatas: List[Dict]
    ) -> str:
        """LLM으로 최종 답변 생성"""
        print("⏳ 4. LLM으로 최종 답변 생성 중 (Sonnet)...")
        
        if not docs:
            answer = "해당 조건에 맞는 사용자를 찾지 못했습니다."
            print(f"   - 최종 답변: {answer}")
            return answer
        
        try:
            # 컨텍스트 준비
            context_str = self._prepare_context(docs, metadatas)
            
            # 프롬프트 생성
            prompt = create_answer_generation_prompt(
                user_query,
                len(docs),
                context_str
            )
            
            # LLM 호출
            message = self.llm_client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=Config.ANSWER_MAX_TOKENS,
                temperature=Config.ANSWER_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = message.content[0].text
            print(f"   - 최종 답변: {answer}")
            return answer
            
        except Exception as e:
            print(f"   ❌ 답변 생성 실패: {e}")
            return f"답변 생성 중 오류 발생: {e}"
    
    def _prepare_context(
        self,
        docs: List[str],
        metadatas: List[Dict]
    ) -> str:
        """컨텍스트 문자열 준비"""
        # 너무 많은 경우 제한
        if len(docs) > Config.MAX_CONTEXT_ITEMS:
            print(
                f"   ⚠️ 검색 결과({len(docs)}개)가 너무 많아 "
                f"{Config.MAX_CONTEXT_ITEMS}개만 요약에 사용합니다."
            )
            docs = docs[:Config.MAX_CONTEXT_ITEMS]
            metadatas = metadatas[:Config.MAX_CONTEXT_ITEMS]
        
        context_items = []
        for i in range(len(docs)):
            user_id = metadatas[i].get('고유번호', 'ID정보없음')
            meta_text = json.dumps(metadatas[i], ensure_ascii=False)
            
            context_items.append(
                f"문서 {i+1}:\n"
                f"- 고유번호: {user_id}\n"
                f"- 요약문: {docs[i]}\n"
                f"- 메타데이터: {meta_text}"
            )
        
        return "\n\n".join(context_items)

class DashboardSummarizer:
    """대시보드 데이터 요약 서비스"""

    def __init__(self, llm_client: anthropic.Anthropic):
        self.llm_client = llm_client

    def generate_summary(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """차트/테이블 데이터를 받아 요약문 생성"""
        print("⏳ 5. 대시보드 데이터 요약 생성 중...")

        # 토큰 절약을 위한 JSON 문자열 변환
        data_str = json.dumps(dashboard_data, ensure_ascii=False)

        system_prompt = """
        당신은 데이터 기반의 의사결정을 지원하는 수석 데이터 분석가입니다.
        제공된 차트 및 테이블 데이터를 바탕으로 웹 대시보드 상단에 표시될 
        '핵심 요약 리포트'를 작성하세요.

        [작성 지침]
        1. 단순 수치 나열보다는 트렌드, 최빈값, 비율 등 '의미'를 해석하여 서술하세요.
        2. "~했습니다", "~높습니다" 등의 정중한 해요/하십시오체를 사용하세요.
        3. 핵심만 추려 3~4문장(한 문단)으로 간결하게 작성하세요.
        4. 마크다운(볼드, 헤더 등) 없이 순수 텍스트(Plain Text)로만 답하세요.
        """

        user_message = f"다음 데이터를 분석하여 요약해 주세요:\n{data_str}"

        try:
            # 기존에 설정된 Config.LLM_MODEL 사용
            message = self.llm_client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=Config.ANALYSIS_MAX_TOKENS, 
                temperature=0.5,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            summary_text = message.content[0].text
            print(f"   - 요약 완료: {summary_text[:30]}...")
            
            return {
                "status": "success",
                "summary": summary_text
            }

        except Exception as e:
            print(f"   ❌ 요약 생성 실패: {e}")
            return {
                "status": "error",
                "summary": "데이터 요약 정보를 불러오는 데 실패했습니다.",
                "error_detail": str(e)
            }

# ============================================================================
# Main Application
# ============================================================================

class RAGService:
    """RAG 서비스 통합 클래스"""
    
    def __init__(self, engine_manager: EngineManager):
        self.llm_client = engine_manager.llm_client
        self.query_analyzer = QueryAnalyzer(engine_manager.llm_client)
        self.vector_searcher = VectorSearcher(
            engine_manager.embedding_model,
            engine_manager.collection
        )
        self.answer_generator = AnswerGenerator(engine_manager.llm_client)
        self.summarizer = DashboardSummarizer(engine_manager.llm_client)
    
    def search(self, user_query: str) -> SearchResponse:
        """하이브리드 검색 실행"""
        print(f"\n--- 쿼리 접수: {user_query} ---")
        
        # 1. 쿼리 분석
        analysis = self.query_analyzer.analyze(user_query)
        
        # 2. 벡터 검색
        docs, metadatas, ids = self.vector_searcher.search(
            analysis["semantic_query"],
            analysis["filters"],
            analysis["limit"]
        )
        
        # 3. 메타데이터 변환
        transformed_metadatas = MetadataTransformer.transform(metadatas, ids)
        
        # 4. 답변 생성
        answer = self.answer_generator.generate(
            user_query,
            docs,
            transformed_metadatas
        )
        
        return SearchResponse(
            answer=answer,
            source_documents=docs,
            source_metadata=transformed_metadatas
        )
    
    # [추가됨] 요약 메서드
    def summarize_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.summarizer.generate_summary(data)
    
    # [추가됨] 비교 분석 메서드
    def compare_with_summary(self, req: CompareRequest) -> Dict[str, Any]:
        """
        A(입력값) vs B(검색값) 비교 후, 요약 및 ID 리스트 반환
        """
        print(f"\n--- 비교 분석 요청: '{req.caseA}'({req.countA}명) vs '{req.caseB}' ---")

        # 1. 집단 B 쿼리 분석 (여기서 '10명' 같은 limit 정보가 추출됨)
        analysis_b = self.query_analyzer.analyze(req.caseB)
        
        # [변경 포인트] "all"로 고정하지 않고, 분석된 limit 값("all" 또는 숫자)을 사용
        limit_b = analysis_b.get("limit", "all")
        print(f"   -> 집단 B 검색 제한(Limit): {limit_b}")

        # 2. 벡터 검색 실행
        _, _, ids_b = self.vector_searcher.search(
            analysis_b["semantic_query"],
            analysis_b["filters"],
            limit=limit_b  # <--- 분석된 limit 적용
        )
        
        # 3. ID 리스트 및 개수 확보
        if ids_b and len(ids_b) > 0:
            id_list_b = ids_b  # 리스트 자체를 가져옴
            count_b = len(id_list_b)
        else:
            id_list_b = []
            count_b = 0
            
        print(f"   -> 집단 B 검색 결과: {count_b}명")

        # 4. LLM 비교 요약 생성
        summary_prompt = f"""
        [데이터]
        - 집단 A ({req.caseA}): {req.countA}명
        - 집단 B ({req.caseB}): {count_b}명

        [지시]
        두 집단의 표본 수를 비교하는 1~2줄의 핵심 요약을 작성하세요.
        정중한 해요체로 작성하세요.
        """

        try:
            message = self.query_analyzer.llm_client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=200,
                temperature=0.5,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary_text = message.content[0].text
        except Exception as e:
            summary_text = f"집단 B({req.caseB})의 인원은 {count_b}명입니다."

        # 5. 결과 반환
        return {
            "caseA": req.caseA,
            "caseB": req.caseB,
            "countA": req.countA,
            "countB": count_b,
            "idsB": id_list_b,
            "summary": summary_text
        }
    
    def generate_comparison_summary(self, req_data: ComparisonRequest) -> Dict[str, str]:
        """
        Case A와 Case B의 그래프 데이터를 받아 비교 요약 생성
        """
        # A와 B의 질의문 추출 (로깅용)
        query_a = req_data.caseA.get("mainQuery", "질의A")
        query_b = req_data.caseB.get("subQuery", "질의B")
        
        print(f"⏳ 심층 비교 분석 중... '{query_a}' vs '{query_b}'")

        # 1. 데이터를 프롬프트에 넣기 좋게 JSON 문자열로 변환
        # (한글 깨짐 방지를 위해 ensure_ascii=False)
        input_json = json.dumps({
            "caseA": req_data.caseA,
            "caseB": req_data.caseB
        }, ensure_ascii=False)

        system_prompt = """
        당신은 데이터 비교 분석 전문가입니다.
        제공된 JSON 데이터는 두 집단(Case A, Case B)의 질의 내용과 그래프 데이터(graphData)입니다.

        [지시사항]
        1. 'graphData' 안의 수치나 항목을 분석하여 두 집단 간의 **가장 두드러진 차이점**을 찾아내세요.
        2. "A집단(질의내용)은 ~인 반면, B집단(질의내용)은 ~입니다." 와 같은 비교 대조 문체를 사용하세요.
        3. 단순 수치 나열은 지양하고, **경향성이나 패턴** 위주로 해석하세요.
        4. 정중한 '해요체'를 사용하여 **2~3문장** 내외로 요약하세요.
        """

        user_message = f"""
        다음 두 집단의 데이터를 비교 분석해 주세요:
        
        {input_json}
        """

        try:
            # LLM 호출
            message = self.llm_client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=300, # 비교 설명이므로 약간 넉넉하게
                temperature=0.5,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            summary_text = message.content[0].text
            print(f"   -> 비교 요약 완료: {summary_text[:30]}...")
            
            return {
                "status": "success",
                "summary": summary_text
            }

        except Exception as e:
            print(f"   ❌ 비교 요약 생성 실패: {e}")
            return {
                "status": "error",
                "summary": "두 집단의 데이터를 비교 분석하는 데 실패했습니다."
            }
    
# ============================================================================
# FastAPI Application
# ============================================================================

# 엔진 초기화 (모듈 로드 시 1회 실행)
print("--- 2. API 서버 설정 ---")
engine_manager = EngineManager()
try:
    engine_manager.initialize()
except Exception as e:
    print(f"❌ 엔진 로드 중 치명적 오류 발생: {e}")
    exit()

# FastAPI 앱 생성
app = FastAPI()

# RAG 서비스 생성
rag_service = RAGService(engine_manager)

# API 엔드포인트 등록
@app.post("/search", response_model=SearchResponse)
def hybrid_search(search_query: SearchQuery):
    try:
        return rag_service.search(search_query.query)
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summary")
def generate_dashboard_summary(data: Dict[str, Any]):
    """
    프론트엔드 차트 데이터를 받아 요약문을 반환하는 엔드포인트
    """
    try:
        return rag_service.summarize_dashboard(data)
    except Exception as e:
        print(f"❌ 요약 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/compare")
def compare_samples(request: CompareRequest):
    """
    Input: { "caseA": "...", "caseB": "...", "countA": 50 }
    Output: { "status": "success", "countB": 30, "summary": "A가 B보다..." }
    """   
    try:
        return rag_service.compare_with_summary(request)
    except Exception as e:
        print(f"❌ 비교 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summary-compare")
def summarize_comparison(request: ComparisonRequest):
    """
    [심층 비교 요약]
    Case A와 Case B의 전체 데이터(쿼리+그래프)를 받아
    LLM이 분석한 비교 리포트를 반환합니다.
    """
    try:
        return rag_service.generate_comparison_summary(request)
    except Exception as e:
        print(f"❌ 비교 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    print("🚀 FastAPI 서버를 http://127.0.0.1:8000 에서 실행합니다.")
    print("   API 테스트 주소: http://127.0.0.1:8000/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
                