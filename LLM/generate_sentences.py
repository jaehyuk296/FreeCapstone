import pandas as pd
from pathlib import Path
import anthropic 
import os                  # <-- os 라이브러리 추가
from dotenv import load_dotenv # <-- dotenv 라이브러리 추가
import time # <--- 1. time 모듈 추가 timeover 오류 방지

# --- .env 파일 로드 ---
load_dotenv() # 현재 폴더 또는 상위 폴дер에서 .env 파일을 찾아 환경 변수로 로드

# --- 1. 파일 경로 설정 및 데이터 로드 ---
# (이전 코드와 동일)
try:
    base_dir = Path(__file__).parent 
except NameError:
    base_dir = Path.cwd() 

sample_data_path = base_dir / 'sample_100_data.json'
try:
    df_sample = pd.read_json(sample_data_path)
    print(f"✅ 샘플 데이터 '{sample_data_path.name}' 로드 성공 ({len(df_sample)}개)")
except Exception as e:
    print(f"❌ 샘플 데이터 로드 실패: {e}")
    exit()

# --- 2. Anthropic API 클라이언트 초기화 (★★★ 수정된 부분 ★★★) ---
# .env 파일에서 'ANTHROPIC_API_KEY'라는 이름의 변수를 찾아 값(API 키)을 가져옵니다.
# (만약 .env 파일에 다른 이름으로 저장했다면, 그 이름으로 바꿔주세요. 예: 'CLAUDE_KEY')
api_key = os.getenv("ANTHROPIC_API_KEY") 

if not api_key:
    print("❌ [오류] .env 파일에서 ANTHROPIC_API_KEY를 찾을 수 없습니다. .env 파일을 확인하거나 키 이름을 확인하세요.")
    exit()

client = anthropic.Anthropic(api_key=api_key) 
print("✅ Anthropic 클라이언트 초기화 완료 (API 키 로드 성공)")


# --- 3. 각 데이터에 대해 문장 생성 ---
# (이하 코드는 이전과 동일)
generated_sentences = [] 

for index, person_data in df_sample.iterrows():
    # ... (프롬프트 생성) ...
    prompt = f"""
다음은 한 사람의 설문 응답 데이터입니다:
<data>
{person_data.to_json(force_ascii=False, indent=2)}
</data>

이 사람의 주요 특징(예: 나이, 직업, 관심사 등)을 파악하여 **간결하고 자연스러운 한 문장으로 요약**해 주세요. 
단, 데이터에 없는 내용은 추측하지 말고, "정보 없음" 또는 관련 언급을 생략하세요.
"""
    
    try:
        # --- 실제 API 호출 예시 ---
        message = client.messages.create(
            model="claude-3-haiku-20240307", # Haiku 모델 사용 (비용 절감)
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        generated_text = message.content[0].text
        
        print(f"   💬 생성된 문장: {generated_text}")
        generated_sentences.append({
            "고유번호": person_data.get('고유번호'), 
            "요약문장": generated_text
        })
        
        time.sleep(1) # 1초 동안 잠시 멈춥니다. (시간 초과 오류 방지)
        
    except Exception as e:
        print(f"   ❌ API 호출 또는 처리 중 오류 발생: {e}")
        generated_sentences.append({
            "고유번호": person_data.get('고유번호'),
            "요약문장": f"오류 발생: {e}"
        })

        if "rate_limit_error" in str(e).lower(): # 오류 메시지에 rate_limit 포함 시
             print("   ⚠️ Rate limit 오류 감지. 5초간 대기합니다...")
             time.sleep(5) # 5초 대기
        else:
             time.sleep(1) # 다른 오류 시 짧게 대기

# --- 4. 최종 결과 확인 ---
print("\n--- 최종 생성된 문장 리스트 ---")
# print(generated_sentences) # 전체 리스트 출력 (길 수 있음)

# 결과를 DataFrame으로 변환하여 보기 좋게 출력
df_results = pd.DataFrame(generated_sentences)
print(df_results.head()) # 앞 5개만 출력

# (선택) 결과를 파일로 저장
results_output_path = base_dir / 'generated_sentences.json'
df_results.to_json(results_output_path, orient='records', force_ascii=False, indent=4) 
print(f"\n🎉 생성된 문장이 '{results_output_path.name}' 파일로 저장되었습니다.")