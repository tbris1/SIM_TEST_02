import { Building2, AlertCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface Ward {
  id: string;
  name: string;
  description: string;
  patientCount: number;
  capacity: number;
  criticalCount: number;
}

interface WardNavigationProps {
  wards: Ward[];
  selectedWardId: string;
  onSelectWard: (wardId: string) => void;
}

export function WardNavigation({ wards, selectedWardId, onSelectWard }: WardNavigationProps) {
  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-sidebar-foreground" />
          <h2 className="text-sm font-semibold text-sidebar-foreground">Hospital Wards</h2>
        </div>
      </div>

      {/* Ward List */}
      <div className="flex-1 overflow-y-auto p-2">
        <nav className="space-y-1">
          {wards.map((ward) => {
            const isActive = ward.id === selectedWardId;
            return (
              <button
                key={ward.id}
                onClick={() => onSelectWard(ward.id)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-md transition-colors",
                  "flex items-center justify-between gap-2",
                  "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  isActive && "bg-sidebar-accent text-sidebar-accent-foreground"
                )}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "text-sm font-medium truncate",
                      isActive ? "text-sidebar-accent-foreground" : "text-sidebar-foreground"
                    )}>
                      {ward.name}
                    </span>
                    {ward.criticalCount > 0 && (
                      <Badge variant="destructive" className="h-5 text-xs">
                        {ward.criticalCount}
                      </Badge>
                    )}
                  </div>
                  <div className={cn(
                    "text-xs mt-0.5",
                    isActive ? "text-sidebar-accent-foreground/70" : "text-sidebar-foreground/60"
                  )}>
                    {ward.patientCount} / {ward.capacity}
                  </div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-sidebar-border space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-sidebar-foreground/60">Total Patients</span>
          <span className="text-sidebar-foreground font-medium">
            {wards.reduce((sum, ward) => sum + ward.patientCount, 0)}
          </span>
        </div>
        {wards.some(ward => ward.criticalCount > 0) && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-sidebar-foreground/60 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              Critical Alerts
            </span>
            <span className="text-destructive font-medium">
              {wards.reduce((sum, ward) => sum + ward.criticalCount, 0)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
