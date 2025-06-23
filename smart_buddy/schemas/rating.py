from pydantic import BaseModel
from typing import Optional

class RatingCreate(BaseModel):
    session_id: int
    rater_id: int
    partner_id: int
    rating_score: int
    review_text: Optional[str] = None
