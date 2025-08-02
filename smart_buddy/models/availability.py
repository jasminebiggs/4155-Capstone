from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from smart_buddy.db import Base

class Availability(Base):
    __tablename__ = "availability"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Availability type: "one-time", "recurring", "block"
    availability_type = Column(String(20), nullable=False)
    
    # For specific dates
    date = Column(Date, nullable=True)
    
    # For recurring availability
    day_of_week = Column(Integer, nullable=True)  # 0=Monday, 6=Sunday
    
    # Time slots
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationship back to user
    user = relationship("UserProfile", back_populates="availability")