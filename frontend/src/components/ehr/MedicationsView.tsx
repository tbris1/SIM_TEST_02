/**
 * MedicationsView: Display patient medications and allergies
 * Shows allergies warning at top and current medications in a table
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';
import type { Medication } from '@/api/types';

export interface MedicationsViewProps {
  allergies: string[];
  medications: Medication[];
  className?: string;
}

export function MedicationsView({
  allergies,
  medications,
  className = '',
}: MedicationsViewProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Allergies Warning */}
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-red-900 mb-2 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Drug Allergies
        </h3>
        {allergies.length > 0 ? (
          <ul className="space-y-1">
            {allergies.map((allergy, index) => (
              <li key={index} className="text-sm text-red-800 font-medium">
                • {allergy}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-red-700">No known drug allergies</p>
        )}
      </div>

      {/* Current Medications */}
      <Card>
        <CardHeader>
          <CardTitle>Current Medications</CardTitle>
        </CardHeader>
        <CardContent>
          {medications.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 px-4 text-sm font-semibold text-foreground">
                      Medication
                    </th>
                    <th className="text-left py-2 px-4 text-sm font-semibold text-foreground">
                      Dose & Frequency
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {medications.map((medication, index) => (
                    <tr key={index} className="border-b border-border last:border-0">
                      <td className="py-3 px-4 text-sm font-medium text-foreground">
                        {medication.name}
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {medication.dose}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">
              No current medications
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
