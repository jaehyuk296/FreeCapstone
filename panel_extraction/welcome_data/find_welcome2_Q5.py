# 1. 판다스 라이브러리를 불러옵니다.
import pandas as pd
import os

# 2. 엑셀 파일을 읽어옵니다.
df = pd.read_excel('../../paneldata/Welcome/Welcome_2nd.xlsx')

# --- 저장하고 싶은 폴더 경로를 변수로 지정 ---
output_folder = '../../json_extraction/welcome2_data/' 

# 3. 전체 인원수를 계산하고 출력합니다.
total_people = len(df)
print(f"전체 인원수: {total_people}명")

print("-" * 30) # 구분선

# 4. 각 지역별 인원수를 계산하고 출력합니다.
# 열에 있는 고유한 값들의 개수를 각각 셉니다.
job_counts = df['Q5'].value_counts()
print("각 답변 인원수:")
print(job_counts)

os.makedirs(output_folder, exist_ok=True)

# 최종 저장 경로와 파일 이름 설정
output_filename = 'job_counts.txt'
full_path = os.path.join(output_folder, output_filename)

# .to_string() 메서드를 사용하면 생략 없이 모든 내용이 문자열로 변환됩니다.
with open(full_path, 'w', encoding='utf-8') as f:
    f.write(job_counts.to_string())

print(f"\n🎉 전체 결과가 '{full_path}' 파일에 성공적으로 저장되었습니다.")
