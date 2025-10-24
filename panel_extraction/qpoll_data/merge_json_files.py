import pandas as pd
import os
import glob

def merge_json_files(input_folder, output_filepath):
    """
    지정된 폴더 내의 모든 _preprocessed_data.json 파일들을
    하나의 마스터 데이터프레임으로 합치고 저장합니다.

    - Args:
        input_folder (str): 개별 JSON 파일들이 저장된 폴더 경로
        output_filepath (str): 최종 통합 JSON 파일을 저장할 경로
    """
    # 1. input_folder에서 *_preprocessed_data.json 패턴에 맞는 모든 파일 경로를 찾습니다.
    json_pattern = os.path.join(input_folder, '**', '*_preprocessed_data.json')
    file_list = glob.glob(json_pattern, recursive=True)

    if not file_list:
        print(f"❌ '{input_folder}' 경로에서 처리할 JSON 파일을 찾을 수 없습니다.")
        return

    print(f"📂 총 {len(file_list)}개의 파일을 통합합니다:")
    for f in file_list:
        print(f"  - {os.path.basename(f)}")

    # 2. 각 JSON 파일을 데이터프레임으로 읽어와 리스트에 저장합니다.
    df_list = [pd.read_json(f) for f in file_list]

    # 3. 모든 데이터프레임을 하나로 합칩니다.
    # ignore_index=True: 기존 인덱스를 무시하고 새로운 인덱스를 생성합니다.
    # sort=False: 불필요한 정렬을 방지하여 성능을 높입니다.
    master_df = pd.concat(df_list, ignore_index=True, sort=False)

    print(f"\n✅ 모든 데이터가 성공적으로 통합되었습니다.")
    print(f"통합된 데이터 정보: {master_df.shape[0]}행, {master_df.shape[1]}열")
    
    # 4. 최종 통합 데이터 저장
    # 저장할 폴더가 없으면 자동으로 생성합니다.
    output_dir = os.path.dirname(output_filepath)
    os.makedirs(output_dir, exist_ok=True)
    
    # JSON으로 저장
    master_df.to_json(output_filepath, orient='records', indent=4, force_ascii=False)
    print(f"🎉 최종 통합 데이터가 '{output_filepath}' 경로에 저장되었습니다.")
    
    return master_df

def main():
    """
    메인 실행 함수
    """
    # 전처리된 JSON 파일들이 있는 상위 폴더 경로
    INPUT_FOLDER = '../../json_extraction/qpoll_data/'
    
    # 최종 통합 파일을 저장할 경로 및 이름
    OUTPUT_FILEPATH = '../../json_extraction/master_data.json'
    
    merge_json_files(INPUT_FOLDER, OUTPUT_FILEPATH)

if __name__ == "__main__":
    main()
