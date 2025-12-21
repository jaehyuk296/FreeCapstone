<div align="center">
  <br>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=7038CA&height=220&text=Thoth&fontSize=70&fontColor=FFFFFF&fontAlignY=40&animation=fadeIn&desc=패널%20인터페이스를%20활용한%20자연어%20검색%20웹서비스&descSize=25&descAlignY=75" width="100%" />
  
<img src="./public/Logo_whiteBG.png" alt="Thoth Logo" height="150" />
</div>


# Thoth Frontend

Thoth는 사용자의 자연어 질문을 이해하고, 직관적인 패널(Panel) UI를 통해 최적의 검색 결과를 시각화하여 제공하는 웹 애플리케이션입니다.
<br>

## [시작화면]

https://github.com/user-attachments/assets/76739128-e475-4504-a9df-dbc0a0c62c95

<br>

### [초기검색화면]

https://github.com/user-attachments/assets/45efdd20-4c12-46a5-8bad-6bfe91bc2d08

<br>

## [편집화면]

### [템플릿변경]

https://github.com/user-attachments/assets/612fdebf-ed6b-476d-bedf-0d1b6aa59e37

<br>

### [추가&삭제]

https://github.com/user-attachments/assets/834bb7ee-bf14-4e04-96cd-5a18f461ea6b

<br>

### [드래그&리사이즈]

https://github.com/user-attachments/assets/10c9a1d1-58db-4d8a-ac4b-a544e4467848

<br>

### [태그변경]

https://github.com/user-attachments/assets/3b417b2b-9359-42f3-8345-8bf799e9f54c

<br>

## [메인화면]

https://github.com/user-attachments/assets/c8da381d-e6b2-48d0-a84c-d1f9352b6066

<br>

### Members

<table width="100%" align="center">
    <tr>
        <td align="center"><b>LEAD/BE</b></td>
        <td align="center"><b>PM/FE</b></td>
        <td align="center"><b>FE</b></td>
        <td align="center"><b>AI</b></td>
        <td align="center"><b>DATA</b></td>
    </tr>
    <tr>
        <td align="center"><img src="https://avatars.githubusercontent.com/miinsoo" width="100" height="100" style="border-radius:50%" /></td>
        <td align="center"><img src="https://avatars.githubusercontent.com/yoominho114" width="100" height="100" style="border-radius:50%" /></td>
        <td align="center"><img src="https://avatars.githubusercontent.com/thdrlghks" width="100" height="100" style="border-radius:50%" />
</td>
        <td align="center"><img src="https://avatars.githubusercontent.com/jaehyuk296" width="100" height="100" style="border-radius:50%" /></td>
        <td align="center"><img src="https://avatars.githubusercontent.com/jooyoi" width="100" height="100" style="border-radius:50%" />
</td>
    </tr>
    <tr>
        <td align="center"><b><a href="https://github.com/miinsoo">채민수</a></b></td>
        <td align="center"><b><a href="https://github.com/yoominho114">유민호</a></b></td>
        <td align="center"><b><a href="https://github.com/thdrlghks">송기환</a></b></td>
        <td align="center"><b><a href="https://github.com/jaehyuk296">이재혁</a></b></td>
        <td align="center"><b><a href="https://github.com/jooyoi">홍주영</a></b></td>
    </tr>
</table>

## Tech Stack
### Languages & Frameworks

- **Node.js 22.19.0 (LTS)**: 시스템 전반의 비즈니스 로직 및 API 게이트웨이를 담당하는 메인 백엔드 환경

- **Express 5.1.0**: RESTful API 구축 및 서비스 미들웨어 관리

- **Python 3.11+**: 시스템 백엔드 및 데이터 분석 메인 언어

- **FastAPI**: 고성능 비동기 API 서버 구축

### AI & LLM Models
- **Anthropic Claude 4.5 Sonnet**: 페르소나 문장 생성 및 고도의 질의 분석 수행

- **nlpai-lab/KURE-v1**: 한국어 문맥 이해에 최적화된 SentenceTransformer 임베딩 모델

- **LangChain**: LLM과 데이터(Pandas, Vector DB) 간의 효율적인 체인 구성 및 에이전트 활용

### Database Management
- **ChromaDB (Vector Store)**: 패널 페르소나 임베딩 데이터의 고속 유사도 검색

- **PostgreSQL + pgvector**: 패널의 원천 메타데이터 및 상세 속성 관리 (RDBMS)

### Data Engineering
- **Pandas & NumPy**: 대규모 설문 엑셀 데이터 전처리 및 통계 분석

- **Glob & OS**: 분산된 JSON 파일의 자동 탐색 및 통합 파이프라인 구축

### Infrastructure
- **PM2**: 메인 서버(Node.js)와 서브 서버(FastAPI)의 프로세스 관리 및 무중단 운영 지원

- **Axios v1.13.1**: Node.js 메인 서버에서 FastAPI 서브 서버로 분석 요청을 전달하는 내부 서버 간 통신(IPC) 구현
## Run

#### Installation

```bash
git clone https://github.com/hansung-sw-capstone-2025-2/2025_8_H_BE.git
```

#### install dependencies
```
# PM2 전역 설치 (필요 시)
npm install -g pm2

# AI Server (Python venv 설정 및 라이브러리 설치)
python -m venv .venv
source .venv/bin/activate  # (윈도우: source .venv/Scripts/activate)
pip install -r LLM/requirements.txt

# Main Server (Node.js 라이브러리 설치)
cd apps
npm install
cd ..

# 

```

#### Pre-run Checklist
- 서버 실행 전 다음 데이터들이 준비되어 있어야 정상적인 검색이 가능합니다.

- OS 환경: 본 가이드와 PM2 설정은 Linux(Ubuntu)/macOS 기반이며, 윈도우 사용 시 ecosystem.config.js 내 파이썬 경로를 .venv/Scripts/python.exe로 수정해야 합니다.

- Vector DB 존재 여부: LLM/panel_vector_db 폴더에 임베딩 데이터가 적재되어 있어야 합니다.

- Raw Data 파일: LLM/merged_panel_data.json 파일이 존재해야 답변 생성 시 원본 메타데이터를 참조할 수 있습니다.

- API Key 유효성: Anthropic API 키가 유효해야 Claude 모델을 통한 쿼리 분석 및 답변 생성이 가능합니다.

#### Run Dev Server
서버 실행 명령어:
```
cd 2025_8_H_BE

# 서버 전체 시작 
pm2 start ecosystem.config.js
```


## Project Structure

1. Root Directory

```

FreeCapstone/
├── apps/                            # 메인 백엔드 서비스 (Node.js/Express)
├── LLM/                             # 핵심 AI/RAG 엔진 및 서브 서버 (FastAPI)
├── json_extraction/                 # 전처리 및 통합된 JSON 데이터 저장소
│   ├── welcome_data/                # Welcome 설문 전처리 결과
│   ├── qpoll_data/                  # QPoll 설문 월별 전처리 결과
│   └── master_data.json             # 전체 통합 마스터 데이터셋
├── panel_extraction/                # 엑셀 원천 데이터 전처리 스크립트 모음
│   ├── welcome_data/                # Welcome 데이터 가공 로직
│   └── qpoll_data/                  # 분산된 JSON 파일 병합 및 관리 
├── paneldata/                       # 원천 설문 데이터 (Excel) 보관소
├── ecosystem.config.js              # PM2 프로세스 관리 및 통합 실행 설정
└── requirements.txt

```

2. Main Server (/apps)

```

apps/
├── src/
│   ├── libs/                        # 공통 유틸리티 및 DB 접근 로직
│   │   └── metadata.repository.js   # PostgreSQL 메타데이터 조회 쿼리 관리
│   ├── middlewares/                 # Express 미들웨어 (에러 핸들링, 응답 표준화)
│   │   ├── errorHandler.js          # 전역 에러 처리 및 상태 코드 관리
│   │   └── responseHandler.js       # API 응답 규격(isSuccess, result 등) 통일
│   ├── modules/                     # 도메인별 핵심 기능 모듈 
│   │   ├── panels/                  # 패널 검색 및 필터링 
│   │   ├── reports/                 # 대시보드 보고서 생성 로직
│   │   ├── compares/                # 그룹 간 비교 분석 서비스
│   │   ├── graphs/                  # 그래프 시각화 데이터 변환 
│   │   ├── tables/                  # 표 데이터 변환 및 매핑 
│   │   └── summaries/               # AI 요약용 컨텍스트 데이터 구성 
│   ├── providers/                   # 외부 서버 통신 계층 (IPC)
│   │   └── panel.provider.js        # Axios를 활용한 FastAPI(AI Server) 요청 처리
│   ├── routes/                      # API 엔드포인트 라우팅 통합 
│   ├── app.js                       # Express 앱 진입점 및 서버 설정
│   └── db.config.js                 # PostgreSQL 데이터베이스 연결 설정
├── package.json                     # Node.js 의존성 관리
└── .env                             # 서버 환경 변수

```

3. AI Server (/LLM)

```

LLM/
├── panel_vector_db/             # ChromaDB 벡터 데이터 저장소 (임베딩된 페르소나 데이터)
├── main.py                      # FastAPI 서버 진입점 (분석 및 요약 API 제공)
├── embed_data.py                # KURE-v1 모델을 사용한 데이터 임베딩 및 DB 적재 스크립트
├── generate_sentences.py        # Anthropic Claude 모델 기반 페르소나 문장 생성 로직
├── evaluate.py                  # RAG 시스템의 정확도(Precision/Recall) 평가 모듈
├── retry_failed_generations.py  # LLM 생성 실패 시 재시도 및 오류 복구 로직
├── merge_data.py                # 분산된 JSON 데이터를 통합하는 유틸리티
├── sample_data.py               # 시스템 테스트를 위한 샘플 데이터셋
├── .venv/                       # Python 가상환경 (Isolated Environment)
└── .env                         # AI 모델 API Key 및 환경 설정

```

## API Endpoints

### 1. Main Server API (/apps)

- **POST /api/panels**

    - **Description**: 자연어 쿼리를 분석하여 조건에 맞는 패널 목록을 반환합니다.

    - **Logic**: 요청 수신 → AI 검색 수행(/search) → PostgreSQL 메타데이터 조회 → DTO 변환

- **POST /api/reports**

    - **Description**: 선택된 패널들의 통계 그래프, 테이블 데이터 및 AI 요약 리포트를 생성합니다.

    - **Logic**: 메타데이터 조회 → 시각화 데이터 변환(Transformer) → AI 요약 요청(/summary) → 결과 병합

- **POST /api/compares**

    - **Description**: 두 사용자 집단(Case A vs Case B)의 특성을 비교 분석합니다.

    - **Logic**: 쿼리 분기 처리 → 집단별 데이터 집계 → 비교 그래프 생성 → AI 심층 분석 요청(/summary-compare)


### 2. AI Server API (/LLM)
### Search & RAG
- **POST /search**: 사용자의 자연어 질의를 분석하여 하이브리드 검색 결과와 답변을 반환합니다.

    - **Request**: {"query": "운동을 좋아하는 30대 남성"}

    - **Logic**: 쿼리 분석(Claude) → 벡터 검색(ChromaDB) → 원본 데이터 매핑 → 최종 답변 생성

### Analysis & Summary
- **POST /summary**: 대시보드의 차트 및 테이블 데이터를 분석하여 인사이트 요약을 생성합니다.

- **POST /compare** 두 집단(Case A, Case B) 간의 인원수 차이를 비교하고 요약 리포트를 제공합니다.

- **POST /summary-compare**: 두 집단의 그래프 데이터를 심층 비교 분석하여 텍스트 리포트를 생성합니다.

### System Utility
- **GET /docs**: Swagger UI를 통해 모든 API 명세와 테스트 환경을 제공합니다.


## Key Features

### Scalable Web Service (Apps)
- **Dynamic Visualization Engine**: GraphTransformer와 TableTransformer를 통해 DB의 원천 메타데이터를 프론트엔드 차트(도넛, 바 등) 및 테이블 규격에 맞는 JSON 포맷으로 실시간 변환합니다.

- **Robust Layered Architecture**: Controller-Service-Repository 패턴을 적용하여 비즈니스 로직을 명확히 분리하고, Global Error Handler를 통해 예측 가능한 예외 처리 및 표준화된 API 응답을 제공합니다.

- **Seamless IPC (Inter-Process Communication)**: Provider 패턴(Axios)을 활용하여 Node.js 메인 서버와 Python AI 서버 간의 데이터 파이프라인을 안정적으로 연결하고 관리합니다.

### Automated Data Pipeline
- **Welcome Data Processing**: 복잡한 엑셀 설문 코드를 "결혼여부", "직업", "소득" 등 의미 있는 텍스트로 자동 매핑 및 전처리합니다.

- **Dynamic Merging**: merge_json_files.py를 통해 여러 폴더에 흩어진 전처리 파일들을 고유번호 기준으로 하나의 마스터 데이터셋으로 자동 통합합니다.

### RAG (Retrieval-Augmented Generation)
- **Hybrid Search**: 사용자의 질문을 분석하여 메타데이터 필터(나이, 성별 등)와 의미적 쿼리(관심사 등)를 결합한 정밀 검색을 수행합니다.

- **Persona Summarization**: Claude 모델을 활용하여 방대한 설문 데이터를 자연스러운 페르소나 요약 문장으로 변환합니다.

### Advanced Analysis & Reliability
- **Comparison Analysis**: 두 집단 간의 특성을 비교 분석하고 시각화 데이터 요약을 제공합니다.

## Environment Variables
- .env 파일에 다음과 같은 API 키 및 DB 설정이 필요합니다.


### 1. Main Server (apps/.env)
```
# Server Configuration
PORT=3000

# Inter-Process Communication (To AI Server)
FASTAPI_SERVER_URL="http://localhost:8000"

# Database Connection (PostgreSQL)
# Format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL="postgresql://user:password@localhost:5432/your_db"
```

### 2. AI Server (LLM/.env)
```
# Anthropic API Key (Required for Claude 3.5 Sonnet)
ANTHROPIC_API_KEY=sk-ant-api03-xxx...

# OpenAI API Key 
OPENAI_API_KEY=sk-proj-xxx...
```

## License
이 프로젝트는 한성대학교 기업연계 SW캡스톤디자인 수업에서 진행되었습니다.
