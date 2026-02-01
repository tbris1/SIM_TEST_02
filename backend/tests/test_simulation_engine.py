"""
Unit tests for core simulation engine: Clock, EventScheduler, Patient, and SimulationSession.
"""

import pytest
from datetime import datetime, timedelta
from app.models.simulation import SimulationClock, EventScheduler, SimulationSession
from app.models.events import Event
from app.models.patient import Patient, PatientState, PatientTrajectory, StateChangeRule
from app.models.actions import UserAction


class TestSimulationClock:
    """Test the hybrid simulation clock (real time + artificial time)."""

    def test_clock_initialization(self):
        """Test clock starts at correct time."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()

        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        # Current time should be very close to scenario_start (minimal real time elapsed)
        current_time = clock.get_current_time()
        elapsed = clock.get_elapsed_minutes()

        assert abs((current_time - scenario_start).total_seconds()) < 5  # Within 5 seconds
        assert elapsed == 0  # No artificial time added yet

    def test_add_artificial_time(self):
        """Test adding artificial time for in-person reviews."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()

        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        # Add 30 minutes of artificial time
        new_time = clock.add_artificial_time(30)

        # Should have added 30 mins to simulation time
        assert clock.artificial_minutes_added == 30
        elapsed = clock.get_elapsed_minutes()
        assert elapsed == 30  # 0 real time (essentially) + 30 artificial

    def test_clock_multiple_artificial_adds(self):
        """Test multiple artificial time additions accumulate."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()

        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        clock.add_artificial_time(15)
        clock.add_artificial_time(10)
        clock.add_artificial_time(5)

        assert clock.artificial_minutes_added == 30
        elapsed = clock.get_elapsed_minutes()
        assert elapsed == 30  # 0 real + 30 artificial


class TestEventScheduler:
    """Test the event scheduler."""

    def test_schedule_event(self):
        """Test scheduling an event."""
        scheduler = EventScheduler()
        event_time = datetime(2024, 1, 15, 20, 30, 0)

        event = Event(
            event_type="investigation_result",
            scheduled_time=event_time,
            patient_id="pt_001",
            data={"test": "value"}
        )

        scheduler.schedule(event, event_time)

        assert len(scheduler.events) == 1

    def test_get_due_events(self):
        """Test retrieving due events."""
        scheduler = EventScheduler()

        # Schedule events at different times
        event1 = Event(
            event_type="investigation_result",
            scheduled_time=datetime(2024, 1, 15, 20, 15, 0),
            patient_id="pt_001"
        )
        event2 = Event(
            event_type="new_request",
            scheduled_time=datetime(2024, 1, 15, 20, 30, 0),
            patient_id="pt_002"
        )

        scheduler.schedule(event1, datetime(2024, 1, 15, 20, 15, 0))
        scheduler.schedule(event2, datetime(2024, 1, 15, 20, 30, 0))

        # At 20:20, only first event should be due
        current_time = datetime(2024, 1, 15, 20, 20, 0)
        due_events = scheduler.get_due_events(current_time)

        assert len(due_events) == 1
        assert due_events[0].patient_id == "pt_001"

        # At 20:35, second event should also be due
        current_time = datetime(2024, 1, 15, 20, 35, 0)
        due_events = scheduler.get_due_events(current_time)

        assert len(due_events) == 1
        assert due_events[0].patient_id == "pt_002"

    def test_events_ordered_by_time(self):
        """Test events are retrieved in chronological order."""
        scheduler = EventScheduler()

        # Schedule events out of order
        times = [
            datetime(2024, 1, 15, 20, 30, 0),
            datetime(2024, 1, 15, 20, 10, 0),
            datetime(2024, 1, 15, 20, 20, 0),
        ]

        for i, time in enumerate(times):
            event = Event(
                event_type="investigation_result",
                scheduled_time=time,
                patient_id=f"pt_{i}"
            )
            scheduler.schedule(event, time)

        # Get all events at once
        current_time = datetime(2024, 1, 15, 21, 0, 0)
        due_events = scheduler.get_due_events(current_time)

        # Should be in time order
        assert len(due_events) == 3
        assert due_events[0].patient_id == "pt_1"  # 20:10
        assert due_events[1].patient_id == "pt_2"  # 20:20
        assert due_events[2].patient_id == "pt_0"  # 20:30


class TestPatientStateMachine:
    """Test patient state transitions."""

    def test_patient_initialization(self):
        """Test patient initializes with correct state."""
        patient = Patient(
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory()
        )

        assert patient.current_state == PatientState.STABLE
        assert len(patient.state_history) == 0

    def test_time_based_state_change(self):
        """Test state changes based on time."""
        # Create rule: deteriorate at 21:30
        rule = StateChangeRule(
            trigger_type="time_elapsed",
            trigger_time=datetime(2024, 1, 15, 21, 30, 0),
            current_state_requirement=PatientState.STABLE_WITH_CONCERNS,
            new_state=PatientState.DETERIORATING,
            clinical_manifestation="Patient more breathless",
            notification_message="Patient deteriorating"
        )

        trajectory = PatientTrajectory(state_change_rules=[rule])

        patient = Patient(
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE_WITH_CONCERNS,
            trajectory=trajectory
        )

        # At 21:00, no change should occur
        triggered = patient.evaluate_state_change(
            datetime(2024, 1, 15, 21, 0, 0),
            []
        )
        assert triggered is None

        # At 21:30, state should change
        triggered = patient.evaluate_state_change(
            datetime(2024, 1, 15, 21, 30, 0),
            []
        )
        assert triggered is not None
        assert triggered.new_state == PatientState.DETERIORATING

    def test_action_based_state_change(self):
        """Test state changes based on user actions."""
        # Create rule: stabilize on escalation
        rule = StateChangeRule(
            trigger_type="escalation_occurred",
            current_state_requirement=None,
            new_state=PatientState.STABLE,
            clinical_manifestation="Patient stabilized",
            notification_message="Patient improving"
        )

        trajectory = PatientTrajectory(state_change_rules=[rule])

        patient = Patient(
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.DETERIORATING,
            trajectory=trajectory
        )

        # Without escalation, no change
        triggered = patient.evaluate_state_change(
            datetime(2024, 1, 15, 21, 0, 0),
            ["review_in_person"]
        )
        assert triggered is None

        # With escalation, state changes
        triggered = patient.evaluate_state_change(
            datetime(2024, 1, 15, 21, 0, 0),
            ["escalate"]
        )
        assert triggered is not None
        assert triggered.new_state == PatientState.STABLE

    def test_action_not_taken_state_change(self):
        """Test state changes when action not taken by deadline."""
        # Create rule: critical if not escalated by 22:00
        rule = StateChangeRule(
            trigger_type="action_not_taken",
            required_action="escalate",
            action_deadline=datetime(2024, 1, 15, 22, 0, 0),
            current_state_requirement=PatientState.DETERIORATING,
            new_state=PatientState.CRITICALLY_UNWELL,
            clinical_manifestation="Patient critical",
            notification_message="Patient critically unwell"
        )

        trajectory = PatientTrajectory(state_change_rules=[rule])

        patient = Patient(
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.DETERIORATING,
            trajectory=trajectory
        )

        # Before deadline, no change
        triggered = patient.evaluate_state_change(
            datetime(2024, 1, 15, 21, 30, 0),
            []
        )
        assert triggered is None

        # After deadline without escalation, state changes
        triggered = patient.evaluate_state_change(
            datetime(2024, 1, 15, 22, 0, 0),
            []
        )
        assert triggered is not None
        assert triggered.new_state == PatientState.CRITICALLY_UNWELL

    def test_apply_state_change(self):
        """Test applying a state change records history."""
        rule = StateChangeRule(
            trigger_type="time_elapsed",
            trigger_time=datetime(2024, 1, 15, 21, 0, 0),
            new_state=PatientState.DETERIORATING,
            clinical_manifestation="Patient worse",
            notification_message="Deteriorating"
        )

        patient = Patient(
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory()
        )

        state_change = patient.apply_state_change(
            rule,
            datetime(2024, 1, 15, 21, 0, 0)
        )

        assert patient.current_state == PatientState.DETERIORATING
        assert len(patient.state_history) == 1
        assert state_change.old_state == PatientState.STABLE
        assert state_change.new_state == PatientState.DETERIORATING


class TestSimulationSession:
    """Test the complete simulation session orchestration."""

    def test_session_initialization(self):
        """Test session initializes correctly."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()
        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        session = SimulationSession(
            scenario_id="test_001",
            clock=clock
        )

        assert session.scenario_id == "test_001"
        current_time = session.clock.get_current_time()
        assert abs((current_time - scenario_start).total_seconds()) < 5
        assert len(session.action_history) == 0
        assert session.is_complete is False

    def test_execute_action_advances_time(self):
        """Test executing action advances time correctly (in-person review adds artificial time)."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()
        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        # Create patient
        patient = Patient(
            patient_id="pt_001",
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory()
        )

        session = SimulationSession(
            scenario_id="test_001",
            clock=clock,
            patients={"pt_001": patient}
        )

        # Execute in-person review (adds 30 min of artificial time)
        action = UserAction(
            action_type="review_in_person",
            patient_id="pt_001",
            details={"location": "Ward 1"}
        )

        result = session.execute_action(action)

        assert result.success is True
        # Should have added 30 mins of artificial time
        assert session.clock.artificial_minutes_added == 30
        # Total elapsed should be 30 (minimal real time + 30 artificial)
        assert session.clock.get_elapsed_minutes() == 30

    def test_execute_action_triggers_events(self):
        """Test action execution processes due events."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()
        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        patient = Patient(
            patient_id="pt_001",
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory()
        )

        session = SimulationSession(
            scenario_id="test_001",
            clock=clock,
            patients={"pt_001": patient}
        )

        # Schedule event at 20:15 (15 mins after start)
        event = Event(
            event_type="investigation_result",
            scheduled_time=datetime(2024, 1, 15, 20, 15, 0),
            patient_id="pt_001",
            data={
                "investigation_type": "ABG",
                "notification_message": "ABG results available"
            }
        )
        session.scheduler.schedule(event, datetime(2024, 1, 15, 20, 15, 0))

        # Execute in-person review (adds 30 mins artificial time, so sim time goes to 20:30)
        action = UserAction(
            action_type="review_in_person",
            patient_id="pt_001"
        )

        result = session.execute_action(action)

        # Event should have been triggered (20:15 < 20:30)
        assert len(result.triggered_events) == 1
        assert "ABG results available" in result.new_notifications

    def test_execute_action_triggers_state_change(self):
        """Test action execution triggers patient state changes."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()
        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        # Create rule: deteriorate at 20:30 (30 mins after start)
        rule = StateChangeRule(
            trigger_type="time_elapsed",
            trigger_time=datetime(2024, 1, 15, 20, 30, 0),
            new_state=PatientState.DETERIORATING,
            clinical_manifestation="Patient worse",
            notification_message="Patient deteriorating"
        )

        patient = Patient(
            patient_id="pt_001",
            name="Test Patient",
            mrn="MRN001",
            age=70,
            gender="Female",
            ward="Ward 1",
            bed="Bed 1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory(state_change_rules=[rule])
        )

        session = SimulationSession(
            scenario_id="test_001",
            clock=clock,
            patients={"pt_001": patient}
        )

        # Execute in-person review (adds 30 mins, so sim time → 20:30)
        action = UserAction(
            action_type="review_in_person",
            patient_id="pt_001"
        )

        result = session.execute_action(action)

        # Patient should have changed state (sim time reached 20:30)
        assert len(result.patient_state_changes) == 1
        assert patient.current_state == PatientState.DETERIORATING
        assert "Patient deteriorating" in result.new_notifications

    def test_session_determinism(self):
        """Test that same actions produce consistent results (artificial time is deterministic)."""
        def create_session():
            scenario_start = datetime(2024, 1, 15, 20, 0, 0)
            # Use same session_start for both to ensure determinism
            session_start = datetime(2024, 1, 15, 19, 55, 0)  # Fixed time
            clock = SimulationClock(
                scenario_start_time=scenario_start,
                session_start_time=session_start
            )

            rule = StateChangeRule(
                trigger_type="time_elapsed",
                trigger_time=datetime(2024, 1, 15, 21, 0, 0),
                new_state=PatientState.DETERIORATING,
                clinical_manifestation="Worse",
                notification_message="Deteriorating"
            )

            patient = Patient(
                patient_id="pt_001",
                name="Test",
                mrn="MRN001",
                age=70,
                gender="F",
                ward="W1",
                bed="B1",
                current_state=PatientState.STABLE,
                trajectory=PatientTrajectory(state_change_rules=[rule])
            )

            return SimulationSession(
                scenario_id="test",
                clock=clock,
                patients={"pt_001": patient}
            )

        # Run same sequence twice
        session1 = create_session()
        session2 = create_session()

        actions = [
            UserAction(action_type="review_in_person", patient_id="pt_001"),  # Adds 30 artificial mins
            UserAction(action_type="document_note", patient_id="pt_001"),     # No artificial time
            UserAction(action_type="escalate", patient_id="pt_001")            # No artificial time
        ]

        for action in actions:
            session1.execute_action(action)
            session2.execute_action(action)

        # Artificial time added should be identical (only review_in_person adds time)
        assert session1.clock.artificial_minutes_added == session2.clock.artificial_minutes_added
        assert session1.clock.artificial_minutes_added == 30  # Only one in-person review

        # Final states should be identical
        assert session1.patients["pt_001"].current_state == session2.patients["pt_001"].current_state

    def test_complete_session(self):
        """Test session completion."""
        scenario_start = datetime(2024, 1, 15, 20, 0, 0)
        session_start = datetime.now()
        clock = SimulationClock(
            scenario_start_time=scenario_start,
            session_start_time=session_start
        )

        patient = Patient(
            patient_id="pt_001",
            name="Test",
            mrn="MRN001",
            age=70,
            gender="F",
            ward="W1",
            bed="B1",
            current_state=PatientState.STABLE,
            trajectory=PatientTrajectory()
        )

        session = SimulationSession(
            scenario_id="test",
            clock=clock,
            patients={"pt_001": patient}
        )

        # Take some actions
        session.execute_action(
            UserAction(action_type="review_in_person", patient_id="pt_001")
        )

        # Complete session
        summary = session.complete_session()

        assert session.is_complete is True
        assert session.completed_at is not None
        assert summary["total_actions"] == 1
        # Total time = minimal real time + 30 artificial mins from in-person review
        assert summary["total_time_elapsed_minutes"] == 30
