import pandas as pd
import numpy as np
import os

# --- 1. 파일 읽기 (수정됨) ---
try:
    # skiprows=1 옵션: 엑셀 파일의 맨 위 1줄(질문)을 건너뛰고 데이터를 읽어옵니다.
    # 이렇게 하면 2번째 줄이 자동으로 컬럼 이름(헤더)으로 지정됩니다.
    df = pd.read_excel('../../paneldata/Quickpoll/qpoll_join_250106.xlsx', skiprows=1)
    
    # 컬럼 이름의 앞뒤 공백을 제거하여 안정성을 높입니다.
    df.columns = df.columns.str.strip()

except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()
# --- 2. 데이터 전처리 ---
# 고유 번호 없는거 그냥 내버려둠

# --- 3. '문항1'의 각 보기가 의미하는 것 정의 (코드북) ---
option_map = {
    '1': '헬스', '2': '홈트레이닝', '3': '요가/필라테스', '4': '달리기/걷기',
    '5': '자전거 타기', '6': '수영', '7': '스포츠(축구, 배드민턴 등)',
    '8': '등산', '9': '기타', '10': '없다'
}

# --- 4. 원-핫 인코딩 수행 (복수 응답 처리) ---
# '문항1' 열을 문자열로 변환하고, 모든 공백을 제거한 뒤, 쉼표를 기준으로 분리합니다.
dummies = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')


# 생성된 컬럼 이름('1', '2'...)을 실제 활동 이름('헬스', '홈트레이닝'...)으로 변경
dummies = dummies.rename(columns=option_map)

# 원래 데이터프레임에 새로 만든 컬럼들을 합치기 (원본 '문항1'은 삭제)
df = pd.concat([df.drop('문항1', axis=1), dummies], axis=1)

# --- 5. 카테고리 및 'is_exercising' 열 생성 (복수 응답 처리 로직으로 수정) ---

# 각 행을 분석하여 해당하는 모든 카테고리를 찾아내는 함수를 정의합니다.
def determine_categories(row):
    categories = set() # 중복을 방지하기 위해 set 사용
    
    # '없다'를 선택한 경우, 다른 것을 선택했더라도 '운동 안함'으로 처리
    if row.get('없다', 0) == 1:
        return '운동 안함'
        
    # 각 조건에 해당하는 카테고리를 set에 추가
    if row.get('헬스', 0) == 1 or row.get('홈트레이닝', 0) == 1:
        categories.add('근력 운동')
    if row.get('요가/필라테스', 0) == 1:
        categories.add('유연성 운동')
    if row.get('달리기/걷기', 0) == 1 or row.get('자전거 타기', 0) == 1 or row.get('수영', 0) == 1:
        categories.add('유산소 운동')
    if row.get('스포츠(축구, 배드민턴 등)', 0) == 1 or row.get('등산', 0) == 1:
        categories.add('복합 운동')
    if row.get('기타', 0) == 1:
        categories.add('기타')

    # 모든 운동을 확인한 후에도 카테고리가 비어있다면 '운동 안함'으로 처리
    if not categories:
        return '운동 안함'
    
    # 찾은 카테고리들을 정렬 후, ', '로 연결하여 하나의 문자열로 반환
    return ', '.join(sorted(list(categories)))

# 위에서 정의한 함수를 모든 행에 적용하여 '카테고리' 열 생성
df['카테고리'] = df.apply(determine_categories, axis=1)

# '카테고리'가 '운동 안함'이 아니면 'is_exercising'을 1로 설정
df['is_exercising'] = (df['카테고리'] != '운동 안함').astype(int)


# --- 6. 날짜 형식 변환 ---
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 7. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '헬스', '홈트레이닝', '요가/필라테스', '달리기/걷기', '자전거 타기',
    '수영', '스포츠(축구, 배드민턴 등)', '등산', '기타', '없다',
    '카테고리', 'is_exercising'
]
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()


# --- 8. 최종 JSON 저장 ---
output_folder = '../../json_extraction/qpoll_data/'
output_filename = '250106_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

# JSON 저장을 위해 날짜를 문자열로 변환한 복사본을 만듭니다.
json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 9. 요약 통계 출력 및 저장 ---
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

# --- 10. 통계 결과를 .txt 파일로 저장 ---
stats_output_filename = '250106_summary_stats.txt'
output_folder = '../../json_extraction/qpoll_data/summary/'
os.makedirs(output_folder, exist_ok=True)
stats_full_path = os.path.join(output_folder, stats_output_filename)

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

