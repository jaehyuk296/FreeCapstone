import pandas as pd
import os
from langchain_anthropic import ChatAnthropic
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from dotenv import load_dotenv
from pathlib import Path  # <--- 1. '절대 경로'를 위해 import

# --- 1. API 키 설정 ---
script_dir = Path(__file__).parent 
env_path = script_dir / ".env"
load_dotenv(dotenv_path=env_path) 

API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not API_KEY:
    print(f"[치명적 오류] .env 파일을 찾지 못했거나 ANTHROPIC_API_KEY가 없습니다.")
    print(f"찾으려 했던 경로: {env_path}")
    exit()
print(f"--- .env 파일 로드 성공! (키: ...{API_KEY[-4:]})")

# 2a. welcome1 (JSON) 로드
file_path_json_w1 = '../json_extraction/welcome_data/Welcome_1st_preprocessed.json' 
try:
    df_welcome1 = pd.read_json(file_path_json_w1)
    print(f"--- {file_path_json_w1} (df_welcome1) 로드 성공 ---")
    print(df_welcome1.head())
    print("-" * 30)
except FileNotFoundError:
    print(f"오류: {file_path_json_w1} 경로에 파일이 없습니다.")
    exit()

# 2b. welcome2 (JSON) 로드 
file_path_json_w2 = '../json_extraction/welcome_data/Welcome_2nd_preprocessed.json' 
try:
    df_welcome2 = pd.read_json(file_path_json_w2)
    # df_welcome2의 컬럼 이름 중 '.'이나 특수문자를 '_'로 변경 (Pandas 에이전트 호환성)
    df_welcome2.columns = df_welcome2.columns.str.replace('[^A-Za-z0-9_]+', '_', regex=True)
    print(f"--- {file_path_json_w2} (df_welcome2) 로드 성공 ---")
    print(df_welcome2.head())
    print("-" * 30)
except FileNotFoundError:
    print(f"오류: {file_path_json_w2} 경로에 파일이 없습니다.")
    exit()

# --- 3. 스키마(데이터 사전) 정의 (⭐ welcome1 + welcome2 정보 ⭐) ---
SCHEMA_DESCRIPTION = f"""
너는 두 개의 pandas dataframe을 분석해야 한다. 이 dataframe들은 '고유번호'(df1) 또는 'mb_sn'(df2) 컬럼을 통해 연결될 수 있다.

df_list[0] (이하 df1)은 사용자의 기본 인구통계 정보를 담고 있다. 컬럼:
{df_welcome1.columns.to_list()}
주요 컬럼 설명: '성별', '나이', '지역_시도', '지역_시군구'

df_list[1] (이하 df2)은 사용자의 상세 설문조사 응답이다. 컬럼:
{df_welcome2.columns.to_list()}
주요 컬럼 설명 (일부):
- 'Q1': 결혼여부 (1=기혼)
- 'Q2': 자녀수
- 'Q6': 월평균 개인소득
- 'Q7': 월평균 가구소득
- 'Q10': 보유차량여부 (1=보유)
- 'Q12_1_ETC': 흡연경험 담배브랜드(기타 주관식)

분석 시 주의사항:
- 두 dataframe을 합쳐야 할 경우 '고유번호'(df1)와 'mb_sn'(df2)을 기준으로 merge 하거나, 두 dataframe에서 각각 정보를 찾아 조합해야 한다.
- 질문에서 특정 'Q' 번호를 언급하면 df2를 참조해야 한다.
- 질문에서 '지역', '나이', '성별'을 언급하면 df1을 참조해야 한다.
"""

# --- 4. LLM (Claude) 모델 로드 ---
llm = ChatAnthropic(model='claude-3-haiku-20240307', temperature=0)

# --- 5. Pandas DataFrame 에이전트 생성 (⭐ 다중 DataFrame 리스트 전달 ⭐) ---
agent = create_pandas_dataframe_agent(
    llm,
    [df_welcome1, df_welcome2], # <--- 두 개의 DataFrame을 리스트로 전달
    verbose=True,
    allow_dangerous_code=True,
    prefix=SCHEMA_DESCRIPTION # <--- 통합된 스키마 정보를 LLM에게 전달
)

# --- 6. 자연어 질의 테스트 (⭐ 복합 질문 위주 ⭐) ---

print("\n--- 복합 질문 테스트 ---")
# 예시 1: df1(나이, 지역) + df2(결혼여부)
query1 = "서울에 사는 30대 기혼자(Q1=1)는 총 몇 명이야?" 
response1 = agent.invoke(query1)
print(f"답변 1: {response1['output']}")

# 예시 2: df1(성별) + df2(소득)
query2 = "남성의 월평균 개인소득(Q6)은 얼마야?"
response2 = agent.invoke(query2)
print(f"답변 2: {response2['output']}")

# 예시 3: df2 내 주관식 검색
query3 = "담배 브랜드로 '에쎄'라고 답한 사람(Q12_1_ETC)은 몇 명이야?"
response3 = agent.invoke(query3)
print(f"답변 3: {response3['output']}")


print("\n--- 테스트 완료 ---")