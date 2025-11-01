import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
import time
import chromadb # ChromaDB 임포트
import numpy as np
import json

print("--- 1. 데이터 로드 시작 ---")

# --- 1. 파일 경로 설정 및 데이터 로드 ---
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 

# 1-1. 1단계에서 생성된 요약 문장 파일 로드
sentences_path = base_dir / 'generated_sentences_ALL_v2.json'
try:
    df_sentences = pd.read_json(sentences_path)
    # '요약문장'이 null이거나 비어있는 경우(오류 발생 등)를 대비해 처리
    df_sentences['요약문장'] = df_sentences['요약문장'].fillna('정보 없음').astype(str)
    # '고유번호'도 문자열로 통일
    df_sentences['고유번호'] = df_sentences['고유번호'].astype(str)
    print(f"✅ 요약 문장 데이터 로드 성공 ({len(df_sentences)}개)")
except Exception as e:
    print(f"❌ 요약 문장 파일 로드 실패: {e}")
    exit()

# 1-2. 원본 메타데이터 파일 로드 (필터링을 위해 필요)
merged_data_path = base_dir / 'merged_panel_data.json'
try:
    df_merged = pd.read_json(merged_data_path)
    df_merged['고유번호'] = df_merged['고유번호'].astype(str)
    print(f"✅ 원본 메타데이터 로드 성공 ({len(df_merged)}개)")
except Exception as e:
    print(f"❌ 원본 메타데이터 파일 로드 실패: {e}")
    exit()

# 1-3. 요약 문장과 원본 메타데이터 병합
try:
    # '고유번호'를 기준으로 df_merged와 df_sentences 병합
    # (df_merged에 이미 '요약문장'이 있다면 이 단계 불필요, 하지만 생성 스크립트가 분리되었으므로 병합)
    df_final = pd.merge(
        df_merged, 
        df_sentences[['고유번호', '요약문장']], 
        on='고유번호', 
        how='inner' # 요약 문장이 생성된 데이터만 대상으로 함
    )
    print(f"✅ 요약 문장 + 메타데이터 병합 완료 (최종 {len(df_final)}개)")
except Exception as e:
    print(f"❌ 데이터 병합 실패: {e}")
    exit()


print("\n--- 2. 임베딩 모델 로드 ---")
# --- 2. 임베딩 모델 로드 ---
# KURE-v1 모델 ID
model_name = 'nlpai-lab/KURE-v1' 
try:
    # KURE-v1 모델 다운로드 및 로드 (최초 실행 시 시간 소요)
    embedding_model = SentenceTransformer(model_name)
    print(f"✅ 임베딩 모델 '{model_name}' 로드 성공.")
except Exception as e:
    print(f"❌ 임베딩 모델 로드 실패: {e}")
    exit()


print("\n--- 3. ChromaDB 설정 ---")
# --- 3. 벡터 DB(ChromaDB) 설정 ---
# 디스크에 'panel_vector_db'라는 폴더를 만들고 영구 저장
db_path = str(base_dir / 'panel_vector_db')
client = chromadb.PersistentClient(path=db_path)

# 'panel_collection'이라는 이름의 컬렉션(테이블) 생성 또는 가져오기
collection_name = "panel_collection"
try:
    # (주의!) KURE-v1 (1024차원)에 맞는 metadata 설정 추가
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"} # 코사인 유사도 사용
    )
    print(f"✅ 벡터 DB 컬렉션 '{collection_name}' 준비 완료.")
except Exception as e:
    print(f"❌ 벡터 DB 설정 실패: {e}")
    exit()


print("\n--- 4. 벡터화 및 DB 적재 시작 ---")
# --- 4. 벡터화 및 DB 적재 (35,000개 처리) ---
start_time = time.time()

# 4-1. 요약 문장들을 벡터로 변환 (GPU 사용 시 훨씬 빠름)
print(f"⏳ {len(df_final)}개 문장 벡터화 시작...")
documents = df_final['요약문장'].tolist() # 벡터화 대상이 될 텍스트 (필수)
embeddings = embedding_model.encode(documents, show_progress_bar=True)
print(f"✅ 벡터화 완료. (소요 시간: {time.time() - start_time:.2f}초)")

# 4-2. DB에 적재할 데이터 리스트 준비
print("⏳ DB에 적재할 데이터 배치 준비 중...")
ids = df_final['고유번호'].tolist()      # 각 항목의 고유 ID (필수)

# (★★★ 이것이 "해시태그/라벨링" 작업입니다 ★★★)
# 검색 시 필터링에 사용할 메타데이터(원천데이터) 준비
# 필터링할 컬럼만 선택
metadata_columns = [
    # --- 기본 인구통계 (Welcome1) ---
    '고유번호',
    '성별',
    '나이',
    '지역_시도',
    '지역_시군구',

    # --- 상세 정보 (Welcome2) ---
    '결혼여부',
    '자녀수',
    '자녀유무',
    '가족수',
    '최종학력',
    '직업',
    '직무',
    '월평균_개인소득',
    '월평균_가구소득',
    '보유휴대폰단말기_브랜드',
    '보유차량여부',
    '자동차제조사',
    
    # --- Qpoll 설문 응답 (필터링에 유용한 것들) ---
    '반려동물_경험',
    '반려동물_경험유무', # 1.0 / 0.0 값 (숫자 필터링 가능)
    '이사_스트레스_여부',  # 1.0 / 0.0 값
    '많이사용하는앱',
    '운동',              # "달리기/걷기" 등 (복수 응답 가능)
    '카테고리',          # "유산소 운동" 등
    '체력_관리_유무',    # "있다" / "없다"
    'ott사용개수',
    'ott사용중',
    '방문빈도',
    '전통시장_방문',
    '설 선호선물있음',
    '여행스타일',
    '친환경_노력_여부',
    '포인트_신경쓰는_정도',
    '초콜릿_섭취_여부',  # 1.0 / 0.0 값
    '개인정보보호_노력여부',
    '비올때_대처방법',
    '주요_저장_사진',
    '선호_물놀이_장소',
    '물놀이_선호여부',  # 1.0 / 0.0 값
    '걱정있음',        # 1.0 / 0.0 값
    '처리방법_요약',
    '알람_방식',
    '혼밥_빈도',
    '혼밥_여부',        # 1.0 / 0.0 값
    '행복한_노년의_조건',
    '아침식사_방식',
    '최애간식_있음',    # 1.0 / 0.0 값
    '최대_지출처',
    'AI_사용여부',
    '소비성향',
    '스트레스_해소법',
    '피부만족도_요약',
    '스킨케어_한달_소비금액',
    '구매_고려_요소',
    '주요_사용_챗봇',
    '선호_서비스',
    '해외여행_희망여부',
    '빠른배송_이용여부'
]
# 실제 df_final에 있는 컬럼만 필터링
existing_metadata_columns = [col for col in metadata_columns if col in df_final.columns]
metadatas = df_final[existing_metadata_columns].replace({np.nan: None}).to_dict('records')
print(f"✅ {len(ids)}개 데이터 배치 준비 완료 (메타데이터 컬럼 {len(existing_metadata_columns)}개 포함).")

# 4-3. ChromaDB에 배치(Batch)로 적재
# (35,000개는 한 번에 넣으면 오류 날 수 있으므로 1000개씩 나눠서 넣기)
BATCH_SIZE = 1000
total_inserted = 0
try:
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_documents = documents[i : i + BATCH_SIZE]
        batch_embeddings = embeddings[i : i + BATCH_SIZE]
        batch_metadatas = metadatas[i : i + BATCH_SIZE]
        
        # .add() 대신 .upsert()를 사용하면, ID가 중복될 경우 덮어쓰기(수정) 됩니다.
        collection.upsert(
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        total_inserted += len(batch_ids)
        print(f"   ... {total_inserted}/{len(ids)}개 적재 완료")

    end_time = time.time()
    print(f"✅ DB 적재 완료! (총 {total_inserted}개)")
    print(f"   (총 소요 시간: {end_time - start_time:.2f}초)")

except Exception as e:
    print(f"❌ DB 적재 중 오류 발생: {e}")

print("\n--- 모든 작업 완료 ---")