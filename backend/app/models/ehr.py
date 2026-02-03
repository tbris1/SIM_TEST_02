"""
Electronic Health Record (EHR) models with progressive revelation.

The EHR system controls what clinical information is visible to the user
and when. This simulates real-world information gathering constraints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from uuid import uuid4


class NoteType(str, Enum):
    """Types of clinical notes in the EHR."""
    ADMISSION = "admission"
    PROGRESS = "progress"
    CONSULTANT_REVIEW = "consultant_review"
    DISCHARGE_SUMMARY = "discharge_summary"
    INVESTIGATION_RESULT = "investigation_result"
    PROCEDURE_NOTE = "procedure_note"
    NURSING_NOTE = "nursing_note"


class VisibilityCondition(str, Enum):
    """Conditions that trigger data visibility."""
    ALWAYS = "always"  # Always visible
    TIME_ELAPSED = "time_elapsed"  # Visible after specific time
    ACTION_TAKEN = "action_taken"  # Visible after specific action
    REVIEW_IN_PERSON = "review_in_person"  # Visible after in-person review
    INVESTIGATION_ORDERED = "investigation_ordered"  # Visible after ordering investigation
    EHR_REVIEWED = "ehr_reviewed"  # Visible after reviewing EHR


class VisibilityRule(BaseModel):
    """
    Rules that control when clinical data becomes visible.
    Simulates the progressive discovery of information in clinical practice.
    """
    rule_id: str = Field(default_factory=lambda: f"vis_{uuid4().hex[:8]}")

    # Visibility condition
    condition: VisibilityCondition

    # Time-based visibility
    visible_after_time: Optional[datetime] = None

    # Action-based visibility
    required_action: Optional[str] = None  # e.g., "review_in_person", "investigate"

    # Patient context
    patient_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "vis_abc123",
                "condition": "review_in_person",
                "required_action": "review_in_person",
                "patient_id": "pt_001"
            }
        }


class ClinicalNote(BaseModel):
    """
    A clinical note in the EHR.
    Can be progress notes, admission notes, consultant reviews, etc.
    """
    note_id: str = Field(default_factory=lambda: f"note_{uuid4().hex[:8]}")

    # Note metadata
    note_type: NoteType
    timestamp: datetime
    author: str
    author_role: str  # e.g., "FY1", "Registrar", "Consultant"

    # Content
    title: str
    content: Union[str, Dict[str, Any]]  # Can be string (new format) or structured dict (legacy)

    # Visibility control
    visibility_rule: Optional[VisibilityRule] = None
    is_visible: bool = False  # Dynamically computed based on visibility rules

    class Config:
        json_schema_extra = {
            "example": {
                "note_id": "note_abc123",
                "note_type": "admission",
                "timestamp": "2024-01-15T14:30:00",
                "author": "Dr. James Wilson",
                "author_role": "FY1",
                "title": "Admission Clerking",
                "content": {
                    "presenting_complaint": "Shortness of breath",
                    "history_presenting_complaint": "3 day history of increasing SOB...",
                    "past_medical_history": ["COPD", "Hypertension"],
                    "medications": ["Salbutamol inhaler", "Amlodipine 5mg"],
                    "examination": {
                        "obs": "RR 24, SpO2 92% on 2L, HR 95, BP 145/85",
                        "respiratory": "Reduced air entry bilateral bases"
                    },
                    "plan": ["CXR", "ABG", "Nebulizers"]
                },
                "visibility_rule": {
                    "condition": "always"
                }
            }
        }


class InvestigationResult(BaseModel):
    """
    An investigation result in the EHR.
    Could be blood tests, imaging, ABG, etc.
    """
    result_id: str = Field(default_factory=lambda: f"result_{uuid4().hex[:8]}")

    # Investigation metadata
    investigation_type: str  # e.g., "CXR", "ABG", "FBC"
    requested_time: datetime
    resulted_time: Optional[datetime] = None

    # Content
    result_data: Dict[str, Any]  # Structured result data
    interpretation: Optional[str] = None
    abnormal_flags: List[str] = Field(default_factory=list)

    # Visibility control
    visibility_rule: Optional[VisibilityRule] = None
    is_visible: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "result_id": "result_abc123",
                "investigation_type": "ABG",
                "requested_time": "2024-01-15T20:10:00",
                "resulted_time": "2024-01-15T20:30:00",
                "result_data": {
                    "pH": 7.32,
                    "pCO2": 7.8,
                    "pO2": 8.2,
                    "HCO3": 28
                },
                "interpretation": "Type 2 respiratory failure",
                "abnormal_flags": ["Low pH", "High pCO2"],
                "visibility_rule": {
                    "condition": "time_elapsed",
                    "visible_after_time": "2024-01-15T20:30:00"
                }
            }
        }


class PatientRecord(BaseModel):
    """
    Complete EHR record for a patient.
    Contains all clinical notes, investigation results, and visibility rules.
    """
    patient_id: str
    mrn: str

    # Demographics (duplicated from Patient model for convenience)
    name: str
    age: int
    gender: str

    # Clinical data
    clinical_notes: List[ClinicalNote] = Field(default_factory=list)
    investigation_results: List[InvestigationResult] = Field(default_factory=list)

    # Summary data (always visible)
    allergies: List[str] = Field(default_factory=list)
    active_diagnoses: List[str] = Field(default_factory=list)
    current_medications: List[Dict[str, str]] = Field(default_factory=list)

    # Last updated
    last_updated: datetime = Field(default_factory=datetime.now)

    def get_visible_notes(self) -> List[ClinicalNote]:
        """Get all currently visible clinical notes."""
        return [note for note in self.clinical_notes if note.is_visible]

    def get_visible_results(self) -> List[InvestigationResult]:
        """Get all currently visible investigation results."""
        return [result for result in self.investigation_results if result.is_visible]

    def update_visibility(
        self,
        current_time: datetime,
        actions_taken: List[str]
    ) -> Dict[str, int]:
        """
        Update visibility of all notes and results based on current conditions.

        Args:
            current_time: Current simulation time
            actions_taken: List of action types taken on this patient

        Returns:
            Dictionary with counts of newly visible items
        """
        newly_visible_notes = 0
        newly_visible_results = 0

        # Update clinical notes visibility
        for note in self.clinical_notes:
            if not note.is_visible and self._check_visibility(
                note.visibility_rule, current_time, actions_taken
            ):
                note.is_visible = True
                newly_visible_notes += 1

        # Update investigation results visibility
        for result in self.investigation_results:
            if not result.is_visible and self._check_visibility(
                result.visibility_rule, current_time, actions_taken
            ):
                result.is_visible = True
                newly_visible_results += 1

        return {
            "newly_visible_notes": newly_visible_notes,
            "newly_visible_results": newly_visible_results
        }

    def _check_visibility(
        self,
        rule: Optional[VisibilityRule],
        current_time: datetime,
        actions_taken: List[str]
    ) -> bool:
        """Check if a visibility rule is satisfied."""
        if not rule:
            return True  # No rule = always visible

        if rule.condition == VisibilityCondition.ALWAYS:
            return True

        elif rule.condition == VisibilityCondition.TIME_ELAPSED:
            if rule.visible_after_time and current_time >= rule.visible_after_time:
                return True

        elif rule.condition == VisibilityCondition.ACTION_TAKEN:
            if rule.required_action and rule.required_action in actions_taken:
                return True

        elif rule.condition == VisibilityCondition.REVIEW_IN_PERSON:
            if "review_in_person" in actions_taken:
                return True

        elif rule.condition == VisibilityCondition.INVESTIGATION_ORDERED:
            if "investigate" in actions_taken:
                return True

        elif rule.condition == VisibilityCondition.EHR_REVIEWED:
            if "view_ehr" in actions_taken:
                return True

        return False

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "pt_001",
                "mrn": "MRN12345",
                "name": "Margaret Thompson",
                "age": 72,
                "gender": "Female",
                "allergies": ["Penicillin"],
                "active_diagnoses": ["COPD", "Hypertension"],
                "current_medications": [
                    {"name": "Salbutamol inhaler", "dose": "2 puffs PRN"},
                    {"name": "Amlodipine", "dose": "5mg OD"}
                ],
                "clinical_notes": [],
                "investigation_results": []
            }
        }


class PatientRecordView(BaseModel):
    """
    Filtered view of a patient record showing only visible information.
    This is what gets returned to the API consumer.
    """
    patient_id: str
    mrn: str
    name: str
    age: int
    gender: str

    # Always visible summary
    allergies: List[str]
    active_diagnoses: List[str]
    current_medications: List[Dict[str, str]]

    # Filtered clinical data
    visible_notes: List[ClinicalNote]
    visible_results: List[InvestigationResult]

    # Metadata
    total_notes: int
    total_results: int
    last_updated: str

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "pt_001",
                "mrn": "MRN12345",
                "name": "Margaret Thompson",
                "age": 72,
                "gender": "Female",
                "allergies": ["Penicillin"],
                "active_diagnoses": ["COPD", "Hypertension"],
                "current_medications": [
                    {"name": "Salbutamol inhaler", "dose": "2 puffs PRN"}
                ],
                "visible_notes": [],
                "visible_results": [],
                "total_notes": 5,
                "total_results": 3,
                "last_updated": "2024-01-15T20:30:00"
            }
        }
