from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.resources import Resource as ResourceModel
from ..schemas.resources import ResourceCreate, ResourceUpdate

def get_all(db: Session):
    return db.query(ResourceModel).all()

def get_one(db: Session, resource_id: int):
    resource = db.query(ResourceModel).filter(ResourceModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

def create(db: Session, resource: ResourceCreate):
    new_resource = ResourceModel(**resource.model_dump())
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

def update(db: Session, resource_id: int, updates: ResourceUpdate):
    resource = db.query(ResourceModel).filter(ResourceModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)
    db.commit()
    db.refresh(resource)
    return resource

def delete(db: Session, resource_id: int):
    resource = db.query(ResourceModel).filter(ResourceModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted"}
