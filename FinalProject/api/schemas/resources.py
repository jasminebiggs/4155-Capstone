from pydantic import BaseModel
from typing import Optional

class ResourceBase(BaseModel):
    item: str
    amount: float
    unit: str

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    item: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None

class Resource(ResourceBase):
    id: int

    class Config:
        from_attributes = True
