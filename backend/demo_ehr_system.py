"""
Demonstration script for the EHR system with progressive revelation.
Shows how clinical data becomes visible over time and with user actions.
"""

from datetime import datetime, timedelta
from app.services.scenario_loader import scenario_loader
from app.services.ehr_service import ehr_service
from app.models.actions import UserAction


def print_separator():
    print("\n" + "=" * 70 + "\n")


def print_ehr_summary(patient_id, session):
    """Print summary of what's currently visible in EHR."""
    patient = session.patients[patient_id]
    current_time = session.clock.get_current_time()
    actions_taken = [action["action_type"] for action in patient.actions_taken]

    # Get visibility summary
    summary = ehr_service.get_visibility_summary(patient_id)

    # Get filtered view
    record_view = ehr_service.get_patient_record_view(
        patient_id,
        current_time,
        actions_taken
    )

    if not record_view:
        print("No EHR record found for this patient")
        return

    print(f"📋 EHR for {record_view.name} (MRN: {record_view.mrn})")
    print(f"   Age: {record_view.age}, Gender: {record_view.gender}")

    # Always visible summary data
    print(f"\n   🚨 Allergies: {', '.join(record_view.allergies) if record_view.allergies else 'None'}")
    print(f"   🏥 Active Diagnoses: {', '.join(record_view.active_diagnoses)}")
    print(f"   💊 Medications: {len(record_view.current_medications)} active")

    # Visibility statistics
    print(f"\n   📝 Clinical Notes: {summary['notes']['visible']}/{summary['notes']['total']} visible")
    print(f"   🔬 Results: {summary['results']['visible']}/{summary['results']['total']} visible")

    # Show visible notes
    if record_view.visible_notes:
        print(f"\n   📄 Visible Clinical Notes:")
        for note in record_view.visible_notes:
            print(f"      • {note.title} ({note.note_type.value})")
            print(f"        By {note.author} ({note.author_role}) at {note.timestamp.strftime('%H:%M')}")

    # Show visible results
    if record_view.visible_results:
        print(f"\n   🧪 Visible Investigation Results:")
        for result in record_view.visible_results:
            print(f"      • {result.investigation_type}")
            print(f"        Resulted: {result.resulted_time.strftime('%H:%M')}")
            if result.interpretation:
                print(f"        Interpretation: {result.interpretation}")


def main():
    print_separator()
    print("🏥 EHR SYSTEM DEMONSTRATION - PROGRESSIVE REVELATION")
    print_separator()

    print("This demo shows how clinical information is progressively revealed")
    print("in the EHR system based on time and user actions.")
    print("\nLoading scenario: simple_test_ehr...")

    # Load scenario with EHR data
    try:
        session = scenario_loader.create_session_from_scenario("simple_test_ehr")
        patient_id = "pt_001"
    except FileNotFoundError:
        print("\n❌ Error: simple_test_ehr.json scenario not found.")
        print("Using simple_test_001 scenario instead (no EHR data will be available)")
        session = scenario_loader.create_session_from_scenario("simple_test_001")
        patient_id = "pt_001"

    print_separator()
    print("📊 INITIAL STATE (20:00 - Start of shift)")
    print_separator()

    state = session.get_state()
    print(f"⏰ Time: {state['clock']['formatted_time']}")
    print(f"👥 Patient: {session.patients[patient_id].name}")
    print(f"   State: {session.patients[patient_id].current_state.value}")

    if ehr_service.has_record(patient_id):
        print_separator()
        print("📋 INITIAL EHR VIEW")
        print("   (All existing clinical notes are visible)")
        print_separator()
        print_ehr_summary(patient_id, session)
    else:
        print("\n   No EHR data loaded for this scenario")

    # Simulate passage of time - chat with nurse
    print_separator()
    print("ACTION 1: Chat with nurse (2 mins)")
    print("   Asking about patient's current condition...")
    print_separator()

    action1 = UserAction(
        action_type="ask_nurse_question",
        patient_id=patient_id,
        details={"question": "What are the current observations?"}
    )
    result1 = session.execute_action(action1)
    print(f"✓ Action completed at {result1.new_simulation_time.strftime('%H:%M')}")

    if result1.new_notifications:
        print("\n📢 New notifications:")
        for notif in result1.new_notifications:
            print(f"   - {notif}")

    if ehr_service.has_record(patient_id):
        print_ehr_summary(patient_id, session)
        print("\n   💡 No changes to EHR - all existing notes already visible")
        print("      (Investigation results will appear when they're resulted)")

    # Review patient in person
    print_separator()
    print("ACTION 2: Review patient in person (30 mins)")
    print("   Traveling to ward and conducting physical assessment...")
    print_separator()

    action2 = UserAction(
        action_type="review_in_person",
        patient_id=patient_id,
        details={"location": "Ward 4A, Bed 12"}
    )
    result2 = session.execute_action(action2)
    print(f"✓ Action completed at {result2.new_simulation_time.strftime('%H:%M')}")

    if result2.new_notifications:
        print("\n📢 New notifications:")
        for notif in result2.new_notifications:
            print(f"   - {notif}")

    if ehr_service.has_record(patient_id):
        print_separator()
        print("📋 UPDATED EHR VIEW")
        print("   (After in-person review - NEW examination note generated!)")
        print_separator()
        print_ehr_summary(patient_id, session)
        print("\n   ✨ NEW examination note generated!")
        print("      • In-person review creates a new clinical note")
        print("      • Note contains physical examination findings based on patient's state")
        print("      • Investigation results also now available (time elapsed)")

    # Document findings
    print_separator()
    print("ACTION 3: Document clinical findings (5 mins)")
    print_separator()

    action3 = UserAction(
        action_type="document_note",
        patient_id=patient_id,
        details={
            "note_content": "Patient reviewed. Increased work of breathing. Plan: ABG, consider escalation."
        }
    )
    result3 = session.execute_action(action3)
    print(f"✓ Action completed at {result3.new_simulation_time.strftime('%H:%M')}")

    # Show final timeline
    print_separator()
    print("📅 SESSION TIMELINE")
    print_separator()

    timeline = session.get_timeline()
    for i, entry in enumerate(timeline[:10], 1):  # Show first 10 events
        time_str = entry['timestamp'][:16] if isinstance(entry['timestamp'], str) else entry['timestamp'].strftime('%H:%M')
        entry_type = entry['type']

        if entry_type == 'action':
            action_data = entry['data']['action']
            print(f"{i}. [{time_str}] ACTION: {action_data['action_type']} for {action_data['patient_id']}")
        elif entry_type == 'notification':
            notif_data = entry['data']
            print(f"{i}. [{time_str}] NOTIFICATION: {notif_data.get('message', notif_data.get('type'))}")

    # Summary of EHR system features
    print_separator()
    print("🎯 EHR SYSTEM FEATURES DEMONSTRATED")
    print_separator()
    print("✓ All existing clinical notes always visible (realistic EHR access)")
    print("✓ Dynamic examination note generation on in-person review")
    print("✓ Examination findings based on patient's current clinical state")
    print("✓ Time-based visibility for investigation results")
    print("✓ Investigation ordering without requiring in-person review")
    print("✓ Always-visible summary data (allergies, diagnoses, medications)")
    print("✓ Integration with simulation timeline and actions")

    if ehr_service.has_record(patient_id):
        print_separator()
        print("📊 FINAL STATISTICS")
        print_separator()

        summary = ehr_service.get_visibility_summary(patient_id)
        print(f"Clinical Notes: {summary['notes']['visible']}/{summary['notes']['total']} visible")
        print(f"Investigation Results: {summary['results']['visible']}/{summary['results']['total']} visible")

        hidden_notes = summary['notes']['total'] - summary['notes']['visible']
        hidden_results = summary['results']['total'] - summary['results']['visible']

        if hidden_results > 0:
            print(f"\n💡 Still hidden: {hidden_results} investigation results")
            print("   (Will become visible when resulted)")

    print_separator()
    print("✅ Demo completed successfully!")
    print_separator()


if __name__ == "__main__":
    main()
