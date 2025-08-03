from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    created_at = Column(DateTime, default=func.now())

# Add Profile class required by the application
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

# Add Session class required by the application
class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    student1 = Column(String(50), nullable=False)
    student2 = Column(String(50), nullable=False)
    datetime = Column(DateTime, nullable=False)

# Add Rating class required by the application
class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    reviewer = Column(String(50), nullable=False)
    reviewee = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    feedback = Column(Text)

