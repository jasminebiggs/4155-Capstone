from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(100))
    order_date = Column(DATETIME, nullable=False, server_default=str(datetime.now()))
    description = Column(String(300))

    tracking_number = Column(String(100), nullable=True, unique=True)
    total_price = Column(DECIMAL(10, 2), nullable=True)
    delivery_type = Column(String(50), nullable=True)

    payment_method = Column(String(50), nullable=True)   # New
    payment_status = Column(String(50), nullable=True)   # New

    customer = relationship("Customer", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")
