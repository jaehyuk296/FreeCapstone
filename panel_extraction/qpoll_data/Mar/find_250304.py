import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250304' # 새로운 파일 ID로 변경
filepath = f'../../../paneldata/Quickpoll/qpoll_join_{FILE_ID}.xlsx'

# --- 2. 파일 읽기 ---
try:
    # skiprows=1 옵션: 엑셀 파일의 맨 위 1줄(질문)을 건너뛰고 데이터를 읽어옵니다.
    df = pd.read_excel(filepath, skiprows=1)
    # 컬럼 이름의 앞뒤 공백을 제거하여 안정성을 높입니다.
    df.columns = df.columns.str.strip()
    print(f"✅ '{filepath}' 파일 읽기 성공.")
except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 3. 데이터 전처리 ('스트레스' 맞춤) ---

# '문항1' (스트레스 요인)에 대한 코드북
option_map_q1 = {
    1: '업무/학업',
    2: '출퇴근',
    3: '인간관계 (가족, 친구, 직장 등)',
    4: '경제적 문제',
    5: '건강 문제',
    6: '기타'
}

# '문항2' (스트레스 해소법)에 대한 코드북
option_map_q2 = {
    1: '수면',
    2: '음식 섭취',
    3: '운동',
    4: '명상/휴식',
    5: '마사지/스파',
    6: '기타'
}

# '문항1'과 '문항2' 열을 각각 숫자형으로 변환
df['문항1'] = pd.to_numeric(df['문항1'], errors='coerce')
df['문항2'] = pd.to_numeric(df['문항2'], errors='coerce')

# 각 문항에 대한 새로운 텍스트 열 생성
df['스트레스_요인'] = df['문항1'].map(option_map_q1)
df['스트레스_해소법'] = df['문항2'].map(option_map_q2)

# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 4. 더 이상 필요 없는 원본 문항 컬럼 삭제 ---
df = df.drop(columns=['문항1', '문항2'], errors='ignore')

print("🤯 '스트레스' 데이터 처리 완료.")


# --- 5. 최종 데이터프레임 생성 ---
final_df = df.copy()

# --- 디버깅용 출력: 최종적으로 어떤 컬럼이 선택되었는지 확인 ---
print("\n--- 최종 데이터프레임의 컬럼 목록 ---")
print(final_df.columns.tolist())
print("-" * 30)
# --- 디버깅용 출력 끝 ---


# --- 6. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Mar/'
output_filename = f'{FILE_ID}_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 7. 요약 통계 생성 및 출력 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

# 통계 내용을 담을 문자열 변수 생성
stats_summary = []

total_people = len(final_df)
stats_summary.append(f"실제 참여자 인원수: {total_people}명")
stats_summary.append("-" * 30)

# 스트레스 요인 통계
stress_factor_counts = final_df['스트레스_요인'].value_counts()
stats_summary.append("스트레스 요인별 인원수:")
stats_summary.append(stress_factor_counts.to_string())
stats_summary.append("-" * 30)

# 스트레스 해소법 통계
stress_relief_counts = final_df['스트레스_해소법'].value_counts()
stats_summary.append("스트레스 해소법별 인원수:")
stats_summary.append(stress_relief_counts.to_string())
stats_summary.append("-" * 30)


# 생성된 통계 문자열을 화면에 출력
final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 8. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Mar/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 스트레스 관련 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string) # 화면에 출력한 통계 문자열을 그대로 파일에 씀

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

