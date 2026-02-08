/**
 * SimulationPage: Main simulation interface
 * Three-column layout: Ward Navigation + Patient List + Patient Detail
 */

import { useState } from 'react';
import { useSimulation } from '../hooks/useSimulation';
import { WardNavigation } from '../components/layout/WardNavigation';
import { PatientList, type PatientListItem } from '../components/patient/PatientList';
import { PatientCard } from '../components/patient/PatientCard';
import { MedicationsView } from '../components/ehr/MedicationsView';
import { ClinicalNotesList } from '../components/ehr/ClinicalNotesList';
import { InvestigationsList } from '../components/ehr/InvestigationsList';
import { ActionPanel } from '../components/actions/ActionPanel';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { VitalsQuickView } from '../components/vitals/VitalsQuickView';
import { NewsTrendTabs } from '../components/vitals/NewsTrendTabs';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, FileText, Activity } from 'lucide-react';

export function SimulationPage() {
  const { state } = useSimulation();
  const [selectedWardId, setSelectedWardId] = useState('medical-ward');

  // Loading state
  if (state.isLoading && !state.currentPatient) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" text="Loading simulation..." />
      </div>
    );
  }

  // No patient state (shouldn't happen, but defensive)
  if (!state.currentPatient || !state.currentPatientEHR) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No patient data available</p>
      </div>
    );
  }

  // Convert current patient to PatientListItem format
  const patientListItem: PatientListItem = {
    patient_id: state.currentPatient.patient_id,
    name: state.currentPatient.name,
    mrn: state.currentPatient.mrn,
    age: state.currentPatient.age,
    gender: state.currentPatient.gender,
    current_state: state.currentPatient.current_state,
    ward: state.currentPatient.ward,
    bed: state.currentPatient.bed,
    primary_diagnosis: state.currentPatientEHR.active_diagnoses[0],
  };

  // Mock ward data (single ward for now, ready for expansion)
  const wards = [
    {
      id: 'medical-ward',
      name: 'Medical Ward',
      description: 'General medical patients',
      patientCount: 1,
      capacity: 30,
      criticalCount: state.currentPatient.current_state === 'critically_unwell' ? 1 : 0,
    },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Column 1: Ward Navigation */}
      <WardNavigation
        wards={wards}
        selectedWardId={selectedWardId}
        onSelectWard={setSelectedWardId}
      />

      {/* Column 2: Patient List */}
      <PatientList
        patients={[patientListItem]}
        selectedPatientId={state.currentPatient.patient_id}
        onSelectPatient={() => {
          // For now, only one patient, so this is a no-op
          // In the future, this would switch patients
        }}
        wardName="Medical Ward"
        wardCapacity={30}
      />

      {/* Column 3: Patient Detail */}
      <div className="flex-1 flex flex-col bg-background overflow-hidden">
        {/* Patient Header */}
        <div className="border-b border-border bg-card px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-foreground">
                {state.currentPatient.name}
              </h1>
              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                <span>MRN: {state.currentPatient.mrn}</span>
                <span>•</span>
                <span>{state.currentPatient.age}y, {state.currentPatient.gender}</span>
                <span>•</span>
                <span>Room {state.currentPatient.ward}, Bed {state.currentPatient.bed}</span>
              </div>
            </div>
            {state.clock && (
              <div className="text-right text-sm">
                <div className="text-muted-foreground">Elapsed Time</div>
                <div className="text-lg font-semibold text-foreground">
                  {state.clock.elapsed_minutes}m
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tabbed Content */}
        <Tabs defaultValue="overview" className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="flex flex-shrink-0 w-full justify-start rounded-none border-b bg-card px-6">
            <TabsTrigger value="overview" className="gap-2">
              <User className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="documentation" className="gap-2">
              <FileText className="h-4 w-4" />
              Documentation
            </TabsTrigger>
            <TabsTrigger value="medications" className="gap-2">
              <Activity className="h-4 w-4" />
              Medications
            </TabsTrigger>
            <TabsTrigger value="investigations" className="gap-2">
              <Activity className="h-4 w-4" />
              Investigations
            </TabsTrigger>
            <TabsTrigger value="actions" className="gap-2">
              <Activity className="h-4 w-4" />
              Actions
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-y-auto">
            <div className="p-6">
              <TabsContent value="overview" className="mt-0 space-y-6">
                {state.currentPatient.vitals_history && state.currentPatient.vitals_history.length > 0 ? (
                  <NewsTrendTabs vitalsHistory={state.currentPatient.vitals_history} />
                ) : state.currentPatient.latest_vitals ? (
                  <VitalsQuickView vitals={state.currentPatient.latest_vitals} />
                ) : (
                  <PatientCard patient={state.currentPatient} />
                )}
              </TabsContent>

              <TabsContent value="documentation" className="mt-0">
                <ClinicalNotesList
                  notes={state.currentPatientEHR.visible_notes}
                  totalNotes={state.currentPatientEHR.total_notes}
                />
              </TabsContent>

              <TabsContent value="medications" className="mt-0">
                <MedicationsView
                  allergies={state.currentPatientEHR.allergies}
                  medications={state.currentPatientEHR.current_medications}
                />
              </TabsContent>

              <TabsContent value="investigations" className="mt-0">
                <InvestigationsList
                  results={state.currentPatientEHR.visible_results}
                  totalResults={state.currentPatientEHR.total_results}
                />
              </TabsContent>

              <TabsContent value="actions" className="mt-0">
                <ActionPanel patientId={state.currentPatient.patient_id} />
              </TabsContent>
            </div>
          </div>
        </Tabs>

        {/* Error Display */}
        {state.error && (
          <div className="border-t border-border bg-destructive/10 px-6 py-3">
            <p className="text-sm text-destructive">
              <span className="font-semibold">Error:</span> {state.error}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
