// TODO: i18n - processed
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { act } from 'react';
import ProgramsListPage from '@/pages/programs/ProgramsListPage';
// Mock dependencies
import { useTranslation } from "react-i18next";const mockPrograms = [
{
  id: 1,
  name: 'Initial Program',
  description: 'Initial program description',
  status: 'active',
  category: 'technical',
  level: 'beginner',
  duration: 30,
  enrolled_count: 5,
  max_participants: 20,
  module_count: 3
}];

const mockSocket = {
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn(),
  connected: true
};
const mockAuth = {
  user: {
    id: 1,
    role: 'tenant_admin',
    email: 'admin@test.com'
  },
  isAuthenticated: true
};
const mockToast = vi.fn();
// Mock modules
vi.mock('@/contexts/SocketContext', () => ({
  useSocket: () => mockSocket
}));
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => mockAuth
}));
vi.mock('@/components/ui/toast', () => ({
  useToast: () => ({ toast: mockToast })
}));
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: mockPrograms })),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};
describe('ProgramsListPage Real-time Updates', () => {
  let socketEventHandlers = {};
  beforeEach(() => {
    vi.clearAllMocks();
    socketEventHandlers = {};
    // Mock socket.on to capture event handlers
    mockSocket.on.mockImplementation((event, handler) => {
      socketEventHandlers[event] = handler;
      return () => {}; // cleanup function
    });
  });
  afterEach(() => {
    vi.clearAllMocks();
  });
  it('registers WebSocket event listeners on mount', async () => {
    renderWithRouter(<ProgramsListPage />);
    await waitFor(() => {
      expect(mockSocket.on).toHaveBeenCalledWith('program_created', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('program_updated', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('program_deleted', expect.any(Function));
    });
  });
  it('adds new program to list when program_created event is received', async () => {
    renderWithRouter(<ProgramsListPage />);
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('Initial Program')).toBeInTheDocument();
    });
    // Simulate program_created event
    const newProgram = {
      id: 2,
      name: 'New Program',
      description: 'New program from WebSocket',
      status: 'draft',
      category: 'soft_skills',
      level: 'intermediate',
      duration: 14,
      enrolled_count: 0,
      max_participants: 15,
      module_count: 2
    };
    act(() => {
      if (socketEventHandlers.program_created) {
        socketEventHandlers.program_created({ program: newProgram });
      }
    });
    await waitFor(() => {
      expect(screen.getByText('New Program')).toBeInTheDocument();
      expect(screen.getByText('New program from WebSocket')).toBeInTheDocument();
    });
  });
  it('updates existing program when program_updated event is received', async () => {
    renderWithRouter(<ProgramsListPage />);
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('Initial Program')).toBeInTheDocument();
    });
    // Simulate program_updated event
    const updatedProgram = {
      id: 1,
      name: 'Updated Program Name',
      description: 'Updated description via WebSocket',
      status: 'active',
      category: 'technical',
      level: 'advanced',
      duration: 45,
      enrolled_count: 8,
      max_participants: 20,
      module_count: 5
    };
    act(() => {
      if (socketEventHandlers.program_updated) {
        socketEventHandlers.program_updated({ program: updatedProgram });
      }
    });
    await waitFor(() => {
      expect(screen.getByText('Updated Program Name')).toBeInTheDocument();
      expect(screen.getByText('Updated description via WebSocket')).toBeInTheDocument();
      expect(screen.queryByText('Initial Program')).not.toBeInTheDocument();
    });
  });
  it('removes program from list when program_deleted event is received', async () => {
    renderWithRouter(<ProgramsListPage />);
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('Initial Program')).toBeInTheDocument();
    });
    // Simulate program_deleted event
    act(() => {
      if (socketEventHandlers.program_deleted) {
        socketEventHandlers.program_deleted({ program_id: 1 });
      }
    });
    await waitFor(() => {
      expect(screen.queryByText('Initial Program')).not.toBeInTheDocument();
    });
  });
  it('handles multiple real-time events in sequence', async () => {
    renderWithRouter(<ProgramsListPage />);
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('Initial Program')).toBeInTheDocument();
    });
    // Add a new program
    const newProgram = {
      id: 2,
      name: 'Second Program',
      description: 'Second program description',
      status: 'active',
      category: 'leadership',
      level: 'beginner',
      duration: 21,
      enrolled_count: 3,
      max_participants: 10,
      module_count: 4
    };
    act(() => {
      if (socketEventHandlers.program_created) {
        socketEventHandlers.program_created({ program: newProgram });
      }
    });
    await waitFor(() => {
      expect(screen.getByText('Second Program')).toBeInTheDocument();
    });
    // Update the first program
    const updatedFirstProgram = {
      id: 1,
      name: 'Updated Initial Program',
      description: 'Updated initial description',
      status: 'completed',
      category: 'technical',
      level: 'expert',
      duration: 60,
      enrolled_count: 12,
      max_participants: 20,
      module_count: 8
    };
    act(() => {
      if (socketEventHandlers.program_updated) {
        socketEventHandlers.program_updated({ program: updatedFirstProgram });
      }
    });
    await waitFor(() => {
      expect(screen.getByText('Updated Initial Program')).toBeInTheDocument();
      expect(screen.getByText('Second Program')).toBeInTheDocument();
    });
    // Delete the second program
    act(() => {
      if (socketEventHandlers.program_deleted) {
        socketEventHandlers.program_deleted({ program_id: 2 });
      }
    });
    await waitFor(() => {
      expect(screen.getByText('Updated Initial Program')).toBeInTheDocument();
      expect(screen.queryByText('Second Program')).not.toBeInTheDocument();
    });
  });
  it('maintains filtered view during real-time updates', async () => {
    renderWithRouter(<ProgramsListPage />);
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('Initial Program')).toBeInTheDocument();
    });
    // Apply search filter (simulate user typing)
    const searchInput = screen.getByPlaceholderText('Search programs...');
    fireEvent.change(searchInput, { target: { value: 'Updated' } });
    // Initially should not show the program
    await waitFor(() => {
      expect(screen.queryByText('Initial Program')).not.toBeInTheDocument();
    });
    // Update program to match filter
    const updatedProgram = {
      id: 1,
      name: 'Updated Program Matching Filter',
      description: 'This should appear in filtered results',
      status: 'active',
      category: 'technical',
      level: 'beginner',
      duration: 30,
      enrolled_count: 5,
      max_participants: 20,
      module_count: 3
    };
    act(() => {
      if (socketEventHandlers.program_updated) {
        socketEventHandlers.program_updated({ program: updatedProgram });
      }
    });
    await waitFor(() => {
      expect(screen.getByText('Updated Program Matching Filter')).toBeInTheDocument();
    });
  });
  it('cleans up event listeners on unmount', () => {
    const { unmount } = renderWithRouter(<ProgramsListPage />);
    // Track cleanup functions
    const cleanupFunctions = [];
    mockSocket.on.mockImplementation((event, handler) => {
      const cleanup = vi.fn();
      cleanupFunctions.push(cleanup);
      return cleanup;
    });
    unmount();
    // Verify cleanup functions were called
    cleanupFunctions.forEach((cleanup) => {
      expect(cleanup).toHaveBeenCalled();
    });
  });
});