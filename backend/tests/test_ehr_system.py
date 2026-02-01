"""
Unit tests for EHR system with progressive revelation.
"""

import pytest
from datetime import datetime, timedelta

from app.models.ehr import (
    PatientRecord,
    ClinicalNote,
    InvestigationResult,
    VisibilityRule,
    VisibilityCondition,
    NoteType
)
from app.services.ehr_service import EHRService


@pytest.fixture
def ehr_service():
    """Create a fresh EHR service for each test."""
    service = EHRService()
    service.clear_all_records()
    return service


@pytest.fixture
def sample_patient_record(ehr_service):
    """Create a sample patient EHR record."""
    return ehr_service.create_patient_record(
        patient_id="pt_001",
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


class TestPatientRecord:
    """Tests for PatientRecord model."""

    def test_create_patient_record(self, ehr_service):
        """Test creating a new patient EHR record."""
        record = ehr_service.create_patient_record(
            patient_id="pt_001",
            mrn="MRN12345",
            name="John Doe",
            age=45,
            gender="Male"
        )

        assert record.patient_id == "pt_001"
        assert record.mrn == "MRN12345"
        assert record.name == "John Doe"
        assert record.age == 45
        assert record.gender == "Male"
        assert len(record.clinical_notes) == 0
        assert len(record.investigation_results) == 0

    def test_get_patient_record(self, ehr_service, sample_patient_record):
        """Test retrieving a patient record."""
        retrieved = ehr_service.get_patient_record("pt_001")

        assert retrieved is not None
        assert retrieved.patient_id == "pt_001"
        assert retrieved.name == "Margaret Thompson"

    def test_get_nonexistent_patient(self, ehr_service):
        """Test retrieving a non-existent patient record."""
        retrieved = ehr_service.get_patient_record("pt_999")
        assert retrieved is None


class TestClinicalNotes:
    """Tests for clinical note management."""

    def test_add_always_visible_note(self, ehr_service, sample_patient_record):
        """Test adding a note that's always visible."""
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        note = ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. Smith",
            author_role="FY1",
            title="Admission Note",
            content={"presenting_complaint": "Chest pain"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        assert note is not None
        assert note.is_visible is True
        assert note.title == "Admission Note"

        # Verify it's in the record
        record = ehr_service.get_patient_record("pt_001")
        assert len(record.clinical_notes) == 1
        assert len(record.get_visible_notes()) == 1

    def test_add_time_based_note(self, ehr_service, sample_patient_record):
        """Test adding a note with time-based visibility."""
        current_time = datetime(2024, 1, 15, 20, 0, 0)
        visible_after = datetime(2024, 1, 15, 20, 30, 0)

        note = ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.PROGRESS,
            timestamp=current_time,
            author="Dr. Jones",
            author_role="Registrar",
            title="Progress Note",
            content={"update": "Patient stable"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.TIME_ELAPSED,
                visible_after_time=visible_after
            )
        )

        assert note is not None
        assert note.is_visible is False  # Not visible yet

        # Check visibility before the time
        record = ehr_service.get_patient_record("pt_001")
        record.update_visibility(current_time, [])
        assert len(record.get_visible_notes()) == 0

        # Check visibility after the time
        later_time = datetime(2024, 1, 15, 20, 35, 0)
        record.update_visibility(later_time, [])
        assert len(record.get_visible_notes()) == 1

    def test_add_action_based_note(self, ehr_service, sample_patient_record):
        """Test adding a note with action-based visibility."""
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        note = ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.NURSING_NOTE,
            timestamp=current_time,
            author="Nurse Smith",
            author_role="RN",
            title="Nursing Assessment",
            content={"obs": "RR 22, SpO2 92%"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.REVIEW_IN_PERSON,
                required_action="review_in_person"
            )
        )

        assert note.is_visible is False

        # Check visibility without action
        record = ehr_service.get_patient_record("pt_001")
        record.update_visibility(current_time, [])
        assert len(record.get_visible_notes()) == 0

        # Check visibility after in-person review
        record.update_visibility(current_time, ["review_in_person"])
        assert len(record.get_visible_notes()) == 1


class TestInvestigationResults:
    """Tests for investigation result management."""

    def test_add_investigation_result(self, ehr_service, sample_patient_record):
        """Test adding an investigation result."""
        requested_time = datetime(2024, 1, 15, 20, 10, 0)
        resulted_time = datetime(2024, 1, 15, 20, 30, 0)

        result = ehr_service.add_investigation_result(
            patient_id="pt_001",
            investigation_type="ABG",
            requested_time=requested_time,
            resulted_time=resulted_time,
            result_data={"pH": 7.32, "pCO2": 7.8},
            interpretation="Type 2 respiratory failure",
            abnormal_flags=["Low pH", "High pCO2"]
        )

        assert result is not None
        assert result.investigation_type == "ABG"
        assert result.interpretation == "Type 2 respiratory failure"

        # Verify it's in the record
        record = ehr_service.get_patient_record("pt_001")
        assert len(record.investigation_results) == 1

    def test_investigation_result_time_visibility(self, ehr_service, sample_patient_record):
        """Test that investigation results become visible after resulted time."""
        requested_time = datetime(2024, 1, 15, 20, 10, 0)
        resulted_time = datetime(2024, 1, 15, 20, 30, 0)

        ehr_service.add_investigation_result(
            patient_id="pt_001",
            investigation_type="CXR",
            requested_time=requested_time,
            resulted_time=resulted_time,
            result_data={"findings": "No acute pathology"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.TIME_ELAPSED,
                visible_after_time=resulted_time
            )
        )

        record = ehr_service.get_patient_record("pt_001")

        # Before resulted time
        before_time = datetime(2024, 1, 15, 20, 20, 0)
        record.update_visibility(before_time, [])
        assert len(record.get_visible_results()) == 0

        # After resulted time
        after_time = datetime(2024, 1, 15, 20, 35, 0)
        record.update_visibility(after_time, [])
        assert len(record.get_visible_results()) == 1


class TestProgressiveRevelation:
    """Tests for progressive revelation functionality."""

    def test_visibility_updates_over_time(self, ehr_service, sample_patient_record):
        """Test that visibility correctly updates as time progresses."""
        base_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add notes with different visibility times
        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.ADMISSION,
            timestamp=base_time,
            author="Dr. A",
            author_role="FY1",
            title="Note 1",
            content={"text": "Always visible"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.PROGRESS,
            timestamp=base_time + timedelta(minutes=30),
            author="Dr. B",
            author_role="Registrar",
            title="Note 2",
            content={"text": "Visible at 20:30"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.TIME_ELAPSED,
                visible_after_time=base_time + timedelta(minutes=30)
            )
        )

        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.PROGRESS,
            timestamp=base_time + timedelta(hours=1),
            author="Dr. C",
            author_role="Consultant",
            title="Note 3",
            content={"text": "Visible at 21:00"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.TIME_ELAPSED,
                visible_after_time=base_time + timedelta(hours=1)
            )
        )

        record = ehr_service.get_patient_record("pt_001")

        # At 20:00 - only 1 note visible
        record.update_visibility(base_time, [])
        assert len(record.get_visible_notes()) == 1

        # At 20:30 - 2 notes visible
        record.update_visibility(base_time + timedelta(minutes=30), [])
        assert len(record.get_visible_notes()) == 2

        # At 21:00 - all 3 notes visible
        record.update_visibility(base_time + timedelta(hours=1), [])
        assert len(record.get_visible_notes()) == 3

    def test_visibility_updates_with_actions(self, ehr_service, sample_patient_record):
        """Test that visibility correctly updates when actions are taken."""
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add notes requiring different actions
        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.NURSING_NOTE,
            timestamp=current_time,
            author="Nurse A",
            author_role="RN",
            title="Nursing Note",
            content={"text": "Visible after in-person review"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.REVIEW_IN_PERSON
            )
        )

        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.CONSULTANT_REVIEW,
            timestamp=current_time,
            author="Dr. Consultant",
            author_role="Consultant",
            title="Consultant Review",
            content={"text": "Visible after EHR reviewed"},
            visibility_rule=VisibilityRule(
                condition=VisibilityCondition.EHR_REVIEWED
            )
        )

        record = ehr_service.get_patient_record("pt_001")

        # No actions taken - no notes visible
        record.update_visibility(current_time, [])
        assert len(record.get_visible_notes()) == 0

        # After in-person review - 1 note visible
        record.update_visibility(current_time, ["review_in_person"])
        assert len(record.get_visible_notes()) == 1

        # After viewing EHR - both notes visible
        record.update_visibility(current_time, ["review_in_person", "view_ehr"])
        assert len(record.get_visible_notes()) == 2

    def test_get_patient_record_view(self, ehr_service, sample_patient_record):
        """Test getting a filtered patient record view."""
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add mixed visibility content
        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. A",
            author_role="FY1",
            title="Visible Note",
            content={"text": "Always visible"},
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

        ehr_service.add_clinical_note(
            patient_id="pt_001",
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

        # Get view without actions
        view = ehr_service.get_patient_record_view("pt_001", current_time, [])

        assert view is not None
        assert view.patient_id == "pt_001"
        assert len(view.visible_notes) == 1
        assert view.total_notes == 2
        assert view.visible_notes[0].title == "Visible Note"

    def test_visibility_summary(self, ehr_service, sample_patient_record):
        """Test getting visibility statistics."""
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        # Add 2 visible and 2 hidden notes
        for i in range(2):
            ehr_service.add_clinical_note(
                patient_id="pt_001",
                note_type=NoteType.ADMISSION,
                timestamp=current_time,
                author=f"Dr. {i}",
                author_role="FY1",
                title=f"Visible Note {i}",
                content={"text": "Always visible"},
                visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
            )

        for i in range(2):
            ehr_service.add_clinical_note(
                patient_id="pt_001",
                note_type=NoteType.PROGRESS,
                timestamp=current_time,
                author=f"Dr. {i+2}",
                author_role="Registrar",
                title=f"Hidden Note {i}",
                content={"text": "Requires action"},
                visibility_rule=VisibilityRule(
                    condition=VisibilityCondition.REVIEW_IN_PERSON
                )
            )

        # Update visibility
        record = ehr_service.get_patient_record("pt_001")
        record.update_visibility(current_time, [])

        # Get summary
        summary = ehr_service.get_visibility_summary("pt_001")

        assert summary is not None
        assert summary["notes"]["total"] == 4
        assert summary["notes"]["visible"] == 2
        assert summary["notes"]["hidden"] == 2


class TestEHRIntegration:
    """Integration tests for EHR system."""

    def test_multiple_patients(self, ehr_service):
        """Test managing EHR records for multiple patients."""
        # Create two patients
        ehr_service.create_patient_record(
            patient_id="pt_001",
            mrn="MRN001",
            name="Patient One",
            age=50,
            gender="Male"
        )

        ehr_service.create_patient_record(
            patient_id="pt_002",
            mrn="MRN002",
            name="Patient Two",
            age=60,
            gender="Female"
        )

        # Add notes to each
        current_time = datetime(2024, 1, 15, 20, 0, 0)

        ehr_service.add_clinical_note(
            patient_id="pt_001",
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. A",
            author_role="FY1",
            title="Patient 1 Note",
            content={"text": "Note for patient 1"}
        )

        ehr_service.add_clinical_note(
            patient_id="pt_002",
            note_type=NoteType.ADMISSION,
            timestamp=current_time,
            author="Dr. B",
            author_role="FY1",
            title="Patient 2 Note",
            content={"text": "Note for patient 2"}
        )

        # Verify separation
        patient_ids = ehr_service.list_patient_records()
        assert len(patient_ids) == 2

        record1 = ehr_service.get_patient_record("pt_001")
        record2 = ehr_service.get_patient_record("pt_002")

        assert len(record1.clinical_notes) == 1
        assert len(record2.clinical_notes) == 1
        assert record1.clinical_notes[0].title == "Patient 1 Note"
        assert record2.clinical_notes[0].title == "Patient 2 Note"
