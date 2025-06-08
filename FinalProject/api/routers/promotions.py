from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..schemas import promotions as schema
from ..controllers import promotions as controller
from ..dependencies.database import get_db

router = APIRouter(prefix="/promotions", tags=["Promotions"])

@router.get("/", response_model=list[schema.Promotion])
def read_all_promos(db: Session = Depends(get_db)):
    return controller.get_all(db)

@router.get("/{promo_id}", response_model=schema.Promotion)
def read_one_promo(promo_id: int, db: Session = Depends(get_db)):
    return controller.get_one(db, promo_id)

@router.post("/", response_model=schema.Promotion, status_code=status.HTTP_201_CREATED)
def create_promo(promo: schema.PromotionCreate, db: Session = Depends(get_db)):
    return controller.create(db, promo)

@router.put("/{promo_id}", response_model=schema.Promotion)
def update_promo(promo_id: int, updates: schema.PromotionUpdate, db: Session = Depends(get_db)):
    return controller.update(db, promo_id, updates)

@router.delete("/{promo_id}")
def delete_promo(promo_id: int, db: Session = Depends(get_db)):
    return controller.delete(db, promo_id)
