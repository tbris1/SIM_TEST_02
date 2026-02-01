"""
API endpoints for Electronic Health Record (EHR) access.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

from ..services.ehr_service import ehr_service
from ..services.simulation_engine import simulation_engine
from ..models.ehr import NoteType, VisibilityCondition

router = APIRouter()


# Request/Response Models
class AddClinicalNoteRequest(BaseModel):
    """Request to add a clinical note to a patient's EHR."""

    note_type: NoteType = Field(..., description="Type of clinical note")
    timestamp: str = Field(..., description="When the note was written (ISO format)")
    author: str = Field(..., description="Author name")
    author_role: str = Field(..., description="Author's clinical role")
    title: str = Field(..., description="Note title")
    content: Dict[str, Any] = Field(..., description="Structured note content")
    visibility_condition: Optional[VisibilityCondition] = Field(
        None,
        description="Visibility condition (defaults to always visible if not specified)"
    )
    required_action: Optional[str] = Field(
        None,
        description="Required action for visibility (if condition is action_taken)"
    )
    visible_after_time: Optional[str] = Field(
        None,
        description="Time when note becomes visible (ISO format, if condition is time_elapsed)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "note_type": "admission",
                "timestamp": "2024-01-15T14:30:00",
                "author": "Dr. James Wilson",
                "author_role": "FY1",
                "title": "Admission Clerking",
                "content": {
                    "presenting_complaint": "Shortness of breath",
                    "history_presenting_complaint": "3 day history of increasing SOB...",
                    "past_medical_history": ["COPD", "Hypertension"],
                    "medications": ["Salbutamol inhaler", "Amlodipine 5mg"]
                },
                "visibility_condition": "always"
            }
        }


class AddInvestigationResultRequest(BaseModel):
    """Request to add an investigation result to a patient's EHR."""

    investigation_type: str = Field(..., description="Type of investigation (e.g., ABG, CXR)")
    requested_time: str = Field(..., description="When investigation was requested (ISO format)")
    resulted_time: str = Field(..., description="When result became available (ISO format)")
    result_data: Dict[str, Any] = Field(..., description="Structured result data")
    interpretation: Optional[str] = Field(None, description="Clinical interpretation")
    abnormal_flags: Optional[List[str]] = Field(None, description="List of abnormal flags")
    visibility_condition: Optional[VisibilityCondition] = Field(
        None,
        description="Visibility condition (defaults to time_elapsed if not specified)"
    )
    visible_after_time: Optional[str] = Field(
        None,
        description="Time when result becomes visible (defaults to resulted_time)"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
                "visibility_condition": "time_elapsed"
            }
        }


class OrderInvestigationRequest(BaseModel):
    """Request to order an investigation for a patient."""

    investigation_type: str = Field(..., description="Type of investigation (ABG, FBC, U&E, CXR, etc.)")
    urgency: str = Field("routine", description="Urgency level: routine, urgent, emergency")
    custom_turnaround_minutes: Optional[int] = Field(
        None,
        description="Custom turnaround time in minutes (uses default if not specified)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "investigation_type": "ABG",
                "urgency": "urgent",
                "custom_turnaround_minutes": 20
            }
        }


class OrderInvestigationResponse(BaseModel):
    """Response from ordering an investigation."""

    message: str
    result_id: str
    investigation_type: str
    requested_time: str
    expected_result_time: str
    turnaround_minutes: int


class EHRRecordResponse(BaseModel):
    """Response containing filtered EHR record view."""

    patient_id: str
    mrn: str
    name: str
    age: int
    gender: str
    allergies: List[str]
    active_diagnoses: List[str]
    current_medications: List[Dict[str, str]]
    visible_notes: List[Dict[str, Any]]
    visible_results: List[Dict[str, Any]]
    total_notes: int
    total_results: int
    last_updated: str


class VisibilitySummaryResponse(BaseModel):
    """Response containing visibility statistics."""

    patient_id: str
    notes: Dict[str, int]
    results: Dict[str, int]


# Endpoints
@router.get("/sessions/{session_id}/patients/{patient_id}/ehr", response_model=EHRRecordResponse)
async def get_patient_ehr(session_id: str, patient_id: str):
    """
    Get a patient's EHR record with filtered visibility.

    Only shows clinical notes and investigation results that are currently visible
    based on the time elapsed and actions taken in the simulation.

    This endpoint demonstrates progressive revelation - as the simulation progresses
    and the user takes actions, more information becomes visible.
    """
    # Get the simulation session
    session = simulation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Check if patient exists in session
    if patient_id not in session.patients:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found in session"
        )

    # Check if EHR record exists
    if not ehr_service.has_record(patient_id):
        raise HTTPException(
            status_code=404,
            detail=f"No EHR record found for patient {patient_id}"
        )

    # Get patient actions taken
    patient = session.patients[patient_id]
    actions_taken = [action["action_type"] for action in patient.actions_taken]

    # Get current simulation time
    current_time = session.clock.get_current_time()

    # Get filtered EHR view
    record_view = ehr_service.get_patient_record_view(
        patient_id,
        current_time,
        actions_taken
    )

    if not record_view:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate EHR view for patient {patient_id}"
        )

    # Convert to dictionary for JSON serialization
    return {
        "patient_id": record_view.patient_id,
        "mrn": record_view.mrn,
        "name": record_view.name,
        "age": record_view.age,
        "gender": record_view.gender,
        "allergies": record_view.allergies,
        "active_diagnoses": record_view.active_diagnoses,
        "current_medications": record_view.current_medications,
        "visible_notes": [note.model_dump() for note in record_view.visible_notes],
        "visible_results": [result.model_dump() for result in record_view.visible_results],
        "total_notes": record_view.total_notes,
        "total_results": record_view.total_results,
        "last_updated": record_view.last_updated
    }


@router.get("/sessions/{session_id}/patients/{patient_id}/ehr/visibility", response_model=VisibilitySummaryResponse)
async def get_visibility_summary(session_id: str, patient_id: str):
    """
    Get visibility statistics for a patient's EHR.

    Shows how many notes and results are visible vs. hidden.
    Useful for debugging and understanding progressive revelation.
    """
    # Get the simulation session
    session = simulation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Check if patient exists in session
    if patient_id not in session.patients:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found in session"
        )

    # Check if EHR record exists
    if not ehr_service.has_record(patient_id):
        raise HTTPException(
            status_code=404,
            detail=f"No EHR record found for patient {patient_id}"
        )

    # Get patient actions and current time
    patient = session.patients[patient_id]
    actions_taken = [action["action_type"] for action in patient.actions_taken]
    current_time = session.clock.get_current_time()

    # Update visibility first
    ehr_service.update_visibility(patient_id, current_time, actions_taken)

    # Get visibility summary
    summary = ehr_service.get_visibility_summary(patient_id)

    if not summary:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get visibility summary for patient {patient_id}"
        )

    return summary


@router.post("/sessions/{session_id}/patients/{patient_id}/ehr/notes", status_code=201)
async def add_clinical_note(
    session_id: str,
    patient_id: str,
    request: AddClinicalNoteRequest
):
    """
    Add a clinical note to a patient's EHR.

    This endpoint is primarily for testing and scenario setup.
    In production, notes would be loaded from scenario JSON files.
    """
    # Get the simulation session
    session = simulation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Check if patient exists in session
    if patient_id not in session.patients:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found in session"
        )

    # Check if EHR record exists
    if not ehr_service.has_record(patient_id):
        raise HTTPException(
            status_code=404,
            detail=f"No EHR record found for patient {patient_id}. Create one first."
        )

    # Parse timestamp
    try:
        timestamp = datetime.fromisoformat(request.timestamp)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timestamp format: {request.timestamp}"
        )

    # Create visibility rule
    from ..models.ehr import VisibilityRule

    visibility_rule = None
    if request.visibility_condition:
        rule_kwargs = {
            "condition": request.visibility_condition,
            "patient_id": patient_id
        }

        if request.required_action:
            rule_kwargs["required_action"] = request.required_action

        if request.visible_after_time:
            try:
                rule_kwargs["visible_after_time"] = datetime.fromisoformat(request.visible_after_time)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid visible_after_time format: {request.visible_after_time}"
                )

        visibility_rule = VisibilityRule(**rule_kwargs)

    # Add note
    note = ehr_service.add_clinical_note(
        patient_id=patient_id,
        note_type=request.note_type,
        timestamp=timestamp,
        author=request.author,
        author_role=request.author_role,
        title=request.title,
        content=request.content,
        visibility_rule=visibility_rule
    )

    if not note:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add clinical note for patient {patient_id}"
        )

    return {
        "message": "Clinical note added successfully",
        "note_id": note.note_id,
        "is_visible": note.is_visible
    }


@router.post("/sessions/{session_id}/patients/{patient_id}/ehr/results", status_code=201)
async def add_investigation_result(
    session_id: str,
    patient_id: str,
    request: AddInvestigationResultRequest
):
    """
    Add an investigation result to a patient's EHR.

    This endpoint is primarily for testing and scenario setup.
    In production, results would be loaded from scenario JSON files or triggered by events.
    """
    # Get the simulation session
    session = simulation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Check if patient exists in session
    if patient_id not in session.patients:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found in session"
        )

    # Check if EHR record exists
    if not ehr_service.has_record(patient_id):
        raise HTTPException(
            status_code=404,
            detail=f"No EHR record found for patient {patient_id}. Create one first."
        )

    # Parse timestamps
    try:
        requested_time = datetime.fromisoformat(request.requested_time)
        resulted_time = datetime.fromisoformat(request.resulted_time)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timestamp format: {str(e)}"
        )

    # Create visibility rule
    from ..models.ehr import VisibilityRule

    visibility_rule = None
    if request.visibility_condition:
        rule_kwargs = {
            "condition": request.visibility_condition,
            "patient_id": patient_id
        }

        if request.visible_after_time:
            try:
                rule_kwargs["visible_after_time"] = datetime.fromisoformat(request.visible_after_time)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid visible_after_time format: {request.visible_after_time}"
                )
        else:
            # Default to resulted_time
            rule_kwargs["visible_after_time"] = resulted_time

        visibility_rule = VisibilityRule(**rule_kwargs)

    # Add result
    result = ehr_service.add_investigation_result(
        patient_id=patient_id,
        investigation_type=request.investigation_type,
        requested_time=requested_time,
        resulted_time=resulted_time,
        result_data=request.result_data,
        interpretation=request.interpretation,
        abnormal_flags=request.abnormal_flags,
        visibility_rule=visibility_rule
    )

    if not result:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add investigation result for patient {patient_id}"
        )

    return {
        "message": "Investigation result added successfully",
        "result_id": result.result_id,
        "is_visible": result.is_visible
    }


@router.post("/sessions/{session_id}/patients/{patient_id}/ehr/investigations/order", response_model=OrderInvestigationResponse)
async def order_investigation(session_id: str, patient_id: str, request: OrderInvestigationRequest):
    """
    Order an investigation for a patient.

    This endpoint simulates ordering investigations via the EHR system.
    The investigation will be processed and results will become available after
    a realistic turnaround time based on the investigation type.

    Users can order investigations without performing an in-person review,
    simulating the ability to request tests remotely and have nurses collect samples.

    Default turnaround times:
    - ABG: 20 minutes
    - FBC, U&E, LFT: 60 minutes
    - CXR: 120 minutes (2 hours)
    - CT scan: 240 minutes (4 hours)
    - Blood cultures: 2880 minutes (48 hours)
    """
    from ..models.ehr import VisibilityRule, VisibilityCondition
    from ..models.events import Event
    from datetime import timedelta

    # Validate session
    session = simulation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Validate patient
    if patient_id not in session.patients:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found in session")

    patient = session.patients[patient_id]

    # Validate EHR exists
    if not ehr_service.has_record(patient_id):
        raise HTTPException(
            status_code=404,
            detail=f"No EHR record found for patient {patient_id}"
        )

    # Get current simulation time
    current_time = session.clock.get_current_time()

    # Determine turnaround time based on investigation type
    default_turnaround_times = {
        "ABG": 20,
        "FBC": 60,
        "U&E": 60,
        "LFT": 60,
        "CRP": 60,
        "Troponin": 60,
        "CXR": 120,
        "ECG": 5,
        "CT_Head": 240,
        "CT_Chest": 240,
        "Blood_Cultures": 2880,
    }

    turnaround_minutes = request.custom_turnaround_minutes
    if turnaround_minutes is None:
        # Use default or 60 minutes if not in dictionary
        turnaround_minutes = default_turnaround_times.get(request.investigation_type, 60)

    # Calculate result time
    resulted_time = current_time + timedelta(minutes=turnaround_minutes)

    # Get investigation template based on patient's current state
    investigation_template = patient.trajectory.get_investigation_template(
        patient.current_state,
        request.investigation_type
    )

    # If no template, use default normal values
    if not investigation_template:
        # Default normal results (simplified)
        default_results = {
            "ABG": {
                "result_data": {"pH": 7.40, "pCO2": 5.0, "pO2": 12.0, "HCO3": 24, "BE": 0},
                "interpretation": "Normal arterial blood gas",
                "abnormal_flags": []
            },
            "FBC": {
                "result_data": {"Hb": 135, "WCC": 7.5, "Platelets": 250},
                "interpretation": "Normal full blood count",
                "abnormal_flags": []
            },
            "U&E": {
                "result_data": {"Na": 140, "K": 4.0, "Urea": 5.0, "Creatinine": 80},
                "interpretation": "Normal renal function",
                "abnormal_flags": []
            },
            "CXR": {
                "result_data": {"findings": "No acute cardiopulmonary pathology"},
                "interpretation": "Normal chest X-ray",
                "abnormal_flags": []
            }
        }
        investigation_template = default_results.get(
            request.investigation_type,
            {
                "result_data": {"status": "Normal"},
                "interpretation": f"Normal {request.investigation_type}",
                "abnormal_flags": []
            }
        )

    # Create visibility rule (becomes visible when resulted)
    visibility_rule = VisibilityRule(
        condition=VisibilityCondition.TIME_ELAPSED,
        visible_after_time=resulted_time
    )

    # Add investigation result to EHR
    result = ehr_service.add_investigation_result(
        patient_id=patient_id,
        investigation_type=request.investigation_type,
        requested_time=current_time,
        resulted_time=resulted_time,
        result_data=investigation_template.get("result_data", {}),
        interpretation=investigation_template.get("interpretation"),
        abnormal_flags=investigation_template.get("abnormal_flags", []),
        visibility_rule=visibility_rule
    )

    if not result:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to order investigation for patient {patient_id}"
        )

    # Schedule event for when result becomes available
    result_event = Event(
        event_type="investigation_result",
        scheduled_time=resulted_time,
        patient_id=patient_id,
        data={
            "investigation_type": request.investigation_type,
            "result_id": result.result_id,
            "notification_message": f"Investigation result available: {request.investigation_type} for {patient.name}"
        }
    )
    session.scheduler.schedule_event(result_event)

    return OrderInvestigationResponse(
        message=f"Investigation ordered successfully: {request.investigation_type}",
        result_id=result.result_id,
        investigation_type=request.investigation_type,
        requested_time=current_time.isoformat(),
        expected_result_time=resulted_time.isoformat(),
        turnaround_minutes=turnaround_minutes
    )
