from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import random

router = APIRouter(prefix="/questions", tags=["questions"])

# ko_app.json 위치 지정 (경로가 맞는지 확인하세요)
DATA_FILE = Path(__file__).parent.parent / "data" / "ko_app.json"

# JSON 파일 읽기
if not DATA_FILE.exists():
    # 파일이 없을 경우를 대비해 빈 리스트 또는 에러 처리
    print(f"❗ JSON file not found: {DATA_FILE}")
    QUESTIONS = []
else:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        QUESTIONS = json.load(f)

# ✅ [추가] 랜덤 테스트 문제 12개 뽑기 엔드포인트
@router.get("/test")
def get_random_test():
    if not QUESTIONS:
        raise HTTPException(status_code=404, detail="No questions available")
        
    # 전체 문제 수와 12개 중 작은 값을 선택 (안전장치)
    num_questions = min(len(QUESTIONS), 12)
    
    # 중복 없이 랜덤 추출
    random_questions = random.sample(QUESTIONS, num_questions)
    return random_questions

# 전체 질문 리스트
@router.get("/")
def get_all_questions():
    return QUESTIONS

# 개별 질문
@router.get("/{id}")
def get_question(id: int):
    # ID가 1부터 시작한다고 가정하고 리스트 인덱스로 접근
    # (ID가 순차적이지 않을 수 있다면 filter를 쓰는 게 더 안전합니다)
    question = next((q for q in QUESTIONS if q["id"] == id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question