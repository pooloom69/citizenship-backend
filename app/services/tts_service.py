import base64
from openai import OpenAI
from app.config import settings
import os
import httpx

# 🚨 [수정] 프록시 설정이 없는 깨끗한 HTTP 클라이언트 생성
# 이렇게 하면 Railway나 Render의 환경 변수(HTTP_PROXY)를 무시합니다.
custom_http_client = httpx.Client(proxies=None)

# OpenAI 클라이언트에 커스텀 HTTP 클라이언트 주입
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=custom_http_client # ✅ [수정] 직접 만든 클라이언트 주입
)


def generate_tts(text: str) -> str:
    try:
        # TTS용 공식 모델명은 'tts-1' 입니다.
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # 목소리: alloy, echo, fable, onyx, nova, shimmer 중 택1
            input=text
        )

        audio_bytes = response.read()
        return base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        print(f"TTS API generation failed: {e}")
        return ""