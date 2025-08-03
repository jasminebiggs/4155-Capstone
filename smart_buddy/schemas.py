
from pydantic import BaseModel
from typing import List, Optional

class ProfileCreate(BaseModel):
    username: str
    email: str
    password: str
    study_style: str
    environment: str
    personality: str
    focus_areas: List[str]
    availability: dict

class SessionCreate(BaseModel):
    student1: str
    student2: str
    datetime: str

class RatingCreate(BaseModel):
    reviewer: str
    reviewee: str
    score: int
    feedback: Optional[str] = None
