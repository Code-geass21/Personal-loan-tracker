import uuid
import enum
from sqlalchemy import Column, String, Boolean, Date, Text, Enum as SAEnum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AlertType(str, enum.Enum):
    overdue           = "overdue"
    due_soon          = "due_soon"
    partial_reminder  = "partial_reminder"

class Alert(Base):
    __tablename__ = "alerts"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id      = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    alert_type   = Column(SAEnum(AlertType), nullable=False)
    trigger_date = Column(Date, nullable=False)
    message      = Column(Text, nullable=False)
    is_sent      = Column(Boolean, nullable=False, default=False)
    is_dismissed = Column(Boolean, nullable=False, default=False)
    created_at   = Column(TIMESTAMP(timezone=True), server_default=func.now())
    sent_at      = Column(TIMESTAMP(timezone=True))
    dismissed_at = Column(TIMESTAMP(timezone=True))

    loan = relationship("Loan", back_populates="alerts")
