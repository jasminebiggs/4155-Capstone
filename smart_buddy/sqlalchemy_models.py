from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from smart_buddy.db import Base
from datetime import datetime  # Needed for DateTime formatting

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True)
    study_style = Column(String(50))
    preferred_environment = Column(String(50))
    personality_traits = Column(JSON)
    academic_focus_areas = Column(JSON)
    password = Column(String(100), nullable=False)
    availability = Column(JSON)

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    student1 = Column(String(50), nullable=False)
    student2 = Column(String(50), nullable=False)
    datetime = Column(DateTime, nullable=False)  # ✅ Correct type and not null

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    reviewer = Column(String(50), nullable=False)
    reviewee = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    feedback = Column(Text)
