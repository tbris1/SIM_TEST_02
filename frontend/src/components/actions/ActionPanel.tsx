/**
 * ActionPanel: Grid of quick-access action buttons
 * Opens modal dialogs for each action (review, investigate, escalate, document)
 */

import { useState } from 'react';
import { Button } from '../common/Button';
import { ReviewPatientModal } from './ReviewPatientModal';
import { OrderInvestigationModal } from './OrderInvestigationModal';
import { EscalateModal } from './EscalateModal';
import { DocumentNoteModal } from './DocumentNoteModal';
import { ReviewAndDocumentModal } from './ReviewAndDocumentModal';
import { useSimulationContext } from '../../context/SimulationContext';

export interface ActionPanelProps {
  patientId: string;
  className?: string;
}

type ModalType = 'review' | 'investigate' | 'escalate' | 'document' | null;

/**
 * Action panel with modal dialogs for patient management
 */
export function ActionPanel({ patientId, className = '' }: ActionPanelProps) {
  const [openModal, setOpenModal] = useState<ModalType>(null);
  const { state, dispatch } = useSimulationContext();

  // Close any open modal
  const closeModal = () => setOpenModal(null);

  // Close review documentation modal
  const closeReviewDocModal = () => {
    dispatch({ type: 'CLOSE_REVIEW_DOCUMENTATION_MODAL' });
  };

  return (
    <>
      <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>

        {/* Action buttons grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* Review Patient */}
          <Button
            variant="primary"
            size="lg"
            onClick={() => setOpenModal('review')}
            className="flex flex-col items-center justify-center h-24"
          >
            <svg
              className="w-8 h-8 mb-2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="font-semibold">Review Patient</span>
            <span className="text-xs opacity-80 mt-1">In-person assessment</span>
          </Button>

          {/* Order Investigation */}
          <Button
            variant="primary"
            size="lg"
            onClick={() => setOpenModal('investigate')}
            className="flex flex-col items-center justify-center h-24"
          >
            <svg
              className="w-8 h-8 mb-2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <span className="font-semibold">Order Investigation</span>
            <span className="text-xs opacity-80 mt-1">Request tests</span>
          </Button>

          {/* Escalate */}
          <Button
            variant="danger"
            size="lg"
            onClick={() => setOpenModal('escalate')}
            className="flex flex-col items-center justify-center h-24"
          >
            <svg
              className="w-8 h-8 mb-2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span className="font-semibold">Escalate</span>
            <span className="text-xs opacity-80 mt-1">Alert senior doctor</span>
          </Button>

          {/* Document Note */}
          <Button
            variant="secondary"
            size="lg"
            onClick={() => setOpenModal('document')}
            className="flex flex-col items-center justify-center h-24"
          >
            <svg
              className="w-8 h-8 mb-2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <span className="font-semibold">Document Note</span>
            <span className="text-xs opacity-80 mt-1">Add clinical note</span>
          </Button>
        </div>
      </div>

      {/* Modals */}
      <ReviewPatientModal
        isOpen={openModal === 'review'}
        onClose={closeModal}
        patientId={patientId}
      />
      <OrderInvestigationModal
        isOpen={openModal === 'investigate'}
        onClose={closeModal}
        patientId={patientId}
      />
      <EscalateModal
        isOpen={openModal === 'escalate'}
        onClose={closeModal}
        patientId={patientId}
      />
      <DocumentNoteModal
        isOpen={openModal === 'document'}
        onClose={closeModal}
        patientId={patientId}
      />

      {/* Review documentation modal (auto-opened after in-person review) */}
      {state.reviewDocumentationModal.examinationNote && (
        <ReviewAndDocumentModal
          isOpen={state.reviewDocumentationModal.isOpen}
          onClose={closeReviewDocModal}
          patientId={state.reviewDocumentationModal.patientId!}
          examinationNote={state.reviewDocumentationModal.examinationNote}
        />
      )}
    </>
  );
}
