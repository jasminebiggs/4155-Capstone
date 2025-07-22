
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.models import sqlalchemy_models as models
from smart_buddy import schemas

router = APIRouter()

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.username == username).first()
    if profile and password == "password":  # Simple static password check for demo
        return RedirectResponse(url="/home", status_code=303)
    raise HTTPException(status_code=401, detail="Invalid username or password")

@router.post("/profile")
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = models.Profile(
        username=profile.username,
        study_style=profile.study_style,
        environment=profile.environment,
        personality=profile.personality,
        focus_areas=profile.focus_areas,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return {"message": f"Profile saved for {db_profile.username}"}

@router.post("/schedule")
def schedule_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = models.Session(
        student1=session.student1,
        student2=session.student2,
        datetime=session.datetime,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return {"message": "Session scheduled", "session_id": db_session.id}

@router.get("/matched-users")
def get_matched_users(username: str, db: Session = Depends(get_db)):
    profiles = db.query(models.Profile).filter(models.Profile.username != username).all()
    matches = [profile.username for profile in profiles]
    return {"matches": matches}

@router.post("/ratings")
def submit_rating(rating: schemas.RatingCreate, db: Session = Depends(get_db)):
    db_rating = models.Rating(
        reviewer=rating.reviewer,
        reviewee=rating.reviewee,
        score=rating.score,
        feedback=rating.feedback,
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return {"message": "Rating submitted", "rating_id": db_rating.id}

@router.get("/ratings")
def view_ratings(db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).all()
    return {"ratings": [{"reviewer": r.reviewer, "reviewee": r.reviewee, "score": r.score, "feedback": r.feedback} for r in ratings]}
