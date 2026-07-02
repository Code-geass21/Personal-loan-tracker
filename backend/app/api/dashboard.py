from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    try:
        summary = db.execute(
            text("SELECT * FROM v_dashboard_summary")
        ).mappings().first()
    except Exception as e:
        summary = {}

    try:
        overdue = db.execute(
            text("SELECT id, direction, status, currency, principal, balance_due, due_date, days_overdue, person_name FROM v_loan_summary WHERE status = 'overdue' ORDER BY days_overdue DESC LIMIT 5")
        ).mappings().all()
    except Exception as e:
        overdue = []

    try:
        due_soon = db.execute(
            text("SELECT id, direction, status, currency, principal, balance_due, due_date, days_until_due, person_name FROM v_loan_summary WHERE days_until_due <= 7 AND days_until_due IS NOT NULL ORDER BY days_until_due ASC LIMIT 5")
        ).mappings().all()
    except Exception as e:
        due_soon = []

    try:
        recent = db.execute(
            text("SELECT id, direction, status, currency, principal, balance_due, due_date, person_name FROM v_loan_summary ORDER BY date_issued DESC LIMIT 5")
        ).mappings().all()
    except Exception as e:
        recent = []

    try:
        unread_alerts = db.execute(
            text("SELECT COUNT(*) as count FROM alerts WHERE is_dismissed = FALSE AND is_sent = FALSE")
        ).mappings().first()
    except Exception as e:
        unread_alerts = None

    return {
        "summary":       dict(summary) if summary else {},
        "overdue":       [dict(r) for r in overdue],
        "due_soon":      [dict(r) for r in due_soon],
        "recent_loans":  [dict(r) for r in recent],
        "unread_alerts": unread_alerts["count"] if unread_alerts else 0,
    }

from app.services.trends_service import get_lending_trends

@router.get("/trends")
def lending_trends(months: int = 18, db: Session = Depends(get_db)):
    return get_lending_trends(db, months)

from app.services.interest_service import accrue_interest

@router.post("/accrue-interest")
def trigger_interest_accrual(db: Session = Depends(get_db)):
    """Manually trigger interest accrual — normally runs automatically daily."""
    stats = accrue_interest(db)
    return {"status": "ok", "stats": stats}
