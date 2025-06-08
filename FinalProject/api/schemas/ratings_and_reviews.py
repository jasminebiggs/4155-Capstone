from datetime import DATETIME
from typing import Optional
from pydantic import BaseModel

class RatingsAndReviews(BaseModel):
    user_id: int
    sandwich_id: int
    rating_score: int
    review_text: Optional[str] = None

class RatingsAndReviewsCreate(BaseModel):
    user_id: int
    sandwich_id: int

class RatingsAndReviewsUpdate(BaseModel):
    rating_score: Optional[int] = None
    review_text: Optional[str] = None

class RatingsAndReviewsRead(BaseModel):
    id: int
    user_id: int
    sandwich_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True