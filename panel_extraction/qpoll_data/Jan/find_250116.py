import pandas as pd
import numpy as np
import os

# --- 1. 파일 읽기 ---
try:
    # 새로운 데이터 파일 경로로 수정
    df = pd.read_excel('../../../paneldata/Quickpoll/qpoll_join_250116.xlsx', skiprows=1)
    df.columns = df.columns.str.strip()
except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 2. '문항1'의 각 보기가 의미하는 것 정의 (코드북) ---
option_map = {
    1: '주1회 이상',
    2: '2주1회 이상',
    3: '월1회 이상',
    4: '3개월1회 이상',
    5: '6개월1회 이상',
    6: '연1회 이상',
    7: '방문안함'
}

# --- 3. 데이터 변환 및 'is_visiting_market' 열 생성 ---

# '문항1' 열을 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
df['문항1'] = pd.to_numeric(df['문항1'], errors='coerce')

# '방문빈도' 열 생성: 숫자 답변을 텍스트로 변환
df['방문빈도'] = df['문항1'].map(option_map)

# 'is_visiting_market' 열 생성: '방문안함'이 아니면 1, '방문안함'이면 0
df['is_visiting_market'] = (df['방문빈도'] != '방문안함').astype(int)


# --- 4. 날짜 형식 변환 ---
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 5. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '방문빈도', 'is_visiting_market'
]
existing_final_columns = [col for col in final_columns if col in df.columns]
final_df = df[existing_final_columns].copy()

# --- 6. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Jan/'
output_filename = '250116_preprocessed_data.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

json_df = final_df.copy()
json_df['설문일시'] = json_df['설문일시'].dt.strftime('%Y-%m-%d %I:%M:%S %p').fillna('')
json_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")

# --- 7. 요약 통계 출력 및 저장 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

total_people = len(final_df)
visiting_people = final_df['is_visiting_market'].sum()

print(f"실제 참여자 인원수: {total_people}명")
if total_people > 0:
    print(f"전통시장 방문자 수: {visiting_people}명")
    print(f"전통시장 방문자 비율: {visiting_people / total_people * 100:.2f}%")
print("-" * 30)

frequency_counts = final_df['방문빈도'].value_counts()
print("방문 빈도별 인원수:")
print(frequency_counts)

# --- 8. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Jan/summary/'
stats_output_filename = '250116_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write("📊 전통시장 방문 현황 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(f"실제 참여자 인원수: {total_people}명\n")
        if total_people > 0:
            f.write(f"전통시장 방문자 수: {visiting_people}명\n")
            f.write(f"전통시장 방문자 비율: {visiting_people / total_people * 100:.2f}%\n")
        f.write("-" * 30 + "\n\n")
        
        f.write("방문 빈도별 인원수:\n")
        f.write(frequency_counts.to_string())

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")

except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

