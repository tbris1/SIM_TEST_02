/**
 * Time and date formatting utilities
 */

/**
 * Format ISO datetime string to HH:MM format (24-hour)
 * @param isoString - ISO 8601 datetime string (e.g., "2024-01-15T14:30:00")
 * @returns Formatted time string (e.g., "14:30")
 * @example formatTime("2024-01-15T14:30:00") // "14:30"
 */
export function formatTime(isoString: string): string {
  const date = new Date(isoString);
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

/**
 * Format ISO datetime string to full date and time
 * @param isoString - ISO 8601 datetime string
 * @returns Formatted datetime string (e.g., "Jan 15, 2024 14:30")
 * @example formatDateTime("2024-01-15T14:30:00") // "Jan 15, 2024 14:30"
 */
export function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[date.getMonth()];
  const day = date.getDate();
  const year = date.getFullYear();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${month} ${day}, ${year} ${hours}:${minutes}`;
}

/**
 * Format elapsed time in minutes to human-readable format
 * @param minutes - Total elapsed time in minutes
 * @returns Formatted elapsed time (e.g., "2h 30m", "45m")
 * @example formatElapsed(150) // "2h 30m"
 * @example formatElapsed(45) // "45m"
 */
export function formatElapsed(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Format date to short format (MMM DD)
 * @param isoString - ISO 8601 datetime string
 * @returns Formatted date string (e.g., "Jan 15")
 * @example formatDate("2024-01-15T14:30:00") // "Jan 15"
 */
export function formatDate(isoString: string): string {
  const date = new Date(isoString);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[date.getMonth()];
  const day = date.getDate();
  return `${month} ${day}`;
}

/**
 * Calculate time difference in minutes between two ISO datetime strings
 * @param startTime - ISO 8601 datetime string (earlier time)
 * @param endTime - ISO 8601 datetime string (later time)
 * @returns Difference in minutes
 * @example timeDifferenceMinutes("2024-01-15T14:00:00", "2024-01-15T14:30:00") // 30
 */
export function timeDifferenceMinutes(startTime: string, endTime: string): number {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const diffMs = end.getTime() - start.getTime();
  return Math.floor(diffMs / 60000); // Convert milliseconds to minutes
}
