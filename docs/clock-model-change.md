# Clock Model Change: Pure Action-Based → Hybrid Real-Time

**Date**: 2026-02-01
**Impact**: Core simulation mechanics

---

## Overview

Changed the simulation clock from **pure action-based** (deterministic) to **hybrid real-time** to create authentic time pressure while maintaining realistic action costs.

---

## Original Model (Phase 1)

**Pure Action-Based Time**:
- Time ONLY advances when user takes actions
- Each action has a fixed time cost (review = 30 mins, chat = 2 mins, etc.)
- Student could pause indefinitely - no time pressure
- Fully deterministic and reproducible

**Example**:
```
Student reviews patient → +30 mins
Student pauses for 10 real minutes thinking → +0 mins (time frozen)
Student escalates → +5 mins
Total: 35 simulated minutes
```

**Pros**:
- Deterministic (same actions = same results)
- Easy to test
- No time pressure on students

**Cons**:
- **No time pressure** - students could pause forever
- **Unrealistic** - real on-call shifts don't pause
- Doesn't teach **actual time management** under pressure

---

## New Model (Hybrid Real-Time)

**Hybrid: Real Time + Artificial Penalties**:
- Clock runs in **real time** (like a stopwatch)
- **In-person reviews** add +30 mins **artificial time**
- Other actions (chat, escalate, document) happen in real time
- Total sim time = Real elapsed + Artificial penalties

**Example**:
```
Student starts → 20:00
Student thinks for 5 real minutes → 20:05 (real time passed)
Student chats with nurse → 20:05 (instant, minimal real time)
Student reviews in person → 20:35 (+30 artificial mins added)
Total: 35 simulated minutes (5 real + 30 artificial)
```

**Pros**:
- **Time pressure** - students can't pause forever
- **Realistic** - simulates actual on-call urgency
- **Balanced** - in-person reviews are "expensive" (encourages remote triage)
- Still mostly deterministic (artificial time is fixed)

**Cons**:
- Slightly less deterministic (real time varies)
- Tests need to account for real time passage

---

## Implementation Details

### SimulationClock Changes

**Before**:
```python
class SimulationClock:
    start_time: datetime
    current_time: datetime
    elapsed_minutes: int = 0

    def advance(self, minutes: int) -> datetime:
        self.elapsed_minutes += minutes
        self.current_time += timedelta(minutes=minutes)
        return self.current_time
```

**After**:
```python
class SimulationClock:
    scenario_start_time: datetime      # When scenario starts (e.g., 20:00)
    session_start_time: datetime       # When student started (real time)
    artificial_minutes_added: int = 0  # Extra time from in-person reviews

    def get_current_time(self) -> datetime:
        """Calculate: scenario_start + real_elapsed + artificial"""
        real_elapsed = (datetime.now() - self.session_start_time).seconds // 60
        total_minutes = real_elapsed + self.artificial_minutes_added
        return self.scenario_start_time + timedelta(minutes=total_minutes)

    def add_artificial_time(self, minutes: int) -> datetime:
        """Add artificial time (e.g., for in-person review)"""
        self.artificial_minutes_added += minutes
        return self.get_current_time()
```

### Action Execution Logic

```python
def execute_action(self, action: UserAction) -> ActionResult:
    old_time = self.clock.get_current_time()

    # Only in-person reviews add artificial time
    if action.action_type == "review_in_person":
        artificial_added = action.time_cost_minutes or 30
        new_time = self.clock.add_artificial_time(artificial_added)
    else:
        # Other actions: just use current real time (no penalty)
        new_time = self.clock.get_current_time()

    # Process events, check state changes, etc.
    ...
```

---

## Action Time Costs

| Action | Time Model | Notes |
|--------|------------|-------|
| `review_in_person` | +30 mins **artificial** | Simulates travel + assessment |
| `ask_nurse_question` | Real time only | Instant (chat is quick) |
| `request_investigation` | Real time only | Ordering is quick |
| `escalate` | Real time only | Phone call is quick |
| `document_note` | Real time only | Documentation is quick |

**Key Insight**: Only **physically going to the patient** adds artificial time. Everything else happens in real time.

---

## Testing Considerations

### Challenge: Real Time Variability

Tests now have slight variability due to real time passage:

```python
# Old test (deterministic)
assert session.clock.elapsed_minutes == 30

# New test (allow for real time)
assert session.clock.artificial_minutes_added == 30  # Deterministic part
assert session.clock.get_elapsed_minutes() == 30     # May be 30-31 mins
```

### Solution: Test Artificial Time Separately

```python
def test_execute_action_advances_time(self):
    # Execute in-person review
    result = session.execute_action(
        UserAction(action_type="review_in_person", patient_id="pt_001")
    )

    # Check artificial time (deterministic)
    assert session.clock.artificial_minutes_added == 30

    # Total elapsed will be ~30 (might be 30-31 due to real time)
    assert 30 <= session.clock.get_elapsed_minutes() <= 31
```

### Determinism for Fixed Session Times

For full determinism in tests, use a fixed `session_start_time`:

```python
clock = SimulationClock(
    scenario_start_time=datetime(2024, 1, 15, 20, 0, 0),
    session_start_time=datetime(2024, 1, 15, 19, 55, 0)  # Fixed time
)
```

---

## Pedagogical Impact

### Learning Objectives Enhanced

1. **Time Pressure Management**
   - Students feel urgency (real clock is ticking)
   - Can't overthink decisions indefinitely
   - More realistic on-call experience

2. **Remote Triage Skills**
   - In-person reviews are "expensive" (+30 mins)
   - Encourages thorough phone triage first
   - Teaches efficient information gathering

3. **Prioritization Under Pressure**
   - Multiple patients deteriorating in real time
   - Must decide: "Can I afford 30 mins to review this patient?"
   - Realistic trade-offs

### Example Scenario

```
20:00 - Session starts
20:03 - Nurse calls about Patient A (SOB)
20:05 - Student chats with nurse (2 mins real time)
20:05 - Student reviews EHR (3 mins real time)
20:08 - Student decides: review in person?
        → If yes: +30 artificial → 20:38
        → If no: continue remote management → 20:08

Meanwhile...
20:15 - ABG results arrive (scheduled event)
20:20 - Patient B nurse calls (new urgent request)

Student must juggle:
- Real time: Other requests arriving
- Artificial time: Cost of in-person reviews
```

---

## Migration Notes

### Code Changes Required

1. **Scenario JSON** - No changes needed (times stay the same)
2. **SimulationClock initialization** - New parameters
3. **Tests** - Updated to use new clock API
4. **Demo scripts** - New demo created showing hybrid model

### Backward Compatibility

Not maintained - this is a breaking change to core mechanics. All code using `SimulationClock` must be updated.

---

## Future Enhancements

### Potential Improvements

1. **Configurable Artificial Time**
   - Let scenarios define in-person review time per patient
   - e.g., ICU patient = 45 mins, routine ward = 20 mins

2. **Action-Specific Real Time Penalties**
   - Documentation could add small artificial time (5 mins)
   - Escalation could add time for handover (3 mins)

3. **Pause Feature**
   - Allow students to pause (for true emergencies)
   - Record pauses separately from simulation time

4. **Session Time Limits**
   - Enforce maximum session length (e.g., 60 mins real time)
   - Prevents extremely long sessions

---

## Summary

| Aspect | Old Model | New Model |
|--------|-----------|-----------|
| **Time Advancement** | Actions only | Real time + Artificial |
| **Time Pressure** | None | Yes (real clock ticks) |
| **In-Person Review** | Fixed time cost | +30 mins artificial |
| **Other Actions** | Fixed time costs | Real time (instant) |
| **Determinism** | Fully deterministic | Mostly deterministic |
| **Realism** | Low (can pause forever) | High (time pressure) |
| **Testing** | Simple | Slightly more complex |

**Conclusion**: The hybrid model significantly improves realism and teaching effectiveness while maintaining the core benefits of rule-based simulation. The trade-off of slightly reduced determinism is worthwhile for the pedagogical gains.

---

**References**:
- [simulation.py](../backend/app/models/simulation.py) - Updated clock implementation
- [demo_realtime_simulation.py](../backend/demo_realtime_simulation.py) - Working example
- [test_simulation_engine.py](../backend/tests/test_simulation_engine.py) - Updated tests (17/17 passing)
