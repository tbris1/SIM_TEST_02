/**
 * Header: Top header bar with title and optional clock slot.
 * Provides consistent header across pages.
 */

import type { ReactNode } from 'react';

export interface HeaderProps {
  title?: string;
  clockSlot?: ReactNode;
  actionSlot?: ReactNode;
  className?: string;
}

/**
 * Header component for top navigation
 */
export function Header({ title, clockSlot, actionSlot, className = '' }: HeaderProps) {
  return (
    <header className={`bg-white border-b border-gray-200 px-6 py-4 ${className}`}>
      <div className="flex items-center justify-between">
        {/* Left side - Title */}
        <div>
          {title && <h2 className="text-2xl font-bold text-gray-900">{title}</h2>}
        </div>

        {/* Center - Clock slot */}
        {clockSlot && (
          <div className="flex-1 flex justify-center">
            {clockSlot}
          </div>
        )}

        {/* Right side - Action slot */}
        {actionSlot && (
          <div className="flex items-center space-x-4">
            {actionSlot}
          </div>
        )}
      </div>
    </header>
  );
}
