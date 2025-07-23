# init_db.py

# This script initializes the database by creating all necessary tables.
# It should be run once before starting the application for the first time,
# or whenever the database schema changes.

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_buddy.db import engine
from smart_buddy.models.sqlalchemy_models import Base

print("Creating database tables...")
# The models are already imported and registered with Base in sqlalchemy_models.py
Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")
