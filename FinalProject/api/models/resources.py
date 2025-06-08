from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from api.dependencies.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item = Column(String(100), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)

    recipes = relationship("Recipe", back_populates="resource")
