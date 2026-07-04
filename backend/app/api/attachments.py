from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.schemas.attachment import AttachmentResponse
from app.services import attachment_service
from app.models.attachment import AttachmentParent
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.post("/loan/{loan_id}", response_model=AttachmentResponse)
async def upload_loan_attachment(
    loan_id: UUID,
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        return await attachment_service.upload(db, loan_id, AttachmentParent.loan, file, notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: UUID, db: Session = Depends(get_db)):
    success = attachment_service.delete(db, attachment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attachment not found")

@router.get("/{attachment_id}/download")
def download_attachment(attachment_id: UUID, db: Session = Depends(get_db)):
    attachment = attachment_service.get_by_id(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Grab the relative path from the database
    db_path = attachment.file_path

    # Glue the Docker upload folder path to the front of it
    base_upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
    full_path = os.path.join(base_upload_dir, db_path)

    # Check if the file exists using the FULL path
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"File not found at: {full_path}")

    return FileResponse(
        path=full_path,
        media_type=attachment.mime_type,
        filename=attachment.original_name
    )
