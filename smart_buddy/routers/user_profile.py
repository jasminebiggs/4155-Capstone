from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from smart_buddy.schemas.user_profile import ProfileSchema
from smart_buddy.models.user_profile import UserProfile
from smart_buddy.db import get_db

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("/", response_model=dict)
async def create_profile(profile: ProfileSchema, db: Session = Depends(get_db)):
    existing = db.query(UserProfile).filter(UserProfile.email == profile.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile with this email already exists")

    new_profile = UserProfile(**profile.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return {"message": "Profile created successfully", "id": new_profile.id}

