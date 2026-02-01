# Phase 3 EHR System - Revision: Dynamic Examination Notes

**Date**: 2026-02-01
**Status**: ✅ Complete

## Overview

This revision updates the EHR system implementation to better simulate realistic clinical practice. The key change is that in-person reviews now **generate new examination notes** based on the patient's current state, rather than revealing pre-existing hidden notes.

## Key Behavioral Changes

### Before (Original Implementation)
- In-person reviews revealed **existing** clinical notes that were previously hidden
- Progressive revelation controlled when users could see notes already in the system
- `REVIEW_IN_PERSON` visibility condition used extensively
- EHR information was progressively "unlocked" based on actions

### After (Revised Implementation)
- In-person reviews **generate NEW clinical notes** with examination findings
- All existing clinical notes are **ALWAYS visible** (realistic EHR access)
- Examination findings are **dynamic** based on patient's current state
- Progressive revelation now primarily applies to investigation results (time-based)

## Why This Change?

The original implementation didn't accurately reflect clinical reality:

1. **Real EHRs**: In practice, doctors can see all existing clinical documentation immediately when they access a patient's EHR. There's no "unlocking" of notes.

2. **Physical Examination**: When a doctor physically examines a patient, they document what they observe **at that moment**. This creates a new note reflecting the patient's current state.

3. **Investigation Ordering**: Doctors can order investigations (bloods, imaging) via the EHR without needing to see the patient first. Nurses collect samples and investigations are processed.

## Implementation Details

### 1. Patient Model Changes

**File**: [app/models/patient.py](../backend/app/models/patient.py)

Added to `PatientTrajectory`:
```python
class PatientTrajectory(BaseModel):
    # ... existing fields ...

    # NEW: Examination findings for each state
    examination_findings: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Physical examination findings for each patient state"
    )

    # NEW: Investigation result templates for each state
    investigation_templates: Dict[str, Dict[str, Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Investigation result templates for each state and investigation type"
    )

    def get_examination_findings(self, state: PatientState) -> Optional[Dict[str, Any]]:
        """Get examination findings for a specific patient state."""
        return self.examination_findings.get(state.value)

    def get_investigation_template(self, state: PatientState, investigation_type: str) -> Optional[Dict[str, Any]]:
        """Get investigation result template for a specific state and investigation type."""
        state_templates = self.investigation_templates.get(state.value, {})
        return state_templates.get(investigation_type)
```

### 2. Simulation Engine Changes

**File**: [app/models/simulation.py](../backend/app/models/simulation.py)

Added automatic examination note generation:
```python
def execute_action(self, action: UserAction) -> ActionResult:
    # ... existing code ...

    # Record action on patient
    patient.record_action(action.action_type, new_time, action.details)

    # NEW: Generate examination note if this is an in-person review
    if action.action_type == "review_in_person":
        self._generate_examination_note(patient, new_time)

    # ... rest of execution ...

def _generate_examination_note(self, patient: Patient, timestamp: datetime):
    """
    Generate an examination note based on the patient's current state.
    This simulates the clinician physically examining the patient and documenting findings.
    """
    from ..services.ehr_service import ehr_service
    from ..models.ehr import NoteType, VisibilityRule, VisibilityCondition

    if not ehr_service.has_record(patient.patient_id):
        return

    # Get examination findings for current state
    examination_findings = patient.trajectory.get_examination_findings(patient.current_state)

    if not examination_findings:
        # Use default if not defined
        examination_findings = {
            "general": "Patient assessed",
            "summary": f"Patient reviewed in person. Current state: {patient.current_state.value}"
        }

    # Generate clinical note with examination findings
    ehr_service.add_clinical_note(
        patient_id=patient.patient_id,
        note_type=NoteType.PROGRESS,
        timestamp=timestamp,
        author="User",
        author_role="FY1",
        title=f"In-Person Review at {timestamp.strftime('%H:%M')}",
        content=examination_findings,
        visibility_rule=VisibilityRule(condition=VisibilityCondition.ALWAYS)
    )
```

### 3. Investigation Ordering Endpoint

**File**: [app/api/ehr.py](../backend/app/api/ehr.py)

Added new endpoint for ordering investigations:
```python
@router.post("/sessions/{session_id}/patients/{patient_id}/ehr/investigations/order")
async def order_investigation(session_id: str, patient_id: str, request: OrderInvestigationRequest):
    """
    Order an investigation for a patient.

    Users can order investigations without performing an in-person review,
    simulating the ability to request tests remotely and have nurses collect samples.

    Default turnaround times:
    - ABG: 20 minutes
    - FBC, U&E, LFT: 60 minutes
    - CXR: 120 minutes (2 hours)
    - CT scan: 240 minutes (4 hours)
    - Blood cultures: 2880 minutes (48 hours)
    """
    # Get patient's current state
    patient = session.patients[patient_id]

    # Calculate result time based on turnaround time
    turnaround_minutes = request.custom_turnaround_minutes or default_turnaround_times.get(
        request.investigation_type, 60
    )
    resulted_time = current_time + timedelta(minutes=turnaround_minutes)

    # Get investigation template for patient's current state
    investigation_template = patient.trajectory.get_investigation_template(
        patient.current_state,
        request.investigation_type
    )

    # If no template, use default normal values
    if not investigation_template:
        investigation_template = default_results.get(request.investigation_type, {...})

    # Create investigation result in EHR (visible when resulted)
    result = ehr_service.add_investigation_result(
        patient_id=patient_id,
        investigation_type=request.investigation_type,
        requested_time=current_time,
        resulted_time=resulted_time,
        result_data=investigation_template.get("result_data", {}),
        interpretation=investigation_template.get("interpretation"),
        abnormal_flags=investigation_template.get("abnormal_flags", []),
        visibility_rule=VisibilityRule(
            condition=VisibilityCondition.TIME_ELAPSED,
            visible_after_time=resulted_time
        )
    )

    # Schedule event for when result becomes available
    session.scheduler.schedule_event(result_event)

    return {
        "message": f"Investigation ordered successfully: {request.investigation_type}",
        "result_id": result.result_id,
        "expected_result_time": resulted_time.isoformat(),
        "turnaround_minutes": turnaround_minutes
    }
```

### 4. Scenario Format Updates

**File**: [data/scenarios/simple_test_ehr.json](../backend/data/scenarios/simple_test_ehr.json)

#### Changed Visibility Rules
All clinical notes now use `"condition": "always"`:
```json
{
  "note_type": "progress",
  "title": "Evening Ward Round",
  "visibility_rule": {
    "condition": "always"  // Changed from "ehr_reviewed"
  }
}
```

#### Added Examination Findings
```json
{
  "trajectory": {
    "state_change_rules": [...],
    "examination_findings": {
      "stable_with_concerns": {
        "general": "Patient sitting up in bed, appears mildly short of breath",
        "appearance": "Alert and orientated, speaking in full sentences",
        "observations": "RR 22, SpO2 92% on 2L/min, HR 92, BP 145/88",
        "respiratory": "Using accessory muscles. Reduced air entry bilateral bases with scattered wheeze.",
        "cardiovascular": "Dual heart sounds, normal volume. No murmurs.",
        "impression": "Patient with known COPD, currently stable but with concerning features"
      },
      "deteriorating": {
        "general": "Patient visibly distressed, significant work of breathing",
        "observations": "RR 28, SpO2 88% on 4L/min, HR 105, BP 152/92",
        "respiratory": "Marked use of accessory muscles. Poor air entry bilaterally.",
        "impression": "COPD exacerbation with worsening respiratory failure. Consider ABG and escalation."
      },
      // ... other states ...
    }
  }
}
```

#### Added Investigation Templates
```json
{
  "trajectory": {
    "investigation_templates": {
      "stable_with_concerns": {
        "ABG": {
          "result_data": {"pH": 7.35, "pCO2": 6.5, "pO2": 8.5, "HCO3": 26},
          "interpretation": "Mild Type 2 respiratory failure with compensation",
          "abnormal_flags": ["Slightly low pH", "Elevated pCO2", "Low pO2"]
        },
        "FBC": {
          "result_data": {"Hb": 13.2, "WCC": 11.5, "Platelets": 245},
          "interpretation": "Mild leukocytosis, possibly infective",
          "abnormal_flags": ["Elevated WCC"]
        }
        // ... other investigations ...
      },
      "deteriorating": {
        "ABG": {
          "result_data": {"pH": 7.32, "pCO2": 7.8, "pO2": 8.2, "HCO3": 28},
          "interpretation": "Type 2 respiratory failure with partial compensation",
          "abnormal_flags": ["Low pH", "High pCO2", "Low pO2"]
        }
        // ... gets worse as patient deteriorates ...
      }
      // ... other states ...
    }
  }
}
```

### 5. Scenario Loader Updates

**File**: [app/services/scenario_loader.py](../backend/app/services/scenario_loader.py)

Updated to load new trajectory data:
```python
def _create_patient_from_data(self, patient_data: Dict[str, Any]) -> Patient:
    # ... parse state change rules ...

    # NEW: Load examination findings
    examination_findings = trajectory.get("examination_findings", {})

    # NEW: Load investigation templates
    investigation_templates = trajectory.get("investigation_templates", {})

    # Create patient trajectory
    patient_trajectory = PatientTrajectory(
        state_change_rules=state_change_rules,
        examination_findings=examination_findings,
        investigation_templates=investigation_templates
    )
```

## Usage Examples

### Example 1: In-Person Review Generates Examination Note

```bash
# Before review - existing notes visible
GET /api/v1/sessions/{session_id}/patients/pt_001/ehr
# Returns:
# - Admission note (always visible)
# - Evening ward round note (always visible)
# - Nursing observations (always visible)
# Total: 3 notes

# Perform in-person review
POST /api/v1/sessions/{session_id}/actions/review?patient_id=pt_001

# After review - NEW note generated
GET /api/v1/sessions/{session_id}/patients/pt_001/ehr
# Returns:
# - Admission note
# - Evening ward round note
# - Nursing observations
# - NEW: In-Person Review at 20:32 (just generated!)
# Total: 4 notes

# The new note contains:
{
  "title": "In-Person Review at 20:32",
  "note_type": "progress",
  "author": "User",
  "content": {
    "general": "Patient sitting up in bed, appears mildly short of breath",
    "observations": "RR 22, SpO2 92% on 2L/min, HR 92, BP 145/88",
    "respiratory": "Using accessory muscles. Reduced air entry bilateral bases...",
    "impression": "Patient with known COPD, currently stable but with concerning features"
  }
}
```

### Example 2: Ordering Investigations

```bash
# Order ABG without seeing patient
POST /api/v1/sessions/{session_id}/patients/pt_001/ehr/investigations/order
{
  "investigation_type": "ABG",
  "urgency": "urgent"
}

# Response:
{
  "message": "Investigation ordered successfully: ABG",
  "result_id": "result_abc123",
  "requested_time": "2024-01-15T20:10:00",
  "expected_result_time": "2024-01-15T20:30:00",
  "turnaround_minutes": 20
}

# Result becomes visible at 20:30 (time-based visibility)
# Investigation result uses template based on patient's current state
```

### Example 3: State-Dependent Examination Findings

```python
# Patient starts in "stable_with_concerns" state
# In-person review generates note with mild findings

# Patient deteriorates to "deteriorating" state
# Next in-person review generates note with worse findings:
{
  "general": "Patient visibly distressed, significant work of breathing",
  "observations": "RR 28, SpO2 88% on 4L/min, HR 105",
  "impression": "COPD exacerbation with worsening respiratory failure"
}
```

## Benefits of This Approach

1. **Realism**: Mirrors actual clinical practice where doctors document what they observe at the time of examination

2. **Dynamic State Reflection**: Examination findings change based on patient's current state, providing accurate clinical picture

3. **Pedagogical Value**: Trains users to perform timely assessments and document findings appropriately

4. **Flexibility**: Easy to define different examination findings for each clinical state

5. **Investigation Ordering**: Allows remote test ordering, simulating modern clinical practice

## Files Changed

**New Files**: None (revision of existing Phase 3 files)

**Modified Files**:
1. `backend/app/models/patient.py` - Added examination_findings and investigation_templates to PatientTrajectory
2. `backend/app/models/simulation.py` - Added _generate_examination_note method
3. `backend/app/api/ehr.py` - Added investigation ordering endpoint
4. `backend/data/scenarios/simple_test_ehr.json` - Added examination findings, investigation templates, changed visibility rules
5. `backend/app/services/scenario_loader.py` - Updated to load new trajectory data
6. `backend/demo_ehr_system.py` - Updated descriptions to reflect new behavior

**Test Updates Required**:
- Update `test_ehr_visibility_after_action` to expect NEW note generation rather than revelation
- Add tests for investigation ordering endpoint
- Add tests for state-dependent examination findings

## Backwards Compatibility

This change is **not backwards compatible** with scenarios that rely on `REVIEW_IN_PERSON` visibility condition for existing notes. However, the impact is minimal:

1. Old scenarios still work - notes will just be always visible
2. Examination findings are optional - system uses default if not provided
3. Investigation templates are optional - system uses normal values if not provided

## Next Steps

This completes the Phase 3 revision. The EHR system now:
- ✅ Simulates realistic clinical information access
- ✅ Generates dynamic examination notes
- ✅ Supports remote investigation ordering
- ✅ Reflects patient state in clinical findings
- ✅ Uses time-based progressive revelation for results

**Ready for**: Phase 4 (AI Integration)
