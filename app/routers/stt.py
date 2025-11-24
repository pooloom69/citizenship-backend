from fastapi import APIRouter, UploadFile, File
from app.services.whisper_service import transcribe_audio

router = APIRouter(prefix="/stt", tags=["speech-to-text"])

@router.post("/")
async def stt(audio: UploadFile = File(...)):
    text = await transcribe_audio(audio)
    return {"text": text}
