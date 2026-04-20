"""
Tests for the Mergington High School API
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add src to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a FastAPI TestClient for testing"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    }
    
    # Yield to run the test
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original)


# Test GET /activities endpoint
class TestGetActivities:
    def test_get_activities_returns_all(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert expected_activity in data

    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club = data["Chess Club"]
        for field in expected_fields:
            assert field in chess_club

    def test_get_activities_participants_list(self, client, reset_activities):
        """Test that participants are returned as a list"""
        # Arrange
        expected_participant = "michael@mergington.edu"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data["Chess Club"]["participants"], list)
        assert expected_participant in data["Chess Club"]["participants"]


# Test POST /activities/{activity_name}/signup endpoint
class TestSignupForActivity:
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert f"Signed up {email} for {activity}" in data["message"]

    def test_signup_verification(self, client, reset_activities):
        """Test that signup actually adds the student to the activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        chess_activity = response.json()[activity]
        assert email in chess_activity["participants"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        # Arrange
        email = "michael@mergington.edu"  # Already signed up
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


# Test DELETE /activities/{activity_name}/signup endpoint
class TestDeleteSignup:
    def test_delete_signup_success(self, client, reset_activities):
        """Test removing a student from an activity"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert f"Removed {email} from {activity}" in response.json()["message"]

    def test_delete_signup_verification(self, client, reset_activities):
        """Test that deletion actually removes the student"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        chess_activity = response.json()[activity]
        assert email not in chess_activity["participants"]

    def test_delete_nonexistent_activity(self, client, reset_activities):
        """Test deleting signup from a non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_delete_not_signed_up(self, client, reset_activities):
        """Test removing a student who is not signed up"""
        # Arrange
        email = "notasignedupstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]