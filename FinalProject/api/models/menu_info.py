from sqlalchemy import Column, String, Integer, DateTime,Float
from sqlalchemy.sql import func

from ..dependencies.database import Base

class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dish_name = Column(String, nullable=False)
    ingredients = Column(String, nullable=False)  # Can store as a comma-separated string or use a separate table
    price = Column(Float, nullable=False)
    calories = Column(Integer, nullable=False)
    food_category = Column(String, nullable=False)  # e.g., "appetizer", "main_course"

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())