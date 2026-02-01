"""
Demo script for testing the API manually.
Run the API server first: uvicorn app.main:app --reload
Then run this script in another terminal.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000/api/v1"


def demo_api():
    """Demonstrate complete API workflow."""

    print("=" * 60)
    print("Medical On-Call Simulation API Demo")
    print("=" * 60)

    # 1. List available scenarios
    print("\n1️⃣  Listing available scenarios...")
    response = requests.get(f"{BASE_URL}/scenarios")
    scenarios = response.json()
    print(f"   Found {len(scenarios)} scenario(s)")
    for scenario in scenarios:
        print(f"   - {scenario['scenario_id']}: {scenario['title']}")

    # 2. Start a new session
    print("\n2️⃣  Starting new simulation session...")
    response = requests.post(
        f"{BASE_URL}/sessions/start",
        json={"scenario_id": "simple_test_001"}
    )
    session = response.json()
    session_id = session["session_id"]
    print(f"   Session created: {session_id}")
    print(f"   Scenario start time: {session['current_time']}")
    print(f"   Elapsed: {session['elapsed_minutes']} minutes")

    # 3. Get session state
    print("\n3️⃣  Getting session state...")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}")
    state = response.json()
    print(f"   Patients: {len(state['patients'])}")
    print(f"   Pending events: {state['scheduler']['pending_events']}")
    print(f"   Actions taken: {state['action_count']}")

    # 4. Get patient details
    print("\n4️⃣  Getting patient details...")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/patients/pt_001")
    patient = response.json()
    print(f"   Patient: {patient['name']}, {patient['age']}yo {patient['gender']}")
    print(f"   Location: {patient['ward']}, {patient['bed']}")
    print(f"   Current state: {patient['current_state']}")

    # 5. Execute action - Review patient
    print("\n5️⃣  Reviewing patient in person...")
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/actions",
        json={
            "action_type": "review_in_person",
            "patient_id": "pt_001",
            "details": {"location": "Ward 4A, Bed 12"},
            "time_cost_minutes": 30
        }
    )
    result = response.json()
    print(f"   Success: {result['success']}")
    print(f"   Time advanced: {result['time_advanced_minutes']} minutes")
    print(f"   New simulation time: {result['new_simulation_time']}")
    print(f"   Notifications: {len(result['new_notifications'])}")
    for notification in result['new_notifications']:
        print(f"     - {notification}")

    # 6. Execute action - Escalate
    print("\n6️⃣  Escalating to registrar...")
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/actions/escalate",
        params={
            "patient_id": "pt_001",
            "escalate_to": "registrar",
            "reason": "Type 2 respiratory failure"
        }
    )
    result = response.json()
    print(f"   Success: {result['success']}")
    print(f"   Patient state changes: {len(result['patient_state_changes'])}")
    for change in result['patient_state_changes']:
        print(f"     - {change['old_state']} → {change['new_state']}")
        print(f"       {change['message']}")

    # 7. Get session timeline
    print("\n7️⃣  Getting session timeline...")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/timeline")
    timeline = response.json()
    print(f"   Timeline entries: {len(timeline['timeline'])}")
    for i, entry in enumerate(timeline['timeline'][:5]):  # Show first 5
        print(f"     {i+1}. [{entry['type']}] {entry['timestamp']}")

    # 8. Complete session
    print("\n8️⃣  Completing session...")
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/complete")
    summary = response.json()
    print(f"   Total time elapsed: {summary['total_time_elapsed_minutes']} minutes")
    print(f"   Total actions: {summary['total_actions']}")
    print(f"   Patients:")
    for patient_id, patient_data in summary['patients'].items():
        print(f"     - {patient_data['name']}: {patient_data['final_state']}")
        print(f"       Actions taken: {patient_data['actions_taken']}")
        print(f"       State changes: {patient_data['state_changes']}")

    # 9. List all sessions
    print("\n9️⃣  Listing all active sessions...")
    response = requests.get(f"{BASE_URL}/sessions")
    sessions = response.json()
    print(f"   Active sessions: {sessions['count']}")

    # 10. Delete session
    print("\n🔟 Deleting session...")
    response = requests.delete(f"{BASE_URL}/sessions/{session_id}")
    result = response.json()
    print(f"   Deleted: {result['deleted']}")

    print("\n" + "=" * 60)
    print("✅ API Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
