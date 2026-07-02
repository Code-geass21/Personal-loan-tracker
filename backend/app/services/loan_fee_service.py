from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.loan_fee import LoanFee
from app.schemas.loan_fee import LoanFeeCreate, LoanFeeUpdate
from app.services.recalculation_service import recalculate_loan_state

def get_by_loan(db: Session, loan_id: UUID) -> List[LoanFee]:
    return db.query(LoanFee).filter(LoanFee.loan_id == loan_id).all()

def create(db: Session, data: LoanFeeCreate) -> LoanFee:
    fee = LoanFee(**data.model_dump())
    db.add(fee)
    db.commit()
    db.refresh(fee)
    recalculate_loan_state(db, str(fee.loan_id)) # Trigger math engine!
    return fee

def update(db: Session, fee_id: UUID, data: LoanFeeUpdate) -> Optional[LoanFee]:
    fee = db.query(LoanFee).filter(LoanFee.id == fee_id).first()
    if not fee: return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(fee, key, value)

    db.commit()
    db.refresh(fee)
    recalculate_loan_state(db, str(fee.loan_id)) # Trigger math engine!
    return fee

def delete(db: Session, fee_id: UUID) -> bool:
    fee = db.query(LoanFee).filter(LoanFee.id == fee_id).first()
    if not fee: return False

    loan_id = fee.loan_id
    db.delete(fee)
    db.commit()
    recalculate_loan_state(db, str(loan_id)) # Trigger math engine!
    return True
