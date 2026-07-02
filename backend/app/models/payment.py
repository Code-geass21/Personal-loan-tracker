import uuid
import enum
from sqlalchemy import Column, String, Numeric, Date, Text, Boolean
from sqlalchemy import Enum as SAEnum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class PaymentMethod(str, enum.Enum):
    cash           = "cash"
    bank_transfer  = "bank_transfer"
    mobile_payment = "mobile_payment"
    upi            = "upi"
    crypto         = "crypto"
    other          = "other"

class Payment(Base):
    __tablename__ = "payments"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id      = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)

    amount       = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(Date, nullable=False, server_default=func.current_date())
    method       = Column(SAEnum(PaymentMethod, name="payment_method"), nullable=False, default=PaymentMethod.cash)
    reference    = Column(String(200))
    notes        = Column(Text)

    # <--- NEW PHASE 3: TAX FIELDS --->
    tax_rate     = Column(Numeric(5, 2), default=0)
    tax_amount   = Column(Numeric(15, 2), default=0)
    principal_component = Column(Numeric(15, 2), default=0)
    interest_component  = Column(Numeric(15, 2), default=0)
    is_manual = Column(Boolean, default=False)

    created_at   = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at   = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    loan = relationship("Loan", back_populates="payments")
