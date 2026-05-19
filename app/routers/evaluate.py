from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, json
import httpx
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
        
        # httpx 클라이언트를 직접 설정하여 프록시 관련 에러 방지
        http_client = httpx.Client()
        _client = OpenAI(api_key=api_key, http_client=http_client)
        
    return _client

@router.post("/")
async def evaluate_answer(request: EvaluateRequest):
    try:
        # 입력값이 너무 짧은 경우 예외 처리
        if not request.user_answer or len(request.user_answer.strip()) < 2:
            return {
                "is_correct": False,
                "feedback": "I couldn't hear you clearly. Please try again in English."
            }
        if len(request.user_answer) > 1000:
            return {
                "is_correct": False,
                "feedback": "Your answer is too long. Please give a concise answer."
            }

        # 🎯 [핵심] 영어 인지 + 부분 점수 + 혼합 피드백 로직이 강화된 프롬프트
        prompt = f"""
You are a professional US Citizenship Interview Officer. 
The interview is conducted ONLY in English.

[STRICT EVALUATION RULES]
1. LANGUAGE CHECK: If the User's Answer is NOT in English (e.g., contains Korean, Spanish, etc.), you MUST set "is_correct": false and "feedback": "Please answer in English."
2. PARTIAL CREDIT: If the question allows multiple answers and the user provides at least ONE correct item from the list, set "is_correct": true.
3. MIXED FEEDBACK: If the user provides multiple items where some are CORRECT and some are INCORRECT:
   - "is_correct": true (since they provided at least one correct answer).
   - "feedback": Explicitly state what was right and what was wrong. (e.g., "The part about [Correct Item] is correct, but [Incorrect Item] is not accurate.")
4. KEYWORD STRICTNESS: Factual correctness of English keywords is mandatory. Ignore minor grammar slips if the meaning is clear.

[Correct Answer List]: {', '.join(request.correct_answers)}
[User's Answer]: "{request.user_answer}"

[Output Format - JSON Only]
{{
  "analysis": "Identify which parts are correct and which are wrong",
  "is_correct": boolean,
  "feedback": "A professional 1-sentence feedback in English"
}}
""".strip()

        client = get_client()
        
        # GPT-4o 호출 (temperature=0.1로 고정하여 채점 일관성 확보)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a factual USCIS evaluator. You output JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1, 
        )

        content = response.choices[0].message.content
        result = json.loads(content)
        
        # 앱 프론트엔드로 필요한 데이터만 전송
        return {
            "is_correct": result.get("is_correct", False),
            "feedback": result.get("feedback", "Please try again.")
        }

    except Exception as e:
        print(f"🔥 [Evaluate Error]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))