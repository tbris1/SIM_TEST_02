"""
Demonstration of the HYBRID REAL-TIME clock.

Key difference from original:
- Clock runs in REAL TIME (like a stopwatch)
- In-person reviews add ARTIFICIAL TIME (+30 mins)
- Total sim time = Real elapsed + Artificial penalties

This creates time pressure - students can't pause forever!
"""

import time
from datetime import datetime
from app.models.simulation import SimulationClock, SimulationSession, EventScheduler
from app.models.patient import Patient, PatientState, PatientTrajectory, StateChangeRule
from app.models.actions import UserAction
from app.models.events import Event


def print_separator():
    print("\n" + "=" * 70 + "\n")


def print_clock_state(session: SimulationSession):
    """Print detailed clock state."""
    state = session.clock.get_state()
    print(f"⏰ Simulation Time: {state['formatted_time']} (Total: {state['formatted_elapsed']})")
    print(f"   ├─ Real elapsed: {state['real_elapsed_minutes']} mins")
    print(f"   └─ Artificial added: {state['artificial_minutes_added']} mins")


def main():
    print_separator()
    print("🏥 HYBRID REAL-TIME SIMULATION - DEMONSTRATION")
    print_separator()

    print("⏱️  CLOCK MODEL:")
    print("   • Simulation clock runs in REAL TIME")
    print("   • In-person reviews add +30 mins ARTIFICIAL time")
    print("   • Total time = Real elapsed + Artificial penalties")
    print("   • This creates time pressure!")

    # Initialize hybrid clock
    scenario_start = datetime(2024, 1, 15, 20, 0, 0)  # Shift starts at 20:00
    session_start = datetime.now()  # Right now in real time

    clock = SimulationClock(
        scenario_start_time=scenario_start,
        session_start_time=session_start
    )

    print_separator()
    print(f"Session started at: {session_start.strftime('%H:%M:%S')} (real time)")
    print(f"Scenario starts at: 20:00 (simulation time)")

    # Create patient with trajectory
    rule_deteriorate = StateChangeRule(
        trigger_type="time_elapsed",
        trigger_time=datetime(2024, 1, 15, 20, 30, 0),  # Deteriorates at 20:30
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

    trajectory = PatientTrajectory(
        state_change_rules=[rule_deteriorate, rule_stabilize]
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
        scenario_id="demo_realtime_001",
        clock=clock,
        patients={"pt_001": patient}
    )

    # Schedule initial nurse call at 20:05
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

    print_separator()
    print_clock_state(session)

    # Simulate student thinking/working
    print_separator()
    print("Student is thinking about the patient... (5 seconds real time)")
    print("⏳ REAL TIME IS PASSING...")
    time.sleep(5)

    print_clock_state(session)
    print("\n💡 Notice: Simulation time advanced by ~5 mins (real time elapsed)")

    # Action 1: Chat with nurse (no artificial time)
    print_separator()
    print("ACTION 1: Chat with nurse - 'What are the observations?'")
    action1 = UserAction(
        action_type="ask_nurse_question",
        patient_id="pt_001",
        details={"question": "What are the current observations?"}
    )
    result1 = session.execute_action(action1)

    print_clock_state(session)
    print(f"\n✓ Action completed (nurse chat adds NO artificial time)")

    if result1.new_notifications:
        print("\n📢 New notifications:")
        for notif in result1.new_notifications:
            print(f"  - {notif}")

    # More real time passing
    print_separator()
    print("Student reviewing EHR notes... (3 seconds real time)")
    print("⏳ REAL TIME CONTINUES...")
    time.sleep(3)

    print_clock_state(session)

    # Action 2: In-person review (ADDS ARTIFICIAL TIME)
    print_separator()
    print("ACTION 2: Review patient in person")
    print("   → This adds +30 mins ARTIFICIAL time (simulates travel + assessment)")
    action2 = UserAction(
        action_type="review_in_person",
        patient_id="pt_001",
        details={"location": "Ward 4A, Bed 12"}
    )
    result2 = session.execute_action(action2)

    print_clock_state(session)
    print(f"\n✓ Action completed")
    print(f"   Time advanced: {result2.time_advanced_minutes} mins")
    print(f"   (Real time: ~8 mins + Artificial: 30 mins = ~38 mins total)")

    if result2.patient_state_changes:
        print("\n⚠️  PATIENT STATE CHANGES:")
        for change in result2.patient_state_changes:
            print(f"  - {change['patient_name']}: {change['old_state']} → {change['new_state']}")
            print(f"    {change['message']}")

    if result2.new_notifications:
        print("\n📢 New notifications:")
        for notif in result2.new_notifications:
            print(f"  - {notif}")

    # Action 3: Escalate (no artificial time)
    print_separator()
    print("ACTION 3: Escalate to registrar")
    action3 = UserAction(
        action_type="escalate",
        patient_id="pt_001",
        details={
            "escalate_to": "registrar",
            "reason": "Type 2 respiratory failure, patient deteriorating"
        }
    )
    result3 = session.execute_action(action3)

    print_clock_state(session)
    print(f"\n✓ Escalation completed (adds NO artificial time)")

    if result3.patient_state_changes:
        print("\n✅ PATIENT STATE CHANGES:")
        for change in result3.patient_state_changes:
            print(f"  - {change['patient_name']}: {change['old_state']} → {change['new_state']}")
            print(f"    {change['message']}")

    # Complete session
    print_separator()
    summary = session.complete_session()

    print("📊 SESSION SUMMARY")
    print(f"Total simulation time: {summary['total_time_elapsed_minutes']} mins")
    print(f"Real time elapsed: {session.clock.get_state()['real_elapsed_minutes']} mins")
    print(f"Artificial time added: {session.clock.artificial_minutes_added} mins")
    print(f"Total actions: {summary['total_actions']}")

    print("\n👥 Patient outcome:")
    for patient_id, patient_summary in summary['patients'].items():
        print(f"  {patient_summary['name']}: {patient_summary['final_state']}")

    print_separator()
    print("✅ Demo complete!")
    print("\n🎯 KEY INSIGHTS:")
    print("   1. Real time creates pressure - students can't pause forever")
    print("   2. In-person reviews are 'expensive' (+30 mins)")
    print("   3. Other actions (chat, escalate) happen in 'real time'")
    print("   4. This balances realism with practical time management training")
    print_separator()


if __name__ == "__main__":
    main()
