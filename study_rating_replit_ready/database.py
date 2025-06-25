# database.py
# completed on June 22

from databases import Database
import sqlalchemy

DATABASE_URL = "postgresql://user:password@localhost:5432/mydb"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

ratings = sqlalchemy.Table(
    "ratings",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("session_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("reviewer_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("partner_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("rating", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("feedback", sqlalchemy.Text),
    sqlalchemy.Column("created_at", sqlalchemy.TIMESTAMP, server_default=sqlalchemy.text("CURRENT_TIMESTAMP")),
    sqlalchemy.UniqueConstraint("session_id", "reviewer_id")
)
