from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.schemas.attachment import AttachmentResponse
from app.services import payment_service, attachment_service
from app.models.attachment import AttachmentParent

router = APIRouter()

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: UUID, db: Session = Depends(get_db)):
    payment = payment_service.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    payment = payment_service.create(db, data)

    # --- THE FIX: Write the Payment Receipt to the Audit Log ---
    from app.models.audit_log import AuditLog

    # If the UI sent a note (like "Pre-Closure Settlement"), include it!
    note = f" (Note: {payment.notes})" if getattr(payment, 'notes', None) else ""

    audit_entry = AuditLog(
        loan_id=payment.loan_id,
        action="Payment Received",
        description=f"A payment of {payment.amount} was recorded for {payment.payment_date}.{note}"
    )
    db.add(audit_entry)
    db.commit()
    # -----------------------------------------------------------

    return payment

@router.patch("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: UUID, data: PaymentUpdate, db: Session = Depends(get_db)):
    result = payment_service.update(db, payment_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result

@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: UUID, db: Session = Depends(get_db)):
    success = payment_service.delete(db, payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")
    # Note: Returning nothing on a 204 No Content is standard and correct!

@router.post("/{payment_id}/attachments", response_model=AttachmentResponse)
async def upload_payment_attachment(
    payment_id: UUID,
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    payment = payment_service.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    try:
        return await attachment_service.upload(db, payment_id, AttachmentParent.payment, file, notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{payment_id}/attachments", response_model=List[AttachmentResponse])
def get_payment_attachments(payment_id: UUID, db: Session = Depends(get_db)):
    return attachment_service.get_by_parent(db, payment_id, AttachmentParent.payment)
