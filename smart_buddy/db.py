import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect if running on Render
is_render = "RENDER" in os.environ

# Render and other platforms often provide a single DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL") 
print(f"Initial DATABASE_URL: {DATABASE_URL}")

# Handle postgres:// URL format (Render uses this)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"Converted postgres:// to postgresql:// URL: {DATABASE_URL}")

# Fallback to individual components if DATABASE_URL is not set (for local development)
if not DATABASE_URL:
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")  # Default PostgreSQL port
    db_name = os.getenv("DB_NAME")

    # Check that all required environment variables are set
    if not all([user, password, host, db_name]):
        error_msg = (
            "Database connection failed. For local development, please set all of "
            "DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME environment variables."
        )
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise ValueError(error_msg)

    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

# SQLAlchemy 1.x and 2.x have different behaviors with postgresql:// URLs
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

print(f"Connecting to database with URL: {DATABASE_URL.split('@')[0]}@[HIDDEN]")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Test connection
    with engine.connect() as connection:
        print("Database connection successful!")
except Exception as e:
    if is_render:
        print(f"ERROR: Database connection failed on Render: {e}", file=sys.stderr)
        print("Make sure the DATABASE_URL environment variable is correctly set in Render dashboard.")
    else:
        print(f"ERROR: Database connection failed locally: {e}", file=sys.stderr)
        print("Check that PostgreSQL is running and your .env file has correct credentials.")
    raise

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Create tables if they don't exist 
def create_tables():
    try:
        from smart_buddy.models.sqlalchemy_models import Profile, Session, Rating
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"ERROR: Failed to create database tables: {e}", file=sys.stderr)
        raise

# Initialize database on import
create_tables()
