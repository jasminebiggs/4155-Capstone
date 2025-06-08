from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import models
from ..schemas import payment_information as payment_schema

def create(db: Session, payment_info: payment_schema.PaymentInformationCreate):
    db_payment_info = models.PaymentInformation(
        card_information=payment_info.card_information,
        transaction_status=payment_info.transaction_status,
        payment_type=payment_info.payment_type
    )
    db.add(db_payment_info)
    db.commit()
    db.refresh(db_payment_info)
    return db_payment_info

def read_all(db: Session):
    return db.query(models.PaymentInformation).all()

def read_one(db: Session, payment_info_id: int):
    payment_info = db.query(models.PaymentInformation).filter(models.PaymentInformation.id == payment_info_id).first()
    if payment_info is None:
        raise HTTPException(status_code=404, detail="Payment Information not found")
    return payment_info

def update(db: Session, payment_info_id: int, payment_info: payment_schema.PaymentInformationUpdate):
    db_payment_info = db.query(models.PaymentInformation).filter(models.PaymentInformation.id == payment_info_id)
    if db_payment_info.first() is None:
        raise HTTPException(status_code=404, detail="Payment Information not found")
    update_data = payment_info.model_dump(exclude_unset=True)
    db_payment_info.update(update_data, synchronize_session=False)
    db.commit()
    return db_payment_info.first()

def delete(db: Session, payment_info_id: int):
    db_payment_info = db.query(models.PaymentInformation).filter(models.PaymentInformation.id == payment_info_id)
    if db_payment_info.first() is None:
        raise HTTPException(status_code=404, detail="Payment Information not found")
    db_payment_info.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

