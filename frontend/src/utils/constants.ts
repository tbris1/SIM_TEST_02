/**
 * Application constants
 */

/**
 * Base URL for API requests
 * Default: http://localhost:8000/api/v1
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Polling interval for session state updates (milliseconds)
 * Default: 2000ms (2 seconds)
 */
export const POLL_INTERVAL_MS = 2000;

/**
 * Polling interval for EHR updates (milliseconds)
 * Default: 5000ms (5 seconds)
 */
export const EHR_POLL_INTERVAL_MS = 5000;
