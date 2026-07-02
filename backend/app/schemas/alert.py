from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.alert import AlertType

class AlertResponse(BaseModel):
    id:           UUID
    loan_id:      UUID
    alert_type:   AlertType
    trigger_date: date
    message:      str
    is_sent:      bool
    is_dismissed: bool
    created_at:   datetime

    class Config:
        from_attributes = True
