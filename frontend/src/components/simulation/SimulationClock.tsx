/**
 * SimulationClock: Real-time clock display for active simulation
 * Displays current simulation time, elapsed time, and artificial time added
 */

import { useSimulation } from '../../hooks/useSimulation';
import { usePolling } from '../../hooks/usePolling';
import { formatTime, formatElapsed } from '../../utils/formatters';
import { POLL_INTERVAL_MS } from '../../utils/constants';

export interface SimulationClockProps {
  /** Whether to show detailed info (elapsed time, artificial time) */
  showDetails?: boolean;
  /** Custom CSS class */
  className?: string;
}

/**
 * SimulationClock component
 * - Polls session state every 2 seconds (when session is active)
 * - Displays current simulation time
 * - Shows elapsed time and artificial time added
 */
export function SimulationClock({ showDetails = true, className = '' }: SimulationClockProps) {
  const { state, refreshSessionState } = useSimulation();

  // Poll for session state updates every 2 seconds when session is active
  usePolling({
    callback: refreshSessionState,
    intervalMs: POLL_INTERVAL_MS,
    enabled: state.isActive && !state.isComplete,
  });

  // If no active session, show placeholder
  if (!state.clock) {
    return (
      <div className={`text-center ${className}`}>
        <p className="text-sm text-gray-400">No active session</p>
        <p className="text-lg font-semibold text-gray-500">--:--</p>
      </div>
    );
  }

  const { current_time, elapsed_minutes, artificial_time_added_minutes } = state.clock;

  return (
    <div className={`text-center ${className}`}>
      {/* Current Time */}
      <p className="text-sm text-gray-500">Simulation Time</p>
      <p className="text-2xl font-bold text-gray-900">{formatTime(current_time)}</p>

      {/* Details: Elapsed & Artificial Time */}
      {showDetails && (
        <div className="mt-2 space-y-1">
          {/* Elapsed Time */}
          <div className="text-xs text-gray-600">
            <span className="font-medium">Elapsed:</span> {formatElapsed(elapsed_minutes)}
          </div>

          {/* Artificial Time (only show if > 0) */}
          {artificial_time_added_minutes > 0 && (
            <div className="text-xs text-orange-600">
              <span className="font-medium">Artificial:</span> +{formatElapsed(artificial_time_added_minutes)}
            </div>
          )}
        </div>
      )}

      {/* Session Complete Indicator */}
      {state.isComplete && (
        <div className="mt-2">
          <span className="inline-block px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
            Session Complete
          </span>
        </div>
      )}
    </div>
  );
}
