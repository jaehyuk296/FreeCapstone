import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250226' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('주요 사용 앱' 맞춤) ---
option_map = {
    1: 'SNS 앱 (인스타그램, 페이스북 등)',
    2: '숏폼/동영상 스트리밍 앱 (유튜브, 넷플릭스 등)',
    3: '커뮤니케이션 앱 (카카오톡, 문자 등)',
    4: '쇼핑/중고거래 앱 (쿠팡, 배달의민족, 당근 등)',
    5: '금융 앱',
    6: '건강/운동 앱',
    7: '게임 앱',
    8: '기타'
}

# '문항1' 열을 숫자형으로 변환 (숫자가 아닌 값은 NaN으로 처리)
df['문항1'] = pd.to_numeric(df['문항1'], errors='coerce')

# '주요_사용_앱' 열 생성: 숫자 답변을 텍스트로 변환
df['주요_사용_앱'] = df['문항1'].map(option_map)

# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("📱 '주요 사용 앱' 데이터 처리 완료.")


# --- 4. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '주요_사용_앱'
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


# --- 6. 요약 통계 출력 및 저장 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

total_people = len(final_df)
app_counts = final_df['주요_사용_앱'].value_counts()

print(f"실제 참여자 인원수: {total_people}명")
print("-" * 30)
print("앱 유형별 인원수:")
print(app_counts)


# --- 7. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Feb/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 주요 사용 앱 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(f"실제 참여자 인원수: {total_people}명\n")
        f.write("-" * 30 + "\n\n")
        f.write("앱 유형별 인원수:\n")
        f.write(app_counts.to_string())
    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

