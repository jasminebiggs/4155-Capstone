from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from smart_buddy.db import Base

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    personality_type = Column(String(50))
    study_style = Column(String(50))
    environment = Column(String(50))
    focus_area = Column(String(100))