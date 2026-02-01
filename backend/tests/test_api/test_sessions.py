"""
Tests for session management API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.services.simulation_engine import simulation_engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear active sessions before each test."""
    simulation_engine.active_sessions.clear()
    yield
    simulation_engine.active_sessions.clear()


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "docs" in data


def test_list_scenarios():
    """Test listing available scenarios."""
    response = client.get("/api/v1/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0

    # Check scenario structure
    scenario = scenarios[0]
    assert "scenario_id" in scenario
    assert "title" in scenario
    assert "description" in scenario
    assert "patient_count" in scenario


def test_start_session():
    """Test starting a new simulation session."""
    response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    assert response.status_code == 201
    data = response.json()

    assert "session_id" in data
    assert data["scenario_id"] == "simple_test_001"
    assert data["is_complete"] is False
    assert "current_time" in data
    assert "elapsed_minutes" in data

    # Verify session was created
    session_id = data["session_id"]
    assert session_id in simulation_engine.active_sessions


def test_start_session_with_custom_time():
    """Test starting a session with custom start time."""
    custom_time = "2024-02-01T18:00:00"
    response = client.post(
        "/api/v1/sessions/start",
        json={
            "scenario_id": "simple_test_001",
            "custom_start_time": custom_time,
        },
    )
    assert response.status_code == 201
    data = response.json()

    assert data["scenario_id"] == "simple_test_001"
    # The current_time should match custom_start_time initially
    assert data["current_time"].startswith("2024-02-01T18:00")


def test_start_session_invalid_scenario():
    """Test starting a session with invalid scenario ID."""
    response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "nonexistent_scenario"},
    )
    assert response.status_code == 404


def test_get_session():
    """Test retrieving session state."""
    # Create a session first
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    session_id = start_response.json()["session_id"]

    # Get session state
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == session_id
    assert data["scenario_id"] == "simple_test_001"
    assert "clock" in data
    assert "patients" in data
    assert "scheduler" in data
    assert data["is_complete"] is False


def test_get_session_not_found():
    """Test retrieving non-existent session."""
    response = client.get("/api/v1/sessions/invalid_session_id")
    assert response.status_code == 404


def test_list_sessions():
    """Test listing all active sessions."""
    # Start multiple sessions
    client.post("/api/v1/sessions/start", json={"scenario_id": "simple_test_001"})
    client.post("/api/v1/sessions/start", json={"scenario_id": "simple_test_001"})

    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()

    assert "sessions" in data
    assert "count" in data
    assert data["count"] == 2
    assert len(data["sessions"]) == 2


def test_get_session_timeline():
    """Test retrieving session timeline."""
    # Create session
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    session_id = start_response.json()["session_id"]

    # Get timeline
    response = client.get(f"/api/v1/sessions/{session_id}/timeline")
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == session_id
    assert "timeline" in data
    assert isinstance(data["timeline"], list)


def test_get_patient_details():
    """Test retrieving patient details."""
    # Create session
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    session_id = start_response.json()["session_id"]

    # Get patient details
    response = client.get(f"/api/v1/sessions/{session_id}/patients/pt_001")
    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "pt_001"
    assert data["name"] == "Margaret Thompson"
    assert data["mrn"] == "MRN12345"
    assert data["age"] == 72
    assert data["ward"] == "Ward 4A"
    assert "current_state" in data
    assert "actions_taken" in data


def test_get_patient_details_not_found():
    """Test retrieving non-existent patient."""
    # Create session
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    session_id = start_response.json()["session_id"]

    # Try to get non-existent patient
    response = client.get(f"/api/v1/sessions/{session_id}/patients/invalid_patient")
    assert response.status_code == 404


def test_complete_session():
    """Test completing a session."""
    # Create session
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    session_id = start_response.json()["session_id"]

    # Complete session
    response = client.post(f"/api/v1/sessions/{session_id}/complete")
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == session_id
    assert data["scenario_id"] == "simple_test_001"
    assert "completed_at" in data
    assert "total_time_elapsed_minutes" in data
    assert "patients" in data
    assert "timeline" in data


def test_complete_session_not_found():
    """Test completing non-existent session."""
    response = client.post("/api/v1/sessions/invalid_session/complete")
    assert response.status_code == 404


def test_delete_session():
    """Test deleting a session."""
    # Create session
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    session_id = start_response.json()["session_id"]

    # Delete session
    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == session_id
    assert data["deleted"] is True

    # Verify session is deleted
    assert session_id not in simulation_engine.active_sessions


def test_delete_session_not_found():
    """Test deleting non-existent session."""
    response = client.delete("/api/v1/sessions/invalid_session")
    assert response.status_code == 404


def test_session_workflow():
    """Test complete session workflow."""
    # 1. List scenarios
    scenarios_response = client.get("/api/v1/scenarios")
    assert scenarios_response.status_code == 200

    # 2. Start session
    start_response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    assert start_response.status_code == 201
    session_id = start_response.json()["session_id"]

    # 3. Get session state
    state_response = client.get(f"/api/v1/sessions/{session_id}")
    assert state_response.status_code == 200

    # 4. Get patient details
    patient_response = client.get(f"/api/v1/sessions/{session_id}/patients/pt_001")
    assert patient_response.status_code == 200

    # 5. Get timeline
    timeline_response = client.get(f"/api/v1/sessions/{session_id}/timeline")
    assert timeline_response.status_code == 200

    # 6. Complete session
    complete_response = client.post(f"/api/v1/sessions/{session_id}/complete")
    assert complete_response.status_code == 200

    # 7. Delete session
    delete_response = client.delete(f"/api/v1/sessions/{session_id}")
    assert delete_response.status_code == 200
