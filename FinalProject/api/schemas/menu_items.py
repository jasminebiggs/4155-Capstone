from typing import List
from pydantic import BaseModel
from datetime import DATETIME

class MenuItem(BaseModel):
    dish_name: str
    ingredients: List[str]  # List of ingredients for the dish
    price: float
    calories: int
    food_category: str  # e.g., "appetizer", "main_course", "dessert"

class MenuItemCreate(BaseModel):
    dish_name: str
    ingredients: List[str]
    price: float
    calories: int
    food_category: str

class MenuItemUpdate(BaseModel):
    price: Optional[float] = None
    calories: Optional[int] = None
    food_category: Optional[str] = None

class MenuItemRead(BaseModel):
    id: int
    dish_name: str
    ingredients: List[str]
    price: float
    calories: int
    food_category: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True