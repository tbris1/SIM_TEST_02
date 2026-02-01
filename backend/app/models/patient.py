"""
Patient models including state machine for clinical trajectories.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class PatientState(str, Enum):
    """
    Discrete patient states for simulation.
    Not a physiology model - just key clinical decision points.
    """
    STABLE = "stable"
    STABLE_WITH_CONCERNS = "stable_with_concerns"
    DETERIORATING = "deteriorating"
    CRITICALLY_UNWELL = "critically_unwell"


class StateChangeRule(BaseModel):
    """
    Declarative rule for when patient state changes.
    These are defined in scenario JSON and evaluated by the state machine.
    """
    rule_id: str = Field(default_factory=lambda: f"rule_{uuid4().hex[:8]}")

    # Trigger conditions
    trigger_type: Literal[
        "time_elapsed",           # State changes at specific time
        "action_taken",           # State changes when user does something
        "action_not_taken",       # State changes if user doesn't do something by deadline
        "investigation_received", # State changes when specific result comes back
        "escalation_occurred"     # State changes after escalation
    ]

    # Time-based triggers
    trigger_time: Optional[datetime] = None

    # Action-based triggers
    required_action: Optional[str] = None  # e.g., "escalate", "review_in_person"
    action_deadline: Optional[datetime] = None

    # Current state requirement (only apply rule if patient in this state)
    current_state_requirement: Optional[PatientState] = None

    # Outcome
    new_state: PatientState
    clinical_manifestation: str  # What the user observes
    notification_message: str    # Message sent to user
    urgency: Literal["low", "medium", "high", "critical"] = "medium"

    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "rule_abc123",
                "trigger_type": "time_elapsed",
                "trigger_time": "2024-01-15T21:30:00",
                "current_state_requirement": "stable_with_concerns",
                "new_state": "deteriorating",
                "clinical_manifestation": "Patient has increased work of breathing, O2 sats 88%",
                "notification_message": "Nurse calling: Margaret Thompson is more breathless",
                "urgency": "high"
            }
        }


class StateChange(BaseModel):
    """Record of a state change that occurred."""
    timestamp: datetime
    old_state: PatientState
    new_state: PatientState
    trigger: str
    clinical_notes: str


class PatientTrajectory(BaseModel):
    """
    Defines the clinical trajectory for a patient in a scenario.
    Contains all rules that govern state transitions.
    """
    trajectory_id: str = Field(default_factory=lambda: f"traj_{uuid4().hex[:8]}")
    state_change_rules: List[StateChangeRule] = Field(default_factory=list)

    def get_applicable_rules(
        self,
        current_state: PatientState,
        current_time: datetime
    ) -> List[StateChangeRule]:
        """
        Get rules that could apply given current state and time.
        """
        applicable = []
        for rule in self.state_change_rules:
            # Check if rule applies to current state
            if rule.current_state_requirement and rule.current_state_requirement != current_state:
                continue
            applicable.append(rule)
        return applicable


class Patient(BaseModel):
    """
    Patient model with state machine.
    Tracks current state and evaluates state transitions based on trajectory rules.
    """
    patient_id: str = Field(default_factory=lambda: f"pt_{uuid4().hex[:8]}")

    # Basic info (minimal for Phase 1, will expand in Phase 3 with EHR)
    name: str
    mrn: str  # Medical Record Number
    age: int
    gender: str
    ward: str
    bed: str

    # State machine
    current_state: PatientState
    state_history: List[StateChange] = Field(default_factory=list)
    trajectory: PatientTrajectory

    # Track actions taken on this patient
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)

    def evaluate_state_change(
        self,
        current_time: datetime,
        user_actions: List[str]
    ) -> Optional[StateChangeRule]:
        """
        Evaluate if patient state should change based on rules.
        Returns the rule that triggered the change, or None if no change.
        """
        applicable_rules = self.trajectory.get_applicable_rules(
            self.current_state,
            current_time
        )

        for rule in applicable_rules:
            if self._rule_triggered(rule, current_time, user_actions):
                return rule

        return None

    def _rule_triggered(
        self,
        rule: StateChangeRule,
        current_time: datetime,
        user_actions: List[str]
    ) -> bool:
        """Check if a specific rule's conditions are met."""

        if rule.trigger_type == "time_elapsed":
            if rule.trigger_time and current_time >= rule.trigger_time:
                return True

        elif rule.trigger_type == "action_taken":
            if rule.required_action in user_actions:
                return True

        elif rule.trigger_type == "action_not_taken":
            if rule.action_deadline and current_time >= rule.action_deadline:
                if rule.required_action not in user_actions:
                    return True

        elif rule.trigger_type == "escalation_occurred":
            if "escalate" in user_actions:
                return True

        return False

    def apply_state_change(
        self,
        rule: StateChangeRule,
        current_time: datetime
    ) -> StateChange:
        """
        Apply a state change and record it in history.
        """
        old_state = self.current_state
        self.current_state = rule.new_state

        state_change = StateChange(
            timestamp=current_time,
            old_state=old_state,
            new_state=rule.new_state,
            trigger=rule.trigger_type,
            clinical_notes=rule.clinical_manifestation
        )

        self.state_history.append(state_change)
        return state_change

    def record_action(self, action_type: str, timestamp: datetime, details: Dict[str, Any]):
        """Record that a user action was taken on this patient."""
        action_record = {
            "action_type": action_type,
            "timestamp": timestamp.isoformat(),
            **details
        }
        self.actions_taken.append(action_record)

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "pt_001",
                "name": "Margaret Thompson",
                "mrn": "MRN12345",
                "age": 72,
                "gender": "Female",
                "ward": "Ward 4A",
                "bed": "Bed 12",
                "current_state": "stable_with_concerns",
                "trajectory": {
                    "state_change_rules": [
                        {
                            "trigger_type": "time_elapsed",
                            "trigger_time": "2024-01-15T21:30:00",
                            "new_state": "deteriorating"
                        }
                    ]
                }
            }
        }
