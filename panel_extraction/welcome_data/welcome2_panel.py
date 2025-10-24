import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = 'Welcome_2nd'
filepath = f'../../paneldata/Welcome/{FILE_ID}.xlsx'

# --- 2. 파일 읽기 ---
try:
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()
    print(f"✅ '{filepath}' 파일 읽기 성공.")
except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 3. 데이터 전처리 (Welcome_2nd 데이터 맞춤) ---

# 3-1. 컬럼 이름 변경
rename_map = {
    'mb_sn': '고유번호',
    'Q1': '결혼여부_코드', 'Q2': '자녀수_코드', 'Q3': '가족수_코드',
    'Q4': '최종학력_코드', 'Q5': '직업_코드', 'Q5_1': '직무_코드',
    'Q6': '월평균_개인소득_코드', 'Q7': '월평균_가구소득_코드',
    'Q8': '보유전자제품_코드', 'Q9_1': '보유휴대폰단말기_브랜드_코드',
    'Q9_2': '보유휴대폰모델명_코드', 'Q10': '보유차량여부_코드',
    'Q11': '자동차제조사_코드', 'Q11_2': '자동차모델_코드', 'Q12': '흡연경험_코드',
    'Q12_1': '흡연경험_담배브랜드_코드','Q12_1_ETC': '흡연경험_담배브랜드(기타브랜드)_코드', 
    'Q12_2': '궐련형 전자담배/가열식 전자담배 이용경험_코드',
    'Q12_2_ETC': '흡연경험_담배_브랜드(기타내용)_코드', 'Q13' : '음용경험_술_코드',
    'Q13_1': '음용경험_술(기타내용)_코드'
}
df = df.rename(columns=rename_map)

# 3-2. 코드북(Option Map) 정의
option_map_q1 = {1: '미혼', 2: '기혼', 3: '기타(사별/이혼 등)'}
option_map_q3 = {1: '1명', 2: '2명', 3: '3명', 4: '4명', 5: '5명 이상'}
option_map_q4 = {1: '고등학교 졸업 이하', 2: '대학교 재학(휴학 포함)', 3: '대학교 졸업', 4: '대학원 재학/졸업 이상'}
option_map_q5 = {
    1: '전문직 (의사, 간호사, 변호사, 회계사, 예술가, 종교인, 엔지니어, 프로그래머, 기술사 등)',
    2: '교직 (교수, 교사, 강사 등)',
    3: '경영/관리직 (사장, 대기업 간부, 고위 공무원 등)', 4: '사무직 (기업체 차장 이하 사무직 종사자, 공무원 등)',
    5: '자영업 (제조업, 건설업, 도소매업, 운수업, 무역업, 서비스업 경영)', 
    6: '판매직 (보험판매, 세일즈맨, 도/소매업 직원, 부동산 판매, 행상, 노점상 등)',
    7: '서비스직 (미용, 통신, 안내, 요식업 직원 등)', 8: '생산/노무직 (차량운전자, 현장직, 생산직 등)',
    9: '기능직 (기술직, 제빵업, 목수, 전기공, 정비사, 배관공 등)',
    10: '농업/임업/축산업/광업/수산업',
    11: '임대업', 12: '중/고등학생', 13: '대학생/대학원생', 14: '전업주부',
    15: '퇴직/연금생활자'
}
option_map_q8 = {
    '1': 'TV', '2': '냉장고', '3': '김치냉장고', '4': '세탁기', '5': '에어컨', '6': '제습기', '7': '공기청정기(에어 케어)',
    '8': '정수기', '9': '일반청소기', '10': '로봇청소기', '11': '무선청소기(예:다이슨, 코드제로, 제트 등)', '12': '커피 머신(에스프레소 머신, 캡슐커피 머신 등)', ''
    '13': '안마의자','14': '음식물처리기', '15': '비데', 
    '16': '의류 관리기(스타일러)', '17': '건조기', '18': '전기레인지(하이라이트, 인덕션, 핫플레이트 등)',
    '19': '식기세척기', '20': '에어프라이어', '21': '가정용 식물 재배기', '22': '노트북', '23': '태블릿PC (아이패드, 갤럭시 탭 등)', 
    '24': '데스크탑', '25': '무선 이어폰(예: 에어팟, 갤럭시 버즈 등)', 
    '26': '스마트 워치(예: 애플워치, 갤럭시 워치, 샤오미 등)', '27': '인공지능 AI 스피커',
    '28': '블루투스 스피커'
}


# 3-3. 각 문항별 전처리
# 단일 선택 문항 처리
df['결혼여부'] = df['결혼여부_코드'].map(option_map_q1)
df['가족수'] = df['가족수_코드'].map(option_map_q3)
df['최종학력'] = df['최종학력_코드'].map(option_map_q4)
df['직업'] = df['직업_코드'].map(option_map_q5)

# 자녀수 처리
df['자녀수'] = pd.to_numeric(df['자녀수_코드'], errors='coerce').fillna(0)
df['자녀유무'] = (df['자녀수'] > 0).astype(int)

# 보유전자제품 (복수 응답) 처리
dummies_q8 = df['보유전자제품_코드'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
dummies_q8 = dummies_q8.rename(columns=option_map_q8)
df = pd.concat([df, dummies_q8], axis=1)

print("📊 Welcome 데이터 처리 완료.")


# --- 4. 최종 데이터프레임 생성 ---
final_df = df.copy()


# --- 5. 최종 JSON 저장 ---
output_folder = '../../json_extraction/welcome_data/'
output_filename = f'{FILE_ID}_preprocessed.json'
os.makedirs(output_folder, exist_ok=True)
json_full_path = os.path.join(output_folder, output_filename)

final_df.to_json(json_full_path, orient='records', indent=4, force_ascii=False)
print(f"\n🎉 전처리가 완료된 전체 데이터가 '{json_full_path}' 경로에 JSON 파일로 저장되었습니다.")


# --- 6. 요약 통계 생성 및 출력 ---
print("\n" + "-"*30)
print("📊 요약 통계")
print("-" * 30)

stats_summary = []
total_people = len(final_df)
stats_summary.append(f"전체 인원수: {total_people}명")
stats_summary.append("-" * 30)

# 통계 추가
if '결혼여부' in final_df.columns:
    stats_summary.append("결혼여부별 인원수:")
    stats_summary.append(final_df['결혼여부'].value_counts().to_string())
    stats_summary.append("-" * 30)
if '직업' in final_df.columns:
    stats_summary.append("직업별 인원수:")
    stats_summary.append(final_df['직업'].value_counts().to_string())
    stats_summary.append("-" * 30)

q8_options = list(option_map_q8.values())
existing_q8 = [opt for opt in q8_options if opt in final_df.columns]
if existing_q8:
    q8_counts = final_df[existing_q8].sum().sort_values(ascending=False)
    stats_summary.append("보유 전자제품별 인원수 (상위 10개):")
    stats_summary.append(q8_counts.head(10).to_string())
    stats_summary.append("-" * 30)


final_stats_string = "\n".join(stats_summary)
print(final_stats_string)


# --- 7. 통계 결과를 .txt 파일로 저장 ---
stats_output_folder = '../../json_extraction/welcome_data/summary/'
stats_output_filename = f'{FILE_ID}_summary_stats.txt'
os.makedirs(stats_output_folder, exist_ok=True)
stats_full_path = os.path.join(stats_output_folder, stats_output_filename)

try:
    with open(stats_full_path, 'w', encoding='utf-8') as f:
        f.write(f"📊 {FILE_ID} 데이터 요약 통계\n")
        f.write("-" * 30 + "\n")
        f.write(final_stats_string)
    print(f"\n📈 요약 통계가 '{stats_full_path}' 경로에 저장되었습니다.")
except Exception as e:
    print(f"❌ 통계 파일 저장 중 에러 발생: {e}")

