/**
 * Central export point for all API modules.
 * Makes it easy to import API functions and types throughout the app.
 */

// Export all types
export * from './types';

// Export API client
export { apiClient, getErrorMessage, API_URL } from './client';

// Export session endpoints
export {
  listScenarios,
  startSession,
  getSessionState,
  completeSession,
  getSessionTimeline,
  getPatientDetails,
  listSessions,
  deleteSession,
} from './sessions';

// Export action endpoints
export {
  executeAction,
  reviewPatientInPerson,
  escalatePatient,
  requestInvestigation,
  documentClinicalNote,
  sendNurseMessage,
} from './actions';

// Export EHR endpoints
export {
  getPatientEHR,
  getVisibilitySummary,
  orderInvestigation,
  addClinicalNote,
  addInvestigationResult,
} from './ehr';
