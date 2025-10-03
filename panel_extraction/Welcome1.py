import pandas as pd
import os

# --- 어떤 조건으로 필터링할지 변수로 정의 ---
target_gender = 'M'
target_age_start = 40
target_age_end = 49
target_city = '서울'
target_district = '성동구'

# --- 저장하고 싶은 폴더 경로를 변수로 지정 ---
output_folder = '../json_extraction/welcome1_data/' 

# 실제 데이터 파일을 불러옵니다.
df = pd.read_excel('../paneldata/Welcome/Welcome_1st.xlsx')

# 1. 성별 조건
condition_gender = df['Q10'] == target_gender

# 2. 나이 조건
current_year = 2025
age = current_year - df['Q11'] + 1
condition_age = (age >= target_age_start) & (age <= target_age_end)

# 3. 지역 조건
condition_city = df['Q12_1'] == target_city
condition_district = df['Q12_2'] == target_district

# --- 모든 조건을 만족하는(&) 데이터만 추출 ---
extracted_panel_df = df[condition_gender & condition_age & condition_city & condition_district]

print(f"--- {target_city} {target_district} {target_age_start}대 {target_gender} 패널 추출 결과 ---")
print(f"총 {len(extracted_panel_df)}명")


# --- 2단계: f-string을 이용해 동적으로 파일 이름 생성 ---
output_filename = f"panel_{target_city}_{target_district}_{target_age_start}대_{target_gender}.json"

# 추출된 패널을 동적으로 생성된 파일 이름으로 저장
# 2. 폴더 경로와 파일 이름을 합쳐서 '전체 경로'를 만듭니다.
full_path = os.path.join(output_folder, output_filename)

# 3. '전체 경로'에 파일을 저장합니다.
extracted_panel_df.to_json(full_path, orient='records', indent=4, force_ascii=False)

print(f"\n 추출된 패널이 '{full_path}' 경로에 성공적으로 저장되었습니다.")