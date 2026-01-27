from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
import os
import json
from dotenv import load_dotenv

# 1. .env 파일 로드
load_dotenv()

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

# 2. API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) # 최신 버전 클라이언트 초기화

# 프론트엔드에서 보낼 데이터 형식 정의
class EvaluateRequest(BaseModel):
    correct_answers: list[str]
    user_answer: str

@router.post("/")
async def evaluate_answer(request: EvaluateRequest):
    try:
        # 🔍 디버깅 로그 (터미널 확인용)
        print(f"📝 [채점 요청] 사용자 답변: {request.user_answer}")
        print(f"🎯 [정답 기준] : {request.correct_answers}")

        # 사용자 답변이 너무 짧으면 바로 오답 처리
        if len(request.user_answer.strip()) < 2:
            return {"is_correct": False, "feedback": "Please say more."}

        # 3. GPT-4o (또는 gpt-3.5-turbo) 프롬프트 작성
        prompt = f"""
        You are a kind US Citizenship Interview officer.
        
        Question context: The user is answering a civics question or defining a word.
        Correct meanings/answers: {', '.join(request.correct_answers)}
        
        User's Answer: "{request.user_answer}"
        
        Task:
        1. Determine if the User's Answer carries the same meaning as any of the Correct Answers.
        2. Ignore minor grammar mistakes or pronunciation errors.
        3. Be generous but accurate.
        
        Output JSON only:
        {{
            "is_correct": boolean,
            "feedback": "string (Explain why it is correct or wrong in 1 sentence, very simple English)"
        }}
        """

        # 4. OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",  # 혹은 "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}, # JSON 강제 모드
            temperature=0.3
        )

        # 5. 결과 파싱
        content = response.choices[0].message.content
        result = json.loads(content)
        
        print(f"🤖 [AI 채점 결과]: {result}") # 로그 출력

        return result

    except Exception as e:
        print(f"🔥 [Evaluation Error]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))