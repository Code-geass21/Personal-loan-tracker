import time
import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.loan import Loan, LoanStatus
from app.models.alert import Alert, AlertType
from app.config import settings
from app.services.interest_service import accrue_interest
import calendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- STEP 1: ADD CALENDAR HELPER ---
def add_months(start_date: date, months: int) -> date:
    """Safely jumps forward by X months, handling leap years."""
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
# -----------------------------------

def generate_alerts(db: Session):
    today = date.today()
    due_soon_date = today + timedelta(days=settings.ALERT_LEAD_DAYS)
    yesterday = today - timedelta(days=1)

    # 1. Process Active & Partial Loans
    active_loans = db.query(Loan).filter(
        Loan.status.in_([LoanStatus.active, LoanStatus.partial])
    ).all()

    for loan in active_loans:
        # --- STEP 2: EACH EMI ALERTS LOOP ---
        if getattr(loan, 'emi_start_date', None) and getattr(loan, 'tenure_months', None):
            for i in range(loan.tenure_months):
                emi_date = add_months(loan.emi_start_date, i)

                # Upcoming EMI Reminder
                if emi_date == due_soon_date:
                    existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today).first()
                    if not existing:
                        db.add(Alert(loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today, message=f"Upcoming EMI due on {emi_date.strftime('%b %d, %Y')} ({settings.ALERT_LEAD_DAYS} days)"))

                # Missed EMI Alert
                elif emi_date == yesterday:
                    existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today).first()
                    if not existing:
                        db.add(Alert(loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today, message=f"EMI scheduled for {emi_date.strftime('%b %d, %Y')} is overdue!"))
        # ------------------------------------

        # --- STEP 3: FINAL DUE DATE ALERTS ---
        if loan.due_date:
            if loan.due_date == due_soon_date:
                existing = db.query(Alert).filter_by(
                    loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today
                ).first()
                if not existing:
                    db.add(Alert(
                        loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today,
                        message=f"Final loan payoff due in {settings.ALERT_LEAD_DAYS} days ({loan.due_date.strftime('%b %d, %Y')})"
                    ))
            elif loan.due_date < today:
                existing = db.query(Alert).filter_by(
                    loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today
                ).first()
                if not existing:
                    db.add(Alert(
                        loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today,
                        message=f"Loan is overdue by {(today - loan.due_date).days} days"
                    ))
        # -------------------------------------

        # --- PARTIAL PAYMENT REMINDER ---
        if loan.status == LoanStatus.partial:
            existing = db.query(Alert).filter_by(
                loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today
            ).first()
            if not existing:
                db.add(Alert(
                    loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today,
                    message=f"Partial payment made — balance remaining: {loan.balance_due} {loan.currency}"
                ))

    # --- STEP 4: SETTLED / FORECLOSED LOANS ---
    closed_loans = db.query(Loan).filter(
        Loan.status.in_([LoanStatus.settled, LoanStatus.cancelled])
    ).all()

    for loan in closed_loans:
        status_str = loan.status.value.upper() if hasattr(loan.status, 'value') else str(loan.status).upper()
        # We reuse 'partial_reminder' to avoid a DB Enum crash, then style it Green in React based on the text!
        existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today).first()
        if not existing:
            db.add(Alert(
                loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today,
                message=f"LOAN {status_str}: Balance cleared or closed on {today.strftime('%b %d, %Y')}"
            ))
    # ---------------------------------------

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
