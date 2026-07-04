from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.loan_fee import LoanFeeCreate, LoanFeeUpdate, LoanFeeResponse
from app.services import loan_fee_service

router = APIRouter()

@router.get("/loan/{loan_id}", response_model=List[LoanFeeResponse])
def get_fees_for_loan(loan_id: UUID, db: Session = Depends(get_db)):
    return loan_fee_service.get_by_loan(db, loan_id)

@router.post("/", response_model=LoanFeeResponse)
def create_fee(data: LoanFeeCreate, db: Session = Depends(get_db)):
    fee = loan_fee_service.create(db, data)

    # --- THE FIX: Write the Fee Receipt to the Audit Log ---
    from app.models.audit_log import AuditLog

    # Make the fee name look pretty (e.g. "pre_closure_fee" -> "Pre Closure Fee")
    fee_type = getattr(fee, 'fee_type', 'Fee').replace('_', ' ').title()

    audit_entry = AuditLog(
        loan_id=fee.loan_id,
        action="Fee Applied",
        description=f"A {fee_type} of {fee.amount} was charged to the loan."
    )
    db.add(audit_entry)
    db.commit()
    # -------------------------------------------------------

    return fee

@router.patch("/{fee_id}", response_model=LoanFeeResponse)
def update_fee(fee_id: UUID, data: LoanFeeUpdate, db: Session = Depends(get_db)):
    fee = loan_fee_service.update(db, fee_id, data)
    if not fee: raise HTTPException(status_code=404, detail="Fee not found")
    return fee

@router.delete("/{fee_id}")
def delete_fee(fee_id: UUID, db: Session = Depends(get_db)):
    success = loan_fee_service.delete(db, fee_id)
    if not success: raise HTTPException(status_code=404, detail="Fee not found")
    return {"detail": "Deleted successfully"}
