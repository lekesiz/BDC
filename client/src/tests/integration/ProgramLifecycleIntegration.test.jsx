import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// Mock SocketContext and useSocket hook
const mockSocket = {
  on: vi.fn(() => vi.fn()), // Returns cleanup function
  off: vi.fn(),
  emit: vi.fn(),
  connected: true
};

vi.mock('@/contexts/SocketContext', () => ({
  useSocket: () => ({
    socket: mockSocket,
    isConnected: true,
    on: mockSocket.on,
    off: mockSocket.off,
    emit: mockSocket.emit
  })
}));
import ProgramsListPage from '@/pages/programs/ProgramsListPage';
import api from '@/lib/api';

// Mock API
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));

// Mock auth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: '1', role: 'super_admin' }
  })
}));

// Mock toast
const mockToast = vi.fn();
vi.mock('@/components/ui/toast', () => ({
  useToast: () => ({ toast: mockToast })
}));

// Test wrapper component
const TestWrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Program Lifecycle Integration', () => {
  const mockPrograms = [
    {
      id: '1',
      name: 'Web Development Bootcamp',
      description: 'Learn full-stack web development',
      code: 'WEB-001',
      category: 'technology',
      level: 'beginner',
      status: 'draft',
      duration: '12 weeks',
      participants_count: 0,
      trainers: [],
      modules: [],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.confirm = vi.fn(() => true);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Program Creation', () => {
    it('creates a program and updates the list', async () => {
      const user = userEvent.setup();
      
      // Mock initial empty list
      api.get.mockResolvedValueOnce({ data: [] });
      
      // Mock program creation
      const newProgram = {
        id: 2,
        name: 'Data Science Fundamentals',
        description: 'Introduction to data science',
        code: 'DS-001',
        category: 'data',
        level: 'beginner',
        status: 'draft',
        duration: 8,
        participants_count: 0,
        trainers: [],
        modules: []
      };
      
      api.post.mockResolvedValueOnce({ data: newProgram });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText(/no programs found/i)).toBeInTheDocument();
      });

      // Click create button (this would navigate to create form)
      const createButton = screen.getByRole('button', { name: /create program/i });
      await user.click(createButton);

      // Simulate program creation via window event (component listens to both methods)
      const programCreatedEvent = new CustomEvent('programCreated', {
        detail: newProgram
      });
      window.dispatchEvent(programCreatedEvent);

      // Verify program appears in list
      await waitFor(() => {
        expect(screen.getByText('Data Science Fundamentals')).toBeInTheDocument();
        expect(screen.getByText('DS-001')).toBeInTheDocument();
      });
    });
  });

  describe('Program Status Updates', () => {
    it('updates program status from draft to active', async () => {
      const user = userEvent.setup();
      
      // Mock initial program list
      api.get.mockResolvedValueOnce({ data: mockPrograms });
      
      // Mock status update
      const updatedProgram = {
        ...mockPrograms[0],
        status: 'active',
        participants_count: 25,
        trainers: ['John Doe']
      };
      
      api.put.mockResolvedValueOnce({ data: updatedProgram });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      // Wait for programs to load
      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Verify initial status
      expect(screen.getByText('draft')).toBeInTheDocument();

      // Simulate status update via WebSocket
      const programUpdatedEvent = new CustomEvent('programUpdated', {
        detail: updatedProgram
      });
      window.dispatchEvent(programUpdatedEvent);

      // Verify updated status
      await waitFor(() => {
        expect(screen.getByText('active')).toBeInTheDocument();
        expect(screen.getByText('25 participants')).toBeInTheDocument();
      });

      // Verify toast notification
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Program Updated',
        description: 'Program status changed to active',
        type: 'success'
      });
    });

    it('handles program lifecycle: draft → active → completed', async () => {
      const program = { ...mockPrograms[0] };
      const states = ['draft', 'active', 'completed'];
      
      api.get.mockResolvedValueOnce({ data: [program] });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Test each state transition
      for (let i = 1; i < states.length; i++) {
        const updatedProgram = {
          ...program,
          status: states[i],
          updated_at: new Date().toISOString()
        };

        // Simulate update via WebSocket
        const event = new CustomEvent('programUpdated', {
          detail: updatedProgram
        });
        window.dispatchEvent(event);

        // Verify status update
        await waitFor(() => {
          expect(screen.getByText(states[i])).toBeInTheDocument();
        });
      }
    });
  });

  describe('Beneficiary Assignment', () => {
    it('assigns beneficiaries to program and updates count', async () => {
      const program = {
        ...mockPrograms[0],
        status: 'active'
      };
      
      api.get.mockResolvedValueOnce({ data: [program] });
      
      // Mock beneficiary assignment
      const beneficiaries = [
        { id: '1', name: 'Student 1' },
        { id: '2', name: 'Student 2' },
        { id: '3', name: 'Student 3' }
      ];
      
      api.post.mockResolvedValueOnce({
        data: {
          ...program,
          participants_count: 3,
          beneficiaries
        }
      });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Simulate beneficiary assignment via WebSocket
      const updatedProgram = {
        ...program,
        participants_count: 3,
        beneficiaries
      };
      
      const event = new CustomEvent('programUpdated', {
        detail: updatedProgram
      });
      window.dispatchEvent(event);

      // Verify participant count update
      await waitFor(() => {
        expect(screen.getByText('3 participants')).toBeInTheDocument();
      });
    });
  });

  describe('Program Deletion', () => {
    it('deletes program and handles cascade effects', async () => {
      const user = userEvent.setup();
      const programs = [
        ...mockPrograms,
        {
          id: '2',
          name: 'Python Programming',
          code: 'PY-001',
          status: 'active',
          participants_count: 10
        }
      ];
      
      api.get.mockResolvedValueOnce({ data: programs });
      api.delete.mockResolvedValueOnce({ data: { success: true } });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
        expect(screen.getByText('Python Programming')).toBeInTheDocument();
      });

      // Click delete on second program
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[1]);

      // Confirm deletion
      expect(global.confirm).toHaveBeenCalledWith(
        'Are you sure you want to delete this program?'
      );

      // Verify API call
      expect(api.delete).toHaveBeenCalledWith('/api/programs/2');

      // Simulate deletion via WebSocket
      const event = new CustomEvent('programDeleted', {
        detail: { id: '2' }
      });
      window.dispatchEvent(event);

      // Verify program removed from list
      await waitFor(() => {
        expect(screen.queryByText('Python Programming')).not.toBeInTheDocument();
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Verify success notification
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Success',
        description: 'Program deleted successfully',
        type: 'success'
      });
    });
  });

  describe('Real-time Updates', () => {
    it('handles multiple concurrent updates', async () => {
      api.get.mockResolvedValueOnce({ data: mockPrograms });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Simulate multiple updates
      const updates = [
        {
          type: 'programCreated',
          data: {
            id: '2',
            name: 'Mobile App Development',
            code: 'MOB-001',
            status: 'draft'
          }
        },
        {
          type: 'programUpdated',
          data: {
            ...mockPrograms[0],
            status: 'active',
            participants_count: 15
          }
        },
        {
          type: 'programCreated',
          data: {
            id: '3',
            name: 'Cloud Computing',
            code: 'CLOUD-001',
            status: 'active'
          }
        }
      ];

      // Dispatch all events
      updates.forEach(({ type, data }) => {
        const event = new CustomEvent(type, { detail: data });
        window.dispatchEvent(event);
      });

      // Verify all updates applied
      await waitFor(() => {
        expect(screen.getByText('Mobile App Development')).toBeInTheDocument();
        expect(screen.getByText('Cloud Computing')).toBeInTheDocument();
        expect(screen.getByText('15 participants')).toBeInTheDocument();
      });
    });

    it('handles WebSocket reconnection', async () => {
      api.get.mockResolvedValueOnce({ data: mockPrograms });

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Simulate disconnection
      mockSocket.connected = false;
      mockSocketContext.isConnected = false;

      // Simulate reconnection
      mockSocket.connected = true;
      mockSocketContext.isConnected = true;

      // Trigger data refresh on reconnection
      api.get.mockResolvedValueOnce({
        data: [
          ...mockPrograms,
          {
            id: '2',
            name: 'New Program After Reconnect',
            code: 'NEW-001',
            status: 'active'
          }
        ]
      });

      // Simulate reconnection event
      const reconnectEvent = new Event('socketReconnected');
      window.dispatchEvent(reconnectEvent);

      // Verify data refreshed
      await waitFor(() => {
        expect(screen.getByText('New Program After Reconnect')).toBeInTheDocument();
      });
    });
  });

  describe('Analytics Generation', () => {
    it('generates program analytics', async () => {
      const program = {
        ...mockPrograms[0],
        status: 'completed',
        participants_count: 30,
        modules: [
          { id: '1', name: 'HTML/CSS', completed: true },
          { id: '2', name: 'JavaScript', completed: true },
          { id: '3', name: 'React', completed: true }
        ],
        analytics: {
          completion_rate: 85,
          average_score: 78,
          satisfaction_rating: 4.5
        }
      };

      api.get.mockResolvedValueOnce({ data: [program] });
      api.get.mockResolvedValueOnce({
        data: {
          program_id: '1',
          completion_rate: 85,
          average_score: 78,
          satisfaction_rating: 4.5,
          module_performance: [
            { module: 'HTML/CSS', average_score: 82 },
            { module: 'JavaScript', average_score: 75 },
            { module: 'React', average_score: 77 }
          ]
        }
      });

      const user = userEvent.setup();

      render(
        <TestWrapper>
          <ProgramsListPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      });

      // Click analytics button
      const analyticsButton = screen.getByRole('button', { name: /view analytics/i });
      await user.click(analyticsButton);

      // Verify analytics API call
      expect(api.get).toHaveBeenCalledWith('/api/programs/1/analytics');

      // Verify analytics display
      await waitFor(() => {
        expect(screen.getByText('85% completion rate')).toBeInTheDocument();
        expect(screen.getByText('78 average score')).toBeInTheDocument();
        expect(screen.getByText('4.5 satisfaction rating')).toBeInTheDocument();
      });
    });
  });
});