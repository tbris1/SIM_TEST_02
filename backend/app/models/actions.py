"""
User action models.
Defines the actions users can take during simulation (review, escalate, etc.)
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class UserAction(BaseModel):
    """
    Represents a single action taken by the user during simulation.
    Each action has a time cost and triggers simulation progression.
    """
    action_type: Literal[
        "review_in_person",      # Physical patient review
        "request_investigation", # Order tests
        "escalate",              # Call senior
        "document_note",         # Write clinical note
        "ask_nurse_question"     # Chat with nurse (minimal time cost)
    ]
    patient_id: str
    timestamp: Optional[datetime] = None  # Set by system when action executed
    details: Dict[str, Any] = Field(default_factory=dict)

    # Time cost in minutes (can be overridden by scenario)
    time_cost_minutes: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "review_in_person",
                "patient_id": "pt_001",
                "details": {
                    "location": "Ward 4A, Bed 12"
                },
                "time_cost_minutes": 30
            }
        }

    def get_time_cost(self) -> int:
        """
        Get the time cost for this action.
        Returns custom time_cost_minutes if set, otherwise default based on action type.
        """
        if self.time_cost_minutes is not None:
            return self.time_cost_minutes

        # Default time costs
        default_costs = {
            "review_in_person": 30,      # 30 mins including travel
            "request_investigation": 2,   # 2 mins to order
            "escalate": 5,                # 5 mins to call and handover
            "document_note": 5,           # 5 mins to document
            "ask_nurse_question": 2       # 2 mins for conversation
        }

        return default_costs.get(self.action_type, 5)


class ReviewInPersonAction(BaseModel):
    """Details specific to in-person review."""
    location: str
    findings_notes: Optional[str] = None


class RequestInvestigationAction(BaseModel):
    """Details for requesting investigations."""
    investigation_type: str  # "FBC", "U&E", "CXR", "ABG", etc.
    urgency: Literal["routine", "urgent", "immediate"] = "routine"
    clinical_indication: Optional[str] = None

    # Result delay in sim minutes (defined in scenario)
    expected_delay_minutes: int = 30


class EscalateAction(BaseModel):
    """Details for escalation."""
    escalate_to: Literal["registrar", "consultant", "specialty"] = "registrar"
    reason: str
    specialty: Optional[str] = None  # If escalating to specialty


class DocumentNoteAction(BaseModel):
    """Details for clinical documentation."""
    note_content: str
    note_type: Literal["clerking", "review", "plan"] = "review"


class ActionResult(BaseModel):
    """
    Result of executing an action.
    Contains what happened, time advanced, and any triggered events.
    """
    success: bool
    action: UserAction
    time_advanced_minutes: int
    new_simulation_time: datetime
    message: str

    # Events/notifications triggered by this action
    triggered_events: list[Dict[str, Any]] = Field(default_factory=list)
    new_notifications: list[str] = Field(default_factory=list)

    # Patient state changes resulting from this action
    patient_state_changes: list[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action": {
                    "action_type": "review_in_person",
                    "patient_id": "pt_001"
                },
                "time_advanced_minutes": 30,
                "new_simulation_time": "2024-01-15T20:35:00",
                "message": "Reviewed Margaret Thompson in person",
                "triggered_events": [
                    {
                        "event_type": "investigation_result",
                        "message": "ABG results now available"
                    }
                ],
                "new_notifications": [
                    "Blood results available for Margaret Thompson"
                ]
            }
        }
