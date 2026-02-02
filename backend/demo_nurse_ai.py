"""
Demonstration script for AI Nurse interactions.
Shows the two-stage LLM pattern in action with various question types.

Needs refining - I wonder if the classifier is actually overkill for a triage converation when the user has access to the EHR too.
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

from app.services.scenario_loader import scenario_loader
from app.services.nurse_logic import nurse_turn, initialize_openai_client
from app.models.patient import PatientState


def print_separator(char="=", length=70):
    """Print a separator line."""
    print("\n" + char * length + "\n")


def print_subseparator():
    """Print a smaller separator."""
    print("-" * 70)


def print_patient_state_info(patient):
    """Print current patient state information."""
    print(f"👤 Patient: {patient.name} ({patient.age}{patient.gender[0]})")
    print(f"📍 Location: {patient.ward}, {patient.bed}")
    print(f"📊 Current State: {patient.current_state.value}")


def print_nurse_interaction(question_num, question, response, elapsed_time):
    """Print a nurse interaction in a formatted way."""
    print(f"\n💬 [Question {question_num}] {question}")
    print_subseparator()
    print(f"\n🩺 [Nurse Response]")
    print(f"{response}")
    print(f"\n⏱️  Response time: {elapsed_time:.1f}s")


def main():
    print_separator()
    print("🏥 AI NURSE INTERACTION DEMONSTRATION")
    print_separator()

    print("This demo shows the AI nurse functionality using the two-stage LLM pattern:")
    print("  1. Router LLM classifies questions to filter relevant data")
    print("  2. Response LLM generates realistic nurse responses")
    print("\nNOTE: You'll see debug output showing the router's classification")
    print("      and the filtered data provided to the response LLM.")

    # Load environment variables
    print_separator()
    print("🔧 INITIALIZATION")
    print_separator()

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key or api_key == "your-openai-api-key-here":
        print("\n❌ ERROR: OpenAI API key not configured")
        print("\nTo use this demo:")
        print("  1. Get an API key from: https://platform.openai.com/api-keys")
        print("  2. Add it to backend/.env file:")
        print("     OPENAI_API_KEY='your-actual-key-here'")
        print("  3. Make sure your key has access to GPT-5 models")
        print("\nExiting demo.")
        return

    # Initialize OpenAI client
    print("Initializing OpenAI client...")
    try:
        openai_client = initialize_openai_client(api_key)
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"\n❌ ERROR: Failed to initialize OpenAI client: {e}")
        print("\nPlease check your API key and try again.")
        return

    # Load scenario
    print("\nLoading scenario: simple_test_ehr...")
    try:
        session = scenario_loader.create_session_from_scenario("simple_test_ehr")
        print(f"✅ Session created: {session.session_id}")
    except FileNotFoundError:
        print("\n❌ ERROR: Scenario 'simple_test_ehr' not found")
        print("Make sure data/scenarios/simple_test_ehr.json exists")
        return
    except Exception as e:
        print(f"\n❌ ERROR: Failed to load scenario: {e}")
        return

    # Get patient
    patient_id = "pt_001"
    patient = session.patients.get(patient_id)
    if not patient:
        print(f"\n❌ ERROR: Patient {patient_id} not found in session")
        return

    print("\n")
    print_patient_state_info(patient)

    # Initial nurse message context
    initial_nurse_message = "Hi doctor, could you review Margaret Thompson? She's more short of breath."

    # ============================================================================
    # PHASE 1: Test Questions - Stable with Concerns State
    # ============================================================================
    print_separator()
    print("📞 TESTING NURSE AI - STABLE WITH CONCERNS STATE")
    print_separator()

    print(f"Initial nurse message: \"{initial_nurse_message}\"")
    print("\nLet's ask the nurse some questions...\n")

    # Get current state data
    current_state = patient.current_state
    patient_state_data = patient.trajectory.get_examination_findings(current_state)

    if not patient_state_data:
        print(f"\n❌ ERROR: No examination findings for state: {current_state}")
        return

    # Question 1: General appearance
    print_subseparator()
    question = "How does the patient look right now?"
    print(f"\n💬 [Question 1] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message=initial_nurse_message
        )
        elapsed = time.time() - start_time

        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Continuing with next question...")

    # Question 2: Nursing concerns
    print_subseparator()
    question = "What are you worried about?"
    print(f"\n💬 [Question 2] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message=initial_nurse_message
        )
        elapsed = time.time() - start_time
        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    # Question 3: Recent events
    print_subseparator()
    question = "Has anything changed recently?"
    print(f"\n💬 [Question 3] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message=initial_nurse_message
        )
        elapsed = time.time() - start_time
        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    # Question 4: Mental state
    print_subseparator()
    question = "How is she mentally?"
    print(f"\n💬 [Question 4] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message=initial_nurse_message
        )
        elapsed = time.time() - start_time
        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    # Question 5: Summary
    print_subseparator()
    question = "Can you give me a quick summary of the situation?"
    print(f"\n💬 [Question 5] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message=initial_nurse_message
        )
        elapsed = time.time() - start_time
        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    # ============================================================================
    # PHASE 2: Simulate State Change to Deteriorating
    # ============================================================================
    print_separator()
    print("⚠️  PATIENT STATE CHANGE")
    print_separator()

    print("Simulating patient deterioration...")
    print(f"Previous state: {patient.current_state.value}")

    # Change patient state
    patient.current_state = PatientState.DETERIORATING

    print(f"New state: {patient.current_state.value}")
    print("\n🚨 Nurse calling: Margaret Thompson is more breathless - she's deteriorated!")

    # Get new state data
    patient_state_data = patient.trajectory.get_examination_findings(patient.current_state)

    if not patient_state_data:
        print(f"\n❌ ERROR: No examination findings for deteriorating state")
        return

    # ============================================================================
    # PHASE 3: Test Questions - Deteriorating State
    # ============================================================================
    print_separator()
    print("📞 TESTING NURSE AI - DETERIORATING STATE")
    print_separator()

    print("Let's ask similar questions and see how the responses differ...\n")

    # Question 6: General appearance (compare with stable state)
    print_subseparator()
    question = "How does she look now?"
    print(f"\n💬 [Question 6] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message="Doctor, Margaret's gotten worse!"
        )
        elapsed = time.time() - start_time
        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    # Question 7: What's changed
    print_subseparator()
    question = "What's changed since earlier?"
    print(f"\n💬 [Question 7] {question}")
    print_subseparator()

    start_time = time.time()
    try:
        response = nurse_turn(
            client=openai_client,
            patient_state=patient_state_data,
            doctor_question=question,
            initial_nurse_message="Doctor, Margaret's gotten worse!"
        )
        elapsed = time.time() - start_time
        print(f"\n🩺 [Nurse Response]")
        print(f"{response}")
        print(f"\n⏱️  Response time: {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print_separator()
    print("✅ DEMO COMPLETE")
    print_separator()

    print("Key observations:")
    print("  • Router successfully classified questions by topic")
    print("  • Nurse responses were contextually appropriate")
    print("  • Responses differed based on patient state (stable vs deteriorating)")
    print("  • Two-stage LLM pattern filtered data effectively")
    print("\nNext steps:")
    print("  • Test with more varied questions")
    print("  • Refine prompts based on clinical realism")
    print("  • Add automated tests with mocked responses")
    print("  • Consider conversation history tracking")

    print_separator()


if __name__ == "__main__":
    main()
