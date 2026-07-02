from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.payment import PaymentMethod

class PaymentBase(BaseModel):
    loan_id:      UUID
    amount:       float
    payment_date: date
    method:       PaymentMethod = PaymentMethod.cash
    reference:    Optional[str] = None
    notes:        Optional[str] = None

    # <--- PHASE 3: TAX FIELDS --->
    tax_rate:     Optional[float] = 0.0
    tax_amount:   Optional[float] = 0.0

    # <--- PHASE 4: MANUAL OVERRIDE & COMPONENT BREAKDOWN --->
    principal_component: Optional[float] = 0.0
    interest_component:  Optional[float] = 0.0
    is_manual:           Optional[bool] = False

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount:       Optional[float] = None
    payment_date: Optional[date] = None
    method:       Optional[PaymentMethod] = None
    reference:    Optional[str] = None
    notes:        Optional[str] = None
    tax_rate:     Optional[float] = None
    tax_amount:   Optional[float] = None

    # Allow updates to these fields
    principal_component: Optional[float] = None
    interest_component:  Optional[float] = None
    is_manual:           Optional[bool] = None

class PaymentResponse(PaymentBase):
    id:         UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
