/**
 * DocumentNoteModal: Add clinical note to patient's EHR
 * Free-text note entry with note type selection
 */

import { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useSimulation } from '../../hooks/useSimulation';
import type { NoteType } from '../../api/types';

export interface DocumentNoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
}

interface NoteTypeOption {
  value: NoteType;
  label: string;
  description: string;
}

const NOTE_TYPES: NoteTypeOption[] = [
  {
    value: 'progress',
    label: 'Progress Note',
    description: 'Routine clinical progress note',
  },
  {
    value: 'admission',
    label: 'Admission Note',
    description: 'Initial admission assessment',
  },
  {
    value: 'consultant_review',
    label: 'Consultant Review',
    description: 'Senior doctor review note',
  },
  {
    value: 'procedure_note',
    label: 'Procedure Note',
    description: 'Documentation of procedure performed',
  },
  {
    value: 'nursing_note',
    label: 'Nursing Note',
    description: 'Nursing staff observation',
  },
  {
    value: 'investigation_result',
    label: 'Investigation Result',
    description: 'Result interpretation note',
  },
  {
    value: 'discharge_summary',
    label: 'Discharge Summary',
    description: 'Discharge documentation',
  },
];

/**
 * Modal for documenting clinical notes
 */
export function DocumentNoteModal({
  isOpen,
  onClose,
  patientId,
}: DocumentNoteModalProps) {
  const { documentNote } = useSimulation();
  const [noteType, setNoteType] = useState<NoteType>('progress');
  const [noteContent, setNoteContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const TIME_COST = 3; // minutes

  // Get selected note type details
  const selectedNoteType = NOTE_TYPES.find((nt) => nt.value === noteType);

  const handleSubmit = async () => {
    // Validate content
    if (noteContent.trim().length < 20) {
      setError('Please provide a detailed note (at least 20 characters)');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      await documentNote(patientId, noteContent.trim(), noteType);

      // Close modal on success
      onClose();
      // Reset to defaults
      setNoteType('progress');
      setNoteContent('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to document note');
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
    <Modal isOpen={isOpen} onClose={handleClose} title="Document Clinical Note" size="lg">
      <div className="space-y-4">
        {/* Time cost info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-blue-600 mr-2 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h4 className="text-sm font-semibold text-blue-900">Time Cost</h4>
              <p className="text-sm text-blue-800 mt-1">
                Documenting this note will take approximately{' '}
                <strong>{TIME_COST} minutes</strong> of simulation time.
              </p>
            </div>
          </div>
        </div>

        {/* Note type selection */}
        <div>
          <label
            htmlFor="note-type"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Note Type
          </label>
          <select
            id="note-type"
            value={noteType}
            onChange={(e) => setNoteType(e.target.value as NoteType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isLoading}
          >
            {NOTE_TYPES.map((nt) => (
              <option key={nt.value} value={nt.value}>
                {nt.label}
              </option>
            ))}
          </select>
          {selectedNoteType && (
            <p className="text-sm text-gray-600 mt-2">{selectedNoteType.description}</p>
          )}
        </div>

        {/* Note content */}
        <div>
          <label
            htmlFor="note-content"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Note Content <span className="text-red-500">*</span>
          </label>
          <textarea
            id="note-content"
            value={noteContent}
            onChange={(e) => setNoteContent(e.target.value)}
            placeholder="Enter clinical note content here...&#10;&#10;Example:&#10;Subjective: Patient reports chest pain...&#10;Objective: Vital signs stable, no acute distress...&#10;Assessment: Possible angina, stable...&#10;Plan: Continue monitoring, repeat ECG in 6h..."
            rows={12}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none font-mono text-sm"
            disabled={isLoading}
          />
          <p className="text-xs text-gray-500 mt-1">
            {noteContent.length} characters (minimum 20 required)
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Documentation tip */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-gray-700 mb-1">
            Documentation Tips
          </h4>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• Use structured format (SOAP: Subjective, Objective, Assessment, Plan)</li>
            <li>• Include relevant clinical findings and reasoning</li>
            <li>• Document time-sensitive information and follow-up plans</li>
            <li>• Be concise but comprehensive</li>
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
            disabled={noteContent.trim().length < 20}
            className="flex-1"
          >
            Document Note
          </Button>
        </div>
      </div>
    </Modal>
  );
}
