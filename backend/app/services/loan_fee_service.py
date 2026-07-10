from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.loan_fee import LoanFee
from app.models.audit_log import AuditLog
from app.schemas.loan_fee import LoanFeeCreate, LoanFeeUpdate
from app.services.recalculation_service import recalculate_loan_state
from app.models.audit_log import AuditLog

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

    changes = []
    for key, new_val in data.model_dump(exclude_unset=True).items():
        old_val = getattr(fee, key)
        
        # Track the exact difference for the audit log
        if str(old_val) != str(new_val):
            clean_name = key.replace('_', ' ').title()
            changes.append(f"{clean_name}: {old_val} ➔ {new_val}")
            
        setattr(fee, key, new_val)

    # Secure the compliance gap
    if changes:
        audit = AuditLog(
            loan_id=fee.loan_id,
            action="Fee Edited",
            description=" | ".join(changes)
        )
        db.add(audit)

    db.commit()
    db.refresh(fee)
    recalculate_loan_state(db, str(fee.loan_id)) # Trigger math engine!
    return fee

def delete(db: Session, fee_id: UUID) -> bool:
    fee = db.query(LoanFee).filter(LoanFee.id == fee_id).first()
    if not fee: return False

    loan_id_str = str(fee.loan_id)

    # --- 1. RECORD THE AUDIT LOG ---
    audit = AuditLog(
        loan_id=fee.loan_id,
        action="Fee Deleted",
        description=f"Deleted charge '{fee.fee_name}' of amount {fee.amount}"
    )
    db.add(audit)

    # --- 2. DELETE THE FEE ---
    db.delete(fee)
    db.commit()

    # --- 3. RECALCULATE THE LEDGER ---
    recalculate_loan_state(db, loan_id_str)
    return True
