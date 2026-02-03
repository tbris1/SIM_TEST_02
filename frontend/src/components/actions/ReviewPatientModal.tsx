/**
 * ReviewPatientModal: Confirm in-person patient review
 * Shows 30-minute time cost warning and location selection
 */

import { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useSimulation } from '../../hooks/useSimulation';

export interface ReviewPatientModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
}

/**
 * Modal for confirming in-person patient review
 */
export function ReviewPatientModal({
  isOpen,
  onClose,
  patientId,
}: ReviewPatientModalProps) {
  const { reviewPatient } = useSimulation();
  const [location, setLocation] = useState<string>('ward');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const TIME_COST = 30; // minutes

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      setError(null);

      await reviewPatient(patientId, location, TIME_COST);

      // Close modal on success
      onClose();
      setLocation('ward'); // Reset for next time
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to review patient');
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
    <Modal isOpen={isOpen} onClose={handleClose} title="Review Patient In-Person" size="md">
      <div className="space-y-4">
        {/* Time cost warning */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
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
                This action will take <strong>{TIME_COST} minutes</strong> of simulation time.
                The clock will advance and patient status may change.
              </p>
            </div>
          </div>
        </div>

        {/* Location selection */}
        <div>
          <label
            htmlFor="location"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Review Location
          </label>
          <select
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isLoading}
          >
            <option value="ward">Ward</option>
            <option value="emergency_department">Emergency Department</option>
            <option value="icu">ICU</option>
            <option value="theatre">Theatre</option>
          </select>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Action info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-800">
            You will perform a thorough in-person assessment of the patient at their
            bedside. This may reveal additional clinical information and update the EHR.
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
            variant="primary"
            onClick={handleSubmit}
            isLoading={isLoading}
            className="flex-1"
          >
            Confirm Review ({TIME_COST}m)
          </Button>
        </div>
      </div>
    </Modal>
  );
}
