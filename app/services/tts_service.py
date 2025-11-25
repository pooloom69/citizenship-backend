import base64
from openai import OpenAI
from app.config import settings

client = OpenAI()

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