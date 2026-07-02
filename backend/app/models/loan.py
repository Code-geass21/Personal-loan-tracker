import uuid
import enum
from sqlalchemy import Column, String, Numeric, Date, Text
from sqlalchemy import Enum as SAEnum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class LoanDirection(str, enum.Enum):
    lent     = "lent"
    borrowed = "borrowed"

class LoanStatus(str, enum.Enum):
    active    = "active"
    partial   = "partial"
    settled   = "settled"
    overdue   = "overdue"
    cancelled = "cancelled"

class InterestType(str, enum.Enum):
    simple   = "simple"
    compound = "compound"

class InterestPeriod(str, enum.Enum):
    daily   = "daily"
    weekly  = "weekly"
    monthly = "monthly"
    yearly  = "yearly"

class Loan(Base):
    __tablename__ = "loans"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id       = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)

    institution_type = Column(String(20), default="non_institutional")      # <--- NEW FIELD
    direction       = Column(SAEnum(LoanDirection, name="loan_direction"),   nullable=False)
    principal       = Column(Numeric(15, 2),         nullable=False)
    currency        = Column(String(3),              nullable=False, default="INR")

    interest_rate   = Column(Numeric(8, 4),          nullable=False, default=0)
    interest_type   = Column(SAEnum(InterestType, name="interest_type"),   nullable=False, default=InterestType.simple)
    interest_period = Column(SAEnum(InterestPeriod, name="interest_period"),  nullable=False, default=InterestPeriod.monthly)

    date_issued     = Column(Date, nullable=False, server_default=func.current_date())
    emi_start_date  = Column(Date)                                          # <--- NEW FIELD
    due_date        = Column(Date)

    status          = Column(SAEnum(LoanStatus, name="loan_status"), nullable=False, default=LoanStatus.active)
    purpose         = Column(String(500))
    notes           = Column(Text)

    total_paid      = Column(Numeric(15, 2), nullable=False, default=0)
    total_interest  = Column(Numeric(15, 2), nullable=False, default=0)
    balance_due     = Column(Numeric(15, 2), nullable=False, default=0)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    person          = relationship("Person",        back_populates="loans")
    payments        = relationship("Payment",       back_populates="loan", cascade="all, delete-orphan")
    interest_ledger = relationship("InterestLedger", back_populates="loan", cascade="all, delete-orphan")
    alerts          = relationship("Alert",         back_populates="loan", cascade="all, delete-orphan")
    audit_logs      = relationship("AuditLog",      back_populates="loan", cascade="all, delete-orphan")
    fees            = relationship("LoanFee",       back_populates="loan", cascade="all, delete-orphan")
