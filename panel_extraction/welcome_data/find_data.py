import pandas as pd
import os

# --- 1. 파일 경로 설정 ---
filepath = '../../paneldata/Welcome/Welcome_2nd.xlsx'
output_folder = '../../json_extraction/welcome_data/summary/'
output_filename = 'Welcome_2nd_Q11_2_counts_sorted_by_name.txt'

# --- 2. 엑셀 파일 읽기 (에러 처리 추가) ---
try:
    df = pd.read_excel(filepath)
    print(f"✅ '{filepath}' 파일 읽기 성공.")
except FileNotFoundError:
    print(f"❌ 에러: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {filepath}")
    exit() # 파일이 없으면 프로그램 종료
except Exception as e:
    print(f"❌ 파일 읽기 중 에러 발생: {e}")
    exit()

# --- 3. 전체 인원수 계산 및 출력 ---
total_people = len(df)
print(f"전체 인원수: {total_people}명")
print("-" * 30)

# --- 4. 특정 열의 데이터 값 개수 계산 및 이름 순으로 정렬하여 출력 ---
target_column = 'Q11'

if target_column in df.columns:
    # --- ✨ 에러 수정 부분 ✨ ---
    # 정렬하기 전에 모든 데이터를 문자열(str) 타입으로 변환합니다.
    df[target_column] = df[target_column].astype(str)

    # value_counts() 결과에 .sort_index()를 추가하여 이름 순으로 정렬합니다.
    region_counts = df[target_column].value_counts().sort_index()
    
    print(f"'{target_column}' 열의 값별 인원수 (이름 순 정렬):")
    print(region_counts)
    
    # --- 5. 결과를 .txt 파일로 저장 ---
    try:
        # 저장할 폴더가 없으면 자동으로 생성
        os.makedirs(output_folder, exist_ok=True)
        full_path = os.path.join(output_folder, output_filename)
        
        # .to_string()을 사용하여 생략 없이 모든 내용을 파일에 씁니다.
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(f"'{target_column}' 열의 값별 인원수 (이름 순 정렬):\n\n")
            f.write(region_counts.to_string())
            
        print(f"\n📈 전체 결과가 '{full_path}' 파일에 성공적으로 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 통계 파일 저장 중 에러 발생: {e}")
        
else:
    print(f"⚠️ 경고: '{target_column}' 열을 찾을 수 없습니다.")


"""
# 5. 'Q10' 열의 값이 'Q10' 문자열인 행을 찾아서 출력합니다.
q10_header_rows = df[df['Q10'] == 'Q10']
print("Q10 컬럼에 'Q10' 값을 가진 행:")
print(q10_header_rows)
"""

'''
# 6. 나이 이상값 찾기
# 'Q11' 열의 값이 1900보다 큰 행을 찾아서 출력합니다.
age_outliers = df[df['Q11'] < 1900] # 1900년 이후 출생자는 이상값으로 간주
print("나이 이상값 (1900년 이전 출생자):")
print(age_outliers) # 이상값 출력  

 #7 null 값 찾기
null_values = df[df['Q12_2'].isnull()] # 'Q11' 열에 null 값이 있는 행 찾기
print("null 값:")
print(null_values) # null 값 출력       
'''