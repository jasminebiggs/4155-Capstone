# Ticket 4: Implement the sessions table to store scheduled study sessions.
# This table includes information about student and partner IDs, as well as session start and end times.

# Ticket 5: Implement the ratings table to allow students to rate and provide feedback on their study sessions.
# The table includes fields for session reference, reviewer, partner, rating score, and optional text feedback.


import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime
from databases import Database

DATABASE_URL = "postgresql://postgres:postgres@localhost/studybuddy"
database = Database(DATABASE_URL)
metadata = MetaData()

sessions = Table(
    "sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", Integer),
    Column("partner_id", Integer),
    Column("start_time", DateTime),
    Column("end_time", DateTime)
)

ratings = Table(
    "ratings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", Integer),
    Column("reviewer_id", Integer),
    Column("partner_id", Integer),
    Column("rating", Integer),
    Column("feedback", String)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
