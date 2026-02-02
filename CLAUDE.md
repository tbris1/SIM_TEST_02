# CLAUDE.md - Project Context & Progress

**Last Updated**: 2026-02-02
**Project**: Medical On-Call Simulation Platform MVP
**Status**: Phases 1-3 Complete ✅ | Phase 4 (AI Integration) Near Complete 🚧 (70%)

---

## 🎯 Project Overview

A web-based simulation platform for training final-year medical students in managing multiple patients during on-call shifts. Focus on prioritization, escalation, and managing uncertainty - NOT complex physiology modeling.

**Key Features**:
- Time-based mechanics (60 min real time = 3-4 hours sim time)
- AI-driven nurse interactions (GPT-5)
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
**Completed**: 2026-02-01

**What was built**:
- [x] SimulationClock - Time management (hybrid real-time model)
- [x] EventScheduler - Priority queue for delayed events
- [x] Patient State Machine - 4 discrete states with rule-based transitions
- [x] User Actions - 5 action types with time costs
- [x] SimulationSession - Main orchestrator
- [x] Comprehensive unit tests (17 tests, 100% passing)
- [x] Demo simulation script
- [x] Simple test scenario JSON

**Documentation**: See [docs/phase1-complete.md](docs/phase1-complete.md)

---

#### Phase 2: API Layer with FastAPI (COMPLETE)
**Status**: ✅ All tests passing (33/33)
**Completed**: 2026-02-01

**What was built**:
- [x] FastAPI app with CORS configuration
- [x] Session management endpoints (create, read, list, delete)
- [x] Action execution endpoints (5 convenience + 1 generic)
- [x] Scenario loader service
- [x] Simulation engine service
- [x] Comprehensive API tests
- [x] OpenAPI/Swagger documentation

**API Endpoints** (14 total):
- Session management: `/api/v1/sessions/*`, `/api/v1/scenarios`
- Action execution: `/api/v1/sessions/{id}/actions/*`

**Documentation**: See [docs/api_reference.md](docs/api_reference.md)

---

#### Phase 3: EHR System (COMPLETE)
**Status**: ✅ Tests passing (26/27) - 1 minor test failure
**Completed**: 2026-02-01

**What was built**:
- [x] PatientRecord model with progressive revelation
- [x] ClinicalNote and InvestigationResult models
- [x] VisibilityRule with time and action-based conditions
- [x] EHRService for managing patient records
- [x] EHR API endpoints (4 new endpoints)
- [x] Dynamic examination note generation
- [x] Investigation ordering system
- [x] Comprehensive EHR tests

**Key Revision**: In-person reviews now **generate new examination notes** dynamically based on patient state, rather than revealing pre-existing hidden notes. All existing clinical notes are always visible in EHR.

**Documentation**: See [docs/phase3-complete.md](docs/phase3-complete.md) and [docs/phase3-ehr-revision.md](docs/phase3-ehr-revision.md)

---

### 🔄 Current Phase

#### Phase 4: AI Integration - Nurse Chat (NEAR COMPLETE)
**Status**: 🚧 70% Complete | 76/77 tests passing

**What's Done**:
- [x] Two-stage LLM pattern implementation
- [x] OpenAI GPT-5 client integration
- [x] Nurse interaction logic with topic classification
- [x] API endpoint for nurse messaging
- [x] Nursing impressions in patient state data
- [x] Initial nurse request system
- [x] Context filtering and fallback handling

**What Remains**:
- [ ] Comprehensive tests for AI interactions (mocked)
- [ ] Testing with real OpenAI GPT-5 API
- [ ] Prompt refinement based on clinical realism
- [ ] Conversation history tracking for multi-turn dialogues
- [ ] Performance testing and optimization

**Key Files**:
- `backend/app/services/nurse_logic.py` - Two-stage LLM pattern
- `backend/app/api/actions.py` - Nurse message endpoint

**New API Endpoint**:
```
POST   /api/v1/sessions/{id}/nurse/message   # Send message to nurse AI
```

**Two-Stage LLM Pattern**:
1. **Router LLM** - Classifies question to filter relevant nursing impression data
2. **Response LLM** - Generates realistic nurse response using filtered context

---

### 📋 Upcoming Phases

#### Phase 5: Frontend - React UI (NEXT - Plan Ready)
**Status**: 📋 Implementation plan complete
**Documentation**: [docs/phase5-plan.md](docs/phase5-plan.md)
**Started**: Not yet

**Tech Stack**:
- React + TypeScript + Vite
- Tailwind CSS (EHR-inspired aesthetic)
- React Context + useReducer for state management
- Desktop-only (1280px+), single-patient MVP

**14-Step Implementation Plan**:
1. Project setup with Vite + Tailwind
2. Type-safe API client layer (21 endpoints)
3. Global state management
4. Layout components and app shell
5. Real-time simulation clock
6. Session start page
7. Patient card & EHR viewer with progressive revelation
8. Action panel with modals
9. AI nurse chat interface
10. Main simulation page (3-column layout)
11. Session summary with timeline
12. React Router setup
13. Error handling and loading states
14. Testing and UI polish

**Estimated Duration**: 28-38 hours (1-2 weeks at part-time pace)

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
│   │   ├── main.py                    # ✅ Phase 2
│   │   ├── config.py                  # ✅ Phase 2
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── sessions.py            # ✅ Phase 2
│   │   │   ├── actions.py             # ✅ Phase 2 + 🚧 Phase 4
│   │   │   └── ehr.py                 # ✅ Phase 3
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── events.py              # ✅ Phase 1
│   │   │   ├── patient.py             # ✅ Phase 1
│   │   │   ├── actions.py             # ✅ Phase 1
│   │   │   ├── simulation.py          # ✅ Phase 1
│   │   │   └── ehr.py                 # ✅ Phase 3
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── simulation_engine.py   # ✅ Phase 2
│   │   │   ├── scenario_loader.py     # ✅ Phase 2
│   │   │   ├── ehr_service.py         # ✅ Phase 3
│   │   │   ├── nurse_logic.py         # 🚧 Phase 4
│   │   │   └── feedback_generator.py  # 📅 Phase 6
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_simulation_engine.py  # ✅ Phase 1
│   │   ├── test_ehr_system.py         # ✅ Phase 3
│   │   └── test_api/                  # ✅ Phase 2 & 3
│   │       ├── test_sessions.py
│   │       ├── test_actions.py
│   │       └── test_ehr.py
│   ├── venv/                          # ✅ Created
│   ├── requirements.txt               # ✅ Updated
│   ├── demo_simulation.py             # ✅ Phase 1
│   ├── demo_ehr_system.py             # ✅ Phase 3
│   └── demo_nurse_ai.py               # ✅ Phase 4
│
├── frontend/                          # 📅 Phase 5
│
├── data/
│   ├── scenarios/
│   │   ├── simple_test_001.json       # ✅ Phase 1
│   │   ├── simple_test_ehr.json       # ✅ Phase 3 (with nursing impressions)
│   │   ├── med_oncall_001.json        # 📅 Phase 7
│   │   └── schema.json                # 📅 Phase 7
│   └── sessions/
│       ├── active/                    # For in-progress sessions
│       └── completed/                 # For finished sessions
│
├── docs/
│   ├── phase1-complete.md             # ✅ Phase 1
│   ├── phase3-complete.md             # ✅ Phase 3
│   ├── phase3-ehr-revision.md         # ✅ Phase 3
│   ├── api_reference.md               # ✅ Phase 2
│   └── clock-model-change.md          # ✅ Phase 1 update
│
├── scripts/
│   └── validate_scenario.py           # 📅 Phase 7
│
├── .env.example                       # ✅ Created
├── .gitignore                         # ✅ Created
├── README.md                          # ✅ Created
├── PROGRESS.md                        # ✅ Updated
└── CLAUDE.md                          # ✅ This file

Legend: ✅ Complete | 🚧 Near Complete | 📅 Planned
```

---

## 🔑 Key Technical Decisions

### 1. Deterministic Simulation
- Time advances in real time, AND when user chooses to "review in person"
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
pytest tests/ -v
```

Expected: `76 passed, 1 failed` (1 minor EHR test failure - unrelated to AI)

To run specific test suites:
```bash
pytest tests/test_simulation_engine.py -v  # Core engine (17 tests)
pytest tests/test_api/ -v                   # API layer (47 tests)
pytest tests/test_ehr_system.py -v          # EHR system (13 tests)
```

### Running Demos

```bash
cd backend
source venv/bin/activate

# Core simulation demo
PYTHONPATH=$(pwd) python demo_simulation.py

# EHR system demo
PYTHONPATH=$(pwd) python demo_ehr_system.py

# AI Nurse demo (requires OpenAI API key in .env)
python demo_nurse_ai.py
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

### Immediate Next Steps (Complete Phase 4 or Start Phase 5)

**Option A: Complete Phase 4 (AI Integration)**

1. **Create tests for nurse AI**
   - Mock OpenAI API responses
   - Test router classification logic
   - Test response generation
   - Test API endpoint with various questions
   - Add to test suite

2. **Test with real OpenAI GPT-5 API**
   - Configure API key in `.env`
   - Test with realistic doctor questions
   - Verify nursing impressions are correctly filtered
   - Validate response quality and clinical realism

3. **Refine prompts**
   - Adjust router system prompt for better classification
   - Enhance nurse response prompt for more realistic dialogue
   - Test edge cases (ambiguous questions, clarifications)
   - Iterate based on clinical feedback

4. **Add conversation history**
   - Track multi-turn conversations
   - Maintain context across messages
   - Store in session state

**Option B: Start Phase 5 (Frontend UI)**

1. **Setup React + Vite + TypeScript**
   - Initialize frontend project
   - Configure build tools
   - Setup API client

2. **Create core components**
   - SimulationClock
   - RequestInbox
   - NurseChat
   - EHRViewer
   - ActionPanel

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

**Current Goal**: Either complete Phase 4 (AI Integration) with tests and refinement, OR begin Phase 5 (Frontend UI) to enable end-to-end testing of the full system including AI nurse interactions.

---

*This file should be updated at the start and end of each development session.*
