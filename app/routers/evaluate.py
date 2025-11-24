from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.evaluate_service import evaluate_answer

router = APIRouter(prefix="/evaluate", tags=["answer-eval"])

# 요청 데이터 구조 정의 (JSON Body)
class EvaluateRequest(BaseModel):
    correct_answers: List[str]
    user_answer: str

@router.post("/")
async def eval_answer(req: EvaluateRequest):
    # 서비스 로직 호출
    result = evaluate_answer(req.correct_answers, req.user_answer)
    return result