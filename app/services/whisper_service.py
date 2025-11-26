import io
from openai import OpenAI
from app.config import settings
from fastapi import UploadFile
from typing import Optional
import os

# 모든 proxy 제거
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)


# 🚨 [수정] http_client=None 추가. 이것이 proxies 충돌을 막는 핵심입니다.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=None 
) 
# Note: Render/Railway는 OPENAI_API_KEY 환경 변수를 자동으로 노출합니다.

async def transcribe_audio(audio_file: UploadFile) -> str:
    """
    업로드된 오디오 파일을 OpenAI Whisper 모델을 사용하여 텍스트로 변환합니다.
    """
    # 파일 형식 체크
    if audio_file.content_type and not audio_file.content_type.startswith("audio/"):
        return "Error: Invalid audio file format."

    try:
        # 1. FastAPI UploadFile을 읽어서 메모리(BytesIO)에 담습니다.
        audio_content = await audio_file.read()
        audio_buffer = io.BytesIO(audio_content)
        
        # 2. Whisper API는 파일 이름(확장자)이 필요합니다.
        filename: Optional[str] = audio_file.filename
        audio_buffer.name = filename if filename else "audio.wav"

        # 3. OpenAI API 호출
        # 🚨 [수정] 시민권 시험은 영어로 진행되므로 언어를 'en'으로 고정합니다.
        # 이렇게 해야 영어를 한국어로 억지로 번역하는 문제를 막을 수 있습니다.
        response = client.audio.transcriptions.create(
            model="whisper-1",  
            file=audio_buffer,
            language="en" 
        )
        return response.text
    except Exception as e:
        print(f"Whisper API transcription failed: {e}")
        return "Error: Speech recognition failed."