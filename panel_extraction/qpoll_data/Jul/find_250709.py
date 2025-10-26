import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250709' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('개인정보보호 습관' 맞춤 - 복수 응답 처리) ---
option_map = {
    '1': '비밀번호 주기적 변경',
    '2': '2단계 인증(OTP 등) 설정/사용',
    '3': '의심스러운 링크/앱 클릭 안 함',
    '4': '공공 와이파이 사용 자제',
    '5': '개인정보 제공 동의 시 꼼꼼히 읽음',
    '6': '기타',
    '7': '따로 신경쓰는 게 없다'
}

# 원-핫 인코딩 수행 (통계 계산용)
dummies = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = pd.concat([df.drop('문항1', axis=1), dummies], axis=1)

# '개인정보보호_노력여부' (1/0) 열 생성 (통계용)
df['개인정보보호_노력여부_binary'] = (df.get('따로 신경쓰는 게 없다', 0) == 0).astype(int)

# (★★★ 추가된 부분 ★★★)
# 1. JSON용 '보호_습관_요약' 컬럼 생성
def get_all_habits(row):
    # '따로 신경쓰는 게 없다'가 1이면, 다른 걸 선택했어도 이 응답을 우선
    if row.get('따로 신경쓰는 게 없다', 0) == 1:
        return '따로 신경쓰는 게 없다'
    
    habits = []
    # '따로 신경쓰는 게 없다'를 제외한 나머지 항목들을 순회
    for key, name in option_map.items():
        if key != '7' and row.get(name, 0) == 1:
            habits.append(name)
            
    if habits:
        return ', '.join(sorted(habits))
    else:
        return '선택 없음' # '신경 안 씀'도 아니고 다른 것도 선택 안 한 경우

df['보호_습관_요약'] = df.apply(get_all_habits, axis=1)

# 2. JSON용 '개인정보보호_노력여부' 텍스트 컬럼 생성
df['개인정보보호_노력여부'] = df['개인정보보호_노력여부_binary'].map({
    1: '노력함',
    0: '노력 안 함'
}).fillna('노력 안 함')


# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("🔒 '개인정보보호 습관' 데이터 처리 완료.")


# (★★★ 수정된 부분 ★★★)
# --- 4. 최종 데이터프레임 생성 (JSON 저장용) ---
# JSON에 저장할 컬럼만 선택합니다. (요약 컬럼만 포함)
json_final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '보호_습관_요약',
    '개인정보보호_노력여부'
]
existing_json_columns = [col for col in json_final_columns if col in df.columns]
json_df = df[existing_json_columns].copy()


# --- 5. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jul/'
output_filename = f'{FILE_ID}_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# (★★★ 수정된 부분 ★★★)
# --- 6. 요약 통계 생성 및 출력 ---
# 통계는 1/0 컬럼이 있는 원본 'df'를 사용합니다.
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

stats_summary = []
total_people = len(df) # 원본 df 사용
stats_summary.append(f"실제 참여자 인원수: {total_people}명")

# 통계 계산 시 1/0 컬럼인 '개인정보보호_노력여부_binary' 사용
if '개인정보보호_노력여부_binary' in df.columns:
    effort_makers = df['개인정보보호_노력여부_binary'].sum()
    if total_people > 0:
        stats_summary.append(f"노력하는 사람 수: {effort_makers}명")
        stats_summary.append(f"노력하는 사람 비율: {effort_makers / total_people * 100:.2f}%")
stats_summary.append("-" * 30)


# 각 보기별 응답 인원수 계산 (원본 df 사용)
habit_options = list(option_map.values())
existing_options = [opt for opt in habit_options if opt in df.columns]

if existing_options:
    habit_counts = df[existing_options].sum().sort_values(ascending=False)
    stats_summary.append("보호 습관별 인원수 (중복 응답):")
    stats_summary.append(habit_counts.to_string())
    stats_summary.append("-" * 30)


# 생성된 통계 문자열을 화면에 출력
final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 7. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Jul/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 개인정보보호 습관 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")