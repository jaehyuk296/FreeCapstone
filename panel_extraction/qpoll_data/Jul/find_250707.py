import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250707' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('초콜릿 섭취' 맞춤) ---
option_map = {
    1: '스트레스를 받을 때',
    2: '기분이 좋을 때',
    3: '간식으로 습관처럼',
    4: '선물로 받았을 때',
    5: '특별한 날(생일, 발렌타인데이 등)',
    6: '기타',
    7: '거의 먹지 않는다'
}

# '문항1' 열을 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
df['문항1'] = pd.to_numeric(df['문항1'], errors='coerce')

# '초콜릿_섭취_상황' 열 생성: 숫자 답변을 텍스트로 변환
df['초콜릿_섭취_상황'] = df['문항1'].map(option_map)

# '초콜릿_섭취_여부' 열 생성: 섭취하면 1, 안 하면 0
df['초콜릿_섭취_여부'] = (df['초콜릿_섭취_상황'] != '거의 먹지 않는다').astype(int)


# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 4. 더 이상 필요 없는 원본 문항 컬럼 삭제 ---
df = df.drop(columns=['문항1'], errors='ignore')

print("🍫 '초콜릿 섭취' 데이터 처리 완료.")


# --- 5. 최종 데이터프레임 생성 ---
final_df = df.copy()


# --- 6. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jul/'
output_filename = f'{FILE_ID}_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 7. 요약 통계 생성 및 출력 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

# 통계 내용을 담을 문자열 변수 생성
stats_summary = []

total_people = len(final_df)
stats_summary.append(f"실제 참여자 인원수: {total_people}명")

if '초콜릿_섭취_여부' in final_df.columns:
    eater_count = final_df['초콜릿_섭취_여부'].sum()
    if total_people > 0:
        stats_summary.append(f"초콜릿 섭취자 수: {eater_count}명")
        stats_summary.append(f"초콜릿 섭취자 비율: {eater_count / total_people * 100:.2f}%")
stats_summary.append("-" * 30)


if '초콜릿_섭취_상황' in final_df.columns:
    situation_counts = final_df['초콜릿_섭취_상황'].value_counts()
    stats_summary.append("섭취 상황별 인원수:")
    stats_summary.append(situation_counts.to_string())
    stats_summary.append("-" * 30)


# 생성된 통계 문자열을 화면에 출력
final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 8. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Jul/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 초콜릿 섭취 현황 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

