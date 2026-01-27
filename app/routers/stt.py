from fastapi import APIRouter, UploadFile, File, HTTPException
import openai
import shutil
import os
from dotenv import load_dotenv

# 1. .env 파일 로드
load_dotenv()

router = APIRouter(prefix="/stt", tags=["speech-to-text"])

# 🔑 여기에 OpenAI API 키를 직접 넣어서 테스트해보세요 (나중에 .env로 이동)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@router.post("/")
async def stt(file: UploadFile = File(...)):
    temp_filename = f"temp_{file.filename}"
    
    try:
        # 1. 일단 서버에 파일을 저장해봅니다.
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. 파일 크기 확인 (가장 중요! ⭐)
        file_size = os.path.getsize(temp_filename)
        print(f"🎤 [디버깅] 파일 이름: {file.filename}")
        print(f"🎤 [디버깅] 파일 크기: {file_size} bytes")

        if file_size == 0:
            print("❌ [오류] 빈 파일이 넘어왔습니다. 프론트엔드 녹음 실패!")
            return {"text": ""}

        # 3. OpenAI Whisper로 전송
        print("🚀 OpenAI로 전송 중...")
        with open(temp_filename, "rb") as audio_file:
            # (OpenAI 라이브러리 버전에 따라 코드가 다를 수 있어 구버전/신버전 호환 방식 사용)
            try:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                text = transcript["text"]
            except:
                # 신버전(1.0.0+)일 경우
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                text = transcript.text

        print(f"✅ [성공] 변환된 텍스트: {text}")
        return {"text": text}

    except Exception as e:
        print(f"🔥 [서버 에러]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 청소: 임시 파일 삭제
        if os.path.exists(temp_filename):
            os.remove(temp_filename)