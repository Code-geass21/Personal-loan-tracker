from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from typing import List, Optional
from datetime import date
from app.models.target import Target
from app.schemas.target import TargetCreate, TargetUpdate
from datetime import date, datetime

def get_all(db: Session) -> List[Target]:
    rows = db.execute(text("""
        SELECT t.* FROM targets t
        LEFT JOIN loans l ON t.loan_id = l.id
        WHERE t.is_active = true
          AND (
              t.scope = 'global'
              OR (t.scope = 'loan' AND l.id IS NOT NULL AND l.status = 'active')
          )
        ORDER BY t.created_at
    """)).mappings().all()
    return [Target(**dict(r)) for r in rows]

def get_by_id(db: Session, target_id: UUID) -> Optional[Target]:
    row = db.execute(text(
        "SELECT * FROM targets WHERE id = :id"
    ), {"id": str(target_id)}).mappings().first()
    return Target(**dict(row)) if row else None

def get_global(db: Session) -> Optional[Target]:
    row = db.execute(text(
        "SELECT * FROM targets WHERE scope = 'global' AND is_active = true LIMIT 1"
    )).mappings().first()
    return Target(**dict(row)) if row else None

def get_for_loan(db: Session, loan_id: UUID) -> Optional[Target]:
    row = db.execute(text(
        "SELECT * FROM targets WHERE scope = 'loan' AND loan_id = :loan_id AND is_active = true LIMIT 1"
    ), {"loan_id": str(loan_id)}).mappings().first()
    return Target(**dict(row)) if row else None

def create(db: Session, data: TargetCreate) -> Target:
    # Deactivate existing active target for same scope
    if str(data.scope) in ('global', 'global_'):
        db.execute(text(
            "UPDATE targets SET is_active = false WHERE scope = 'global' AND is_active = true"
        ))
    else:
        db.execute(text(
            "UPDATE targets SET is_active = false WHERE scope = 'loan' AND loan_id = :loan_id AND is_active = true"
        ), {"loan_id": str(data.loan_id)})

    scope_val = "global" if str(data.scope) in ("global", "global_") else "loan"
    loan_id_val = str(data.loan_id) if data.loan_id else None

    row = db.execute(text("""
        INSERT INTO targets (id, scope, loan_id, monthly_amount, currency, notes, is_active)
        VALUES (gen_random_uuid(), :scope, :loan_id, :monthly_amount, :currency, :notes, true)
        RETURNING *
    """), {
        "scope":          scope_val,
        "loan_id":        loan_id_val,
        "monthly_amount": float(data.monthly_amount),
        "currency":       data.currency,
        "notes":          data.notes,
    }).mappings().first()

    db.commit()
    return Target(**dict(row))

def update(db: Session, target_id: UUID, data: TargetUpdate) -> Optional[Target]:
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        return get_by_id(db, target_id)
    sets = ", ".join([f"{k} = :{k}" for k in fields])
    fields["id"] = str(target_id)
    db.execute(text(f"UPDATE targets SET {sets} WHERE id = :id"), fields)
    db.commit()
    return get_by_id(db, target_id)

def delete(db: Session, target_id: UUID) -> bool:
    result = db.execute(text(
        "DELETE FROM targets WHERE id = :id"
    ), {"id": str(target_id)})
    db.commit()
    return result.rowcount > 0

def get_progress(db: Session, target: Target, target_month: str = None) -> dict:
    # 1. Determine the Start and End of the target month
    if target_month:
        # Parse incoming 'YYYY-MM' from the React UI
        dt = datetime.strptime(target_month, "%Y-%m").date()
        month_start = dt.replace(day=1)
    else:
        month_start = date.today().replace(day=1)

    # Cap the timeframe at the 1st of the NEXT month
    if month_start.month == 12:
        month_end = date(month_start.year + 1, 1, 1)
    else:
        month_end = date(month_start.year, month_start.month + 1, 1)

    scope_val = str(target.scope).replace("global_", "global")

    # 2. Query with strict bounds (>= month_start AND < month_end)
    if scope_val == "global":
        result = db.execute(text("""
            SELECT COALESCE(SUM(p.amount), 0) as total
            FROM payments p
            JOIN loans l ON p.loan_id = l.id
            WHERE p.payment_date >= :month_start AND p.payment_date < :month_end
            AND l.status != 'cancelled'
        """), {"month_start": month_start, "month_end": month_end}).mappings().first()
    else:
        result = db.execute(text("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE loan_id = :loan_id
            AND payment_date >= :month_start AND payment_date < :month_end
        """), {"loan_id": str(target.loan_id), "month_start": month_start, "month_end": month_end}).mappings().first()

    paid          = float(result["total"])
    target_amount = float(target.monthly_amount)
    raw_pct       = (paid / target_amount * 100) if target_amount > 0 else 0
    safe_pct      = min(100.0, raw_pct)

    # NEW: Fetch the person's name if this is an individual loan target
    person_name = None
    if target.loan_id:
        name_row = db.execute(text("""
            SELECT p.full_name
            FROM loans l JOIN persons p ON l.person_id = p.id
            WHERE l.id = :loan_id
        """), {"loan_id": str(target.loan_id)}).mappings().first()
        if name_row:
            person_name = name_row["full_name"]

    return {
        "target_id":       str(target.id),
        "scope":           scope_val,
        "loan_id":         str(target.loan_id) if target.loan_id else None,
        "person_name":     person_name, # <-- Pass the name to React!
        "monthly_amount":  target_amount,
        "currency":        target.currency,
        "paid_this_month": paid,
        "remaining":       max(0, target_amount - paid),
        "percentage":      round(safe_pct, 1),
        "month":           month_start.strftime("%B %Y"),
        "query_month":     month_start.strftime("%Y-%m")
    }
