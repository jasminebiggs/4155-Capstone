# tests/test_user_profile.py

def test_create_user_profile(client):
    response = client.post("/profiles/", json={
        "name": "Jasmine",
        "email": "jasmine@example.com",
        "study_style": "solo",
        "preferred_environment": "quiet",
        "personality_traits": "introvert",
        "study_subjects": "CS, Math",
        "availability": "Weekends",
        "goals": "Graduate early"
    })
    assert response.status_code == 200
