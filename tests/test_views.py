"Test Cases"
from fastapi.testclient import TestClient
from app import app, app_sessions

client = TestClient(app)

def test_index():
    """Test index page renders correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Select an Application" in response.text  # Checking if applications are loaded

def test_handle_selection():
    """Test selecting an application for streaming."""
    response = client.post("/select-app", data={"application": "Google Chrome"})
    assert response.status_code == 200  # Redirect

def test_handle_selection_invalid():
    """Test selecting an application without providing a name."""
    response = client.post("/select-app", data={"application": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Application is required"}

def test_stream_invalid_session():
    """Test accessing stream with an invalid session ID."""
    response = client.get("/stream/invalid_session_id")
    assert response.status_code == 200
    assert "expired or invalid" in response.text  # Verify session expired template is served

def test_close_session():
    """Test closing a valid session."""
    app_sessions['sample'] = {}

    # Now close the session
    response = client.post("/close-session", data={"session_id": 'sample'})
    assert response.status_code == 200

    # Verify session is removed
    response = client.post("/close-session", data={"session_id": 'sample'})
    assert response.status_code == 404
