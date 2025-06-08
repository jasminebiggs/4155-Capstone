from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import models  # Adjust this based on your folder structure
from ..schemas import customers as customer_schema

def create(db: Session, customer: customer_schema.CustomerCreate):
    db_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
        address=customer.address
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def read_all(db: Session):
    return db.query(models.Customer).all()

def read_one(db: Session, customer_id: int):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

def update(db: Session, customer_id: int, customer: customer_schema.CustomerUpdate):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id)
    if db_customer.first() is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_data = customer.model_dump(exclude_unset=True)
    db_customer.update(update_data, synchronize_session=False)
    db.commit()
    return db_customer.first()

def delete(db: Session, customer_id: int):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id)
    if db_customer.first() is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db_customer.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
