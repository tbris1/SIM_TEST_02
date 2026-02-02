/**
 * TypeScript types for simulation state management.
 * Defines the global state shape and reducer action types.
 */

import type {
  ClockState,
  PatientDetailsResponse,
  EHRRecordResponse,
  NurseMessageResponse,
} from '../api/types';

// ============================================================================
// Notification Types
// ============================================================================

/**
 * Severity levels for notifications
 */
export type NotificationSeverity = 'info' | 'warning' | 'error' | 'success';

/**
 * Notification object for displaying alerts to the user
 */
export interface Notification {
  id: string;
  message: string;
  severity: NotificationSeverity;
  timestamp: string;
  isRead: boolean;
}

// ============================================================================
// Nurse Chat Types
// ============================================================================

/**
 * Individual chat message
 */
export interface ChatMessage {
  id: string;
  content: string;
  sender: 'doctor' | 'nurse';
  timestamp: string;
  timeCost?: number; // Time cost in minutes if applicable
}

// ============================================================================
// Simulation State
// ============================================================================

/**
 * Global simulation state
 */
export interface SimulationState {
  // Session metadata
  sessionId: string | null;
  scenarioId: string | null;
  isActive: boolean;
  isComplete: boolean;

  // Clock state
  clock: ClockState | null;

  // Current patient data
  currentPatient: PatientDetailsResponse | null;
  currentPatientEHR: EHRRecordResponse | null;

  // Notifications and alerts
  notifications: Notification[];

  // Nurse conversation history
  nurseConversation: ChatMessage[];

  // Loading and error states
  isLoading: boolean;
  error: string | null;
}

// ============================================================================
// Reducer Action Types
// ============================================================================

/**
 * All possible actions for the simulation reducer
 */
export type SimulationAction =
  // Session lifecycle
  | { type: 'SESSION_START_REQUEST' }
  | {
      type: 'SESSION_START_SUCCESS';
      payload: {
        sessionId: string;
        scenarioId: string;
        clock: ClockState;
        patient: PatientDetailsResponse;
        ehr: EHRRecordResponse;
      };
    }
  | { type: 'SESSION_START_FAILURE'; payload: { error: string } }
  // Session state refresh (polling)
  | {
      type: 'SESSION_STATE_UPDATED';
      payload: {
        clock: ClockState;
        patient: PatientDetailsResponse;
      };
    }
  // Patient EHR updates
  | {
      type: 'PATIENT_EHR_UPDATED';
      payload: {
        ehr: EHRRecordResponse;
      };
    }
  // Action execution
  | { type: 'ACTION_EXECUTE_REQUEST' }
  | {
      type: 'ACTION_EXECUTE_SUCCESS';
      payload: {
        message: string;
      };
    }
  | { type: 'ACTION_EXECUTE_FAILURE'; payload: { error: string } }
  // Nurse chat
  | {
      type: 'NURSE_MESSAGE_SENT';
      payload: {
        message: ChatMessage;
      };
    }
  | {
      type: 'NURSE_MESSAGE_RECEIVED';
      payload: {
        response: NurseMessageResponse;
      };
    }
  // Notifications
  | {
      type: 'NOTIFICATION_ADD';
      payload: {
        notification: Notification;
      };
    }
  | {
      type: 'NOTIFICATION_MARK_READ';
      payload: {
        notificationId: string;
      };
    }
  | { type: 'NOTIFICATION_CLEAR_ALL' }
  // Session completion
  | { type: 'SESSION_COMPLETE_REQUEST' }
  | { type: 'SESSION_COMPLETE_SUCCESS' }
  | { type: 'SESSION_COMPLETE_FAILURE'; payload: { error: string } }
  // General state management
  | { type: 'SET_LOADING'; payload: { isLoading: boolean } }
  | { type: 'SET_ERROR'; payload: { error: string | null } }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESET_STATE' };

// ============================================================================
// Initial State
// ============================================================================

/**
 * Initial state for the simulation reducer
 */
export const initialSimulationState: SimulationState = {
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
