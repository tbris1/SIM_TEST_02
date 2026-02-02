/**
 * API endpoints for simulation session management.
 * Handles session lifecycle: start, get state, timeline, complete, delete.
 */

import { apiClient } from './client';
import type {
  StartSessionRequest,
  SessionResponse,
  SessionStateResponse,
  SessionListResponse,
  SessionTimelineResponse,
  PatientDetailsResponse,
  ScenarioListItem,
} from './types';

/**
 * List all available scenarios
 */
export const listScenarios = async (): Promise<ScenarioListItem[]> => {
  const response = await apiClient.get<ScenarioListItem[]>('/scenarios');
  return response.data;
};

/**
 * Start a new simulation session from a scenario
 */
export const startSession = async (
  request: StartSessionRequest
): Promise<SessionResponse> => {
  const response = await apiClient.post<SessionResponse>('/sessions/start', request);
  return response.data;
};

/**
 * Get the current state of a simulation session
 */
export const getSessionState = async (sessionId: string): Promise<SessionStateResponse> => {
  const response = await apiClient.get<SessionStateResponse>(`/sessions/${sessionId}`);
  return response.data;
};

/**
 * Complete a session and generate summary
 */
export const completeSession = async (sessionId: string): Promise<any> => {
  const response = await apiClient.post(`/sessions/${sessionId}/complete`);
  return response.data;
};

/**
 * Get chronological timeline of session events
 */
export const getSessionTimeline = async (
  sessionId: string
): Promise<SessionTimelineResponse> => {
  const response = await apiClient.get<SessionTimelineResponse>(
    `/sessions/${sessionId}/timeline`
  );
  return response.data;
};

/**
 * Get detailed information about a specific patient in a session
 */
export const getPatientDetails = async (
  sessionId: string,
  patientId: string
): Promise<PatientDetailsResponse> => {
  const response = await apiClient.get<PatientDetailsResponse>(
    `/sessions/${sessionId}/patients/${patientId}`
  );
  return response.data;
};

/**
 * List all active simulation sessions
 */
export const listSessions = async (): Promise<SessionListResponse> => {
  const response = await apiClient.get<SessionListResponse>('/sessions');
  return response.data;
};

/**
 * Delete a simulation session
 */
export const deleteSession = async (sessionId: string): Promise<{ session_id: string; deleted: boolean }> => {
  const response = await apiClient.delete<{ session_id: string; deleted: boolean }>(
    `/sessions/${sessionId}`
  );
  return response.data;
};
