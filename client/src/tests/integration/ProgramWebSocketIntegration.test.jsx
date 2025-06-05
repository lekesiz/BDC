/**
 * Integration test for Program WebSocket functionality
 * Tests real-time updates for program operations
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { SocketProvider } from '../../contexts/SocketContext';
import { AuthProvider } from '../../hooks/useAuth';
import ProgramsListPage from '../../pages/programs/ProgramsListPage';
// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    emit: vi.fn(),
    disconnect: vi.fn(),
    connected: true
  }))
}));
// Mock API
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ 
      data: [
        {
          id: 1,
          name: 'Test Program',
          description: 'Test Description',
          category: 'technical',
          level: 'beginner',
          status: 'active',
          duration_weeks: 4
        }
      ]
    }))
  }
}));
// Mock auth hook
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: 1, role: 'super_admin' },
    isAuthenticated: true
  }),
  AuthProvider: ({ children }) => children
}));
// Mock toast
vi.mock('../../components/ui/toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}));
describe('Program WebSocket Integration', () => {
  let mockSocket;
  let eventHandlers = {};
  beforeEach(() => {
    // Reset event handlers
    eventHandlers = {};
    // Mock socket with event handling
    mockSocket = {
      on: vi.fn((event, handler) => {
        eventHandlers[event] = handler;
      }),
      emit: vi.fn(),
      disconnect: vi.fn(),
      connected: true
    };
    // Override the socket.io mock
    vi.doMock('socket.io-client', () => ({
      default: vi.fn(() => mockSocket)
    }));
  });
  afterEach(() => {
    vi.clearAllMocks();
  });
  const renderWithProviders = (component) => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <SocketProvider>
            {component}
          </SocketProvider>
        </AuthProvider>
      </BrowserRouter>
    );
  };
  it('should handle program_created event and update list', async () => {
    renderWithProviders(<ProgramsListPage />);
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument();
    });
    // Simulate program_created event
    const newProgram = {
      id: 2,
      name: 'New WebSocket Program',
      description: 'Created via WebSocket',
      category: 'soft_skills',
      level: 'intermediate',
      status: 'draft',
      duration_weeks: 6
    };
    // Trigger the custom event that our Socket context dispatches
    window.dispatchEvent(new CustomEvent('programCreated', { 
      detail: newProgram 
    }));
    // Check if new program appears in the list
    await waitFor(() => {
      expect(screen.getByText('New WebSocket Program')).toBeInTheDocument();
    });
  });
  it('should handle program_updated event and refresh program data', async () => {
    renderWithProviders(<ProgramsListPage />);
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument();
    });
    // Simulate program_updated event
    const updatedProgram = {
      id: 1,
      name: 'Updated Test Program',
      description: 'Updated via WebSocket',
      category: 'technical',
      level: 'advanced',
      status: 'active',
      duration_weeks: 8
    };
    // Trigger the custom event
    window.dispatchEvent(new CustomEvent('programUpdated', { 
      detail: updatedProgram 
    }));
    // Check if program data is updated
    await waitFor(() => {
      expect(screen.getByText('Updated Test Program')).toBeInTheDocument();
    });
  });
  it('should handle program_deleted event and remove from list', async () => {
    renderWithProviders(<ProgramsListPage />);
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Program')).toBeInTheDocument();
    });
    // Simulate program_deleted event
    const deletedProgram = {
      id: 1,
      name: 'Test Program'
    };
    // Trigger the custom event
    window.dispatchEvent(new CustomEvent('programDeleted', { 
      detail: deletedProgram 
    }));
    // Check if program is removed from the list
    await waitFor(() => {
      expect(screen.queryByText('Test Program')).not.toBeInTheDocument();
    });
  });
  it('should establish socket connection with authentication', () => {
    renderWithProviders(<ProgramsListPage />);
    // Verify socket connection is attempted
    expect(mockSocket.on).toHaveBeenCalledWith('connect', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('disconnect', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('program_created', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('program_updated', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('program_deleted', expect.any(Function));
  });
  it('should emit join_room event for user room', () => {
    renderWithProviders(<ProgramsListPage />);
    // Verify user room join
    expect(mockSocket.emit).toHaveBeenCalledWith('join_room', { room: 'user_1' });
  });
});