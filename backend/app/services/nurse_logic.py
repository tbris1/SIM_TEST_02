"""
Nurse AI interaction logic using two-stage LLM pattern.

This module implements:
1. Router LLM - Classifies doctor's questions to filter relevant nursing impression data
2. Response LLM - Generates realistic nurse responses using filtered data

Based on the pattern from existing_nurse_AI_interaction project.
"""

from typing import Any, Dict, List, Optional
import json
import os
from openai import OpenAI


# Topic to JSON path mapping for nursing impressions
TOPIC_TO_PATHS = {
    "GENERAL_APPEARANCE": [
        "nursing_impression.general_appearance",
        "observations"
    ],
    "NURSING_CONCERNS": [
        "nursing_impression.concerns",
        "observations"
    ],
    "RECENT_EVENTS": [
        "nursing_impression.recent_events"
    ],
    "MENTAL_STATE": [
        "nursing_impression.mental_state",
        "observations"
    ],
    "RECENT_OBSERVATIONS": [
        "observations"
    ],
    "PATIENT_APPEARANCE": [
        "nursing_impression.general_appearance"
    ],
    "DETERIORATION": [
        "nursing_impression.concerns",
        "nursing_impression.recent_events",
        "observations"
    ],
    "CURRENT_STATUS": [
        "nursing_impression.general_appearance",
        "nursing_impression.concerns",
        "observations"
    ]
}


# Router system prompt for classifying questions
ROUTER_SYSTEM_PROMPT = f"""You are a routing classifier for a simulated ward nurse.

You will be given:
1) A doctor's free-text question.
2) A list of allowed TOPICS and the JSON schema.

Your task:
- Choose the best TOPIC or TOPICS.
- Provide JSON path(s) that contain the information needed to answer.
- If the question is ambiguous, return a short clarifying_question instead.

Return ONLY valid JSON with keys:
topic, json_paths, clarifying_question

Example output format:
{{
  "topic": ["GENERAL_APPEARANCE"],
  "json_paths": ["nursing_impression.general_appearance", "observations"],
  "clarifying_question": null
}}

TOPICS:
GENERAL_APPEARANCE, NURSING_CONCERNS, RECENT_EVENTS, MENTAL_STATE, RECENT_OBSERVATIONS, PATIENT_APPEARANCE, DETERIORATION, CURRENT_STATUS

TOPIC_TO_PATHS = {TOPIC_TO_PATHS}

Rules:
- Do not answer the doctor.
- Do not invent fields.
- Prefer the smallest number of json_paths.
- Focus on nursing impressions and bedside observations, NOT EHR data.
- Remember: The doctor can see the EHR. They're asking about YOUR observations and impressions.
"""


# Nurse response system prompt
NURSE_SYSTEM_PROMPT = """You are a ward nurse speaking to an on-call doctor.
You are requesting a review of a patient under your care or answering the doctor's follow-up questions.

You must answer the doctor's questions using ONLY the provided NURSING_IMPRESSION and OBSERVATIONS data.

Important constraints:
- Keep replies brief, friendly, and realistic
- DO NOT just list data - engage in a conversational manner
- DO NOT repeat information that's already in the EHR system (the doctor can see that)
- Focus on your bedside observations and clinical impressions
- You may not know certain details if they're not in your provided data
- Do not offer to carry out additional tasks unless asked directly
- Only provide answers to the specific question or questions asked
- If CLARIFYING_QUESTION is provided, consider asking a follow-up question before answering

You are a professional nurse with clinical experience. Speak naturally and conversationally.
"""


def get_by_paths(data: Dict[str, Any], paths: List[str]) -> Dict[str, Any]:
    """
    Extract data from nested JSON using dot-notation paths.

    Args:
        data: The full patient state data
        paths: List of dot-notation paths (e.g., "nursing_impression.general_appearance")

    Returns:
        Dictionary with paths as keys and extracted data as values
    """
    result = {}
    for path in paths:
        keys = path.split('.')
        sub_data = data
        for key in keys:
            if isinstance(sub_data, dict):
                sub_data = sub_data.get(key, {})
            else:
                sub_data = {}
                break
        result[path] = sub_data
    return result


def router_classify_question(client: OpenAI, question: str) -> Dict[str, Any]:
    """
    Use router LLM to classify doctor's question and determine relevant data paths.

    Args:
        client: OpenAI client instance
        question: Doctor's question to classify

    Returns:
        Dictionary with keys: topic, json_paths, clarifying_question
    """
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=ROUTER_SYSTEM_PROMPT,
            input=question
        )
        return json.loads(response.output_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing router response: {e}")
        # Fallback to general appearance and concerns
        return {
            "topic": ["CURRENT_STATUS"],
            "json_paths": [
                "nursing_impression.general_appearance",
                "nursing_impression.concerns",
                "observations"
            ],
            "clarifying_question": None
        }
    except Exception as e:
        print(f"Error in router classification: {e}")
        # Fallback
        return {
            "topic": ["CURRENT_STATUS"],
            "json_paths": [
                "nursing_impression.general_appearance",
                "nursing_impression.concerns",
                "observations"
            ],
            "clarifying_question": None
        }


def nurse_turn(
    client: OpenAI,
    patient_state: Dict[str, Any],
    doctor_question: str,
    initial_nurse_message: Optional[str] = None
) -> str:
    """
    Generate nurse response to doctor's question using two-stage LLM pattern.

    Args:
        client: OpenAI client instance
        patient_state: Current patient state data (should include examination_findings for current state)
        doctor_question: The doctor's question
        initial_nurse_message: The initial message from nurse (optional)

    Returns:
        The nurse's response as a string
    """
    # Classify the question to get relevant data paths
    classified = router_classify_question(client, doctor_question)
    json_paths = classified.get("json_paths", [])
    clarifying_question = classified.get("clarifying_question")

    # Filter patient state to relevant nursing impression fields
    filtered_data = get_by_paths(patient_state, json_paths)
    filtered_data_str = json.dumps(filtered_data, indent=2)

    print(f"[Nurse AI] Classified topics: {classified.get('topic')}")
    print(f"[Nurse AI] Nurse data provided to LLM:\n{filtered_data_str}")

    # Construct input for response LLM
    input_text = f"""
INITIAL_NURSE_MESSAGE:
{initial_nurse_message if initial_nurse_message else "Patient review requested"}

DOCTOR_QUESTION:
{doctor_question}

CLARIFYING_QUESTION:
{clarifying_question if clarifying_question else "None"}

NURSING_DATA:
{filtered_data_str}
"""

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=NURSE_SYSTEM_PROMPT,
            input=input_text
        )
        return response.output_text
    except Exception as e:
        print(f"Error generating nurse response: {e}")
        return "Sorry, I'm having trouble responding right now. Could you please repeat the question?"


def initialize_openai_client(api_key: Optional[str] = None) -> OpenAI:
    """
    Initialize and return OpenAI client for Responses API.

    Args:
        api_key: Optional API key. If not provided, will try to load from environment.

    Returns:
        OpenAI client instance configured for GPT-5 access
    """
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise ValueError("OPENAI_API_KEY not provided and not found in environment")

    return OpenAI(api_key=api_key)
