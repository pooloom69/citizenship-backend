from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, json
import httpx  # 👈 [필수] 에러 해결을 위해 추가
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

class EvaluateRequest(BaseModel):
    correct_answers: list[str]
    user_answer: str

_client: OpenAI | None = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        
        # ⭐ [핵심 수정] httpx 클라이언트를 직접 만들어서 넣어줍니다.
        # 이렇게 해야 'unexpected keyword argument proxies' 에러가 안 납니다.
        http_client = httpx.Client()
        _client = OpenAI(api_key=api_key, http_client=http_client)
        
    return _client

@router.post("/")
async def evaluate_answer(request: EvaluateRequest):
    try:
        # 사용자가 너무 짧게 말했을 경우 예외 처리
        if not request.user_answer or len(request.user_answer.strip()) < 2:
            return {
                "is_correct": False, 
                "feedback": "I couldn't hear you clearly. Please try again."
            }

        # 프롬프트 구성
        prompt = f"""
You are a kind US Citizenship Interview officer.

Correct meanings/answers: {', '.join(request.correct_answers)}
User's Answer: "{request.user_answer}"

Check if the User's Answer matches any of the Correct meanings/answers contextually.
Allow for minor grammatical errors or slight differences in phrasing.

Output JSON only:
{{
  "is_correct": boolean,
  "feedback": "string (A brief 1-sentence supportive feedback)"
}}
""".strip()

        client = get_client()
        
        # GPT-4o 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"🔥 [Evaluate Error]: {str(e)}") # 서버 로그에 에러 출력
        raise HTTPException(status_code=500, detail=str(e))