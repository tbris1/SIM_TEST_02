"""
Service layer wrapper for the simulation engine.
Manages active simulation sessions and provides business logic.
"""

from typing import Dict, Optional, Any
from datetime import datetime

from ..models.simulation import SimulationSession
from ..models.actions import UserAction, ActionResult
from .scenario_loader import scenario_loader


class SimulationEngineService:
    """
    Service for managing active simulation sessions.
    Provides a clean interface between API layer and simulation engine.
    """

    def __init__(self):
        """Initialize the service with an empty session registry."""
        self.active_sessions: Dict[str, SimulationSession] = {}

    def create_session(
        self, scenario_id: str, custom_start_time: Optional[datetime] = None
    ) -> SimulationSession:
        """
        Create a new simulation session from a scenario.

        Args:
            scenario_id: The scenario to load
            custom_start_time: Optional custom start time

        Returns:
            Newly created SimulationSession

        Raises:
            FileNotFoundError: If scenario doesn't exist
            ValueError: If scenario data is invalid
        """
        # Create session from scenario
        session = scenario_loader.create_session_from_scenario(
            scenario_id=scenario_id, custom_start_time=custom_start_time
        )

        # Store in active sessions
        self.active_sessions[session.session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[SimulationSession]:
        """
        Retrieve an active session by ID.

        Args:
            session_id: The session ID to retrieve

        Returns:
            SimulationSession if found, None otherwise
        """
        return self.active_sessions.get(session_id)

    def execute_action(
        self, session_id: str, action: UserAction
    ) -> ActionResult:
        """
        Execute a user action within a simulation session.

        Args:
            session_id: The session to execute the action in
            action: The user action to execute

        Returns:
            ActionResult with execution outcome

        Raises:
            ValueError: If session doesn't exist
        """
        session = self.get_session(session_id)

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.is_complete:
            raise ValueError(f"Session {session_id} is already complete")

        # Execute action on session
        result = session.execute_action(action)

        return result

    def complete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Mark a session as complete and generate summary.

        Args:
            session_id: The session to complete

        Returns:
            Session summary dictionary

        Raises:
            ValueError: If session doesn't exist
        """
        session = self.get_session(session_id)

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.is_complete:
            raise ValueError(f"Session {session_id} is already complete")

        # Complete session
        summary = session.complete_session()

        return summary

    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current state of a session.

        Args:
            session_id: The session ID

        Returns:
            Session state dictionary

        Raises:
            ValueError: If session doesn't exist
        """
        session = self.get_session(session_id)

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        return session.get_state()

    def get_session_timeline(self, session_id: str) -> list[Dict[str, Any]]:
        """
        Get chronological timeline of session events.

        Args:
            session_id: The session ID

        Returns:
            Timeline list of events

        Raises:
            ValueError: If session doesn't exist
        """
        session = self.get_session(session_id)

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        return session.get_timeline()

    def get_patient_details(
        self, session_id: str, patient_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific patient in a session.

        Args:
            session_id: The session ID
            patient_id: The patient ID

        Returns:
            Patient details dictionary or None if not found

        Raises:
            ValueError: If session doesn't exist
        """
        session = self.get_session(session_id)

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        patient = session.patients.get(patient_id)

        if not patient:
            return None

        return {
            "patient_id": patient.patient_id,
            "name": patient.name,
            "mrn": patient.mrn,
            "age": patient.age,
            "gender": patient.gender,
            "ward": patient.ward,
            "bed": patient.bed,
            "current_state": patient.current_state,
            "actions_taken": patient.actions_taken,
            "state_history": patient.state_history,
        }

    def list_active_sessions(self) -> list[Dict[str, Any]]:
        """
        List all active sessions.

        Returns:
            List of session summary dictionaries
        """
        return [
            {
                "session_id": session_id,
                "scenario_id": session.scenario_id,
                "is_complete": session.is_complete,
                "elapsed_minutes": session.clock.get_elapsed_minutes(),
                "patient_count": len(session.patients),
                "action_count": len(session.action_history),
                "created_at": session.created_at.isoformat(),
            }
            for session_id, session in self.active_sessions.items()
        ]

    def delete_session(self, session_id: str) -> bool:
        """
        Remove a session from active sessions.

        Args:
            session_id: The session to delete

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False

    def get_active_session_count(self) -> int:
        """
        Get the number of active sessions.

        Returns:
            Count of active sessions
        """
        return len(self.active_sessions)


# Global simulation engine service instance
simulation_engine = SimulationEngineService()
