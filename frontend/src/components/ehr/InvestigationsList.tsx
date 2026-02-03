/**
 * InvestigationsList: Display list of investigation results
 * Renders all visible results in reverse chronological order (newest first)
 */

import { InvestigationCard } from './InvestigationCard';
import type { InvestigationResult } from '../../api/types';

export interface InvestigationsListProps {
  results: InvestigationResult[];
  totalResults: number;
  className?: string;
}

export function InvestigationsList({
  results,
  totalResults,
  className = '',
}: InvestigationsListProps) {
  // Sort results by requested time (newest first)
  const sortedResults = [...results].sort(
    (a, b) =>
      new Date(b.requested_time).getTime() - new Date(a.requested_time).getTime()
  );

  const visibleCount = results.length;
  const hiddenCount = totalResults - visibleCount;

  // Count abnormal results
  const abnormalCount = results.filter(
    (result) => result.abnormal_flags && result.abnormal_flags.length > 0
  ).length;

  return (
    <div className={className}>
      {/* Header with progressive revelation indicator */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Investigation Results
          </h3>
          {abnormalCount > 0 && (
            <p className="text-sm text-red-600 mt-1">
              {abnormalCount} abnormal result{abnormalCount !== 1 ? 's' : ''}
            </p>
          )}
        </div>
        <div className="text-sm text-gray-600">
          <span className="font-medium">{visibleCount}</span> of{' '}
          <span className="font-medium">{totalResults}</span> visible
          {hiddenCount > 0 && (
            <span className="ml-2 text-orange-600 font-medium">
              ({hiddenCount} hidden)
            </span>
          )}
        </div>
      </div>

      {/* Results list */}
      {sortedResults.length > 0 ? (
        <div className="space-y-4">
          {sortedResults.map((result) => (
            <InvestigationCard key={result.result_id} result={result} />
          ))}
        </div>
      ) : (
        <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-gray-500">No investigation results visible yet</p>
          {hiddenCount > 0 && (
            <p className="text-sm text-orange-600 mt-2">
              {hiddenCount} result{hiddenCount !== 1 ? 's' : ''} will be revealed
              as you progress
            </p>
          )}
        </div>
      )}
    </div>
  );
}
