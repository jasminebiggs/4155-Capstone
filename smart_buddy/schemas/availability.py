from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional, List
from enum import Enum

class AvailabilityType(str, Enum):
    ONE_TIME = "one-time"
    RECURRING = "recurring"
    BLOCK = "block"

class AvailabilityCreate(BaseModel):
    availability_type: AvailabilityType
    date: Optional[date] = None  # Required for one-time
    day_of_week: Optional[int] = None  # Required for recurring (0-6)
    start_time: time
    end_time: time
    
    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if v is not None and not (0 <= v <= 6):
            raise ValueError('day_of_week must be between 0 (Monday) and 6 (Sunday)')
        return v
    
    @validator('end_time')
    def validate_time_order(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
    
    @validator('date')
    def validate_date_for_type(cls, v, values):
        if values.get('availability_type') == 'one-time' and v is None:
            raise ValueError('date is required for one-time availability')
        return v
    
    @validator('day_of_week')
    def validate_day_for_type(cls, v, values):
        if values.get('availability_type') == 'recurring' and v is None:
            raise ValueError('day_of_week is required for recurring availability')
        return v
    
    
class AvailabilityResponse(BaseModel):
    id: int
    user_id: int
    availability_type: str
    date: Optional[date] = None
    day_of_week: Optional[int] = None
    start_time: time
    end_time: time
    is_active: bool
    
    class Config:
        from_attributes = True

class AvailabilityBulkCreate(BaseModel):
    """For creating multiple availability slots at once"""
    slots: List[AvailabilityCreate]