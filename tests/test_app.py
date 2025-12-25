import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Debate Team" in data
    assert "participants" in data["Debate Team"]
    assert "alex@mergington.edu" in data["Debate Team"]["participants"]

def test_signup_success():
    # Test successful signup
    response = client.post("/activities/Debate%20Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up newstudent@mergington.edu for Debate Team" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Debate Team"]["participants"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Math%20Club/signup?email=duplicate@mergington.edu")
    # Try again
    response = client.post("/activities/Math%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"

def test_unregister_success():
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=unregister@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@mergington.edu from Basketball Team" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@mergington.edu" not in data["Basketball Team"]["participants"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_not_signed_up():
    response = client.delete("/activities/Debate%20Team/unregister?email=notsigned@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not signed up for this activity"