/**
 * TypeScript types for the Medical On-Call Simulation API.
 * These types match the backend Pydantic models and API responses.
 */

// ============================================================================
// Enums (as const objects for better compatibility)
// ============================================================================

/**
 * Patient clinical states
 */
export const PatientState = {
  STABLE: 'stable',
  STABLE_WITH_CONCERNS: 'stable_with_concerns',
  DETERIORATING: 'deteriorating',
  CRITICALLY_UNWELL: 'critically_unwell',
} as const;

export type PatientState = (typeof PatientState)[keyof typeof PatientState];

/**
 * Types of clinical notes
 */
export const NoteType = {
  ADMISSION: 'admission',
  PROGRESS: 'progress',
  CONSULTANT_REVIEW: 'consultant_review',
  DISCHARGE_SUMMARY: 'discharge_summary',
  INVESTIGATION_RESULT: 'investigation_result',
  PROCEDURE_NOTE: 'procedure_note',
  NURSING_NOTE: 'nursing_note',
} as const;

export type NoteType = (typeof NoteType)[keyof typeof NoteType];

/**
 * Visibility conditions for EHR data
 */
export const VisibilityCondition = {
  ALWAYS: 'always',
  TIME_ELAPSED: 'time_elapsed',
  ACTION_TAKEN: 'action_taken',
  REVIEW_IN_PERSON: 'review_in_person',
  INVESTIGATION_ORDERED: 'investigation_ordered',
  EHR_REVIEWED: 'ehr_reviewed',
} as const;

export type VisibilityCondition = (typeof VisibilityCondition)[keyof typeof VisibilityCondition];

// ============================================================================
// Session Types
// ============================================================================

/**
 * Request to start a new simulation session
 */
export interface StartSessionRequest {
  scenario_id: string;
  custom_start_time?: string; // ISO format
}

/**
 * Basic session information response
 */
export interface SessionResponse {
  session_id: string;
  scenario_id: string;
  is_complete: boolean;
  created_at: string; // ISO format
  current_time: string; // ISO format
  elapsed_minutes: number;
}

/**
 * Clock state within a session
 */
export interface ClockState {
  current_time: string; // ISO format
  elapsed_minutes: number;
  artificial_time_added_minutes: number;
}

/**
 * Detailed session state
 */
export interface SessionStateResponse {
  session_id: string;
  scenario_id: string;
  clock: ClockState;
  scheduler: Record<string, any>;
  patients: Record<string, any>;
  action_count: number;
  notification_count: number;
  is_complete: boolean;
}

/**
 * Scenario list item
 */
export interface ScenarioListItem {
  scenario_id: string;
  title: string;
  description: string;
  difficulty: string;
  estimated_duration_minutes: number;
  patient_count: number;
}

/**
 * State change history entry
 */
export interface StateChange {
  timestamp: string; // ISO format
  old_state: PatientState;
  new_state: PatientState;
  trigger: string;
  clinical_notes: string;
}

/**
 * Patient details response
 */
export interface PatientDetailsResponse {
  patient_id: string;
  name: string;
  mrn: string;
  age: number;
  gender: string;
  ward: string;
  bed: string;
  current_state: PatientState;
  actions_taken: Array<Record<string, any>>;
  state_history: StateChange[];
}

/**
 * Session timeline entry
 */
export interface TimelineEntry {
  timestamp: string; // ISO format
  event_type: string;
  patient_id?: string;
  description: string;
  data?: Record<string, any>;
}

/**
 * Session timeline response
 */
export interface SessionTimelineResponse {
  session_id: string;
  timeline: TimelineEntry[];
}

/**
 * Session list response
 */
export interface SessionListResponse {
  sessions: SessionResponse[];
  count: number;
}

// ============================================================================
// Action Types
// ============================================================================

/**
 * Request to execute a user action
 */
export interface ExecuteActionRequest {
  action_type: string;
  patient_id: string;
  details?: Record<string, any>;
  time_cost_minutes?: number;
}

/**
 * Response from executing an action
 */
export interface ExecuteActionResponse {
  success: boolean;
  action_type: string;
  patient_id: string;
  time_advanced_minutes: number;
  new_simulation_time: string; // ISO format
  message: string;
  triggered_events: Array<Record<string, any>>;
  new_notifications: string[];
  patient_state_changes: Array<Record<string, any>>;
}

/**
 * Request to send a message to the nurse
 */
export interface NurseMessageRequest {
  patient_id: string;
  message: string;
  conversation_history?: Array<{
    role: 'nurse' | 'doctor';
    content: string;
  }>;
}

/**
 * Response from nurse message
 */
export interface NurseMessageResponse {
  success: boolean;
  nurse_response: string;
  time_cost_minutes: number;
}

// ============================================================================
// EHR Types
// ============================================================================

/**
 * Visibility rule for EHR data
 */
export interface VisibilityRule {
  rule_id: string;
  condition: VisibilityCondition;
  visible_after_time?: string; // ISO format
  required_action?: string;
  patient_id?: string;
}

/**
 * Clinical note in EHR
 */
export interface ClinicalNote {
  note_id: string;
  note_type: NoteType;
  timestamp: string; // ISO format
  author: string;
  author_role: string;
  title: string;
  content: Record<string, any>;
  visibility_rule?: VisibilityRule;
  is_visible: boolean;
}

/**
 * Investigation result in EHR
 */
export interface InvestigationResult {
  result_id: string;
  investigation_type: string;
  requested_time: string; // ISO format
  resulted_time?: string; // ISO format
  result_data: Record<string, any>;
  interpretation?: string;
  abnormal_flags: string[];
  visibility_rule?: VisibilityRule;
  is_visible: boolean;
}

/**
 * Medication entry
 */
export interface Medication {
  name: string;
  dose: string;
}

/**
 * Patient EHR record view
 */
export interface EHRRecordResponse {
  patient_id: string;
  mrn: string;
  name: string;
  age: number;
  gender: string;
  allergies: string[];
  active_diagnoses: string[];
  current_medications: Medication[];
  visible_notes: ClinicalNote[];
  visible_results: InvestigationResult[];
  total_notes: number;
  total_results: number;
  last_updated: string; // ISO format
}

/**
 * Visibility summary response
 */
export interface VisibilitySummaryResponse {
  patient_id: string;
  notes: {
    visible: number;
    hidden: number;
    total: number;
  };
  results: {
    visible: number;
    hidden: number;
    total: number;
  };
}

/**
 * Request to order an investigation
 */
export interface OrderInvestigationRequest {
  investigation_type: string;
  urgency?: string; // 'routine' | 'urgent' | 'emergency'
  custom_turnaround_minutes?: number;
}

/**
 * Response from ordering an investigation
 */
export interface OrderInvestigationResponse {
  message: string;
  result_id: string;
  investigation_type: string;
  requested_time: string; // ISO format
  expected_result_time: string; // ISO format
  turnaround_minutes: number;
}

/**
 * Request to add a clinical note
 */
export interface AddClinicalNoteRequest {
  note_type: NoteType;
  timestamp: string; // ISO format
  author: string;
  author_role: string;
  title: string;
  content: Record<string, any>;
  visibility_condition?: VisibilityCondition;
  required_action?: string;
  visible_after_time?: string; // ISO format
}

/**
 * Request to add an investigation result
 */
export interface AddInvestigationResultRequest {
  investigation_type: string;
  requested_time: string; // ISO format
  resulted_time: string; // ISO format
  result_data: Record<string, any>;
  interpretation?: string;
  abnormal_flags?: string[];
  visibility_condition?: VisibilityCondition;
  visible_after_time?: string; // ISO format
}

// ============================================================================
// Error Types
// ============================================================================

/**
 * API error response
 */
export interface APIError {
  detail: string;
  status?: number;
}
