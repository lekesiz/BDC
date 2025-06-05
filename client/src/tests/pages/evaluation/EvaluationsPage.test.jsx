import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import EvaluationsPage from '../../../pages/evaluation/EvaluationsPage';
import api from '@/lib/api';
import { EVALUATION_STATUS } from '@/lib/constants';
import { useToast } from '@/components/ui/toast';
// Mock modules
vi.mock('@/lib/api');
vi.mock('@/components/ui/toast');
// Mock useNavigate hook
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});
// Mock toast hook
const mockAddToast = vi.fn();
useToast.mockReturnValue({
  toast: mockAddToast,
});
// Sample evaluations data
const mockEvaluations = {
  items: [
    {
      id: '1',
      title: 'JavaScript Basics',
      description: 'Test your knowledge of JavaScript fundamentals',
      status: EVALUATION_STATUS.ACTIVE,
      time_limit: 30,
      questions: [
        { id: '1', question_text: 'What is JavaScript?' },
        { id: '2', question_text: 'What is a variable?' },
      ],
      passing_score: 70,
      skills: ['JavaScript', 'Programming'],
    },
    {
      id: '2',
      title: 'HTML & CSS',
      description: 'Test your knowledge of HTML and CSS',
      status: EVALUATION_STATUS.DRAFT,
      time_limit: 45,
      questions: [
        { id: '3', question_text: 'What is HTML?' },
        { id: '4', question_text: 'What is CSS?' },
      ],
      passing_score: 60,
      skills: ['HTML', 'CSS', 'Web Development'],
    },
    {
      id: '3',
      title: 'React Fundamentals',
      description: 'Test your knowledge of React JS',
      status: EVALUATION_STATUS.ARCHIVED,
      time_limit: null,
      questions: [
        { id: '5', question_text: 'What is React?' },
        { id: '6', question_text: 'What is JSX?' },
      ],
      passing_score: 75,
      skills: ['React', 'JavaScript', 'Web Development'],
    },
  ],
};
describe('EvaluationsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue({ data: mockEvaluations });
  });
  it('renders loading state initially', async () => {
    // Mock API never resolves to keep loading state
    api.get.mockImplementationOnce(() => new Promise(() => {}));
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Loading spinner should be shown - look for any loading indicator
    const loadingIndicator = screen.getByRole('status') || screen.getByTestId('loading-spinner');
    expect(loadingIndicator).toBeInTheDocument();
  });
  it('renders list of evaluations correctly', async () => {
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Check all evaluations are rendered
    expect(screen.getByText('HTML & CSS')).toBeInTheDocument();
    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    // Check evaluation details
    expect(screen.getByText('Test your knowledge of JavaScript fundamentals')).toBeInTheDocument();
    expect(screen.getByText('30 min')).toBeInTheDocument();
    expect(screen.getByText('2 Questions')).toBeInTheDocument();
    expect(screen.getByText('70% to Pass')).toBeInTheDocument();
    // Check status badges
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Draft')).toBeInTheDocument();
    expect(screen.getByText('Archived')).toBeInTheDocument();
    // Check skill tags are displayed
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('Programming')).toBeInTheDocument();
    expect(screen.getByText('HTML')).toBeInTheDocument();
    expect(screen.getByText('CSS')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
  });
  it('handles API errors correctly', async () => {
    // Mock API error
    api.get.mockRejectedValueOnce(new Error('Failed to fetch'));
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for error handling
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        title: 'Error',
        description: 'Failed to load evaluations',
        type: 'error',
      });
    });
  });
  it('navigates to create page when Create New Test button is clicked', async () => {
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Click create button
    fireEvent.click(screen.getByText('Create New Test'));
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/create');
  });
  it('navigates to view page when View button is clicked', async () => {
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Get all View buttons and click the first one
    const viewButtons = screen.getAllByText('View');
    fireEvent.click(viewButtons[0]);
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/1');
  });
  it('navigates to edit page when Edit button is clicked', async () => {
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Get all Edit buttons and click the first one
    const editButtons = screen.getAllByText('Edit');
    fireEvent.click(editButtons[0]);
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/1/edit');
  });
  it('deletes an evaluation when Delete button is clicked and confirmed', async () => {
    // Mock confirm to return true (user confirms deletion)
    global.confirm = vi.fn(() => true);
    // Mock delete API call
    api.delete.mockResolvedValue({ data: { success: true } });
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Get all Delete buttons and click the first one
    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    // Check confirm was called
    expect(global.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this evaluation? This action cannot be undone.'
    );
    // Check delete API was called
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith(expect.stringContaining('/1'));
    });
    // Check toast was shown
    expect(mockAddToast).toHaveBeenCalledWith({
      title: 'Success',
      description: 'Evaluation deleted successfully',
      type: 'success',
    });
  });
  it('does not delete when user cancels confirmation', async () => {
    // Mock confirm to return false (user cancels deletion)
    global.confirm = vi.fn(() => false);
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Get all Delete buttons and click the first one
    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    // Check confirm was called
    expect(global.confirm).toHaveBeenCalled();
    // Check delete API was NOT called
    expect(api.delete).not.toHaveBeenCalled();
  });
  it('handles delete errors correctly', async () => {
    // Mock confirm to return true (user confirms deletion)
    global.confirm = vi.fn(() => true);
    // Mock delete API to fail
    api.delete.mockRejectedValueOnce(new Error('Delete failed'));
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Get all Delete buttons and click the first one
    const deleteButtons = screen.getAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    // Check error handling
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        title: 'Error',
        description: 'Failed to delete evaluation',
        type: 'error',
      });
    });
  });
  it('filters evaluations by status', async () => {
    // Mock API calls for filtering
    const mockApiCall = vi.fn().mockResolvedValue({ data: mockEvaluations });
    api.get.mockImplementation(mockApiCall);
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Initially all evaluations are visible
    expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    expect(screen.getByText('HTML & CSS')).toBeInTheDocument();
    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    // Filter by Draft status
    fireEvent.change(screen.getByRole('combobox'), { target: { value: EVALUATION_STATUS.DRAFT } });
    // In the current implementation, filtering is done client-side
    // Only draft evaluation should be visible
    expect(screen.queryByText('JavaScript Basics')).not.toBeInTheDocument();
    expect(screen.getByText('HTML & CSS')).toBeInTheDocument();
    expect(screen.queryByText('React Fundamentals')).not.toBeInTheDocument();
    // Change filter to Active
    fireEvent.change(screen.getByRole('combobox'), { target: { value: EVALUATION_STATUS.ACTIVE } });
    // Only active evaluation should be visible
    expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    expect(screen.queryByText('HTML & CSS')).not.toBeInTheDocument();
    expect(screen.queryByText('React Fundamentals')).not.toBeInTheDocument();
  });
  it('filters evaluations by search term', async () => {
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Initially all evaluations are visible
    expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    expect(screen.getByText('HTML & CSS')).toBeInTheDocument();
    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    // Filter by search term
    fireEvent.change(screen.getByPlaceholderText('Search evaluations...'), { target: { value: 'React' } });
    // Only React evaluation should be visible
    expect(screen.queryByText('JavaScript Basics')).not.toBeInTheDocument();
    expect(screen.queryByText('HTML & CSS')).not.toBeInTheDocument();
    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    // Clear search
    fireEvent.change(screen.getByPlaceholderText('Search evaluations...'), { target: { value: '' } });
    // All evaluations should be visible again
    expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    expect(screen.getByText('HTML & CSS')).toBeInTheDocument();
    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
  });
  it('displays empty state when no evaluations are available', async () => {
    // Mock empty evaluations list
    api.get.mockResolvedValueOnce({ data: { items: [] } });
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for empty state to show
    await waitFor(() => {
      expect(screen.getByText('No evaluations found')).toBeInTheDocument();
    });
    // Check empty state content
    expect(screen.getByText('Get started by creating your first evaluation')).toBeInTheDocument();
    expect(screen.getAllByText('Create New Test')[1]).toBeInTheDocument(); // One in header, one in empty state
  });
  it('displays filtered empty state when search returns no results', async () => {
    render(
      <BrowserRouter>
        <EvaluationsPage />
      </BrowserRouter>
    );
    // Wait for evaluations to load
    await waitFor(() => {
      expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
    });
    // Filter by non-matching search term
    fireEvent.change(screen.getByPlaceholderText('Search evaluations...'), { target: { value: 'NotFound' } });
    // Empty state should show with filter message
    await waitFor(() => {
      expect(screen.getByText('No evaluations found')).toBeInTheDocument();
    });
    expect(screen.getByText('Try adjusting your filters or search term')).toBeInTheDocument();
  });
});