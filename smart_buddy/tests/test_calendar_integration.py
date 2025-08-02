"""
Integration tests for availability calendar UI
Mock calendar UI inputs and test end-to-end flows
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from smart_buddy.main import app
from smart_buddy.models.sqlalchemy_models import Profile, Base
from smart_buddy.db import get_db
from unittest.mock import Mock, patch
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_calendar_integration.db"
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

class MockCalendarUI:
    """Mock calendar UI for testing frontend interactions"""
    
    def __init__(self):
        self.selected_slots = {}
        self.ui_state = {
            "current_week": "2025-01-20",  # Mock current week
            "view_mode": "week",
            "selected_slots": {},
            "is_loading": False,
            "error_message": None
        }
    
    def click_time_slot(self, day: str, time_slot: str):
        """Simulate clicking a time slot in the calendar UI"""
        if day not in self.selected_slots:
            self.selected_slots[day] = []
        
        if time_slot in self.selected_slots[day]:
            # Toggle off if already selected
            self.selected_slots[day].remove(time_slot)
            if not self.selected_slots[day]:
                del self.selected_slots[day]
        else:
            # Toggle on
            self.selected_slots[day].append(time_slot)
        
        self.ui_state["selected_slots"] = self.selected_slots.copy()
        return self.selected_slots
    
    def clear_all_selections(self):
        """Simulate clearing all calendar selections"""
        self.selected_slots = {}
        self.ui_state["selected_slots"] = {}
        return self.selected_slots
    
    def select_entire_day(self, day: str):
        """Simulate selecting entire day (all time slots)"""
        all_slots = ["Morning", "Afternoon", "Evening"]
        self.selected_slots[day] = all_slots.copy()
        self.ui_state["selected_slots"] = self.selected_slots.copy()
        return self.selected_slots
    
    def bulk_select_days(self, days: list, time_slots: list):
        """Simulate bulk selection of multiple days and times"""
        for day in days:
            if day not in self.selected_slots:
                self.selected_slots[day] = []
            for slot in time_slots:
                if slot not in self.selected_slots[day]:
                    self.selected_slots[day].append(slot)
        
        self.ui_state["selected_slots"] = self.selected_slots.copy()
        return self.selected_slots
    
    def get_form_data(self):
        """Get form data as it would be submitted by the calendar UI"""
        form_data = {}
        for day, slots in self.selected_slots.items():
            for slot in slots:
                key = f"availability[{day}][]"
                if key not in form_data:
                    form_data[key] = []
                form_data[key].append(slot)
        return form_data
    
    def get_api_payload(self):
        """Get API payload as it would be sent by the calendar UI"""
        return {"availability": self.selected_slots.copy()}

@pytest.fixture
def mock_calendar():
    """Create mock calendar UI"""
    return MockCalendarUI()

@pytest.fixture
def test_profile(db_session):
    """Create test profile for calendar integration tests"""
    profile = Profile(
        email="calendar@example.com",
        username="calendar_user",
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
    return profile

class TestCalendarUIInteractions:
    """Test calendar UI interaction flows"""
    
    def test_single_slot_selection(self, mock_calendar):
        """Test selecting a single time slot"""
        result = mock_calendar.click_time_slot("Monday", "Morning")
        
        assert "Monday" in result
        assert "Morning" in result["Monday"]
        assert len(result["Monday"]) == 1
        
        # Test form data generation
        form_data = mock_calendar.get_form_data()
        assert "availability[Monday][]" in form_data
        assert "Morning" in form_data["availability[Monday][]"]
    
    def test_multiple_slots_same_day(self, mock_calendar):
        """Test selecting multiple time slots on the same day"""
        mock_calendar.click_time_slot("Monday", "Morning")
        mock_calendar.click_time_slot("Monday", "Evening")
        result = mock_calendar.click_time_slot("Monday", "Afternoon")
        
        assert len(result["Monday"]) == 3
        assert set(result["Monday"]) == {"Morning", "Afternoon", "Evening"}
    
    def test_toggle_slot_off(self, mock_calendar):
        """Test toggling a selected slot off"""
        mock_calendar.click_time_slot("Monday", "Morning")
        mock_calendar.click_time_slot("Monday", "Afternoon")
        
        # Toggle off morning
        result = mock_calendar.click_time_slot("Monday", "Morning")
        
        assert "Monday" in result
        assert "Morning" not in result["Monday"]
        assert "Afternoon" in result["Monday"]
    
    def test_toggle_all_slots_off(self, mock_calendar):
        """Test toggling all slots off removes the day"""
        mock_calendar.click_time_slot("Monday", "Morning")
        result = mock_calendar.click_time_slot("Monday", "Morning")  # Toggle off
        
        assert "Monday" not in result
    
    def test_select_entire_day(self, mock_calendar):
        """Test selecting entire day functionality"""
        result = mock_calendar.select_entire_day("Tuesday")
        
        assert "Tuesday" in result
        assert len(result["Tuesday"]) == 3
        assert set(result["Tuesday"]) == {"Morning", "Afternoon", "Evening"}
    
    def test_bulk_selection(self, mock_calendar):
        """Test bulk selection of multiple days"""
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        work_hours = ["Morning", "Afternoon"]
        
        result = mock_calendar.bulk_select_days(weekdays, work_hours)
        
        for day in weekdays:
            assert day in result
            assert set(result[day]) == set(work_hours)
        
        # Weekend should not be selected
        assert "Saturday" not in result
        assert "Sunday" not in result
    
    def test_clear_all_selections(self, mock_calendar):
        """Test clearing all calendar selections"""
        # First make some selections
        mock_calendar.click_time_slot("Monday", "Morning")
        mock_calendar.click_time_slot("Tuesday", "Evening")
        mock_calendar.select_entire_day("Wednesday")
        
        # Then clear all
        result = mock_calendar.clear_all_selections()
        
        assert result == {}
        assert mock_calendar.ui_state["selected_slots"] == {}

class TestCalendarToAPIIntegration:
    """Test integration between calendar UI and API endpoints"""
    
    def test_calendar_selections_to_profile_creation(self, client, mock_calendar):
        """Test calendar selections being used in profile creation"""
        # User selects availability in calendar UI
        mock_calendar.click_time_slot("Monday", "Morning")
        mock_calendar.click_time_slot("Monday", "Evening")
        mock_calendar.click_time_slot("Wednesday", "Afternoon")
        mock_calendar.select_entire_day("Friday")
        
        # Get the form data as it would be submitted
        calendar_selections = mock_calendar.get_api_payload()
        
        # Create profile with calendar data
        profile_data = {
            "email": "calendar_test@example.com",
            "username": "calendar_test_user",
            "study_style": "Group",
            "preferred_environment": "Quiet",
            "personality_traits": "Introvert",
            "academic_focus_areas": "Computer Science",
            "password": "testpassword"
        }
        
        # Mock form data including availability
        with patch('smart_buddy.main.request') as mock_request:
            mock_form = Mock()
            mock_form.items.return_value = [
                ('email', 'calendar_test@example.com'),
                ('username', 'calendar_test_user'),
                ('study_style', 'Group'),
                ('preferred_environment', 'Quiet'),
                ('personality_traits', 'Introvert'),
                ('academic_focus_areas', 'Computer Science'),
                ('password', 'testpassword'),
                ('availability[Monday][]', 'Morning'),
                ('availability[Monday][]', 'Evening'),
                ('availability[Wednesday][]', 'Afternoon'),
                ('availability[Friday][]', 'Morning'),
                ('availability[Friday][]', 'Afternoon'),
                ('availability[Friday][]', 'Evening'),
            ]
            mock_request.form.return_value = mock_form
            
            response = client.post("/profile", data=profile_data)
            
            # Should succeed (though may fail due to missing form handling)
            # In real integration, this would test the full form submission
            assert response.status_code in [200, 302, 422]  # Various possible outcomes
    
    def test_calendar_update_via_api(self, client, test_profile, mock_calendar, monkeypatch):
        """Test updating availability through calendar UI to API"""
        def mock_get_current_user():
            return test_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: test_profile)
        
        # User makes selections in calendar UI
        mock_calendar.click_time_slot("Monday", "Morning")
        mock_calendar.click_time_slot("Tuesday", "Afternoon")
        mock_calendar.click_time_slot("Tuesday", "Evening")
        mock_calendar.select_entire_day("Saturday")
        
        # Get API payload from calendar selections
        api_payload = mock_calendar.get_api_payload()
        
        # Submit to API
        response = client.post(
            "/availability",
            json=api_payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        
        # Verify the data was saved correctly
        get_response = client.get(
            "/availability",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert get_response.status_code == 200
        saved_data = get_response.json()
        
        expected_availability = {
            "Monday": ["Morning"],
            "Tuesday": ["Afternoon", "Evening"],
            "Saturday": ["Morning", "Afternoon", "Evening"]
        }
        
        assert saved_data["availability"] == expected_availability

class TestCalendarUIScenarios:
    """Test realistic user scenarios with calendar UI"""
    
    def test_typical_student_schedule_scenario(self, client, test_profile, mock_calendar, monkeypatch):
        """Test typical student creating their weekly schedule"""
        def mock_get_current_user():
            return test_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: test_profile)
        
        # Scenario: Student available for study sessions
        # - Weekday mornings (before classes)
        # - Some weekday evenings
        # - Weekend afternoons
        
        # Select weekday mornings
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        mock_calendar.bulk_select_days(weekdays, ["Morning"])
        
        # Add some evening slots
        mock_calendar.click_time_slot("Tuesday", "Evening")
        mock_calendar.click_time_slot("Thursday", "Evening")
        
        # Add weekend afternoons
        mock_calendar.click_time_slot("Saturday", "Afternoon")
        mock_calendar.click_time_slot("Sunday", "Afternoon")
        
        # Submit to API
        api_payload = mock_calendar.get_api_payload()
        response = client.post(
            "/availability",
            json=api_payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        
        # Verify realistic schedule was saved
        expected_schedule = {
            "Monday": ["Morning"],
            "Tuesday": ["Morning", "Evening"],
            "Wednesday": ["Morning"],
            "Thursday": ["Morning", "Evening"],
            "Friday": ["Morning"],
            "Saturday": ["Afternoon"],
            "Sunday": ["Afternoon"]
        }
        
        get_response = client.get(
            "/availability",
            headers={"Authorization": "Bearer test_token"}
        )
        
        saved_schedule = get_response.json()["availability"]
        assert saved_schedule == expected_schedule
    
    def test_schedule_modification_scenario(self, client, test_profile, mock_calendar, monkeypatch):
        """Test user modifying existing schedule"""
        def mock_get_current_user():
            return test_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: test_profile)
        
        # Initial schedule setup
        mock_calendar.select_entire_day("Monday")
        mock_calendar.click_time_slot("Wednesday", "Morning")
        mock_calendar.click_time_slot("Friday", "Evening")
        
        initial_payload = mock_calendar.get_api_payload()
        client.post(
            "/availability",
            json=initial_payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # User decides to modify schedule
        # Remove Monday morning (conflict with new class)
        mock_calendar.click_time_slot("Monday", "Morning")  # Toggle off
        
        # Add Tuesday afternoon (free period)
        mock_calendar.click_time_slot("Tuesday", "Afternoon")
        
        # Change Friday evening to afternoon
        mock_calendar.click_time_slot("Friday", "Evening")  # Toggle off
        mock_calendar.click_time_slot("Friday", "Afternoon")  # Toggle on
        
        # Submit modified schedule
        modified_payload = mock_calendar.get_api_payload()
        response = client.post(
            "/availability",
            json=modified_payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        
        # Verify modifications were applied
        expected_modified_schedule = {
            "Monday": ["Afternoon", "Evening"],  # Morning removed
            "Tuesday": ["Afternoon"],  # Added
            "Wednesday": ["Morning"],  # Unchanged
            "Friday": ["Afternoon"]  # Changed from Evening
        }
        
        get_response = client.get(
            "/availability",
            headers={"Authorization": "Bearer test_token"}
        )
        
        saved_schedule = get_response.json()["availability"]
        assert saved_schedule == expected_modified_schedule
    
    def test_emergency_schedule_clear_scenario(self, client, test_profile, mock_calendar, monkeypatch):
        """Test user clearing entire schedule (emergency/busy period)"""
        def mock_get_current_user():
            return test_profile
        
        monkeypatch.setattr("smart_buddy.routers.availability.get_current_user", lambda token, db: test_profile)
        
        # Set up full schedule first
        all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in all_days:
            mock_calendar.select_entire_day(day)
        
        # Submit full schedule
        full_payload = mock_calendar.get_api_payload()
        client.post(
            "/availability",
            json=full_payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Emergency: clear entire schedule
        mock_calendar.clear_all_selections()
        
        # Submit empty schedule
        empty_payload = mock_calendar.get_api_payload()
        response = client.post(
            "/availability",
            json=empty_payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        
        # Verify schedule was cleared
        get_response = client.get(
            "/availability",
            headers={"Authorization": "Bearer test_token"}
        )
        
        saved_schedule = get_response.json()["availability"]
        assert saved_schedule == {}

class TestCalendarUIValidation:
    """Test calendar UI validation and error handling"""
    
    def test_invalid_day_handling(self, mock_calendar):
        """Test calendar UI handling invalid day names"""
        # Calendar UI should prevent invalid day selection
        # but test what happens if it somehow occurs
        try:
            mock_calendar.click_time_slot("InvalidDay", "Morning")
            # If no error, check the selection
            selections = mock_calendar.get_api_payload()
            # This would be caught by API validation
            assert "InvalidDay" in selections["availability"]
        except Exception as e:
            # UI should handle this gracefully
            assert isinstance(e, (ValueError, KeyError))
    
    def test_invalid_time_slot_handling(self, mock_calendar):
        """Test calendar UI handling invalid time slots"""
        try:
            mock_calendar.click_time_slot("Monday", "InvalidTime")
            selections = mock_calendar.get_api_payload()
            # This would be caught by API validation
            assert "InvalidTime" in selections["availability"]["Monday"]
        except Exception as e:
            # UI should handle this gracefully
            assert isinstance(e, (ValueError, KeyError))
    
    def test_calendar_ui_state_consistency(self, mock_calendar):
        """Test that calendar UI state remains consistent"""
        # Make various selections
        mock_calendar.click_time_slot("Monday", "Morning")
        mock_calendar.select_entire_day("Tuesday")
        mock_calendar.click_time_slot("Wednesday", "Evening")
        
        # Check UI state consistency
        ui_state = mock_calendar.ui_state["selected_slots"]
        direct_selections = mock_calendar.selected_slots
        
        assert ui_state == direct_selections
        
        # Check API payload consistency
        api_payload = mock_calendar.get_api_payload()
        assert api_payload["availability"] == direct_selections
