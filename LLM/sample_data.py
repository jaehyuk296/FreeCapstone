import pandas as pd
from pathlib import Path

# --- 1. 파일 경로 설정 ---
# 이 스크립트 파일이 있는 폴더 기준 (merge_data.py와 같은 위치라고 가정)
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 

# 원본 통합 데이터 파일 경로
merged_data_path = base_dir / 'merged_panel_data.json' 
# 샘플 데이터를 저장할 파일 경로
sample_output_path = base_dir / 'sample_100_data.json'

# --- 2. 원본 데이터 읽기 ---
try:
    df_merged = pd.read_json(merged_data_path)
    print(f"✅ 원본 데이터 '{merged_data_path.name}' 로드 성공 (총 {len(df_merged)}개 데이터)")
except FileNotFoundError:
    print(f"❌ [오류] 원본 데이터 파일 '{merged_data_path.name}'을 찾을 수 없습니다. 경로를 확인하세요.")
    exit()
except Exception as e:
    print(f"❌ [오류] 원본 데이터 파일 로드 중 오류 발생: {e}")
    exit()

# --- 3. 100개 샘플 무작위 추출 ---
if len(df_merged) >= 100:
    # df_merged.sample(n=100) : 전체 데이터에서 무작위로 100개를 뽑습니다.
    # random_state=42 : 항상 동일한 샘플을 뽑고 싶을 때 사용 (숫자는 아무거나 상관없음), 재현 가능성을 위함
    df_sample = df_merged.sample(n=100, random_state=42) 
    print(f"✅ 데이터 {len(df_merged)}개 중 100개 샘플 무작위 추출 완료.")
else:
    # 데이터가 100개 미만이면 전체 데이터를 사용
    print(f"⚠️ [경고] 전체 데이터 개수({len(df_merged)}개)가 100개 미만입니다. 전체 데이터를 샘플로 사용합니다.")
    df_sample = df_merged.copy()

# --- 4. 샘플 데이터 저장 ---
try:
    df_sample.to_json(sample_output_path, orient='records', force_ascii=False, indent=4)
    print(f"🎉 100개 샘플 데이터가 '{sample_output_path.name}' 파일로 저장되었습니다.")
    print(f"   💾 저장 위치: {sample_output_path}")
except Exception as e:
    print(f"❌ 샘플 데이터 저장 중 오류 발생: {e}")