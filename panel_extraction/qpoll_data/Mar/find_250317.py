import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250317' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('AI 챗봇' 맞춤) ---

# '문항1' (사용 경험)에 대한 코드북
option_map_q1 = {
    '1': 'ChatGPT', '2': '딥서치', '3': 'Gemini (구글)', '4': 'Claude (Anthropic)',
    '5': 'Copilot (마이크로소프트)', '6': 'HyperCLOVA X (네이버)', '7': '기타_경험', '8': '사용해본 경험 없음'
}

# '문항2' (주요 사용)에 대한 코드북
option_map_q2 = {
    1: 'ChatGPT', 2: '딥서치', 3: 'Gemini (구글)', 4: 'Claude (Anthropic)',
    5: 'Copilot (마이크로소프트)', 6: 'HyperCLOVA X (네이버)', 7: '기타_주요사용', 8: '사용해본 경험 없음'
}

# '문항3' (활용 용도)에 대한 코드북
option_map_q3 = {
    1: '정보 검색 및 질문 해결', 2: '업무 보조 (문서작성, 분석 등)', 3: '데이터 분석 및 학습 도움',
    4: '번역 및 언어 학습', 5: '창작 활동 (글쓰기, 아이디어 등)', 6: '이미지 생성',
    7: '개인 비서 (일정 관리, 메모)', 8: '코딩 및 프로그래밍 도움', 9: '기타_용도'
}

# '문항4' (선호 서비스)에 대한 코드북
option_map_q4 = { 1: 'ChatGPT', 2: '딥서치' }


# '문항1' - 복수 응답 처리 (원-핫 인코딩)
dummies_q1 = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
dummies_q1 = dummies_q1.rename(columns=option_map_q1)
df = pd.concat([df, dummies_q1], axis=1)

# '문항2' - 단일 응답 처리
df['문항2'] = pd.to_numeric(df['문항2'], errors='coerce')
df['주요_사용_챗봇'] = df['문항2'].map(option_map_q2)

# '문항3' - 단일 응답 처리 (수정됨)
df['문항3'] = pd.to_numeric(df['문항3'], errors='coerce')
df['활용_용도'] = df['문항3'].map(option_map_q3)

# '문항4' - 단일 응답 처리
df['문항4'] = pd.to_numeric(df['문항4'], errors='coerce')
df['선호_서비스'] = df['문항4'].map(option_map_q4)


# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

# --- 4. 더 이상 필요 없는 원본 문항 컬럼 삭제 ---
df = df.drop(columns=['문항1', '문항2', '문항3', '문항4'], errors='ignore')

print("🤖 'AI 챗봇' 데이터 처리 완료.")


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

# 문항1 통계 (복수 응답)
q1_options = list(option_map_q1.values())
existing_q1 = [opt for opt in q1_options if opt in final_df.columns]
if existing_q1:
    q1_counts = final_df[existing_q1].sum().sort_values(ascending=False)
    stats_summary.append("AI 챗봇 사용 경험 (중복 응답):")
    stats_summary.append(q1_counts.to_string())
    stats_summary.append("-" * 30)

# 문항2 통계 (단일 응답)
if '주요_사용_챗봇' in final_df.columns:
    q2_counts = final_df['주요_사용_챗봇'].value_counts()
    stats_summary.append("주로 사용하는 AI 챗봇:")
    stats_summary.append(q2_counts.to_string())
    stats_summary.append("-" * 30)

# 문항3 통계 (단일 응답 - 수정됨)
if '활용_용도' in final_df.columns:
    q3_counts = final_df['활용_용도'].value_counts()
    stats_summary.append("AI 챗봇 활용 용도:")
    stats_summary.append(q3_counts.to_string())
    stats_summary.append("-" * 30)

# 문항4 통계 (단일 응답)
if '선호_서비스' in final_df.columns:
    q4_counts = final_df['선호_서비스'].value_counts()
    stats_summary.append("선호 서비스:")
    stats_summary.append(q4_counts.to_string())
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
        f.write(f"📊 {FILE_ID} AI 챗봇 사용 현황 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)

    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

