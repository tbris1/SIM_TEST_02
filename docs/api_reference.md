# API Reference

**Medical On-Call Simulation API v0.1.0**

Base URL: `http://localhost:8000/api/v1`

## Overview

The Medical On-Call Simulation API provides REST endpoints for managing simulation sessions, executing user actions, and tracking patient state progression. The API is built with FastAPI and provides interactive documentation at `/docs`.

## Quick Start

1. **Start the API server:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Access interactive docs:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

3. **Basic workflow:**
   ```bash
   # List scenarios
   GET /api/v1/scenarios

   # Start a session
   POST /api/v1/sessions/start

   # Execute actions
   POST /api/v1/sessions/{session_id}/actions

   # Complete session
   POST /api/v1/sessions/{session_id}/complete
   ```

---

## Health & Status Endpoints

### GET `/`
Root endpoint - API health check.

**Response:**
```json
{
  "name": "Medical On-Call Simulation API",
  "version": "0.1.0",
  "status": "operational",
  "docs": "/docs"
}
```

### GET `/health`
Detailed health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "api_prefix": "/api/v1"
}
```

---

## Scenario Endpoints

### GET `/api/v1/scenarios`
List all available simulation scenarios.

**Response:** `200 OK`
```json
[
  {
    "scenario_id": "simple_test_001",
    "title": "Simple Test Scenario - Single Patient",
    "description": "Minimal scenario for testing simulation engine",
    "difficulty": "easy",
    "estimated_duration_minutes": 30,
    "patient_count": 1,
    "file_path": "/path/to/simple_test_001.json"
  }
]
```

---

## Session Management Endpoints

### POST `/api/v1/sessions/start`
Start a new simulation session from a scenario.

**Request Body:**
```json
{
  "scenario_id": "simple_test_001",
  "custom_start_time": "2024-01-15T20:00:00"  // Optional
}
```

**Response:** `201 Created`
```json
{
  "session_id": "session_abc123",
  "scenario_id": "simple_test_001",
  "is_complete": false,
  "created_at": "2024-01-15T19:45:00",
  "current_time": "2024-01-15T20:00:00",
  "elapsed_minutes": 0
}
```

**Errors:**
- `404 Not Found` - Scenario doesn't exist
- `400 Bad Request` - Invalid request format

---

### GET `/api/v1/sessions/{session_id}`
Get the current state of a simulation session.

**Response:** `200 OK`
```json
{
  "session_id": "session_abc123",
  "scenario_id": "simple_test_001",
  "clock": {
    "scenario_start_time": "2024-01-15T20:00:00",
    "current_time": "2024-01-15T20:30:00",
    "elapsed_minutes": 30,
    "real_elapsed_minutes": 5,
    "artificial_minutes_added": 25,
    "formatted_time": "20:30",
    "formatted_elapsed": "30 mins"
  },
  "scheduler": {
    "total_events": 2,
    "pending_events": 1,
    "next_event_time": "2024-01-15T21:00:00"
  },
  "patients": {
    "pt_001": {
      "patient_id": "pt_001",
      "name": "Margaret Thompson",
      "current_state": "stable_with_concerns",
      "ward": "Ward 4A",
      "bed": "Bed 12"
    }
  },
  "action_count": 3,
  "notification_count": 2,
  "is_complete": false
}
```

**Errors:**
- `404 Not Found` - Session doesn't exist

---

### GET `/api/v1/sessions`
List all active simulation sessions.

**Response:** `200 OK`
```json
{
  "sessions": [
    {
      "session_id": "session_abc123",
      "scenario_id": "simple_test_001",
      "is_complete": false,
      "elapsed_minutes": 30,
      "patient_count": 1,
      "action_count": 3,
      "created_at": "2024-01-15T19:45:00"
    }
  ],
  "count": 1
}
```

---

### GET `/api/v1/sessions/{session_id}/timeline`
Get chronological timeline of all session events.

**Response:** `200 OK`
```json
{
  "session_id": "session_abc123",
  "timeline": [
    {
      "type": "notification",
      "timestamp": "2024-01-15T20:05:00",
      "data": {
        "type": "new_request",
        "patient_id": "pt_001",
        "message": "Nurse calling from Ward 4A about Margaret Thompson",
        "urgency": "urgent",
        "time": "2024-01-15T20:05:00"
      }
    },
    {
      "type": "action",
      "timestamp": "2024-01-15T20:10:00",
      "elapsed_minutes": 10,
      "data": {
        "action": {
          "action_type": "review_in_person",
          "patient_id": "pt_001"
        },
        "time_advanced": 30
      }
    }
  ]
}
```

---

### GET `/api/v1/sessions/{session_id}/patients/{patient_id}`
Get detailed information about a specific patient.

**Response:** `200 OK`
```json
{
  "patient_id": "pt_001",
  "name": "Margaret Thompson",
  "mrn": "MRN12345",
  "age": 72,
  "gender": "Female",
  "ward": "Ward 4A",
  "bed": "Bed 12",
  "current_state": "deteriorating",
  "actions_taken": [
    {
      "action_type": "review_in_person",
      "timestamp": "2024-01-15T20:10:00",
      "details": {}
    }
  ],
  "state_history": [
    {
      "old_state": "stable_with_concerns",
      "new_state": "deteriorating",
      "timestamp": "2024-01-15T21:30:00",
      "reason": "Time elapsed trigger"
    }
  ]
}
```

**Errors:**
- `404 Not Found` - Session or patient doesn't exist

---

### POST `/api/v1/sessions/{session_id}/complete`
Mark a session as complete and generate summary.

**Response:** `200 OK`
```json
{
  "session_id": "session_abc123",
  "scenario_id": "simple_test_001",
  "completed_at": "2024-01-15T21:00:00",
  "total_time_elapsed_minutes": 60,
  "total_actions": 5,
  "patients": {
    "pt_001": {
      "name": "Margaret Thompson",
      "final_state": "stable",
      "state_changes": 2,
      "actions_taken": 5
    }
  },
  "timeline": [...]
}
```

**Errors:**
- `404 Not Found` - Session doesn't exist
- `400 Bad Request` - Session already complete

---

### DELETE `/api/v1/sessions/{session_id}`
Delete a simulation session.

**Response:** `200 OK`
```json
{
  "session_id": "session_abc123",
  "deleted": true
}
```

**Errors:**
- `404 Not Found` - Session doesn't exist

---

## Action Execution Endpoints

### POST `/api/v1/sessions/{session_id}/actions`
Execute a user action within a simulation session.

**Request Body:**
```json
{
  "action_type": "review_in_person",
  "patient_id": "pt_001",
  "details": {
    "location": "Ward 4A, Bed 12"
  },
  "time_cost_minutes": 30
}
```

**Action Types:**
- `review_in_person` - Physical patient review (default: 30 mins)
- `request_investigation` - Order tests (default: 2 mins)
- `escalate` - Call senior doctor (default: 5 mins)
- `document_note` - Write clinical note (default: 5 mins)
- `ask_nurse_question` - Chat with nurse (default: 2 mins)

**Response:** `200 OK`
```json
{
  "success": true,
  "action_type": "review_in_person",
  "patient_id": "pt_001",
  "time_advanced_minutes": 30,
  "new_simulation_time": "2024-01-15T20:30:00",
  "message": "Action completed: review_in_person",
  "triggered_events": [
    {
      "event_id": "abg_results",
      "event_type": "investigation_result",
      "patient_id": "pt_001",
      "notifications": ["ABG results available for Margaret Thompson"]
    }
  ],
  "new_notifications": [
    "ABG results available for Margaret Thompson"
  ],
  "patient_state_changes": [
    {
      "type": "patient_state_change",
      "patient_id": "pt_001",
      "patient_name": "Margaret Thompson",
      "old_state": "stable_with_concerns",
      "new_state": "stable",
      "message": "Patient stabilized after escalation",
      "urgency": "low",
      "time": "2024-01-15T20:30:00"
    }
  ]
}
```

**Errors:**
- `400 Bad Request` - Invalid action or session complete
- `404 Not Found` - Session doesn't exist

---

### Convenience Endpoints

#### POST `/api/v1/sessions/{session_id}/actions/review`
Convenience endpoint for in-person patient review.

**Query Parameters:**
- `patient_id` (required)
- `location` (optional)
- `time_cost_minutes` (optional, default: 30)

---

#### POST `/api/v1/sessions/{session_id}/actions/escalate`
Convenience endpoint for escalating to senior doctor.

**Query Parameters:**
- `patient_id` (required)
- `escalate_to` (optional, default: "registrar")
- `reason` (optional)
- `time_cost_minutes` (optional, default: 5)

---

#### POST `/api/v1/sessions/{session_id}/actions/investigate`
Convenience endpoint for requesting investigations.

**Query Parameters:**
- `patient_id` (required)
- `investigation_type` (required)
- `urgency` (optional, default: "routine")
- `expected_delay_minutes` (optional, default: 30)

---

#### POST `/api/v1/sessions/{session_id}/actions/document`
Convenience endpoint for documenting clinical notes.

**Query Parameters:**
- `patient_id` (required)
- `note_content` (required)
- `note_type` (optional, default: "review")

---

## Simulation Flow

### Typical Session Flow

1. **List available scenarios**
   ```bash
   GET /api/v1/scenarios
   ```

2. **Start a new session**
   ```bash
   POST /api/v1/sessions/start
   {
     "scenario_id": "simple_test_001"
   }
   ```

3. **Get current state** (repeat as needed)
   ```bash
   GET /api/v1/sessions/{session_id}
   ```

4. **Execute actions** (repeat for each user action)
   ```bash
   POST /api/v1/sessions/{session_id}/actions
   {
     "action_type": "review_in_person",
     "patient_id": "pt_001"
   }
   ```

5. **Check patient details**
   ```bash
   GET /api/v1/sessions/{session_id}/patients/pt_001
   ```

6. **Complete session**
   ```bash
   POST /api/v1/sessions/{session_id}/complete
   ```

7. **Review timeline**
   ```bash
   GET /api/v1/sessions/{session_id}/timeline
   ```

---

## Time Management

The simulation uses a **hybrid clock model**:

- **Real time**: Actual wall-clock time elapsed
- **Artificial time**: Penalties added for time-consuming actions (e.g., in-person reviews)
- **Total simulation time** = Real time + Artificial time

### Time Costs by Action Type

| Action Type | Default Time Cost |
|-------------|------------------|
| `review_in_person` | 30 minutes |
| `escalate` | 5 minutes |
| `document_note` | 5 minutes |
| `request_investigation` | 2 minutes |
| `ask_nurse_question` | 2 minutes |

Time costs can be customized per action using the `time_cost_minutes` parameter.

---

## Event Processing

When an action is executed:

1. Time advances (real + artificial)
2. All scheduled events up to current time are processed
3. Patient state rules are evaluated
4. State changes trigger notifications
5. Results are returned to the client

### Event Types

- `new_request` - New patient request arrives
- `investigation_result` - Lab/imaging results available
- `escalation_response` - Senior doctor responds

---

## Error Handling

All endpoints follow standard HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request format or logic error
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

Error responses include a `detail` field:
```json
{
  "detail": "Session not found: session_abc123"
}
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

To modify CORS settings, edit [app/config.py](../backend/app/config.py).

---

## Testing

Run API tests:
```bash
cd backend
source venv/bin/activate
pytest tests/test_api/ -v
```

Test coverage:
- Session management: 13 tests
- Action execution: 15 tests

---

## Next Steps

- **Phase 3**: EHR system with progressive revelation
- **Phase 4**: AI integration for nurse interactions
- **Phase 5**: Frontend UI
- **Phase 6**: AI feedback generation
- **Phase 7**: Additional scenarios and polish

---

## Support

For issues or questions:
- GitHub: [medical-oncall-sim repository](https://github.com)
- Documentation: See [README.md](../README.md) and [CLAUDE.md](../CLAUDE.md)

---

**Last Updated**: 2026-02-01
**API Version**: 0.1.0
**Phase**: 2 (API Layer)
