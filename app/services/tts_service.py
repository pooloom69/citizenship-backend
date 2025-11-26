import base64
from openai import OpenAI
from app.config import settings
import os
# 🔥 Proxy 환경변수 완전 제거
for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(key, None)

# 🔥 OpenAI client – 기본 transport 사용 (httpx 비활성화됨)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=None   # ⭐ 핵심: 커스텀 transport 금지. 기본 transport 사용
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