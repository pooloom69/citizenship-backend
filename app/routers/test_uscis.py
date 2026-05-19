# test_uscis.py (루트 폴더에 만들어서 실행해 보세요)
import asyncio
from app.services.uscis_service import fetch_uscis_status

async def test():
    # 실제 본인의 접수 번호나 샘플 번호를 넣어보세요
    result = await fetch_uscis_status("IOE0935975835") 
    print(f"조회 결과: {result}")

if __name__ == "__main__":
    asyncio.run(test())