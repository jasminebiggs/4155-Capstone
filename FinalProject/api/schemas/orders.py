from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class OrderDetailInput(BaseModel):
    sandwich_id: int
    quantity: int


class OrderBase(BaseModel):
    customer_name: str
    description: Optional[str] = None
    tracking_number: str
    total_price: float
    delivery_type: str
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None


class OrderCreate(OrderBase):
    order_date: Optional[datetime] = None
    order_details: List[OrderDetailInput]


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    description: Optional[str] = None
    tracking_number: Optional[str] = None
    total_price: Optional[float] = None
    delivery_type: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None


class Order(OrderBase):
    id: int
    order_date: datetime

    class Config:
        from_attributes = True
