from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import random

router = APIRouter(prefix="/questions", tags=["questions"])

# 🚨 중요: 방금 만든 5개 국어 JSON 데이터를 이 파일명으로 저장해야 합니다.
# 경로: backend/data/questions_all.json (폴더 구조에 맞게 수정하세요)
DATA_FILE = Path(__file__).parent.parent / "data" / "questions_all.json"

# JSON 파일 읽기 (앱 시작 시 한 번만 로드)
if not DATA_FILE.exists():
    print(f"❗ 오류: JSON 파일을 찾을 수 없습니다. 경로를 확인하세요: {DATA_FILE}")
    QUESTIONS = []
else:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            QUESTIONS = json.load(f)
        print(f"✅ {len(QUESTIONS)}개의 다국어 문제를 로드했습니다.")
    except json.JSONDecodeError:
        print("❗ 오류: JSON 파일 형식이 잘못되었습니다.")
        QUESTIONS = []

# 1. 랜덤 테스트 문제 12개 뽑기 (테스트 모드용)
@router.get("/test")
def get_random_test():
    if not QUESTIONS:
        raise HTTPException(status_code=404, detail="No questions available")
        
    # 전체 문제 수와 12개 중 작은 값을 선택 (안전장치)
    num_questions = min(len(QUESTIONS), 12)
    
    # 중복 없이 랜덤 추출
    random_questions = random.sample(QUESTIONS, num_questions)
    return random_questions

# 2. 전체 질문 리스트 (문제 은행용)
@router.get("/")
def get_all_questions():
    if not QUESTIONS:
        raise HTTPException(status_code=404, detail="No data found")
    return QUESTIONS

# 3. 개별 질문 가져오기 (연습 모드용)
# questions.py 파일의 get_question 함수 수정

@router.get("/{id}")
def get_question(id: int):
    question = next((q for q in QUESTIONS if q["id"] == id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail=f"Question {id} not found")
    
    # 🚨 [디버깅 추가] 앱에서 요청할 때마다 서버 터미널에 가지고 있는 데이터 키(Key)를 출력함
    print(f"🆔 ID {id} 요청 들어옴.")
    print(f"📦 가지고 있는 언어 데이터: {list(question.keys())}") 
    
    return question