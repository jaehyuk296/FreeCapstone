import pandas as pd
import os
from langchain_anthropic import ChatAnthropic
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from dotenv import load_dotenv
from pathlib import Path  # <--- 1. '절대 경로'를 위해 import

# --- 1. API 키 설정
script_dir = Path(__file__).parent 
env_path = script_dir / ".env"
load_dotenv(dotenv_path=env_path) 

# (⭐ 2. '강제 확인' 코드 추가 ⭐)
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if API_KEY:
    print(f"--- .env 파일 로드 성공! (키의 마지막 4자리: ...{API_KEY[-4:]})")
else:
    print(f"'.env' 파일을 찾지 못했거나, 파일 안에 'ANTHROPIC_API_KEY'가 없습니다.")
    print(f"찾으려 했던 경로: {env_path}")
    exit() # <--- 키가 없으면 여기서 프로그램 강제 종료!
# (⭐ 여기까지 ⭐)

# --- 2. 파일에서 데이터 로드 (JSON) ---
file_path_json = '../json_extraction/welcome_data/Welcome_1st_preprocessed.json' 
try:
    df_welcome1 = pd.read_json(file_path_json)
    print(f"--- {file_path_json} 로드 성공 ---")
    print(df_welcome1.head())
    print("-" * 30)
except FileNotFoundError:
    print(f"오류: {file_path_json} 경로에 파일이 없습니다.")
    exit()

# --- 3. LLM (Claude) 모델 로드 ---
llm = ChatAnthropic(model='claude-3-haiku-20240307', temperature=0)

# --- 4. Pandas DataFrame 에이전트 생성 ('옛날' 0.1.x 방식) ---
agent = create_pandas_dataframe_agent(
    llm,
    df_welcome1,
    verbose=True,
    allow_dangerous_code=True 
)

# --- 5. 자연어 질의 테스트 ---

print("\n--- (난이도 하) 단순 필터링 및 집계 ---")
query1 = "전체 응답자는 몇 명이야?"
response1 = agent.invoke(query1) 
print(f"답변: {response1['output']}")

query2 = "평균 나이는 몇 살이야?"
response2 = agent.invoke(query2)
print(f"답변: {response2['output']}")

print("\n--- (난이도 중) 복합 필터링 (AND / OR) ---")
query3 = "서울에 사는 30대 남성은 몇 명?"
response3 = agent.invoke(query3)
print(f"답변: {response3['output']}")

print("\n--- 테스트 완료 ---")