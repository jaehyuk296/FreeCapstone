import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250617' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('땀 불편함' 맞춤 - 복수 응답 처리) ---
option_map = {
    '1': '옷이 젖거나 얼룩지는 것',
    '2': '땀 냄새가 걱정된다',
    '3': '메이크업이 무너진다',
    '4': '머리나 두피가 금방 기름진다',
    '5': '피부 트러블이 생긴다',
    '6': '다른 사람의 땀 냄새가 불쾌하다',
    '7': '특별히 불편한 점이 없다'
}

# 원-핫 인코딩 수행 (통계 계산용)
dummies = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = pd.concat([df.drop('문항1', axis=1), dummies], axis=1)

# '땀_불편함_요약' 열 생성 (JSON 저장용)
def get_all_discomforts(row):
    discomforts = []
    # (★★★ 로직 수정: '특별히 불편한 점이 없다' 우선 처리 ★★★)
    if row.get('특별히 불편한 점이 없다', 0) == 1:
        return '특별히 불편한 점이 없다'

    for option_text in option_map.values():
        # '특별히 불편한 점이 없다'는 위에서 처리했으므로 제외
        if option_text != '특별히 불편한 점이 없다' and row.get(option_text, 0) == 1:
            discomforts.append(option_text)
            
    return ', '.join(sorted(discomforts)) if discomforts else '선택 없음'

df['땀_불편함_요약'] = df.apply(get_all_discomforts, axis=1)

# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("땀 '땀 불편함' 데이터 처리 완료.")


# (★★★ 수정된 부분 ★★★)
# --- 4. 최종 데이터프레임 생성 (JSON 저장용) ---
# JSON에 저장할 컬럼만 선택합니다. (요약 컬럼만 포함)
json_final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '땀_불편함_요약'
]
existing_json_columns = [col for col in json_final_columns if col in df.columns]
json_df = df[existing_json_columns].copy()


# --- 5. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jun/'
output_filename = f'{FILE_ID}_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-m-d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# (★★★ 수정된 부분 ★★★)
# --- 6. 요약 통계 생성 및 출력 ---
# 통계는 원-핫 인코딩 컬럼이 있는 원본 'df'를 사용합니다.
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

stats_summary = []
total_people = len(df) # 원본 df 사용
stats_summary.append(f"실제 참여자 인원수: {total_people}명")
stats_summary.append("-" * 30)

# 각 보기별 응답 인원수 계산 (원본 df 사용)
individual_options = list(option_map.values())
existing_options = [opt for opt in individual_options if opt in df.columns]

if existing_options:
    individual_counts = df[existing_options].sum().sort_values(ascending=False)
    stats_summary.append("불편함 유형별 인원수 (중복 응답):")
    stats_summary.append(individual_counts.to_string())
    stats_summary.append("-" * 30)


# 생성된 통계 문자열을 화면에 출력
final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 7. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Jun/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 여름철 땀 불편함 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")