from sqlalchemy import Column, String, Integer, ForeignKey
from typing import Optional

from sqlalchemy.orm import relationship

from ..dependencies.database import Base

class Customers(Base):
    __tablename__ = "customers"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(50), index=True)
    email: str = Column(String(25), index=True)
    phone_number: str = Column(String(10), index=True)
    address: str = Column(String(50), index=True)

    ratings = relationship("Rating", back_populates="customer")
    orders = relationship("Order", back_populates="customer")