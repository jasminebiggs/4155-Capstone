from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.schemas.rating import RatingCreate
from smart_buddy.models.rating import Rating

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("/")
def submit_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    new_rating = Rating(
        session_id=rating.session_id,
        rater_id=rating.rater_id,
        partner_id=rating.partner_id,
        rating_score=rating.rating_score,
        review_text=rating.review_text
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return {"message": "Rating submitted", "id": new_rating.id}
