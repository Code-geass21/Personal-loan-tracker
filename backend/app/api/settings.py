from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT key, value FROM app_settings")).mappings().all()
    return {r["key"]: r["value"] for r in rows}

@router.patch("/{key}")
def update_setting(key: str, payload: dict, db: Session = Depends(get_db)):
    value = payload.get("value")
    db.execute(text("""
        INSERT INTO app_settings (key, value, updated_at)
        VALUES (:key, :value, NOW())
        ON CONFLICT (key) DO UPDATE SET value = :value, updated_at = NOW()
    """), {"key": key, "value": value})
    db.commit()
    return {"key": key, "value": value}
