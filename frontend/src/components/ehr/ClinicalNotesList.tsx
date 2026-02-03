/**
 * ClinicalNotesList: Display list of clinical notes
 * Renders all visible notes in reverse chronological order (newest first)
 */

import { ClinicalNoteCard } from './ClinicalNoteCard';
import type { ClinicalNote } from '../../api/types';

export interface ClinicalNotesListProps {
  notes: ClinicalNote[];
  totalNotes: number;
  className?: string;
}

export function ClinicalNotesList({
  notes,
  totalNotes,
  className = '',
}: ClinicalNotesListProps) {
  // Sort notes by timestamp (newest first)
  const sortedNotes = [...notes].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  const visibleCount = notes.length;
  const hiddenCount = totalNotes - visibleCount;

  return (
    <div className={className}>
      {/* Header with progressive revelation indicator */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Clinical Notes</h3>
        <div className="text-sm text-gray-600">
          <span className="font-medium">{visibleCount}</span> of{' '}
          <span className="font-medium">{totalNotes}</span> visible
          {hiddenCount > 0 && (
            <span className="ml-2 text-orange-600 font-medium">
              ({hiddenCount} hidden)
            </span>
          )}
        </div>
      </div>

      {/* Notes list */}
      {sortedNotes.length > 0 ? (
        <div className="space-y-4">
          {sortedNotes.map((note) => (
            <ClinicalNoteCard key={note.note_id} note={note} />
          ))}
        </div>
      ) : (
        <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-gray-500">No clinical notes visible yet</p>
          {hiddenCount > 0 && (
            <p className="text-sm text-orange-600 mt-2">
              {hiddenCount} note{hiddenCount !== 1 ? 's' : ''} will be revealed
              as you progress
            </p>
          )}
        </div>
      )}
    </div>
  );
}
