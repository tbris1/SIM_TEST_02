"""
NEWS2 Calculator Service
Calculates National Early Warning Score 2 from vital signs.
"""

from app.services.vitals_parser import VitalSigns


def calculate_news2_score(vitals: VitalSigns) -> int:
    """
    Calculate NEWS2 score (0-20+)

    NEWS2 Scoring System:
    - Respiratory rate: 3,1,0,1,2,3 points
    - SpO2 Scale 1: 3,2,1,0 points (preferred for most patients)
    - Oxygen therapy: +2 points if on supplemental O2
    - Systolic BP: 3,2,1,0,0,3 points
    - Heart rate: 3,1,0,0,1,2,3 points
    - Consciousness: 0 (Alert) or +3 (any reduction)
    - Temperature: 3,1,0,0,1,2 points

    Reference: Royal College of Physicians (2017)

    Args:
        vitals: VitalSigns object with patient vital signs

    Returns:
        Integer NEWS2 score (0-20+)
    """
    score = 0

    # Respiratory Rate Scoring
    rr = vitals.respiratory_rate
    if rr <= 8:
        score += 3
    elif rr <= 11:
        score += 1
    elif rr <= 20:
        score += 0  # Normal range
    elif rr <= 24:
        score += 2
    else:  # >= 25
        score += 3

    # Oxygen Saturation (Scale 1 - for most patients)
    spo2 = vitals.oxygen_saturation
    if spo2 <= 91:
        score += 3
    elif spo2 <= 93:
        score += 2
    elif spo2 <= 95:
        score += 1
    else:  # >= 96
        score += 0  # Normal

    # Oxygen Therapy
    if vitals.oxygen_therapy:
        score += 2

    # Systolic Blood Pressure
    sbp = vitals.blood_pressure_systolic
    if sbp <= 90:
        score += 3
    elif sbp <= 100:
        score += 2
    elif sbp <= 110:
        score += 1
    elif sbp <= 219:
        score += 0  # Normal range
    else:  # >= 220
        score += 3

    # Heart Rate (Pulse)
    hr = vitals.heart_rate
    if hr <= 40:
        score += 3
    elif hr <= 50:
        score += 1
    elif hr <= 90:
        score += 0  # Normal range
    elif hr <= 110:
        score += 1
    elif hr <= 130:
        score += 2
    else:  # >= 131
        score += 3

    # Level of Consciousness (AVPU)
    if vitals.consciousness != "Alert":
        score += 3

    # Temperature
    temp = vitals.temperature
    if temp <= 35.0:
        score += 3
    elif temp <= 36.0:
        score += 1
    elif temp <= 38.0:
        score += 0  # Normal range
    elif temp <= 39.0:
        score += 1
    else:  # >= 39.1
        score += 2

    return score


def get_news_risk_level(score: int) -> tuple[str, str]:
    """
    Get risk level and recommended action based on NEWS2 score.

    Args:
        score: NEWS2 score

    Returns:
        Tuple of (risk_level, recommended_action)
    """
    if score == 0:
        return ("Low", "Continue routine monitoring")
    elif 1 <= score <= 4:
        return ("Low", "Monitor at least every 4-6 hours")
    elif score == 5 or score == 6:
        return ("Medium", "Urgent review by clinician skilled in acute illness assessment")
    else:  # >= 7
        return ("High", "Emergency assessment by clinical team - consider ICU")
