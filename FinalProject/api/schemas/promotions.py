from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class PromotionBase(BaseModel):
    code: str
    expiration_date: date

class PromotionCreate(PromotionBase):
    pass

class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    expiration_date: Optional[date] = None

class Promotion(PromotionBase):
    id: int

    class Config:
        from_attributes = True
