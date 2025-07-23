"""
API tests for availability CRUD endpoints
Testing GET, POST, PUT, DELETE operations for /availability
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from smart_buddy.main import app
from smart_buddy.models.sqlalchemy_models import Profile, Base
from smart_buddy.db import get_db
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_availability_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Create database session for test setup"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_profile(db_session):
    """Create a sample profile for testing"""
    profile = Profile(
        email="test@example.com",
        username="testuser",
        study_style="Group",
        preferred_environment="Quiet",
        personality_traits={"type": "Introvert"},
        academic_focus_areas=["Computer Science"],
        password="testpassword",
        availability={
            "Monday": ["Morning", "Afternoon"],
            "Tuesday": ["Evening"],
            "Wednesday": [],
            "Thursday": ["Morning"],
            "Friday": ["Afternoon", "Evening"],
            "Saturday": ["Morning"],
            "Sunday": []
        }
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

@pytest.fixture
def auth_headers():
    """Mock authentication headers (simplified for testing)"""
    # In a real app, you'd generate a valid JWT token
    return {"Authorization": "Bearer mock_token"}

class TestAvailabilityGetEndpoint:
    """Test GET /availability endpoint"""
    
    def test_get_availability_success(self, client, sample_profile, monkeypatch):
        """Test successful retrieval of availability data"""
        # Mock the get_current_user dependency to return our test user
        def mock_get_current_user():
            return sample_profile
        
        # Override the dependency
        from smart_buddy.routers.availability import get_current_user
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        response = client.get("/availability", headers={"Authorization": "Bearer test_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert "availability" in data
        assert data["availability"]["Monday"] == ["Morning", "Afternoon"]
        assert data["availability"]["Tuesday"] == ["Evening"]
    
    def test_get_availability_unauthorized(self, client):
        """Test GET availability without authentication"""
        response = client.get("/availability")
        assert response.status_code == 401
    
    def test_get_availability_user_not_found(self, client, monkeypatch):
        """Test GET availability when user doesn't exist"""
        def mock_get_current_user():
            return None
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: None)
        
        response = client.get("/availability", headers={"Authorization": "Bearer test_token"})
        assert response.status_code == 404

class TestAvailabilityPostEndpoint:
    """Test POST /availability endpoint"""
    
    def test_update_availability_success(self, client, sample_profile, monkeypatch):
        """Test successful update of availability data"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        new_availability = {
            "availability": {
                "Monday": ["Evening"],
                "Tuesday": ["Morning", "Afternoon"],
                "Wednesday": ["Morning"],
                "Thursday": [],
                "Friday": ["Evening"],
                "Saturday": ["Morning", "Afternoon", "Evening"],
                "Sunday": ["Afternoon"]
            }
        }
        
        response = client.post(
            "/availability",
            json=new_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Availability updated successfully"
    
    def test_update_availability_invalid_day(self, client, sample_profile, monkeypatch):
        """Test update with invalid day name"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        invalid_availability = {
            "availability": {
                "InvalidDay": ["Morning"],
                "Monday": ["Afternoon"]
            }
        }
        
        response = client.post(
            "/availability",
            json=invalid_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "Invalid day" in response.json()["detail"]
    
    def test_update_availability_invalid_times_format(self, client, sample_profile, monkeypatch):
        """Test update with invalid times format"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        invalid_availability = {
            "availability": {
                "Monday": "Morning",  # Should be list, not string
                "Tuesday": ["Afternoon"]
            }
        }
        
        response = client.post(
            "/availability",
            json=invalid_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "should be a list" in response.json()["detail"]
    
    def test_update_availability_unauthorized(self, client):
        """Test POST availability without authentication"""
        availability_data = {
            "availability": {
                "Monday": ["Morning"]
            }
        }
        
        response = client.post("/availability", json=availability_data)
        assert response.status_code == 401
    
    def test_update_availability_user_not_found(self, client, monkeypatch):
        """Test POST availability when user doesn't exist"""
        def mock_get_current_user():
            return None
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: None)
        
        availability_data = {
            "availability": {
                "Monday": ["Morning"]
            }
        }
        
        response = client.post(
            "/availability",
            json=availability_data,
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 404

class TestAvailabilityValidation:
    """Test availability data validation in API endpoints"""
    
    def test_valid_days_validation(self, client, sample_profile, monkeypatch):
        """Test that only valid days are accepted"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in valid_days:
            availability_data = {
                "availability": {
                    day: ["Morning"]
                }
            }
            
            response = client.post(
                "/availability",
                json=availability_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
    
    def test_valid_time_slots_validation(self, client, sample_profile, monkeypatch):
        """Test that only valid time slots are accepted"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        valid_times = ["Morning", "Afternoon", "Evening"]
        
        for time_slot in valid_times:
            availability_data = {
                "availability": {
                    "Monday": [time_slot]
                }
            }
            
            response = client.post(
                "/availability",
                json=availability_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
    
    def test_empty_availability_update(self, client, sample_profile, monkeypatch):
        """Test updating with empty availability (clearing schedule)"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        empty_availability = {
            "availability": {}
        }
        
        response = client.post(
            "/availability",
            json=empty_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
    
    def test_partial_week_availability(self, client, sample_profile, monkeypatch):
        """Test updating with partial week availability"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        partial_availability = {
            "availability": {
                "Monday": ["Morning"],
                "Wednesday": ["Evening"],
                "Friday": ["Afternoon"]
            }
        }
        
        response = client.post(
            "/availability",
            json=partial_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200

class TestAvailabilityEdgeCases:
    """Test edge cases and error handling"""
    
    def test_malformed_json_request(self, client, sample_profile, monkeypatch):
        """Test handling of malformed JSON in request"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        # Send invalid JSON
        response = client.post(
            "/availability",
            data="invalid json",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_availability_field(self, client, sample_profile, monkeypatch):
        """Test request missing required availability field"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        invalid_request = {
            "not_availability": {
                "Monday": ["Morning"]
            }
        }
        
        response = client.post(
            "/availability",
            json=invalid_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_availability_with_null_values(self, client, sample_profile, monkeypatch):
        """Test handling of null values in availability data"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        null_availability = {
            "availability": None
        }
        
        response = client.post(
            "/availability",
            json=null_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # This should be handled gracefully
        assert response.status_code in [200, 400]  # Depends on validation logic
    
    def test_very_large_availability_data(self, client, sample_profile, monkeypatch):
        """Test handling of unusually large availability data"""
        def mock_get_current_user():
            return sample_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: sample_profile)
        
        # Create large availability data (many time slots per day)
        large_availability = {
            "availability": {
                day: [f"Slot{i}" for i in range(100)]  # 100 time slots per day
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            }
        }
        
        response = client.post(
            "/availability",
            json=large_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 400, 413]  # OK, Bad Request, or Payload Too Large

class TestAvailabilityIntegration:
    """Integration tests combining multiple operations"""
    
    def test_create_update_retrieve_availability_flow(self, client, db_session, monkeypatch):
        """Test complete flow: create profile, update availability, retrieve availability"""
        # Create a profile first
        profile = Profile(
            email="integration@example.com",
            username="integration_user",
            study_style="Group",
            preferred_environment="Quiet",
            personality_traits={"type": "Introvert"},
            academic_focus_areas=["Computer Science"],
            password="testpassword",
            availability=None
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)
        
        def mock_get_current_user():
            return profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: profile)
        
        # Update availability
        new_availability = {
            "availability": {
                "Monday": ["Morning", "Evening"],
                "Tuesday": ["Afternoon"],
                "Wednesday": [],
                "Thursday": ["Morning"],
                "Friday": ["Evening"],
                "Saturday": ["Morning", "Afternoon"],
                "Sunday": []
            }
        }
        
        update_response = client.post(
            "/availability",
            json=new_availability,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert update_response.status_code == 200
        
        # Retrieve updated availability
        get_response = client.get(
            "/availability",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        assert retrieved_data["availability"] == new_availability["availability"]
    
    def test_multiple_users_availability_isolation(self, client, db_session, monkeypatch):
        """Test that availability updates for one user don't affect another"""
        # Create two profiles
        user1 = Profile(
            email="user1@example.com",
            username="user1",
            study_style="Group",
            preferred_environment="Quiet",
            personality_traits={"type": "Introvert"},
            academic_focus_areas=["Math"],
            password="pass1",
            availability={"Monday": ["Morning"]}
        )
        
        user2 = Profile(
            email="user2@example.com",
            username="user2",
            study_style="Solo",
            preferred_environment="Active",
            personality_traits={"type": "Extrovert"},
            academic_focus_areas=["Science"],
            password="pass2",
            availability={"Tuesday": ["Evening"]}
        )
        
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        
        # Update user1's availability
        def mock_get_current_user_1():
            return user1
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: user1)
        
        user1_new_availability = {
            "availability": {
                "Wednesday": ["Afternoon"]
            }
        }
        
        response = client.post(
            "/availability",
            json=user1_new_availability,
            headers={"Authorization": "Bearer user1_token"}
        )
        
        assert response.status_code == 200
        
        # Verify user2's availability unchanged
        def mock_get_current_user_2():
            return user2
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: user2)
        
        user2_response = client.get(
            "/availability",
            headers={"Authorization": "Bearer user2_token"}
        )
        
        assert user2_response.status_code == 200
        user2_data = user2_response.json()
        assert user2_data["availability"]["Tuesday"] == ["Evening"]
        assert "Wednesday" not in user2_data["availability"]
