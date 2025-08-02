from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from pydantic import BaseModel, conint
from smart_buddy.db import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RatingInput(BaseModel):
    session_id: int
    reviewer_id: int
    partner_id: int
    rating: conint(ge=1, le=5)
    feedback: Optional[str] = None

@router.post("/rate")
def rate_partner(data: RatingInput, db: Session = Depends(get_db)):
    try:
        session_check = db.execute(
            text("SELECT id FROM sessions WHERE id = :session_id"),
            {"session_id": data.session_id}
        ).fetchone()
        if not session_check:
            raise HTTPException(status_code=400, detail="Session does not exist")

        existing = db.execute(
            text("SELECT id FROM ratings WHERE session_id = :session_id AND reviewer_id = :reviewer_id"),
            {"session_id": data.session_id, "reviewer_id": data.reviewer_id}
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Rating already submitted")

        db.execute(
            text("INSERT INTO ratings (session_id, reviewer_id, partner_id, rating, feedback) VALUES (:session_id, :reviewer_id, :partner_id, :rating, :feedback)"),
            data.dict()
        )
        db.commit()
        return {"message": "Rating submitted"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
