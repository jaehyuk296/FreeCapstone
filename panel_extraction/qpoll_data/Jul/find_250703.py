import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250703' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('일회용품 줄이기' 맞춤 - 복수 응답 처리) ---
option_map = {
    '1': '장바구니나 에코백을 챙긴다',
    '2': '비닐 대신 종이봉투나 박스를 이용한다',
    '3': '쇼핑할 때 봉투를 받지 않는다',
    '4': '편의점이나 마트에서 유료 봉투를 아낀다',
    '5': '기타',
    '6': '따로 노력하고 있지 않다'
}

# 원-핫 인코딩 수행
dummies = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = pd.concat([df.drop('문항1', axis=1), dummies], axis=1)

# '친환경_노력_여부' 열 생성: '따로 노력하고 있지 않다'를 선택하지 않았으면 1, 선택했으면 0
df['친환경_노력_여부'] = (df.get('따로 노력하고 있지 않다', 0) == 0).astype(int)


# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("♻️ '일회용품 줄이기' 데이터 처리 완료.")


# --- 4. 최종 데이터프레임 생성 ---
final_df = df.copy()


# --- 5. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jul/'
output_filename = f'{FILE_ID}_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 6. 요약 통계 생성 및 출력 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

# 통계 내용을 담을 문자열 변수 생성
stats_summary = []

total_people = len(final_df)
stats_summary.append(f"실제 참여자 인원수: {total_people}명")

if '친환경_노력_여부' in final_df.columns:
    effort_makers = final_df['친환경_노력_여부'].sum()
    if total_people > 0:
        stats_summary.append(f"노력하는 사람 수: {effort_makers}명")
        stats_summary.append(f"노력하는 사람 비율: {effort_makers / total_people * 100:.2f}%")
stats_summary.append("-" * 30)


# 각 보기별 응답 인원수 계산
effort_options = list(option_map.values())
existing_options = [opt for opt in effort_options if opt in final_df.columns]

if existing_options:
    effort_counts = final_df[existing_options].sum().sort_values(ascending=False)
    stats_summary.append("노력 유형별 인원수 (중복 응답):")
    stats_summary.append(effort_counts.to_string())
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
        f.write(f"📊 {FILE_ID} 일회용품 줄이기 노력 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

