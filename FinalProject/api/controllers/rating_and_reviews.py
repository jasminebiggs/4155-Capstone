from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import models, schemas  # Adjust import if needed

# Create a new Rating
def create(db: Session, rating: schemas.RatingCreate):
    db_rating = models.Rating(
        user_id=rating.user_id,
        sandwich_id=rating.sandwich_id,
        review_text=rating.review_text,
        rating_score=rating.rating_score
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

# Read all Ratings
def read_all(db: Session):
    return db.query(models.Rating).all()

# Read a single Rating by ID
def read_one(db: Session, rating_id: int):
    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

# Update a Rating
def update(db: Session, rating_id: int, rating_update: schemas.RatingUpdate):
    db_rating = db.query(models.Rating).filter(models.Rating.id == rating_id)
    if not db_rating.first():
        raise HTTPException(status_code=404, detail="Rating not found")

    update_data = rating_update.model_dump(exclude_unset=True)
    db_rating.update(update_data, synchronize_session=False)
    db.commit()
    return db_rating.first()

# Delete a Rating
def delete(db: Session, rating_id: int):
    db_rating = db.query(models.Rating).filter(models.Rating.id == rating_id)
    if not db_rating.first():
        raise HTTPException(status_code=404, detail="Rating not found")

    db_rating.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
