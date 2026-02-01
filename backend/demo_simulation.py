"""
Demonstration script showing the simulation engine in action.
Runs through a simple scenario without needing the API or frontend.
"""

from datetime import datetime
from app.models.simulation import SimulationClock, SimulationSession, EventScheduler
from app.models.patient import Patient, PatientState, PatientTrajectory, StateChangeRule
from app.models.actions import UserAction
from app.models.events import Event


def print_separator():
    print("\n" + "=" * 70 + "\n")


def print_session_state(session: SimulationSession):
    """Print current session state."""
    state = session.get_state()
    print(f"⏰ Time: {state['clock']['formatted_time']} (Elapsed: {state['clock']['formatted_elapsed']})")
    print(f"📊 Actions taken: {state['action_count']}")
    print(f"📢 Notifications: {state['notification_count']}")

    print("\n👥 Patients:")
    for patient_id, patient_data in state['patients'].items():
        print(f"  - {patient_data['name']} ({patient_data['ward']}, {patient_data['bed']})")
        print(f"    State: {patient_data['current_state']}")


def main():
    print_separator()
    print("🏥 MEDICAL ON-CALL SIMULATION - DEMONSTRATION")
    print_separator()

    # Initialize simulation at 20:00 (8 PM)
    start_time = datetime(2024, 1, 15, 20, 0, 0)
    clock = SimulationClock(start_time=start_time, current_time=start_time)

    print("Starting simulation at 20:00 (night shift begins)")
    print_separator()

    # Create patient with state trajectory
    print("Creating patient: Margaret Thompson, 72F")
    print("Initial state: Stable with concerns (admitted with shortness of breath)")
    print("\nClinical trajectory rules:")
    print("  1. Deteriorates at 21:30 if not escalated")
    print("  2. Stabilizes immediately if escalated")
    print("  3. Becomes critical at 22:00 if still not escalated")

    rule_deteriorate = StateChangeRule(
        trigger_type="time_elapsed",
        trigger_time=datetime(2024, 1, 15, 21, 30, 0),
        current_state_requirement=PatientState.STABLE_WITH_CONCERNS,
        new_state=PatientState.DETERIORATING,
        clinical_manifestation="Increased work of breathing, O2 sats 88%",
        notification_message="🚨 Nurse calling: Margaret Thompson more breathless",
        urgency="high"
    )

    rule_stabilize = StateChangeRule(
        trigger_type="escalation_occurred",
        new_state=PatientState.STABLE,
        clinical_manifestation="Registrar started NIV, patient improving",
        notification_message="✅ Patient stabilized after senior review",
        urgency="low"
    )

    rule_critical = StateChangeRule(
        trigger_type="action_not_taken",
        required_action="escalate",
        action_deadline=datetime(2024, 1, 15, 22, 0, 0),
        current_state_requirement=PatientState.DETERIORATING,
        new_state=PatientState.CRITICALLY_UNWELL,
        clinical_manifestation="Patient drowsy, suspected CO2 retention",
        notification_message="🆘 URGENT: Margaret Thompson critically unwell",
        urgency="critical"
    )

    trajectory = PatientTrajectory(
        state_change_rules=[rule_deteriorate, rule_stabilize, rule_critical]
    )

    patient = Patient(
        patient_id="pt_001",
        name="Margaret Thompson",
        mrn="MRN12345",
        age=72,
        gender="Female",
        ward="Ward 4A",
        bed="Bed 12",
        current_state=PatientState.STABLE_WITH_CONCERNS,
        trajectory=trajectory
    )

    # Create session
    session = SimulationSession(
        scenario_id="demo_001",
        clock=clock,
        patients={"pt_001": patient}
    )

    # Schedule initial request
    initial_request = Event(
        event_type="new_request",
        scheduled_time=datetime(2024, 1, 15, 20, 5, 0),
        patient_id="pt_001",
        data={
            "request_type": "nurse_call",
            "notification_message": "📞 Nurse calling from Ward 4A about Margaret Thompson"
        }
    )
    session.scheduler.schedule(initial_request, datetime(2024, 1, 15, 20, 5, 0))

    # Schedule ABG results
    abg_results = Event(
        event_type="investigation_result",
        scheduled_time=datetime(2024, 1, 15, 20, 30, 0),
        patient_id="pt_001",
        data={
            "investigation_type": "ABG",
            "notification_message": "📋 ABG results available: pH 7.32, pCO2 7.8 (Type 2 resp failure)"
        }
    )
    session.scheduler.schedule(abg_results, datetime(2024, 1, 15, 20, 30, 0))

    print_separator()
    print_session_state(session)

    # Action 1: Initial triage with nurse (would normally be chat, here just time advance)
    print_separator()
    print("ACTION 1: Triage with nurse over phone (2 mins)")
    action1 = UserAction(
        action_type="ask_nurse_question",
        patient_id="pt_001",
        details={"question": "What are the current observations?"}
    )
    result1 = session.execute_action(action1)
    print(f"✓ Time advanced: {result1.time_advanced_minutes} mins")

    if result1.new_notifications:
        print("\n📢 New notifications:")
        for notif in result1.new_notifications:
            print(f"  - {notif}")

    print_session_state(session)

    # Action 2: Review patient in person
    print_separator()
    print("ACTION 2: Review patient in person (30 mins including travel)")
    action2 = UserAction(
        action_type="review_in_person",
        patient_id="pt_001",
        details={"location": "Ward 4A, Bed 12"}
    )
    result2 = session.execute_action(action2)
    print(f"✓ Time advanced: {result2.time_advanced_minutes} mins")

    if result2.new_notifications:
        print("\n📢 New notifications:")
        for notif in result2.new_notifications:
            print(f"  - {notif}")

    print_session_state(session)

    # Action 3: Document findings
    print_separator()
    print("ACTION 3: Document clinical findings (5 mins)")
    action3 = UserAction(
        action_type="document_note",
        patient_id="pt_001",
        details={
            "note_content": "Patient reviewed. Increased work of breathing. Type 2 resp failure."
        }
    )
    result3 = session.execute_action(action3)
    print(f"✓ Time advanced: {result3.time_advanced_minutes} mins")

    print_session_state(session)

    # Action 4: Continue with other tasks (time passes, reaches 21:30)
    print_separator()
    print("ACTION 4: Document handover notes for other patients (53 mins)")
    print("(This will advance time past 21:30...)")
    action4 = UserAction(
        action_type="document_note",
        patient_id="pt_001",
        details={"note_content": "Handover notes"},
        time_cost_minutes=53  # Advance to 21:30
    )
    result4 = session.execute_action(action4)
    print(f"✓ Time advanced: {result4.time_advanced_minutes} mins")

    if result4.patient_state_changes:
        print("\n⚠️  PATIENT STATE CHANGES:")
        for change in result4.patient_state_changes:
            print(f"  - {change['patient_name']}: {change['old_state']} → {change['new_state']}")
            print(f"    {change['message']}")

    if result4.new_notifications:
        print("\n📢 New notifications:")
        for notif in result4.new_notifications:
            print(f"  - {notif}")

    print_session_state(session)

    # Action 5: Escalate to senior
    print_separator()
    print("ACTION 5: Escalate to registrar (5 mins)")
    action5 = UserAction(
        action_type="escalate",
        patient_id="pt_001",
        details={
            "escalate_to": "registrar",
            "reason": "Type 2 respiratory failure, patient deteriorating"
        }
    )
    result5 = session.execute_action(action5)
    print(f"✓ Time advanced: {result5.time_advanced_minutes} mins")

    if result5.patient_state_changes:
        print("\n✅ PATIENT STATE CHANGES:")
        for change in result5.patient_state_changes:
            print(f"  - {change['patient_name']}: {change['old_state']} → {change['new_state']}")
            print(f"    {change['message']}")

    print_session_state(session)

    # Complete session
    print_separator()
    print("Completing session...")
    summary = session.complete_session()

    print("\n📊 SESSION SUMMARY")
    print(f"Total elapsed time: {summary['total_time_elapsed_minutes']} minutes")
    print(f"Total actions: {summary['total_actions']}")

    print("\n👥 Patient outcomes:")
    for patient_id, patient_summary in summary['patients'].items():
        print(f"  {patient_summary['name']}:")
        print(f"    Final state: {patient_summary['final_state']}")
        print(f"    State changes: {patient_summary['state_changes']}")
        print(f"    Actions taken: {patient_summary['actions_taken']}")

    print("\n📅 Timeline:")
    for i, event in enumerate(summary['timeline'][:10], 1):  # Show first 10 events
        event_type = event['type']
        if event_type == 'action':
            action_data = event['data']['action']
            print(f"  {i}. [{event['elapsed_minutes']}m] ACTION: {action_data['action_type']}")
        elif event_type == 'notification':
            notif_data = event['data']
            print(f"  {i}. NOTIFICATION: {notif_data.get('message', 'N/A')}")

    print_separator()
    print("✅ Demonstration complete!")
    print("\nKey takeaways:")
    print("  • Time advances only when user takes actions (deterministic)")
    print("  • Events trigger at specific sim times (investigation results)")
    print("  • Patient states change based on rules (deterioration, stabilization)")
    print("  • All actions, events, and state changes are recorded in timeline")
    print_separator()


if __name__ == "__main__":
    main()
