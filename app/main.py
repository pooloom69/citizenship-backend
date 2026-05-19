# main.py
import os
from dotenv import load_dotenv

# 1. 앱 시작 전 .env 로드 (가장 중요! ⭐)
# 이 코드가 라우터 임포트보다 위에 있어야, 라우터들이 API 키를 물고 들어갑니다.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 임포트 (중복 제거 및 정리)
from app.routers import questions, stt, tts, evaluate, civics, definitions

# USCIS 라우터는 playwright 의존성이 무거워 호스팅 환경에 따라 옵셔널로 로드
try:
    from app.routers import uscis
    _HAS_USCIS = True
except ImportError:
    _HAS_USCIS = False

app = FastAPI(title="Citizenship Coach API")

# 2. CORS 설정 — 모바일 앱(Expo)에서 접속 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 라우터 등록
app.include_router(questions.router)
app.include_router(stt.router)
app.include_router(tts.router)
app.include_router(evaluate.router)
app.include_router(civics.router)
app.include_router(definitions.router)
if _HAS_USCIS:
    app.include_router(uscis.router)

@app.get("/")
def root():
    # 간단한 API 키 확인용 (배포 시에는 지우는 게 좋습니다)
    api_key_status = "Loaded" if os.getenv("OPENAI_API_KEY") else "Missing"
    return {
        "message": "Citizenship Coach API is running",
        "api_key_status": api_key_status
    }