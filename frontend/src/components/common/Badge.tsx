/**
 * Badge: Status badge component.
 * Supports patient state colors and general variants.
 */

import type { ReactNode } from 'react';
import { PatientState } from '../../api/types';

export type BadgeVariant = 'info' | 'success' | 'warning' | 'danger' | 'neutral';

export interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  patientState?: PatientState;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  info: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-orange-100 text-orange-800',
  danger: 'bg-red-100 text-red-800',
  neutral: 'bg-gray-100 text-gray-800',
};

const patientStateStyles: Record<PatientState, string> = {
  stable: 'bg-state-stable text-white',
  stable_with_concerns: 'bg-state-concerns text-white',
  deteriorating: 'bg-state-deteriorating text-white',
  critically_unwell: 'bg-state-critical text-white',
};

/**
 * Badge component for status indicators
 */
export function Badge({ children, variant, patientState, className = '' }: BadgeProps) {
  const baseStyles = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';

  let colorStyles = '';
  if (patientState) {
    colorStyles = patientStateStyles[patientState];
  } else if (variant) {
    colorStyles = variantStyles[variant];
  } else {
    colorStyles = variantStyles.neutral;
  }

  return <span className={`${baseStyles} ${colorStyles} ${className}`}>{children}</span>;
}
