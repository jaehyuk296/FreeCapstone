# 1. 판다스 라이브러리를 불러옵니다.
import pandas as pd

# 2. 엑셀 파일을 읽어옵니다.
df = pd.read_excel('../paneldata/Welcome/Welcome_1st.xlsx')

# 3. 전체 인원수를 계산하고 출력합니다.
total_people = len(df)
print(f"전체 인원수: {total_people}명")

print("-" * 30) # 구분선


'''
# 4. 각 지역별 인원수를 계산하고 출력합니다.
# 열에 있는 고유한 값들의 개수를 각각 셉니다.
region_counts = df['Q12_2'].value_counts()
print("각 지역별 인원수:")
print(region_counts)
'''

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
'''
 #7 null 값 찾기
null_values = df[df['Q12_2'].isnull()] # 'Q11' 열에 null 값이 있는 행 찾기
print("null 값:")
print(null_values) # null 값 출력       
