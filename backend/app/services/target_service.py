from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from typing import List, Optional
from datetime import date
from app.models.target import Target
from app.schemas.target import TargetCreate, TargetUpdate

def get_all(db: Session) -> List[Target]:
    rows = db.execute(text(
        "SELECT * FROM targets WHERE is_active = true ORDER BY created_at"
    )).mappings().all()
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

def get_progress(db: Session, target: Target) -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    scope_val = str(target.scope).replace("global_", "global")

    if scope_val == "global":
        result = db.execute(text("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments WHERE payment_date >= :month_start
        """), {"month_start": month_start}).mappings().first()
    else:
        result = db.execute(text("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments WHERE loan_id = :loan_id AND payment_date >= :month_start
        """), {"loan_id": str(target.loan_id), "month_start": month_start}).mappings().first()

    paid          = float(result["total"])
    target_amount = float(target.monthly_amount)
    pct           = min(100, (paid / target_amount * 100)) if target_amount > 0 else 0

    return {
        "target_id":       str(target.id),
        "scope":           scope_val,
        "loan_id":         str(target.loan_id) if target.loan_id else None,
        "monthly_amount":  target_amount,
        "currency":        target.currency,
        "paid_this_month": paid,
        "remaining":       max(0, target_amount - paid),
        "percentage":      round(pct, 1),
        "month":           month_start.strftime("%B %Y"),
    }
