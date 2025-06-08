from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_all_sandwiches():
    response = client.get("/sandwiches/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order_by_tracking_number():
    response = client.get("/orders/track/TRK12345")
    assert response.status_code == 200
    assert "tracking_number" in response.json()
