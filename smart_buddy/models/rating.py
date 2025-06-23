from sqlalchemy import Column, Integer, String
from .base import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    rater_id = Column(Integer, nullable=False)
    partner_id = Column(Integer, nullable=False)
    rating_score = Column(Integer, nullable=False)
    review_text = Column(String, nullable=True)
