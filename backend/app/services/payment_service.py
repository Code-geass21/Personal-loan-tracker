from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.recalculation_service import recalculate_loan_state
from app.models.audit_log import AuditLog

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
        
    changes = []
    for field, new_val in data.model_dump(exclude_unset=True).items():
        old_val = getattr(payment, field)
        
        # Track the exact difference for the audit log
        if str(old_val) != str(new_val):
            clean_name = field.replace('_', ' ').title()
            changes.append(f"{clean_name}: {old_val} ➔ {new_val}")
            
        setattr(payment, field, new_val)

    # Secure the compliance gap
    if changes:
        audit = AuditLog(
            loan_id=payment.loan_id,
            action="Payment Edited",
            description=" | ".join(changes)
        )
        db.add(audit)

    db.commit()
    # Trigger the real-time engine to rebuild the ledger with the new payment values!
    recalculate_loan_state(db, str(payment.loan_id))
    db.refresh(payment)
    return payment

def delete(db: Session, payment_id: UUID) -> bool:
    payment = get_by_id(db, payment_id)
    if not payment:
        return False

    loan_id_str = str(payment.loan_id)

    # --- 1. RECORD THE AUDIT LOG ---
    audit = AuditLog(
        loan_id=payment.loan_id,
        action="Payment Deleted",
        description=f"Deleted a payment of {payment.amount} (Originally recorded on: {payment.payment_date})"
    )
    db.add(audit)

    # --- 2. DELETE THE PAYMENT ---
    db.delete(payment)
    db.commit()

    # --- 3. RECALCULATE THE LEDGER ---
    recalculate_loan_state(db, loan_id_str)
    return True
