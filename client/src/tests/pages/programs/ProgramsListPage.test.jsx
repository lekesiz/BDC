import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import ProgramsListPage from '@/pages/programs/ProgramsListPage';
import api from '@/lib/api';

// Mock dependencies
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    delete: vi.fn()
  }
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: '1', role: 'admin' }
  })
}));

vi.mock('@/contexts/SocketContext', () => ({
  useSocket: () => ({
    on: vi.fn(),
    off: vi.fn()
  })
}));

const mockToast = vi.fn();

vi.mock('@/components/ui/toast', () => ({
  useToast: () => ({
    toast: mockToast
  })
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn()
  };
});

// Mock window.confirm
global.confirm = vi.fn();

const mockPrograms = [
  {
    id: '1',
    name: 'Web Development Bootcamp',
    description: 'Learn full-stack web development',
    code: 'WEB-001',
    category: 'technology',
    level: 'beginner',
    status: 'active',
    duration: '12 weeks',
    participants_count: 25,
    trainers: ['John Doe'],
    rating: 4.5
  },
  {
    id: '2',
    name: 'Data Science Fundamentals',
    description: 'Introduction to data science and analytics',
    code: 'DS-001',
    category: 'data',
    level: 'intermediate',
    status: 'active',
    duration: '8 weeks',
    participants_count: 15,
    trainers: ['Jane Smith'],
    rating: 4.8
  },
  {
    id: '3',
    name: 'Digital Marketing',
    description: 'Master digital marketing strategies',
    code: 'DM-001',
    category: 'marketing',
    level: 'beginner',
    status: 'draft',
    duration: '6 weeks',
    participants_count: 0,
    trainers: ['Mike Johnson'],
    rating: 0
  }
];

const renderComponent = () => {
  return render(
    <BrowserRouter>
      <ProgramsListPage />
    </BrowserRouter>
  );
};

describe('ProgramsListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue({ data: mockPrograms });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders and loads programs', async () => {
    renderComponent();
    
    // Wait for programs to load
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/programs');
    });

    // Check if programs are displayed
    expect(await screen.findByText('Web Development Bootcamp')).toBeInTheDocument();
  });

  it('fetches and displays programs', async () => {
    renderComponent();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/programs');
    });

    // Check if programs are displayed
    expect(await screen.findByText('Web Development Bootcamp')).toBeInTheDocument();
    expect(screen.getByText('Data Science Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Digital Marketing')).toBeInTheDocument();
  });

  it('displays program details correctly', async () => {
    renderComponent();

    // Wait for programs to load first
    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Check program details
    const container = screen.getByText('Web Development Bootcamp').closest('div');
    expect(container).toHaveTextContent('12 weeks');
  });

  it('filters programs by search term', async () => {
    const user = userEvent.setup();
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search programs/i);
    await user.type(searchInput, 'data');

    // Should only show Data Science program
    await waitFor(() => {
      expect(screen.queryByText('Web Development Bootcamp')).not.toBeInTheDocument();
      expect(screen.getByText('Data Science Fundamentals')).toBeInTheDocument();
      expect(screen.queryByText('Digital Marketing')).not.toBeInTheDocument();
    });
  });

  it('filters programs by category', async () => {
    const user = userEvent.setup();
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Open filter dropdown
    const filterButton = screen.getByRole('button', { name: /filter/i });
    await user.click(filterButton);

    // Select technology category
    const categorySelect = screen.getByLabelText(/category/i);
    await user.selectOptions(categorySelect, 'technology');

    // Should only show technology programs
    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      expect(screen.queryByText('Data Science Fundamentals')).not.toBeInTheDocument();
      expect(screen.queryByText('Digital Marketing')).not.toBeInTheDocument();
    });
  });

  it('filters programs by level', async () => {
    const user = userEvent.setup();
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Open filter dropdown
    const filterButton = screen.getByRole('button', { name: /filter/i });
    await user.click(filterButton);

    // Select beginner level
    const levelSelect = screen.getByLabelText(/level/i);
    await user.selectOptions(levelSelect, 'beginner');

    // Should show beginner programs
    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      expect(screen.queryByText('Data Science Fundamentals')).not.toBeInTheDocument();
      expect(screen.getByText('Digital Marketing')).toBeInTheDocument();
    });
  });

  it('filters programs by status', async () => {
    const user = userEvent.setup();
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Open filter dropdown
    const filterButton = screen.getByRole('button', { name: /filter/i });
    await user.click(filterButton);

    // Select active status
    const statusSelect = screen.getByLabelText(/status/i);
    await user.selectOptions(statusSelect, 'active');

    // Should show only active programs
    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
      expect(screen.getByText('Data Science Fundamentals')).toBeInTheDocument();
      expect(screen.queryByText('Digital Marketing')).not.toBeInTheDocument();
    });
  });

  it('deletes a program when confirmed', async () => {
    const user = userEvent.setup();
    global.confirm.mockReturnValue(true);
    api.delete.mockResolvedValue({});

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Click delete button on first program
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this program?');
    expect(api.delete).toHaveBeenCalledWith('/api/programs/1');

    // Program should be removed from list
    await waitFor(() => {
      expect(screen.queryByText('Web Development Bootcamp')).not.toBeInTheDocument();
    });
  });

  it('does not delete program when cancelled', async () => {
    const user = userEvent.setup();
    global.confirm.mockReturnValue(false);

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(api.delete).not.toHaveBeenCalled();
    expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
  });

  it('handles real-time program creation', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Simulate real-time event
    const newProgram = {
      id: '4',
      name: 'New Program',
      description: 'A new program',
      code: 'NEW-001',
      category: 'technology',
      level: 'beginner',
      status: 'active'
    };

    const event = new CustomEvent('programCreated', { detail: newProgram });
    window.dispatchEvent(event);

    await waitFor(() => {
      expect(screen.getByText('New Program')).toBeInTheDocument();
    });
  });

  it('handles real-time program update', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Simulate real-time update
    const updatedProgram = {
      ...mockPrograms[0],
      name: 'Updated Web Development Bootcamp'
    };

    const event = new CustomEvent('programUpdated', { detail: updatedProgram });
    window.dispatchEvent(event);

    await waitFor(() => {
      expect(screen.queryByText('Web Development Bootcamp')).not.toBeInTheDocument();
      expect(screen.getByText('Updated Web Development Bootcamp')).toBeInTheDocument();
    });
  });

  it('handles real-time program deletion', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    });

    // Simulate real-time deletion
    const event = new CustomEvent('programDeleted', { detail: { id: '1' } });
    window.dispatchEvent(event);

    await waitFor(() => {
      expect(screen.queryByText('Web Development Bootcamp')).not.toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    api.get.mockRejectedValueOnce(new Error('Network error'));

    renderComponent();

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Error',
        description: 'Failed to load programs',
        type: 'error'
      });
    });
  });
});