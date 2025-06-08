from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import models  # adjust the import if needed
from ..schemas import menu_items as menu_schema

def create(db: Session, menu_item: menu_schema.MenuItemCreate):
    db_menu_item = models.MenuItem(
        dish_name=menu_item.dish_name,
        ingredients=menu_item.ingredients,
        price=menu_item.price,
        calories=menu_item.calories,
        food_category=menu_item.food_category
    )
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

def read_all(db: Session):
    return db.query(models.MenuItem).all()

def read_one(db: Session, menu_item_id: int):
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu Item not found")
    return menu_item

def update(db: Session, menu_item_id: int, menu_item: menu_schema.MenuItemUpdate):
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id)
    if db_menu_item.first() is None:
        raise HTTPException(status_code=404, detail="Menu Item not found")
    update_data = menu_item.model_dump(exclude_unset=True)
    db_menu_item.update(update_data, synchronize_session=False)
    db.commit()
    return db_menu_item.first()

def delete(db: Session, menu_item_id: int):
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id)
    if db_menu_item.first() is None:
        raise HTTPException(status_code=404, detail="Menu Item not found")
    db_menu_item.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
