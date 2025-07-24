import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Render and other platforms often provide a single DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to individual components if DATABASE_URL is not set (for local development).
if not DATABASE_URL:
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432") # Default PostgreSQL port
    db_name = os.getenv("DB_NAME")

    # Check that all required environment variables are set.
    if not all([user, password, host, db_name]):
        raise ValueError(
            "Database connection failed. For local development, please set all of "
            "DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME environment variables."
        )

    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

# SQLAlchemy 1.x and 2.x have different behaviors with postgresql:// URLs.
# Replacing "postgresql://" with "postgresql+psycopg2://" is a safe way
# to ensure compatibility.
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Create tables if they don't exist
def create_tables():
    from smart_buddy.models.sqlalchemy_models import Profile, Session, Rating
    Base.metadata.create_all(bind=engine)

# Initialize database on import
# create_tables() # It is not recommended to run create_tables() on every import. 
# Consider using a migration tool like Alembic to manage your database schema.