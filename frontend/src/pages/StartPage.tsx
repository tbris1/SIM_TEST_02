/**
 * StartPage: Scenario selection and session initialization
 * Displays available scenarios and allows users to start a new simulation session
 */

import { useState, useEffect } from 'react';
import { listScenarios } from '../api/sessions';
import { useSimulation } from '../hooks/useSimulation';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import type { ScenarioListItem } from '../api/types';

export function StartPage() {
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const [isLoadingScenarios, setIsLoadingScenarios] = useState(true);
  const [scenariosError, setScenariosError] = useState<string | null>(null);
  const [startingScenarioId, setStartingScenarioId] = useState<string | null>(null);

  const { state, startSession } = useSimulation();

  // Load scenarios on mount
  useEffect(() => {
    const loadScenarios = async () => {
      try {
        setIsLoadingScenarios(true);
        setScenariosError(null);
        const data = await listScenarios();
        setScenarios(data);
      } catch (error) {
        console.error('Failed to load scenarios:', error);
        setScenariosError('Failed to load scenarios. Please try again.');
      } finally {
        setIsLoadingScenarios(false);
      }
    };

    loadScenarios();
  }, []);

  // Handle starting a session
  const handleStartSession = async (scenarioId: string) => {
    try {
      setStartingScenarioId(scenarioId);
      await startSession(scenarioId);
      // Note: Navigation to /simulation will be added in STEP 12 (Routing)
      // For now, session state is available in SimulationContext
    } catch (error) {
      console.error('Failed to start session:', error);
      // Error is already handled in useSimulation hook
    } finally {
      setStartingScenarioId(null);
    }
  };

  // Get difficulty badge variant
  const getDifficultyVariant = (difficulty: string): 'success' | 'warning' | 'danger' => {
    const lower = difficulty.toLowerCase();
    if (lower.includes('easy') || lower.includes('beginner')) return 'success';
    if (lower.includes('medium') || lower.includes('intermediate')) return 'warning';
    if (lower.includes('hard') || lower.includes('advanced')) return 'danger';
    return 'warning';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Medical On-Call Simulation
        </h1>
        <p className="text-lg text-gray-600">
          Select a scenario to begin your simulation
        </p>
      </div>

      {/* Success Message - Show when session is active */}
      {state.isActive && (
        <Card>
          <div className="text-center">
            <div className="mb-4">
              <span className="inline-block w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Session Started!</h2>
            <p className="text-gray-600 mb-4">
              Your simulation session is now active. The clock is running.
            </p>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Session ID:</span> {state.sessionId}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Scenario ID:</span> {state.scenarioId}
              </p>
              {state.currentPatient && (
                <p className="text-sm text-gray-600">
                  <span className="font-semibold">Current Patient:</span> {state.currentPatient.name}
                </p>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-4">
              Note: Navigation to simulation page will be added in STEP 12
            </p>
          </div>
        </Card>
      )}

      {/* Loading State */}
      {isLoadingScenarios && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" text="Loading scenarios..." />
        </div>
      )}

      {/* Error State */}
      {scenariosError && (
        <Card>
          <div className="text-center text-red-600">
            <p className="font-semibold mb-2">Error</p>
            <p>{scenariosError}</p>
            <Button
              variant="secondary"
              onClick={() => window.location.reload()}
              className="mt-4"
            >
              Retry
            </Button>
          </div>
        </Card>
      )}

      {/* Scenarios Grid */}
      {!isLoadingScenarios && !scenariosError && scenarios.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scenarios.map((scenario) => (
            <Card key={scenario.scenario_id} className="flex flex-col">
              <div className="flex-1">
                {/* Scenario Header */}
                <div className="mb-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-xl font-bold text-gray-900 flex-1">
                      {scenario.title}
                    </h3>
                    <Badge variant={getDifficultyVariant(scenario.difficulty)}>
                      {scenario.difficulty}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{scenario.description}</p>
                </div>

                {/* Scenario Details */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-medium">Duration:</span>
                    <span className="ml-1">~{scenario.estimated_duration_minutes} minutes</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span className="font-medium">Patients:</span>
                    <span className="ml-1">{scenario.patient_count}</span>
                  </div>
                </div>
              </div>

              {/* Start Button */}
              <Button
                variant="primary"
                fullWidth
                isLoading={startingScenarioId === scenario.scenario_id || state.isLoading}
                disabled={state.isActive || isLoadingScenarios}
                onClick={() => handleStartSession(scenario.scenario_id)}
              >
                {state.isActive ? 'Session Active' : 'Start Session'}
              </Button>
            </Card>
          ))}
        </div>
      )}

      {/* No Scenarios */}
      {!isLoadingScenarios && !scenariosError && scenarios.length === 0 && (
        <Card>
          <div className="text-center text-gray-600">
            <p className="font-semibold mb-2">No Scenarios Available</p>
            <p className="text-sm">Please check your backend server.</p>
          </div>
        </Card>
      )}

      {/* Error Display from Context */}
      {state.error && (
        <Card>
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">
              <span className="font-semibold">Error:</span> {state.error}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
