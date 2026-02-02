/**
 * Axios HTTP client for the Medical On-Call Simulation API.
 * Configured with base URL and common settings.
 */

import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import type { APIError } from './types';

/**
 * Base API URL - reads from environment variable or defaults to localhost:8000
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Full API path with version
 */
export const API_URL = `${API_BASE_URL}/api/v1`;

/**
 * Configured axios instance for API calls
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

/**
 * Request interceptor - can be used to add auth tokens, logging, etc.
 */
apiClient.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - handles common error cases
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status);
    }
    return response;
  },
  (error: AxiosError<APIError>) => {
    // Handle common error scenarios
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const detail = error.response.data?.detail || 'An error occurred';

      console.error(`[API Error ${status}]`, detail);

      // Handle specific status codes
      if (status === 404) {
        console.error('[API] Resource not found');
      } else if (status === 500) {
        console.error('[API] Server error');
      } else if (status === 503) {
        console.error('[API] Service unavailable');
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('[API] No response from server - is the backend running?');
    } else {
      // Something else happened
      console.error('[API] Request setup error', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * Helper function to extract error message from API error
 */
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail || error.message || 'An unexpected error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default apiClient;
