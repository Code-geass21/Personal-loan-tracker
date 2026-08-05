"""
Interest accrual service — Personal Loan Tracker
Uses actual calendar months, not fixed 30-day periods.
Supports simple and compound interest.
"""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import date, timedelta
from app.utils.finance import smart_annualize_rate

logger = logging.getLogger(__name__)

def _next_month(d: date) -> date:
    """Return the same day next month (handles month-end correctly)."""
    return d + relativedelta(months=1)

def _period_end(period_start: date, period: str) -> date:
    """Return the last day of the period (exclusive end = next period start - 1 day)."""
    if period == "monthly":
        return _next_month(period_start) - relativedelta(days=1)
    elif period == "weekly":
        return period_start + relativedelta(days=6)
    elif period == "daily":
        return period_start
    elif period == "yearly":
        return period_start + relativedelta(years=1) - relativedelta(days=1)
    return _next_month(period_start) - relativedelta(days=1)

def _next_period_start(period_start: date, period: str) -> date:
    """Return the start of the next period."""
    if period == "monthly":
        return _next_month(period_start)
    elif period == "weekly":
        return period_start + relativedelta(days=7)
    elif period == "daily":
        return period_start + relativedelta(days=1)
    elif period == "yearly":
        return period_start + relativedelta(years=1)
    return _next_month(period_start)


def accrue_interest(db: Session, loan_id: str = None):
    """
    Forces every loan to accrue and log interest.
    Uses Strict Daily math for informal loans, and Monthly math for EMI/bank loans.
    """
    stats = {"processed": 0, "entries_added": 0, "errors": 0}
    today = date.today()

    query = "SELECT * FROM loans WHERE status IN ('active', 'partial')"
    params = {}
    if loan_id:
        query += " AND id = :lid"
        params["lid"] = str(loan_id)

    loans = db.execute(text(query), params).mappings().all()

    for loan in loans:
        try:
            lid = loan["id"]
            principal = Decimal(str(loan["principal"]))
            entered_rate = Decimal(str(loan["interest_rate"]))
            date_issued = loan["date_issued"]

            # Find the last recorded ledger date
            last_entry = db.execute(
                text("SELECT MAX(period_end) as max_end FROM interest_ledger WHERE loan_id = :lid"),
                {"lid": lid}
            ).mappings().first()

            if last_entry and last_entry["max_end"]:
                start_date = last_entry["max_end"] + timedelta(days=1)
            else:
                start_date = date_issued

            # Stop if we are already caught up to today
            if start_date > today:
                stats["processed"] += 1
                continue

            entries_added = 0

            # ==========================================
            # --- THE SPLIT ENGINE STARTS EXACTLY HERE ---
            # ==========================================
            if loan.get("amortization_type") == "emi":
                # BANK RULES: Calculate in monthly chunks to match formal EMI statements
                from dateutil.relativedelta import relativedelta
                current_date = start_date
                next_month = current_date + relativedelta(months=1)

                while next_month <= today:
                    # Bank Math: Annual Rate / 12
                    monthly_rate = (entered_rate / Decimal("100")) / Decimal("12")
                    monthly_interest = (principal * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    if monthly_interest > 0:
                        db.execute(text("""
                            INSERT INTO interest_ledger (id, loan_id, period_start, period_end, opening_balance, interest_accrued, closing_balance, created_at)
                            VALUES (gen_random_uuid(), :lid, :p_start, :p_end, :op_bal, :accrued, :cl_bal, NOW())
                        """), {
                            "lid": lid,
                            "p_start": current_date,
                            "p_end": next_month - relativedelta(days=1), # Closes the day before
                            "op_bal": float(principal),
                            "accrued": float(monthly_interest),
                            "cl_bal": float(principal + monthly_interest)
                        })
                        entries_added += 1

                    current_date = next_month
                    next_month = current_date + relativedelta(months=1)

            else:
                # INFORMAL RULES: Strict Daily calculation for personal tracking
                from app.utils.finance import smart_annualize_rate
                annual_rate = smart_annualize_rate(entered_rate, loan["interest_period"])
                daily_rate = (annual_rate / Decimal("100")) / Decimal("365")

                current_date = start_date

                while current_date <= today:
                    daily_interest = (principal * daily_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    if daily_interest > 0:
                        db.execute(text("""
                            INSERT INTO interest_ledger (id, loan_id, period_start, period_end, opening_balance, interest_accrued, closing_balance, created_at)
                            VALUES (gen_random_uuid(), :lid, :p_start, :p_end, :op_bal, :accrued, :cl_bal, NOW())
                        """), {
                            "lid": lid,
                            "p_start": current_date,
                            "p_end": current_date,
                            "op_bal": float(principal),
                            "accrued": float(daily_interest),
                            "cl_bal": float(principal + daily_interest)
                        })
                        entries_added += 1

                    current_date += timedelta(days=1)
            # ==========================================
            # --- THE SPLIT ENGINE ENDS EXACTLY HERE ---
            # ==========================================

            # Update the main loan totals
            if entries_added > 0:
                totals = db.execute(
                    text("SELECT COALESCE(SUM(interest_accrued), 0) as total FROM interest_ledger WHERE loan_id = :lid"),
                    {"lid": lid}
                ).mappings().first()

                total_interest = Decimal(str(totals["total"]))
                total_paid = Decimal(str(loan["total_paid"] or 0))
                balance_due = max(Decimal("0"), principal + total_interest - total_paid)

                db.execute(text("""
                    UPDATE loans SET total_interest = :ti, balance_due = :bd, updated_at = NOW() WHERE id = :lid
                """), {
                    "ti": float(total_interest),
                    "bd": float(balance_due),
                    "lid": lid,
                })
                stats["entries_added"] += entries_added

            db.commit()
            stats["processed"] += 1

        except Exception as e:
            db.rollback()
            stats["errors"] += 1
            logger.error(f"Accrual error for loan {loan['id']}: {e}")

    return stats


def recalculate_loan(db: Session, lid: str) -> None:
    """
    Full recalculation for a single loan — call after any modification.
    Clears ledger and rebuilds from scratch.
    """
    # Clear existing ledger
    db.execute(text("DELETE FROM interest_ledger WHERE loan_id = :lid"), {"lid": lid})
    # Reset interest totals (trigger will recalc balance from payments)
    db.execute(text("""
        UPDATE loans SET total_interest = 0,
        balance_due = principal - total_paid
        WHERE id = :lid
    """), {"lid": lid})
    db.commit()
    # Re-accrue from scratch
    accrue_interest(db, loan_id=lid)
