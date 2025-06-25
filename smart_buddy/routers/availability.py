# smart_buddy/routers/availability.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from smart_buddy.db import get_db
from smart_buddy.models.availability import Availability
from smart_buddy.schemas.availability import AvailabilityCreate, AvailabilityResponse

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.post("/")
def create_availability(
    user_id: int,
    availability: AvailabilityCreate,
    db: Session = Depends(get_db)
):
    """Create a single availability slot for a user"""
    
    # Check for time conflicts
    existing = db.query(Availability).filter(
        Availability.user_id == user_id,
        Availability.is_active == True
    ).all()
    
    for slot in existing:
        if _has_conflict(availability, slot):
            raise HTTPException(
                status_code=400, 
                detail="Time conflict with existing availability"
            )
    
    # Create new availability
    new_availability = Availability(
        user_id=user_id,
        availability_type=availability.availability_type,
        date=availability.date,
        day_of_week=availability.day_of_week,
        start_time=availability.start_time,
        end_time=availability.end_time
    )
    
    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)
    
    return {"message": "Availability created", "id": new_availability.id}

@router.get("/user/{user_id}")
def get_user_availability(user_id: int, db: Session = Depends(get_db)):
    """Get all availability slots for a user"""
    
    availability = db.query(Availability).filter(
        Availability.user_id == user_id,
        Availability.is_active == True
    ).all()
    
    return availability

@router.delete("/{availability_id}")
def delete_availability(availability_id: int, db: Session = Depends(get_db)):
    """Delete an availability slot"""
    
    availability = db.query(Availability).filter(
        Availability.id == availability_id
    ).first()
    
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    
    # Soft delete
    availability.is_active = False
    db.commit()
    
    return {"message": "Availability deleted"}

def _has_conflict(new_availability: AvailabilityCreate, existing: Availability) -> bool:
    """Check if two availability slots conflict"""
    
    # Same specific date
    if new_availability.date and existing.date == new_availability.date:
        return _times_overlap(
            new_availability.start_time, new_availability.end_time,
            existing.start_time, existing.end_time
        )
    
    # Same recurring day
    if (new_availability.day_of_week is not None and 
        existing.day_of_week == new_availability.day_of_week):
        return _times_overlap(
            new_availability.start_time, new_availability.end_time,
            existing.start_time, existing.end_time
        )
    
    return False

def _times_overlap(start1, end1, start2, end2) -> bool:
    """Check if two time ranges overlap"""
    return start1 < end2 and start2 < end1