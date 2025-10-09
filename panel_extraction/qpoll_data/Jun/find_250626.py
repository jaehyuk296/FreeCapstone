import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250626' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('AI 활용 분야' 맞춤 - 복수 응답 처리) ---
option_map = {
    '1': '업무 보조(문서 작성, 이메일 등)',
    '2': '학습/공부 보조',
    '3': '번역이나 외국어 학습',
    '4': '이미지 생성 또는 디자인 참고',
    '5': '디지털 콘텐츠 제작(블로그, 영상 기획 등)',
    '6': '검색/정보 탐색',
    '7': '기타',
    '8': 'AI 서비스를 사용해 본 적 없다'
}

# 원-핫 인코딩 수행
dummies = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
dummies = dummies.rename(columns=option_map)
df = pd.concat([df.drop('문항1', axis=1), dummies], axis=1)

# 'AI_사용여부' 열 생성: '사용해 본 적 없다'를 선택하지 않았으면 1, 선택했으면 0
df['AI_사용여부'] = (df.get('AI 서비스를 사용해 본 적 없다', 0) == 0).astype(int)


# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("🤖 'AI 활용 분야' 데이터 처리 완료.")


# --- 4. 최종 데이터프레임 생성 ---
final_df = df.copy()


# --- 5. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jun/'
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

if 'AI_사용여부' in final_df.columns:
    ai_users = final_df['AI_사용여부'].sum()
    if total_people > 0:
        stats_summary.append(f"AI 서비스 이용자 수: {ai_users}명")
        stats_summary.append(f"AI 서비스 이용자 비율: {ai_users / total_people * 100:.2f}%")
stats_summary.append("-" * 30)


# 각 보기별 응답 인원수 계산
usage_options = list(option_map.values())
existing_options = [opt for opt in usage_options if opt in final_df.columns]

if existing_options:
    usage_counts = final_df[existing_options].sum().sort_values(ascending=False)
    stats_summary.append("활용 분야별 인원수 (중복 응답):")
    stats_summary.append(usage_counts.to_string())
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
        f.write(f"📊 {FILE_ID} AI 서비스 활용 분야 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

