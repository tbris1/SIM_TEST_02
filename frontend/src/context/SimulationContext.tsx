/**
 * SimulationContext: Global state management for the simulation.
 * Uses React Context + useReducer for state management.
 */

import { createContext, useContext, useReducer, type ReactNode } from 'react';
import type {
  SimulationState,
  SimulationAction,
  ChatMessage,
  Notification,
} from '../types/simulation';

// ============================================================================
// Initial State
// ============================================================================

const initialState: SimulationState = {
  sessionId: null,
  scenarioId: null,
  isActive: false,
  isComplete: false,
  clock: null,
  currentPatient: null,
  currentPatientEHR: null,
  notifications: [],
  nurseConversation: [],
  isLoading: false,
  error: null,
};

// ============================================================================
// Reducer Function
// ============================================================================

/**
 * Simulation state reducer
 */
function simulationReducer(
  state: SimulationState,
  action: SimulationAction
): SimulationState {
  switch (action.type) {
    // Session start
    case 'SESSION_START_REQUEST':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'SESSION_START_SUCCESS':
      return {
        ...state,
        sessionId: action.payload.sessionId,
        scenarioId: action.payload.scenarioId,
        isActive: true,
        isComplete: false,
        clock: action.payload.clock,
        currentPatient: action.payload.patient,
        currentPatientEHR: action.payload.ehr,
        isLoading: false,
        error: null,
      };

    case 'SESSION_START_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload.error,
      };

    // Session state refresh (from polling)
    case 'SESSION_STATE_UPDATED':
      return {
        ...state,
        clock: action.payload.clock,
        currentPatient: action.payload.patient,
      };

    // Patient EHR updates
    case 'PATIENT_EHR_UPDATED':
      return {
        ...state,
        currentPatientEHR: action.payload.ehr,
      };

    // Action execution
    case 'ACTION_EXECUTE_REQUEST':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'ACTION_EXECUTE_SUCCESS': {
      const notification: Notification = {
        id: `notification-${Date.now()}`,
        message: action.payload.message,
        severity: 'success',
        timestamp: new Date().toISOString(),
        isRead: false,
      };

      return {
        ...state,
        notifications: [...state.notifications, notification],
        isLoading: false,
        error: null,
      };
    }

    case 'ACTION_EXECUTE_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload.error,
      };

    // Nurse chat
    case 'NURSE_MESSAGE_SENT': {
      return {
        ...state,
        nurseConversation: [...state.nurseConversation, action.payload.message],
      };
    }

    case 'NURSE_MESSAGE_RECEIVED': {
      const nurseMessage: ChatMessage = {
        id: `nurse-${Date.now()}`,
        content: action.payload.response.nurse_response,
        sender: 'nurse',
        timestamp: new Date().toISOString(),
        timeCost: action.payload.response.time_cost_minutes,
      };

      return {
        ...state,
        nurseConversation: [...state.nurseConversation, nurseMessage],
      };
    }

    // Notifications
    case 'NOTIFICATION_ADD':
      return {
        ...state,
        notifications: [...state.notifications, action.payload.notification],
      };

    case 'NOTIFICATION_MARK_READ':
      return {
        ...state,
        notifications: state.notifications.map((n) =>
          n.id === action.payload.notificationId ? { ...n, isRead: true } : n
        ),
      };

    case 'NOTIFICATION_CLEAR_ALL':
      return {
        ...state,
        notifications: [],
      };

    // Session completion
    case 'SESSION_COMPLETE_REQUEST':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'SESSION_COMPLETE_SUCCESS':
      return {
        ...state,
        isActive: false,
        isComplete: true,
        isLoading: false,
        error: null,
      };

    case 'SESSION_COMPLETE_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload.error,
      };

    // General state management
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload.isLoading,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload.error,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
}

// ============================================================================
// Context Creation
// ============================================================================

interface SimulationContextValue {
  state: SimulationState;
  dispatch: React.Dispatch<SimulationAction>;
}

const SimulationContext = createContext<SimulationContextValue | undefined>(
  undefined
);

// ============================================================================
// Provider Component
// ============================================================================

interface SimulationProviderProps {
  children: ReactNode;
}

/**
 * SimulationProvider: Wraps the app and provides simulation state
 */
export function SimulationProvider({ children }: SimulationProviderProps) {
  const [state, dispatch] = useReducer(simulationReducer, initialState);

  return (
    <SimulationContext.Provider value={{ state, dispatch }}>
      {children}
    </SimulationContext.Provider>
  );
}

// ============================================================================
// Context Hook
// ============================================================================

/**
 * useSimulationContext: Access simulation state and dispatch
 * Must be used within SimulationProvider
 */
export function useSimulationContext() {
  const context = useContext(SimulationContext);
  if (context === undefined) {
    throw new Error(
      'useSimulationContext must be used within a SimulationProvider'
    );
  }
  return context;
}
