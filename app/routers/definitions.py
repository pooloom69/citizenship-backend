import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/definitions", tags=["definitions"])

# 데이터 파일 위치 로드
DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/definitions.json")

def load_definitions():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/")
def get_all_definitions():
    return load_definitions()

@router.get("/{def_id}")
def get_definition(def_id: int):
    definitions = load_definitions()
    for item in definitions:
        if item["id"] == def_id:
            return item
    raise HTTPException(status_code=404, detail="Definition not found")