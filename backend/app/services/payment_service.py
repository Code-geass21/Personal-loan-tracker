from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.recalculation_service import recalculate_loan_state

def get_by_loan(db: Session, loan_id: UUID) -> List[Payment]:
    return db.query(Payment).filter(
        Payment.loan_id == loan_id
    ).order_by(Payment.payment_date.desc(), Payment.created_at.desc()).all()

def get_by_id(db: Session, payment_id: UUID) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()

def create(db: Session, data: PaymentCreate) -> Payment:
    payment = Payment(**data.model_dump())
    db.add(payment)
    db.commit()
    # Trigger the real-time engine!
    recalculate_loan_state(db, str(payment.loan_id))
    db.refresh(payment)
    return payment

def update(db: Session, payment_id: UUID, data: PaymentUpdate) -> Optional[Payment]:
    payment = get_by_id(db, payment_id)
    if not payment:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)
    db.commit()
    # Trigger the real-time engine!
    recalculate_loan_state(db, str(payment.loan_id))
    db.refresh(payment)
    return payment

def delete(db: Session, payment_id: UUID) -> bool:
    payment = get_by_id(db, payment_id)
    if not payment:
        return False
    loan_id_str = str(payment.loan_id)
    db.delete(payment)
    db.commit()
    # Trigger the real-time engine!
    recalculate_loan_state(db, loan_id_str)
    return True
