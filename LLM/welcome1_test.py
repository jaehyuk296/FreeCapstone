import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
# (⭐ 1. import 경로가 'community'로 변경됨)
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
# (2. AgentExecutor는 'langchain.agents'가 맞음)
from langchain.agents import AgentExecutor

# --- 1. Google API 키 설정 ---
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCdi4-7afJUa07PEYfb3zhH73cj8R99ykg' # (학생의 키)

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

# --- 3. LLM (최신 Gemini) 모델 로드 ---
# (최신 라이브러리는 'gemini-1.0-pro' 이름을 정상적으로 지원함)
llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", temperature=0)

# --- 4. Pandas DataFrame 에이전트 생성 (⭐'최신' 방식⭐) ---
# create_pandas_dataframe_agent는 이제 '설계도(agent)'를 반환함
agent_runnable = create_pandas_dataframe_agent(
    llm,
    df_welcome1,
    verbose=True,
    allow_dangerous_code=True 
)

# '설계도(agent_runnable)'를 '실행기(AgentExecutor)'로 조립
agent_executor = AgentExecutor(
    agent=agent_runnable.agent,  # 에이전트 설계도
    tools=agent_runnable.tools,  # 사용 도구 (Pandas)
    verbose=True
)


# --- 5. 자연어 질의 테스트 ---
# (invoke 방식이 {"input": query} 형태가 맞음)

print("\n--- (난이도 하) 단순 필터링 및 집계 ---")
query1 = "전체 응답자는 몇 명이야?"
response1 = agent_executor.invoke({"input": query1})
print(f"답변: {response1['output']}")

query2 = "평균 나이는 몇 살이야?"
response2 = agent_executor.invoke({"input": query2})
print(f"답변: {response2['output']}")

print("\n--- (난이도 중) 복합 필터링 (AND / OR) ---")
query3 = "서울에 사는 30대 남성은 몇 명?"
response3 = agent_executor.invoke({"input": query3})
print(f"답변: {response3['output']}")

query4 = "지역_시도가 '서울' 이거나 '경기'인 사람은 총 몇 명이야?"
response4 = agent_executor.invoke({"input": query4})
print(f"답변: {response4['output']}")

print("\n--- (난이도 상) 그룹별 집계 (Group By) ---")
query5 = "각 지역_시도 별로 몇 명씩 살고 있는지 알려줘."
response5 = agent_executor.invoke({"input": query5})
print(f"답변: {response5['output']}")

query6 = "성별로 평균 나이를 계산해줘."
response6 = agent_executor.invoke({"input": query6})
print(f"답변: {response6['output']}")

print("\n--- (난이도 최상) 정렬 및 예외 처리 ---")
query7 = "나이가 가장 많은 1명의 고유번호는 뭐야?"
response7 = agent_executor.invoke({"input": query7})
print(f"답변: {response7['output']}")

query8 = "부산을 제외한 나머지 지역에는 총 몇 명이 살아?"
response8 = agent_executor.invoke({"input": query8})
print(f"답변: {response8['output']}")

print("\n--- 테스트 완료 ---")