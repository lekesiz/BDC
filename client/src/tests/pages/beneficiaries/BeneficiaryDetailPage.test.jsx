import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import BeneficiaryDetailPage from '../../../pages/beneficiaries/BeneficiaryDetailPage';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import api from '@/lib/api';
// Mock the modules
vi.mock('@/hooks/useAuth');
vi.mock('@/components/ui/toast');
vi.mock('@/lib/api');
// Mock router
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: '123' }),
    useNavigate: () => mockNavigate,
  };
});
// Mock navigate function
const mockNavigate = vi.fn();
// Mock data
const mockBeneficiary = {
  id: '123',
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone: '+1234567890',
  status: 'active',
  bio: 'Test bio information',
  birth_date: '1990-01-01',
  address: '123 Main St',
  city: 'Test City',
  state: 'Test State',
  zip_code: '12345',
  country: 'Test Country',
  nationality: 'Test Nationality',
  created_at: '2023-01-01T00:00:00Z',
  evaluation_count: 5,
  completed_evaluation_count: 3,
  session_count: 2,
  trainer_count: 2,
  notes: [
    {
      id: '1',
      title: 'Test Note',
      content: 'This is a test note',
      created_at: '2023-01-02T00:00:00Z',
      created_by_name: 'Test User'
    }
  ],
  recent_activities: [
    {
      description: 'Completed an evaluation',
      timestamp: '2023-01-03T00:00:00Z',
      icon: 'PieChart'
    }
  ]
};
const mockEvaluations = {
  evaluations: [
    {
      id: '1',
      title: 'Initial Assessment',
      description: 'First evaluation for beneficiary',
      status: 'completed',
      evaluation_date: '2023-01-05T00:00:00Z',
      evaluator_name: 'Test Evaluator',
      score: 85,
      max_score: 100,
      percentage_score: 85,
      time_taken: '45 minutes'
    }
  ]
};
const mockSessions = {
  sessions: [
    {
      id: '1',
      title: 'Introduction Session',
      description: 'Initial meeting and overview',
      status: 'completed',
      scheduled_at: '2023-01-10T00:00:00Z',
      duration: 60,
      trainer_name: 'Test Trainer',
      location: 'Online'
    }
  ]
};
const mockTrainers = [
  {
    id: '1',
    first_name: 'Jane',
    last_name: 'Smith',
    email: 'jane@example.com',
    profile_picture: null,
    assigned_date: '2023-01-15T00:00:00Z',
    session_count: 2
  }
];
const mockProgress = {
  overall_percentage: 65,
  completed_evaluations: 3,
  average_score: 78,
  improvement_rate: 12,
  skills: [
    {
      id: '1',
      name: 'Communication',
      proficiency_level: 'Intermediate',
      progress_percentage: 70,
      last_evaluated_at: '2023-01-20T00:00:00Z'
    }
  ],
  growth_areas: [
    {
      title: 'Technical Skills',
      description: 'Needs improvement in technical knowledge'
    }
  ]
};
const mockDocuments = {
  documents: [
    {
      id: '1',
      name: 'Evaluation Report',
      description: 'Detailed assessment results',
      type: 'evaluation_report',
      created_at: '2023-01-25T00:00:00Z',
      size_formatted: '1.2 MB',
      file_type: 'pdf',
      uploaded_by_name: 'Test Uploader',
      view_url: '/documents/1/view',
      download_url: '/documents/1/download'
    }
  ]
};
// Mock Auth hook
const mockHasRole = vi.fn();
useAuth.mockReturnValue({
  hasRole: mockHasRole
});
// Mock Toast hook
const mockAddToast = vi.fn();
useToast.mockReturnValue({
  addToast: mockAddToast
});
describe('BeneficiaryDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementations
    api.get.mockImplementation((url) => {
      if (url.includes('/api/beneficiaries/123')) {
        return Promise.resolve({ data: mockBeneficiary });
      }
      if (url.includes('/evaluations')) {
        return Promise.resolve({ data: mockEvaluations });
      }
      if (url.includes('/sessions')) {
        return Promise.resolve({ data: mockSessions });
      }
      if (url.includes('/trainers')) {
        return Promise.resolve({ data: mockTrainers });
      }
      if (url.includes('/progress')) {
        return Promise.resolve({ data: mockProgress });
      }
      if (url.includes('/documents')) {
        return Promise.resolve({ data: mockDocuments });
      }
      return Promise.reject(new Error('Not found'));
    });
    api.delete.mockResolvedValue({ data: { success: true } });
    // Default role
    mockHasRole.mockReturnValue(true);
  });
  it('renders loading state initially', () => {
    api.get.mockImplementationOnce(() => new Promise(() => {})); // Never resolves
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
  it('renders beneficiary details correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText('Test bio information')).toBeInTheDocument();
    expect(screen.getByText(/123 Main St/)).toBeInTheDocument();
    expect(screen.getByText('Test Nationality')).toBeInTheDocument();
    // Quick stats
    expect(screen.getByText('5')).toBeInTheDocument(); // evaluation_count
    expect(screen.getByText('3')).toBeInTheDocument(); // completed_evaluation_count
    expect(screen.getByText('2')).toBeInTheDocument(); // session_count
    // Note
    expect(screen.getByText('Test Note')).toBeInTheDocument();
    expect(screen.getByText('This is a test note')).toBeInTheDocument();
    // Recent activity
    expect(screen.getByText('Completed an evaluation')).toBeInTheDocument();
  });
  it('handles the evaluations tab correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click on evaluations tab
    fireEvent.click(screen.getByText('Evaluations'));
    // Verify API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries/123/evaluations');
    });
    // Check evaluation data is displayed
    expect(screen.getByText('Initial Assessment')).toBeInTheDocument();
    expect(screen.getByText('First evaluation for beneficiary')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });
  it('handles the sessions tab correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click on sessions tab
    fireEvent.click(screen.getByText('Sessions'));
    // Verify API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries/123/sessions');
    });
    // Check session data is displayed
    expect(screen.getByText('Introduction Session')).toBeInTheDocument();
    expect(screen.getByText('Initial meeting and overview')).toBeInTheDocument();
    expect(screen.getByText('60 minutes')).toBeInTheDocument();
    expect(screen.getByText('Test Trainer')).toBeInTheDocument();
  });
  it('handles the trainers tab correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click on trainers tab
    fireEvent.click(screen.getByText('Trainers'));
    // Verify API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries/123/trainers');
    });
    // Check trainer data is displayed
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    expect(screen.getByText('2 sessions conducted')).toBeInTheDocument();
  });
  it('handles the progress tab correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click on progress tab
    fireEvent.click(screen.getByText('Progress'));
    // Verify API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries/123/progress');
    });
    // Check progress data is displayed
    expect(screen.getByText('65% Complete')).toBeInTheDocument();
    expect(screen.getByText('78%')).toBeInTheDocument(); // average_score
    expect(screen.getByText('+12%')).toBeInTheDocument(); // improvement_rate
    // Skills
    expect(screen.getByText('Communication')).toBeInTheDocument();
    expect(screen.getByText('Intermediate')).toBeInTheDocument();
    // Growth areas
    expect(screen.getByText('Technical Skills')).toBeInTheDocument();
    expect(screen.getByText('Needs improvement in technical knowledge')).toBeInTheDocument();
  });
  it('handles the documents tab correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click on documents tab
    fireEvent.click(screen.getByText('Documents'));
    // Verify API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/beneficiaries/123/documents');
    });
    // Check document data is displayed
    expect(screen.getByText('Evaluation Report')).toBeInTheDocument();
    expect(screen.getByText('Detailed assessment results')).toBeInTheDocument();
    expect(screen.getByText('1.2 MB')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('Test Uploader')).toBeInTheDocument();
  });
  it('handles edit navigation correctly', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click edit button
    fireEvent.click(screen.getByText('Edit'));
    // Verify navigation
    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries/123/edit');
  });
  it('handles delete confirmation modal', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click delete button to open modal
    fireEvent.click(screen.getByText('Delete'));
    // Check modal content
    expect(screen.getByText('Delete Beneficiary')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to delete the beneficiary/)).toBeInTheDocument();
    expect(screen.getByText('John Doe', { selector: 'strong' })).toBeInTheDocument();
    // Click cancel
    fireEvent.click(screen.getByText('Cancel'));
    // Modal should close
    await waitFor(() => {
      expect(screen.queryByText('Delete Beneficiary')).not.toBeInTheDocument();
    });
  });
  it('handles delete confirmation successfully', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Click delete button to open modal
    fireEvent.click(screen.getByText('Delete'));
    // Click delete confirmation
    fireEvent.click(screen.getByText('Delete Beneficiary'));
    // Verify API call
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/api/beneficiaries/123');
    });
    // Verify toast
    expect(mockAddToast).toHaveBeenCalledWith({
      type: 'success',
      title: 'Beneficiary deleted',
      message: 'The beneficiary has been successfully deleted.'
    });
    // Verify navigation
    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries');
  });
  it('handles API error when fetching beneficiary', async () => {
    // Mock API error
    api.get.mockRejectedValueOnce(new Error('Failed to fetch'));
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    // Wait for error handling
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        type: 'error',
        title: 'Failed to load beneficiary',
        message: 'An unexpected error occurred'
      });
    });
    // Verify navigation back to listing
    expect(mockNavigate).toHaveBeenCalledWith('/beneficiaries');
  });
  it('handles API error when fetching tab data', async () => {
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Mock API error for evaluations
    api.get.mockRejectedValueOnce(new Error('Failed to fetch evaluations'));
    // Click on evaluations tab
    fireEvent.click(screen.getByText('Evaluations'));
    // Wait for error handling
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        type: 'error',
        title: 'Failed to load evaluations',
        message: 'An unexpected error occurred'
      });
    });
  });
  it('handles empty states for each tab', async () => {
    // Mock empty responses
    api.get.mockImplementation((url) => {
      if (url.includes('/api/beneficiaries/123')) {
        return Promise.resolve({ data: mockBeneficiary });
      }
      if (url.includes('/evaluations')) {
        return Promise.resolve({ data: { evaluations: [] } });
      }
      if (url.includes('/sessions')) {
        return Promise.resolve({ data: { sessions: [] } });
      }
      if (url.includes('/trainers')) {
        return Promise.resolve({ data: [] });
      }
      if (url.includes('/progress')) {
        return Promise.resolve({ data: {} });
      }
      if (url.includes('/documents')) {
        return Promise.resolve({ data: { documents: [] } });
      }
      return Promise.reject(new Error('Not found'));
    });
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Test empty evaluations tab
    fireEvent.click(screen.getByText('Evaluations'));
    await waitFor(() => {
      expect(screen.getByText('No evaluations found')).toBeInTheDocument();
    });
    // Test empty sessions tab
    fireEvent.click(screen.getByText('Sessions'));
    await waitFor(() => {
      expect(screen.getByText('No sessions scheduled')).toBeInTheDocument();
    });
    // Test empty trainers tab
    fireEvent.click(screen.getByText('Trainers'));
    await waitFor(() => {
      expect(screen.getByText('No trainers assigned')).toBeInTheDocument();
    });
    // Test empty progress tab
    fireEvent.click(screen.getByText('Progress'));
    await waitFor(() => {
      expect(screen.getByText('No progress data yet')).toBeInTheDocument();
    });
    // Test empty documents tab
    fireEvent.click(screen.getByText('Documents'));
    await waitFor(() => {
      expect(screen.getByText('No documents')).toBeInTheDocument();
    });
  });
  it('handles role-based permissions correctly', async () => {
    // Mock user without permissions
    mockHasRole.mockReturnValue(false);
    render(
      <BrowserRouter>
        <BeneficiaryDetailPage />
      </BrowserRouter>
    );
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    // Edit and Delete buttons should not be visible
    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
    expect(screen.queryByText('Delete')).not.toBeInTheDocument();
  });
});