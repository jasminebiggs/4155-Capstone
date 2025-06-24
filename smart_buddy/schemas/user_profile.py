from pydantic import BaseModel
from typing import Optional

class ProfileSchema(BaseModel):
    name: str
    email: str
    major: Optional[str] = None
    bio: Optional[str] = None
    personality_traits: Optional[str] = None
    openness: Optional[int] = None
    conscientiousness: Optional[int] = None
    extraversion: Optional[int] = None
    agreeableness: Optional[int] = None
    neuroticism: Optional[int] = None
    study_style: Optional[str] = None
    preferred_environment: Optional[str] = None
    study_subjects: Optional[str] = None
    availability: Optional[str] = None
    goals: Optional[str] = None
