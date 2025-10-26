import pandas as pd
import numpy as np
import os

# --- 1. 파일 경로 및 ID 설정 ---
FILE_ID = '250204' # 새로운 파일 ID로 변경
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

# --- 3. 데이터 전처리 ('겨울방학 추억' 맞춤 - 복수 응답 처리) ---
option_map = {
    '1': '가족과 함께 떠난 여행',
    '2': '겨울방학 숙제를 하던 순간',
    '3': '방학 동안 다녔던 학원이나 특별 활동',
    '4': '친구들과 보낸 즐거운 시간',
    '5': '눈썰매, 스키 등 겨울 스포츠',
    '6': '눈사람 만들기',
    '7': '기타'
}

# 원-핫 인코딩 수행
# '문항1' 열을 문자열로 변환하고, 공백 제거 후 쉼표를 기준으로 분리합니다.
dummies = df['문항1'].astype(str).str.replace(' ', '').str.get_dummies(sep=',')
# 생성된 컬럼 이름을 실제 활동 이름으로 변경
dummies = dummies.rename(columns=option_map)

# 원래 데이터프레임에 새로 만든 컬럼들을 합치기 (원본 '문항1'은 삭제)
df = pd.concat([df.drop('문항1', axis=1), dummies], axis=1)

# 선택한 모든 활동을 하나의 문자열로 합치는 함수
def get_all_memories(row):
    memories = []
    for option_text in option_map.values():
        if option_text in row and row[option_text] == 1:
            memories.append(option_text)
    return ', '.join(sorted(memories)) if memories else '선택 없음'

# '기억에_남는_일' 열 생성
df['기억에_남는_일'] = df.apply(get_all_memories, axis=1)

# '설문일시' 열을 datetime 형식으로 변환
df['설문일시'] = pd.to_datetime(df['설문일시'], errors='coerce')

print("思い出 '겨울방학 추억' 데이터 처리 완료.")


# --- 4. 최종 컬럼 선택 ---
final_columns = [
    '구분', '고유번호', '성별', '나이', '지역', '설문일시',
    '기억에_남는_일'
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


