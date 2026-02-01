"""
API tests for EHR endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.services.simulation_engine import simulation_engine
from app.services.scenario_loader import scenario_loader
from app.services.ehr_service import ehr_service
from app.models.ehr import VisibilityRule, VisibilityCondition, NoteType

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up before and after each test."""
    simulation_engine.active_sessions.clear()
    ehr_service.clear_all_records()
    yield
    simulation_engine.active_sessions.clear()
    ehr_service.clear_all_records()


@pytest.fixture
def test_session():
    """Create a test session with a patient."""
    # Create session from simple test scenario
    session = scenario_loader.create_session_from_scenario("simple_test_001")
    simulation_engine.active_sessions[session.session_id] = session

    # Create EHR record for the patient
    patient_id = "pt_001"
    ehr_service.create_patient_record(
        patient_id=patient_id,
        mrn="MRN12345",
        name="Margaret Thompson",
        age=72,
        gender="Female",
        allergies=["Penicillin"],
        active_diagnoses=["COPD", "Hypertension"],
        current_medications=[
            {"name": "Salbutamol inhaler", "dose": "2 puffs PRN"}
        ]
    )

    return session


class TestGetPatientEHR:
    """Tests for GET /sessions/{session_id}/patients/{patient_id}/ehr endpoint."""

    def test_get_ehr_success(self, test_session):
        """Test successfully getting a patient's EHR."""
        session_id = test_session.session_id
        patient_id = "pt_001"

        # Add a clinical note
        current_time = datetime(2024, 1, 15, 20, 0, 0)
        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. Smith",
            author_role="FY1",
            title="Admission Note",
            content={"presenting_complaint": "SOB"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        response = client.get(f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr")

        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["name"] == "Margaret Thompson"
        assert data["age"] == 72
        assert len(data["allergies"]) == 1
        assert len(data["visible_notes"]) == 1
        assert data["total_notes"] == 1

    def test_get_ehr_session_not_found(self):
        """Test getting EHR for non-existent session."""
        response = client.get("/api/v1/sessions/invalid_session/patients/pt_001/ehr")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_ehr_patient_not_found(self, test_session):
        """Test getting EHR for non-existent patient."""
        session_id = test_session.session_id
        response = client.get(f"/api/v1/sessions/{session_id}/patients/pt_999/ehr")
        assert response.status_code == 404
        assert "patient pt_999 not found" in response.json()["detail"].lower()

    def test_get_ehr_no_record(self, test_session):
        """Test getting EHR when no EHR record exists."""
        session_id = test_session.session_id

        # Create a new patient in session without EHR record
        from app.models.patient import Patient, PatientTrajectory, PatientState
        new_patient = Patient(
            patient_id="pt_002",
            name="Test Patient",
            mrn="MRN999",
            age=50,
            gender="Male",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory()
        )
        test_session.patients["pt_002"] = new_patient

        response = client.get(f"/api/v1/sessions/{session_id}/patients/pt_002/ehr")
        assert response.status_code == 404
        assert "no ehr record found" in response.json()["detail"].lower()

    def test_ehr_visibility_filtering(self, test_session):
        """Test that EHR correctly filters based on visibility rules."""
        session_id = test_session.session_id
        patient_id = "pt_001"
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add always visible note
        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. A",
            author_role="FY1",
            title="Visible Note",
            content={"text": "Always visible"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        # Add note requiring in-person review
        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.PROGRESS,
            timestamp=current_time,
            author="Dr. B",
            author_role="Registrar",
            title="Hidden Note",
            content={"text": "Requires review"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.REVIEW_IN_PERSON
            )
        )

        # Get EHR - should only see 1 note
        response = client.get(f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr")
        assert response.status_code == 200
        data = response.json()
        assert len(data["visible_notes"]) == 1
        assert data["total_notes"] == 2
        assert data["visible_notes"][0]["title"] == "Visible Note"

    def test_ehr_visibility_after_action(self, test_session):
        """Test that EHR reveals more information after actions are taken."""
        session_id = test_session.session_id
        patient_id = "pt_001"
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add note requiring in-person review
        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.NURSING_NOTE,
            timestamp=current_time,
            author="Nurse A",
            author_role="RN",
            title="Nursing Assessment",
            content={"obs": "RR 22, SpO2 92%"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.REVIEW_IN_PERSON
            )
        )

        # Before action - note not visible
        response = client.get(f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr")
        assert response.status_code == 200
        data = response.json()
        assert len(data["visible_notes"]) == 0

        # Perform in-person review action
        action_response = client.post(
            f"/api/v1/sessions/{session_id}/actions/review?patient_id={patient_id}"
        )
        assert action_response.status_code == 200

        # After action - note should be visible
        response = client.get(f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr")
        assert response.status_code == 200
        data = response.json()
        assert len(data["visible_notes"]) == 1
        assert data["visible_notes"][0]["title"] == "Nursing Assessment"


class TestGetVisibilitySummary:
    """Tests for GET /sessions/{session_id}/patients/{patient_id}/ehr/visibility endpoint."""

    def test_get_visibility_summary(self, test_session):
        """Test getting visibility summary."""
        session_id = test_session.session_id
        patient_id = "pt_001"
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add mixed visibility notes
        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. A",
            author_role="FY1",
            title="Visible Note",
            content={"text": "Always visible"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.PROGRESS,
            timestamp=current_time,
            author="Dr. B",
            author_role="Registrar",
            title="Hidden Note",
            content={"text": "Requires action"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.REVIEW_IN_PERSON
            )
        )

        response = client.get(
            f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr/visibility"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["notes"]["total"] == 2
        assert data["notes"]["visible"] == 1
        assert data["notes"]["hidden"] == 1

    def test_visibility_summary_session_not_found(self):
        """Test visibility summary for non-existent session."""
        response = client.get(
            "/api/v1/sessions/invalid_session/patients/pt_001/ehr/visibility"
        )
        assert response.status_code == 404


class TestAddClinicalNote:
    """Tests for POST /sessions/{session_id}/patients/{patient_id}/ehr/notes endpoint."""

    def test_add_clinical_note_success(self, test_session):
        """Test adding a clinical note via API."""
        session_id = test_session.session_id
        patient_id = "pt_001"

        note_data = {
            "note_type": "admission",
            "timestamp": "2024-01-15T20:00:00",
            "author": "Dr. Smith",
            "author_role": "FY1",
            "title": "Admission Clerking",
            "content": {
                "presenting_complaint": "Chest pain",
                "history": "2 hour history of central chest pain"
            },
            "visibility_condition": "always"
        }

        response = client.post(
            f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr/notes",
            json=note_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "note_id" in data
        assert data["message"] == "Clinical note added successfully"
        assert data["is_visible"] is True

        # Verify note was added
        record = ehr_service.get_patient_record(patient_id)
        assert len(record.clinical_notes) == 1

    def test_add_note_with_time_visibility(self, test_session):
        """Test adding a note with time-based visibility."""
        session_id = test_session.session_id
        patient_id = "pt_001"

        note_data = {
            "note_type": "progress",
            "timestamp": "2024-01-15T20:00:00",
            "author": "Dr. Jones",
            "author_role": "Registrar",
            "title": "Progress Note",
            "content": {"update": "Patient stable"},
            "visibility_condition": "time_elapsed",
            "visible_after_time": "2024-01-15T21:00:00"
        }

        response = client.post(
            f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr/notes",
            json=note_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_visible"] is False  # Not visible yet

    def test_add_note_invalid_timestamp(self, test_session):
        """Test adding a note with invalid timestamp format."""
        session_id = test_session.session_id
        patient_id = "pt_001"

        note_data = {
            "note_type": "admission",
            "timestamp": "invalid-timestamp",
            "author": "Dr. Smith",
            "author_role": "FY1",
            "title": "Test Note",
            "content": {"text": "Test"}
        }

        response = client.post(
            f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr/notes",
            json=note_data
        )

        assert response.status_code == 400
        assert "invalid timestamp" in response.json()["detail"].lower()


class TestAddInvestigationResult:
    """Tests for POST /sessions/{session_id}/patients/{patient_id}/ehr/results endpoint."""

    def test_add_investigation_result_success(self, test_session):
        """Test adding an investigation result via API."""
        session_id = test_session.session_id
        patient_id = "pt_001"

        result_data = {
            "investigation_type": "ABG",
            "requested_time": "2024-01-15T20:10:00",
            "resulted_time": "2024-01-15T20:30:00",
            "result_data": {
                "pH": 7.32,
                "pCO2": 7.8,
                "pO2": 8.2
            },
            "interpretation": "Type 2 respiratory failure",
            "abnormal_flags": ["Low pH", "High pCO2"],
            "visibility_condition": "time_elapsed"
        }

        response = client.post(
            f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr/results",
            json=result_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "result_id" in data
        assert data["message"] == "Investigation result added successfully"

        # Verify result was added
        record = ehr_service.get_patient_record(patient_id)
        assert len(record.investigation_results) == 1

    def test_add_result_with_custom_visibility(self, test_session):
        """Test adding a result with custom visibility time."""
        session_id = test_session.session_id
        patient_id = "pt_001"

        result_data = {
            "investigation_type": "CXR",
            "requested_time": "2024-01-15T20:00:00",
            "resulted_time": "2024-01-15T20:30:00",
            "result_data": {"findings": "No acute pathology"},
            "visibility_condition": "time_elapsed",
            "visible_after_time": "2024-01-15T21:00:00"
        }

        response = client.post(
            f"/api/v1/sessions/{session_id}/patients/{patient_id}/ehr/results",
            json=result_data
        )

        assert response.status_code == 201

        # Verify result is not visible yet
        record = ehr_service.get_patient_record(patient_id)
        current_time = datetime(2024, 1, 15, 20, 35, 0)
        record.update_visibility(current_time, [])
        assert len(record.get_visible_results()) == 0


class TestEHRIntegrationWithScenario:
    """Integration tests for EHR with scenario loading."""

    def test_load_scenario_with_ehr_data(self):
        """Test loading a scenario that includes EHR data."""
        # This test would use the simple_test_ehr.json scenario
        # For now, we'll test the basic flow

        session = scenario_loader.create_session_from_scenario("simple_test_001")
        simulation_engine.active_sessions[session.session_id] = session
        patient_id = "pt_001"

        # Manually create EHR for this test
        ehr_service.create_patient_record(
            patient_id=patient_id,
            mrn="MRN12345",
            name="Margaret Thompson",
            age=72,
            gender="Female"
        )

        # Add note with time-based visibility
        current_time = datetime(2024, 1, 15, 20, 0, 0)
        ehr_service.add_clinical_note(
            patient_id=patient_id,
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. Smith",
            author_role="FY1",
            title="Admission Note",
            content={"text": "Initial assessment"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        # Get EHR via API
        response = client.get(
            f"/api/v1/sessions/{session.session_id}/patients/{patient_id}/ehr"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["visible_notes"]) == 1
