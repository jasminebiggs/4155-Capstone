from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import promotions as model
from ..schemas import promotions as schema

# Create a new Promotion
def create(db: Session, promotion: schema.PromotionCreate):
    db_promotion = model.Promotion(
        code=promotion.code,
        expiration_date=promotion.expiration_date
    )
    db.add(db_promotion)
    db.commit()
    db.refresh(db_promotion)
    return db_promotion

# Read all Promotions
def read_all(db: Session):
    return db.query(model.Promotion).all()

# Read a single Promotion by ID
def read_one(db: Session, promotion_id: int):
    promotion = db.query(model.Promotion).filter(model.Promotion.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion

# Update a Promotion
def update(db: Session, promotion_id: int, promotion_update: schema.PromotionUpdate):
    db_promotion = db.query(model.Promotion).filter(model.Promotion.id == promotion_id)
    if not db_promotion.first():
        raise HTTPException(status_code=404, detail="Promotion not found")

    update_data = promotion_update.model_dump(exclude_unset=True)
    db_promotion.update(update_data, synchronize_session=False)
    db.commit()
    return db_promotion.first()

# Delete a Promotion
def delete(db: Session, promotion_id: int):
    db_promotion = db.query(model.Promotion).filter(model.Promotion.id == promotion_id)
    if not db_promotion.first():
        raise HTTPException(status_code=404, detail="Promotion not found")

    db_promotion.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
