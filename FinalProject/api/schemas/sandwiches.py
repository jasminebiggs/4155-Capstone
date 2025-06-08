from pydantic import BaseModel
from typing import Optional


class SandwichBase(BaseModel):
    sandwich_name: str
    price: float
    category: Optional[str] = None  # new field

class SandwichCreate(SandwichBase):
    pass

class SandwichUpdate(BaseModel):
    sandwich_name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None  # new field

class Sandwich(SandwichBase):
    id: int

    class Config:
        from_attributes = True
