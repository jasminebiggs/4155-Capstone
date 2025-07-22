from sqlalchemy import Column, Integer, String, Text, JSON
from smart_buddy.db import Base

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True)
    study_style = Column(String(50))
    preferred_environment = Column(String(50))  # ADDED
    personality_traits = Column(JSON)           # ADDED
    academic_focus_areas = Column(JSON)         # ADDED
    password = Column(String(100), nullable=False)
    availability = Column(JSON)

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, index=True)
    student1 = Column(String(50))
    student2 = Column(String(50))
    datetime = Column(String(50))

class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, index=True)
    reviewer = Column(String(50))
    reviewee = Column(String(50))
    score = Column(Integer)
    feedback = Column(Text)
