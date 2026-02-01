"""
Event models for the simulation engine.
Events represent things that happen at specific simulated times (results, deteriorations, new requests).
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class Event(BaseModel):
    """
    Base event model for scheduled occurrences in the simulation.
    Events are triggered at specific sim times and processed by the session orchestrator.
    """
    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:8]}")
    event_type: Literal[
        "investigation_result",
        "patient_deterioration",
        "new_request",
        "escalation_response"
    ]
    scheduled_time: datetime
    patient_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    processed: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_abc123",
                "event_type": "investigation_result",
                "scheduled_time": "2024-01-15T20:30:00",
                "patient_id": "pt_001",
                "data": {
                    "investigation": "ABG",
                    "result": {"pH": 7.32, "pCO2": 7.8}
                }
            }
        }

    def __lt__(self, other: 'Event') -> bool:
        """Allow events to be compared for priority queue ordering."""
        return self.scheduled_time < other.scheduled_time


class InvestigationResultEvent(BaseModel):
    """Specific event for investigation results becoming available."""
    investigation_type: str  # "FBC", "U&E", "ABG", "CXR", etc.
    result_data: Dict[str, Any]
    notification_message: str

    class Config:
        json_schema_extra = {
            "example": {
                "investigation_type": "ABG",
                "result_data": {
                    "pH": 7.32,
                    "pCO2": 7.8,
                    "pO2": 8.2,
                    "interpretation": "Type 2 respiratory failure"
                },
                "notification_message": "ABG results available for Margaret Thompson"
            }
        }


class PatientDeteriorationEvent(BaseModel):
    """Event for patient state changes."""
    new_state: str
    clinical_manifestation: str
    notification_message: str
    urgency: Literal["low", "medium", "high", "critical"] = "medium"

    class Config:
        json_schema_extra = {
            "example": {
                "new_state": "deteriorating",
                "clinical_manifestation": "Increased work of breathing, O2 sats 88%",
                "notification_message": "Nurse calling: Margaret Thompson more breathless",
                "urgency": "high"
            }
        }


class NewRequestEvent(BaseModel):
    """Event for new patient requests/bleeps."""
    request_type: Literal["nurse_call", "bleep", "fast_bleep"]
    initial_concern: str
    urgency: Literal["routine", "urgent", "immediate"]

    class Config:
        json_schema_extra = {
            "example": {
                "request_type": "nurse_call",
                "initial_concern": "Patient has chest pain",
                "urgency": "urgent"
            }
        }


class EscalationResponseEvent(BaseModel):
    """Event for senior doctor response after escalation."""
    escalation_outcome: str
    actions_taken: list[str]
    new_plan: str

    class Config:
        json_schema_extra = {
            "example": {
                "escalation_outcome": "Registrar reviewed patient",
                "actions_taken": ["Started NIV", "Adjusted medications"],
                "new_plan": "Continue NIV, repeat ABG in 1 hour"
            }
        }
