from sqlalchemy.orm import Session
from api.dependencies.database import SessionLocal
from api.models import customers, sandwiches, resources, recipes, orders, order_details, promotions, ratings_and_reviews
from datetime import datetime, timedelta

db: Session = SessionLocal()

def seed():
    db.query(ratings_and_reviews.Rating).delete()
    db.query(order_details.OrderDetail).delete()
    db.query(orders.Order).delete()
    db.query(recipes.Recipe).delete()
    db.query(resources.Resource).delete()
    db.query(sandwiches.Sandwich).delete()
    db.query(customers.Customer).delete()
    db.query(promotions.Promotion).delete()

    customer1 = customers.Customer(name="Alex Smith", phone="555-1234", address="123 Main St")
    customer2 = customers.Customer(name="Jamie Doe", phone="555-5678", address="456 Oak Ave")

    sandwich1 = sandwiches.Sandwich(sandwich_name="Veggie Delight", price=5.99, category="vegetarian")
    sandwich2 = sandwiches.Sandwich(sandwich_name="Spicy Chicken", price=7.49, category="spicy")
    sandwich3 = sandwiches.Sandwich(sandwich_name="Kid's Ham", price=4.99, category="kids")

    resource1 = resources.Resource(item="Lettuce", amount=100, unit="grams")
    resource2 = resources.Resource(item="Chicken Breast", amount=50, unit="pieces")
    resource3 = resources.Resource(item="Ham", amount=30, unit="pieces")

    recipe1 = recipes.Recipe(sandwich=sandwich1, resource=resource1)
    recipe2 = recipes.Recipe(sandwich=sandwich2, resource=resource2)
    recipe3 = recipes.Recipe(sandwich=sandwich3, resource=resource3)

    order1 = orders.Order(
        customer_name="Alex Smith",
        order_date=datetime.utcnow() - timedelta(days=1),
        description="Delivery order",
        tracking_number="TRK12345",
        total_price=13.48,
        delivery_type="delivery"
    )
    order2 = orders.Order(
        customer_name="Jamie Doe",
        order_date=datetime.utcnow(),
        description="Takeout",
        tracking_number="TRK67890",
        total_price=4.99,
        delivery_type="takeout"
    )

    detail1 = order_details.OrderDetail(order=order1, sandwich=sandwich1, quantity=1)
    detail2 = order_details.OrderDetail(order=order1, sandwich=sandwich2, quantity=1)
    detail3 = order_details.OrderDetail(order=order2, sandwich=sandwich3, quantity=1)

    promo = promotions.Promotion(code="SAVE10", expiration_date=datetime.utcnow() + timedelta(days=10))

    review = ratings_and_reviews.Rating(
        customer_name="Alex Smith",
        sandwich=sandwich2,
        rating_score=4,
        review_text="Great sandwich!"
    )

    db.add_all([
        customer1, customer2,
        sandwich1, sandwich2, sandwich3,
        resource1, resource2, resource3,
        recipe1, recipe2, recipe3,
        order1, order2,
        detail1, detail2, detail3,
        promo,
        review
    ])
    db.commit()
    print("✅ Seed data inserted.")

if __name__ == "__main__":
    seed()
