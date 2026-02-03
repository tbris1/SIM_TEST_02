import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { User } from 'lucide-react';

export interface PatientListItem {
  patient_id: string;
  name: string;
  mrn: string;
  age: number;
  gender: string;
  current_state: 'stable' | 'stable_with_concerns' | 'deteriorating' | 'critically_unwell';
  ward: string;
  bed: string;
  primary_diagnosis?: string;
}

interface PatientListProps {
  patients: PatientListItem[];
  selectedPatientId: string | null;
  onSelectPatient: (patientId: string) => void;
  wardName?: string;
  wardCapacity?: number;
}

const stateConfig = {
  stable: {
    label: 'Stable',
    variant: 'default' as const,
    className: 'bg-success/10 text-success border-success/20',
  },
  stable_with_concerns: {
    label: 'Monitor',
    variant: 'secondary' as const,
    className: 'bg-warning/10 text-warning border-warning/20',
  },
  deteriorating: {
    label: 'Deteriorating',
    variant: 'destructive' as const,
    className: 'bg-destructive/10 text-destructive border-destructive/20',
  },
  critically_unwell: {
    label: 'Critical',
    variant: 'destructive' as const,
    className: 'bg-destructive text-destructive-foreground',
  },
};

export function PatientList({
  patients,
  selectedPatientId,
  onSelectPatient,
  wardName = 'Medical Ward',
  wardCapacity = 30
}: PatientListProps) {
  return (
    <div className="w-80 border-r border-border bg-card flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-foreground">{wardName}</h2>
          <Badge variant="secondary" className="text-xs">
            {patients.length} / {wardCapacity}
          </Badge>
        </div>
      </div>

      {/* Patient List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-2">
          {patients.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <User className="h-12 w-12 mb-3 opacity-20" />
              <p className="text-sm">No patients in this ward</p>
            </div>
          ) : (
            patients.map((patient) => {
              const isSelected = patient.patient_id === selectedPatientId;
              const stateStyle = stateConfig[patient.current_state];

              return (
                <button
                  key={patient.patient_id}
                  onClick={() => onSelectPatient(patient.patient_id)}
                  className={cn(
                    "w-full text-left p-3 rounded-lg border transition-all",
                    "hover:border-primary/50 hover:bg-accent/50",
                    isSelected
                      ? "border-primary bg-accent shadow-sm"
                      : "border-border bg-card"
                  )}
                >
                  {/* Patient Name and Status */}
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm text-foreground truncate">
                        {patient.name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge
                          variant="outline"
                          className={cn("text-xs font-normal", stateStyle.className)}
                        >
                          {stateStyle.label}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div className="text-xs text-muted-foreground">
                        {patient.ward}
                      </div>
                      <div className="text-xs font-medium text-foreground">
                        Bed {patient.bed}
                      </div>
                    </div>
                  </div>

                  {/* Patient Details */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>MRN: {patient.mrn}</span>
                      <span>•</span>
                      <span>{patient.age}y</span>
                      <span>•</span>
                      <span>{patient.gender}</span>
                    </div>
                    {patient.primary_diagnosis && (
                      <div className="text-xs text-muted-foreground truncate">
                        {patient.primary_diagnosis}
                      </div>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
