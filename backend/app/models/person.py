import uuid
import enum
from datetime import date
from sqlalchemy import Column, String, Boolean, Text, Date, Integer, func
from sqlalchemy import Enum as SAEnum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship as orm_relationship
from app.database import Base

# <--- NEW: ENTITY TYPE ENUM --->
class EntityType(str, enum.Enum):
    individual = "individual"
    institution = "institution"

class RelationshipTag(str, enum.Enum):
    friend = "friend"
    family = "family"
    colleague = "colleague"
    acquaintance = "acquaintance"
    other = "other"

class KYCStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

class Person(Base):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # <--- NEW: ENTITY TYPE COLUMN --->
    entity_type = Column(String(50), nullable=False, default="individual")

    full_name = Column(String(200), nullable=False)
    nickname = Column(String(100))
    phone = Column(String(50))
    email = Column(String(200))

    relationship = Column(SAEnum(RelationshipTag, name="relationship_tag"), nullable=False, default=RelationshipTag.other)

    dob = Column(Date, nullable=True)
    id_expiry = Column(Date, nullable=True)
    trust_score = Column(Integer, default=50)
    kyc_status = Column(SAEnum(KYCStatus, name="kyc_status"), default=KYCStatus.pending)
    emergency_contact = Column(String(200), nullable=True)

    address = Column(Text)
    national_id = Column(String(100))
    notes = Column(Text)
    is_archived = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    loans = orm_relationship("Loan", back_populates="person", lazy="select")
