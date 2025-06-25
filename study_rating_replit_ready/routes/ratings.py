# routes/ratings.py
# completed on June 22

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conint
from database import database

router = APIRouter()

class RatingInput(BaseModel):
    session_id: int
    reviewer_id: int
    partner_id: int
    rating: conint(ge=1, le=5)
    feedback: str | None = None

@router.post("/rate")
async def rate_partner(data: RatingInput):
    session_check = await database.fetch_one(
        """
        SELECT id FROM study_sessions
        WHERE id = :session_id AND status = 'completed'
        """,
        {"session_id": data.session_id}
    )
    if not session_check:
        raise HTTPException(status_code=400, detail="Session not complete")

    existing = await database.fetch_one(
        """
        SELECT id FROM ratings
        WHERE session_id = :session_id AND reviewer_id = :reviewer_id
        """,
        {"session_id": data.session_id, "reviewer_id": data.reviewer_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Rating already submitted")

    await database.execute(
        """
        INSERT INTO ratings (session_id, reviewer_id, partner_id, rating, feedback)
        VALUES (:session_id, :reviewer_id, :partner_id, :rating, :feedback)
        """,
        data.dict()
    )

    return {"message": "Rating submitted"}
