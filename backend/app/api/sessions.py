"""
API endpoints for simulation session management.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime, timedelta

from ..services.simulation_engine import simulation_engine
from ..services.scenario_loader import scenario_loader
from ..services.vitals_parser import parse_vitals_from_text
from ..services.news_calculator import calculate_news2_score

router = APIRouter()


# Request/Response Models
class StartSessionRequest(BaseModel):
    """Request to start a new simulation session."""

    scenario_id: str = Field(..., description="ID of the scenario to load")
    custom_start_time: Optional[str] = Field(
        None,
        description="Custom scenario start time (ISO format). If not provided, uses scenario default.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "simple_test_001",
                "custom_start_time": "2024-01-15T20:00:00",
            }
        }


class SessionResponse(BaseModel):
    """Response containing session information."""

    session_id: str
    scenario_id: str
    is_complete: bool
    created_at: str
    current_time: str
    elapsed_minutes: int


class SessionStateResponse(BaseModel):
    """Detailed session state response."""

    session_id: str
    scenario_id: str
    clock: Dict[str, Any]
    scheduler: Dict[str, Any]
    patients: Dict[str, Any]
    action_count: int
    notification_count: int
    is_complete: bool


class VitalSignsResponse(BaseModel):
    """Vital signs response with NEWS2 score."""

    timestamp: str
    heart_rate: int
    blood_pressure: str  # Format: "145/88"
    temperature: float
    respiratory_rate: int
    oxygen_saturation: int
    oxygen_therapy: bool
    consciousness: str
    pain_score: Optional[int] = None
    news_score: int


class PatientDetailsResponse(BaseModel):
    """Patient details response."""

    patient_id: str
    name: str
    mrn: str
    age: int
    gender: str
    ward: str
    bed: str
    current_state: str
    actions_taken: List[Dict[str, Any]]
    state_history: List[Dict[str, Any]]
    latest_vitals: Optional[VitalSignsResponse] = None
    vitals_history: List[VitalSignsResponse] = []


class ScenarioListItem(BaseModel):
    """Scenario list item."""

    scenario_id: str
    title: str
    description: str
    difficulty: str
    estimated_duration_minutes: int
    patient_count: int


# Endpoints
@router.get("/scenarios", response_model=List[ScenarioListItem])
async def list_scenarios():
    """
    List all available simulation scenarios.

    Returns a list of scenarios that can be used to start new sessions.
    """
    try:
        scenarios = scenario_loader.list_scenarios()
        return scenarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scenarios: {str(e)}")


@router.post("/sessions/start", response_model=SessionResponse, status_code=201)
async def start_session(request: StartSessionRequest):
    """
    Start a new simulation session from a scenario.

    Creates a new session, initializes the simulation clock, loads patients,
    and schedules initial events.
    """
    try:
        # Parse custom start time if provided
        custom_start_time = None
        if request.custom_start_time:
            custom_start_time = datetime.fromisoformat(request.custom_start_time)

        # Create session
        session = simulation_engine.create_session(
            scenario_id=request.scenario_id, custom_start_time=custom_start_time
        )

        # Return session info
        return SessionResponse(
            session_id=session.session_id,
            scenario_id=session.scenario_id,
            is_complete=session.is_complete,
            created_at=session.created_at.isoformat(),
            current_time=session.clock.get_current_time().isoformat(),
            elapsed_minutes=session.clock.get_elapsed_minutes(),
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    """
    Get the current state of a simulation session.

    Returns detailed information about the session including clock state,
    patient states, pending events, and action history.
    """
    try:
        state = simulation_engine.get_session_state(session_id)
        return SessionStateResponse(**state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@router.post("/sessions/{session_id}/complete")
async def complete_session(session_id: str):
    """
    Mark a session as complete and generate summary.

    Returns a timeline of all actions and events, final patient states,
    and session statistics.
    """
    try:
        summary = simulation_engine.complete_session(session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")


@router.get("/sessions/{session_id}/timeline")
async def get_session_timeline(session_id: str):
    """
    Get chronological timeline of session events.

    Returns a sorted list of all actions, notifications, and state changes
    that occurred during the session.
    """
    try:
        timeline = simulation_engine.get_session_timeline(session_id)
        return {"session_id": session_id, "timeline": timeline}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")


@router.get("/sessions/{session_id}/patients/{patient_id}", response_model=PatientDetailsResponse)
async def get_patient_details(session_id: str, patient_id: str):
    """
    Get detailed information about a specific patient in a session.

    Returns patient demographics, current state, action history,
    state change history, and vital signs with NEWS2 score.
    """
    try:
        patient_details = simulation_engine.get_patient_details(session_id, patient_id)

        if not patient_details:
            raise HTTPException(
                status_code=404, detail=f"Patient {patient_id} not found in session {session_id}"
            )

        # Get session to access scenario data
        session = simulation_engine.get_session(session_id)
        if session and session.scenario_id:
            try:
                # Load scenario data to get examination findings
                scenario_data = scenario_loader.load_scenario(session.scenario_id)

                # Get current patient state
                current_state = patient_details.get("current_state")

                # Find patient in scenario data
                scenario_patient = None
                for patient in scenario_data.get("patients", []):
                    if patient.get("patient_id") == patient_id:
                        scenario_patient = patient
                        break

                # Get examination findings for current state
                observations_text = None
                if scenario_patient and current_state:
                    trajectory = scenario_patient.get("trajectory", {})
                    exam_findings = trajectory.get("examination_findings", {})
                    state_findings = exam_findings.get(current_state, {})
                    observations_text = state_findings.get("observations", "")

                # Parse vitals if observations exist
                if observations_text:
                    vitals = parse_vitals_from_text(observations_text)
                    news_score = calculate_news2_score(vitals)

                    # Use session's current simulation time instead of parsed timestamp
                    current_time = session.clock.get_current_time() if session and session.clock else vitals.timestamp

                    # Create vitals response
                    latest_vitals = VitalSignsResponse(
                        timestamp=current_time.isoformat() if isinstance(current_time, datetime) else current_time,
                        heart_rate=vitals.heart_rate,
                        blood_pressure=f"{vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}",
                        temperature=vitals.temperature,
                        respiratory_rate=vitals.respiratory_rate,
                        oxygen_saturation=vitals.oxygen_saturation,
                        oxygen_therapy=vitals.oxygen_therapy,
                        consciousness=vitals.consciousness,
                        pain_score=vitals.pain_score,
                        news_score=news_score
                    )

                    patient_details["latest_vitals"] = latest_vitals

                    # Build vitals history from state changes
                    vitals_history = []
                    vitals_timestamps_seen = set()  # Track timestamps to avoid duplicates
                    state_history = patient_details.get("state_history", [])
                    trajectory = scenario_patient.get("trajectory", {})
                    exam_findings = trajectory.get("examination_findings", {})

                    # Add current vitals as most recent
                    vitals_history.append(latest_vitals)
                    vitals_timestamps_seen.add(latest_vitals.timestamp)
                    print(f"DEBUG: Added current vitals with timestamp {latest_vitals.timestamp}, NEWS={latest_vitals.news_score}")

                    # Add historical vitals from previous states (sorted oldest to newest)
                    # Process in chronological order so collision offsets preserve correct sequence
                    sorted_state_history = sorted(
                        state_history,
                        key=lambda x: x.get("timestamp", ""),
                        reverse=False
                    )

                    for state_change in sorted_state_history:
                        # Use OLD state to capture vitals before the change
                        old_state_name = state_change.get("old_state")
                        new_state_name = state_change.get("new_state")
                        state_timestamp = state_change.get("timestamp")

                        # Skip if state didn't actually change (e.g., stable → stable)
                        if old_state_name == new_state_name:
                            state_timestamp_str = state_timestamp.isoformat() if isinstance(state_timestamp, datetime) else state_timestamp
                            print(f"DEBUG: Skipping no-op state change {old_state_name} → {new_state_name} at {state_timestamp_str}")
                            continue

                        if old_state_name and state_timestamp:
                            state_timestamp_str = state_timestamp.isoformat() if isinstance(state_timestamp, datetime) else state_timestamp
                            print(f"DEBUG: Processing state change from {old_state_name} → {new_state_name} at {state_timestamp_str}, using old_state vitals")

                            state_findings = exam_findings.get(old_state_name, {})
                            state_observations = state_findings.get("observations", "")

                            if state_observations:
                                try:
                                    # Parse vitals from this historical state
                                    historical_vitals = parse_vitals_from_text(state_observations)
                                    # Set timestamp to 1 minute before state change (vitals taken just before transition)
                                    state_change_dt = state_timestamp if isinstance(state_timestamp, datetime) else datetime.fromisoformat(state_timestamp.replace('Z', '+00:00'))
                                    historical_vitals.timestamp = state_change_dt - timedelta(minutes=1)

                                    # Handle timestamp collisions by adding seconds offset
                                    # Process oldest to newest, so newer states get timestamps closer to state change time
                                    historical_ts_iso = historical_vitals.timestamp.isoformat()
                                    collision_offset = 0
                                    while historical_ts_iso in vitals_timestamps_seen:
                                        collision_offset += 1
                                        # Add seconds to move forward in time (closer to state change)
                                        historical_vitals.timestamp = state_change_dt - timedelta(minutes=1) + timedelta(seconds=collision_offset)
                                        historical_ts_iso = historical_vitals.timestamp.isoformat()
                                        print(f"DEBUG: Timestamp collision detected, adjusting historical vitals to {historical_ts_iso} for state {old_state_name}")

                                    historical_news_score = calculate_news2_score(historical_vitals)

                                    historical_vitals_response = VitalSignsResponse(
                                        timestamp=historical_vitals.timestamp.isoformat(),
                                        heart_rate=historical_vitals.heart_rate,
                                        blood_pressure=f"{historical_vitals.blood_pressure_systolic}/{historical_vitals.blood_pressure_diastolic}",
                                        temperature=historical_vitals.temperature,
                                        respiratory_rate=historical_vitals.respiratory_rate,
                                        oxygen_saturation=historical_vitals.oxygen_saturation,
                                        oxygen_therapy=historical_vitals.oxygen_therapy,
                                        consciousness=historical_vitals.consciousness,
                                        pain_score=historical_vitals.pain_score,
                                        news_score=historical_news_score
                                    )

                                    vitals_history.append(historical_vitals_response)
                                    vitals_timestamps_seen.add(historical_vitals_response.timestamp)
                                    print(f"DEBUG: Added historical vitals for old_state {old_state_name}, timestamp {historical_vitals_response.timestamp}, NEWS={historical_vitals_response.news_score}, HR={historical_vitals_response.heart_rate}")
                                except Exception as e:
                                    print(f"Warning: Failed to parse historical vitals for old_state {old_state_name}: {e}")

                    patient_details["vitals_history"] = vitals_history
                    print(f"DEBUG: Final vitals_history has {len(vitals_history)} entries")
            except Exception as e:
                # Log error but don't fail the request if vitals parsing fails
                print(f"Warning: Failed to parse vitals: {e}")

        return PatientDetailsResponse(**patient_details)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patient details: {str(e)}")


@router.get("/sessions")
async def list_sessions():
    """
    List all active simulation sessions.

    Returns summary information for all sessions currently in memory.
    """
    try:
        sessions = simulation_engine.list_active_sessions()
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a simulation session.

    Removes the session from active memory. This operation cannot be undone.
    """
    try:
        deleted = simulation_engine.delete_session(session_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return {"session_id": session_id, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
