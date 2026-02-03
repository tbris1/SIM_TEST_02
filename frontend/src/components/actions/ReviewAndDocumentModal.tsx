/**
 * ReviewAndDocumentModal: Two-part modal for review workflow
 * Part A: Read-only examination findings from system
 * Part B: Editable textarea for user's clinical impression & plan
 */

import { useState } from 'react';
import type { ReactElement } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useSimulation } from '../../hooks/useSimulation';
import type { ClinicalNote } from '../../api/types';

export interface ReviewAndDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
  examinationNote: ClinicalNote;
}

/**
 * Render examination findings content
 */
const renderExaminationFindings = (content: Record<string, any>): ReactElement => {
  return (
    <div className="space-y-3">
      {Object.entries(content).map(([key, value]) => {
        const formattedKey = key
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        if (typeof value === 'string') {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-blue-800">
                {formattedKey}:
              </span>
              <p className="text-sm text-blue-900 mt-1 whitespace-pre-wrap">
                {value}
              </p>
            </div>
          );
        } else if (Array.isArray(value)) {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-blue-800">
                {formattedKey}:
              </span>
              <ul className="text-sm text-blue-900 mt-1 list-disc list-inside space-y-1">
                {value.map((item, index) => (
                  <li key={index}>{String(item)}</li>
                ))}
              </ul>
            </div>
          );
        } else if (typeof value === 'object' && value !== null) {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-blue-800">
                {formattedKey}:
              </span>
              <pre className="text-xs text-blue-900 mt-1 bg-blue-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(value, null, 2)}
              </pre>
            </div>
          );
        }

        return null;
      })}
    </div>
  );
};

/**
 * Modal for documenting clinical review with examination findings
 */
export function ReviewAndDocumentModal({
  isOpen,
  onClose,
  patientId,
  examinationNote,
}: ReviewAndDocumentModalProps) {
  const { documentNote } = useSimulation();
  const [userImpression, setUserImpression] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    // Validate minimum length
    if (userImpression.trim().length < 20) {
      setError('Please provide a detailed clinical impression (at least 20 characters)');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Save user's clinical impression as a separate note
      await documentNote(patientId, userImpression.trim(), 'progress');

      // Close modal and reset
      onClose();
      setUserImpression('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to document note');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
      setUserImpression('');
      setError(null);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Document Clinical Review" size="lg">
      <div className="space-y-4">
        {/* Part A: Read-Only Examination Findings */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center mb-3">
            <svg
              className="w-5 h-5 text-blue-600 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <h3 className="text-sm font-semibold text-blue-900">
              Examination Findings (System-Generated)
            </h3>
          </div>
          <div className="text-sm">
            {renderExaminationFindings(examinationNote.content)}
          </div>
        </div>

        {/* Instruction */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <p className="text-sm text-gray-700">
            <strong>Your task:</strong> Based on the examination findings above, document
            your clinical impression, differential diagnoses, and management plan.
          </p>
        </div>

        {/* Part B: User Documentation */}
        <div>
          <label
            htmlFor="user-impression"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Your Clinical Impression & Plan <span className="text-red-500">*</span>
          </label>
          <textarea
            id="user-impression"
            value={userImpression}
            onChange={(e) => setUserImpression(e.target.value)}
            placeholder="Example:

Clinical Impression:
- Patient appears [stable/unwell/deteriorating]
- Key findings: [summarize examination findings]
- Differential diagnoses: 1) ... 2) ... 3) ...

Plan:
1. Investigations: [what tests are needed?]
2. Treatment: [what interventions?]
3. Monitoring: [what parameters to watch?]
4. Escalation: [when to call senior?]"
            rows={12}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none font-mono text-sm"
            disabled={isLoading}
          />
          <p className="text-xs text-gray-500 mt-1">
            {userImpression.length} characters (minimum 20 required)
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Time cost info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-xs text-yellow-800">
            <strong>Time cost:</strong> Documenting your impression will take
            approximately 3 minutes of simulation time.
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
            Skip Documentation
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            isLoading={isLoading}
            disabled={userImpression.trim().length < 20}
            className="flex-1"
          >
            Save Clinical Note
          </Button>
        </div>
      </div>
    </Modal>
  );
}
