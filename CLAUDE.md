# CLAUDE.md - Project Context & Progress

**Last Updated**: 2026-02-01 (Clock Model Updated)
**Project**: Medical On-Call Simulation Platform MVP
**Status**: Phase 1 Complete ✅ (with hybrid real-time clock) | Phase 2 Ready to Start

---

## 🎯 Project Overview

A web-based simulation platform for training final-year medical students in managing multiple patients during on-call shifts. Focus on prioritization, escalation, and managing uncertainty - NOT complex physiology modeling.

**Key Features**:
- Time-based mechanics (60 min real time = 3-4 hours sim time)
- AI-driven nurse interactions (GPT-4)
- Simulated hospital EHR with progressive information revelation
- Rule-based patient state transitions
- Deterministic, reproducible sessions
- Timeline recording for feedback

**Tech Stack**:
- Backend: Python + FastAPI
- Frontend: React + TypeScript (Phase 5)
- AI: OpenAI GPT-4 (Phase 4)
- Storage: JSON files

---

## 📊 Progress Tracker

### ✅ Completed Phases

#### Phase 1: Core Simulation Engine (COMPLETE)
**Status**: ✅ All tests passing (17/17)

**What was built**:
- [x] SimulationClock - Time management (deterministic, action-based)
- [x] EventScheduler - Priority queue for delayed events
- [x] Patient State Machine - 4 discrete states with rule-based transitions
- [x] User Actions - 5 action types with time costs
- [x] SimulationSession - Main orchestrator
- [x] Comprehensive unit tests (17 tests, 100% passing)
- [x] Demo simulation script
- [x] Simple test scenario JSON

**Key Files Created**:
- `backend/app/models/events.py` - Event types and models
- `backend/app/models/patient.py` - Patient state machine
- `backend/app/models/actions.py` - User action models
- `backend/app/models/simulation.py` - Core engine (Clock, Scheduler, Session)
- `backend/tests/test_simulation_engine.py` - Unit tests
- `data/scenarios/simple_test.json` - Test scenario
- `backend/demo_simulation.py` - Interactive demo

**Verification**:
```bash
cd backend
source venv/bin/activate
pytest tests/test_simulation_engine.py -v  # 17 passed
python demo_simulation.py  # See it in action
```

**Documentation**: See [docs/phase1-complete.md](docs/phase1-complete.md)

---

### 🔄 Current Phase

#### Phase 2: API Layer with FastAPI (IN PROGRESS)
**Status**: Ready to start

**Goals**:
- Expose simulation engine via REST API
- Session management (create, get, update)
- Action execution endpoint
- CORS configuration for frontend
- Test with Postman/curl

**Files to Create**:
- [ ] `backend/app/main.py` - FastAPI app entry point
- [ ] `backend/app/config.py` - Configuration and settings
- [ ] `backend/app/api/sessions.py` - Session CRUD endpoints
- [ ] `backend/app/api/actions.py` - Action execution endpoint
- [ ] `backend/app/services/simulation_engine.py` - Service layer refactor
- [ ] `backend/app/services/scenario_loader.py` - Load scenarios from JSON
- [ ] `backend/tests/test_api/` - API integration tests

**API Endpoints to Build**:
```
POST   /api/v1/sessions/start          # Create new session from scenario
GET    /api/v1/sessions/{id}           # Get session state
POST   /api/v1/sessions/{id}/actions   # Execute action
POST   /api/v1/sessions/{id}/complete  # Complete session
GET    /api/v1/scenarios                # List available scenarios
```

---

### 📋 Upcoming Phases

#### Phase 3: EHR System (PLANNED)
- PatientRecord models with full clinical data
- Visibility rules for progressive information revelation
- EHR endpoints
- Clinical notes system

#### Phase 4: AI Integration - Nurse Chat (PLANNED)
- OpenAI API wrapper
- NurseInteraction service with prompt engineering
- Chat endpoints
- Conversation state management

#### Phase 5: Frontend - React UI (PLANNED)
- Core components (Clock, Inbox, Chat, EHR, Actions)
- Main simulation page
- API client
- State management hooks

#### Phase 6: AI Feedback & Timeline (PLANNED)
- Timeline visualization
- GPT-4 feedback generation
- Objective metrics calculation

#### Phase 7: Scenarios & Polish (PLANNED)
- Create 2-3 complete clinical scenarios
- Scenario validation tool
- UI polish and error handling
- End-to-end testing

---

## 🏗️ Project Structure

```
medical-oncall-sim/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # ⏳ Phase 2
│   │   ├── config.py                  # ⏳ Phase 2
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── sessions.py            # ⏳ Phase 2
│   │   │   └── actions.py             # ⏳ Phase 2
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── events.py              # ✅ Phase 1
│   │   │   ├── patient.py             # ✅ Phase 1
│   │   │   ├── actions.py             # ✅ Phase 1
│   │   │   ├── simulation.py          # ✅ Phase 1
│   │   │   └── ehr.py                 # 📅 Phase 3
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── simulation_engine.py   # ⏳ Phase 2
│   │   │   ├── scenario_loader.py     # ⏳ Phase 2
│   │   │   ├── ehr_service.py         # 📅 Phase 3
│   │   │   ├── nurse_ai.py            # 📅 Phase 4
│   │   │   └── feedback_generator.py  # 📅 Phase 6
│   │   └── utils/
│   │       └── openai_client.py       # 📅 Phase 4
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_simulation_engine.py  # ✅ Phase 1
│   │   └── test_api/                  # ⏳ Phase 2
│   ├── venv/                          # ✅ Created
│   ├── requirements.txt               # ✅ Phase 1
│   └── demo_simulation.py             # ✅ Phase 1
│
├── frontend/                          # 📅 Phase 5
│
├── data/
│   ├── scenarios/
│   │   ├── simple_test.json           # ✅ Phase 1
│   │   ├── med_oncall_001.json        # 📅 Phase 7
│   │   └── schema.json                # 📅 Phase 7
│   └── sessions/
│       ├── active/                    # For in-progress sessions
│       └── completed/                 # For finished sessions
│
├── docs/
│   ├── phase1-complete.md             # ✅ Phase 1
│   └── api_reference.md               # ⏳ Phase 2
│
├── scripts/
│   └── validate_scenario.py           # 📅 Phase 7
│
├── .env.example                       # ✅ Created
├── .gitignore                         # ✅ Created
├── README.md                          # ✅ Created
└── CLAUDE.md                          # ✅ This file

Legend: ✅ Complete | ⏳ Current | 📅 Planned
```

---

## 🔑 Key Technical Decisions

### 1. Deterministic Simulation
- Time advances ONLY when user takes actions
- No background timers or real-time progression
- Ensures reproducibility for testing and debugging
- Same action sequence = identical results every time

### 2. Rule-Based State Transitions (Not Physiology)
- Discrete states: STABLE, STABLE_WITH_CONCERNS, DETERIORATING, CRITICALLY_UNWELL
- Transparent rules defined in scenario JSON
- Three trigger types:
  - `time_elapsed`: Changes at specific sim time
  - `action_taken`: Changes when user does something
  - `action_not_taken`: Changes if user misses deadline
- Educator-authorable without coding

### 3. Event Scheduler Architecture
- Priority queue (Python heapq)
- Events scheduled at specific sim times
- Processed when clock advances past their scheduled time
- Supports delayed results, patient deteriorations, new requests

### 4. JSON Storage for MVP
- Scenarios: Static JSON files (version controlled)
- Sessions: Temporary JSON (active) + archived (completed)
- No database needed for MVP
- Easy to inspect/debug
- Can migrate to SQLite/PostgreSQL later

### 5. FastAPI over Flask
- Type safety with Pydantic (critical for complex simulation logic)
- Async support for future AI/WebSocket integration
- Auto-generated API docs (OpenAPI/Swagger)
- Modern Python standards

### 6. Hybrid Real-Time Clock (UPDATED 2026-02-01)
**IMPORTANT CHANGE**: Clock model updated from pure action-based to hybrid real-time

- **OLD**: Time only advanced when user took actions (fully deterministic but no time pressure)
- **NEW**: Clock runs in **real time** + **in-person reviews add artificial time**
  - Simulation time = Real elapsed time + Artificial time penalties
  - Only **review_in_person** adds artificial time (+30 mins)
  - Other actions (chat, escalate, document) happen in real time
  - Creates **time pressure** - students can't pause forever
  - More realistic on-call experience

**Example**:
```
Student starts at 20:00
Student thinks for 5 real minutes → 20:05 (real time passed)
Student reviews patient in person → 20:35 (+30 artificial mins added)
Total: 35 simulated minutes (5 real + 30 artificial)
```

**Pedagogical Benefits**:
- Real time pressure (can't pause indefinitely)
- In-person reviews are "expensive" (encourages phone triage)
- Balances realism with practical training

**See**: [docs/clock-model-change.md](docs/clock-model-change.md) for full details

---

## 🚀 Quick Start Guide

### Setup (First Time)

```bash
cd medical-oncall-sim/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp ../.env.example ../.env
# Edit .env and add OPENAI_API_KEY (needed for Phase 4+)
```

### Running Tests

```bash
cd backend
source venv/bin/activate
PYTHONPATH=$(pwd) pytest tests/test_simulation_engine.py -v
```

Expected: `17 passed in 0.34s`

### Running Demo

```bash
cd backend
source venv/bin/activate
PYTHONPATH=$(pwd) python demo_simulation.py
```

### Running API (Phase 2+)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## 📝 Current Action Items

### Immediate Next Steps (Phase 2)

1. **Create `app/main.py`**
   - Initialize FastAPI app
   - Add CORS middleware
   - Include API routers
   - Add health check endpoint

2. **Create `app/config.py`**
   - Load environment variables
   - Configure paths (scenarios, sessions)
   - Set up logging

3. **Create `app/services/scenario_loader.py`**
   - Load scenario JSON files
   - Validate scenario structure
   - Convert JSON to Pydantic models

4. **Create `app/services/simulation_engine.py`**
   - Refactor SimulationSession into service
   - Add session persistence (save/load from JSON)
   - Session lifecycle management

5. **Create `app/api/sessions.py`**
   - POST `/sessions/start` - Create session from scenario
   - GET `/sessions/{id}` - Get current state
   - POST `/sessions/{id}/complete` - Complete session

6. **Create `app/api/actions.py`**
   - POST `/sessions/{id}/actions` - Execute action

7. **Test API with curl/Postman**
   - Start session
   - Execute actions
   - Verify time advances
   - Check events trigger correctly

---

## 🧪 Testing Strategy

### Unit Tests (Phase 1 ✅)
- Core simulation engine fully tested
- All edge cases covered
- Determinism verified

### Integration Tests (Phase 2 ⏳)
- API endpoint testing with FastAPI TestClient
- Session lifecycle tests
- Action execution end-to-end

### Scenario Tests (Phase 7 📅)
- Automated playthrough with predetermined actions
- Assert expected outcomes
- Validate scenario JSON structure

### Manual Tests
- AI conversation quality (Phase 4)
- UI/UX flow (Phase 5)
- End-to-end session completion (Phase 5)

---

## 🐛 Known Issues / TODOs

### Technical Debt
- [ ] Pydantic deprecation warnings (class-based config → ConfigDict)
  - Low priority, will fix in Phase 2 refactor
  - 12 warnings in current tests

### Future Enhancements
- [ ] WebSocket support for real-time notifications (post-MVP)
- [ ] Session replay/recording feature (post-MVP)
- [ ] Multi-patient concurrent management (expand from 1 to 4 patients)
- [ ] Medication prescribing system (explicitly out of scope for MVP)

---

## 📚 Reference Documents

### Project Planning
- [Implementation Plan](/.claude/plans/snug-launching-bird.md) - Complete 7-phase roadmap
- [Overview & MVP Definition](../Overview-&-MVP-definition.txt) - Original requirements

### Technical Documentation
- [Phase 1 Complete](docs/phase1-complete.md) - Detailed Phase 1 summary
- [API Reference](docs/api_reference.md) - ⏳ To be created in Phase 2

### Key Concepts
- **Simulated Time**: Advances only with user actions, not real time
- **Patient Trajectory**: Pre-defined clinical path with branching based on decisions
- **Event Queue**: Scheduled future occurrences (results, deteriorations)
- **State Machine**: Discrete patient states with rule-based transitions
- **Determinism**: Same actions always produce same results

---

## 💡 Tips for Future Claude Sessions

### When Resuming Work

1. **Read this file first** - Get up to speed on current status
2. **Check the Progress Tracker** - Know what phase we're in
3. **Review recent docs** - Check `docs/phase*-complete.md` files
4. **Run tests** - Verify nothing broke: `pytest tests/ -v`
5. **Check todos** - Look at "Current Action Items" section

### When Adding Features

1. **Update this file** - Mark tasks complete, add new ones
2. **Write tests first** - Maintain high test coverage
3. **Document decisions** - Add to "Key Technical Decisions"
4. **Update structure diagram** - Keep file tree current

### When Completing a Phase

1. **Create `docs/phase{N}-complete.md`** - Document what was built
2. **Update Progress Tracker** - Mark phase complete
3. **Update Project Structure** - Change status icons
4. **Run full test suite** - Ensure nothing regressed
5. **Update "Last Updated"** date at top of this file

---

## 🔗 Useful Commands

```bash
# Activate virtual environment
cd backend && source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_simulation_engine.py -v

# Run demo
python demo_simulation.py

# Start API server (Phase 2+)
uvicorn app.main:app --reload --port 8000

# Check code with type checker (future)
mypy app/

# Format code (future)
black app/ tests/

# Install new dependency
pip install package-name
pip freeze > requirements.txt
```

---

## 📞 Questions for Developer

When resuming or before proceeding:

1. **Time available?** - Know how much can be done in session
2. **Phase goals?** - Complete current phase or just make progress?
3. **Testing preference?** - Write tests first or after implementation?
4. **Scenario content?** - Use placeholder clinical data or need realistic?
5. **Deployment target?** - Local only for now, or plan for cloud?

---

**Remember**: This is a solo developer project optimized for incremental progress. Each phase is designed to be completable in 1-2 weeks of part-time work. Focus on getting each phase fully working before moving to the next.

**Current Goal**: Complete Phase 2 (API Layer) to enable API-based testing before building frontend.

---

*This file should be updated at the start and end of each development session.*
