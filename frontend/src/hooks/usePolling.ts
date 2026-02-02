/**
 * usePolling: Custom hook for automatic polling.
 * Used primarily for refreshing session state to get clock updates.
 */

import { useEffect, useRef } from 'react';

export interface UsePollingOptions {
  /**
   * Callback function to execute on each poll
   */
  callback: () => void | Promise<void>;

  /**
   * Polling interval in milliseconds
   * Default: 2000 (2 seconds)
   */
  intervalMs?: number;

  /**
   * Whether polling is enabled
   * Set to false to pause polling
   */
  enabled?: boolean;
}

/**
 * Custom hook for polling
 * Executes callback function at regular intervals
 *
 * @example
 * usePolling({
 *   callback: refreshSessionState,
 *   intervalMs: 2000,
 *   enabled: isSessionActive
 * });
 */
export function usePolling({
  callback,
  intervalMs = 2000,
  enabled = true,
}: UsePollingOptions): void {
  // Use ref to always get the latest callback without recreating the effect
  const savedCallback = useRef(callback);

  // Update ref when callback changes
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the polling interval
  useEffect(() => {
    if (!enabled) {
      return;
    }

    // Execute callback immediately on mount
    const execute = async () => {
      try {
        await savedCallback.current();
      } catch (error) {
        console.error('Polling callback error:', error);
      }
    };

    execute(); // Execute immediately

    // Set up interval for subsequent polls
    const intervalId = setInterval(execute, intervalMs);

    // Cleanup on unmount or when dependencies change
    return () => {
      clearInterval(intervalId);
    };
  }, [intervalMs, enabled]);
}

/**
 * Default polling interval constant
 */
export const DEFAULT_POLL_INTERVAL_MS = 2000; // 2 seconds
