import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "3306")
db   = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist
def create_tables():
    from smart_buddy.models.sqlalchemy_models import Profile, Session, Rating
    Base.metadata.create_all(bind=engine)

# Initialize database on import
# create_tables() # It is not recommended to run create_tables() on every import. 
# Consider using a migration tool like Alembic to manage your database schema.