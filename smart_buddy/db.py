import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Database Configuration ---

# Detect if the application is running on a platform like Render
is_render = "RENDER" in os.environ

# This will hold the final database connection URL
DATABASE_URL = None

# Check for a DATABASE_URL environment variable, common on hosting platforms
# If it exists, we assume it's for a PostgreSQL database (as per the original logic)
if os.getenv("DATABASE_URL"):
    print("DATABASE_URL found, configuring for PostgreSQL (Render/Production).")
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Heroku and other platforms use "postgres://", but SQLAlchemy needs "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # If no DATABASE_URL, configure for a local MySQL database
    print("No DATABASE_URL found, configuring for local MySQL development.")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "3306")  # Default MySQL port
    db_name = os.getenv("DB_NAME")

    # Ensure all required environment variables are set for a local connection
    if not all([db_user, db_password, db_host, db_name]):
        error_msg = (
            "Database connection failed. For local MySQL development, please set all "
            "required environment variables: DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME."
        )
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise ValueError(error_msg)
    
    # Construct the database URL for a local MySQL instance
    # Requires a driver like PyMySQL, hence 'mysql+pymysql'
    DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# --- SQLAlchemy Engine Setup ---

try:
    # Create the SQLAlchemy engine using the determined URL
    engine = create_engine(DATABASE_URL)

    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create a Base class for declarative models
    Base = declarative_base()

    # Test the database connection to ensure it's working
    with engine.connect() as connection:
        print("Database connection established successfully!")

except Exception as e:
    print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
    if is_render:
        print("Hint: Ensure the DATABASE_URL environment variable is correctly set in your deployment environment.", file=sys.stderr)
    else:
        print("Hint: Check that your local MySQL server is running, PyMySQL is installed (`pip install pymysql`), and the .env file has the correct credentials.", file=sys.stderr)
    raise

# --- Database Session Dependency ---

def get_db():
    """
    Dependency function to get a database session for each request.
    Ensures the session is always closed after the request.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# --- Table Creation ---

def create_tables():
    """
    Create all database tables defined by models inheriting from Base.
    """
    try:
        # It's good practice to import models here to avoid circular dependency issues.
        # from smart_buddy.models.sqlalchemy_models import Profile, Session, Rating
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created successfully.")
    except Exception as e:
        print(f"ERROR: Failed to create database tables: {e}", file=sys.stderr)
        raise

# Initialize the database by creating tables when the application starts
create_tables()