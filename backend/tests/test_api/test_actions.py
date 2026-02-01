"""
Tests for action execution API endpoints.
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


@pytest.fixture
def active_session():
    """Create an active session for testing."""
    response = client.post(
        "/api/v1/sessions/start",
        json={"scenario_id": "simple_test_001"},
    )
    return response.json()["session_id"]


def test_execute_action_review_in_person(active_session):
    """Test executing an in-person review action."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
            "details": {"location": "Ward 4A, Bed 12"},
            "time_cost_minutes": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "review_in_person"
    assert data["patient_id"] == "pt_001"
    assert data["time_advanced_minutes"] >= 30  # At least 30 mins (+ real time)
    assert "new_simulation_time" in data
    assert "message" in data


def test_execute_action_escalate(active_session):
    """Test executing an escalation action."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "escalate",
            "patient_id": "pt_001",
            "details": {"escalate_to": "registrar", "reason": "Patient deteriorating"},
            "time_cost_minutes": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "escalate"
    assert data["patient_id"] == "pt_001"


def test_execute_action_request_investigation(active_session):
    """Test requesting an investigation."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "request_investigation",
            "patient_id": "pt_001",
            "details": {"investigation_type": "ABG", "urgency": "urgent"},
            "time_cost_minutes": 2,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "request_investigation"


def test_execute_action_document_note(active_session):
    """Test documenting a clinical note."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "document_note",
            "patient_id": "pt_001",
            "details": {"note_content": "Patient reviewed, stable", "note_type": "review"},
            "time_cost_minutes": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "document_note"


def test_execute_action_ask_nurse_question(active_session):
    """Test asking nurse a question."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "ask_nurse_question",
            "patient_id": "pt_001",
            "details": {"question": "What are the current observations?"},
            "time_cost_minutes": 2,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "ask_nurse_question"


def test_execute_action_invalid_patient(active_session):
    """Test executing action for non-existent patient."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "invalid_patient",
            "details": {},
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Action executes but returns failure
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_execute_action_session_not_found():
    """Test executing action in non-existent session."""
    response = client.post(
        "/api/v1/sessions/invalid_session/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
            "details": {},
        },
    )
    assert response.status_code == 400


def test_review_patient_convenience_endpoint(active_session):
    """Test the convenience endpoint for patient review."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions/review",
        params={
            "patient_id": "pt_001",
            "location": "Ward 4A, Bed 12",
            "time_cost_minutes": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "review_in_person"


def test_escalate_convenience_endpoint(active_session):
    """Test the convenience endpoint for escalation."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions/escalate",
        params={
            "patient_id": "pt_001",
            "escalate_to": "registrar",
            "reason": "Type 2 respiratory failure",
            "time_cost_minutes": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "escalate"


def test_investigate_convenience_endpoint(active_session):
    """Test the convenience endpoint for requesting investigations."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions/investigate",
        params={
            "patient_id": "pt_001",
            "investigation_type": "ABG",
            "urgency": "urgent",
            "expected_delay_minutes": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "request_investigation"


def test_document_convenience_endpoint(active_session):
    """Test the convenience endpoint for documenting notes."""
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions/document",
        params={
            "patient_id": "pt_001",
            "note_content": "Patient reviewed at 20:15. Increased work of breathing.",
            "note_type": "review",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["action_type"] == "document_note"


def test_action_triggers_events(active_session):
    """Test that actions can trigger scheduled events."""
    # Execute an action that advances time significantly
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
            "time_cost_minutes": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Check if any events were triggered
    # (depends on scenario timing, but structure should be present)
    assert "triggered_events" in data
    assert "new_notifications" in data
    assert isinstance(data["triggered_events"], list)
    assert isinstance(data["new_notifications"], list)


def test_action_sequence(active_session):
    """Test executing a sequence of actions."""
    # 1. Ask nurse question
    response1 = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "ask_nurse_question",
            "patient_id": "pt_001",
            "details": {"question": "What are the observations?"},
        },
    )
    assert response1.status_code == 200
    time_after_first = response1.json()["new_simulation_time"]

    # 2. Review in person
    response2 = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
            "time_cost_minutes": 30,
        },
    )
    assert response2.status_code == 200
    time_after_second = response2.json()["new_simulation_time"]

    # Time should advance
    assert time_after_second > time_after_first

    # 3. Escalate
    response3 = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "escalate",
            "patient_id": "pt_001",
            "details": {"escalate_to": "registrar", "reason": "Respiratory failure"},
        },
    )
    assert response3.status_code == 200

    # Check if escalation triggered patient state change
    # (depends on scenario rules, but check structure)
    data = response3.json()
    assert "patient_state_changes" in data


def test_action_updates_patient_history(active_session):
    """Test that actions are recorded in patient history."""
    # Execute action
    client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
        },
    )

    # Get patient details
    response = client.get(f"/api/v1/sessions/{active_session}/patients/pt_001")
    assert response.status_code == 200
    data = response.json()

    # Check action is in history
    assert len(data["actions_taken"]) > 0
    assert data["actions_taken"][0]["action_type"] == "review_in_person"


def test_action_updates_session_timeline(active_session):
    """Test that actions appear in session timeline."""
    # Execute action
    client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "document_note",
            "patient_id": "pt_001",
            "details": {"note_content": "Test note"},
        },
    )

    # Get timeline
    response = client.get(f"/api/v1/sessions/{active_session}/timeline")
    assert response.status_code == 200
    data = response.json()

    # Check timeline has entries
    assert len(data["timeline"]) > 0


def test_completed_session_rejects_actions(active_session):
    """Test that completed sessions reject new actions."""
    # Complete session
    client.post(f"/api/v1/sessions/{active_session}/complete")

    # Try to execute action
    response = client.post(
        f"/api/v1/sessions/{active_session}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
        },
    )
    assert response.status_code == 400
    assert "already complete" in response.json()["detail"].lower()
