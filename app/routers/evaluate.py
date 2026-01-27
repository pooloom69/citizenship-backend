from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, json
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
        _client = OpenAI(api_key=api_key)
    return _client

@router.post("/")
async def evaluate_answer(request: EvaluateRequest):
    try:
        if len(request.user_answer.strip()) < 2:
            return {"is_correct": False, "feedback": "Please say more."}

        prompt = f"""
You are a kind US Citizenship Interview officer.

Correct meanings/answers: {', '.join(request.correct_answers)}
User's Answer: "{request.user_answer}"

Output JSON only:
{{
  "is_correct": boolean,
  "feedback": "string"
}}
""".strip()

        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
