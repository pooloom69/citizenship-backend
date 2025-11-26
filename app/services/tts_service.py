# 

import os
import base64
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_tts(text: str) -> str:
    try:
        url = "https://api.openai.com/v1/audio/speech"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini-tts",  # 최신 권장 모델
            "voice": "alloy",
            "input": text
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print("TTS Error:", response.text)
            return ""

        audio_bytes = response.content
        return base64.b64encode(audio_bytes).decode("utf-8")

    except Exception as e:
        print(f"TTS generation failed: {e}")
        return ""
