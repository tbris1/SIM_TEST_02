/**
 * AppShell: Main application layout.
 * Combines Sidebar, Header, and content area.
 */

import type { ReactNode } from 'react';
import { Sidebar, type SidebarNavItem } from './Sidebar';
import { Header } from './Header';

export interface AppShellProps {
  children: ReactNode;
  navItems?: SidebarNavItem[];
  headerTitle?: string;
  headerClockSlot?: ReactNode;
  headerActionSlot?: ReactNode;
  showSidebar?: boolean;
  fullHeight?: boolean;
}

/**
 * AppShell component for main application layout
 */
export function AppShell({
  children,
  navItems,
  headerTitle,
  headerClockSlot,
  headerActionSlot,
  showSidebar = true,
  fullHeight = false,
}: AppShellProps) {
  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar - Fixed width dark blue sidebar */}
      {showSidebar && (
        <div className="w-64 flex-shrink-0">
          <div className="fixed top-0 left-0 h-screen w-64">
            <Sidebar navItems={navItems} />
          </div>
        </div>
      )}

      {/* Main content area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header
          title={headerTitle}
          clockSlot={headerClockSlot}
          actionSlot={headerActionSlot}
        />

        {/* Content */}
        <main className={fullHeight ? "flex-1 overflow-hidden" : "flex-1 overflow-auto"}>
          {fullHeight ? (
            children
          ) : (
            <div className="container mx-auto px-6 py-8">
              {children}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
