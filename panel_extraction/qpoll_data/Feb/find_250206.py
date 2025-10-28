import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250206' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('반려동물 경험' 맞춤) ---
option_map = {
    1: '현재 키우는 중',
    2: '과거에 키워본 경험 있음',
    3: '키워본 경험 없음'
}

# '문항1' 열을 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
df['문항1'] = pd.to_numeric(df['문항1'], errors='coerce')

# '반려동물_경험' 열 생성: 숫자 답변을 텍스트로 변환
df['반려동물_경험'] = df['문항1'].map(option_map)

# '반려동물_경험유무' 열 생성: 경험이 없으면 0, 있으면 1
df['반려동물_경험유무'] = (df['반려동물_경험'] != '키워본 경험 없음').astype(int)

# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("🐶 '반려동물 경험' 데이터 처리 완료.")


# --- 4. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '반려동물_경험', '반려동물_경험유무'
]
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()

# --- 5. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Feb/'
output_filename = f'{FILE_ID}_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")
