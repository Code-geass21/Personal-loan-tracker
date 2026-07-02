import uuid
from sqlalchemy import Column, Numeric, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Target(Base):
    __tablename__ = "targets"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope          = Column(String(10), nullable=False)  # 'global' or 'loan'
    loan_id        = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"))
    monthly_amount = Column(Numeric(15, 2), nullable=False)
    currency       = Column(String(3), nullable=False, default="INR")
    notes          = Column(Text)
    is_active      = Column(Boolean, nullable=False, default=True)
    created_at     = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at     = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
