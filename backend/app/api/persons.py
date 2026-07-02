from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.person import PersonCreate, PersonUpdate, PersonResponse, PersonWithStats
from app.services import person_service

router = APIRouter()

@router.get("/", response_model=List[PersonResponse])
def list_persons(
    include_archived: bool = False,
    db: Session = Depends(get_db)
):
    return person_service.get_all(db, include_archived)

@router.get("/{person_id}", response_model=PersonWithStats)
def get_person(person_id: UUID, db: Session = Depends(get_db)):
    result = person_service.get_with_stats(db, person_id)
    if not result:
        raise HTTPException(status_code=404, detail="Person not found")
    return result

@router.post("/", response_model=PersonResponse, status_code=201)
def create_person(data: PersonCreate, db: Session = Depends(get_db)):
    return person_service.create(db, data)

@router.patch("/{person_id}", response_model=PersonResponse)
def update_person(person_id: UUID, data: PersonUpdate, db: Session = Depends(get_db)):
    result = person_service.update(db, person_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Person not found")
    return result

@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: UUID, db: Session = Depends(get_db)):
    success = person_service.delete(db, person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
