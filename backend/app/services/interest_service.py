from datetime import date, timedelta, datetime
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import traceback
from app.utils.finance import smart_annualize_rate

logger = logging.getLogger(__name__)

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
        query += " AND id = CAST(:lid AS UUID)"
        params["lid"] = str(loan_id)

    loans = db.execute(text(query), params).mappings().all()

    for loan in loans:
        try:
            lid = str(loan["id"])
            principal = Decimal(str(loan["principal"]))
            entered_rate = Decimal(str(loan["interest_rate"]))

            # Bulletproof Date Parsing
            d_issued = loan["date_issued"]
            if isinstance(d_issued, str):
                d_issued = datetime.strptime(d_issued, "%Y-%m-%d").date()
            elif isinstance(d_issued, datetime):
                d_issued = d_issued.date()

            # Find the last recorded ledger date
            last_entry = db.execute(
                text("SELECT MAX(period_end) as max_end FROM interest_ledger WHERE loan_id = CAST(:lid AS UUID)"),
                {"lid": lid}
            ).mappings().first()

            if last_entry and last_entry["max_end"]:
                max_end = last_entry["max_end"]
                if isinstance(max_end, str):
                    max_end = datetime.strptime(max_end, "%Y-%m-%d").date()
                elif isinstance(max_end, datetime):
                    max_end = max_end.date()
                start_date = max_end + timedelta(days=1)
            else:
                start_date = d_issued

            entries_added = 0

            # Only accrue if we haven't reached today
            if start_date <= today:
                # ==========================================
                # --- THE SPLIT ENGINE ---
                # ==========================================
                if loan.get("amortization_type") == "emi":
                    # BANK RULES: Calculate in monthly chunks
                    current_date = start_date
                    next_month = current_date + relativedelta(months=1)

                    while next_month <= today:
                        monthly_rate = (entered_rate / Decimal("100")) / Decimal("12")
                        monthly_interest = (principal * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                        if monthly_interest > 0:
                            db.execute(text("""
                                INSERT INTO interest_ledger (id, loan_id, period_start, period_end, opening_balance, interest_accrued, closing_balance, calculated_at)
                                VALUES (gen_random_uuid(), CAST(:lid AS UUID), :p_start, :p_end, :op_bal, :accrued, :cl_bal, NOW())
                            """), {
                                "lid": lid,
                                "p_start": current_date,
                                "p_end": next_month - relativedelta(days=1),
                                "op_bal": float(principal),
                                "accrued": float(monthly_interest),
                                "cl_bal": float(principal + monthly_interest)
                            })
                            entries_added += 1

                        current_date = next_month
                        next_month = current_date + relativedelta(months=1)
                else:
                    # INFORMAL RULES: Strict Daily calculation
                    annual_rate = smart_annualize_rate(entered_rate, loan.get("interest_period", "yearly"))
                    daily_rate = (annual_rate / Decimal("100")) / Decimal("365")

                    current_date = start_date

                    while current_date <= today:
                        daily_interest = (principal * daily_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                        if daily_interest > 0:
                            db.execute(text("""
                                INSERT INTO interest_ledger (id, loan_id, period_start, period_end, opening_balance, interest_accrued, closing_balance, calculated_at)
                                VALUES (gen_random_uuid(), CAST(:lid AS UUID), :p_start, :p_end, :op_bal, :accrued, :cl_bal, NOW())
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

            # ALWAYS update the main loan totals, even if 0 entries were added today
            # This forces the balance_due to sync perfectly with the ledger table
            totals = db.execute(
                text("SELECT COALESCE(SUM(interest_accrued), 0) as total FROM interest_ledger WHERE loan_id = CAST(:lid AS UUID)"),
                {"lid": lid}
            ).mappings().first()

            total_interest = Decimal(str(totals["total"]))
            total_paid = Decimal(str(loan["total_paid"] or 0))
            balance_due = max(Decimal("0"), principal + total_interest - total_paid)

            db.execute(text("""
                UPDATE loans SET total_interest = :ti, balance_due = :bd, updated_at = NOW() WHERE id = CAST(:lid AS UUID)
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
            traceback.print_exc() # <--- Prints the exact crash to your Docker logs

    return stats

def recalculate_loan(db: Session, lid: str) -> None:
    """
    Full recalculation for a single loan. Clears ledger and rebuilds.
    """
    db.execute(text("DELETE FROM interest_ledger WHERE loan_id = CAST(:lid AS UUID)"), {"lid": str(lid)})
    db.execute(text("""
        UPDATE loans SET total_interest = 0, balance_due = principal - COALESCE(total_paid, 0)
        WHERE id = CAST(:lid AS UUID)
    """), {"lid": str(lid)})
    db.commit()
    accrue_interest(db, loan_id=str(lid))
