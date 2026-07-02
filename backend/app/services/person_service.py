from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.person import Person
from app.models.loan import Loan, LoanDirection, LoanStatus
from app.schemas.person import PersonCreate, PersonUpdate

def get_all(db: Session, include_archived: bool = False) -> List[Person]:
    q = db.query(Person)
    if not include_archived:
        q = q.filter(Person.is_archived == False)
    return q.order_by(Person.full_name).all()

def get_by_id(db: Session, person_id: UUID) -> Optional[Person]:
    return db.query(Person).filter(Person.id == person_id).first()

def create(db: Session, data: PersonCreate) -> Person:
    person = Person(**data.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person

def update(db: Session, person_id: UUID, data: PersonUpdate) -> Optional[Person]:
    person = get_by_id(db, person_id)
    if not person:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person

def delete(db: Session, person_id: UUID) -> bool:
    person = get_by_id(db, person_id)
    if not person:
        return False
    loan_count = db.query(Loan).filter(Loan.person_id == person_id).count()
    if loan_count > 0:
        person.is_archived = True
        db.commit()
    else:
        db.delete(person)
        db.commit()
    return True

def get_with_stats(db: Session, person_id: UUID) -> Optional[dict]:
    person = get_by_id(db, person_id)
    if not person:
        return None
    loans = db.query(Loan).filter(Loan.person_id == person_id).all()
    total_lent     = sum(l.principal for l in loans if l.direction == LoanDirection.lent)
    total_borrowed = sum(l.principal for l in loans if l.direction == LoanDirection.borrowed)
    active_loans   = sum(1 for l in loans if l.status not in [LoanStatus.settled, LoanStatus.cancelled])
    net_balance    = total_lent - total_borrowed
    return {
        "id":            person.id,
        "full_name":     person.full_name,
        "nickname":      person.nickname,
        "phone":         person.phone,
        "email":         person.email,
        "relationship":  person.relationship,
        "address":       person.address,
        "national_id":   person.national_id,
        "notes":         person.notes,
        "is_archived":   person.is_archived,
        "created_at":    person.created_at,
        "updated_at":    person.updated_at,
        "total_lent":    float(total_lent),
        "total_borrowed":float(total_borrowed),
        "net_balance":   float(net_balance),
        "active_loans":  active_loans,
    }
