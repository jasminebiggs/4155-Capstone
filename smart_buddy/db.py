from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DB connection config
class conf:
    db_user = "root"
    db_password = "Siraulo76!"
    db_host = "localhost"
    db_name = "smart_buddy_api"
    db_port = 3306

# MySQL connection string
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Siraulo76!@localhost:3306/smart_buddy_api"

# SQLAlchemy engine & session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base model
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
