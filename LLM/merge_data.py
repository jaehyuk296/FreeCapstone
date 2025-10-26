import pandas as pd
import os
from pathlib import Path
import glob # 파일 경로 패턴 매칭을 위한 라이브러리

# --- 0. 기본 경로 설정 ---
# 이 스크립트 파일(merge_data.py)이 있는 폴더를 기준으로 상대 경로 설정
base_dir = Path(__file__).parent 
json_extraction_dir = base_dir.parent / 'json_extraction'

# --- 1. Welcome 데이터 로드 ---
print("--- Welcome 데이터 로딩 시작 ---")
try:
    path_w1 = json_extraction_dir / 'welcome_data/Welcome_1st_preprocessed.json'
    df_welcome1 = pd.read_json(path_w1)
    # '고유번호'가 문자열(str) 타입인지 확인 (병합을 위해 중요)
    df_welcome1['고유번호'] = df_welcome1['고유번호'].astype(str) 
    print(f"  {path_w1.name} 로드 성공 (Shape: {df_welcome1.shape})")

    path_w2 = json_extraction_dir / 'welcome_data/Welcome_2nd_preprocessed.json'
    df_welcome2 = pd.read_json(path_w2)
    # welcome2의 컬럼 이름 정리 (이전 코드 참고)
    df_welcome2.columns = df_welcome2.columns.str.replace('[^A-Za-z0-9_]+', '_', regex=True)
    # welcome2에 '고유번호' 컬럼이 있는지 확인하고 타입 통일
    if '고유번호' in df_welcome2.columns:
         df_welcome2['고유번호'] = df_welcome2['고유번호'].astype(str)
    elif 'mb_sn' in df_welcome2.columns: # 만약 이름이 mb_sn 이라면 변경
         df_welcome2.rename(columns={'mb_sn': '고유번호'}, inplace=True)
         df_welcome2['고유번호'] = df_welcome2['고유번호'].astype(str)
    else:
        print(f"  [경고] {path_w2.name}에 '고유번호' 또는 'mb_sn' 컬럼이 없어 병합에서 제외될 수 있습니다.")
    print(f"  {path_w2.name} 로드 성공 (Shape: {df_welcome2.shape})")

except FileNotFoundError as e:
    print(f"[오류] Welcome 데이터 파일 로드 실패: {e}")
    exit()
print("-" * 30)

# --- 2. Qpoll 데이터 로드 및 통합 ---
print("--- Qpoll 데이터 로딩 시작 ---")
qpoll_dir = json_extraction_dir / 'qpoll_data'
all_qpoll_files = []

# qpoll_data 폴더 내 모든 하위 폴더(*) 안의 *_preprocessed_data.json 찾기
# glob 패턴을 사용하여 파일 경로 리스트 생성
try:
    # 예: .../qpoll_data/Jan/*_preprocessed_data.json 등 모든 경로 찾기
    path_pattern = str(qpoll_dir / '*' / '*_preprocessed_data.json') 
    all_qpoll_files = glob.glob(path_pattern) 
    
    if not all_qpoll_files:
        print(f"  [경고] {qpoll_dir} 경로 또는 하위 폴더에서 Qpoll JSON 파일을 찾을 수 없습니다.")
        df_qpoll = pd.DataFrame() # 빈 DataFrame 생성
    else:
        print(f"  총 {len(all_qpoll_files)}개의 Qpoll JSON 파일 발견.")
        
        qpoll_dfs = [] # 각 qpoll 파일을 읽어서 저장할 리스트
        for f_path_str in all_qpoll_files:
            f_path = Path(f_path_str)
            try:
                df_temp = pd.read_json(f_path)
                # '고유번호' 컬럼 확인 및 타입 통일
                if '고유번호' in df_temp.columns:
                    df_temp['고유번호'] = df_temp['고유번호'].astype(str)
                    qpoll_dfs.append(df_temp)
                else:
                     print(f"    [경고] {f_path.name} 파일에 '고유번호' 컬럼이 없어 통합에서 제외됩니다.")
            except Exception as e:
                print(f"    [오류] {f_path.name} 파일 로드 중 오류 발생: {e}")
        
        if qpoll_dfs: # 읽어온 qpoll DataFrame이 있다면
            # 모든 qpoll DataFrame을 하나로 합치기 (위아래로 붙이기)
            df_qpoll = pd.concat(qpoll_dfs, ignore_index=True) 
            print(f"  모든 Qpoll 데이터 통합 성공 (Shape: {df_qpoll.shape})")
        else:
            print(f"  로드 가능한 Qpoll 데이터가 없습니다.")
            df_qpoll = pd.DataFrame() # 빈 DataFrame 생성

except Exception as e:
    print(f"[오류] Qpoll 데이터 검색 또는 로드 중 오류 발생: {e}")
    df_qpoll = pd.DataFrame() # 오류 발생 시 빈 DataFrame 생성
print("-" * 30)
# --- 3. 모든 데이터 병합 (Merge) ---
print("--- 모든 데이터 병합 시작 ---")

df_merged = pd.DataFrame() # 먼저 빈 DataFrame으로 확실하게 초기화

# df_welcome1이 성공적으로 로드되었는지 확인
if 'df_welcome1' in locals() and isinstance(df_welcome1, pd.DataFrame) and not df_welcome1.empty:
    df_merged = df_welcome1.copy() # 원본 수정을 피하기 위해 복사본 사용
    print(f"  df_merged 초기화 완료 (df_welcome1 기준, Shape: {df_merged.shape})")

    # df_welcome2 병합 시도
    if 'df_welcome2' in locals() and isinstance(df_welcome2, pd.DataFrame) and '고유번호' in df_welcome2.columns:
        try:
            # 중복 컬럼 발생 시 어떻게 처리할지 명시 (예: '_w2' 접미사 추가)
            df_merged = pd.merge(df_merged, df_welcome2, on='고유번호', how='left', suffixes=('', '_w2'))
            print(f"  df_welcome2 병합 완료 (Shape: {df_merged.shape})")
        except Exception as e:
            print(f"  [오류] df_welcome2 병합 중 오류 발생: {e}")
            # 병합 실패 시 어떻게 할지 결정 (여기서는 계속 진행)
    
    # df_qpoll 병합 시도
    if 'df_qpoll' in locals() and isinstance(df_qpoll, pd.DataFrame) and not df_qpoll.empty and '고유번호' in df_qpoll.columns:
        try:
            # 중복 컬럼 발생 시 '_qpoll' 접미사 추가
            df_merged = pd.merge(df_merged, df_qpoll, on='고유번호', how='left', suffixes=('', '_qpoll'))
            print(f"  df_qpoll 병합 완료 (Shape: {df_merged.shape})")
        except Exception as e:
            print(f"  [오류] df_qpoll 병합 중 오류 발생: {e}")
            # 병합 실패 시 어떻게 할지 결정 (여기서는 계속 진행)
    elif 'df_qpoll' in locals() and df_qpoll.empty:
        print(f"  df_qpoll 데이터가 없어 병합을 건너뜁니다.")

else:
    # df_welcome1 로드 실패 시 df_merged는 여전히 빈 상태
    print("[치명적 오류] df_welcome1 로드 실패 또는 비어있어 병합을 시작할 수 없습니다.")

print("-" * 30)

# --- 4. 최종 데이터 확인 및 저장 ---
# df_merged가 비어있지 않은 경우에만 실행
if not df_merged.empty:
    print("--- 최종 통합 데이터 (df_merged) ---")
    try:
        print(df_merged.head()) # 앞 5줄 확인
        print(f"최종 데이터 Shape: {df_merged.shape}")
    except Exception as e:
        print(f"  [오류] 최종 데이터 출력 중 오류 발생: {e}")
    print("-" * 30)

    output_path = base_dir / 'merged_panel_data.json' # 저장될 파일 이름 및 경로
    try:
        df_merged.to_json(output_path, orient='records', force_ascii=False, indent=4)
        print(f"✅ 통합 데이터를 '{output_path.name}' 파일로 성공적으로 저장했습니다.")
        print(f"   저장 위치: {output_path}")
    except Exception as e:
        print(f"❌ 통합 데이터 저장 중 오류 발생: {e}")
else:
    # df_merged가 비어있는 경우 (초기화 실패 또는 병합 실패 등)
    print("❌ 최종 통합 데이터(df_merged)가 비어있거나 생성되지 않아 저장하지 않습니다.")

print("-" * 30)
print("데이터 통합 및 저장 완료!")