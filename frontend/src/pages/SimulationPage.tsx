/**
 * SimulationPage: Main simulation interface
 * Displays patient card, EHR viewer, and action panel during active simulation
 */

import { useSimulation } from '../hooks/useSimulation';
import { PatientCard } from '../components/patient/PatientCard';
import { EHRViewer } from '../components/ehr/EHRViewer';
import { ActionPanel } from '../components/actions/ActionPanel';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function SimulationPage() {
  const { state } = useSimulation();

  // Loading state
  if (state.isLoading && !state.currentPatient) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" text="Loading simulation..." />
      </div>
    );
  }

  // No patient state (shouldn't happen, but defensive)
  if (!state.currentPatient || !state.currentPatientEHR) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No patient data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Session Info Header */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-blue-900">
              Active Simulation
            </h2>
            <p className="text-sm text-blue-700">
              Scenario: {state.scenarioId || 'Unknown'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-blue-700">
              Session: {state.sessionId?.slice(0, 12)}...
            </p>
            {state.clock && (
              <p className="text-sm text-blue-700">
                Elapsed: {state.clock.elapsed_minutes}m
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Grid: Patient Card + Action Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Patient Card */}
        <div className="lg:col-span-2">
          <PatientCard patient={state.currentPatient} />
        </div>

        {/* Right Column: Action Panel */}
        <div>
          <ActionPanel patientId={state.currentPatient.patient_id} />
        </div>
      </div>

      {/* EHR Viewer - Full Width */}
      <EHRViewer />

      {/* Error Display */}
      {state.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            <span className="font-semibold">Error:</span> {state.error}
          </p>
        </div>
      )}
    </div>
  );
}
