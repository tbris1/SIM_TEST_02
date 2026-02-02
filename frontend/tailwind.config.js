/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // EHR-inspired color palette
        'sidebar-bg': '#1e3a5f',  // Dark blue sidebar
        'sidebar-hover': '#2d4a6f',
        'sidebar-active': '#3d5a7f',

        // Patient state colors
        'state-stable': '#10b981',      // Green
        'state-concerns': '#f59e0b',    // Orange
        'state-deteriorating': '#ef4444', // Red
        'state-critical': '#991b1b',    // Dark red

        // UI accent colors
        'primary': '#3b82f6',     // Blue
        'secondary': '#6b7280',   // Gray
        'success': '#10b981',     // Green
        'danger': '#ef4444',      // Red
        'warning': '#f59e0b',     // Orange
        'info': '#3b82f6',        // Blue
      },
    },
  },
  plugins: [],
}
