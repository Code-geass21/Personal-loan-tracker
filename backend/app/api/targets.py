from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.target import TargetCreate, TargetUpdate, TargetResponse
from app.services import target_service

router = APIRouter()

@router.get("/", response_model=List[TargetResponse])
def list_targets(db: Session = Depends(get_db)):
    return target_service.get_all(db)

@router.get("/progress")
def all_progress(db: Session = Depends(get_db)):
    """Progress for the global target and every active loan target."""
    targets = target_service.get_all(db)
    return [target_service.get_progress(db, t) for t in targets]

@router.get("/global")
def global_target(db: Session = Depends(get_db)):
    target = target_service.get_global(db)
    if not target:
        return None
    return target_service.get_progress(db, target)

@router.get("/loan/{loan_id}")
def loan_target(loan_id: UUID, db: Session = Depends(get_db)):
    target = target_service.get_for_loan(db, loan_id)
    if not target:
        return None
    return target_service.get_progress(db, target)

@router.post("/", response_model=TargetResponse, status_code=201)
def create_target(data: TargetCreate, db: Session = Depends(get_db)):
    return target_service.create(db, data)

@router.patch("/{target_id}", response_model=TargetResponse)
def update_target(target_id: UUID, data: TargetUpdate, db: Session = Depends(get_db)):
    result = target_service.update(db, target_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Target not found")
    return result

@router.delete("/{target_id}", status_code=204)
def delete_target(target_id: UUID, db: Session = Depends(get_db)):
    success = target_service.delete(db, target_id)
    if not success:
        raise HTTPException(status_code=404, detail="Target not found")
