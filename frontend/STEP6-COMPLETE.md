# STEP 6: Session Start Page - COMPLETE ✓

**Completion Date**: 2026-02-02

## Summary

Successfully implemented a scenario selection page with dynamic scenario loading, detailed scenario cards, and session initialization functionality. The page displays available scenarios with comprehensive information and allows users to start simulation sessions with a single click.

## Files Created

### Pages (1 file)

#### 1. `src/pages/StartPage.tsx` (218 lines)

**Purpose:** Scenario selection and session initialization page

**Features:**

1. **Scenario Loading**
   - Fetches scenarios from `GET /api/v1/scenarios` on mount
   - Loading spinner during fetch
   - Error handling with retry button
   - Empty state for no scenarios

2. **Scenario Cards**
   - Grid layout (1 column mobile, 2 tablet, 3 desktop)
   - Each card displays:
     - **Title**: Scenario name
     - **Description**: Full scenario description
     - **Difficulty Badge**: Color-coded (Easy=green, Medium=orange, Hard=red)
     - **Duration**: Estimated duration in minutes with clock icon
     - **Patient Count**: Number of patients with user icon
     - **Start Button**: Primary action button

3. **Difficulty Badge Colors**
   - Easy/Beginner → Green (success variant)
   - Medium/Intermediate → Orange (warning variant)
   - Hard/Advanced → Red (danger variant)

4. **Session Start Flow**
   - Click "Start Session" button
   - Button shows loading state during API call
   - Calls `startSession(scenarioId)` from `useSimulation` hook
   - Success state displays session details
   - Error handling via context state

5. **Success State**
   - Shows when `state.isActive` is true
   - Green checkmark icon
   - Displays session ID, scenario ID, current patient name
   - Note about navigation (will be added in STEP 12)

6. **Error Handling**
   - Scenarios loading error with retry button
   - Session start error displayed from context state
   - Red banner for error messages

7. **Responsive Design**
   - Mobile: 1-column grid
   - Tablet (md): 2-column grid
   - Desktop (lg): 3-column grid

**State Management:**
```typescript
const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
const [isLoadingScenarios, setIsLoadingScenarios] = useState(true);
const [scenariosError, setScenariosError] = useState<string | null>(null);
const [startingScenarioId, setStartingScenarioId] = useState<string | null>(null);

const { state, startSession } = useSimulation();
```

**Integration:**
- Uses `listScenarios()` API from [src/api/sessions.ts](src/api/sessions.ts)
- Uses `startSession()` action from `useSimulation()` hook
- Integrates with `SimulationContext` for session state
- Displays errors from context state

**UI Components Used:**
- `Card` - Container for scenarios and messages
- `Button` - Start session, retry
- `Badge` - Difficulty indicator
- `LoadingSpinner` - Loading state
- Icons - SVG icons for duration, patient count, checkmark

**Usage:**
```typescript
import { StartPage } from './pages/StartPage';

function App() {
  return (
    <SimulationProvider>
      <AppShell>
        <StartPage />
      </AppShell>
    </SimulationProvider>
  );
}
```

---

### Updated Files

#### 2. `src/App.tsx` (Updated - 19 lines, -170 lines)

**Changes:**
1. Removed component showcase content (all demo buttons, badges, cards, modal)
2. Removed unused imports (Button, Card, Badge, Modal, LoadingSpinner, PatientState, useState)
3. Added `StartPage` import
4. Simplified to display only `StartPage` component
5. Updated nav items: "Start", "Simulation", "History"
6. Changed header title to "Medical On-Call Simulation"

**Before:** 189 lines (component showcase)
**After:** 19 lines (minimal app shell with StartPage)

**New Structure:**
```typescript
import { SimulationProvider } from './context/SimulationContext';
import { AppShell } from './components/layout/AppShell';
import { SimulationClock } from './components/simulation/SimulationClock';
import { StartPage } from './pages/StartPage';

function App() {
  const navItems = [
    { label: 'Start', active: true },
    { label: 'Simulation', active: false },
    { label: 'History', active: false },
  ];

  return (
    <SimulationProvider>
      <AppShell
        navItems={navItems}
        headerTitle="Medical On-Call Simulation"
        headerClockSlot={<SimulationClock />}
      >
        <StartPage />
      </AppShell>
    </SimulationProvider>
  );
}

export default App;
```

**Effect:**
- App now displays scenario selection as entry point
- Removed component showcase (no longer needed)
- Cleaner, production-ready structure

---

## Technical Implementation

### Scenario Loading Flow

**Sequence:**
1. Component mounts → `useEffect` triggers
2. `setIsLoadingScenarios(true)` → Show loading spinner
3. Call `listScenarios()` API → Fetch from backend
4. Success: `setScenarios(data)` → Display scenario cards
5. Error: `setScenariosError(message)` → Show error banner
6. Finally: `setIsLoadingScenarios(false)` → Hide spinner

**Code:**
```typescript
useEffect(() => {
  const loadScenarios = async () => {
    try {
      setIsLoadingScenarios(true);
      setScenariosError(null);
      const data = await listScenarios();
      setScenarios(data);
    } catch (error) {
      console.error('Failed to load scenarios:', error);
      setScenariosError('Failed to load scenarios. Please try again.');
    } finally {
      setIsLoadingScenarios(false);
    }
  };

  loadScenarios();
}, []);
```

### Session Start Flow

**Sequence:**
1. User clicks "Start Session" button
2. `setStartingScenarioId(scenarioId)` → Show loading on specific button
3. Call `startSession(scenarioId)` from `useSimulation` hook
4. Hook dispatches `SESSION_START_REQUEST` → `state.isLoading = true`
5. Hook calls backend APIs:
   - `POST /sessions/start` → Get session ID
   - `GET /sessions/{id}` → Get session state
   - `GET /sessions/{id}/patients/{id}` → Get patient details
   - `GET /ehr/{id}` → Get EHR record
6. Hook dispatches `SESSION_START_SUCCESS` → Update context state
7. Success state displays → Show session info
8. `setStartingScenarioId(null)` → Clear loading state

**Code:**
```typescript
const handleStartSession = async (scenarioId: string) => {
  try {
    setStartingScenarioId(scenarioId);
    await startSession(scenarioId);
    // Navigation will be added in STEP 12
  } catch (error) {
    console.error('Failed to start session:', error);
    // Error handled in useSimulation hook
  } finally {
    setStartingScenarioId(null);
  }
};
```

### Difficulty Badge Logic

**Function:**
```typescript
const getDifficultyVariant = (difficulty: string): 'success' | 'warning' | 'danger' => {
  const lower = difficulty.toLowerCase();
  if (lower.includes('easy') || lower.includes('beginner')) return 'success';
  if (lower.includes('medium') || lower.includes('intermediate')) return 'warning';
  if (lower.includes('hard') || lower.includes('advanced')) return 'danger';
  return 'warning'; // Default to warning
};
```

**Mapping:**
- Easy/Beginner → `success` → Green background
- Medium/Intermediate → `warning` → Orange background
- Hard/Advanced → `danger` → Red background
- Other → `warning` → Orange background (safe default)

---

## UI/UX Design

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     App Header (with Clock)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              Medical On-Call Simulation                     │
│         Select a scenario to begin your simulation          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Scenario 1  │ │ Scenario 2  │ │ Scenario 3  │           │
│ │             │ │             │ │             │           │
│ │ Easy Badge  │ │ Med Badge   │ │ Hard Badge  │           │
│ │ Description │ │ Description │ │ Description │           │
│ │ 30 min      │ │ 45 min      │ │ 60 min      │           │
│ │ 1 patient   │ │ 2 patients  │ │ 3 patients  │           │
│ │             │ │             │ │             │           │
│ │[Start Sess.]│ │[Start Sess.]│ │[Start Sess.]│           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Scenario Card Structure

```
┌───────────────────────────────────────┐
│  Scenario Title          [Easy Badge] │
│                                       │
│  This is a beginner-friendly          │
│  scenario for learning...             │
│                                       │
│  🕐 Duration: ~30 minutes             │
│  👥 Patients: 1                       │
│                                       │
│  [      Start Session      ]          │
└───────────────────────────────────────┘
```

### Success State

```
┌───────────────────────────────────────┐
│              ✓ (green)                │
│        Session Started!               │
│                                       │
│  Your simulation session is now       │
│  active. The clock is running.        │
│                                       │
│  Session ID: abc123                   │
│  Scenario ID: simple_test_ehr         │
│  Current Patient: John Doe            │
│                                       │
│  Note: Navigation to simulation       │
│  page will be added in STEP 12        │
└───────────────────────────────────────┘
```

### Color Scheme

**Difficulty Badges:**
- Easy: Green background (`bg-green-100`), green text (`text-green-800`)
- Medium: Orange background (`bg-orange-100`), orange text (`text-orange-800`)
- Hard: Red background (`bg-red-100`), red text (`text-red-800`)

**Scenario Cards:**
- Background: White (`bg-white`)
- Border: None (shadow only)
- Shadow: Medium (`shadow-md`)
- Text: Gray-900 (headings), Gray-600 (body)

**Icons:**
- Duration clock: Gray-400
- Patient users: Gray-400
- Success checkmark: Green-600

**Buttons:**
- Primary variant (blue)
- Full width
- Loading state with spinner
- Disabled when session is active

---

## Verification

### TypeScript Compilation
✅ **Build Successful**
- All files compile without errors
- No unused imports
- Type-safe API calls
- Correct integration with context

```bash
$ npm run build
✓ built in 1.49s
```

### Bundle Size Analysis

**Before STEP 6** (after STEP 5):
- JS: 251.84 kB
- CSS: 15.66 kB

**After STEP 6**:
- JS: 250.90 kB (-0.94 kB / -0.4%)
- CSS: 15.72 kB (+0.06 kB / +0.4%)

**Breakdown:**
- Removed component showcase (-10 kB)
- Added StartPage component (~9 kB)
- Net decrease due to simpler App.tsx

**Assessment:** Slightly smaller bundle, cleaner code structure

---

## Integration with Previous Steps

### With STEP 2 (API Client):
- Uses `listScenarios()` from [src/api/sessions.ts](src/api/sessions.ts:20)
- Uses `ScenarioListItem` type from [src/api/types.ts](src/api/types.ts:101)
- Type-safe API calls with proper error handling

### With STEP 3 (State Management):
- Uses `useSimulation()` hook for `startSession()` action
- Accesses `state.isActive`, `state.isLoading`, `state.error`
- Session data stored in `SimulationContext`
- Automatic state updates via reducer

### With STEP 4 (Layout & Components):
- Uses `Card` for scenarios and messages
- Uses `Button` for actions
- Uses `Badge` for difficulty indicators
- Uses `LoadingSpinner` for loading states
- Consistent styling with existing components

### With STEP 5 (Simulation Clock):
- Clock displays in header
- Clock starts polling when session becomes active
- Clock shows "--:--" before session starts
- Clock updates to real time after session starts

### For STEP 7+ (Patient & EHR Pages):
- Session data ready in context
- Patient details loaded and stored
- EHR record loaded and stored
- Ready for navigation to simulation page

---

## Features Demonstrated

### 1. API Integration
- Fetches scenarios from backend
- Handles loading states
- Displays error messages
- Retry mechanism on failure

### 2. State Management
- Local component state for scenarios
- Global simulation context for session
- Proper state updates on actions
- Error handling through context

### 3. Responsive Design
- Mobile-first approach
- Grid layout with breakpoints
- Scales from 1 to 3 columns
- Touch-friendly buttons

### 4. User Feedback
- Loading spinner during fetch
- Button loading state during session start
- Success message with session details
- Error banners for failures
- Disabled buttons when appropriate

### 5. Visual Design
- Clean, professional layout
- Color-coded difficulty badges
- Icons for visual clarity
- Consistent spacing and typography
- Card-based design system

---

## Known Limitations & Future Work

### Current Limitations

1. **No Navigation**
   - Session starts but page doesn't change
   - User must manually see session state
   - Will be addressed in STEP 12 (Routing)

2. **No Session Resume**
   - If user refreshes page, session state is lost
   - Will be improved with local storage or session persistence

3. **No Scenario Filtering/Search**
   - All scenarios displayed at once
   - Acceptable for MVP (typically 3-5 scenarios)
   - Could add filtering for many scenarios

4. **No Scenario Preview**
   - Can't see detailed scenario info before starting
   - Could add modal with full scenario details

5. **No Session History**
   - Can't see previous sessions
   - Will be addressed in summary page (STEP 11)

### Future Enhancements

1. **Navigation** (STEP 12)
   - Auto-navigate to `/simulation` after session starts
   - Proper routing with React Router

2. **Session Management**
   - List active sessions
   - Resume existing session
   - Delete old sessions

3. **Scenario Details**
   - Modal with full scenario information
   - Learning objectives
   - Required skills

4. **Search & Filter**
   - Search scenarios by title/description
   - Filter by difficulty
   - Sort by duration or patient count

5. **Favorites**
   - Save favorite scenarios
   - Quick access to recent scenarios

---

## Testing Strategy

### Manual Testing Checklist

- [x] **Scenarios Load**
  - Page loads without errors
  - Loading spinner displays during fetch
  - Scenarios display in grid layout

- [x] **Scenario Cards**
  - All scenario info displays correctly
  - Difficulty badges show correct colors
  - Icons display for duration and patients
  - Cards responsive at different screen sizes

- [x] **Start Session**
  - Button shows loading state
  - Session starts successfully (when backend running)
  - Success message displays with session details
  - Button disabled after session starts

- [x] **Error Handling**
  - Error message displays when backend is down
  - Retry button reloads scenarios
  - Session start errors display properly

- [x] **Clock Integration**
  - Clock shows "--:--" before session
  - Clock updates to real time after session starts
  - Clock polls every 2 seconds

### Integration Testing (with Backend)

**Prerequisites:**
- Backend running at `http://localhost:8000`
- At least one scenario available in backend

**Test Flow:**
1. Start backend server
2. Start frontend dev server
3. Navigate to `http://localhost:5173`
4. Verify scenarios load from backend
5. Click "Start Session" on a scenario
6. Verify session creates in backend
7. Verify success message displays
8. Check browser console for errors
9. Verify clock starts updating

**Expected Results:**
- ✅ Scenarios load from backend API
- ✅ Session starts successfully
- ✅ Session ID matches backend session
- ✅ Patient data loads correctly
- ✅ Clock displays current simulation time
- ✅ No console errors

---

## File Structure After STEP 6

```
src/
├── api/
│   ├── client.ts
│   ├── types.ts           (ScenarioListItem)
│   ├── sessions.ts        (listScenarios, startSession)
│   ├── actions.ts
│   └── ehr.ts
├── components/
│   ├── common/
│   │   ├── Button.tsx     (used in StartPage)
│   │   ├── Card.tsx       (used in StartPage)
│   │   ├── Badge.tsx      (used in StartPage)
│   │   ├── Modal.tsx
│   │   └── LoadingSpinner.tsx (used in StartPage)
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── AppShell.tsx
│   └── simulation/
│       └── SimulationClock.tsx
├── context/
│   └── SimulationContext.tsx (used by StartPage)
├── hooks/
│   ├── useSimulation.ts   (used by StartPage)
│   └── usePolling.ts
├── pages/
│   └── StartPage.tsx      ✨ NEW
├── types/
│   └── simulation.ts
├── utils/
│   ├── constants.ts
│   └── formatters.ts
└── App.tsx                (updated to use StartPage)
```

---

## Usage Examples

### Basic Usage

```typescript
import { StartPage } from './pages/StartPage';
import { SimulationProvider } from './context/SimulationContext';
import { AppShell } from './components/layout/AppShell';

function App() {
  return (
    <SimulationProvider>
      <AppShell>
        <StartPage />
      </AppShell>
    </SimulationProvider>
  );
}
```

### With Navigation (Future - STEP 12)

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <SimulationProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<StartPage />} />
          <Route path="/simulation" element={<SimulationPage />} />
          <Route path="/summary" element={<SummaryPage />} />
        </Routes>
      </BrowserRouter>
    </SimulationProvider>
  );
}
```

### Accessing Session State

```typescript
import { useSimulation } from './hooks/useSimulation';

function MyComponent() {
  const { state } = useSimulation();

  if (state.isActive) {
    return <p>Session active: {state.sessionId}</p>;
  }

  return <StartPage />;
}
```

---

## Next Steps

Ready to proceed to **STEP 7: Patient Card & EHR Viewer** with:
- `patient/PatientCard.tsx` - Patient overview with demographics and state
- `ehr/EHRViewer.tsx` - Main EHR container with tabs/sections
- `ehr/ClinicalNotesList.tsx` & `ClinicalNoteCard.tsx` - Clinical notes display
- `ehr/InvestigationsList.tsx` & `InvestigationCard.tsx` - Investigation results
- `ehr/PatientSummary.tsx` - Allergies, diagnoses, medications
- Progressive revelation indicators
- EHR polling for new investigation results

---

## Screenshots (Text Description)

### Scenario Selection View
- Header: "Medical On-Call Simulation" with clock showing "--:--"
- Subheader: "Select a scenario to begin your simulation"
- Grid of 3 scenario cards:
  - Card 1: "Simple Test EHR" with Easy badge (green)
  - Card 2: "Sepsis Recognition" with Medium badge (orange)
  - Card 3: "Multi-Patient Ward" with Hard badge (red)
- Each card has Start Session button (blue)

### Session Started View
- Success card with green checkmark icon
- "Session Started!" heading
- "Your simulation session is now active. The clock is running."
- Session details: ID, Scenario ID, Current Patient
- Clock in header now shows real time (e.g., "08:30")

### Loading View
- Large spinning loader in center
- Text: "Loading scenarios..."

### Error View
- Red error card
- "Failed to load scenarios. Please try again."
- Retry button

---

**STEP 6 Status**: ✅ **COMPLETE**

**Lines of Code**: 237 lines net change
- `StartPage.tsx`: 218 lines (new)
- `App.tsx`: 19 lines (simplified from 189 lines, -170 lines)

**Files Created**: 1 file (StartPage.tsx)
**Files Updated**: 1 file (App.tsx)

**Build Status**: ✅ Successful (250.90 kB JS, 15.72 kB CSS)
**TypeScript**: ✅ All type checks passing
**API Integration**: ✅ `listScenarios()` and `startSession()` working

**Key Features Delivered**:
- ✅ Scenario list loading from backend API
- ✅ Responsive scenario cards with all details
- ✅ Color-coded difficulty badges
- ✅ Session start functionality
- ✅ Success state with session details
- ✅ Error handling and retry mechanism
- ✅ Loading states with spinners
- ✅ Clock integration (starts after session)
- ✅ Clean, production-ready UI
