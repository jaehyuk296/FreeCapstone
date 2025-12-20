import pandas as pd
from pathlib import Path
import anthropic 
import os                  
from dotenv import load_dotenv 
import time 
# 재시도를 위한 Anthropic의 특정 오류 클래스를 가져옵니다.
from anthropic import RateLimitError, APIConnectionError, InternalServerError

# --- .env 파일 로드 ---
load_dotenv() 

# --- 1. 파일 경로 설정 및 데이터 로드 ---
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 

sample_data_path = base_dir / 'merged_panel_data.json'
try:
    df_sample = pd.read_json(sample_data_path)
    print(f"✅ 샘플 데이터 '{sample_data_path.name}' 로드 성공 ({len(df_sample)}개)")
except Exception as e:
    print(f"❌ 샘플 데이터 로드 실패: {e}")
    exit()

# --- 2. Anthropic API 클라이언트 초기화 ---
api_key = os.getenv("ANTHROPIC_API_KEY") 

if not api_key:
    print("❌ [오류] .env 파일에서 ANTHROPIC_API_KEY를 찾을 수 없습니다.")
    exit()

client = anthropic.Anthropic(api_key=api_key) 
print("✅ Anthropic 클라이언트 초기화 완료 (API 키 로드 성공)")


# --- 3. 각 데이터에 대해 문장 생성 ---

# 재시도 설정
MAX_RETRIES = 5       # 최대 재시도 횟수
BASE_SLEEP_TIME = 1   # 성공 시 기본 대기 시간 (초)

generated_sentences = [] 

for index, person_data in df_sample.iterrows():
    
    print(f"\n--- {index+1}/{len(df_sample)}번째 사람 데이터 처리 시작 ---")
    
    prompt = f"""
다음은 한 사람의 설문 응답 데이터입니다:
<data>
{person_data.to_json(force_ascii=False, indent=2)}
</data>

이 사람의 주요 특징(예: 나이, 직업, 관심사 등)을 파악하여 **간결하고 자연스러운 한 문장으로 요약**해 주세요. 
단, 데이터에 없는 내용은 추측하지 말고, "정보 없음" 또는 관련 언급을 생략하세요.
"""
    
    retries = 0   # 현재 재시도 횟수
    success = False # 성공 여부 플래그
    
    # --- 재시도 루프 시작 ---
    while retries < MAX_RETRIES and not success:
        try:
            # --- 실제 API 호출 ---
            message = client.messages.create(
                model="claude-sonnet-4-5", # (모델 이름은 확인된 최신 것으로 사용)
                max_tokens=250,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            generated_text = message.content[0].text.strip()
            
            # --- 성공 처리 ---
            print(f"   💬 생성된 문장: {generated_text}")
            generated_sentences.append({
                "고유번호": person_data.get('고유번호'), 
                "요약문장": generated_text
            })
            success = True # 성공 플래그 설정
            time.sleep(BASE_SLEEP_TIME) # 성공 시에도 기본 대기 (API 배려)
        
        # --- 오류 처리 ---
        except RateLimitError as e:
            retries += 1
            # (2 ** 1) = 2초, (2 ** 2) = 4초, (2 ** 3) = 8초...
            wait_time = (2 ** retries) 
            print(f"   ⚠️ Rate limit (시도 {retries}/{MAX_RETRIES}). {wait_time}초 대기...")
            time.sleep(wait_time)
            
        except (APIConnectionError, InternalServerError) as e:
            retries += 1
            wait_time = (2 ** retries)
            print(f"   ⚠️ 서버 오류 (시도 {retries}/{MAX_RETRIES}). {wait_time}초 대기... ({e})")
            time.sleep(wait_time)

        except Exception as e:
            # 404 (모델 없음), 400 (잘못된 요청) 등 재시도가 의미 없는 오류
            print(f"   ❌ [치명적 오류] 재시도 불가. {e}")
            generated_sentences.append({
                "고유번호": person_data.get('고유번호'),
                "요약문장": f"오류 발생 (재시도 불가): {e}"
            })
            break # 재시도 루프 중단
    # --- 재시도 루프 종료 ---
    
    # 최대 재시도 횟수를 초과한 경우
    if not success and retries == MAX_RETRIES:
        print(f"   ❌ [최종 실패] {MAX_RETRIES}번 재시도 후에도 실패. 다음으로 넘어갑니다.")
        generated_sentences.append({
            "고유번호": person_data.get('고유번호'),
            "요약문장": f"오류 발생: 최대 재시도 횟수 초과"
        })

# --- 4. 최종 결과 확인 ---
print("\n--- 최종 생성된 문장 리스트 ---")
df_results = pd.DataFrame(generated_sentences)
print(df_results.head()) 

results_output_path = base_dir / 'generated_sentences.json'
df_results.to_json(results_output_path, orient='records', force_ascii=False, indent=4) 
print(f"\n🎉 생성된 문장이 '{results_output_path.name}' 파일로 저장되었습니다.")