import pandas as pd
import numpy as np
import os

# --- 1. 파일 읽기 및 컬럼 이름 지정 ---
try:
    df = pd.read_excel('../../../paneldata/Quickpoll/qpoll_join_250106.xlsx', skiprows=1)
    df.columns = df.columns.str.strip()
    print("✅ 파일 읽기 성공.")
except Exception as e:
    print(f"❌ 파일 읽기 또는 컬럼 지정 중 에러 발생: {e}")
    exit()

# --- 2. '문항1'의 각 보기가 의미하는 것 정의 (코드북) ---
option_map = {
    '1': '헬스', '2': '홈트레이닝', '3': '요가/필라테스', '4': '달리기/걷기',
    '5': '자전거 타기', '6': '수영', '7': '스포츠(축구, 배드민턴 등)',
    '8': '등산', '9': '기타', '10': '없다'
}

# --- 3. 원-핫 인코딩 수행 (★★★ 버그 수정된 부분 ★★★) ---
# '문항1' 열을 문자열로 변환하고, 
# str.replace(' ', '') : '8, 3, 4' -> '8,3,4' 처럼 모든 공백을 제거합니다.
# str.get_dummies(sep=',') : 공백이 제거된 문자열을 쉼표로 분리합니다.
dummies = df['문항1'].astype(str).str.strip().str.replace(' ', '').str.get_dummies(sep=',')

# 생성된 컬럼 이름('1', '2'...)을 실제 활동 이름('헬스', '홈트레이닝'...)으로 변경
dummies = dummies.rename(columns=option_map)
df = df.drop('문항1', axis=1) # 원본 '문항1' 열 삭제
df = pd.concat([df, dummies], axis=1)
print("✅ 원-핫 인코딩 완료 (공백 문제 해결).")


# --- 4. 카테고리 및 '체력_관리_유무' 열 생성 (중복 답변 처리 수정본) ---

# 각 카테고리별로 해당하는지 boolean 값(True/False)을 미리 계산
is_strength = (df.get('헬스', 0) == 1) | (df.get('홈트레이닝', 0) == 1)
is_flexibility = df.get('요가/필라테스', 0) == 1
is_cardio = (df.get('달리기/걷기', 0) == 1) | (df.get('자전거 타기', 0) == 1) | (df.get('수영', 0) == 1)
is_complex_sports = (df.get('스포츠(축구, 배드민턴 등)', 0) == 1) | (df.get('등산', 0) == 1)
is_etc = df.get('기타', 0) == 1
is_none = df.get('없다', 0) == 1

# 몇 종류의 운동을 선택했는지 합산 (True=1, False=0)
exercise_type_count = (
    is_strength.astype(int) + 
    is_flexibility.astype(int) + 
    is_cardio.astype(int) + 
    is_complex_sports.astype(int) + 
    is_etc.astype(int)
)

# 1. 우선순위에 따른 조건 리스트
conditions = [
    is_none,                                # 1순위: '없다'를 선택한 경우
    exercise_type_count > 1,                  # 2순위: 운동 종류를 2가지 이상 선택한 경우
    is_complex_sports,                        # 3순위: '스포츠' 또는 '등산'을 선택한 경우
    is_strength,                              # 4순위: 근력 운동
    is_flexibility,                           # 5순위: 유연성 운동
    is_cardio,                                # 6순위: 유산소 운동
    is_etc                                    # 7순위: 기타
]

# 2. 각 조건에 해당하는 결과 리스트
choices = [
    '운동 안함',
    '복합 운동',
    '복합 운동',
    '근력 운동',
    '유연성 운동',
    '유산소 운동',
    '기타'
]

# 3. np.select로 카테고리 할당 (조건에 모두 안 맞으면 '운동 안함')
df['카테고리'] = np.select(conditions, choices, default='운동 안함')

# '체력_관리_유무' 열 생성 (1 또는 0)
exercise_categories = ['근력 운동', '유연성 운동', '유산소 운동', '복합 운동', '기타']
df['체력_관리_유무'] = df['카테고리'].isin(exercise_categories).astype(int)
print("✅ '카테고리' 및 '체력_관리_유무' 열 생성 완료 (중복 응답 처리됨).")


# --- 5. 요약 컬럼 생성 및 값 변환 ---

# 1. '운동' 요약 컬럼 생성 (중복 답변 시 "헬스, 등산" 등으로 표시)
exercise_names = [name for key, name in option_map.items() if key != '10' and name in df.columns]

def get_exercise_summary(row):
    # '없다'가 1이면 '없음'을 반환
    if '없다' in df.columns and row['없다'] == 1:
        return '없음'
    
    selected_exercises = []
    # '없다'를 제외한 운동 이름들을 순회
    for name in exercise_names:
        # 버그가 해결되어 '요가/필라테스', '달리기/걷기', '등산' 모두 1로 잘 잡힙니다.
        if row[name] == 1:
            selected_exercises.append(name)
            
    if selected_exercises:
        # 리스트에 쌓인 모든 항목을 쉼표로 묶어 반환
        return ', '.join(sorted(selected_exercises))
    else:
        # '없다'도 아니고 다른 운동도 선택 안 한 경우
        return '선택 없음' 

df['운동'] = df.apply(get_exercise_summary, axis=1)

# 2. '체력_관리_유무' 값을 1/0에서 '있다'/'없다'로 변경
df['체력_관리_유무'] = df['체력_관리_유무'].map({1: '있다', 0: '없다'}).fillna('없다')
print("✅ '운동' 요약 컬럼 생성 및 '체력_관리_유무' 값 변환 완료.")


# --- 6. 날짜 형식 변환 ---
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 7. 최종 컬럼 선택 (요약 컬럼과 카테고리 모두 포함) ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '운동',         # "달리기/걷기, 등산, 요가/필라테스" 처럼 모든 응답이 나열됨
    '카테고리',     # "복합 운동" 처럼 분류된 결과가 나옴
    '체력_관리_유무' 
]
# 혹시 원본 파일에 '구분', '성별' 등의 컬럼이 없을 경우를 대비하여, 있는 컬럼만 선택
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()

# --- 8. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jan/'
output_filename = '250106_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

# JSON 저장을 위해 datetime 형식을 문자열로 변환
json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')

# JSON 파일로 저장
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)

print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")