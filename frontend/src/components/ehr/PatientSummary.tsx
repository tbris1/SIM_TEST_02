/**
 * PatientSummary: Always-visible patient information
 * Displays allergies, active diagnoses, and current medications
 */

import type { Medication } from '../../api/types';

export interface PatientSummaryProps {
  allergies: string[];
  diagnoses: string[];
  medications: Medication[];
  className?: string;
}

export function PatientSummary({
  allergies,
  diagnoses,
  medications,
  className = '',
}: PatientSummaryProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Allergies */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-red-900 mb-2 flex items-center">
          <svg
            className="w-4 h-4 mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          Allergies
        </h3>
        {allergies.length > 0 ? (
          <ul className="space-y-1">
            {allergies.map((allergy, index) => (
              <li key={index} className="text-sm text-red-800 font-medium">
                • {allergy}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-red-700">No known allergies</p>
        )}
      </div>

      {/* Active Diagnoses */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">
          Active Diagnoses
        </h3>
        {diagnoses.length > 0 ? (
          <ul className="space-y-1">
            {diagnoses.map((diagnosis, index) => (
              <li key={index} className="text-sm text-blue-800">
                • {diagnosis}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-blue-700 italic">No active diagnoses</p>
        )}
      </div>

      {/* Current Medications */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-green-900 mb-2">
          Current Medications
        </h3>
        {medications.length > 0 ? (
          <ul className="space-y-2">
            {medications.map((medication, index) => (
              <li key={index} className="text-sm text-green-800">
                <span className="font-medium">{medication.name}</span>
                <span className="text-green-700"> - {medication.dose}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-green-700 italic">No current medications</p>
        )}
      </div>
    </div>
  );
}
