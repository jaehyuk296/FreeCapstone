import pandas as pd
import numpy as np 
import os
from pathlib import Path
import glob 

# --- 0. 기본 경로 설정 ---
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 
    print(f"⚠️ __file__ 변수를 찾을 수 없어 현재 작업 디렉토리({base_dir})를 기준으로 합니다.")
    
json_extraction_dir = base_dir.parent / 'json_extraction'

# --- 1. Welcome 데이터 로드 ---
print("--- Welcome 데이터 로딩 시작 ---")
df_welcome1 = pd.DataFrame() 
df_welcome2 = pd.DataFrame() 

try:
    # --- Welcome 1 로드 및 중복 제거 ---
    path_w1 = json_extraction_dir / 'welcome_data/Welcome_1st_preprocessed.json'
    df_welcome1 = pd.read_json(path_w1)
    if '고유번호' in df_welcome1.columns:
        df_welcome1['고유번호'] = df_welcome1['고유번호'].astype(str)
        print(f" ✅ {path_w1.name} 로드 성공 (Shape: {df_welcome1.shape})")

        initial_duplicates_w1 = df_welcome1['고유번호'].duplicated().sum()
        if initial_duplicates_w1 > 0:
            print(f"   ⚠️ [경고] {path_w1.name}에 중복된 '고유번호' {initial_duplicates_w1}개 발견. 첫 번째 값만 남기고 제거합니다.")
            df_welcome1 = df_welcome1.drop_duplicates(subset='고유번호', keep='first')
            print(f"   ✅ 중복 제거 후 Welcome1 Shape: {df_welcome1.shape}")
    else:
        print(f" ❌ [치명적 오류] {path_w1.name}에 '고유번호' 컬럼이 없어 중단합니다.")
        exit() 

    # --- Welcome 2 로드 및 중복 제거 ---
    path_w2 = json_extraction_dir / 'welcome_data/Welcome_2nd_preprocessed.json'
    df_welcome2 = pd.read_json(path_w2)
    print(f" ✅ {path_w2.name} 로드 성공 (Shape: {df_welcome2.shape})")
    print(f"   - 로드된 Welcome2 컬럼: {df_welcome2.columns.tolist()}") 

    if '고유번호' in df_welcome2.columns:
         df_welcome2['고유번호'] = df_welcome2['고유번호'].astype(str)
         print(f"   - '고유번호' 컬럼 확인 및 타입 변환 완료.")

         # --- ⭐ 중복 '고유번호' 확인 및 제거 추가 (Welcome2) ⭐ ---
         initial_duplicates_w2 = df_welcome2['고유번호'].duplicated().sum()
         if initial_duplicates_w2 > 0:
             print(f"   ⚠️ [경고] {path_w2.name}에 중복된 '고유번호' {initial_duplicates_w2}개 발견. 첫 번째 값만 남기고 제거합니다.")
             df_welcome2 = df_welcome2.drop_duplicates(subset='고유번호', keep='first')
             print(f"   ✅ 중복 제거 후 Welcome2 Shape: {df_welcome2.shape}")

    else:
         print(f"   ⚠️ [경고] {path_w2.name}에 '고유번호' 컬럼이 없습니다.")

    if '고유번호' not in df_welcome2.columns:
        print(f"   ❌ [오류] df_welcome2에 '고유번호' 컬럼이 없어 병합 불가.")
        df_welcome2 = pd.DataFrame() 

except FileNotFoundError as e:
    print(f"❌ [오류] Welcome 데이터 파일({e.filename}) 로드 실패. 경로를 확인하세요.")
    if df_welcome1.empty: exit() 
except Exception as e:
     print(f"❌ [오류] Welcome 데이터 처리 중 예상치 못한 오류: {e}")
     exit()
print("-" * 30)

# --- 2. Qpoll 데이터 로드 (파일 목록만) ---
# (이전 코드와 동일 - 생략)
print("--- Qpoll 데이터 검색 시작 ---")
qpoll_dir = json_extraction_dir / 'qpoll_data'
all_qpoll_files = []
try:
    path_pattern = str(qpoll_dir / '*' / '*_preprocessed_data.json')
    all_qpoll_files = glob.glob(path_pattern, recursive=True) 

    if not all_qpoll_files:
        print(f"   ⚠️ [경고] {qpoll_dir} 경로 또는 하위 폴더에서 Qpoll JSON 파일을 찾을 수 없습니다.")
    else:
        print(f"   ✅ 총 {len(all_qpoll_files)}개의 Qpoll JSON 파일 발견.")

except Exception as e:
    print(f"❌ [오류] Qpoll 파일 검색 중 오류 발생: {e}")
print("-" * 30)


# --- 3. 모든 데이터 병합 (Merge) ---
print("--- 모든 데이터 병합 시작 ---")
df_merged = pd.DataFrame()

# 중복 생성 방지할 공통 컬럼 정의 (Welcome1 기준)
common_base_columns = ['구분', '성별', '나이', '지역_시도', '지역_시군구', '설문일시'] 

# 3-1. Welcome1을 기준으로 시작
if not df_welcome1.empty:
    df_merged = df_welcome1.copy()
    print(f"   ✅ df_merged 초기화 완료 (df_welcome1 기준, Shape: {df_merged.shape})")

    # 3-2. Welcome2 병합 (⭐ 로직 수정 ⭐)
    if not df_welcome2.empty and '고유번호' in df_welcome2.columns:
        try:
            common_ids_w2 = df_merged['고유번호'].isin(df_welcome2['고유번호']).sum()
            print(f"   - df_welcome1과 df_welcome2 간 겹치는 고유번호: {common_ids_w2} 개")
            
            # Welcome2에서 가져올 컬럼 리스트 생성 (고유번호 제외)
            cols_to_merge_w2 = df_welcome2.columns.difference(['고유번호']).tolist()
            
            # Welcome1과 겹치는 컬럼 이름 변경 (예: '성별' -> '성별_w2')
            cols_rename_w2 = {
                col: f"{col}_w2" 
                for col in cols_to_merge_w2 
                if col in df_merged.columns # df_merged(Welcome1)에도 있는 컬럼만 이름 변경
            }
            df_welcome2_renamed = df_welcome2.rename(columns=cols_rename_w2)
            
            # 이름 변경된 df_welcome2를 병합
            df_merged = pd.merge(df_merged, df_welcome2_renamed, on='고유번호', how='left')
            print(f"   ✅ df_welcome2 병합 완료 (Shape: {df_merged.shape})")

            # (병합 후 확인 코드 생략)

        except Exception as e:
            print(f"   ❌ [오류] df_welcome2 병합 중 오류 발생: {e}")
    else:
        print(f"   ℹ️ df_welcome2 데이터 병합 건너<0xEB><0x9C><0x8D>니다.") # 깨진 문자 수정: 건너뜁니다

    # 3-3. Qpoll 데이터 순차적 병합 (이전 코드와 동일)
    print(f"\n   --- Qpoll 데이터 순차 병합 시작 ---")
    if all_qpoll_files:
        for f_path_str in all_qpoll_files:
            f_path = Path(f_path_str)
            try:
                df_temp = pd.read_json(f_path)
                qpoll_id = f_path.stem.split('_')[0] 

                if '고유번호' in df_temp.columns:
                    df_temp['고유번호'] = df_temp['고유번호'].astype(str)

                    # 공통 기본 컬럼 제외 및 Qpoll 고유 컬럼에 접미사 추가
                    cols_to_exclude = [col for col in common_base_columns if col != '고유번호' and col in df_temp.columns]
                    # '지역' 컬럼 처리: Qpoll의 '지역'이 Welcome1의 '지역_시도'와 같다면 제외
                    if '지역' in df_temp.columns and '지역_시도' in df_merged.columns:
                         cols_to_exclude.append('지역') # 중복 방지 위해 제외 목록에 추가
                         
                    qpoll_specific_cols = [
                        col for col in df_temp.columns 
                        if col != '고유번호' and col not in cols_to_exclude
                    ]
                    cols_to_rename = {col: f"{col}_{qpoll_id}" for col in qpoll_specific_cols}
                    df_temp_processed = df_temp[['고유번호'] + qpoll_specific_cols].rename(columns=cols_to_rename)
                    
                    common_ids_qpoll = df_merged['고유번호'].isin(df_temp_processed['고유번호']).sum()
                    df_merged = pd.merge(df_merged, df_temp_processed, on='고유번호', how='left') 
                    print(f"     ✅ {f_path.name} 병합 완료 (겹치는 ID: {common_ids_qpoll} 개, 현재 Shape: {df_merged.shape})")

                else:
                    print(f"     ⚠️ [경고] {f_path.name} 파일에 '고유번호' 컬럼이 없어 병합에서 제외됩니다.")
            except Exception as e:
                print(f"     ❌ [오류] {f_path.name} 파일 처리/병합 중 오류 발생: {e}")
        print(f"   --- Qpoll 데이터 순차 병합 완료 ---")
    else:
         print(f"   ℹ️ Qpoll 파일이 없어 병합을 건너<0xEB><0x9C><0x8D>니다.") # 깨진 문자 수정: 건너뜁니다

else:
    print("❌ [치명적 오류] df_welcome1 로드 실패 또는 비어있어 병합을 시작할 수 없습니다.")

print("-" * 30)

# --- 4. 최종 데이터 확인 및 저장 ---
if not df_merged.empty:
    print("--- 최종 통합 데이터 (df_merged) ---")
    try:
        # 최종 중복 '고유번호' 확인 및 제거
        final_duplicates = df_merged['고유번호'].duplicated().sum()
        if final_duplicates > 0:
            print(f"   ⚠️ [경고] 최종 병합 데이터에 중복된 '고유번호' {final_duplicates}개 발견. 첫 번째 값만 남기고 제거합니다.")
            df_merged = df_merged.drop_duplicates(subset='고유번호', keep='first')
            print(f"   ✅ 최종 중복 제거 후 Shape: {df_merged.shape}")

        # (★★★ 수정된 부분: 컬럼 이름에서 날짜 ID 제거 ★★★)
        print("\n   --- 컬럼 이름 정리 시작 (날짜 ID 제거) ---")
        cleaned_columns = {}
        processed_names = set() # 이미 처리된 최종 이름 추적 (중복 방지)
        
        for col in df_merged.columns:
            original_col = col # 원래 컬럼 이름 저장
            
            # 컬럼 이름 마지막 부분이 '_YYMMDD' 형태인지 확인
            if len(col) > 7 and col[-7] == '_' and col[-6:].isdigit():
                # '_' 앞부분까지만 잘라서 기본 이름으로 사용
                base_name = col.rsplit('_', 1)[0]
                
                # --- 중복 이름 처리 ---
                # 만약 정리된 이름(base_name)이 이미 최종 컬럼명으로 사용되었다면,
                # 현재 컬럼 이름에 '_dup' 같은 접미사를 붙여 구분합니다.
                # (또는 다른 규칙 적용 가능: 예: '_dup2', '_dup3'...)
                final_name = base_name
                counter = 1
                while final_name in processed_names:
                    counter += 1
                    final_name = f"{base_name}_dup{counter}"
                    
                cleaned_columns[original_col] = final_name
                processed_names.add(final_name)
                if original_col != final_name:
                     print(f"     '{original_col}'  ->  '{final_name}' (날짜 제거)")
                
            else:
                # 패턴에 맞지 않으면 원래 이름 유지 (단, 중복 방지 체크는 필요)
                final_name = col
                counter = 1
                while final_name in processed_names:
                    counter += 1
                    final_name = f"{col}_dup{counter}"

                cleaned_columns[original_col] = final_name
                processed_names.add(final_name)
                if original_col != final_name:
                     print(f"     '{original_col}'  ->  '{final_name}' (중복 방지)")

        df_merged.rename(columns=cleaned_columns, inplace=True)
        print(f"   ✅ 컬럼 이름 정리 완료. (현재 컬럼 수: {len(df_merged.columns)})")
        # (★★★ 여기까지 수정 ★★★)

        print("\n   데이터 앞 5줄 미리보기:")
        print(df_merged.head())
        print(f"\n   최종 데이터 Shape: {df_merged.shape}")
        
    except Exception as e:
        print(f"   ❌ [오류] 최종 데이터 출력 또는 컬럼 정리 중 오류 발생: {e}")
    print("-" * 30)

    # --- 이하 저장 로직은 동일 ---
    output_path = base_dir / 'merged_panel_data.json'
    try:
        df_merged_for_json = df_merged.replace({np.nan: None})
        df_merged_for_json.to_json(output_path, orient='records', force_ascii=False, indent=4)
        print(f"✅ 통합 데이터를 '{output_path.name}' 파일로 성공적으로 저장했습니다.")
        print(f"   💾 저장 위치: {output_path}")
    except Exception as e:
        print(f"❌ 통합 데이터 저장 중 오류 발생: {e}")
else:
    print("❌ 최종 통합 데이터(df_merged)가 비어있거나 생성되지 않아 저장하지 않습니다.")

print("-" * 30)
print("🏁 데이터 통합 및 저장 완료!")