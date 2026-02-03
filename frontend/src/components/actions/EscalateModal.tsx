/**
 * EscalateModal: Escalate patient to senior doctor
 * Shows escalation target selection and reason input with 5-minute time cost
 */

import { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useSimulation } from '../../hooks/useSimulation';

export interface EscalateModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
}

interface EscalationTarget {
  value: string;
  label: string;
  description: string;
}

const ESCALATION_TARGETS: EscalationTarget[] = [
  {
    value: 'registrar',
    label: 'Registrar',
    description: 'Senior resident / registrar on-call',
  },
  {
    value: 'consultant',
    label: 'Consultant',
    description: 'Attending physician / consultant on-call',
  },
  {
    value: 'icu_team',
    label: 'ICU Team',
    description: 'Intensive care unit team for critical patients',
  },
  {
    value: 'met_team',
    label: 'MET Team',
    description: 'Medical emergency team (rapid response)',
  },
];

/**
 * Modal for escalating patient to senior doctor
 */
export function EscalateModal({
  isOpen,
  onClose,
  patientId,
}: EscalateModalProps) {
  const { escalatePatient } = useSimulation();
  const [escalateTo, setEscalateTo] = useState<string>('registrar');
  const [reason, setReason] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const TIME_COST = 5; // minutes

  // Get selected escalation target details
  const selectedTarget = ESCALATION_TARGETS.find((t) => t.value === escalateTo);

  const handleSubmit = async () => {
    // Validate reason
    if (reason.trim().length < 10) {
      setError('Please provide a detailed reason (at least 10 characters)');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      await escalatePatient(patientId, escalateTo, reason.trim(), TIME_COST);

      // Close modal on success
      onClose();
      // Reset to defaults
      setEscalateTo('registrar');
      setReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to escalate patient');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
      setError(null);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Escalate Patient" size="md">
      <div className="space-y-4">
        {/* Time cost warning */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-yellow-600 mr-2 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h4 className="text-sm font-semibold text-yellow-900">Time Cost</h4>
              <p className="text-sm text-yellow-800 mt-1">
                Escalating will take <strong>{TIME_COST} minutes</strong> to contact the
                senior doctor and handover the patient.
              </p>
            </div>
          </div>
        </div>

        {/* Escalation target selection */}
        <div>
          <label
            htmlFor="escalate-to"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Escalate To
          </label>
          <select
            id="escalate-to"
            value={escalateTo}
            onChange={(e) => setEscalateTo(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isLoading}
          >
            {ESCALATION_TARGETS.map((target) => (
              <option key={target.value} value={target.value}>
                {target.label}
              </option>
            ))}
          </select>
          {selectedTarget && (
            <p className="text-sm text-gray-600 mt-2">{selectedTarget.description}</p>
          )}
        </div>

        {/* Reason input */}
        <div>
          <label
            htmlFor="reason"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Reason for Escalation <span className="text-red-500">*</span>
          </label>
          <textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Describe clinical concerns and why escalation is needed..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
            disabled={isLoading}
          />
          <p className="text-xs text-gray-500 mt-1">
            {reason.length} characters (minimum 10 required)
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Urgency notice */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-800">
            <strong>Note:</strong> Escalation should be used when patient condition is
            deteriorating, unclear diagnosis requires senior input, or clinical situation
            is beyond your competence.
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3 pt-2">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isLoading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleSubmit}
            isLoading={isLoading}
            disabled={reason.trim().length < 10}
            className="flex-1"
          >
            Escalate Patient
          </Button>
        </div>
      </div>
    </Modal>
  );
}
