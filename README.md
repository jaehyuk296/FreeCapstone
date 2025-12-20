# 🚀 FreeCapstone: Panel Data RAG & Analytics System
>본 프로젝트는 대규모 패널 설문 데이터를 기반으로 데이터 전처리, 자연어 검색(RAG) 그리고 데이터 분석을 수행하는 통합 시스템입니다. 복잡한 설문 응답을 LLM이 이해할 수 있는 형태로 정제하고, 이를 벡터 DB와 연동하여 최적의 인사이트를 도출합니다.

# 🛠 Tech Stack
💻 Languages & Frameworks
- Python 3.11+: 시스템 백엔드 및 데이터 분석 메인 언어

- FastAPI: 고성능 비동기 API 서버 구축

- React + Vite: 빠르고 현대적인 사용자 인터페이스(UI) 개발

🤖 AI & LLM Models
- Anthropic Claude 4.5 Sonnet: 페르소나 문장 생성 및 고도의 질의 분석 수행

- nlpai-lab/KURE-v1: 한국어 문맥 이해에 최적화된 SentenceTransformer 임베딩 모델

- LangChain: LLM과 데이터(Pandas, Vector DB) 간의 효율적인 체인 구성 및 에이전트 활용

🗄️ Database Management
- ChromaDB (Vector Store): 패널 페르소나 임베딩 데이터의 고속 유사도 검색

- PostgreSQL: 패널의 원천 메타데이터 및 상세 속성 관리 (RDBMS)


📊 Data Engineering
- Pandas & NumPy: 대규모 설문 엑셀 데이터 전처리 및 통계 분석

- Glob & OS: 분산된 JSON 파일의 자동 탐색 및 통합 파이프라인 구축

# 🚀 Installation

## 저장소 복제
```
git clone https://github.com/hansung-sw-capstone-2025-2/2025_8_H_BE.git
```

## 의존성 설치
```
pip install -r requirements.txt
```

## 🛠 실행 전 체크리스트 (Pre-run Checklist)
- 서버 실행 전 다음 데이터들이 준비되어 있어야 정상적인 검색이 가능합니다.

- Vector DB 존재 여부: LLM/panel_vector_db 폴더에 임베딩 데이터가 적재되어 있어야 합니다.

- Raw Data 파일: LLM/merged_panel_data.json 파일이 존재해야 답변 생성 시 원본 메타데이터를 참조할 수 있습니다.

- API Key 유효성: Anthropic API 키가 유효해야 Claude 모델을 통한 쿼리 분석 및 답변 생성이 가능합니다.

## 프로젝트 실행 방법
서버 실행 명령어:
```
cd 2025_8_H_BE

# LLM 디렉터리로 이동 후 실행
cd LLM
python main.py
```


# 📁 Directory Structure

```
FreeCapstone/
├── 📱 apps/                         # 웹 애플리케이션 프론트엔드/서비스 소스 코드
├── 📁 json_extraction/              # 전처리 및 통합된 JSON 데이터 저장소
│   ├── welcome_data/                # Welcome 설문 전처리 결과 (1st, 2nd)
│   ├── qpoll_data/                  # QPoll 설문 월별 전처리 결과
│   └── master_data.json             # 전체 통합 마스터 데이터셋
├── 🧠 LLM/                         # 핵심 RAG 서비스 및 모델 연동 로직
│   ├── panel_vector_db/             # ChromaDB 벡터 데이터 저장소
│   ├── main.py                      # FastAPI 서버 및 RAG 엔진 통합
│   ├── embed_data.py                # KURE-v1 모델 기반 임베딩 및 DB 적재
│   ├── generate_sentences.py        # Claude 모델 기반 페르소나 문장 생성
│   ├── evaluate.py                  # 시스템 정확도(Precision/Recall) 평가
│   └── retry_failed_generations.py  # 실패한 LLM 생성 작업 재시도
├── 🛠 panel_extraction/             # 엑셀 원천 데이터 전처리 스크립트
│   ├── welcome_data/                # Welcome 데이터 가공 로직
│   └── qpoll_data/                  # 분산된 JSON 파일 병합 및 관리 
├── 📊 paneldata/                    # 원천 설문 데이터 (Excel) 보관소
└── 📑 requirements.txt              # 프로젝트 의존성 라이브러리 목록
```

# 🔌 API Endpoints

## 🔍 Search & RAG
- POST /search: 사용자의 자연어 질의를 분석하여 하이브리드 검색 결과와 답변을 반환합니다.

- Request: {"query": "운동을 좋아하는 30대 남성"}

- Logic: 쿼리 분석(Claude) → 벡터 검색(ChromaDB) → 원본 데이터 매핑 → 최종 답변 생성

## 📊 Analysis & Summary
- POST /summary: 대시보드의 차트 및 테이블 데이터를 분석하여 인사이트 요약을 생성합니다.

- POST /compare: 두 집단(Case A, Case B) 간의 인원수 차이를 비교하고 요약 리포트를 제공합니다.

- POST /summary-compare: 두 집단의 그래프 데이터를 심층 비교 분석하여 텍스트 리포트를 생성합니다.

## 🛠 System Utility
- GET /docs: Swagger UI를 통해 모든 API 명세와 테스트 환경을 제공합니다.


# 🔑 Key Features
1️⃣ Automated Data Pipeline
Welcome Data Processing: 복잡한 엑셀 설문 코드를 "결혼여부", "직업", "소득" 등 의미 있는 텍스트로 자동 매핑 및 전처리합니다.

Dynamic Merging: merge_json_files.py를 통해 여러 폴더에 흩어진 전처리 파일들을 고유번호 기준으로 하나의 마스터 데이터셋으로 자동 통합합니다.

2️⃣ RAG (Retrieval-Augmented Generation)
Hybrid Search: 사용자의 질문을 분석하여 메타데이터 필터(나이, 성별 등)와 의미적 쿼리(관심사 등)를 결합한 정밀 검색을 수행합니다.

Persona Summarization: Claude 모델을 활용하여 방대한 설문 데이터를 자연스러운 페르소나 요약 문장으로 변환합니다.

3️⃣ Advanced Analysis & Reliability
Comparison Analysis: 두 집단 간의 특성을 비교 분석하고 시각화 데이터 요약을 제공합니다.

# 🔐 Environment Variables
> .env 파일에 다음과 같은 API 키 및 DB 설정이 필요합니다.


## AI API Keys
```
ANTHROPIC_API_KEY=sk-ant-api03-xxx
OPENAI_API_KEY=your_openai_api_key
```

## Database Settings
```
DB_HOST=localhost
DB_PORT=your_port
DB_NAME=your_DB
DB_USER=postgres
DB_PASSWORD=your_password
```

## License
이 프로젝트는 한성대학교 기업연계 SW캡스톤디자인 수업에서 진행되었습니다.
