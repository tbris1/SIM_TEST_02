import { useState } from 'react';
import { AppShell } from './components/layout/AppShell';
import { Button } from './components/common/Button';
import { Card } from './components/common/Card';
import { Badge } from './components/common/Badge';
import { Modal } from './components/common/Modal';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { PatientState } from './api';

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const navItems = [
    { label: 'Dashboard', active: true },
    { label: 'Scenarios', active: false },
    { label: 'History', active: false },
  ];

  const handleLoadingTest = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  return (
    <AppShell
      navItems={navItems}
      headerTitle="Component Showcase"
      headerClockSlot={
        <div className="text-center">
          <p className="text-sm text-gray-500">Simulation Time</p>
          <p className="text-lg font-semibold">08:30 AM</p>
        </div>
      }
    >
      <div className="space-y-8">
        {/* Status Banner */}
        <Card>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Medical On-Call Simulation
            </h2>
            <p className="text-gray-600">
              Phase 5: Frontend UI Implementation - Steps 1-4 Complete
            </p>
            <div className="mt-4 flex justify-center space-x-2">
              <Badge variant="success">Step 1: Setup ✓</Badge>
              <Badge variant="success">Step 2: API Client ✓</Badge>
              <Badge variant="success">Step 3: State Management ✓</Badge>
              <Badge variant="success">Step 4: Layout & Components ✓</Badge>
            </div>
          </div>
        </Card>

        {/* Buttons */}
        <Card title="Button Variants">
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button variant="primary">Primary Button</Button>
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="danger">Danger Button</Button>
              <Button variant="success">Success Button</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="primary" size="sm">Small</Button>
              <Button variant="primary" size="md">Medium</Button>
              <Button variant="primary" size="lg">Large</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="primary" isLoading onClick={handleLoadingTest}>
                Loading Button
              </Button>
              <Button variant="secondary" disabled>Disabled Button</Button>
            </div>
          </div>
        </Card>

        {/* Badges */}
        <Card title="Badge Components">
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Patient States:</h4>
              <div className="flex flex-wrap gap-2">
                <Badge patientState={PatientState.STABLE}>Stable</Badge>
                <Badge patientState={PatientState.STABLE_WITH_CONCERNS}>
                  Stable with Concerns
                </Badge>
                <Badge patientState={PatientState.DETERIORATING}>Deteriorating</Badge>
                <Badge patientState={PatientState.CRITICALLY_UNWELL}>
                  Critically Unwell
                </Badge>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">General Variants:</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="info">Info</Badge>
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="danger">Danger</Badge>
                <Badge variant="neutral">Neutral</Badge>
              </div>
            </div>
          </div>
        </Card>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Patient Information">
            <div className="space-y-2">
              <p className="text-sm">
                <span className="font-semibold">Name:</span> John Doe
              </p>
              <p className="text-sm">
                <span className="font-semibold">MRN:</span> 12345678
              </p>
              <p className="text-sm">
                <span className="font-semibold">Age:</span> 65 years
              </p>
              <p className="text-sm">
                <span className="font-semibold">Location:</span> Ward 4B
              </p>
            </div>
          </Card>

          <Card title="Quick Actions">
            <div className="space-y-2">
              <Button variant="primary" fullWidth>
                Review Patient
              </Button>
              <Button variant="secondary" fullWidth>
                Order Investigation
              </Button>
              <Button variant="danger" fullWidth>
                Escalate to Registrar
              </Button>
            </div>
          </Card>
        </div>

        {/* Modal and Loading */}
        <Card title="Modal & Loading Components">
          <div className="space-y-4">
            <div className="flex gap-4">
              <Button variant="primary" onClick={() => setIsModalOpen(true)}>
                Open Modal
              </Button>
              <Button variant="secondary" onClick={handleLoadingTest}>
                Test Loading (2s)
              </Button>
            </div>
            {isLoading && (
              <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-md">
                <LoadingSpinner size="sm" />
                <span className="text-sm text-gray-700">Loading data...</span>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Modal Example */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Example Modal"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            This is an example modal dialog. It includes a title, content area, and close
            button. The modal can be closed by clicking the X button, clicking outside, or
            pressing the Escape key.
          </p>
          <div className="flex justify-end space-x-2">
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={() => setIsModalOpen(false)}>
              Confirm
            </Button>
          </div>
        </div>
      </Modal>
    </AppShell>
  );
}

export default App;
