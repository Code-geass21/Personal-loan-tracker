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

def accrue_interest(db: Session, loan_id: str = None) -> dict:
    """
    Accrue interest for all eligible loans (or a specific loan).
    Uses actual calendar periods, not fixed day counts.
    """
    today = date.today()
    stats = {"processed": 0, "entries_added": 0, "errors": 0}

    query = """
        SELECT id, principal, interest_rate, interest_type, interest_period,
               date_issued, balance_due, total_interest, total_paid, status
        FROM loans
        WHERE status IN ('active', 'partial', 'overdue')
          AND interest_rate > 0
    """
    params = {}
    if loan_id:
        query += " AND id = :loan_id"
        params["loan_id"] = loan_id

    loans = db.execute(text(query), params).mappings().all()

    for loan in loans:
        try:
            lid            = str(loan["id"])
            principal      = Decimal(str(loan["principal"]))
            rate           = Decimal(str(loan["interest_rate"]))
            interest_type  = str(loan["interest_type"])
            period         = str(loan["interest_period"])
            total_paid     = Decimal(str(loan["total_paid"] or 0))

            # Find last accrual
            last = db.execute(text("""
                SELECT period_end, closing_balance
                FROM interest_ledger
                WHERE loan_id = :lid
                ORDER BY period_end DESC LIMIT 1
            """), {"lid": lid}).mappings().first()

            if last:
                current_start   = last["period_end"] + relativedelta(days=1)
                opening_balance = Decimal(str(last["closing_balance"]))
            else:
                current_start   = loan["date_issued"]
                opening_balance = principal

            entries      = 0
            new_interest = Decimal("0")

            # Process all complete periods up to today
            while True:
                p_end = _period_end(current_start, period)
                if p_end >= today:
                    break  # Period not complete yet

                if interest_type == "simple":
                    # Simple: use principal minus payments made before this period
                    paid_before = db.execute(text("""
                        SELECT COALESCE(SUM(amount), 0) as paid
                        FROM payments
                        WHERE loan_id = :lid AND payment_date < :p_start
                    """), {"lid": lid, "p_start": current_start}).mappings().first()
                    effective_base = principal - Decimal(str(paid_before["paid"]))
                    if effective_base < 0:
                        effective_base = Decimal("0")
                    opening_balance = effective_base
                    interest = (effective_base * rate / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                else:
                    # Compound: use closing balance of previous period
                    interest = (opening_balance * rate / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )

                closing_balance = opening_balance + interest

                # Insert — skip if period already exists
                result = db.execute(text("""
                    INSERT INTO interest_ledger
                        (loan_id, period_start, period_end, opening_balance,
                         interest_accrued, closing_balance, calc_type, rate_applied)
                    VALUES
                        (:lid, :p_start, :p_end, :opening_bal,
                         :interest, :closing_bal, :calc_type, :rate)
                    ON CONFLICT (loan_id, period_start) DO NOTHING
                """), {
                    "lid":         lid,
                    "p_start":     current_start,
                    "p_end":       p_end,
                    "opening_bal": float(opening_balance),
                    "interest":    float(interest),
                    "closing_bal": float(closing_balance),
                    "calc_type":   interest_type,
                    "rate":        float(rate),
                })

                if result.rowcount > 0:
                    new_interest    += interest
                    opening_balance  = closing_balance
                    entries         += 1

                current_start = _next_period_start(current_start, period)

            if entries > 0:
                # Recalculate totals from ledger (source of truth)
                ledger_total = db.execute(text("""
                    SELECT COALESCE(SUM(interest_accrued), 0) as total
                    FROM interest_ledger WHERE loan_id = :lid
                """), {"lid": lid}).mappings().first()

                total_interest = Decimal(str(ledger_total["total"]))
                balance_due    = max(Decimal("0"), principal + total_interest - total_paid)

                db.execute(text("""
                    UPDATE loans SET
                        total_interest = :ti,
                        balance_due    = :bd,
                        updated_at     = NOW()
                    WHERE id = :lid
                """), {
                    "ti":  float(total_interest),
                    "bd":  float(balance_due),
                    "lid": lid,
                })
                stats["entries_added"] += entries

            db.commit()
            stats["processed"] += 1

        except Exception as e:
            db.rollback()
            stats["errors"] += 1
            logger.error(f"Interest accrual error for loan {loan['id']}: {e}")

    logger.info(f"Interest accrual complete: {stats}")
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
