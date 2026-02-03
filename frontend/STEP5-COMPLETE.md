# STEP 5: Simulation Clock - COMPLETE ✓

**Completion Date**: 2026-02-02

## Summary

Successfully implemented a real-time simulation clock component with automatic polling, time formatting utilities, and configuration constants. The clock displays current simulation time, elapsed time, and artificial time added by in-person reviews, with auto-refresh every 2 seconds during active sessions.

## Files Created

### Utilities (2 files)

#### 1. `src/utils/constants.ts` (19 lines)

**Purpose:** Application-wide configuration constants

**Constants:**
- `API_BASE_URL` - Base URL for API requests (default: http://localhost:8000/api/v1)
  - Reads from `VITE_API_BASE_URL` environment variable
  - Fallback to localhost for development
- `POLL_INTERVAL_MS` - Polling interval for session state updates (2000ms / 2 seconds)
- `EHR_POLL_INTERVAL_MS` - Polling interval for EHR updates (5000ms / 5 seconds)

**Usage:**
```typescript
import { API_BASE_URL, POLL_INTERVAL_MS } from './utils/constants';
```

---

#### 2. `src/utils/formatters.ts` (83 lines)

**Purpose:** Time and date formatting utilities

**Functions:**

1. **`formatTime(isoString: string): string`**
   - Formats ISO datetime to HH:MM (24-hour format)
   - Example: `"2024-01-15T14:30:00"` → `"14:30"`

2. **`formatDateTime(isoString: string): string`**
   - Formats ISO datetime to full date and time
   - Example: `"2024-01-15T14:30:00"` → `"Jan 15, 2024 14:30"`

3. **`formatElapsed(minutes: number): string`**
   - Formats elapsed time in minutes to human-readable format
   - Examples:
     - `150` → `"2h 30m"`
     - `45` → `"45m"`
     - `120` → `"2h"`

4. **`formatDate(isoString: string): string`**
   - Formats date to short format (MMM DD)
   - Example: `"2024-01-15T14:30:00"` → `"Jan 15"`

5. **`timeDifferenceMinutes(startTime: string, endTime: string): number`**
   - Calculates time difference in minutes between two ISO datetime strings
   - Example: `("2024-01-15T14:00:00", "2024-01-15T14:30:00")` → `30`

**Features:**
- Pure functions with no side effects
- Fully typed with TypeScript
- JSDoc comments with examples
- Handles edge cases (e.g., hours with no remaining minutes)

**Usage:**
```typescript
import { formatTime, formatElapsed } from './utils/formatters';

const time = formatTime("2024-01-15T14:30:00"); // "14:30"
const elapsed = formatElapsed(150); // "2h 30m"
```

---

### Components (1 file)

#### 3. `src/components/simulation/SimulationClock.tsx` (77 lines)

**Purpose:** Real-time clock display for active simulation with automatic polling

**Features:**
- **Real-time Updates**: Polls session state every 2 seconds using `usePolling` hook
- **Current Time Display**: Shows simulation time in HH:MM format
- **Elapsed Time**: Displays total elapsed time (e.g., "2h 30m")
- **Artificial Time Indicator**: Highlights artificial time added by in-person reviews (orange text)
- **Session Complete Badge**: Shows green badge when session is complete
- **No Session State**: Displays placeholder when no active session
- **Auto-start/stop Polling**: Only polls when session is active and not complete

**Props:**
```typescript
export interface SimulationClockProps {
  /** Whether to show detailed info (elapsed time, artificial time) */
  showDetails?: boolean;
  /** Custom CSS class */
  className?: string;
}
```

**Layout:**
```
┌─────────────────────┐
│ Simulation Time     │ (gray label)
│     14:30           │ (large bold time)
│                     │
│ Elapsed: 2h 30m     │ (small gray text)
│ Artificial: +30m    │ (small orange text, if > 0)
│                     │
│ [Session Complete]  │ (green badge, if complete)
└─────────────────────┘
```

**Behavior:**
1. When session is active:
   - Polls `refreshSessionState()` every 2 seconds
   - Updates clock display in real-time
   - Shows elapsed time
   - Shows artificial time if > 0
2. When session is complete:
   - Stops polling
   - Shows "Session Complete" badge
3. When no session:
   - Shows "--:--" placeholder
   - No polling

**Integration:**
- Uses `useSimulation()` hook to access session state
- Uses `usePolling()` hook for automatic updates
- Integrated into `AppShell` header via `headerClockSlot` prop

**Styling:**
- Current time: Large (text-2xl), bold, gray-900
- Labels: Small (text-sm), gray-500
- Elapsed time: Extra small (text-xs), gray-600
- Artificial time: Extra small (text-xs), **orange-600** (highlights added time)
- Complete badge: Green background (bg-green-100), green text (text-green-800)
- No session: Gray-400 placeholder

**Usage:**
```typescript
import { SimulationClock } from './components/simulation/SimulationClock';

// In header clock slot
<AppShell
  headerClockSlot={<SimulationClock />}
>
  {/* ... */}
</AppShell>

// Compact version without details
<SimulationClock showDetails={false} />
```

---

### Updated Files

#### 4. `src/App.tsx` (Updated - 194 lines, +5 lines)

**Changes:**
1. Added `SimulationProvider` import from context
2. Added `SimulationClock` import
3. Wrapped entire app in `<SimulationProvider>`
4. Replaced hardcoded clock placeholder with `<SimulationClock />`

**Before:**
```typescript
<AppShell
  headerClockSlot={
    <div className="text-center">
      <p className="text-sm text-gray-500">Simulation Time</p>
      <p className="text-lg font-semibold">08:30 AM</p>
    </div>
  }
>
```

**After:**
```typescript
<SimulationProvider>
  <AppShell
    headerClockSlot={<SimulationClock />}
  >
    {/* ... */}
  </AppShell>
</SimulationProvider>
```

**Effect:**
- Clock now displays real simulation state (when session is active)
- Clock shows "--:--" placeholder when no session is active
- Auto-refreshes every 2 seconds during active sessions
- App now has access to full simulation context

---

## Technical Implementation

### Polling Architecture

**Flow:**
1. `SimulationClock` component mounts
2. `usePolling` hook initializes with:
   - `callback`: `refreshSessionState` (from `useSimulation`)
   - `intervalMs`: 2000 (from `POLL_INTERVAL_MS`)
   - `enabled`: true only when `state.isActive && !state.isComplete`
3. Hook executes callback immediately, then every 2 seconds
4. Each callback updates `SimulationContext` state via reducer
5. Clock component re-renders with updated state
6. When session completes, polling stops automatically

**Advantages:**
- Automatic cleanup on unmount
- Conditional polling based on session state
- No manual interval management
- Efficient: only polls when needed

### Time Formatting Strategy

**Approach:**
- All backend times are ISO 8601 strings (e.g., `"2024-01-15T14:30:00"`)
- Frontend formats for display using pure functions
- No external dependencies (like `date-fns`) for basic formatting
- Custom formatters keep bundle size small

**Rationale:**
- ISO format ensures timezone consistency
- Simple formatting doesn't require heavy libraries
- Custom functions are fast and predictable
- Easy to test and maintain

### State Integration

**SimulationClock** relies on:
1. **`useSimulation()` hook**: Provides `state` and `refreshSessionState()`
2. **`usePolling()` hook**: Manages automatic polling lifecycle
3. **`SimulationContext`**: Global state with `ClockState` data

**Data Flow:**
```
Backend API
    ↓
refreshSessionState() (API call)
    ↓
SimulationContext reducer (ACTION_EXECUTE_SUCCESS)
    ↓
state.clock updated (ClockState)
    ↓
SimulationClock re-renders (new time)
```

---

## Verification

### TypeScript Compilation
✅ **Build Successful**
- All files compile without errors
- No unused imports
- Type-safe formatter functions
- Correct integration with existing types (`ClockState`)

```bash
$ npm run build
✓ built in 759ms
```

### Bundle Size Analysis

**Before STEP 5** (after STEP 4):
- JS: 242.09 kB
- CSS: 15.24 kB

**After STEP 5**:
- JS: 251.84 kB (+9.75 kB / +4.0%)
- CSS: 15.66 kB (+0.42 kB / +2.8%)

**Breakdown:**
- SimulationClock component (~3 kB)
- Formatters utility (~5 kB)
- Constants utility (~1 kB)
- Minor CSS additions (~0.4 kB)

**Assessment:** Reasonable increase for real-time clock functionality

---

## Integration with Previous Steps

### With STEP 2 (API Client):
- Uses `ClockState` type from `src/api/types.ts`
- Ready for `refreshSessionState()` API calls

### With STEP 3 (State Management):
- Integrates with `useSimulation()` hook
- Uses `usePolling()` hook for automatic updates
- Accesses `state.clock`, `state.isActive`, `state.isComplete`
- Calls `refreshSessionState()` for updates

### With STEP 4 (Layout & Components):
- Displays in `Header` component via `clockSlot` prop
- Integrated into `AppShell` layout
- Consistent styling with existing components
- Uses Tailwind CSS classes

### For STEP 6+ (Session Start & Simulation Pages):
- Clock ready to display real session data
- Automatic polling starts when session is active
- Will show live updates during simulation
- Artificial time will highlight in-person reviews

---

## Design Decisions

### 1. Polling vs WebSockets

**Decision:** Use polling with 2-second interval

**Rationale:**
- Simpler implementation (no WebSocket server needed)
- Sufficient for medical simulation use case (not real-time critical)
- Backend already has REST endpoints
- Easy to debug and test
- Lower server complexity

**Trade-offs:**
- Slightly higher network overhead (acceptable for MVP)
- 2-second delay (acceptable for simulation clock)

### 2. Formatter Functions vs date-fns

**Decision:** Custom formatter functions

**Rationale:**
- Only need basic time formatting (HH:MM, elapsed time)
- Keeps bundle size small (~5 kB vs ~70 kB for date-fns)
- No timezone complexity (backend handles all time logic)
- Easy to customize for medical simulation context

**Trade-offs:**
- Less feature-rich than date-fns (acceptable for our needs)

### 3. Artificial Time Highlighting

**Decision:** Show artificial time in orange with "+" prefix

**Rationale:**
- Pedagogical feature: students should see time cost of actions
- Orange color indicates "caution" (time was artificially added)
- "+" prefix makes it clear this is added time, not elapsed time
- Only shown when > 0 (doesn't clutter display when 0)

### 4. Conditional Polling

**Decision:** Only poll when `state.isActive && !state.isComplete`

**Rationale:**
- Efficient: no unnecessary API calls
- Clock stops when session completes (no stale updates)
- Automatic cleanup (no manual interval management)
- Prevents polling before session starts

---

## Testing Strategy

### Manual Testing Checklist

- [ ] **No Session State**
  - Load app without starting session
  - Verify clock shows "--:--" placeholder
  - Confirm "No active session" text displays

- [ ] **Active Session** (when STEP 6+ implemented)
  - Start session from scenario list
  - Verify clock shows current simulation time (HH:MM)
  - Confirm elapsed time displays correctly
  - Watch clock update every 2 seconds

- [ ] **Artificial Time** (when STEP 8 implemented)
  - Perform in-person review action (30 min cost)
  - Verify orange "Artificial: +30m" appears
  - Confirm artificial time accumulates on multiple reviews

- [ ] **Session Complete** (when STEP 11 implemented)
  - Complete session
  - Verify polling stops (no more network requests)
  - Confirm "Session Complete" green badge appears

- [ ] **Formatter Functions**
  - Test `formatTime()` with various times
  - Test `formatElapsed()` with edge cases (0m, 59m, 60m, 150m)
  - Verify no errors with invalid inputs

### Automated Testing (Future)

Suggested test cases for `formatters.ts`:
```typescript
describe('formatTime', () => {
  it('formats morning times', () => {
    expect(formatTime('2024-01-15T08:30:00')).toBe('08:30');
  });

  it('formats afternoon times', () => {
    expect(formatTime('2024-01-15T14:30:00')).toBe('14:30');
  });
});

describe('formatElapsed', () => {
  it('formats minutes only', () => {
    expect(formatElapsed(45)).toBe('45m');
  });

  it('formats hours and minutes', () => {
    expect(formatElapsed(150)).toBe('2h 30m');
  });

  it('formats hours only', () => {
    expect(formatElapsed(120)).toBe('2h');
  });
});
```

---

## File Structure After STEP 5

```
src/
├── api/
│   ├── client.ts
│   ├── types.ts           (ClockState used by SimulationClock)
│   ├── sessions.ts
│   ├── actions.ts
│   └── ehr.ts
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Modal.tsx
│   │   └── LoadingSpinner.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx      (displays SimulationClock)
│   │   └── AppShell.tsx
│   └── simulation/
│       └── SimulationClock.tsx ✨ NEW
├── context/
│   └── SimulationContext.tsx
├── hooks/
│   ├── useSimulation.ts   (provides refreshSessionState)
│   └── usePolling.ts      (used by SimulationClock)
├── types/
│   └── simulation.ts
├── utils/
│   ├── constants.ts       ✨ NEW
│   └── formatters.ts      ✨ NEW
└── App.tsx                (updated with SimulationProvider + SimulationClock)
```

---

## Usage Examples

### Basic Clock Display

```typescript
import { SimulationClock } from './components/simulation/SimulationClock';
import { AppShell } from './components/layout/AppShell';

function App() {
  return (
    <SimulationProvider>
      <AppShell
        headerClockSlot={<SimulationClock />}
      >
        {/* Your content */}
      </AppShell>
    </SimulationProvider>
  );
}
```

### Compact Clock (No Details)

```typescript
// For sidebar or status bar
<SimulationClock showDetails={false} />
```

### Using Formatters Directly

```typescript
import { formatTime, formatElapsed } from './utils/formatters';

const currentTime = formatTime(state.clock.current_time);
// "14:30"

const elapsed = formatElapsed(state.clock.elapsed_minutes);
// "2h 30m"
```

### Constants Usage

```typescript
import { API_BASE_URL, POLL_INTERVAL_MS } from './utils/constants';

// API client
const client = axios.create({
  baseURL: API_BASE_URL,
});

// Custom polling
usePolling({
  callback: fetchData,
  intervalMs: POLL_INTERVAL_MS,
});
```

---

## Next Steps

Ready to proceed to **STEP 6: Session Start Page** with:
- Scenario list display from `GET /api/v1/scenarios`
- Scenario cards with title, description, difficulty, duration
- "Start Session" button
- Navigation to `/simulation` on success
- Integration with `startSession()` from `useSimulation()`
- Clock will start displaying real data once session is active

---

## Known Limitations

1. **No Error Handling in Clock**
   - Clock doesn't display error messages if polling fails
   - Will be addressed in STEP 13 (Error Handling)

2. **No Loading State**
   - Clock doesn't show loading indicator during first refresh
   - Acceptable for MVP (clock updates are fast)

3. **No Timezone Display**
   - Clock shows time in browser's local timezone
   - Backend handles all timezone logic

4. **Hardcoded Polling Interval**
   - 2-second interval is fixed in constants
   - Future: could make configurable per scenario

---

**STEP 5 Status**: ✅ **COMPLETE**

**Lines of Code**: 179 lines (3 new files)
- `constants.ts`: 19 lines
- `formatters.ts`: 83 lines
- `SimulationClock.tsx`: 77 lines

**Files Created**: 3 files (constants, formatters, SimulationClock)
**Files Updated**: 1 file (App.tsx)

**Build Status**: ✅ Successful (251.84 kB JS, 15.66 kB CSS)
**TypeScript**: ✅ All type checks passing
**Integration**: ✅ Fully integrated with STEP 3 state management

**Key Features Delivered**:
- ✅ Real-time clock display with 2-second polling
- ✅ Formatted time display (HH:MM)
- ✅ Elapsed time display (Xh Ym)
- ✅ Artificial time highlighting (orange)
- ✅ Session complete indicator
- ✅ Automatic polling start/stop
- ✅ Placeholder for no active session
- ✅ Time formatting utilities
- ✅ Application constants
