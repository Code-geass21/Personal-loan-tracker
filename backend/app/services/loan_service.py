from app.services.recalculation_service import recalculate_loan_state
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from typing import List, Optional
from datetime import date
from app.models.loan import Loan, LoanStatus
from app.schemas.loan import LoanCreate, LoanUpdate

def get_all(
    db: Session,
    direction: Optional[str] = None,
    status: Optional[str] = None,
    person_id: Optional[UUID] = None,
    currency: Optional[str] = None,
) -> List[dict]:
    query = "SELECT * FROM v_loan_summary WHERE 1=1"
    params = {}
    if direction:
        query += " AND direction = :direction"
        params["direction"] = direction
    if status:
        query += " AND status = :status"
        params["status"] = status
    if person_id:
        query += " AND person_id = :person_id"
        params["person_id"] = str(person_id)
    if currency:
        query += " AND currency = :currency"
        params["currency"] = currency
    query += " ORDER BY due_date ASC NULLS LAST"
    result = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in result]

def get_by_id(db: Session, loan_id: UUID) -> Optional[Loan]:
    return db.query(Loan).filter(Loan.id == loan_id).first()

def get_summary_by_id(db: Session, loan_id: UUID) -> Optional[dict]:
    result = db.execute(
        text("SELECT * FROM v_loan_summary WHERE id = :id"),
        {"id": str(loan_id)}
    ).mappings().first()
    return dict(result) if result else None

def create(db: Session, data: LoanCreate):
    loan_data = data.model_dump()
    loan = Loan(**loan_data)
    loan.balance_due = loan.principal
    db.add(loan)
    db.commit()
    # Trigger the real-time engine!
    recalculate_loan_state(db, str(loan.id))
    db.refresh(loan)
    return loan

def update(db: Session, loan_id: UUID, data: LoanUpdate):
    loan = get_by_id(db, loan_id)
    if not loan:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(loan, field, value)
    
    db.commit()
    # Trigger the real-time engine!
    recalculate_loan_state(db, str(loan.id))
    db.refresh(loan)
    return loan

def delete(db: Session, loan_id: UUID) -> bool:
    loan = get_by_id(db, loan_id)
    if not loan:
        return False
    db.delete(loan)
    db.commit()
    return True

def cancel(db: Session, loan_id: UUID) -> Optional[Loan]:
    loan = get_by_id(db, loan_id)
    if not loan:
        return None
    loan.status = LoanStatus.cancelled
    db.commit()
    db.refresh(loan)
    return loan

def get_overdue(db: Session) -> List[dict]:
    result = db.execute(
        text("SELECT * FROM v_loan_summary WHERE status = 'overdue' ORDER BY days_overdue DESC")
    ).mappings().all()
    return [dict(r) for r in result]

def get_due_soon(db: Session, days: int = 7) -> List[dict]:
    result = db.execute(
        text("SELECT * FROM v_loan_summary WHERE days_until_due <= :days AND days_until_due IS NOT NULL ORDER BY days_until_due ASC"),
        {"days": days}
    ).mappings().all()
    return [dict(r) for r in result]
