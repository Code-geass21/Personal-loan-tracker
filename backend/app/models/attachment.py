import uuid
import enum
from sqlalchemy import Column, String, Integer, Text, Enum as SAEnum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class AttachmentParent(str, enum.Enum):
    loan    = "loan"
    payment = "payment"

class FileType(str, enum.Enum):
    photo      = "photo"
    pdf        = "pdf"
    screenshot = "screenshot"
    other      = "other"

class Attachment(Base):
    __tablename__ = "attachments"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id     = Column(UUID(as_uuid=True), nullable=False)
    parent_type   = Column(SAEnum(AttachmentParent, name="attachment_parent"), nullable=False)
    file_type     = Column(SAEnum(FileType, name="file_type"), nullable=False, default=FileType.other)
    original_name = Column(String(500), nullable=False)
    file_path     = Column(Text, nullable=False)
    mime_type     = Column(String(100), nullable=False)
    file_size_kb  = Column(Integer, nullable=False)
    notes         = Column(Text)
    uploaded_at   = Column(TIMESTAMP(timezone=True), server_default=func.now())
