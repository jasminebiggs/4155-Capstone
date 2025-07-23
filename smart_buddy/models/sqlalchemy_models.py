from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from smart_buddy.db import Base

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True)  # Increased length for emails
    username = Column(String(100), unique=True, index=True, nullable=False)  # Increased length
    study_style = Column(String(100))
    preferred_environment = Column(String(100))
    personality_traits = Column(JSON)
    academic_focus_areas = Column(JSON)
    password = Column(String(255), nullable=False)  # Increased for hashed passwords
    availability = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student1 = Column(String(100), nullable=False)
    student2 = Column(String(100), nullable=False)
    datetime = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default='scheduled')  # scheduled, completed, cancelled

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reviewer = Column(String(100), nullable=False)
    reviewee = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
