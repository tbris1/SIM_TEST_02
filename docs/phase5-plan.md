# Phase 5: Frontend UI Implementation Plan

**Created**: 2026-02-02
**Status**: Approved & Ready for Implementation

---

## Overview

Build a React + TypeScript + Vite frontend for the medical on-call simulation platform, connecting to the existing FastAPI backend (21 REST endpoints, 99% test coverage).

**Key Decisions:**
- **Tech Stack**: React + TypeScript + Vite + Tailwind CSS
- **State Management**: React Context + useReducer
- **MVP Scope**: Single-patient focus with full simulation flow
- **Target**: Desktop only (1280px+)
- **Aesthetic**: Clean EHR-inspired design (dark blue sidebar, white content, professional medical software look)

## Backend API Ready

**21 endpoints across 3 domains:**
- **Sessions** (7): Start, get state, timeline, list, complete, delete
- **Actions** (7): Review patient, escalate, order investigations, document, nurse chat
- **EHR** (7): Get patient record, visibility, order investigations, add notes/results

**CORS configured** for `localhost:3000` and `localhost:5173`

## Implementation Steps

### STEP 1: Project Setup (2-3 hours)

**Goal**: Initialize Vite + React + TypeScript + Tailwind CSS

**Tasks:**
1. Run `npm create vite@latest . -- --template react-ts` in `frontend/` directory
2. Install dependencies:
   ```bash
   npm install
   npm install -D tailwindcss postcss autoprefixer
   npm install axios date-fns react-router-dom
   ```
3. Configure Tailwind with EHR-inspired color palette:
   - `sidebar-bg: #1e3a5f` (dark blue)
   - Status colors: stable (green), concerns (orange), deteriorating (red), critical (dark red)
4. Create project structure:
   ```
   src/
   ├── api/          # API client (types, sessions, actions, ehr)
   ├── components/   # UI components (layout, patient, ehr, actions, nurse, simulation, common)
   ├── context/      # SimulationContext
   ├── hooks/        # useSimulation, usePolling
   ├── pages/        # StartPage, SimulationPage, SummaryPage
   ├── types/        # TypeScript interfaces
   └── utils/        # Formatters, constants
   ```

**Verification:**
- `npm run dev` runs on `localhost:5173`
- Tailwind classes work
- TypeScript compiles without errors

---

### STEP 2: API Client Layer (3-4 hours)

**Goal**: Create type-safe API client with full backend contract modeling

**Critical Files:**
- `src/api/types.ts` - TypeScript interfaces for all API responses (ClockState, SessionResponse, PatientDetailsResponse, EHRRecordResponse, etc.)
- `src/api/client.ts` - Axios instance with base URL `http://localhost:8000/api/v1`
- `src/api/sessions.ts` - Session management endpoints
- `src/api/actions.ts` - Action execution endpoints (review, escalate, nurse chat, etc.)
- `src/api/ehr.ts` - EHR access endpoints

**Key Types to Define:**
- Enums: `PatientState`, `NoteType`
- Session: `SessionResponse`, `SessionStateResponse`, `ClockState`
- Patient: `PatientDetailsResponse`, state history
- EHR: `ClinicalNote`, `InvestigationResult`, `EHRRecordResponse`
- Actions: `ExecuteActionResponse`, `NurseMessageResponse`

**Verification:**
- Import types in components - autocomplete works
- Test API calls from browser console

---

### STEP 3: State Management (3-4 hours)

**Goal**: Global simulation state with Context + useReducer

**Critical Files:**
- `src/types/simulation.ts` - SimulationState interface and action types
- `src/context/SimulationContext.tsx` - Provider with reducer logic
- `src/hooks/useSimulation.ts` - Custom hook for simulation actions
- `src/hooks/usePolling.ts` - Polling hook for clock updates

**State Shape:**
```typescript
{
  sessionId, scenarioId, isActive, isComplete
  clock (time, elapsed, artificial minutes)
  currentPatient (details, state, history)
  currentPatientEHR (notes, results, visibility)
  notifications (alerts, state changes)
  nurseConversation (chat history)
  isLoading, error
}
```

**Actions:**
- `startSession(scenarioId)` - Start new session, fetch initial data
- `refreshSessionState()` - Poll for clock updates
- `reviewPatient()` - Execute in-person review action
- `sendNurseMessage(message)` - AI nurse chat
- `completeSession()` - End session and get summary

**Verification:**
- Wrap App in SimulationProvider
- Test state updates from console

---

### STEP 4: Layout & Common Components (2-3 hours)

**Goal**: Reusable UI components and app shell

**Components to Build:**
- `common/Button.tsx` - Variants: primary, secondary, danger, success
- `common/Card.tsx` - Container with optional title
- `common/Badge.tsx` - Status badges with state-based colors
- `common/Modal.tsx` - Reusable modal dialog
- `common/LoadingSpinner.tsx` - Loading indicator
- `layout/AppShell.tsx` - Main layout with sidebar and header
- `layout/Sidebar.tsx` - Dark blue navigation sidebar
- `layout/Header.tsx` - Top header with clock

**Styling:**
- Dark blue sidebar (`#1e3a5f`)
- White content areas
- Colored badges for patient states
- Professional medical software aesthetic

**Verification:**
- Render AppShell with dummy content
- Test button variants and badge colors
- Check layout at 1280px+

---

### STEP 5: Simulation Clock (1-2 hours)

**Goal**: Real-time clock display with polling

**Component:**
- `simulation/SimulationClock.tsx` - Display current time, elapsed time, artificial time

**Behavior:**
- Poll `refreshSessionState()` every 2 seconds (when session active)
- Show formatted simulation time (HH:mm)
- Show elapsed time (Xh Ym)
- Highlight artificial time added by in-person reviews

**Utilities:**
- `utils/formatters.ts` - formatTime, formatDateTime, formatElapsed functions
- `utils/constants.ts` - API_BASE_URL, POLL_INTERVAL_MS (2000)

**Verification:**
- Start session and verify clock updates every 2s
- Check artificial time displays after in-person review
- Confirm polling stops when session completes

---

### STEP 6: Session Start Page (2-3 hours)

**Goal**: Scenario selection and session initialization

**Component:**
- `pages/StartPage.tsx` - List scenarios, start session button

**Flow:**
1. Load scenarios from `GET /api/v1/scenarios`
2. Display scenario cards with title, description, difficulty, duration, patient count
3. Click "Start Session" → call `startSession(scenarioId)`
4. Navigate to `/simulation` on success

**Verification:**
- Load start page and see scenario list
- Start session and verify navigation
- Check backend creates session

---

### STEP 7: Patient Card & EHR Viewer (4-5 hours)

**Goal**: Display patient information and EHR with progressive revelation

**Components:**
- `patient/PatientCard.tsx` - Patient overview with demographics and current state
- `ehr/EHRViewer.tsx` - Main EHR container with tabs/sections
- `ehr/ClinicalNotesList.tsx` & `ClinicalNoteCard.tsx` - Clinical notes display
- `ehr/InvestigationsList.tsx` & `InvestigationCard.tsx` - Investigation results
- `ehr/PatientSummary.tsx` - Allergies, diagnoses, medications (always visible)

**EHR Features:**
- Always visible: demographics, allergies, diagnoses, medications
- Progressive revelation indicator: "Visible: X/Y notes, X/Y results"
- Refresh EHR every 5 seconds to catch new investigation results
- Structured display of clinical notes with timestamps, authors, content
- Investigation results with abnormal flags and interpretation

**Verification:**
- Load patient EHR and verify data displays
- Check progressive revelation indicator updates
- Verify clinical notes and results render properly
- Test with scenario from backend

---

### STEP 8: Action Panel & Modals (4-5 hours)

**Goal**: Quick-access action buttons with modal dialogs

**Components:**
- `actions/ActionPanel.tsx` - Grid of action buttons
- `actions/ReviewPatientModal.tsx` - Confirm in-person review (30 min cost)
- `actions/OrderInvestigationModal.tsx` - Select investigation type and urgency
- `actions/EscalateModal.tsx` - Escalate to senior with reason
- `actions/DocumentNoteModal.tsx` - Free-text note entry

**Modal Features:**
- Time cost warnings (review: 30m, escalate: 5m, investigate: 2m)
- Investigation dropdown: ABG, FBC, U&E, CXR, ECG with turnaround times
- Confirmation buttons with loading states
- Auto-refresh patient and EHR after action

**Verification:**
- Click action buttons and verify modals open
- Test each action and confirm API calls succeed
- Verify time advances correctly
- Check EHR updates with new data

---

### STEP 9: Nurse Chat (3-4 hours)

**Goal**: AI-powered chat interface with conversation history

**Components:**
- `nurse/NurseChat.tsx` - Main chat container
- `nurse/ChatMessage.tsx` - Individual message bubble (nurse vs doctor styling)
- `nurse/ChatInput.tsx` - Text input with send button

**Features:**
- Display conversation history from state
- Send message → `POST /api/v1/sessions/{id}/nurse/message`
- Auto-scroll to latest message
- Loading state while waiting for AI response
- Distinct styling for nurse (gray bubble) vs doctor (blue bubble) messages

**Verification:**
- Send messages and verify they appear
- Check nurse AI responses arrive
- Verify conversation history persists
- Test chat during active simulation

---

### STEP 10: Main Simulation Page (2-3 hours)

**Goal**: Compose all components into cohesive simulation UI

**Component:**
- `pages/SimulationPage.tsx` - Main layout with 3-column grid

**Layout:**
```
+------------------+----------------------+------------------+
| Patient Card     | EHR Viewer          | Nurse Chat      |
| (col-span-4)     | (col-span-5)        | (col-span-3)    |
|                  |                      |                  |
| Action Panel     | - Summary           | - Messages       |
|                  | - Clinical Notes    | - Input          |
| Complete Session | - Investigations    |                  |
+------------------+----------------------+------------------+
```

**Features:**
- Notification banner at top for state changes
- Header with simulation clock
- Dark blue sidebar navigation
- Complete Session button (danger variant)

**Verification:**
- Load simulation page with active session
- Verify all components render correctly
- Test responsive layout at 1280px+
- Navigate between sections

---

### STEP 11: Session Summary Page (2-3 hours)

**Goal**: Timeline visualization and completion summary

**Component:**
- `pages/SummaryPage.tsx` - Session statistics and timeline

**Display:**
- Summary cards: total time elapsed, actions taken, patients managed
- Patient outcomes: final state for each patient with badge
- Timeline: chronological list of all events/actions
- "Start New Session" button

**Verification:**
- Complete session and navigate to summary
- Verify statistics display correctly
- Check timeline renders chronologically
- Test "Start New Session" navigation

---

### STEP 12: Routing & App Entry (1-2 hours)

**Goal**: Wire up React Router and app initialization

**Files:**
- `src/App.tsx` - Router with SimulationProvider wrapper
- `src/main.tsx` - React root render
- `.env` - VITE_API_BASE_URL=http://localhost:8000
- `vite.config.ts` - Dev server config, API proxy

**Routes:**
- `/` - StartPage (scenario selection)
- `/simulation` - SimulationPage (active session)
- `/summary` - SummaryPage (completion timeline)

**Verification:**
- Start both backend and frontend
- Navigate through full flow: Start → Simulation → Summary
- Test browser back/forward buttons

---

### STEP 13: Error Handling (1-2 hours)

**Goal**: Graceful error handling and user feedback

**Tasks:**
- Add error boundaries to pages
- Display error messages in UI (red banner)
- Loading spinners during API calls
- Network timeout handling
- Retry logic for failed requests

**Verification:**
- Test with backend offline - see error messages
- Test slow network - see loading spinners
- Verify error recovery when backend returns

---

### STEP 14: Testing & Polish (2-3 hours)

**Goal**: End-to-end testing and UI polish

**Testing Checklist:**
- [ ] Start session from scenario list
- [ ] Clock updates every 2 seconds
- [ ] Review patient → new examination note appears
- [ ] Send nurse message → get AI response
- [ ] Order investigation → wait for result
- [ ] Escalate patient → state change occurs
- [ ] Complete session → view summary with timeline

**UI Polish:**
- [ ] Hover states on buttons
- [ ] Smooth transitions and animations
- [ ] Consistent spacing and typography
- [ ] Color contrast for accessibility
- [ ] Test at 1280px, 1440px, 1920px

**Verification:**
- Complete full simulation without errors
- All features work as expected
- Console clean (no warnings/errors)

---

## Critical Files

**Top 5 files for Phase 5 implementation:**

1. **`frontend/src/api/types.ts`** - TypeScript interfaces for all 21 API endpoints; ensures type safety throughout app

2. **`frontend/src/context/SimulationContext.tsx`** - Global state management with Context + useReducer; handles session lifecycle, patient data, notifications, chat history

3. **`frontend/src/hooks/useSimulation.ts`** - Custom hook encapsulating all simulation actions; abstracts API calls and state updates

4. **`frontend/src/pages/SimulationPage.tsx`** - Main simulation UI composing patient card, EHR, actions, and nurse chat; primary user experience

5. **`frontend/src/components/ehr/EHRViewer.tsx`** - Complex progressive revelation logic; demonstrates key pedagogical feature

---

## Dependencies & Sequencing

**Critical Path:**
1. Setup (Step 1) → API Client (Step 2) → State Management (Step 3)
2. Layout (Step 4) → Clock (Step 5)
3. Start Page (Step 6) enables session creation
4. Patient/EHR (Step 7) + Actions (Step 8) + Nurse Chat (Step 9) in parallel
5. Simulation Page (Step 10) composes above
6. Summary (Step 11) + Routing (Step 12) finalize navigation
7. Error Handling (Step 13) + Testing (Step 14) for production readiness

**Milestones:**
- After Step 3: Can start session programmatically
- After Step 6: Can start session via UI
- After Step 10: Full single-patient simulation works
- After Step 12: Complete flow start to summary
- After Step 14: Production-ready MVP

---

## Verification Strategy

**At Each Step:**
1. Run `npm run dev` - verify no TypeScript errors
2. Test component in isolation with dummy data
3. Verify API integration with live backend
4. Check console for errors/warnings

**End-to-End Test:**
1. Start backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:5173`
4. Select scenario "simple_test_ehr"
5. Review patient → verify new examination note
6. Chat with nurse → verify AI response
7. Order investigation → wait for result
8. Complete session → view timeline
9. Start new session → repeat

**Success Criteria:**
- ✅ All components render without errors
- ✅ Clock updates in real-time (every 2s)
- ✅ Actions trigger time advancement and state changes
- ✅ AI nurse chat works with context-aware responses
- ✅ EHR progressive revelation functions correctly
- ✅ Session can be completed and summary viewed
- ✅ No console errors or warnings
- ✅ TypeScript compiles without issues

---

## Estimated Duration

**Total: 28-38 hours** (1-2 weeks at 20 hours/week)

Breakdown by component:
- Setup & Config: 2-3h
- API Layer: 3-4h
- State Management: 3-4h
- Layout & Common: 2-3h
- Clock: 1-2h
- Start Page: 2-3h
- Patient & EHR: 4-5h
- Action Panel: 4-5h
- Nurse Chat: 3-4h
- Simulation Page: 2-3h
- Summary Page: 2-3h
- Routing: 1-2h
- Error Handling: 1-2h
- Testing & Polish: 2-3h

---

## Next Steps After Phase 5

Once frontend MVP is complete:
1. **Phase 6: AI Feedback** - Add GPT-4 feedback generation on session completion
2. **Phase 7: Scenarios & Polish** - Create 2-3 complete clinical scenarios, UI polish, end-to-end testing
3. **Multi-patient expansion** - Scale from 1 to 4 patients simultaneously
4. **Mobile responsiveness** - Adapt layout for tablets and phones
5. **Deployment** - Docker containers, cloud hosting, CI/CD pipeline
