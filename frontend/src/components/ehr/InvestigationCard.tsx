/**
 * InvestigationCard: Display individual investigation result
 * Shows investigation type, timing, results, abnormal flags, and interpretation
 */

import type { ReactElement } from 'react';
import { Badge } from '../common/Badge';
import type { InvestigationResult } from '../../api/types';

export interface InvestigationCardProps {
  result: InvestigationResult;
  className?: string;
}

/**
 * Format investigation type for display
 */
const formatInvestigationType = (type: string): string => {
  // Handle common abbreviations
  const upperType = type.toUpperCase();
  if (['ABG', 'FBC', 'CXR', 'ECG', 'CT', 'MRI'].includes(upperType)) {
    return upperType;
  }
  // Otherwise format normally
  return type
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Render result data object as formatted table
 */
const renderResultData = (data: Record<string, any>): ReactElement => {
  return (
    <div className="space-y-2">
      {Object.entries(data).map(([key, value]) => {
        const formattedKey = key
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          // Nested object - render as sub-table
          return (
            <div key={key} className="ml-2">
              <p className="text-xs font-semibold text-gray-700 mb-1">
                {formattedKey}:
              </p>
              <div className="ml-4 space-y-1">
                {Object.entries(value).map(([subKey, subValue]) => {
                  const formattedSubKey = subKey
                    .split('_')
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                  return (
                    <div
                      key={subKey}
                      className="flex justify-between text-sm bg-gray-50 px-2 py-1 rounded"
                    >
                      <span className="text-gray-700">{formattedSubKey}</span>
                      <span className="font-medium text-gray-900">
                        {String(subValue)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        } else {
          return (
            <div
              key={key}
              className="flex justify-between text-sm bg-gray-50 px-3 py-2 rounded"
            >
              <span className="text-gray-700">{formattedKey}</span>
              <span className="font-medium text-gray-900">{String(value)}</span>
            </div>
          );
        }
      })}
    </div>
  );
};

export function InvestigationCard({ result, className = '' }: InvestigationCardProps) {
  const {
    investigation_type,
    requested_time,
    resulted_time,
    result_data,
    interpretation,
    abnormal_flags,
  } = result;

  const hasAbnormalFlags = abnormal_flags && abnormal_flags.length > 0;

  return (
    <div
      className={`bg-white border ${
        hasAbnormalFlags ? 'border-red-300' : 'border-gray-200'
      } rounded-lg p-4 hover:shadow-md transition-shadow ${className}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-base font-semibold text-gray-900">
              {formatInvestigationType(investigation_type)}
            </h4>
            {hasAbnormalFlags && (
              <Badge variant="danger" className="text-xs">
                Abnormal
              </Badge>
            )}
          </div>
          <div className="text-xs text-gray-600 space-y-1">
            <p>
              <span className="font-medium">Requested:</span>{' '}
              {new Date(requested_time).toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
            {resulted_time && (
              <p>
                <span className="font-medium">Resulted:</span>{' '}
                {new Date(resulted_time).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Abnormal Flags */}
      {hasAbnormalFlags && (
        <div className="mb-3 bg-red-50 border border-red-200 rounded p-2">
          <p className="text-xs font-semibold text-red-900 mb-1">
            Abnormal Findings:
          </p>
          <ul className="space-y-1">
            {abnormal_flags.map((flag, index) => (
              <li key={index} className="text-sm text-red-800">
                • {flag}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Result Data */}
      <div className="mb-3">{renderResultData(result_data)}</div>

      {/* Interpretation */}
      {interpretation && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-700 mb-1">
            Interpretation:
          </p>
          <p className="text-sm text-gray-900 whitespace-pre-wrap">
            {interpretation}
          </p>
        </div>
      )}
    </div>
  );
}
