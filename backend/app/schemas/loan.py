from pydantic import BaseModel, condecimal
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.loan import LoanDirection, LoanStatus, InterestType, InterestPeriod

class LoanBase(BaseModel):
    person_id:       UUID
    institution_type: str = "non_institutional" # <--- NEW FIELD
    direction:       LoanDirection
    principal:       float
    currency:        str = "INR"
    interest_rate:   float = 0
    interest_type:   InterestType = InterestType.simple
    interest_period: InterestPeriod = InterestPeriod.monthly
    date_issued:     date
    emi_start_date:  Optional[date] = None      # <--- NEW FIELD
    due_date:        Optional[date] = None
    purpose:         Optional[str] = None
    notes:           Optional[str] = None

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    institution_type: Optional[str] = None      # <--- NEW FIELD
    principal:       Optional[float] = None
    date_issued:     Optional[date] = None
    emi_start_date:  Optional[date] = None      # <--- NEW FIELD
    currency:        Optional[str] = None
    interest_rate:   Optional[float] = None
    interest_type:   Optional[InterestType] = None
    interest_period: Optional[InterestPeriod] = None
    due_date:        Optional[date] = None
    status:          Optional[LoanStatus] = None
    purpose:         Optional[str] = None
    notes:           Optional[str] = None

class LoanResponse(LoanBase):
    id:             UUID
    status:         LoanStatus
    total_paid:     float
    total_interest: float
    balance_due:    float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LoanSummary(LoanResponse):
    person_name:         str
    person_nickname:     Optional[str]
    person_phone:        Optional[str]
    person_relationship: str
    days_overdue:        Optional[int]
    days_until_due:      Optional[int]
