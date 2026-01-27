from fastapi import APIRouter, HTTPException
import requests
import pgeocode

router = APIRouter(prefix="/civics", tags=["civics"])

# 🔑 Open States API 키 (사용자님 키 입력)
OPEN_STATES_API_KEY = "a4fd6f4b-4384-47f5-aeb9-9be500dd4cbf"  # 예시 키가 있다면 교체하세요

# 🏛️ 주지사 명단 (State Code -> Governor Name)
# 2025~2026년 기준 주요 주지사 명단입니다. 필요한 주가 있으면 추가하면 됩니다.
# 🏛️ 미국 50개 주 주지사 명단 (2025-2026 임기 기준)
US_GOVERNORS = {
    # A
    "AL": "Kay Ivey",           # Alabama
    "AK": "Mike Dunleavy",      # Alaska
    "AZ": "Katie Hobbs",        # Arizona
    "AR": "Sarah Huckabee Sanders", # Arkansas
    # C
    "CA": "Gavin Newsom",       # California
    "CO": "Jared Polis",        # Colorado
    "CT": "Ned Lamont",         # Connecticut
    # D
    "DE": "Matt Meyer",         # Delaware (New! 2025 취임)
    # F
    "FL": "Ron DeSantis",       # Florida
    # G
    "GA": "Brian Kemp",         # Georgia
    # H
    "HI": "Josh Green",         # Hawaii
    # I
    "ID": "Brad Little",        # Idaho
    "IL": "JB Pritzker",        # Illinois
    "IN": "Mike Braun",         # Indiana (New! 2025 취임)
    "IA": "Kim Reynolds",       # Iowa
    # K
    "KS": "Laura Kelly",        # Kansas
    "KY": "Andy Beshear",       # Kentucky
    # L
    "LA": "Jeff Landry",        # Louisiana
    # M
    "ME": "Janet Mills",        # Maine
    "MD": "Wes Moore",          # Maryland
    "MA": "Maura Healey",       # Massachusetts
    "MI": "Gretchen Whitmer",   # Michigan
    "MN": "Tim Walz",           # Minnesota
    "MS": "Tate Reeves",        # Mississippi
    "MO": "Mike Kehoe",         # Missouri (New! 2025 취임)
    "MT": "Greg Gianforte",     # Montana
    # N
    "NE": "Jim Pillen",         # Nebraska
    "NV": "Joe Lombardo",       # Nevada
    "NH": "Kelly Ayotte",       # New Hampshire (New! 2025 취임)
    "NJ": "Phil Murphy",        # New Jersey (⚠️ 2026년 1월 임기 종료 예정, 확인 필요)
    "NM": "Michelle Lujan Grisham", # New Mexico
    "NY": "Kathy Hochul",       # New York
    "NC": "Josh Stein",         # North Carolina (New! 2025 취임)
    "ND": "Kelly Armstrong",    # North Dakota (New! 2025 취임)
    # O
    "OH": "Mike DeWine",        # Ohio
    "OK": "Kevin Stitt",        # Oklahoma
    "OR": "Tina Kotek",         # Oregon
    # P
    "PA": "Josh Shapiro",       # Pennsylvania
    # R
    "RI": "Dan McKee",          # Rhode Island
    # S
    "SC": "Henry McMaster",     # South Carolina
    "SD": "Kristi Noem",        # South Dakota
    # T
    "TN": "Bill Lee",           # Tennessee
    "TX": "Greg Abbott",        # Texas
    # U
    "UT": "Spencer Cox",        # Utah
    # V
    "VT": "Phil Scott",         # Vermont
    "VA": "Abigail Spanberger",     # Virginia (⚠️ 2026년 1월 임기 종료 예정, 확인 필요)
    # W
    "WA": "Bob Ferguson",       # Washington (New! 2025 취임)
    "WV": "Patrick Morrisey",   # West Virginia (New! 2025 취임)
    "WI": "Tony Evers",         # Wisconsin
    "WY": "Mark Gordon",        # Wyoming
}

@router.get("/representatives/{zip_code}")
def get_representatives(zip_code: str):
    try:
        # 1. ZIP Code -> 위도/경도/주(State) 변환
        nomi = pgeocode.Nominatim('us')
        location = nomi.query_postal_code(zip_code)
        
        # 유효하지 않은 우편번호 체크 (NaN 체크)
        if location.latitude != location.latitude: 
            return {"error": "Invalid ZIP Code"}

        lat = location.latitude
        lng = location.longitude
        state_code = location.state_code  # 예: 'CA'

        # 2. Open States API 호출 (상원의원 찾기)
        url = "https://v3.openstates.org/people.geo"
        params = {
            "lat": lat,
            "lng": lng,
            "apikey": OPEN_STATES_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        results = {
            "senators": [],
            "governor": ""
        }

        # 3. 상원의원(Senator) 추출 로직
        # 보내주신 JSON 분석 결과:
        # jurisdiction.name이 "United States" 이고, 
        # current_role.org_classification이 "upper" 인 사람이 진짜 'US Senator'입니다.
        if "results" in data:
            for person in data["results"]:
                role = person.get("current_role", {})
                jurisdiction = person.get("jurisdiction", {})
                
                # 조건: 미국 연방(United States) 소속 + 상원(upper)
                if jurisdiction.get("name") == "United States" and role.get("org_classification") == "upper":
                    results["senators"].append(person["name"])

        # 4. 주지사(Governor) 매칭 로직
        # 위에서 구한 state_code('CA')를 이용해 명단에서 찾습니다.
        if state_code in US_GOVERNORS:
            results["governor"] = US_GOVERNORS[state_code]
        else:
            results["governor"] = "Unknown Governor"

        print(f"✅ ZIP: {zip_code} -> {state_code}, Senators: {results['senators']}, Gov: {results['governor']}")
        return results

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))