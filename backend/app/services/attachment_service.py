import os
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List, Optional
from uuid import UUID
from app.models.attachment import Attachment, AttachmentParent, FileType
from app.config import settings

ALLOWED_MIME = {
    "image/jpeg": FileType.photo,
    "image/png":  FileType.photo,
    "image/webp": FileType.photo,
    "application/pdf": FileType.pdf,
    "image/gif":  FileType.screenshot,
}

def get_by_parent(db: Session, parent_id: UUID, parent_type: AttachmentParent) -> List[Attachment]:
    return db.query(Attachment).filter(
        Attachment.parent_id   == parent_id,
        Attachment.parent_type == parent_type
    ).order_by(Attachment.uploaded_at.desc()).all()

def get_by_id(db: Session, attachment_id: UUID) -> Optional[Attachment]:
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()

async def upload(
    db: Session,
    parent_id: UUID,
    parent_type: AttachmentParent,
    file: UploadFile,
    notes: Optional[str] = None
) -> Attachment:
    # Validate size
    contents = await file.read()
    size_kb = len(contents) // 1024
    max_kb = settings.MAX_UPLOAD_MB * 1024
    if size_kb > max_kb:
        raise ValueError(f"File too large. Max {settings.MAX_UPLOAD_MB}MB allowed.")

    # Determine file type
    mime = file.content_type or "application/octet-stream"
    file_type = ALLOWED_MIME.get(mime, FileType.other)

    # Save file to uploads volume
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{uuid.uuid4()}{ext}"
    subdir = os.path.join(settings.UPLOAD_DIR, str(parent_type), str(parent_id))
    os.makedirs(subdir, exist_ok=True)
    filepath = os.path.join(subdir, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    # Relative path for storage
    rel_path = os.path.join(str(parent_type), str(parent_id), filename)

    attachment = Attachment(
        parent_id     = parent_id,
        parent_type   = parent_type,
        file_type     = file_type,
        original_name = file.filename or filename,
        file_path     = rel_path,
        mime_type     = mime,
        file_size_kb  = max(1, size_kb),
        notes         = notes,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def delete(db: Session, attachment_id: UUID) -> bool:
    attachment = get_by_id(db, attachment_id)
    if not attachment:
        return False
    # Delete file from disk
    full_path = os.path.join(settings.UPLOAD_DIR, attachment.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    db.delete(attachment)
    db.commit()
    return True
