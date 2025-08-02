# smart_buddy/routers/availability.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

# --- Local Imports ---
# Combining imports from both branches
from smart_buddy.db import get_db
from smart_buddy.models.sqlalchemy_models import Profile, Availability # Assuming Availability model exists
from smart_buddy.schemas.availability import AvailabilityCreate, AvailabilityResponse # Assuming these schemas are defined
from smart_buddy.config import SECRET_KEY, ALGORITHM # For JWT

# --- Router and Template Setup ---
router = APIRouter(prefix="/availability", tags=["Availability"])
templates = Jinja2Templates(directory="smart_buddy/templates")

# --- Authentication (from new-jasmine-sprint2) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token to get the current user.
    This is a critical security dependency.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Profile).filter(Profile.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- Helper Functions for Conflict Checking (from main) ---
def _times_overlap(start1, end1, start2, end2) -> bool:
    """Check if two time ranges overlap."""
    return start1 < end2 and start2 < end1

def _has_conflict(new_availability: AvailabilityCreate, existing: Availability) -> bool:
    """Check if two availability slots conflict."""
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

# --- Endpoints ---

@router.get("/", response_class=HTMLResponse)
async def availability_page(request: Request):
    """Display the availability calendar interface."""
    return templates.TemplateResponse("availability.html", {"request": request})

@router.get("/my-availability", response_model=List[AvailabilityResponse])
def get_my_availability(db: Session = Depends(get_db), current_user: Profile = Depends(get_current_user)):
    """Get all active availability slots for the currently logged-in user."""
    availability = db.query(Availability).filter(
        Availability.user_id == current_user.id,
        Availability.is_active == True
    ).all()
    return availability

@router.post("/", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: Profile = Depends(get_current_user)
):
    """Create a single availability slot for the currently logged-in user."""
    # Check for time conflicts with the user's existing slots
    existing_slots = db.query(Availability).filter(
        Availability.user_id == current_user.id,
        Availability.is_active == True
    ).all()
    
    for slot in existing_slots:
        if _has_conflict(availability, slot):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Time conflict with an existing availability slot."
            )
            
    # Create new availability and associate it with the current user
    new_availability = Availability(
        **availability.dict(),
        user_id=current_user.id
    )
    
    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)
    
    return new_availability

@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    availability_id: int, 
    db: Session = Depends(get_db), 
    current_user: Profile = Depends(get_current_user)
):
    """Delete an availability slot owned by the current user."""
    availability = db.query(Availability).filter(
        Availability.id == availability_id
    ).first()
    
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")

    # Security Check: Ensure the user owns this availability slot
    if availability.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this availability")
        
    # Soft delete
    availability.is_active = False
    db.commit()
    
    return {"message": "Availability deleted"}