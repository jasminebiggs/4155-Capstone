from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import orders as model, order_details, recipes, sandwiches, resources
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from sqlalchemy import func

def create(db: Session, request):
    sandwich_ids = [detail.sandwich_id for detail in request.order_details]
    quantities = {detail.sandwich_id: detail.quantity for detail in request.order_details}

    for sandwich_id in sandwich_ids:
        linked_recipes = db.query(recipes.Recipe).filter(recipes.Recipe.sandwich_id == sandwich_id).all()
        for recipe in linked_recipes:
            resource = db.query(resources.Resource).filter(resources.Resource.id == recipe.resource_id).first()
            if resource.amount < quantities[sandwich_id]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient {resource.item} for sandwich ID {sandwich_id}"
                )

    new_item = model.Order(
        customer_name=request.customer_name,
        order_date=request.order_date,
        description=request.description,
        tracking_number=request.tracking_number,
        total_price=request.total_price,
        delivery_type=request.delivery_type
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        for detail in request.order_details:
            new_detail = order_details.OrderDetail(
                order_id=new_item.id,
                sandwich_id=detail.sandwich_id,
                quantity=detail.quantity
            )
            db.add(new_detail)

            # Deduct resource quantities
            linked_recipes = db.query(recipes.Recipe).filter(recipes.Recipe.sandwich_id == detail.sandwich_id).all()
            for recipe in linked_recipes:
                resource = db.query(resources.Resource).filter(resources.Resource.id == recipe.resource_id).first()
                resource.amount -= detail.quantity

            # Increment popularity
            sandwich = db.query(sandwiches.Sandwich).filter(sandwiches.Sandwich.id == detail.sandwich_id).first()
            sandwich.popularity += detail.quantity

        db.commit()

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.Order).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_by_tracking_number(db: Session, tracking_number: str):
    order = db.query(model.Order).filter(model.Order.tracking_number == tracking_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found with that tracking number")
    return order


def get_by_date_range(db: Session, start_date: date, end_date: date):
    return db.query(model.Order).filter(
        func.date(model.Order.order_date) >= start_date,
        func.date(model.Order.order_date) <= end_date
    ).all()


def get_total_revenue(db: Session, date: date):
    orders = db.query(model.Order).filter(func.date(model.Order.order_date) == date).all()
    total = sum(float(order.total_price) for order in orders)
    return {"date": date, "total_revenue": total}
