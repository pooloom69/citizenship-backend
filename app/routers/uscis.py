from fastapi import APIRouter, HTTPException
from app.services.uscis_service import fetch_uscis_status

router = APIRouter(prefix="/uscis", tags=["uscis"])

@router.get("/status/{receipt_number}")
async def get_status(receipt_number: str):
    # 간단한 번호 형식 체크 (예: MSC, LIN, EAC 등 13자리)
    if len(receipt_number) != 13:
        raise HTTPException(status_code=400, detail="Invalid Receipt Number format.")
    
    result = await fetch_uscis_status(receipt_number)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["message"])
        
    return result