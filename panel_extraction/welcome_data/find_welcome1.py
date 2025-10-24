import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
# Welcome 데이터는 파일이 하나이므로 파일 이름을 직접 지정합니다.
FILE_ID = 'Welcome_1st'
filepath = f'../../paneldata/Welcome/{FILE_ID}.xlsx'

# --- 2. 파일 읽기 ---
try:
    df = pd.read_excel(filepath)
    # 컬럼 이름의 앞뒤 공백을 제거합니다.
    df.columns = df.columns.str.strip()
    print(f"✅ '{filepath}' 파일 읽기 성공.")
except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 3. 데이터 전처리 (Welcome 데이터 맞춤) ---

# 3-1. 컬럼 이름 변경
# 코드북을 참고하여 알아보기 쉬운 한글 이름으로 변경합니다.
rename_map = {
    'mb_sn': '고유번호',
    'Q10': '성별_코드',
    'Q11': '출생년도',
    'Q12_1': '지역_시도',
    'Q12_2': '지역_시군구'
    # ... 여기에 다른 Q넘버들도 추가 ...
}
df = df.rename(columns=rename_map)


# 3-2. 데이터 값 변환
# 성별 변환
gender_map = {'M': '남성', 'F': '여성'}
if '성별_코드' in df.columns:
    df['성별'] = df['성별_코드'].map(gender_map)

# 나이 계산
if '출생년도' in df.columns:
    current_year = 2025 # 기준 연도
    df['나이'] = current_year - pd.to_numeric(df['출생년도'], errors='coerce') + 1

print("📊 Welcome 데이터 처리 완료.")


# --- 4. 최종 데이터프레임 생성 ---
# 분석에 필요한 최종 컬럼들을 선택합니다. (원본 코드 컬럼은 제외)
final_columns = [
    '고유번호', '성별', '나이', '지역_시도', '지역_시군구'
    # ... 여기에 다른 전처리된 컬럼들도 추가 ...
]
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()


# --- 5. 최종 JSON 저장 ---
output_folder = '../../json_extraction/welcome_data/'
output_filename = f'{FILE_ID}_preprocessed.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

final_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 6. 요약 통계 생성 및 출력 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

stats_summary = []
total_people = len(final_df)
stats_summary.append(f"전체 인원수: {total_people}명")
stats_summary.append("-" * 30)

# 각 항목별 통계 추가
if '성별' in final_df.columns:
    stats_summary.append("성별 인원수:")
    stats_summary.append(final_df['성별'].value_counts().to_string())
    stats_summary.append("-" * 30)

if '나이' in final_df.columns:
    stats_summary.append("연령대별 인원수:")
    # 연령대 그룹을 만들기 위한 구간(bins)과 라벨(labels) 정의
    bins = [0, 19, 29, 39, 49, 59, 69, 100]
    labels = ['10대', '20대', '30대', '40대', '50대', '60대', '70대 이상']
    # '나이' 컬럼을 사용해 '연령대' 컬럼 임시 생성
    final_df['연령대'] = pd.cut(final_df['나이'], bins=bins, labels=labels, right=True)
    age_group_counts = final_df['연령대'].value_counts().sort_index()
    stats_summary.append(age_group_counts.to_string())
    stats_summary.append("-" * 30)  

if '지역_시도' in final_df.columns:
    stats_summary.append("지역(시/도)별 인원수:")
    stats_summary.append(final_df['지역_시도'].value_counts().to_string())
    stats_summary.append("-" * 30)

if '지역_시군구' in final_df.columns:
    stats_summary.append("지역(시/군/구)별 인원수:")
    stats_summary.append(final_df['지역_시군구'].value_counts().to_string())
    stats_summary.append("-" * 30)

final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 7. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../json_extraction/welcome_data/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 데이터 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)
    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

