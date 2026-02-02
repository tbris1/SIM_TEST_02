/**
 * API endpoints for executing simulation actions.
 * Includes review patient, escalate, order investigations, document notes, and nurse chat.
 */

import { apiClient } from './client';
import type {
  ExecuteActionRequest,
  ExecuteActionResponse,
  NurseMessageRequest,
  NurseMessageResponse,
} from './types';

/**
 * Execute a generic user action
 */
export const executeAction = async (
  sessionId: string,
  request: ExecuteActionRequest
): Promise<ExecuteActionResponse> => {
  const response = await apiClient.post<ExecuteActionResponse>(
    `/sessions/${sessionId}/actions`,
    request
  );
  return response.data;
};

/**
 * Review a patient in person (adds artificial time)
 */
export const reviewPatientInPerson = async (
  sessionId: string,
  patientId: string,
  location?: string,
  timeCostMinutes: number = 30
): Promise<ExecuteActionResponse> => {
  const params = new URLSearchParams({
    patient_id: patientId,
    time_cost_minutes: timeCostMinutes.toString(),
  });

  if (location) {
    params.append('location', location);
  }

  const response = await apiClient.post<ExecuteActionResponse>(
    `/sessions/${sessionId}/actions/review?${params.toString()}`
  );
  return response.data;
};

/**
 * Escalate a patient to a senior doctor
 */
export const escalatePatient = async (
  sessionId: string,
  patientId: string,
  escalateTo: string = 'registrar',
  reason: string = '',
  timeCostMinutes: number = 5
): Promise<ExecuteActionResponse> => {
  const params = new URLSearchParams({
    patient_id: patientId,
    escalate_to: escalateTo,
    reason: reason,
    time_cost_minutes: timeCostMinutes.toString(),
  });

  const response = await apiClient.post<ExecuteActionResponse>(
    `/sessions/${sessionId}/actions/escalate?${params.toString()}`
  );
  return response.data;
};

/**
 * Request an investigation for a patient
 */
export const requestInvestigation = async (
  sessionId: string,
  patientId: string,
  investigationType: string,
  urgency: string = 'routine',
  expectedDelayMinutes: number = 30
): Promise<ExecuteActionResponse> => {
  const params = new URLSearchParams({
    patient_id: patientId,
    investigation_type: investigationType,
    urgency: urgency,
    expected_delay_minutes: expectedDelayMinutes.toString(),
  });

  const response = await apiClient.post<ExecuteActionResponse>(
    `/sessions/${sessionId}/actions/investigate?${params.toString()}`
  );
  return response.data;
};

/**
 * Document a clinical note
 */
export const documentClinicalNote = async (
  sessionId: string,
  patientId: string,
  noteContent: string,
  noteType: string = 'review'
): Promise<ExecuteActionResponse> => {
  const params = new URLSearchParams({
    patient_id: patientId,
    note_content: noteContent,
    note_type: noteType,
  });

  const response = await apiClient.post<ExecuteActionResponse>(
    `/sessions/${sessionId}/actions/document?${params.toString()}`
  );
  return response.data;
};

/**
 * Send a message to the nurse and get AI-generated response
 */
export const sendNurseMessage = async (
  sessionId: string,
  request: NurseMessageRequest
): Promise<NurseMessageResponse> => {
  const response = await apiClient.post<NurseMessageResponse>(
    `/sessions/${sessionId}/nurse/message`,
    request
  );
  return response.data;
};
