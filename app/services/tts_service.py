import base64
from openai import OpenAI
from app.config import settings
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