/**
 * ClinicalNoteCard: Display individual clinical note
 * Shows timestamp, author, title, and content with structured formatting
 */

import type { ReactElement } from 'react';
import { Badge } from '../common/Badge';
import type { ClinicalNote, NoteType as NoteTypeEnum } from '../../api/types';

export interface ClinicalNoteCardProps {
  note: ClinicalNote;
  className?: string;
}

/**
 * Get badge variant for note type
 */
const getNoteTypeVariant = (noteType: NoteTypeEnum): 'success' | 'warning' | 'danger' => {
  switch (noteType) {
    case 'admission':
    case 'discharge_summary':
      return 'success';
    case 'consultant_review':
    case 'procedure_note':
      return 'warning';
    case 'investigation_result':
      return 'danger';
    default:
      return 'success';
  }
};

/**
 * Format note type for display
 */
const formatNoteType = (noteType: NoteTypeEnum): string => {
  return noteType
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Render content object as formatted text
 */
const renderContent = (content: Record<string, any>): ReactElement => {
  return (
    <div className="space-y-2">
      {Object.entries(content).map(([key, value]) => {
        // Format key: remove underscores, capitalize
        const formattedKey = key
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        // Handle different value types
        if (typeof value === 'string') {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-gray-700">
                {formattedKey}:
              </span>
              <p className="text-sm text-gray-900 mt-1 whitespace-pre-wrap">
                {value}
              </p>
            </div>
          );
        } else if (Array.isArray(value)) {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-gray-700">
                {formattedKey}:
              </span>
              <ul className="text-sm text-gray-900 mt-1 list-disc list-inside space-y-1">
                {value.map((item, index) => (
                  <li key={index}>{String(item)}</li>
                ))}
              </ul>
            </div>
          );
        } else if (typeof value === 'object' && value !== null) {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-gray-700">
                {formattedKey}:
              </span>
              <pre className="text-xs text-gray-900 mt-1 bg-gray-50 p-2 rounded overflow-x-auto">
                {JSON.stringify(value, null, 2)}
              </pre>
            </div>
          );
        } else {
          return (
            <div key={key}>
              <span className="text-xs font-semibold text-gray-700">
                {formattedKey}:
              </span>
              <p className="text-sm text-gray-900 mt-1">{String(value)}</p>
            </div>
          );
        }
      })}
    </div>
  );
};

export function ClinicalNoteCard({ note, className = '' }: ClinicalNoteCardProps) {
  const { note_type, timestamp, author, author_role, title, content } = note;

  return (
    <div
      className={`bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow ${className}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant={getNoteTypeVariant(note_type)} className="text-xs">
              {formatNoteType(note_type)}
            </Badge>
            <span className="text-xs text-gray-500">
              {new Date(timestamp).toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
          <h4 className="text-base font-semibold text-gray-900">{title}</h4>
          <p className="text-xs text-gray-600 mt-1">
            {author} • {author_role}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        {renderContent(content)}
      </div>
    </div>
  );
}
