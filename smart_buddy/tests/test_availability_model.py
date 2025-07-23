"""
Unit tests for availability data model & schema
Testing data validation, serialization, and model constraints
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from smart_buddy.models.sqlalchemy_models import Profile, Base
from smart_buddy.schemas import Availability
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_availability.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_availability_data():
    """Sample availability data for testing"""
    return {
        "Monday": ["Morning", "Afternoon"],
        "Tuesday": ["Evening"],
        "Wednesday": ["Morning", "Evening"],
        "Thursday": [],
        "Friday": ["Afternoon", "Evening"],
        "Saturday": ["Morning"],
        "Sunday": []
    }

@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "study_style": "Group",
        "preferred_environment": "Quiet",
        "personality_traits": {"type": "Introvert"},
        "academic_focus_areas": ["Computer Science", "Mathematics"],
        "password": "testpassword123"
    }

class TestAvailabilitySchema:
    """Test the Availability Pydantic schema"""
    
    def test_valid_availability_schema(self, sample_availability_data):
        """Test that valid availability data passes schema validation"""
        availability = Availability(availability=sample_availability_data)
        assert availability.availability == sample_availability_data
    
    def test_empty_availability_schema(self):
        """Test that empty availability data is valid"""
        availability = Availability(availability={})
        assert availability.availability == {}
    
    def test_availability_with_all_days(self):
        """Test availability with all days of the week"""
        full_week_data = {
            "Monday": ["Morning", "Afternoon", "Evening"],
            "Tuesday": ["Morning", "Afternoon", "Evening"],
            "Wednesday": ["Morning", "Afternoon", "Evening"],
            "Thursday": ["Morning", "Afternoon", "Evening"],
            "Friday": ["Morning", "Afternoon", "Evening"],
            "Saturday": ["Morning", "Afternoon", "Evening"],
            "Sunday": ["Morning", "Afternoon", "Evening"]
        }
        availability = Availability(availability=full_week_data)
        assert len(availability.availability) == 7
    
    def test_availability_serialization(self, sample_availability_data):
        """Test that availability schema can be serialized to dict"""
        availability = Availability(availability=sample_availability_data)
        serialized = availability.dict()
        assert "availability" in serialized
        assert serialized["availability"] == sample_availability_data
    
    def test_availability_json_serialization(self, sample_availability_data):
        """Test that availability schema can be serialized to JSON"""
        availability = Availability(availability=sample_availability_data)
        json_str = availability.json()
        parsed = json.loads(json_str)
        assert parsed["availability"] == sample_availability_data

class TestProfileAvailabilityModel:
    """Test the Profile model with availability data"""
    
    def test_create_profile_with_availability(self, db_session, sample_profile_data, sample_availability_data):
        """Test creating a profile with availability data"""
        profile = Profile(
            **sample_profile_data,
            availability=sample_availability_data
        )
        db_session.add(profile)
        db_session.commit()
        
        # Verify the profile was saved
        saved_profile = db_session.query(Profile).filter(Profile.username == "testuser").first()
        assert saved_profile is not None
        assert saved_profile.availability == sample_availability_data
    
    def test_create_profile_without_availability(self, db_session, sample_profile_data):
        """Test creating a profile without availability data"""
        profile = Profile(
            **sample_profile_data,
            availability=None
        )
        db_session.add(profile)
        db_session.commit()
        
        saved_profile = db_session.query(Profile).filter(Profile.username == "testuser").first()
        assert saved_profile is not None
        assert saved_profile.availability is None
    
    def test_update_profile_availability(self, db_session, sample_profile_data, sample_availability_data):
        """Test updating a profile's availability data"""
        # Create profile without availability
        profile = Profile(**sample_profile_data, availability=None)
        db_session.add(profile)
        db_session.commit()
        
        # Update with availability
        profile.availability = sample_availability_data
        db_session.commit()
        
        # Verify update
        updated_profile = db_session.query(Profile).filter(Profile.username == "testuser").first()
        assert updated_profile.availability == sample_availability_data
    
    def test_profile_availability_json_storage(self, db_session, sample_profile_data):
        """Test that complex availability data is stored correctly as JSON"""
        complex_availability = {
            "Monday": ["Morning", "Afternoon"],
            "Tuesday": ["Evening"],
            "Wednesday": [],
            "Thursday": ["Morning", "Afternoon", "Evening"],
            "Friday": ["Afternoon"],
            "Saturday": ["Morning", "Evening"],
            "Sunday": []
        }
        
        profile = Profile(**sample_profile_data, availability=complex_availability)
        db_session.add(profile)
        db_session.commit()
        
        saved_profile = db_session.query(Profile).filter(Profile.username == "testuser").first()
        assert saved_profile.availability == complex_availability
    
    def test_profile_unique_username_constraint(self, db_session, sample_profile_data, sample_availability_data):
        """Test that username uniqueness is enforced"""
        profile1 = Profile(**sample_profile_data, availability=sample_availability_data)
        db_session.add(profile1)
        db_session.commit()
        
        # Try to create another profile with same username
        profile2_data = sample_profile_data.copy()
        profile2_data["email"] = "different@example.com"
        profile2 = Profile(**profile2_data, availability=sample_availability_data)
        
        db_session.add(profile2)
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestAvailabilityDataValidation:
    """Test availability data validation and edge cases"""
    
    def test_availability_with_invalid_day(self):
        """Test that invalid day names are handled (note: schema doesn't validate day names)"""
        invalid_data = {
            "InvalidDay": ["Morning"],
            "Monday": ["Afternoon"]
        }
        # Schema should still accept this - validation happens at business logic level
        availability = Availability(availability=invalid_data)
        assert availability.availability == invalid_data
    
    def test_availability_with_invalid_time_slots(self):
        """Test that invalid time slots are handled (note: schema doesn't validate time slots)"""
        invalid_data = {
            "Monday": ["InvalidTime", "Morning"],
            "Tuesday": ["Afternoon"]
        }
        # Schema should still accept this - validation happens at business logic level
        availability = Availability(availability=invalid_data)
        assert availability.availability == invalid_data
    
    def test_availability_with_empty_day_lists(self):
        """Test that days with empty availability lists are valid"""
        data_with_empty_days = {
            "Monday": [],
            "Tuesday": ["Morning"],
            "Wednesday": [],
            "Thursday": ["Evening"],
            "Friday": [],
            "Saturday": [],
            "Sunday": ["Afternoon"]
        }
        availability = Availability(availability=data_with_empty_days)
        assert availability.availability == data_with_empty_days
    
    def test_availability_with_duplicate_time_slots(self):
        """Test that duplicate time slots in a day are preserved"""
        data_with_duplicates = {
            "Monday": ["Morning", "Morning", "Afternoon"],
            "Tuesday": ["Evening", "Evening"]
        }
        availability = Availability(availability=data_with_duplicates)
        assert availability.availability == data_with_duplicates
        assert len(availability.availability["Monday"]) == 3
        assert len(availability.availability["Tuesday"]) == 2

class TestAvailabilityModelIntegration:
    """Integration tests for availability model with database operations"""
    
    def test_multiple_profiles_different_availability(self, db_session):
        """Test multiple profiles with different availability patterns"""
        profiles_data = [
            {
                "email": "user1@example.com",
                "username": "user1",
                "study_style": "Group",
                "preferred_environment": "Quiet",
                "personality_traits": {"type": "Introvert"},
                "academic_focus_areas": ["Math"],
                "password": "pass1",
                "availability": {"Monday": ["Morning"], "Tuesday": ["Evening"]}
            },
            {
                "email": "user2@example.com",
                "username": "user2",
                "study_style": "Solo",
                "preferred_environment": "Active",
                "personality_traits": {"type": "Extrovert"},
                "academic_focus_areas": ["Science"],
                "password": "pass2",
                "availability": {"Wednesday": ["Afternoon"], "Friday": ["Morning", "Evening"]}
            }
        ]
        
        for profile_data in profiles_data:
            profile = Profile(**profile_data)
            db_session.add(profile)
        
        db_session.commit()
        
        # Verify both profiles saved correctly
        all_profiles = db_session.query(Profile).all()
        assert len(all_profiles) == 2
        
        user1 = db_session.query(Profile).filter(Profile.username == "user1").first()
        user2 = db_session.query(Profile).filter(Profile.username == "user2").first()
        
        assert user1.availability == {"Monday": ["Morning"], "Tuesday": ["Evening"]}
        assert user2.availability == {"Wednesday": ["Afternoon"], "Friday": ["Morning", "Evening"]}
    
    def test_query_profiles_by_availability(self, db_session):
        """Test querying profiles based on availability data"""
        # Create profiles with specific availability patterns
        morning_person = Profile(
            email="morning@example.com",
            username="morning_person",
            study_style="Group",
            preferred_environment="Quiet",
            personality_traits={"type": "Introvert"},
            academic_focus_areas=["Math"],
            password="pass",
            availability={"Monday": ["Morning"], "Tuesday": ["Morning"], "Wednesday": ["Morning"]}
        )
        
        evening_person = Profile(
            email="evening@example.com",
            username="evening_person",
            study_style="Solo",
            preferred_environment="Active",
            personality_traits={"type": "Extrovert"},
            academic_focus_areas=["Science"],
            password="pass",
            availability={"Monday": ["Evening"], "Tuesday": ["Evening"], "Wednesday": ["Evening"]}
        )
        
        db_session.add_all([morning_person, evening_person])
        db_session.commit()
        
        # Note: JSON querying syntax varies by database
        # This is a basic test - in real scenarios you'd use JSON query operators
        all_profiles = db_session.query(Profile).all()
        assert len(all_profiles) == 2
        
        morning_profile = db_session.query(Profile).filter(Profile.username == "morning_person").first()
        evening_profile = db_session.query(Profile).filter(Profile.username == "evening_person").first()
        
        assert "Morning" in str(morning_profile.availability)
        assert "Evening" in str(evening_profile.availability)
