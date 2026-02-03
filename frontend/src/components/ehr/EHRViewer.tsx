/**
 * EHRViewer: Main EHR container with progressive revelation
 * Displays patient summary, clinical notes, and investigation results
 * Automatically polls for new data every 5 seconds
 */

import { useSimulation } from '../../hooks/useSimulation';
import { usePolling } from '../../hooks/usePolling';
import { PatientSummary } from './PatientSummary';
import { ClinicalNotesList } from './ClinicalNotesList';
import { InvestigationsList } from './InvestigationsList';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { EHR_POLL_INTERVAL_MS } from '../../utils/constants';

export interface EHRViewerProps {
  className?: string;
}

export function EHRViewer({ className = '' }: EHRViewerProps) {
  const { state, refreshEHR } = useSimulation();

  // Poll for EHR updates every 5 seconds (to catch new investigation results)
  usePolling({
    callback: async () => {
      if (state.currentPatient) {
        await refreshEHR(state.currentPatient.patient_id);
      }
    },
    intervalMs: EHR_POLL_INTERVAL_MS,
    enabled: state.isActive && !state.isComplete && !!state.currentPatient,
  });

  // Loading state
  if (state.isLoading && !state.currentPatientEHR) {
    return (
      <div className={`flex justify-center py-12 ${className}`}>
        <LoadingSpinner size="lg" text="Loading EHR..." />
      </div>
    );
  }

  // No EHR data
  if (!state.currentPatientEHR) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <p className="text-gray-500">No patient EHR available</p>
      </div>
    );
  }

  const {
    allergies,
    active_diagnoses,
    current_medications,
    visible_notes,
    visible_results,
    total_notes,
    total_results,
  } = state.currentPatientEHR;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Patient Summary (Always Visible) */}
      <PatientSummary
        allergies={allergies}
        diagnoses={active_diagnoses}
        medications={current_medications}
      />

      {/* Progressive Revelation Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">
          EHR Visibility Status
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-blue-800">Clinical Notes:</span>
            <span className="ml-2 font-semibold text-blue-900">
              {visible_notes.length} of {total_notes} visible
            </span>
            {total_notes > visible_notes.length && (
              <span className="ml-2 text-orange-600">
                ({total_notes - visible_notes.length} hidden)
              </span>
            )}
          </div>
          <div>
            <span className="text-blue-800">Investigation Results:</span>
            <span className="ml-2 font-semibold text-blue-900">
              {visible_results.length} of {total_results} visible
            </span>
            {total_results > visible_results.length && (
              <span className="ml-2 text-orange-600">
                ({total_results - visible_results.length} hidden)
              </span>
            )}
          </div>
        </div>
        <p className="text-xs text-blue-700 mt-2">
          Additional clinical information will be revealed as you review the patient
          and take actions.
        </p>
      </div>

      {/* Clinical Notes */}
      <ClinicalNotesList notes={visible_notes} totalNotes={total_notes} />

      {/* Investigation Results */}
      <InvestigationsList results={visible_results} totalResults={total_results} />
    </div>
  );
}
