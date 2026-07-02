import time
import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.loan import Loan, LoanStatus
from app.models.alert import Alert, AlertType
from app.config import settings
from app.services.interest_service import accrue_interest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_alerts(db: Session):
    today = date.today()
    due_soon_date = today + timedelta(days=settings.ALERT_LEAD_DAYS)

    active_loans = db.query(Loan).filter(
        Loan.status.in_([LoanStatus.active, LoanStatus.partial])
    ).all()

    for loan in active_loans:
        if not loan.due_date:
            continue

        if loan.due_date < today:
            existing = db.query(Alert).filter_by(
                loan_id=loan.id,
                alert_type=AlertType.overdue,
                trigger_date=today
            ).first()
            if not existing:
                db.add(Alert(
                    loan_id=loan.id,
                    alert_type=AlertType.overdue,
                    trigger_date=today,
                    message=f"Loan is overdue by {(today - loan.due_date).days} days"
                ))

        elif loan.due_date <= due_soon_date:
            existing = db.query(Alert).filter_by(
                loan_id=loan.id,
                alert_type=AlertType.due_soon,
                trigger_date=today
            ).first()
            if not existing:
                db.add(Alert(
                    loan_id=loan.id,
                    alert_type=AlertType.due_soon,
                    trigger_date=today,
                    message=f"Loan due in {(loan.due_date - today).days} days"
                ))

        if loan.status == LoanStatus.partial:
            existing = db.query(Alert).filter_by(
                loan_id=loan.id,
                alert_type=AlertType.partial_reminder,
                trigger_date=today
            ).first()
            if not existing:
                db.add(Alert(
                    loan_id=loan.id,
                    alert_type=AlertType.partial_reminder,
                    trigger_date=today,
                    message=f"Partial payment made — balance remaining: {loan.balance_due} {loan.currency}"
                ))

    db.commit()
    logger.info(f"Alert check complete for {today}")

def run():
    logger.info("Worker started — alerts + interest accrual")
    while True:
        db = SessionLocal()
        try:
            # 1. Accrue interest on all eligible loans
            stats = accrue_interest(db)
            logger.info(f"Interest accrual done: {stats}")

            # 2. Generate alerts
            generate_alerts(db)

        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            db.close()

        # Sleep 24 hours
        time.sleep(86400)

if __name__ == "__main__":
    run()
