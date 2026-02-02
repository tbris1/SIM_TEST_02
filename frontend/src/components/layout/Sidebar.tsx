/**
 * Sidebar: Dark blue navigation sidebar.
 * Provides navigation links and branding.
 */

import type { ReactNode } from 'react';

export interface SidebarNavItem {
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
  active?: boolean;
}

export interface SidebarProps {
  navItems?: SidebarNavItem[];
  className?: string;
}

/**
 * Sidebar component with dark blue background
 */
export function Sidebar({ navItems = [], className = '' }: SidebarProps) {
  return (
    <aside className={`bg-sidebar-bg text-white h-full flex flex-col ${className}`}>
      {/* Logo/Branding */}
      <div className="p-6 border-b border-blue-800">
        <h1 className="text-xl font-bold">Medical On-Call</h1>
        <p className="text-sm text-blue-200 mt-1">Simulation Platform</p>
      </div>

      {/* Navigation */}
      {navItems.length > 0 && (
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item, index) => (
            <button
              key={index}
              onClick={item.onClick}
              className={`w-full flex items-center px-4 py-3 rounded-md transition-colors ${
                item.active
                  ? 'bg-blue-700 text-white'
                  : 'text-blue-100 hover:bg-blue-800 hover:text-white'
              }`}
            >
              {item.icon && <span className="mr-3">{item.icon}</span>}
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
      )}

      {/* Footer */}
      <div className="p-4 border-t border-blue-800">
        <p className="text-xs text-blue-300">© 2026 Medical Simulation</p>
      </div>
    </aside>
  );
}
