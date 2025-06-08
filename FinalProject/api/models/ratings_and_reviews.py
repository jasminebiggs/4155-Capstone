from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from ..dependencies.database import Base

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    sandwich_id = Column(Integer, ForeignKey('sandwiches.id'), nullable=False)
    review_text = Column(String(250))
    rating_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship('Customers', back_populates='ratings')
    sandwich = relationship('Sandwich', back_populates='ratings')