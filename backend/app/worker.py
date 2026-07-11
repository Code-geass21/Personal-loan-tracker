import time
import logging
import calendar
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.loan import Loan, LoanStatus
from app.models.alert import Alert, AlertType
from app.models.loan_fee import LoanFee  # Fixes the mapping crash!
from app.config import settings
from app.services.interest_service import accrue_interest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_months(start_date: date, months: int) -> date:
    """Safely jumps forward by X months, handling leap years."""
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def generate_alerts(db: Session):
    today = date.today()
    due_soon_date = today + timedelta(days=settings.ALERT_LEAD_DAYS)

    # 1. Process Active & Partial Loans
    active_loans = db.query(Loan).filter(
        Loan.status.in_([LoanStatus.active, LoanStatus.partial])
    ).all()

    for loan in active_loans:
        # --- DYNAMIC EMI ALERTS ---
        if getattr(loan, 'emi_start_date', None) and getattr(loan, 'tenure_months', None):
            past_emis = []
            future_emis = []

            for i in range(loan.tenure_months):
                emi_date = add_months(loan.emi_start_date, i)
                if emi_date < today:
                    past_emis.append(emi_date)
                else:
                    future_emis.append(emi_date)

            # Most Recent Missed EMI Alert
            if past_emis:
                last_missed = past_emis[-1]
                days_late = (today - last_missed).days
                existing_overdue = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today).first()
                if not existing_overdue:
                    db.add(Alert(loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today, message=f"EMI scheduled for {last_missed.strftime('%b %d, %Y')} is overdue by {days_late} days!"))

            # Next Upcoming EMI Alert
            if future_emis:
                next_emi = future_emis[0]
                days_until = (next_emi - today).days
                if days_until <= settings.ALERT_LEAD_DAYS:
                    existing_soon = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today).first()
                    if not existing_soon:
                        db.add(Alert(loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today, message=f"Upcoming EMI due on {next_emi.strftime('%b %d, %Y')} (in {days_until} days)"))
        # --------------------------

        # --- FINAL DUE DATE ALERTS ---
        if loan.due_date:
            if loan.due_date == due_soon_date:
                existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today).first()
                if not existing:
                    db.add(Alert(loan_id=loan.id, alert_type=AlertType.due_soon, trigger_date=today, message=f"Final loan payoff due in {settings.ALERT_LEAD_DAYS} days ({loan.due_date.strftime('%b %d, %Y')})"))
            elif loan.due_date < today:
                existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today).first()
                if not existing:
                    db.add(Alert(loan_id=loan.id, alert_type=AlertType.overdue, trigger_date=today, message=f"Loan is overdue by {(today - loan.due_date).days} days"))
        # -----------------------------

        # --- PARTIAL PAYMENT REMINDER ---
        if loan.status == LoanStatus.partial:
            existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today).first()
            if not existing:
                db.add(Alert(loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today, message=f"Partial payment made — balance remaining: {loan.balance_due} {loan.currency}"))

    # --- SETTLED / FORECLOSED LOANS ---
    closed_loans = db.query(Loan).filter(
        Loan.status.in_([LoanStatus.settled, LoanStatus.cancelled])
    ).all()

    for loan in closed_loans:
        status_str = loan.status.value.upper() if hasattr(loan.status, 'value') else str(loan.status).upper()
        existing = db.query(Alert).filter_by(loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today).first()
        if not existing:
            db.add(Alert(loan_id=loan.id, alert_type=AlertType.partial_reminder, trigger_date=today, message=f"LOAN {status_str}: Balance cleared or closed on {today.strftime('%b %d, %Y')}"))
    # ----------------------------------

    db.commit()
    logger.info(f"Alert check complete for {today}")


def run():
    logger.info("Worker started — alerts + interest accrual")
    while True:
        db = SessionLocal()
        try:
            stats = accrue_interest(db)
            logger.info(f"Interest accrual done: {stats}")
            generate_alerts(db)
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            db.close()

        time.sleep(86400)

if __name__ == "__main__":
    run()
