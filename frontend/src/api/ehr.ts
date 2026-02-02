/**
 * API endpoints for Electronic Health Record (EHR) access.
 * Handles patient records, clinical notes, investigation results, and progressive revelation.
 */

import { apiClient } from './client';
import type {
  EHRRecordResponse,
  VisibilitySummaryResponse,
  OrderInvestigationRequest,
  OrderInvestigationResponse,
  AddClinicalNoteRequest,
  AddInvestigationResultRequest,
} from './types';

/**
 * Get a patient's EHR record with filtered visibility
 * Only shows clinical notes and investigation results that are currently visible
 */
export const getPatientEHR = async (
  sessionId: string,
  patientId: string
): Promise<EHRRecordResponse> => {
  const response = await apiClient.get<EHRRecordResponse>(
    `/sessions/${sessionId}/patients/${patientId}/ehr`
  );
  return response.data;
};

/**
 * Get visibility statistics for a patient's EHR
 * Shows how many notes and results are visible vs. hidden
 */
export const getVisibilitySummary = async (
  sessionId: string,
  patientId: string
): Promise<VisibilitySummaryResponse> => {
  const response = await apiClient.get<VisibilitySummaryResponse>(
    `/sessions/${sessionId}/patients/${patientId}/ehr/visibility`
  );
  return response.data;
};

/**
 * Order an investigation for a patient
 * The investigation will be processed and results will become available after turnaround time
 */
export const orderInvestigation = async (
  sessionId: string,
  patientId: string,
  request: OrderInvestigationRequest
): Promise<OrderInvestigationResponse> => {
  const response = await apiClient.post<OrderInvestigationResponse>(
    `/sessions/${sessionId}/patients/${patientId}/ehr/investigations/order`,
    request
  );
  return response.data;
};

/**
 * Add a clinical note to a patient's EHR
 * Primarily for testing and scenario setup
 */
export const addClinicalNote = async (
  sessionId: string,
  patientId: string,
  request: AddClinicalNoteRequest
): Promise<{ message: string; note_id: string; is_visible: boolean }> => {
  const response = await apiClient.post<{ message: string; note_id: string; is_visible: boolean }>(
    `/sessions/${sessionId}/patients/${patientId}/ehr/notes`,
    request
  );
  return response.data;
};

/**
 * Add an investigation result to a patient's EHR
 * Primarily for testing and scenario setup
 */
export const addInvestigationResult = async (
  sessionId: string,
  patientId: string,
  request: AddInvestigationResultRequest
): Promise<{ message: string; result_id: string; is_visible: boolean }> => {
  const response = await apiClient.post<{ message: string; result_id: string; is_visible: boolean }>(
    `/sessions/${sessionId}/patients/${patientId}/ehr/results`,
    request
  );
  return response.data;
};
