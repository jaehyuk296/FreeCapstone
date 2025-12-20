import pandas as pd
import numpy as np
import os

# --- 1. 파일 읽기 ---
try:
    df = pd.read_excel('../../../paneldata/Quickpoll/qpoll_join_250107.xlsx', skiprows=1)
    df.columns = df.columns.str.strip()
    print("✅ 파일 읽기 성공.")
except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 2. '문항1'의 각 보기가 의미하는 것 정의 (코드북) ---
option_map = {
    '1': '1개', '2': '2개', '3': '3개', '4': '4개이상', '5': '없다'
}

# --- 3. '문항1' 전처리 (공백 제거 등) ---
df['문항1_clean'] = df['문항1'].astype(str).str.strip().str.replace(' ', '')

# --- 4. 요약 컬럼 생성 (JSON 저장용) ---
df['ott사용개수'] = df['문항1_clean'].map(option_map).fillna('선택 없음')
print("✅ 'ott사용개수' 요약 컬럼 생성 완료.")

# --- 5. 원-핫 인코딩 (통계 분석용) ---
dummies = df['문항1_clean'].str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = df.drop('문항1', axis=1) # 원본 '문항1' 열 삭제
df = pd.concat([df, dummies], axis=1)

# --- 6. 'ott사용중' 열 생성 (통계용 1/0, JSON용 문자열) ---
# 6-1. 통계용 1(사용중) / 0(사용안함) 컬럼
if '없다' in df.columns:
    df['is_using_ott_binary'] = (df['없다'] == 0).astype(int)
else:
    df['is_using_ott_binary'] = 1
print("✅ 통계용 'is_using_ott_binary' (1/0) 열 생성 완료.")

# 6-2. JSON 저장용 'ott사용중' 문자열 컬럼 (요청 사항)
df['ott사용중'] = df['is_using_ott_binary'].map({
    1: '사용중이다', 
    0: '사용하지않는다'
}).fillna('사용하지않는다')
print("✅ JSON용 'ott사용중' (문자열) 열 생성 완료.")


# --- 7. 날짜 형식 변환 ---
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 8. 최종 컬럼 선택 (JSON 저장용) ---
json_final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    'ott사용개수',  # '1개', '2개' 등 원-핫 인코딩 컬럼 대신 삽입
    'ott사용중'     # '사용중이다' / '사용하지않는다'
]
existing_json_columns = [col for col in json_final_columns if col in df.columns]
json_df = df[existing_json_columns].copy()

# --- 9. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jan/'
output_filename = '250107_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

# JSON 저장을 위해 datetime 형식을 문자열로 변환
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 10. 요약 통계 출력 및 저장 (기존 df와 1/0 컬럼 사용) ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

total_people = len(df)
# 통계를 위해 문자열이 아닌 1/0 (binary) 컬럼을 사용합니다.
ott_users = df['is_using_ott_binary'].sum()

print(f"실제 참여자 인원수: {total_people}명")
if total_people > 0:
    print(f"OTT 이용자 수: {ott_users}명")
    print(f"OTT 이용자 비율: {ott_users / total_people * 100:.2f}%")
print("-" * 30)

individual_options = list(option_map.values())
existing_options = [opt for opt in individual_options if opt in df.columns]

if existing_options:
    # 통계를 위해 원-핫 인코딩된 컬럼들을 사용합니다.
    individual_counts = df[existing_options].sum().sort_values(ascending=False)
    print("각 보기별 응답 인원수:")
    print(individual_counts)
    print("-" * 30)

# --- 11. 통계 결과를 .txt 파일로 저장 ---
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