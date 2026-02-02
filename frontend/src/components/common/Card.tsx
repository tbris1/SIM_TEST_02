/**
 * Card: Container component with optional title.
 * Used for grouping related content with consistent styling.
 */

import type { ReactNode } from 'react';

export interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
}

/**
 * Card component for content containers
 */
export function Card({ title, children, className = '', noPadding = false }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      {title && (
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
      )}
      <div className={noPadding ? '' : 'p-6'}>{children}</div>
    </div>
  );
}
