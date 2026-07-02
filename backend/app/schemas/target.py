from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TargetBase(BaseModel):
    scope:          str  # 'global' or 'loan'
    loan_id:        Optional[UUID] = None
    monthly_amount: float
    currency:       str = "INR"
    notes:          Optional[str] = None

class TargetCreate(TargetBase):
    pass

class TargetUpdate(BaseModel):
    monthly_amount: Optional[float] = None
    currency:       Optional[str]   = None
    notes:          Optional[str]   = None
    is_active:      Optional[bool]  = None

class TargetResponse(TargetBase):
    id:         UUID
    is_active:  bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
