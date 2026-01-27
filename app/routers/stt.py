from fastapi import APIRouter, UploadFile, File, HTTPException
import openai
import shutil
import os
import logging

# 로깅 설정 (서버 로그에서 확인하기 위함)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stt", tags=["speech-to-text"])

@router.post("/")
async def stt(file: UploadFile = File(...)):
    # 파일 이름 안전하게 처리
    temp_filename = f"temp_{file.filename}"
    
    try:
        # 1. 일단 서버에 파일을 저장
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. 파일 크기 확인 (가장 중요! ⭐)
        file_size = os.path.getsize(temp_filename)
        logger.info(f"🎤 [요청 도착] 파일명: {file.filename} / 크기: {file_size} bytes")

        if file_size == 0:
            logger.error("❌ [오류] 빈 파일(0 byte)이 넘어왔습니다. 권한 문제거나 녹음 실패입니다.")
            return {"text": ""}

        # 3. OpenAI 클라이언트 초기화 (1.x 버전 방식)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("서버에 OPENAI_API_KEY가 설정되지 않았습니다!")
            
        client = openai.OpenAI(api_key=api_key)

        # 4. Whisper 전송
        logger.info("🚀 OpenAI Whisper로 전송 중...")
        with open(temp_filename, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        result_text = transcript.text
        logger.info(f"✅ [성공] 변환 결과: {result_text}")
        
        return {"text": result_text}

    except Exception as e:
        logger.error(f"🔥 [서버 에러]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 5. 청소: 임시 파일 삭제
        if os.path.exists(temp_filename):
            os.remove(temp_filename)