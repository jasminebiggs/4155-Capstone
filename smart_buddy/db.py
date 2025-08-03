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

# Default MySQL connection string
DEFAULT_MYSQL_URL = "mysql+pymysql://root:Siraulo76!@localhost:3306/smart_buddy"

# Check for a DATABASE_URL environment variable, common on hosting platforms
if os.getenv("DATABASE_URL"):
    print("DATABASE_URL found, configuring for PostgreSQL (Render/Production).")
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Heroku and other platforms use "postgres://", but SQLAlchemy needs "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # If environment variables are set, use them
    if all([os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"), os.getenv("DB_NAME")]):
        print("Database environment variables found, using them for MySQL connection.")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "3306")  # Default MySQL port
        db_name = os.getenv("DB_NAME")
        
        # Construct the database URL from environment variables
        DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # If no environment variables, use the default connection string
        print("No database environment variables found, using default MySQL connection.")
        DATABASE_URL = DEFAULT_MYSQL_URL

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
