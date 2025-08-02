from smart_buddy.schemas.user_profile import UserProfileCreate
from smart_buddy.models.user_profile import UserProfile
from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.models.base import UserProfile
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("/")
def create_user_profile(profile: UserProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(UserProfile).filter(UserProfile.email == profile.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile with this email already exists")

    new_profile = UserProfile(**profile.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return {"message": "Profile created", "id": new_profile.id}


router = APIRouter()
templates = Jinja2Templates(directory="smart_buddy/templates")

@router.post("/create-profile")
async def create_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    personality_type: str = Form(...),
    study_style: str = Form(...),
    environment: str = Form(...),
    focus_area: str = Form(...),
    db: Session = Depends(get_db),
):
    profile = UserProfile(
        name=name,
        email=email,
        personality_type=personality_type,
        study_style=study_style,
        environment=environment,
        focus_area=focus_area,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return templates.TemplateResponse("profile_saved.html", {"request": request, "profile": profile})