from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from app.models.person import RelationshipTag, KYCStatus, EntityType

class PersonBase(BaseModel):
    entity_type: EntityType = EntityType.individual # <--- NEW FIELD
    full_name: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    relationship: RelationshipTag = RelationshipTag.other
    address: Optional[str] = None
    national_id: Optional[str] = None
    notes: Optional[str] = None
    dob: Optional[date] = None
    id_expiry: Optional[date] = None
    trust_score: int = 50
    kyc_status: KYCStatus = KYCStatus.pending
    emergency_contact: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    entity_type: Optional[EntityType] = None # <--- NEW FIELD
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    relationship: Optional[RelationshipTag] = None
    address: Optional[str] = None
    national_id: Optional[str] = None
    notes: Optional[str] = None
    dob: Optional[date] = None
    id_expiry: Optional[date] = None
    trust_score: Optional[int] = None
    kyc_status: Optional[KYCStatus] = None
    emergency_contact: Optional[str] = None

class PersonResponse(PersonBase):
    id: UUID
    is_archived: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PersonWithStats(PersonResponse):
    total_lent: float = 0.0
    total_borrowed: float = 0.0
