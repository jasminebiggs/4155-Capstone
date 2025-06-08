from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..schemas import resources as schema
from ..controllers import resources as controller
from ..dependencies.database import get_db

router = APIRouter(prefix="/resources", tags=["Resources"])

@router.get("/", response_model=list[schema.Resource])
def read_all_resources(db: Session = Depends(get_db)):
    return controller.get_all(db)

@router.get("/{resource_id}", response_model=schema.Resource)
def read_one_resource(resource_id: int, db: Session = Depends(get_db)):
    return controller.get_one(db, resource_id)

@router.post("/", response_model=schema.Resource, status_code=status.HTTP_201_CREATED)
def create_resource(resource: schema.ResourceCreate, db: Session = Depends(get_db)):
    return controller.create(db, resource)

@router.put("/{resource_id}", response_model=schema.Resource)
def update_resource(resource_id: int, updates: schema.ResourceUpdate, db: Session = Depends(get_db)):
    return controller.update(db, resource_id, updates)

@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    return controller.delete(db, resource_id)
