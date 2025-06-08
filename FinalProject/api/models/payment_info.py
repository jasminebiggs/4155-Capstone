from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..dependencies.database import Base

class PaymentInformation(Base):
    __tablename__ = 'payment_information'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_information = Column(String, nullable=False)  # Typically encrypted
    transaction_status = Column(String, nullable=False)  # e.g., "completed"
    payment_type = Column(String, nullable=False)  # e.g., "credit_card"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    payment_details = relationship("PaymentDetails", backref="payment_information")