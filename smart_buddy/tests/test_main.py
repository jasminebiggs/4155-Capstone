from fastapi.testclient import TestClient
from smart_buddy.main import app
from smart_buddy import main

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SMART BUDDY environment setup successful!"}

def test_get_user_name_mock(mocker):
    mock_func = mocker.patch("smart_buddy.main.get_user_name", return_value="Mocked Adam Pang")
    assert main.get_user_name() == "Mocked Adam Pang"
    mock_func.assert_called_once()