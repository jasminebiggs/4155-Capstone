import pytest
import sqlalchemy
from datetime import datetime
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from database import database
from main import app

@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    await database.connect()
    yield
    await database.disconnect()

# ticket4 - Test session scheduling - test case
@pytest.mark.anyio
async def test_schedule_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/sessions/schedule", json={
            "student_id": 1,
            "partner_id": 2,
            "start_time": "2025-07-23T10:00:00",
            "end_time": "2025-07-23T11:00:00"
        })

    assert response.status_code == 201
    assert response.json() == {"message": "Session scheduled successfully"}

# ticket5 - Test rating submission
@pytest.mark.anyio
async def test_submit_rating():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/rate", json={
            "session_id": 1,
            "reviewer_id": 1,
            "partner_id": 2,
            "rating": 5,
            "feedback": "Great session!"
        })

    assert response.status_code == 200
    assert response.json() == {"message": "Rating submitted"}
