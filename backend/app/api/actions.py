"""
API endpoints for executing simulation actions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..services.simulation_engine import simulation_engine
from ..models.actions import UserAction, ActionResult

router = APIRouter()


# Request/Response Models
class ExecuteActionRequest(BaseModel):
    """Request to execute a user action."""

    action_type: str = Field(
        ...,
        description="Type of action: review_in_person, request_investigation, escalate, document_note, ask_nurse_question",
    )
    patient_id: str = Field(..., description="ID of the patient this action applies to")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Action-specific details"
    )
    time_cost_minutes: Optional[int] = Field(
        None, description="Custom time cost in minutes (uses default if not provided)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "review_in_person",
                "patient_id": "pt_001",
                "details": {"location": "Ward 4A, Bed 12"},
                "time_cost_minutes": 30,
            }
        }


class ExecuteActionResponse(BaseModel):
    """Response from executing an action."""

    success: bool
    action_type: str
    patient_id: str
    time_advanced_minutes: int
    new_simulation_time: str
    message: str
    triggered_events: List[Dict[str, Any]] = []
    new_notifications: List[str] = []
    patient_state_changes: List[Dict[str, Any]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action_type": "review_in_person",
                "patient_id": "pt_001",
                "time_advanced_minutes": 30,
                "new_simulation_time": "2024-01-15T20:35:00",
                "message": "Action completed: review_in_person",
                "triggered_events": [],
                "new_notifications": ["Patient reviewed successfully"],
                "patient_state_changes": [],
            }
        }


# Endpoints
@router.post("/sessions/{session_id}/actions", response_model=ExecuteActionResponse)
async def execute_action(session_id: str, request: ExecuteActionRequest):
    """
    Execute a user action within a simulation session.

    This is the main interaction endpoint. When a user takes an action:
    1. Time advances (based on action type)
    2. Any scheduled events that occurred during that time are processed
    3. Patient states are evaluated and may change
    4. Results, notifications, and state changes are returned

    Available action types:
    - `review_in_person`: Physical patient review (default: 30 mins)
    - `request_investigation`: Order tests (default: 2 mins)
    - `escalate`: Call senior doctor (default: 5 mins)
    - `document_note`: Write clinical note (default: 5 mins)
    - `ask_nurse_question`: Chat with nurse (default: 2 mins)
    """
    try:
        # Create UserAction from request
        action = UserAction(
            action_type=request.action_type,
            patient_id=request.patient_id,
            details=request.details,
            time_cost_minutes=request.time_cost_minutes,
        )

        # Execute action via service
        result = simulation_engine.execute_action(session_id, action)

        # Convert to response format
        return ExecuteActionResponse(
            success=result.success,
            action_type=result.action.action_type,
            patient_id=result.action.patient_id,
            time_advanced_minutes=result.time_advanced_minutes,
            new_simulation_time=result.new_simulation_time.isoformat(),
            message=result.message,
            triggered_events=result.triggered_events,
            new_notifications=result.new_notifications,
            patient_state_changes=result.patient_state_changes,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute action: {str(e)}"
        )


@router.post("/sessions/{session_id}/actions/review")
async def review_patient_in_person(
    session_id: str,
    patient_id: str,
    location: Optional[str] = None,
    time_cost_minutes: int = 30,
):
    """
    Convenience endpoint for in-person patient review.

    Adds artificial time (default 30 mins) to simulate travel + assessment.
    """
    try:
        action = UserAction(
            action_type="review_in_person",
            patient_id=patient_id,
            details={"location": location or "Unknown"},
            time_cost_minutes=time_cost_minutes,
        )

        result = simulation_engine.execute_action(session_id, action)

        return ExecuteActionResponse(
            success=result.success,
            action_type=result.action.action_type,
            patient_id=result.action.patient_id,
            time_advanced_minutes=result.time_advanced_minutes,
            new_simulation_time=result.new_simulation_time.isoformat(),
            message=result.message,
            triggered_events=result.triggered_events,
            new_notifications=result.new_notifications,
            patient_state_changes=result.patient_state_changes,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to review patient: {str(e)}"
        )


@router.post("/sessions/{session_id}/actions/escalate")
async def escalate_patient(
    session_id: str,
    patient_id: str,
    escalate_to: str = "registrar",
    reason: str = "",
    time_cost_minutes: int = 5,
):
    """
    Convenience endpoint for escalating to senior doctor.

    Records the escalation and may trigger state changes (e.g., patient stabilizes).
    """
    try:
        action = UserAction(
            action_type="escalate",
            patient_id=patient_id,
            details={"escalate_to": escalate_to, "reason": reason},
            time_cost_minutes=time_cost_minutes,
        )

        result = simulation_engine.execute_action(session_id, action)

        return ExecuteActionResponse(
            success=result.success,
            action_type=result.action.action_type,
            patient_id=result.action.patient_id,
            time_advanced_minutes=result.time_advanced_minutes,
            new_simulation_time=result.new_simulation_time.isoformat(),
            message=result.message,
            triggered_events=result.triggered_events,
            new_notifications=result.new_notifications,
            patient_state_changes=result.patient_state_changes,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to escalate patient: {str(e)}"
        )


@router.post("/sessions/{session_id}/actions/investigate")
async def request_investigation(
    session_id: str,
    patient_id: str,
    investigation_type: str,
    urgency: str = "routine",
    expected_delay_minutes: int = 30,
):
    """
    Convenience endpoint for requesting investigations.

    Investigations return results after a delay (based on simulation time, not real time).
    """
    try:
        action = UserAction(
            action_type="request_investigation",
            patient_id=patient_id,
            details={
                "investigation_type": investigation_type,
                "urgency": urgency,
                "expected_delay_minutes": expected_delay_minutes,
            },
            time_cost_minutes=2,
        )

        result = simulation_engine.execute_action(session_id, action)

        return ExecuteActionResponse(
            success=result.success,
            action_type=result.action.action_type,
            patient_id=result.action.patient_id,
            time_advanced_minutes=result.time_advanced_minutes,
            new_simulation_time=result.new_simulation_time.isoformat(),
            message=result.message,
            triggered_events=result.triggered_events,
            new_notifications=result.new_notifications,
            patient_state_changes=result.patient_state_changes,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to request investigation: {str(e)}"
        )


@router.post("/sessions/{session_id}/actions/document")
async def document_clinical_note(
    session_id: str, patient_id: str, note_content: str, note_type: str = "review"
):
    """
    Convenience endpoint for documenting clinical notes.

    Records the note in the patient's action history.
    """
    try:
        action = UserAction(
            action_type="document_note",
            patient_id=patient_id,
            details={"note_content": note_content, "note_type": note_type},
            time_cost_minutes=5,
        )

        result = simulation_engine.execute_action(session_id, action)

        return ExecuteActionResponse(
            success=result.success,
            action_type=result.action.action_type,
            patient_id=result.action.patient_id,
            time_advanced_minutes=result.time_advanced_minutes,
            new_simulation_time=result.new_simulation_time.isoformat(),
            message=result.message,
            triggered_events=result.triggered_events,
            new_notifications=result.new_notifications,
            patient_state_changes=result.patient_state_changes,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to document note: {str(e)}"
        )
