from fastapi import APIRouter, UploadFile, File, HTTPException
import openai
import shutil
import os
import logging
import httpx  # 👈 핵심 추가: httpx 직접 사용

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stt", tags=["speech-to-text"])

@router.post("/")
async def stt(file: UploadFile = File(...)):
    temp_filename = f"temp_{file.filename}"
    
    try:
        # 1. 파일 저장
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. 크기 확인
        file_size = os.path.getsize(temp_filename)
        logger.info(f"🎤 [요청 도착] 파일명: {file.filename} / 크기: {file_size} bytes")

        if file_size == 0:
            return {"text": ""}

        # 3. API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("서버에 OPENAI_API_KEY가 없습니다.")
            
        # ⭐ 핵심 수정 부분: httpx 클라이언트를 직접 생성해서 주입 ⭐
        # 이렇게 하면 버전이 꼬여도 'proxies' 에러를 피해갈 수 있습니다.
        http_client = httpx.Client() 
        client = openai.OpenAI(api_key=api_key, http_client=http_client)

        # 4. Whisper 전송
        logger.info("🚀 OpenAI Whisper로 전송 중...")
        with open(temp_filename, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
            )

        # 무음 감지: no_speech_prob이 높으면 빈 텍스트 반환
        no_speech_prob = getattr(transcript, "no_speech_prob", 0) or 0
        if no_speech_prob > 0.5:
            logger.info(f"🔇 무음 감지 (no_speech_prob={no_speech_prob:.2f}), 빈 텍스트 반환")
            return {"text": ""}

        result_text = transcript.text.strip()

        # Whisper 환각 문구 필터
        HALLUCINATIONS = {
            "thank you for watching", "thanks for watching", "thank you.",
            "thanks for watching!", "thank you for watching.", "you",
            ".", "...", " ", "bye", "bye.", "okay.", "okay",
        }
        if result_text.lower() in HALLUCINATIONS:
            logger.info(f"🚫 환각 문구 감지: '{result_text}', 빈 텍스트 반환")
            return {"text": ""}

        logger.info(f"✅ [성공] 결과: {result_text}")
        return {"text": result_text}

    except Exception as e:
        logger.error(f"🔥 [서버 에러]: {str(e)}")
        # 프론트엔드에서 에러 내용을 볼 수 있게 그대로 전달
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)