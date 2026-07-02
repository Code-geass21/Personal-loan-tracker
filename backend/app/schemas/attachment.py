from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.attachment import AttachmentParent, FileType

class AttachmentResponse(BaseModel):
    id:            UUID
    parent_id:     UUID
    parent_type:   AttachmentParent
    file_type:     FileType
    original_name: str
    file_path:     str
    mime_type:     str
    file_size_kb:  int
    notes:         Optional[str]
    uploaded_at:   datetime

    class Config:
        from_attributes = True
