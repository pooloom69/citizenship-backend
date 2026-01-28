from fastapi import APIRouter, HTTPException
import requests
import pgeocode

router = APIRouter(prefix="/civics", tags=["civics"])

# 🔑 Open States API 키
OPEN_STATES_API_KEY = "a4fd6f4b-4384-47f5-aeb9-9be500dd4cbf" 

# 📢 30번 문제: 하원의장 (전국 공통, 2026년 기준)
SPEAKER_OF_THE_HOUSE = "Mike Johnson"

# 🏛️ 62번 문제: 주 수도 (State Capital) 데이터
US_CAPITALS = {
    "AL": "Montgomery", "AK": "Juneau", "AZ": "Phoenix", "AR": "Little Rock",
    "CA": "Sacramento", "CO": "Denver", "CT": "Hartford", "DE": "Dover",
    "FL": "Tallahassee", "GA": "Atlanta", "HI": "Honolulu", "ID": "Boise",
    "IL": "Springfield", "IN": "Indianapolis", "IA": "Des Moines", "KS": "Topeka",
    "KY": "Frankfort", "LA": "Baton Rouge", "ME": "Augusta", "MD": "Annapolis",
    "MA": "Boston", "MI": "Lansing", "MN": "Saint Paul", "MS": "Jackson",
    "MO": "Jefferson City", "MT": "Helena", "NE": "Lincoln", "NV": "Carson City",
    "NH": "Concord", "NJ": "Trenton", "NM": "Santa Fe", "NY": "Albany",
    "NC": "Raleigh", "ND": "Bismarck", "OH": "Columbus", "OK": "Oklahoma City",
    "OR": "Salem", "PA": "Harrisburg", "RI": "Providence", "SC": "Columbia",
    "SD": "Pierre", "TN": "Nashville", "TX": "Austin", "UT": "Salt Lake City",
    "VT": "Montpelier", "VA": "Richmond", "WA": "Olympia", "WV": "Charleston",
    "WI": "Madison", "WY": "Cheyenne"
}

# 🏛️ 61번 문제: 주지사 명단 (2025-2026 임기 기준)
US_GOVERNORS = {
    "AL": "Kay Ivey", "AK": "Mike Dunleavy", "AZ": "Katie Hobbs", "AR": "Sarah Huckabee Sanders",
    "CA": "Gavin Newsom", "CO": "Jared Polis", "CT": "Ned Lamont", "DE": "Matt Meyer",
    "FL": "Ron DeSantis", "GA": "Brian Kemp", "HI": "Josh Green", "ID": "Brad Little",
    "IL": "JB Pritzker", "IN": "Mike Braun", "IA": "Kim Reynolds", "KS": "Laura Kelly",
    "KY": "Andy Beshear", "LA": "Jeff Landry", "ME": "Janet Mills", "MD": "Wes Moore",
    "MA": "Maura Healey", "MI": "Gretchen Whitmer", "MN": "Tim Walz", "MS": "Tate Reeves",
    "MO": "Mike Kehoe", "MT": "Greg Gianforte", "NE": "Jim Pillen", "NV": "Joe Lombardo",
    "NH": "Kelly Ayotte", "NJ": "Phil Murphy", "NM": "Michelle Lujan Grisham", "NY": "Kathy Hochul",
    "NC": "Josh Stein", "ND": "Kelly Armstrong", "OH": "Mike DeWine", "OK": "Kevin Stitt",
    "OR": "Tina Kotek", "PA": "Josh Shapiro", "RI": "Dan McKee", "SC": "Henry McMaster",
    "SD": "Kristi Noem", "TN": "Bill Lee", "TX": "Greg Abbott", "UT": "Spencer Cox",
    "VT": "Phil Scott", "VA": "Abigail Spanberger", "WA": "Bob Ferguson", "WV": "Patrick Morrisey",
    "WI": "Tony Evers", "WY": "Mark Gordon"
}

# 주 이름 매핑 (State Code -> Full Name)
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

@router.get("/{zip_code}")
def get_civics_data(zip_code: str):
    """
    ZIP 코드를 받아서 23번(상원), 29번(하원), 30번(하원의장), 61번(주지사), 62번(수도) 정보를 반환
    """
    try:
        # 1. ZIP Code -> 위도/경도 변환
        nomi = pgeocode.Nominatim('us')
        location = nomi.query_postal_code(zip_code)
        
        if location.latitude != location.latitude: # NaN check
            return {"error": "Invalid ZIP Code"}

        lat = location.latitude
        lng = location.longitude
        state_code = location.state_code  # 예: 'CA'

        # 2. Open States API 호출 (연방 의원 찾기)
        url = "https://v3.openstates.org/people.geo"
        params = {
            "lat": lat,
            "lng": lng,
            "apikey": OPEN_STATES_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        results = {
            "state_name": US_STATES.get(state_code, state_code),
            "senators": [],       # 23번
            "representative": "", # 29번
            "speaker": SPEAKER_OF_THE_HOUSE, # 30번
            "governor": "",       # 61번
            "capital": ""         # 62번
        }

        # 3. API 결과 파싱 (상원/하원 구분)
        if "results" in data:
            for person in data["results"]:
                role = person.get("current_role", {})
                jurisdiction = person.get("jurisdiction", {})
                
                # 조건: 미국 연방(United States) 소속이어야 함
                if jurisdiction.get("name") == "United States":
                    # 상원 (Upper) -> US Senator (23번)
                    if role.get("org_classification") == "upper":
                        results["senators"].append(person["name"])
                    
                    # 하원 (Lower) -> US Representative (29번)
                    # *참고: 우편번호 중심 좌표라 정확도가 완벽하진 않지만 가장 가까운 의원을 가져옴
                    elif role.get("org_classification") == "lower":
                        results["representative"] = person["name"]

        # 4. 주지사 & 수도 매칭 (61번, 62번)
        results["governor"] = US_GOVERNORS.get(state_code, "Unknown Governor")
        results["capital"] = US_CAPITALS.get(state_code, "Unknown Capital")

        print(f"✅ ZIP: {zip_code} ({state_code}) 데이터 로드 완료")
        return results

    except Exception as e:
        print(f"🔥 Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))