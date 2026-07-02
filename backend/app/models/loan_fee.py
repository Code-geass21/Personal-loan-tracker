import uuid
import enum
from sqlalchemy import Column, String, Numeric, Enum as SAEnum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class FeeStatus(str, enum.Enum):
    pending = "pending"
    paid    = "paid"
    waived  = "waived"

class LoanFee(Base):
    __tablename__ = "loan_fees"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id    = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)

    fee_name   = Column(String(100), nullable=False)
    amount     = Column(Numeric(15, 2), nullable=False)
    status     = Column(SAEnum(FeeStatus, name="fee_status"), nullable=False, default=FeeStatus.pending)

    # <--- NEW PHASE 3: TAX FIELDS --->
    tax_rate   = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    loan       = relationship("Loan", back_populates="fees")
