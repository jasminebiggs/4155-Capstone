import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Database Configuration ---

# Detect if the application is running on Render
is_render = "RENDER" in os.environ

# This will hold the final database connection URL
DATABASE_URL = None

# Check for a DATABASE_URL environment variable (common on hosting platforms like Render)
if os.getenv("DATABASE_URL"):
    print("DATABASE_URL found, configuring for PostgreSQL (Render/Production).")
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Some platforms use "postgres://" but SQLAlchemy needs "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # For local development using MySQL
    print("No DATABASE_URL found, configuring for local MySQL development.")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "smart_buddy")
    
    # Construct the database URL for a local MySQL instance
    DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# --- SQLAlchemy Engine Setup ---

try:
    # Create the SQLAlchemy engine
    engine = create_engine(DATABASE_URL)
    
    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a Base class for declarative models
    Base = declarative_base()
    
    # Test the database connection
    with engine.connect() as connection:
        print("Database connection established successfully!")

except Exception as e:
    print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
    if is_render:
        print("Hint: Ensure the DATABASE_URL environment variable is correctly set in your Render environment.", file=sys.stderr)
    else:
        print("Hint: Check that your local MySQL server is running and the environment variables are set correctly.", file=sys.stderr)
    raise

def get_db():
    """
    Dependency function to get a database session for each request.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Table Creation ---
def create_tables():
    """Create all database tables defined by models inheriting from Base."""
    try:
        # Import models to ensure they're registered with the Base
        from smart_buddy.sqlalchemy_models import Profile, Session, Rating
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created successfully.")
    except Exception as e:
        print(f"ERROR: Failed to create database tables: {e}", file=sys.stderr)
        raise

# Initialize the database by creating tables
create_tables()
