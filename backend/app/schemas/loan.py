from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
# Added DayCountMethod to the import below
from app.models.loan import LoanDirection, LoanStatus, InterestType, InterestPeriod, DayCountMethod

class LoanBase(BaseModel):
    person_id:       UUID
    institution_type: str = "non_institutional"
    direction:       LoanDirection
    principal:       float
    currency:        str = "INR"
    interest_rate:   float = 0
    interest_type:   InterestType = InterestType.simple
    interest_period: InterestPeriod = InterestPeriod.monthly

    # <--- NEW: MATH & EMI FIELDS --->
    day_count_method: DayCountMethod = DayCountMethod.actual_365
    tenure_months:   Optional[int] = None
    emi_amount:      Optional[float] = None
    # --------------------------------

    date_issued:     date
    emi_start_date:  Optional[date] = None
    due_date:        Optional[date] = None
    purpose:         Optional[str] = None
    notes:           Optional[str] = None

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    institution_type: Optional[str] = None
    principal:       Optional[float] = None
    date_issued:     Optional[date] = None
    emi_start_date:  Optional[date] = None
    currency:        Optional[str] = None
    interest_rate:   Optional[float] = None
    interest_type:   Optional[InterestType] = None
    interest_period: Optional[InterestPeriod] = None

    # <--- NEW: MATH & EMI FIELDS --->
    day_count_method: Optional[DayCountMethod] = None
    tenure_months:   Optional[int] = None
    emi_amount:      Optional[float] = None
    # --------------------------------

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
