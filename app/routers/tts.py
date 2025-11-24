#tts.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.tts_service import generate_tts

router = APIRouter(prefix="/tts", tags=["tts"])

class TTSRequest(BaseModel):
    text: str

@router.post("/")
async def tts(req: TTSRequest):
    # 1. TTS 서비스 호출
    audio_data = generate_tts(req.text)
    
    # 2. 결과가 없으면 에러 반환
    if not audio_data:
        raise HTTPException(status_code=500, detail="TTS generation failed")
    
    # 3. 'audio_base64'라는 키값으로 데이터 전송 (프론트엔드와 약속된 이름)
    return {"audio_base64": audio_data}