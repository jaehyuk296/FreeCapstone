import pandas as pd
import numpy as np
import os

# --- 1. 파일 읽기 및 컬럼 이름 지정 (한 번만 실행) ---
try:
    df = pd.read_excel('../../paneldata/Quickpoll/qpoll_join_250106.xlsx', skiprows=1)
    
    # 만약을 위해 컬럼 이름의 앞뒤 공백을 제거합니다.
    df.columns = df.columns.str.strip()
except Exception as e:
    print(f"❌ 파일 읽기 또는 컬럼 지정 중 에러 발생: {e}")
    exit()

# --- 2. '문항1'의 각 보기가 의미하는 것 정의 (코드북) ---
option_map = {
    '1': '헬스', '2': '홈트레이닝', '3': '요가/필라테스', '4': '달리기/걷기',
    '5': '자전거 타기', '6': '수영', '7': '스포츠(축구, 배드민턴 등)',
    '8': '등산', '9': '기타', '10': '없다'
}

# --- 3. 원-핫 인코딩 수행 (복수 응답 처리) ---
dummies = df['문항1'].astype(str).str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = df.drop('문항1', axis=1) # 원본 '문항1' 열 삭제
df = pd.concat([df, dummies], axis=1)

# --- 4. 카테고리 및 'is_exercising' 열 생성 ---
df['카테고리'] = '운동 안함' # 기본값 설정

if '헬스' in df.columns:
    df.loc[df['헬스'] == 1, '카테고리'] = '근력 운동'
if '홈트레이닝' in df.columns:
    df.loc[df['홈트레이닝'] == 1, '카테고리'] = '근력 운동'
if '요가/필라테스' in df.columns:
    df.loc[df['요가/필라테스'] == 1, '카테고리'] = '유연성 운동'
if '달리기/걷기' in df.columns:
    df.loc[df['달리기/걷기'] == 1, '카테고리'] = '유산소 운동'
if '자전거 타기' in df.columns:
    df.loc[df['자전거 타기'] == 1, '카테고리'] = '유산소 운동'
if '수영' in df.columns:
    df.loc[df['수영'] == 1, '카테고리'] = '유산소 운동'
if '스포츠(축구, 배드민턴 등)' in df.columns:
    df.loc[df['스포츠(축구, 배드민턴 등)'] == 1, '카테고리'] = '복합 운동'
if '등산' in df.columns:
    df.loc[df['등산'] == 1, '카테고리'] = '복합 운동'
if '기타' in df.columns:
    df.loc[df['기타'] == 1, '카테고리'] = '기타'
if '없다' in df.columns:
    df.loc[df['없다'] == 1, '카테고리'] = '운동 안함'

exercise_categories = ['근력 운동', '유연성 운동', '유산소 운동', '복합 운동', '기타']
df['is_exercising'] = df['카테고리'].isin(exercise_categories).astype(int)

# --- 5. 날짜 형식 변환 ---
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 6. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '헬스', '홈트레이닝', '요가/필라테스', '달리기/걷기', '자전거 타기',
    '수영', '스포츠(축구, 배드민턴 등)', '등산', '기타', '없다',
    '카테고리', 'is_exercising'
]
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()

# --- 7. 최종 JSON 저장 ---
output_folder = '../../json_extraction/qpoll_data/'
output_filename = '250106_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")

# --- 8. 요약 통계 출력 및 저장 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

total_people = len(final_df)
exercising_people = final_df['is_exercising'].sum()

print(f"실제 참여자 인원수: {total_people}명")
if total_people > 0:
    print(f"운동하는 사람 수: {exercising_people}명")
    print(f"운동하는 사람 비율: {exercising_people / total_people * 100:.2f}%")
print("-" * 30)

individual_options = list(option_map.values())
existing_options = [opt for opt in individual_options if opt in final_df.columns]

if existing_options:
    individual_counts = final_df[existing_options].sum().sort_values(ascending=False)
    print("각 보기별 응답 인원수:")
    print(individual_counts)
    print("-" * 30)

category_counts = final_df['카테고리'].value_counts()
print("카테고리별 인원수:")
print(category_counts)

# --- 9. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../json_extraction/qpoll_data/summary/'
stats_output_filename = '250106_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write("📊 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(f"실제 참여자 인원수: {total_people}명\n")
        if total_people > 0:
            f.write(f"운동하는 사람 수: {exercising_people}명\n")
            f.write(f"운동하는 사람 비율: {exercising_people / total_people * 100:.2f}%\n")
        f.write("-" * 30 + "\n\n")
        
        if existing_options:
            f.write("각 보기별 응답 인원수:\n")
            f.write(individual_counts.to_string() + "\n")
            f.write("-" * 30 + "\n\n")
            
        f.write("카테고리별 인원수:\n")
        f.write(category_counts.to_string())

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")

except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

