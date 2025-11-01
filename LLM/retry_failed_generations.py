import pandas as pd
from pathlib import Path
import anthropic 
import os                  
from dotenv import load_dotenv 
import time 
from anthropic import RateLimitError, APIConnectionError, InternalServerError
import json

# --- 0. .env 로드 및 기본 설정 ---
load_dotenv() 
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 

print("--- 1. 경로 및 엔진 로드 시작 ---")

# --- 1-1. 파일 경로 설정 ---
# (★중요★) 1단계에서 생성된 "원본 데이터"
merged_data_path = base_dir / 'merged_panel_data.json' 
# (★중요★) 1단계에서 "오류가 포함된" 요약 문장 파일
failed_results_path = base_dir / 'generated_sentences.json' 
# (★중요★) 최종적으로 "수정된" 전체 요약 문장을 저장할 파일
final_output_path = base_dir / 'generated_sentences_ALL_v2.json' 

# --- 1-2. LLM 엔진 로드 ---
try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
    llm_client = anthropic.Anthropic(api_key=api_key)
    LLM_MODEL = "claude-sonnet-4-5" # (사용 가능한 최신 Sonnet 모델 ID)
    print(f"✅ LLM ({LLM_MODEL}) 클라이언트 초기화 완료.")
except Exception as e:
    print(f"❌ LLM 클라이언트 초기화 실패: {e}")
    exit()

# --- 2. 실패한 데이터 선별 ---
print(f"\n--- 2. '{failed_results_path.name}'에서 오류 데이터 선별 중 ---")
try:
    df_results_old = pd.read_json(failed_results_path)
    # '요약문장'에 '오류 발생'이라는 텍스트가 포함된 행을 찾습니다.
    df_results_old['요약문장'] = df_results_old['요약문장'].astype(str)
    failed_rows = df_results_old[df_results_old['요약문장'].str.contains("오류 발생")]
    failed_ids = failed_rows['고유번호'].tolist()
    
    if not failed_ids:
        print("✅ 오류가 발생한 데이터가 없습니다. 작업을 종료합니다.")
        exit()
        
    print(f"🔥 총 {len(failed_ids)}개의 오류 항목을 발견했습니다. 재처리를 시작합니다.")
    
except FileNotFoundError:
    print(f"❌ [오류] '{failed_results_path.name}' 파일을 찾을 수 없습니다. 파일 이름을 확인하세요.")
    exit()
except Exception as e:
    print(f"❌ 오류 데이터 선별 중 알 수 없는 오류: {e}")
    exit()

# --- 3. 재처리가 필요한 원본 데이터 로드 ---
print(f"\n--- 3. '{merged_data_path.name}'에서 원본 데이터 로드 중 ---")
try:
    df_merged = pd.read_json(merged_data_path)
    df_merged['고유번호'] = df_merged['고유번호'].astype(str)
    
    # 실패한 ID 목록을 사용해 원본 데이터에서 재처리할 대상만 필터링
    df_to_retry = df_merged[df_merged['고유번호'].isin(failed_ids)]
    print(f"✅ 재처리 대상 원본 데이터 {len(df_to_retry)}개 준비 완료.")
    
except Exception as e:
    print(f"❌ 원본 데이터 로드 또는 필터링 실패: {e}")
    exit()


# --- 4. 오류 항목 재처리 (1단계와 동일한 로직) ---
print(f"\n--- 4. {len(df_to_retry)}개 항목 재처리 시작 ---")
MAX_RETRIES = 5
BASE_SLEEP_TIME = 1
newly_generated_sentences = [] # 새로 생성된 문장만 저장

# (1단계와 동일한 재시도 루프)
for index, person_data in df_to_retry.iterrows():
    
    print(f"\n--- {index+1}/{len(df_to_retry)}번째 오류 데이터 처리 시작 (고유번호: {person_data.get('고유번호')}) ---")
    
    prompt = f"""
다음은 한 사람의 설문 응답 데이터입니다:
<data>
{person_data.to_json(force_ascii=False, indent=2)}
</data>
이 사람의 주요 특징(예: 나이, 직업, 관심사 등)을 파악하여 **간결하고 자연스러운 한 문장으로 요약**해 주세요. 
단, 데이터에 없는 내용은 추측하지 말고, "정보 없음" 또는 관련 언급을 생략하세요.
"""
    
    retries = 0   
    success = False 
    
    while retries < MAX_RETRIES and not success:
        try:
            message = llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=250,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            generated_text = message.content[0].text.strip()
            
            print(f"   💬 (재처리 성공) 생성된 문장: {generated_text}")
            newly_generated_sentences.append({
                "고유번호": person_data.get('고유번호'), 
                "요약문장": generated_text
            })
            success = True 
            time.sleep(BASE_SLEEP_TIME)
        
        except (RateLimitError, APIConnectionError, InternalServerError) as e:
            retries += 1
            wait_time = (2 ** retries) 
            print(f"   ⚠️ (재시도) Rate limit/서버 오류 (시도 {retries}/{MAX_RETRIES}). {wait_time}초 대기...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ [치명적 오류] 재시도 불가. {e}")
            newly_generated_sentences.append({
                "고유번호": person_data.get('고유번호'),
                "요약문장": f"오류 발생 (재처리 시도 중): {e}"
            })
            break 
    
    if not success and retries == MAX_RETRIES:
        print(f"   ❌ [최종 실패] {MAX_RETRIES}번 재시도 후에도 실패.")
        newly_generated_sentences.append({
            "고유번호": person_data.get('고유번호'),
            "요약문장": f"오류 발생: 최대 재시도 횟수 초과 (재처리)"
        })

print(f"\n--- 5. 재처리 결과 병합 및 저장 ---")
# 새로 생성된 결과(list of dicts)를 DataFrame으로 변환
df_new_results = pd.DataFrame(newly_generated_sentences)

try:
    # '고유번호'를 기준으로 데이터를 업데이트하기 위해 인덱스로 설정
    df_results_old.set_index('고유번호', inplace=True)
    df_new_results.set_index('고유번호', inplace=True)

    # df_results_old (기존 결과)에 df_new_results (새 결과)를 덮어쓰기
    df_results_old.update(df_new_results)
    
    # 인덱스를 다시 컬럼으로 복원
    df_results_old.reset_index(inplace=True)

    # 최종 v2 파일로 저장
    df_results_old.to_json(final_output_path, orient='records', force_ascii=False, indent=4) 
    print(f"\n🎉 모든 오류 처리가 완료된 최종 데이터가 '{final_output_path.name}' 파일로 저장되었습니다.")

except Exception as e:
    print(f"❌ 최종 결과 병합 또는 저장 중 오류 발생: {e}")