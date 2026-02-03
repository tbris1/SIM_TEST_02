"""
Vitals Parser Service
Extracts structured vital signs data from free-text examination observations.
"""

import re
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class VitalSigns:
    """Structured vital signs data"""
    timestamp: datetime
    heart_rate: int  # bpm
    blood_pressure_systolic: int  # mmHg
    blood_pressure_diastolic: int  # mmHg
    temperature: float  # Celsius
    respiratory_rate: int  # breaths per minute
    oxygen_saturation: int  # percentage
    oxygen_therapy: bool  # on supplemental O2
    consciousness: str  # "Alert", "CVPU", "Unresponsive"
    pain_score: Optional[int] = None  # 0-10 scale


def parse_vitals_from_text(observations: str, timestamp: Optional[datetime] = None) -> VitalSigns:
    """
    Parse vitals from text like:
    "RR 22, SpO2 92% on 2L/min via nasal cannula, HR 92, BP 145/88, Temp 36.8°C"

    Args:
        observations: Free-text observation string
        timestamp: Optional timestamp (defaults to now)

    Returns:
        VitalSigns object with parsed data (uses defaults if not found)
    """
    if timestamp is None:
        timestamp = datetime.now()

    # Respiratory rate: "RR 22" or "RR: 22"
    rr_match = re.search(r'RR:?\s*(\d+)', observations, re.IGNORECASE)
    respiratory_rate = int(rr_match.group(1)) if rr_match else 16

    # Oxygen saturation: "SpO2 92%" or "O2 sat 92%"
    spo2_match = re.search(r'(?:SpO2|O2\s*sat):?\s*(\d+)%?', observations, re.IGNORECASE)
    oxygen_saturation = int(spo2_match.group(1)) if spo2_match else 95

    # Oxygen therapy: check for "on 2L", "via nasal cannula", etc.
    o2_therapy = bool(re.search(
        r'(?:on\s+\d+L|nasal\s+cannula|face\s*mask|oxygen|O2\s+therapy)',
        observations,
        re.IGNORECASE
    ))

    # Heart rate: "HR 92" or "pulse 92"
    hr_match = re.search(r'(?:HR|pulse):?\s*(\d+)', observations, re.IGNORECASE)
    heart_rate = int(hr_match.group(1)) if hr_match else 75

    # Blood pressure: "BP 145/88"
    bp_match = re.search(r'BP:?\s*(\d+)/(\d+)', observations, re.IGNORECASE)
    if bp_match:
        blood_pressure_systolic = int(bp_match.group(1))
        blood_pressure_diastolic = int(bp_match.group(2))
    else:
        blood_pressure_systolic = 120
        blood_pressure_diastolic = 80

    # Temperature: "Temp 36.8°C" or "T 37.2"
    temp_match = re.search(r'(?:Temp|T):?\s*([\d.]+)', observations, re.IGNORECASE)
    temperature = float(temp_match.group(1)) if temp_match else 36.5

    # Consciousness - default to Alert unless mentioned
    consciousness = "Alert"
    if re.search(r'confused|drowsy|unresponsive|unconscious', observations, re.IGNORECASE):
        consciousness = "CVPU"

    # Pain score: "Pain 3/10" or "pain score 5"
    pain_match = re.search(r'pain\s*(?:score)?:?\s*(\d+)(?:/10)?', observations, re.IGNORECASE)
    pain_score = int(pain_match.group(1)) if pain_match else None

    return VitalSigns(
        timestamp=timestamp,
        heart_rate=heart_rate,
        blood_pressure_systolic=blood_pressure_systolic,
        blood_pressure_diastolic=blood_pressure_diastolic,
        temperature=temperature,
        respiratory_rate=respiratory_rate,
        oxygen_saturation=oxygen_saturation,
        oxygen_therapy=o2_therapy,
        consciousness=consciousness,
        pain_score=pain_score
    )
