/**
 * PatientCard: Patient overview with demographics and current state
 * Displays patient information, location, and clinical state with history
 */

import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { PatientDetailsResponse, PatientState as PatientStateType } from '../../api/types';

export interface PatientCardProps {
  patient: PatientDetailsResponse;
  className?: string;
}

/**
 * Get badge variant for patient state
 */
const getStateVariant = (state: PatientStateType): 'success' | 'warning' | 'danger' => {
  switch (state) {
    case 'stable':
      return 'success';
    case 'stable_with_concerns':
      return 'warning';
    case 'deteriorating':
    case 'critically_unwell':
      return 'danger';
    default:
      return 'warning';
  }
};

/**
 * Format state for display
 */
const formatState = (state: PatientStateType): string => {
  return state
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export function PatientCard({ patient, className = '' }: PatientCardProps) {
  const {
    name,
    mrn,
    age,
    gender,
    ward,
    bed,
    current_state,
    state_history,
  } = patient;

  const stateVariant = getStateVariant(current_state);
  const stateDisplay = formatState(current_state);

  return (
    <Card className={className}>
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{name}</h2>
            <p className="text-sm text-gray-600">MRN: {mrn}</p>
          </div>
          <Badge variant={stateVariant} className="text-base px-3 py-1">
            {stateDisplay}
          </Badge>
        </div>
      </div>

      {/* Demographics */}
      <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-200">
        <div>
          <p className="text-xs text-gray-500 mb-1">Age</p>
          <p className="text-sm font-medium text-gray-900">{age} years</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Gender</p>
          <p className="text-sm font-medium text-gray-900">{gender}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Ward</p>
          <p className="text-sm font-medium text-gray-900">{ward}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Bed</p>
          <p className="text-sm font-medium text-gray-900">{bed}</p>
        </div>
      </div>

      {/* State History */}
      {state_history && state_history.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">State History</h3>
          <div className="space-y-2">
            {state_history.slice(0, 3).map((change, index) => (
              <div
                key={index}
                className="text-xs bg-gray-50 rounded p-2 border border-gray-200"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-gray-700">
                    {formatState(change.old_state)} → {formatState(change.new_state)}
                  </span>
                  <span className="text-gray-500">
                    {new Date(change.timestamp).toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                {change.trigger && (
                  <p className="text-gray-600">
                    <span className="font-medium">Trigger:</span> {change.trigger}
                  </p>
                )}
              </div>
            ))}
          </div>
          {state_history.length > 3 && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              +{state_history.length - 3} more changes
            </p>
          )}
        </div>
      )}
    </Card>
  );
}
