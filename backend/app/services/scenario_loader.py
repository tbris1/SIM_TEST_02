"""
Service for loading and managing simulation scenarios from JSON files.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..config import settings
from ..models.simulation import SimulationClock, EventScheduler, SimulationSession
from ..models.patient import Patient, StateChangeRule, PatientTrajectory
from ..models.events import Event
from ..models.ehr import (
    NoteType, VisibilityCondition, VisibilityRule,
    ClinicalNote, InvestigationResult
)
from .ehr_service import ehr_service


class ScenarioLoader:
    """
    Loads scenario JSON files and initializes simulation sessions.
    """

    def __init__(self, scenarios_dir: Optional[Path] = None):
        """
        Initialize the scenario loader.

        Args:
            scenarios_dir: Directory containing scenario JSON files.
                          Defaults to settings.scenarios_dir
        """
        self.scenarios_dir = scenarios_dir or settings.scenarios_dir

        if not self.scenarios_dir.exists():
            raise FileNotFoundError(
                f"Scenarios directory not found: {self.scenarios_dir}"
            )

    def list_scenarios(self) -> List[Dict[str, Any]]:
        """
        List all available scenarios.

        Returns:
            List of scenario metadata dictionaries
        """
        scenarios = []

        for json_file in self.scenarios_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)

                scenarios.append({
                    "scenario_id": data.get("scenario_id"),
                    "title": data.get("metadata", {}).get("title", "Untitled"),
                    "description": data.get("metadata", {}).get("description", ""),
                    "difficulty": data.get("metadata", {}).get("difficulty", "medium"),
                    "estimated_duration_minutes": data.get("metadata", {}).get(
                        "estimated_duration_minutes", 60
                    ),
                    "patient_count": len(data.get("patients", [])),
                    "file_path": str(json_file),
                })
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load scenario from {json_file}: {e}")
                continue

        return scenarios

    def load_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """
        Load a specific scenario by ID.

        Args:
            scenario_id: The unique identifier of the scenario

        Returns:
            Parsed scenario data dictionary

        Raises:
            FileNotFoundError: If scenario file doesn't exist
            ValueError: If scenario JSON is invalid
        """
        scenario_file = self.scenarios_dir / f"{scenario_id}.json"

        if not scenario_file.exists():
            raise FileNotFoundError(f"Scenario not found: {scenario_id}")

        try:
            with open(scenario_file, "r") as f:
                data = json.load(f)

            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in scenario file: {e}")

    def create_session_from_scenario(
        self, scenario_id: str, custom_start_time: Optional[datetime] = None
    ) -> SimulationSession:
        """
        Create a new simulation session from a scenario file.

        Args:
            scenario_id: The scenario ID to load
            custom_start_time: Optional custom start time (overrides scenario default)

        Returns:
            Initialized SimulationSession ready to run

        Raises:
            FileNotFoundError: If scenario doesn't exist
            ValueError: If scenario data is invalid
        """
        # Load scenario data
        scenario_data = self.load_scenario(scenario_id)

        # Parse start time
        if custom_start_time:
            scenario_start_time = custom_start_time
        else:
            start_time_str = scenario_data.get("simulation_settings", {}).get(
                "start_time", "2024-01-15T20:00:00"
            )
            scenario_start_time = datetime.fromisoformat(start_time_str)

        # Create simulation clock
        clock = SimulationClock(
            scenario_start_time=scenario_start_time,
            session_start_time=datetime.now(),
        )

        # Create event scheduler
        scheduler = EventScheduler()

        # Parse and create patients
        patients = {}
        for patient_data in scenario_data.get("patients", []):
            patient = self._create_patient_from_data(patient_data)
            patients[patient.patient_id] = patient

        # Create session
        session = SimulationSession(
            scenario_id=scenario_id,
            clock=clock,
            scheduler=scheduler,
            patients=patients,
        )

        # Schedule initial events
        for event_data in scenario_data.get("scheduled_events", []):
            event = self._create_event_from_data(event_data)
            scheduled_time = datetime.fromisoformat(event_data["scheduled_time"])
            scheduler.schedule(event, scheduled_time)

        # Load EHR data for each patient
        for patient_data in scenario_data.get("patients", []):
            if "ehr" in patient_data:
                self._load_ehr_data(patient_data, scenario_start_time)

        return session

    def _create_patient_from_data(self, patient_data: Dict[str, Any]) -> Patient:
        """
        Create a Patient object from scenario JSON data.

        Args:
            patient_data: Patient dictionary from scenario JSON

        Returns:
            Initialized Patient object
        """
        # Parse state change rules
        state_change_rules = []
        trajectory = patient_data.get("trajectory", {})

        for rule_data in trajectory.get("state_change_rules", []):
            # Parse optional datetime fields
            trigger_time = None
            if "trigger_time" in rule_data:
                trigger_time = datetime.fromisoformat(rule_data["trigger_time"])

            action_deadline = None
            if "action_deadline" in rule_data:
                action_deadline = datetime.fromisoformat(rule_data["action_deadline"])

            rule = StateChangeRule(
                rule_id=rule_data["rule_id"],
                trigger_type=rule_data["trigger_type"],
                trigger_time=trigger_time,
                required_action=rule_data.get("required_action"),
                action_deadline=action_deadline,
                current_state_requirement=rule_data.get("current_state_requirement"),
                new_state=rule_data["new_state"],
                clinical_manifestation=rule_data["clinical_manifestation"],
                notification_message=rule_data["notification_message"],
                urgency=rule_data.get("urgency", "routine"),
            )
            state_change_rules.append(rule)

        # Load examination findings (if present in scenario)
        examination_findings = trajectory.get("examination_findings", {})

        # Load investigation templates (if present in scenario)
        investigation_templates = trajectory.get("investigation_templates", {})

        # Create patient trajectory
        patient_trajectory = PatientTrajectory(
            state_change_rules=state_change_rules,
            examination_findings=examination_findings,
            investigation_templates=investigation_templates
        )

        # Create patient
        patient = Patient(
            patient_id=patient_data["patient_id"],
            name=patient_data["name"],
            mrn=patient_data["mrn"],
            age=patient_data["age"],
            gender=patient_data["gender"],
            ward=patient_data["ward"],
            bed=patient_data["bed"],
            current_state=patient_data.get("initial_state", "stable"),
            trajectory=patient_trajectory,
        )

        return patient

    def _create_event_from_data(self, event_data: Dict[str, Any]) -> Event:
        """
        Create an Event object from scenario JSON data.

        Args:
            event_data: Event dictionary from scenario JSON

        Returns:
            Initialized Event object
        """
        event = Event(
            event_id=event_data["event_id"],
            event_type=event_data["event_type"],
            patient_id=event_data["patient_id"],
            data=event_data.get("data", {}),
        )

        return event

    def _load_ehr_data(
        self,
        patient_data: Dict[str, Any],
        scenario_start_time: datetime
    ) -> None:
        """
        Load EHR data for a patient from scenario JSON.

        Args:
            patient_data: Patient dictionary from scenario JSON
            scenario_start_time: Start time of the scenario
        """
        ehr_data = patient_data.get("ehr", {})
        patient_id = patient_data["patient_id"]

        # Create patient EHR record
        ehr_service.create_patient_record(
            patient_id=patient_id,
            mrn=patient_data["mrn"],
            name=patient_data["name"],
            age=patient_data["age"],
            gender=patient_data["gender"],
            allergies=ehr_data.get("allergies", []),
            active_diagnoses=ehr_data.get("active_diagnoses", []),
            current_medications=ehr_data.get("current_medications", [])
        )

        # Load clinical notes
        for note_data in ehr_data.get("clinical_notes", []):
            # Parse visibility rule
            visibility_rule = None
            if "visibility_rule" in note_data:
                visibility_rule = self._create_visibility_rule(
                    note_data["visibility_rule"],
                    patient_id,
                    scenario_start_time
                )

            # Add note
            ehr_service.add_clinical_note(
                patient_id=patient_id,
                note_type=NoteType(note_data["note_type"]),
                timestamp=datetime.fromisoformat(note_data["timestamp"]),
                author=note_data["author"],
                author_role=note_data["author_role"],
                title=note_data["title"],
                content=note_data["content"],
                visibility_rule=visibility_rule
            )

        # Load investigation results
        for result_data in ehr_data.get("investigation_results", []):
            # Parse visibility rule
            visibility_rule = None
            if "visibility_rule" in result_data:
                visibility_rule = self._create_visibility_rule(
                    result_data["visibility_rule"],
                    patient_id,
                    scenario_start_time
                )

            # Add result
            ehr_service.add_investigation_result(
                patient_id=patient_id,
                investigation_type=result_data["investigation_type"],
                requested_time=datetime.fromisoformat(result_data["requested_time"]),
                resulted_time=datetime.fromisoformat(result_data["resulted_time"]),
                result_data=result_data["result_data"],
                interpretation=result_data.get("interpretation"),
                abnormal_flags=result_data.get("abnormal_flags", []),
                visibility_rule=visibility_rule
            )

    def _create_visibility_rule(
        self,
        rule_data: Dict[str, Any],
        patient_id: str,
        scenario_start_time: datetime
    ) -> VisibilityRule:
        """
        Create a VisibilityRule from scenario JSON data.

        Args:
            rule_data: Visibility rule dictionary
            patient_id: Patient identifier
            scenario_start_time: Start time of scenario

        Returns:
            Initialized VisibilityRule
        """
        condition = VisibilityCondition(rule_data["condition"])

        rule_kwargs = {
            "condition": condition,
            "patient_id": patient_id
        }

        # Add optional fields
        if "visible_after_time" in rule_data:
            rule_kwargs["visible_after_time"] = datetime.fromisoformat(
                rule_data["visible_after_time"]
            )

        if "required_action" in rule_data:
            rule_kwargs["required_action"] = rule_data["required_action"]

        return VisibilityRule(**rule_kwargs)


# Global scenario loader instance
scenario_loader = ScenarioLoader()
