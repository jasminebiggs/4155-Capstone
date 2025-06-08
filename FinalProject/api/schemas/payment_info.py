from datetime import DATETIME
from typing import Optional
from pydantic import BaseModel


class PaymentInformation(BaseModel):
    card_information: str  # This would typically be encrypted or tokenized
    transaction_status: str  # e.g., "completed", "pending", "failed"
    payment_type: str  # e.g., "credit_card", "paypal", "bank_transfer"

class PaymentInformationCreate(BaseModel):
    card_information: str
    transaction_status: str
    payment_type: str

class PaymentInformationUpdate(BaseModel):
    transaction_status: Optional[str] = None
    payment_type: Optional[str] = None

class PaymentInformationRead(BaseModel):
    id: int
    card_information: str
    transaction_status: str
    payment_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True