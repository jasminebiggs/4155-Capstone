# test/test_rating.py
# Additional test for Ticket 5

import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.anyio
async def test_submit_rating():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/rate", json={
            "session_id": 1,
            "reviewer_id": 2,
            "partner_id": 3,
            "rating": 5,
            "feedback": "Awesome study buddy"
        })
        assert response.status_code == 200
        assert response.json() == {"message": "Rating submitted"}
