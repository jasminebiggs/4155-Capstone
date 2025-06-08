from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Sandwich(Base):
    __tablename__ = "sandwiches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sandwich_name = Column(String(100), unique=True, nullable=True)
    price = Column(DECIMAL(4, 2), nullable=False, server_default='0.0')
    category = Column(String(50), nullable=True)
    popularity = Column(Integer, default=0)  # New field

    recipes = relationship("Recipe", back_populates="sandwich")
    order_details = relationship("OrderDetail", back_populates="sandwich")
    ratings = relationship("Rating", back_populates="sandwich")
    customer = relationship("Customers", back_populates="sandwich")
