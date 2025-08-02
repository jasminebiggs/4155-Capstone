# Ticket 4: Implement the session scheduling endpoint.
# Adds an API route to schedule study sessions, storing session details like student, partner, start time, and end time.

# Ticket 5: Integrates the rating system from the separate `ratings.py` route.
# The rating logic is defined in the `routes/ratings.py` file and included here via FastAPI router.


from fastapi import FastAPI
from pydantic import BaseModel
from database import database, sessions
from routes.ratings import router as ratings_router, RatingInput, rate_partner

app = FastAPI()
app.include_router(ratings_router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ticket4 - Session scheduling
class SessionCreate(BaseModel):
    student_id: int
    partner_id: int
    start_time: str
    end_time: str

@app.post("/sessions/schedule", status_code=201)
async def schedule_session(session: SessionCreate):
    query = sessions.insert().values(
        student_id=session.student_id,
        partner_id=session.partner_id,
        start_time=session.start_time,
        end_time=session.end_time
    )
    await database.execute(query)
    return {"message": "Session scheduled successfully"}
