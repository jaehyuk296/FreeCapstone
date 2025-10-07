import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250310' # 스킨케어 데이터 ID
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

# --- 3. 데이터 전처리 ('스킨케어' 맞춤) ---

# '문항1' (피부 만족도)에 대한 코드북
option_map_q1 = {
    '1': '매우 만족한다', '2': '만족한다', '3': '보통이다',
    '4': '불만족한다', '5': '매우 불만족한다'
}

# '문항2' (스킨케어 소비금액)에 대한 코드북
option_map_q2 = {
    1: '3만원 미만', 2: '3만원 이상 ~ 5만원 미만', 3: '5만원 이상 ~ 10만원 미만',
    4: '10만원 이상 ~ 15만원 미만', 5: '15만원 이상'
}

# '문항3' (구매 고려 요소)에 대한 코드북
option_map_q3 = {
    1: '브랜드 명성', 2: '제품 리뷰 및 사용후기', 3: '성분 및 효과',
    4: '가격', 5: '패키지 디자인', 6: '친환경/비건 제품 여부', 7: '기타'
}

# '문항1'에 대한 원-핫 인코딩 수행 (복수 응답 처리)
dummies_q1 = (df['문항1'].astype(str).str.replace(' ', '')
              .str.split(',').explode()
              .str.strip()
              .str.get_dummies()
              .groupby(level=0).sum())
dummies_q1 = dummies_q1.rename(columns=option_map_q1)
df = pd.concat([df, dummies_q1], axis=1)

# 선택한 모든 만족도를 하나의 문자열로 합치는 함수
def get_all_satisfactions(row):
    satisfactions = []
    for option_text in option_map_q1.values():
        if option_text in row and row[option_text] == 1:
            satisfactions.append(option_text)
    return ', '.join(sorted(satisfactions)) if satisfactions else '선택 없음'
df['피부만족도_요약'] = df.apply(get_all_satisfactions, axis=1)


# '문항2', '문항3'을 각각 숫자형으로 변환 (단일 응답 처리)
df['문항2'] = pd.to_numeric(df['문항2'], errors='coerce')
df['문항3'] = pd.to_numeric(df['문항3'], errors='coerce')

# 단일 선택 문항에 대한 새로운 텍스트 열 생성
df['스킨케어_소비금액'] = df['문항2'].map(option_map_q2)
df['구매_고려_요소'] = df['문항3'].map(option_map_q3)

# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 4. 더 이상 필요 없는 원본 문항 컬럼 삭제 ---
df = df.drop(columns=['문항1', '문항2', '문항3'], errors='ignore')

print("💅 '스킨케어' 데이터 처리 완료.")


# --- 5. 최종 데이터프레임 생성 ---
final_df = df.copy()


# --- 6. 최종 JSON 저장 ---
output_folder = '../../../json_extraction/qpoll_data/Mar/'
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
stats_summary.append("-" * 30)

# 피부 만족도 통계 (복수 응답)
satisfaction_options = list(option_map_q1.values())
existing_satisfactions = [opt for opt in satisfaction_options if opt in final_df.columns]
if existing_satisfactions:
    satisfaction_counts = final_df[existing_satisfactions].sum().sort_values(ascending=False)
    stats_summary.append("피부 만족도별 인원수 (중복 응답):")
    stats_summary.append(satisfaction_counts.to_string())
    stats_summary.append("-" * 30)

# 스킨케어 소비금액 통계
if '스킨케어_소비금액' in final_df.columns:
    spending_counts = final_df['스킨케어_소비금액'].value_counts()
    stats_summary.append("스킨케어 소비금액별 인원수:")
    stats_summary.append(spending_counts.to_string())
    stats_summary.append("-" * 30)

# 구매 고려 요소 통계
if '구매_고려_요소' in final_df.columns:
    factor_counts = final_df['구매_고려_요소'].value_counts()
    stats_summary.append("구매 고려 요소별 인원수:")
    stats_summary.append(factor_counts.to_string())

    if not factor_counts.empty:
        most_important_factor = factor_counts.index[0]
        stats_summary.append(f"\n=> 가장 중요하게 보는 요소: {most_important_factor} ({int(factor_counts.iloc[0])}명)")
    stats_summary.append("-" * 30)

# 생성된 통계 문자열을 화면에 출력
final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 8. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../../json_extraction/qpoll_data/Mar/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 스킨케어 관련 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string) # 화면에 출력한 통계 문자열을 그대로 파일에 씀

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

