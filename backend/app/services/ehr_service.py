"""
Service for managing Electronic Health Records with progressive revelation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from ..models.ehr import (
    PatientRecord,
    PatientRecordView,
    ClinicalNote,
    InvestigationResult,
    VisibilityRule,
    VisibilityCondition,
    NoteType
)


class EHRService:
    """
    Service for managing patient EHR records.
    Handles storage, retrieval, and visibility filtering of clinical data.
    """

    def __init__(self):
        """Initialize the EHR service with empty storage."""
        self.patient_records: Dict[str, PatientRecord] = {}

    def create_patient_record(
        self,
        patient_id: str,
        mrn: str,
        name: str,
        age: int,
        gender: str,
        allergies: Optional[List[str]] = None,
        active_diagnoses: Optional[List[str]] = None,
        current_medications: Optional[List[Dict[str, str]]] = None,
    ) -> PatientRecord:
        """
        Create a new patient EHR record.

        Args:
            patient_id: Unique patient identifier
            mrn: Medical record number
            name: Patient name
            age: Patient age
            gender: Patient gender
            allergies: List of allergies
            active_diagnoses: List of active diagnoses
            current_medications: List of current medications

        Returns:
            Created PatientRecord
        """
        record = PatientRecord(
            patient_id=patient_id,
            mrn=mrn,
            name=name,
            age=age,
            gender=gender,
            allergies=allergies or [],
            active_diagnoses=active_diagnoses or [],
            current_medications=current_medications or [],
        )

        self.patient_records[patient_id] = record
        return record

    def get_patient_record(self, patient_id: str) -> Optional[PatientRecord]:
        """
        Get a patient's full EHR record.

        Args:
            patient_id: Patient identifier

        Returns:
            PatientRecord if found, None otherwise
        """
        return self.patient_records.get(patient_id)

    def add_clinical_note(
        self,
        patient_id: str,
        note_type: NoteType,
        timestamp: datetime,
        author: str,
        author_role: str,
        title: str,
        content: Dict[str, Any],
        visibility_rule: Optional[VisibilityRule] = None,
    ) -> Optional[ClinicalNote]:
        """
        Add a clinical note to a patient's EHR.

        Args:
            patient_id: Patient identifier
            note_type: Type of note
            timestamp: When the note was written
            author: Author name
            author_role: Author's role
            title: Note title
            content: Structured note content
            visibility_rule: Rule controlling visibility

        Returns:
            Created ClinicalNote if successful, None if patient not found
        """
        record = self.get_patient_record(patient_id)
        if not record:
            return None

        # Default to always visible if no rule specified
        if not visibility_rule:
            visibility_rule = VisibilityRule(condition=VisibilityCondition.ALWAYS)

        note = ClinicalNote(
            note_type=note_type,
            timestamp=timestamp,
            author=author,
            author_role=author_role,
            title=title,
            content=content,
            visibility_rule=visibility_rule,
            is_visible=(visibility_rule.condition == VisibilityCondition.ALWAYS)
        )

        record.clinical_notes.append(note)
        record.last_updated = datetime.now()

        return note

    def add_investigation_result(
        self,
        patient_id: str,
        investigation_type: str,
        requested_time: datetime,
        resulted_time: datetime,
        result_data: Dict[str, Any],
        interpretation: Optional[str] = None,
        abnormal_flags: Optional[List[str]] = None,
        visibility_rule: Optional[VisibilityRule] = None,
    ) -> Optional[InvestigationResult]:
        """
        Add an investigation result to a patient's EHR.

        Args:
            patient_id: Patient identifier
            investigation_type: Type of investigation
            requested_time: When investigation was requested
            resulted_time: When results became available
            result_data: Structured result data
            interpretation: Clinical interpretation
            abnormal_flags: List of abnormal flags
            visibility_rule: Rule controlling visibility

        Returns:
            Created InvestigationResult if successful, None if patient not found
        """
        record = self.get_patient_record(patient_id)
        if not record:
            return None

        # Default to time-based visibility (available when resulted)
        if not visibility_rule:
            visibility_rule = VisibilityRule(
                condition=VisibilityCondition.TIME_ELAPSED,
                visible_after_time=resulted_time
            )

        result = InvestigationResult(
            investigation_type=investigation_type,
            requested_time=requested_time,
            resulted_time=resulted_time,
            result_data=result_data,
            interpretation=interpretation,
            abnormal_flags=abnormal_flags or [],
            visibility_rule=visibility_rule,
            is_visible=False  # Will be updated by update_visibility
        )

        record.investigation_results.append(result)
        record.last_updated = datetime.now()

        return result

    def update_visibility(
        self,
        patient_id: str,
        current_time: datetime,
        actions_taken: List[str]
    ) -> Optional[Dict[str, int]]:
        """
        Update visibility of all EHR data for a patient based on current conditions.

        Args:
            patient_id: Patient identifier
            current_time: Current simulation time
            actions_taken: List of action types taken on this patient

        Returns:
            Dictionary with counts of newly visible items, or None if patient not found
        """
        record = self.get_patient_record(patient_id)
        if not record:
            return None

        return record.update_visibility(current_time, actions_taken)

    def get_patient_record_view(
        self,
        patient_id: str,
        current_time: datetime,
        actions_taken: List[str]
    ) -> Optional[PatientRecordView]:
        """
        Get a filtered view of a patient's EHR showing only visible information.

        This method:
        1. Updates visibility based on current conditions
        2. Filters to show only visible data
        3. Returns a view object for API consumption

        Args:
            patient_id: Patient identifier
            current_time: Current simulation time
            actions_taken: List of action types taken on this patient

        Returns:
            PatientRecordView if patient found, None otherwise
        """
        record = self.get_patient_record(patient_id)
        if not record:
            return None

        # Update visibility first
        record.update_visibility(current_time, actions_taken)

        # Create filtered view
        view = PatientRecordView(
            patient_id=record.patient_id,
            mrn=record.mrn,
            name=record.name,
            age=record.age,
            gender=record.gender,
            allergies=record.allergies,
            active_diagnoses=record.active_diagnoses,
            current_medications=record.current_medications,
            visible_notes=record.get_visible_notes(),
            visible_results=record.get_visible_results(),
            total_notes=len(record.clinical_notes),
            total_results=len(record.investigation_results),
            last_updated=record.last_updated.isoformat()
        )

        return view

    def list_patient_records(self) -> List[str]:
        """
        List all patient IDs with EHR records.

        Returns:
            List of patient IDs
        """
        return list(self.patient_records.keys())

    def has_record(self, patient_id: str) -> bool:
        """
        Check if a patient record exists.

        Args:
            patient_id: Patient identifier

        Returns:
            True if record exists, False otherwise
        """
        return patient_id in self.patient_records

    def get_visibility_summary(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of what's visible vs. hidden for a patient.

        Args:
            patient_id: Patient identifier

        Returns:
            Dictionary with visibility statistics, or None if patient not found
        """
        record = self.get_patient_record(patient_id)
        if not record:
            return None

        visible_notes = record.get_visible_notes()
        visible_results = record.get_visible_results()

        return {
            "patient_id": patient_id,
            "notes": {
                "total": len(record.clinical_notes),
                "visible": len(visible_notes),
                "hidden": len(record.clinical_notes) - len(visible_notes)
            },
            "results": {
                "total": len(record.investigation_results),
                "visible": len(visible_results),
                "hidden": len(record.investigation_results) - len(visible_results)
            }
        }

    def clear_all_records(self):
        """Clear all patient records. Useful for testing."""
        self.patient_records.clear()


# Global EHR service instance
ehr_service = EHRService()
