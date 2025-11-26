from openai import OpenAI
from app.config import settings
import json
from typing import List, Dict, Any
import os
# 🚨 [수정] http_client=None 추가. 이것이 proxies 충돌을 막는 핵심입니다.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=None 
) 
# Note: Render/Railway는 OPENAI_API_KEY 환경 변수를 자동으로 노출합니다.

def evaluate_answer(correct_answers: List[str], user_answer: str) -> Dict[str, Any]:
    # 프롬프트: 영어로 피드백을 주도록 변경했습니다.
    prompt = f"""
    You are a Citizenship Test Answer Evaluation System.
    
    [Information]
    - Correct Answers: {correct_answers}
    - User Answer: {user_answer}

    [Instructions]
    1. Determine if the User Answer is semantically consistent with one of the Correct Answers. (Allow for minor spelling errors, missing articles, etc.)
    2. You MUST respond in the following JSON format only.
    3. The "feedback" field MUST be in English.

    {{
      "is_correct": true/false,
      "feedback": "Feedback message in English explaining why it is correct or incorrect."
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 응답 내용 파싱
        content = response.choices[0].message.content
        return json.loads(content)

    except json.JSONDecodeError:
        print(f"JSON Decoding Error. Content was: {content}")
        return {"is_correct": False, "feedback": "Evaluation Error: Unable to parse result."}
    except Exception as e:
        print(f"Evaluation Error: {e}")
        return {"is_correct": False, "feedback": "An error occurred during evaluation."}