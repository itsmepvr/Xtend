import pytest
from starlette.testclient import TestClient
from xtend.app import app, app_sessions

client = TestClient(app)

def test_stream_page_invalid_session_returns_expired_template():
    session_id = "invalid123"
    if session_id in app_sessions:
        del app_sessions[session_id]
    response = client.get(f"/stream/{session_id}")
    assert response.status_code == 200
    assert "session expired" in response.text.lower()
