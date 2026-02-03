"""
Core simulation engine models: Clock, EventScheduler, and SimulationSession.
"""

import heapq
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

from .events import Event
from .patient import Patient, PatientState
from .actions import UserAction, ActionResult


class SimulationClock(BaseModel):
    """
    Hybrid clock: runs in real time + adds artificial time for in-person reviews.

    Total simulation time = Real elapsed time + Artificial time penalties
    This creates time pressure while penalizing in-person reviews realistically.
    """
    # Base times
    scenario_start_time: datetime  # When does the scenario start (e.g., 20:00)
    session_start_time: datetime   # When did the student actually start (real time)

    # Time tracking
    artificial_minutes_added: int = 0  # Extra time from in-person reviews
    last_check_time: datetime = Field(default_factory=datetime.now)  # For real-time tracking

    class Config:
        arbitrary_types_allowed = True

    def get_current_time(self) -> datetime:
        """
        Calculate current simulation time.
        = scenario_start_time + real_elapsed + artificial_added
        """
        real_now = datetime.now()
        real_elapsed_seconds = (real_now - self.session_start_time).total_seconds()
        real_elapsed_minutes = int(real_elapsed_seconds / 60)

        total_minutes = real_elapsed_minutes + self.artificial_minutes_added
        return self.scenario_start_time + timedelta(minutes=total_minutes)

    def get_elapsed_minutes(self) -> int:
        """Get total elapsed simulation minutes (real + artificial)."""
        real_now = datetime.now()
        real_elapsed_seconds = (real_now - self.session_start_time).total_seconds()
        real_elapsed_minutes = int(real_elapsed_seconds / 60)
        return real_elapsed_minutes + self.artificial_minutes_added

    def add_artificial_time(self, minutes: int) -> datetime:
        """
        Add artificial time (e.g., for in-person review).
        This simulates time-consuming activities beyond real time elapsed.
        """
        self.artificial_minutes_added += minutes
        self.last_check_time = datetime.now()
        return self.get_current_time()

    def get_state(self) -> Dict[str, Any]:
        """Get current clock state."""
        current_time = self.get_current_time()
        elapsed_minutes = self.get_elapsed_minutes()

        real_now = datetime.now()
        real_elapsed_seconds = (real_now - self.session_start_time).total_seconds()
        real_elapsed_minutes = int(real_elapsed_seconds / 60)

        return {
            "scenario_start_time": self.scenario_start_time.isoformat(),
            "current_time": current_time.isoformat(),
            "elapsed_minutes": elapsed_minutes,
            "real_elapsed_minutes": real_elapsed_minutes,
            "artificial_minutes_added": self.artificial_minutes_added,
            "formatted_time": current_time.strftime("%H:%M"),
            "formatted_elapsed": f"{elapsed_minutes} mins"
        }


class EventScheduler(BaseModel):
    """
    Priority queue for managing scheduled events.
    Events fire at specific simulated times, not real times.
    """
    events: List[Event] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def schedule(
        self,
        event: Event,
        scheduled_time: datetime,
        priority: int = 0
    ) -> None:
        """
        Schedule an event to fire at a specific simulation time.
        Lower priority numbers fire first if times are equal.
        """
        event.scheduled_time = scheduled_time
        heapq.heappush(self.events, (scheduled_time, priority, event))

    def get_due_events(self, current_time: datetime) -> List[Event]:
        """
        Retrieve all events that should fire at or before current time.
        Marks events as processed.
        """
        due_events = []

        while self.events and self.events[0][0] <= current_time:
            _, _, event = heapq.heappop(self.events)
            if not event.processed:
                event.processed = True
                due_events.append(event)

        return due_events

    def get_pending_events(self) -> List[Event]:
        """Get all pending (unprocessed) events."""
        return [e for _, _, e in self.events if not e.processed]

    def get_state(self) -> Dict[str, Any]:
        """Get scheduler state for debugging/display."""
        return {
            "total_events": len(self.events),
            "pending_events": len(self.get_pending_events()),
            "next_event_time": self.events[0][0].isoformat() if self.events else None
        }


class SimulationSession(BaseModel):
    """
    Main simulation orchestrator.
    Manages the entire simulation lifecycle: clock, patients, events, actions.
    """
    session_id: str = Field(default_factory=lambda: f"session_{uuid4().hex[:8]}")
    scenario_id: str

    # Core components
    clock: SimulationClock
    scheduler: EventScheduler = Field(default_factory=EventScheduler)
    patients: Dict[str, Patient] = Field(default_factory=dict)

    # Session tracking
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
    notifications: List[Dict[str, Any]] = Field(default_factory=list)
    is_complete: bool = False

    # Session metadata
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True

    def execute_action(self, action: UserAction) -> ActionResult:
        """
        Main simulation step - execute a user action.

        Process:
        1. Validate action
        2. Calculate current time (real time + artificial penalties)
        3. Add artificial time if action requires it (e.g., in-person review)
        4. Process any events that occurred during that time
        5. Evaluate patient state changes
        6. Return results
        """
        # Validate patient exists
        if action.patient_id not in self.patients:
            current_time = self.clock.get_current_time()
            return ActionResult(
                success=False,
                action=action,
                time_advanced_minutes=0,
                new_simulation_time=current_time,
                message=f"Patient {action.patient_id} not found"
            )

        patient = self.patients[action.patient_id]

        # Get time before action
        old_time = self.clock.get_current_time()

        # Add artificial time if this action requires it (e.g., in-person review)
        artificial_time_added = 0
        if action.action_type == "review_in_person":
            # In-person review adds 30 mins (or custom) to simulate travel + assessment
            artificial_time_added = action.time_cost_minutes if action.time_cost_minutes else 30
            new_time = self.clock.add_artificial_time(artificial_time_added)
        elif action.action_type == "document_note":
            # Documenting a note adds 3 mins (or custom) to simulate typing
            artificial_time_added = action.time_cost_minutes if action.time_cost_minutes else 3
            new_time = self.clock.add_artificial_time(artificial_time_added)
        else:
            # Other actions: just use current real time (no artificial penalty)
            new_time = self.clock.get_current_time()

        action.timestamp = new_time

        # Record action on patient
        patient.record_action(
            action.action_type,
            new_time,
            action.details
        )

        # Generate examination note if this is an in-person review
        if action.action_type == "review_in_person":
            self._generate_examination_note(patient, new_time)

        # Create clinical note if this is documentation action
        if action.action_type == "document_note":
            self._create_user_documentation_note(patient, new_time, action.details)

        # Calculate actual time advanced (including real time passage)
        time_advanced = int((new_time - old_time).total_seconds() / 60)

        # Get all events that occurred during this time window
        due_events = self.scheduler.get_due_events(new_time)

        # Process events and collect notifications
        triggered_events = []
        new_notifications = []

        for event in due_events:
            result = self._process_event(event)
            triggered_events.append(result)
            new_notifications.extend(result.get("notifications", []))

        # Evaluate patient state changes
        patient_state_changes = []
        for patient in self.patients.values():
            # Collect action types taken on this patient
            patient_actions = [
                a["action_type"]
                for a in patient.actions_taken
            ]

            # Check if state should change
            triggered_rule = patient.evaluate_state_change(
                new_time,
                patient_actions
            )

            if triggered_rule:
                state_change = patient.apply_state_change(triggered_rule, new_time)

                # Create notification for state change
                notification = {
                    "type": "patient_state_change",
                    "patient_id": patient.patient_id,
                    "patient_name": patient.name,
                    "old_state": state_change.old_state,
                    "new_state": state_change.new_state,
                    "message": triggered_rule.notification_message,
                    "urgency": triggered_rule.urgency,
                    "time": new_time.isoformat()
                }

                patient_state_changes.append(notification)
                new_notifications.append(triggered_rule.notification_message)
                self.notifications.append(notification)

        # Record action in history
        self.action_history.append({
            "action": action.model_dump(),
            "timestamp": new_time.isoformat(),
            "elapsed_minutes": self.clock.get_elapsed_minutes(),
            "time_advanced": time_advanced,
            "artificial_time_added": artificial_time_added
        })

        # Auto-save checkpoint (in real implementation, would save to file)
        # self._save_checkpoint()

        return ActionResult(
            success=True,
            action=action,
            time_advanced_minutes=time_advanced,
            new_simulation_time=new_time,
            message=f"Action completed: {action.action_type}",
            triggered_events=triggered_events,
            new_notifications=new_notifications,
            patient_state_changes=patient_state_changes
        )

    def _process_event(self, event: Event) -> Dict[str, Any]:
        """
        Process a single event and return the result.
        Different event types have different processing logic.
        """
        current_time = self.clock.get_current_time()

        result = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "patient_id": event.patient_id,
            "notifications": []
        }

        if event.event_type == "investigation_result":
            # Investigation result available
            message = event.data.get(
                "notification_message",
                f"Investigation result available for patient {event.patient_id}"
            )
            result["notifications"].append(message)

            # Add to notifications
            self.notifications.append({
                "type": "investigation_result",
                "patient_id": event.patient_id,
                "message": message,
                "time": current_time.isoformat(),
                "data": event.data
            })

        elif event.event_type == "new_request":
            # New patient request arrived
            message = event.data.get(
                "notification_message",
                f"New request for patient {event.patient_id}"
            )
            result["notifications"].append(message)

            self.notifications.append({
                "type": "new_request",
                "patient_id": event.patient_id,
                "message": message,
                "urgency": event.data.get("urgency", "routine"),
                "time": current_time.isoformat()
            })

        elif event.event_type == "escalation_response":
            # Senior has responded
            message = event.data.get(
                "notification_message",
                "Senior doctor has reviewed patient"
            )
            result["notifications"].append(message)

            self.notifications.append({
                "type": "escalation_response",
                "patient_id": event.patient_id,
                "message": message,
                "time": current_time.isoformat(),
                "data": event.data
            })

        return result

    def _generate_examination_note(self, patient: Patient, timestamp: datetime):
        """
        Generate an examination note based on the patient's current state.
        This simulates the clinician physically examining the patient and documenting findings.
        """
        # Import here to avoid circular dependency
        from ..services.ehr_service import ehr_service
        from ..models.ehr import NoteType, VisibilityRule, VisibilityCondition

        # Check if patient has an EHR record
        if not ehr_service.has_record(patient.patient_id):
            # No EHR record exists - skip note generation
            return

        # Get examination findings for current state
        examination_findings = patient.trajectory.get_examination_findings(patient.current_state)

        if not examination_findings:
            # No examination findings defined for this state - use default
            content = f"Patient reviewed in person. Current state: {patient.current_state.value}"
        else:
            # Format examination findings as a structured string
            in_person_note = examination_findings.get("in_person_note", "")
            in_person_examination = examination_findings.get("in_person_examination", "")

            # Build the content string with Notes and Examination sections
            parts = []
            if in_person_note:
                parts.append(f"Notes\n{in_person_note}")
            if in_person_examination:
                parts.append(f"Examination\n{in_person_examination}")

            content = "\n\n".join(parts) if parts else "Patient reviewed in person"

        # Generate clinical note with examination findings
        ehr_service.add_clinical_note(
            patient_id=patient.patient_id,
            note_type=NoteType.PROGRESS,
            timestamp=timestamp,
            author="User",  # The trainee performing the review
            author_role="FY1",
            title=f"In-Person Review at {timestamp.strftime('%H:%M')}",
            content=content,
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
        )

    def _create_user_documentation_note(self, patient: Patient, timestamp: datetime, details: Dict[str, Any]):
        """
        Create a clinical note from user documentation action.
        This records the clinician's documentation in the EHR.
        """
        # Import here to avoid circular dependency
        from ..services.ehr_service import ehr_service
        from ..models.ehr import NoteType, VisibilityRule, VisibilityCondition

        # Check if patient has an EHR record
        if not ehr_service.has_record(patient.patient_id):
            # No EHR record exists - skip note creation
            return

        # Extract note content and type from action details
        note_content = details.get("note_content", "")
        note_type_str = details.get("note_type", "progress")

        # Map string to NoteType enum
        note_type_map = {
            "admission": NoteType.ADMISSION,
            "progress": NoteType.PROGRESS,
            "consultant_review": NoteType.CONSULTANT_REVIEW,
            "discharge_summary": NoteType.DISCHARGE_SUMMARY,
            "investigation_result": NoteType.INVESTIGATION_RESULT,
            "procedure_note": NoteType.PROCEDURE_NOTE,
            "nursing_note": NoteType.NURSING_NOTE,
        }
        note_type = note_type_map.get(note_type_str, NoteType.PROGRESS)

        # Wrap the free-text content in a dictionary structure as required by EHR schema
        structured_content = {
            "clinical_note": note_content
        }

        # Create the clinical note
        ehr_service.add_clinical_note(
            patient_id=patient.patient_id,
            note_type=note_type,
            timestamp=timestamp,
            author="User",  # The trainee documenting
            author_role="FY1",
            title=f"Clinical Documentation - {timestamp.strftime('%H:%M')}",
            content=structured_content,  # Structured content matching EHR schema
            visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)  # Immediately visible
        )

    def get_state(self) -> Dict[str, Any]:
        """Get complete current simulation state."""
        return {
            "session_id": self.session_id,
            "scenario_id": self.scenario_id,
            "clock": self.clock.get_state(),
            "scheduler": self.scheduler.get_state(),
            "patients": {
                pid: {
                    "patient_id": p.patient_id,
                    "name": p.name,
                    "current_state": p.current_state,
                    "ward": p.ward,
                    "bed": p.bed
                }
                for pid, p in self.patients.items()
            },
            "action_count": len(self.action_history),
            "notification_count": len(self.notifications),
            "is_complete": self.is_complete
        }

    def get_timeline(self) -> List[Dict[str, Any]]:
        """
        Get chronological timeline of all session events.
        Useful for debugging and feedback generation.
        """
        timeline = []

        # Add all actions
        for action_record in self.action_history:
            timeline.append({
                "type": "action",
                "timestamp": action_record["timestamp"],
                "elapsed_minutes": action_record["elapsed_minutes"],
                "data": action_record
            })

        # Add all notifications
        for notification in self.notifications:
            timeline.append({
                "type": "notification",
                "timestamp": notification["time"],
                "data": notification
            })

        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])

        return timeline

    def complete_session(self) -> Dict[str, Any]:
        """
        Mark session as complete and generate summary.
        """
        self.is_complete = True
        self.completed_at = datetime.now()

        summary = {
            "session_id": self.session_id,
            "scenario_id": self.scenario_id,
            "completed_at": self.completed_at.isoformat(),
            "total_time_elapsed_minutes": self.clock.get_elapsed_minutes(),
            "total_actions": len(self.action_history),
            "patients": {
                pid: {
                    "name": p.name,
                    "final_state": p.current_state,
                    "state_changes": len(p.state_history),
                    "actions_taken": len(p.actions_taken)
                }
                for pid, p in self.patients.items()
            },
            "timeline": self.get_timeline()
        }

        return summary

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "scenario_id": "med_oncall_001",
                "clock": {
                    "current_time": "2024-01-15T20:30:00",
                    "elapsed_minutes": 30
                }
            }
        }
