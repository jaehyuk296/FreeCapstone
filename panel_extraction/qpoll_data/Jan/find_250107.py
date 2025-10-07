import pandas as pd
import numpy as np
import os

# --- 1. 파일 읽기 (수정됨) ---
try:
    # skiprows=1 옵션: 엑셀 파일의 맨 위 1줄(질문)을 건너뛰고 데이터를 읽어옵니다.
    # 이렇게 하면 2번째 줄이 자동으로 컬럼 이름(헤더)으로 지정됩니다.
    df = pd.read_excel('../../../paneldata/Quickpoll/qpoll_join_250107.xlsx', skiprows=1)
    
    # 만약을 위해 컬럼 이름의 앞뒤 공백을 제거합니다.
    df.columns = df.columns.str.strip()

except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 2. 불필요한 행 제거 (skiprows로 처리했으므로 이 부분은 더 이상 필요 없음) ---


# --- 3. '문항1'의 각 보기가 의미하는 것 정의 (코드북) ---
option_map = {
    '1': '1개', '2': '2개', '3': '3개', '4': '4개이상', '5': '없다'
}

# --- 4. 원-핫 인코딩 수행 (복수 응답 처리) ---
dummies = df['문항1'].astype(str).str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = df.drop('문항1', axis=1) # 원본 '문항1' 열 삭제
df = pd.concat([df, dummies], axis=1)

# --- 5. 'is_using_ott' 열 생성 ---
# '없다' 컬럼이 존재하고 그 값이 1이면 OTT를 이용하지 않는 것(0)으로,
# 그렇지 않으면 이용하는 것(1)으로 간주합니다.
if '없다' in df.columns:
    df['is_using_ott'] = (df['없다'] == 0).astype(int)
else:
    # '없다' 컬럼이 없는 경우는 모두 이용한다고 가정 (예외 처리)
    df['is_using_ott'] = 1


# --- 6. 날짜 형식 변환 ---
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 7. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '1개', '2개', '3개', '4개이상', '없다',
    'is_using_ott'
]
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()

# --- 8. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jan/'
output_filename = '250107_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")

# --- 9. 요약 통계 출력 및 저장 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

total_people = len(final_df)
ott_users = final_df['is_using_ott'].sum()

print(f"실제 참여자 인원수: {total_people}명")
if total_people > 0:
    print(f"OTT 이용자 수: {ott_users}명")
    print(f"OTT 이용자 비율: {ott_users / total_people * 100:.2f}%")
print("-" * 30)

individual_options = list(option_map.values())
existing_options = [opt for opt in individual_options if opt in final_df.columns]

if existing_options:
    individual_counts = final_df[existing_options].sum().sort_values(ascending=False)
    print("각 보기별 응답 인원수:")
    print(individual_counts)
    print("-" * 30)

# --- 10. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Jan/summary/'
stats_output_filename = '250107_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write("📊 OTT 이용 현황 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(f"실제 참여자 인원수: {total_people}명\n")
        if total_people > 0:
            f.write(f"OTT 이용자 수: {ott_users}명\n")
            f.write(f"OTT 이용자 비율: {ott_users / total_people * 100:.2f}%\n")
        f.write("-" * 30 + "\n\n")
        
        if existing_options:
            f.write("각 보기별 응답 인원수:\n")
            f.write(individual_counts.to_string() + "\n")
            f.write("-" * 30 + "\n\n")
            
    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")

except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

