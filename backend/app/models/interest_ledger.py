import uuid
from sqlalchemy import Column, Numeric, Date, Enum as SAEnum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.loan import InterestType

class InterestLedger(Base):
    __tablename__ = "interest_ledger"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id          = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    period_start     = Column(Date, nullable=False)
    period_end       = Column(Date, nullable=False)
    opening_balance  = Column(Numeric(15, 2), nullable=False)
    interest_accrued = Column(Numeric(15, 2), nullable=False)
    closing_balance  = Column(Numeric(15, 2), nullable=False)
    calc_type        = Column(SAEnum(InterestType), nullable=False)
    rate_applied     = Column(Numeric(8, 4), nullable=False)
    calculated_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())

    loan = relationship("Loan", back_populates="interest_ledger")
