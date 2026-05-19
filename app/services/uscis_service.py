from playwright.async_api import async_playwright
import asyncio

async def fetch_uscis_status(receipt_number: str):
    async with async_playwright() as p:
        # 1. 브라우저 실행 (로컬 테스트 시 False, 서버 배포 시 True)
        browser = await p.chromium.launch(headless=True)
        
        # context 설정 부분 보강
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800},
            locale="en-US",
            timezone_id="America/Los_Angeles"
        )

        # 더 정교한 봇 우회 스크립트
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)
                
        page = await context.new_page()
                
        # ✨ 반드시 try 블록으로 감싸야 에러 발생 시 JSON 응답을 보낼 수 있습니다.
        try:
            print(f"Connecting to USCIS for: {receipt_number}...")
            # USCIS 접속
            await page.goto("https://egov.uscis.gov/casestatus/landing.do", wait_until="load", timeout=60000)
            
            # 4. 입력창 대기 및 입력
            input_selector = "#receipt_number"
            await page.wait_for_selector(input_selector, timeout=30000)
            await page.fill(input_selector, receipt_number)
            
            # 5. 조회 버튼 클릭
            await page.click("button[type='submit']")
            
            # 6. 결과 페이지 대기 및 텍스트 추출
            result_header_selector = ".rows.text-center h1" 
            await page.wait_for_selector(result_header_selector, timeout=30000)
            
            status = await page.inner_text(result_header_selector)
            detail = await page.inner_text(".rows.text-center p")
            
            print(f"✅ 조회 성공: {status.strip()}")
            return {
                "status": status.strip(),
                "detail": detail.strip(),
                "receipt_number": receipt_number
            }
            
        except Exception as e:
            # 실패 시 디버깅을 위한 스크린샷
            print(f"🚨 Scraping Error: {str(e)}")
            # 실제 에러 내용을 JSON으로 리턴하여 'JSON Parse error'를 방지합니다.
            return {"error": "check_failed", "message": str(e)}
            
        finally:
            await browser.close()