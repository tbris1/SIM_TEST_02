/**
 * OrderInvestigationModal: Select and order investigations
 * Shows investigation types, urgency levels, and turnaround times
 */

import { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useSimulation } from '../../hooks/useSimulation';

export interface OrderInvestigationModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
}

interface InvestigationOption {
  value: string;
  label: string;
  description: string;
  routineTurnaround: number; // minutes
  urgentTurnaround: number; // minutes
}

const INVESTIGATIONS: InvestigationOption[] = [
  {
    value: 'abg',
    label: 'ABG (Arterial Blood Gas)',
    description: 'Blood gas analysis with pH, pO2, pCO2, lactate',
    routineTurnaround: 30,
    urgentTurnaround: 10,
  },
  {
    value: 'fbc',
    label: 'FBC (Full Blood Count)',
    description: 'Hemoglobin, WBC, platelets',
    routineTurnaround: 60,
    urgentTurnaround: 30,
  },
  {
    value: 'u_and_e',
    label: 'U&E (Urea & Electrolytes)',
    description: 'Sodium, potassium, creatinine, urea',
    routineTurnaround: 60,
    urgentTurnaround: 30,
  },
  {
    value: 'cxr',
    label: 'CXR (Chest X-Ray)',
    description: 'Portable or department chest radiograph',
    routineTurnaround: 90,
    urgentTurnaround: 30,
  },
  {
    value: 'ecg',
    label: 'ECG (Electrocardiogram)',
    description: '12-lead electrocardiogram',
    routineTurnaround: 20,
    urgentTurnaround: 10,
  },
  {
    value: 'ct_head',
    label: 'CT Head',
    description: 'Non-contrast CT brain scan',
    routineTurnaround: 180,
    urgentTurnaround: 60,
  },
  {
    value: 'troponin',
    label: 'Troponin',
    description: 'Cardiac troponin I/T',
    routineTurnaround: 60,
    urgentTurnaround: 30,
  },
];

/**
 * Modal for ordering investigations
 */
export function OrderInvestigationModal({
  isOpen,
  onClose,
  patientId,
}: OrderInvestigationModalProps) {
  const { orderInvestigation } = useSimulation();
  const [investigationType, setInvestigationType] = useState<string>('abg');
  const [urgency, setUrgency] = useState<'routine' | 'urgent'>('routine');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const TIME_COST = 2; // minutes to order

  // Get selected investigation details
  const selectedInvestigation = INVESTIGATIONS.find(
    (inv) => inv.value === investigationType
  );

  const turnaroundTime =
    urgency === 'urgent'
      ? selectedInvestigation?.urgentTurnaround
      : selectedInvestigation?.routineTurnaround;

  const handleSubmit = async () => {
    if (!selectedInvestigation) return;

    try {
      setIsLoading(true);
      setError(null);

      await orderInvestigation(
        patientId,
        investigationType,
        urgency,
        turnaroundTime
      );

      // Close modal on success
      onClose();
      // Reset to defaults
      setInvestigationType('abg');
      setUrgency('routine');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to order investigation');
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
    <Modal isOpen={isOpen} onClose={handleClose} title="Order Investigation" size="lg">
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
                Ordering takes <strong>{TIME_COST} minutes</strong>. Results will be
                available after <strong>{turnaroundTime} minutes</strong> turnaround time.
              </p>
            </div>
          </div>
        </div>

        {/* Investigation type selection */}
        <div>
          <label
            htmlFor="investigation"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Investigation Type
          </label>
          <select
            id="investigation"
            value={investigationType}
            onChange={(e) => setInvestigationType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isLoading}
          >
            {INVESTIGATIONS.map((inv) => (
              <option key={inv.value} value={inv.value}>
                {inv.label}
              </option>
            ))}
          </select>
          {selectedInvestigation && (
            <p className="text-sm text-gray-600 mt-2">
              {selectedInvestigation.description}
            </p>
          )}
        </div>

        {/* Urgency selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Urgency
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setUrgency('routine')}
              disabled={isLoading}
              className={`px-4 py-3 border-2 rounded-lg transition-all ${
                urgency === 'routine'
                  ? 'border-primary bg-blue-50 text-primary'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">Routine</div>
              <div className="text-sm mt-1">
                {selectedInvestigation?.routineTurnaround} min turnaround
              </div>
            </button>
            <button
              type="button"
              onClick={() => setUrgency('urgent')}
              disabled={isLoading}
              className={`px-4 py-3 border-2 rounded-lg transition-all ${
                urgency === 'urgent'
                  ? 'border-red-500 bg-red-50 text-red-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">Urgent</div>
              <div className="text-sm mt-1">
                {selectedInvestigation?.urgentTurnaround} min turnaround
              </div>
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <h4 className="text-sm font-semibold text-blue-900 mb-1">Summary</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Investigation: {selectedInvestigation?.label}</li>
            <li>• Urgency: {urgency === 'urgent' ? 'Urgent' : 'Routine'}</li>
            <li>• Time to order: {TIME_COST} minutes</li>
            <li>• Results available in: ~{turnaroundTime} minutes</li>
          </ul>
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
            variant="primary"
            onClick={handleSubmit}
            isLoading={isLoading}
            className="flex-1"
          >
            Order Investigation
          </Button>
        </div>
      </div>
    </Modal>
  );
}
