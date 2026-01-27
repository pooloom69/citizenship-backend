# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import questions, stt, tts, evaluate
from app.routers import questions, civics
from app.routers import definitions

app = FastAPI(title="Citizenship Coach API")

# CORS — 모바일 앱에서 호출 가능하게
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 나중에 도메인 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers 등록
app.include_router(questions.router)
app.include_router(stt.router)
app.include_router(tts.router)
app.include_router(evaluate.router)
app.include_router(civics.router)
app.include_router(definitions.router)

@app.get("/")
def root():
    return {"message": "Citizenship Coach API is running"}
