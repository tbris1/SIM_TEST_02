import { SimulationProvider, useSimulationContext } from './context/SimulationContext';
import { AppShell } from './components/layout/AppShell';
import { SimulationClock } from './components/simulation/SimulationClock';
import { StartPage } from './pages/StartPage';
import { SimulationPage } from './pages/SimulationPage';

/**
 * AppContent: Handles conditional rendering based on simulation state
 */
function AppContent() {
  const { state } = useSimulationContext();

  // Determine which page to show
  const isSimulationActive = state.isActive && !!state.currentPatient;

  const navItems = [
    { label: 'Start', active: !isSimulationActive },
    { label: 'Simulation', active: isSimulationActive },
    { label: 'History', active: false },
  ];

  return (
    <AppShell
      navItems={navItems}
      headerTitle="Medical On-Call Simulation"
      headerClockSlot={<SimulationClock />}
    >
      {isSimulationActive ? <SimulationPage /> : <StartPage />}
    </AppShell>
  );
}

function App() {
  return (
    <SimulationProvider>
      <AppContent />
    </SimulationProvider>
  );
}

export default App;
