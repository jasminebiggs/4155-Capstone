from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..schemas import sandwiches as schema
from ..models import sandwiches as model
from ..dependencies.database import get_db
from fastapi import HTTPException

router = APIRouter(prefix="/sandwiches", tags=["Sandwiches"])

@router.get("/", response_model=list[schema.Sandwich])
def read_all(db: Session = Depends(get_db)):
    return db.query(model.Sandwich).all()

@router.get("/{sandwich_id}", response_model=schema.Sandwich)
def read_one(sandwich_id: int, db: Session = Depends(get_db)):
    sandwich = db.query(model.Sandwich).filter(model.Sandwich.id == sandwich_id).first()
    if not sandwich:
        raise HTTPException(status_code=404, detail="Sandwich not found")
    return sandwich

@router.post("/", response_model=schema.Sandwich, status_code=status.HTTP_201_CREATED)
def create(sandwich: schema.SandwichCreate, db: Session = Depends(get_db)):
    new_item = model.Sandwich(**sandwich.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/{sandwich_id}", response_model=schema.Sandwich)
def update(sandwich_id: int, updates: schema.SandwichUpdate, db: Session = Depends(get_db)):
    sandwich = db.query(model.Sandwich).filter(model.Sandwich.id == sandwich_id).first()
    if not sandwich:
        raise HTTPException(status_code=404, detail="Sandwich not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(sandwich, key, value)
    db.commit()
    db.refresh(sandwich)
    return sandwich

@router.delete("/{sandwich_id}")
def delete(sandwich_id: int, db: Session = Depends(get_db)):
    sandwich = db.query(model.Sandwich).filter(model.Sandwich.id == sandwich_id).first()
    if not sandwich:
        raise HTTPException(status_code=404, detail="Sandwich not found")
    db.delete(sandwich)
    db.commit()
    return {"message": "Sandwich deleted"}

@router.get("/category/{category}", response_model=list[schema.Sandwich])
def get_by_category(category: str, db: Session = Depends(get_db)):
    return db.query(model.Sandwich).filter(model.Sandwich.category.ilike(f"%{category}%")).all()

@router.get("/popular", response_model=list[schema.Sandwich])
def get_popular_sandwiches(db: Session = Depends(get_db)):
    return db.query(model.Sandwich).order_by(model.Sandwich.popularity.desc()).limit(5).all()
