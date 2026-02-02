/**
 * useSimulation: Custom hook for simulation actions.
 * Provides methods to interact with the simulation (start session, execute actions, etc.)
 */

import { useCallback } from 'react';
import { useSimulationContext } from '../context/SimulationContext';
import {
  startSession as apiStartSession,
  getSessionState,
  completeSession as apiCompleteSession,
  getPatientDetails,
} from '../api/sessions';
import {
  reviewPatientInPerson,
  escalatePatient as apiEscalatePatient,
  requestInvestigation as apiRequestInvestigation,
  documentClinicalNote as apiDocumentClinicalNote,
  sendNurseMessage as apiSendNurseMessage,
} from '../api/actions';
import {
  getPatientEHR,
  orderInvestigation as apiOrderInvestigation,
} from '../api/ehr';
import { getErrorMessage } from '../api/client';
import type { ChatMessage, Notification } from '../types/simulation';

/**
 * Hook return type
 */
export interface UseSimulationReturn {
  // State
  state: ReturnType<typeof useSimulationContext>['state'];

  // Session lifecycle actions
  startSession: (scenarioId: string) => Promise<void>;
  refreshSessionState: () => Promise<void>;
  completeSession: () => Promise<void>;

  // Patient actions
  reviewPatient: (
    patientId: string,
    location?: string,
    timeCostMinutes?: number
  ) => Promise<void>;
  escalatePatient: (
    patientId: string,
    escalateTo?: string,
    reason?: string,
    timeCostMinutes?: number
  ) => Promise<void>;

  // Investigation actions
  requestInvestigation: (
    patientId: string,
    investigationType: string,
    urgency?: string,
    expectedDelayMinutes?: number
  ) => Promise<void>;
  orderInvestigation: (
    patientId: string,
    investigationType: string,
    urgency?: string,
    expectedTurnaroundMinutes?: number
  ) => Promise<void>;

  // Documentation actions
  documentNote: (
    patientId: string,
    noteContent: string,
    noteType?: string
  ) => Promise<void>;

  // Nurse chat
  sendNurseMessage: (patientId: string, message: string) => Promise<void>;

  // EHR refresh
  refreshEHR: (patientId: string) => Promise<void>;

  // Notification actions
  addNotification: (
    message: string,
    severity?: 'info' | 'warning' | 'error' | 'success'
  ) => void;
  markNotificationRead: (notificationId: string) => void;
  clearAllNotifications: () => void;

  // Utility actions
  clearError: () => void;
  resetState: () => void;
}

/**
 * Custom hook for simulation management
 */
export function useSimulation(): UseSimulationReturn {
  const { state, dispatch } = useSimulationContext();

  // ========================================================================
  // Session lifecycle actions
  // ========================================================================

  const startSession = useCallback(
    async (scenarioId: string) => {
      try {
        dispatch({ type: 'SESSION_START_REQUEST' });

        // Start the session
        const sessionResponse = await apiStartSession({ scenario_id: scenarioId });

        // Get the session state with clock
        const sessionState = await getSessionState(sessionResponse.session_id);

        // Get the first patient (assumes single patient for MVP)
        const patientIds = Object.keys(sessionState.patients);
        if (patientIds.length === 0) {
          throw new Error('No patients found in session');
        }
        const firstPatientId = patientIds[0];

        // Get patient details and EHR
        const [patientDetails, patientEHR] = await Promise.all([
          getPatientDetails(sessionResponse.session_id, firstPatientId),
          getPatientEHR(sessionResponse.session_id, firstPatientId),
        ]);

        dispatch({
          type: 'SESSION_START_SUCCESS',
          payload: {
            sessionId: sessionResponse.session_id,
            scenarioId: sessionResponse.scenario_id,
            clock: sessionState.clock,
            patient: patientDetails,
            ehr: patientEHR,
          },
        });
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'SESSION_START_FAILURE',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [dispatch]
  );

  const refreshSessionState = useCallback(async () => {
    if (!state.sessionId || !state.currentPatient) return;

    try {
      const sessionState = await getSessionState(state.sessionId);
      const patientDetails = await getPatientDetails(
        state.sessionId,
        state.currentPatient.patient_id
      );

      dispatch({
        type: 'SESSION_STATE_UPDATED',
        payload: {
          clock: sessionState.clock,
          patient: patientDetails,
        },
      });
    } catch (error) {
      console.error('Failed to refresh session state:', error);
    }
  }, [state.sessionId, state.currentPatient, dispatch]);

  const completeSession = useCallback(async () => {
    if (!state.sessionId) return;

    try {
      dispatch({ type: 'SESSION_COMPLETE_REQUEST' });
      await apiCompleteSession(state.sessionId);
      dispatch({ type: 'SESSION_COMPLETE_SUCCESS' });
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: 'SESSION_COMPLETE_FAILURE',
        payload: { error: errorMessage },
      });
      throw error;
    }
  }, [state.sessionId, dispatch]);

  // ========================================================================
  // Patient actions
  // ========================================================================

  const reviewPatient = useCallback(
    async (
      patientId: string,
      location?: string,
      timeCostMinutes: number = 30
    ) => {
      if (!state.sessionId) return;

      try {
        dispatch({ type: 'ACTION_EXECUTE_REQUEST' });

        const response = await reviewPatientInPerson(
          state.sessionId,
          patientId,
          location,
          timeCostMinutes
        );

        dispatch({
          type: 'ACTION_EXECUTE_SUCCESS',
          payload: {
            message: response.message,
          },
        });

        // Refresh patient data and EHR after action
        await refreshSessionState();
        await refreshEHR(patientId);
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'ACTION_EXECUTE_FAILURE',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [state.sessionId, dispatch]
  );

  const escalatePatient = useCallback(
    async (
      patientId: string,
      escalateTo: string = 'registrar',
      reason: string = '',
      timeCostMinutes: number = 5
    ) => {
      if (!state.sessionId) return;

      try {
        dispatch({ type: 'ACTION_EXECUTE_REQUEST' });

        const response = await apiEscalatePatient(
          state.sessionId,
          patientId,
          escalateTo,
          reason,
          timeCostMinutes
        );

        dispatch({
          type: 'ACTION_EXECUTE_SUCCESS',
          payload: {
            message: response.message,
          },
        });

        await refreshSessionState();
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'ACTION_EXECUTE_FAILURE',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [state.sessionId, dispatch]
  );

  // ========================================================================
  // Investigation actions
  // ========================================================================

  const requestInvestigation = useCallback(
    async (
      patientId: string,
      investigationType: string,
      urgency: string = 'routine',
      expectedDelayMinutes: number = 30
    ) => {
      if (!state.sessionId) return;

      try {
        dispatch({ type: 'ACTION_EXECUTE_REQUEST' });

        const response = await apiRequestInvestigation(
          state.sessionId,
          patientId,
          investigationType,
          urgency,
          expectedDelayMinutes
        );

        dispatch({
          type: 'ACTION_EXECUTE_SUCCESS',
          payload: {
            message: response.message,
          },
        });

        await refreshSessionState();
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'ACTION_EXECUTE_FAILURE',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [state.sessionId, dispatch]
  );

  const orderInvestigation = useCallback(
    async (
      patientId: string,
      investigationType: string,
      urgency: string = 'routine',
      expectedTurnaroundMinutes: number = 30
    ) => {
      if (!state.sessionId) return;

      try {
        dispatch({ type: 'ACTION_EXECUTE_REQUEST' });

        const response = await apiOrderInvestigation(state.sessionId, patientId, {
          investigation_type: investigationType,
          urgency,
          custom_turnaround_minutes: expectedTurnaroundMinutes,
        });

        dispatch({
          type: 'ACTION_EXECUTE_SUCCESS',
          payload: {
            message: response.message,
          },
        });

        await refreshSessionState();
        await refreshEHR(patientId);
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'ACTION_EXECUTE_FAILURE',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [state.sessionId, dispatch]
  );

  // ========================================================================
  // Documentation actions
  // ========================================================================

  const documentNote = useCallback(
    async (
      patientId: string,
      noteContent: string,
      noteType: string = 'review'
    ) => {
      if (!state.sessionId) return;

      try {
        dispatch({ type: 'ACTION_EXECUTE_REQUEST' });

        const response = await apiDocumentClinicalNote(
          state.sessionId,
          patientId,
          noteContent,
          noteType
        );

        dispatch({
          type: 'ACTION_EXECUTE_SUCCESS',
          payload: {
            message: response.message,
          },
        });

        await refreshEHR(patientId);
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'ACTION_EXECUTE_FAILURE',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [state.sessionId, dispatch]
  );

  // ========================================================================
  // Nurse chat
  // ========================================================================

  const sendNurseMessage = useCallback(
    async (patientId: string, message: string) => {
      if (!state.sessionId) return;

      try {
        // Add doctor's message to conversation immediately
        const doctorMessage: ChatMessage = {
          id: `doctor-${Date.now()}`,
          content: message,
          sender: 'doctor',
          timestamp: new Date().toISOString(),
        };

        dispatch({
          type: 'NURSE_MESSAGE_SENT',
          payload: { message: doctorMessage },
        });

        // Send to API and get nurse response
        const response = await apiSendNurseMessage(state.sessionId, {
          patient_id: patientId,
          message,
        });

        dispatch({
          type: 'NURSE_MESSAGE_RECEIVED',
          payload: { response },
        });
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        dispatch({
          type: 'SET_ERROR',
          payload: { error: errorMessage },
        });
        throw error;
      }
    },
    [state.sessionId, dispatch]
  );

  // ========================================================================
  // EHR refresh
  // ========================================================================

  const refreshEHR = useCallback(
    async (patientId: string) => {
      if (!state.sessionId) return;

      try {
        const ehr = await getPatientEHR(state.sessionId, patientId);
        dispatch({
          type: 'PATIENT_EHR_UPDATED',
          payload: { ehr },
        });
      } catch (error) {
        console.error('Failed to refresh EHR:', error);
      }
    },
    [state.sessionId, dispatch]
  );

  // ========================================================================
  // Notification actions
  // ========================================================================

  const addNotification = useCallback(
    (
      message: string,
      severity: 'info' | 'warning' | 'error' | 'success' = 'info'
    ) => {
      const notification: Notification = {
        id: `notification-${Date.now()}`,
        message,
        severity,
        timestamp: new Date().toISOString(),
        isRead: false,
      };

      dispatch({
        type: 'NOTIFICATION_ADD',
        payload: { notification },
      });
    },
    [dispatch]
  );

  const markNotificationRead = useCallback(
    (notificationId: string) => {
      dispatch({
        type: 'NOTIFICATION_MARK_READ',
        payload: { notificationId },
      });
    },
    [dispatch]
  );

  const clearAllNotifications = useCallback(() => {
    dispatch({ type: 'NOTIFICATION_CLEAR_ALL' });
  }, [dispatch]);

  // ========================================================================
  // Utility actions
  // ========================================================================

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, [dispatch]);

  const resetState = useCallback(() => {
    dispatch({ type: 'RESET_STATE' });
  }, [dispatch]);

  // ========================================================================
  // Return
  // ========================================================================

  return {
    state,
    startSession,
    refreshSessionState,
    completeSession,
    reviewPatient,
    escalatePatient,
    requestInvestigation,
    orderInvestigation,
    documentNote,
    sendNurseMessage,
    refreshEHR,
    addNotification,
    markNotificationRead,
    clearAllNotifications,
    clearError,
    resetState,
  };
}
