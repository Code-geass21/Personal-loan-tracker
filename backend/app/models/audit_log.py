import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id       = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    action        = Column(String(50), nullable=False)
    changed_field = Column(String(100))
    old_value     = Column(Text)
    new_value     = Column(Text)
    description   = Column(Text)
    changed_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())

    loan = relationship("Loan", back_populates="audit_logs")
