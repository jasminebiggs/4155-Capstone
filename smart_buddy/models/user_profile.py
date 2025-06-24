from sqlalchemy import Column, Integer, String, Text, Float
from smart_buddy.db import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    major = Column(String(100))
    bio = Column(Text)
    personality_traits = Column(String(100))
    study_style = Column(String(100))
    preferred_environment = Column(String(100))
    study_subjects = Column(Text)
    availability = Column(Text)
    goals = Column(Text)

    # Add these if your form is using them:
    openness = Column(Float)
    conscientiousness = Column(Float)
    extraversion = Column(Float)
    agreeableness = Column(Float)
    neuroticism = Column(Float)
