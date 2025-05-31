import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import TestResultsPage from '../../../pages/evaluation/TestResultsPage';
import api from '@/lib/api';
import { QUESTION_TYPES } from '@/lib/constants';
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
    useParams: () => ({ id: '123' }),
  };
});

// Mock toast hook
const mockAddToast = vi.fn();
useToast.mockReturnValue({
  toast: mockAddToast,
});

// Mock URL utilities
global.URL.createObjectURL = vi.fn(() => 'mock-url');
global.Blob = vi.fn(() => ({}));
document.createElement = vi.fn().mockImplementation((tag) => {
  if (tag === 'a') {
    return {
      href: '',
      setAttribute: vi.fn(),
      click: vi.fn(),
      remove: vi.fn(),
    };
  }
  return {};
});
document.body.appendChild = vi.fn();

// Sample session data
const mockSessionData = {
  id: '123',
  test_id: '456',
  beneficiary_id: '789',
  started_at: '2023-06-15T10:00:00Z',
  completed_at: '2023-06-15T10:45:00Z',
  score: 80,
  responses: [
    {
      question_id: '1',
      response_data: 0, // Multiple choice selected option index
      is_correct: true,
      points: 10,
      explanation: 'Correct! JavaScript is a programming language.',
    },
    {
      question_id: '2',
      response_data: 'Container for storing values', // Text response
      is_correct: true,
      points: 10,
      explanation: 'Good definition of a variable.',
    },
    {
      question_id: '3',
      response_data: true, // True/False response
      is_correct: false,
      points: 0,
      explanation: 'HTML is not a programming language.',
    },
    {
      question_id: '4',
      response_data: [0, 2, 1], // Matching response
      is_correct: false,
      points: 5,
      explanation: 'Some matches were incorrect.',
    },
    {
      question_id: '5',
      response_data: [2, 0, 1], // Ordering response
      is_correct: true,
      points: 15,
      explanation: 'Correct order!',
    },
  ],
};

// Sample test data
const mockTestData = {
  id: '456',
  title: 'Web Development Fundamentals',
  description: 'Test your knowledge of web development basics',
  time_limit: 60,
  passing_score: 70,
  skills: ['JavaScript', 'HTML', 'CSS', 'Web Development'],
  questions: [
    {
      id: '1',
      question_text: 'What is JavaScript?',
      question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
      points: 10,
      skills: ['JavaScript'],
      options: [
        { text: 'A programming language', is_correct: true },
        { text: 'A markup language', is_correct: false },
        { text: 'A database system', is_correct: false },
        { text: 'A styling language', is_correct: false },
      ],
    },
    {
      id: '2',
      question_text: 'What is a variable?',
      question_type: QUESTION_TYPES.TEXT,
      points: 10,
      skills: ['JavaScript', 'Programming'],
      correct_answer: 'A container for storing data values',
    },
    {
      id: '3',
      question_text: 'HTML is a programming language',
      question_type: QUESTION_TYPES.TRUE_FALSE,
      points: 10,
      skills: ['HTML'],
      options: [
        { text: 'True', is_correct: false },
        { text: 'False', is_correct: true },
      ],
    },
    {
      id: '4',
      question_text: 'Match the following',
      question_type: QUESTION_TYPES.MATCHING,
      points: 10,
      skills: ['Web Development'],
      matches: [
        { left: 'HTML', right: 'Structure', position: 0 },
        { left: 'CSS', right: 'Style', position: 1 },
        { left: 'JavaScript', right: 'Behavior', position: 2 },
      ],
    },
    {
      id: '5',
      question_text: 'Order the steps to create a web page',
      question_type: QUESTION_TYPES.ORDERING,
      points: 15,
      skills: ['Web Development'],
      order_items: [
        { text: 'Write HTML', position: 0 },
        { text: 'Add CSS', position: 1 },
        { text: 'Add JavaScript', position: 2 },
      ],
    },
  ],
};

// Sample feedback data
const mockFeedbackData = {
  overall_assessment: 'You have a good understanding of web development concepts, but could improve in some areas.',
  strengths: [
    'Strong understanding of JavaScript fundamentals',
    'Solid grasp of programming concepts',
  ],
  areas_for_improvement: [
    'More practice with HTML concepts needed',
    'Review matching of technologies with their purposes',
  ],
  recommendations: [
    'Complete additional HTML exercises',
    'Review the relationship between HTML, CSS, and JavaScript',
  ],
  skill_feedback: {
    'JavaScript': 'Your JavaScript knowledge is strong, scoring 90% in this area.',
    'HTML': 'You should review HTML concepts, as you scored only a 60% in this area.',
    'Web Development': 'Good understanding of web development workflow, but some gaps in matching technologies to their purposes.',
  },
};

describe('TestResultsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockImplementation((url) => {
      if (url.includes('/session')) {
        return Promise.resolve({ data: mockSessionData });
      }
      if (url.includes('/evaluations/detail')) {
        return Promise.resolve({ data: mockTestData });
      }
      if (url.includes('/feedback')) {
        return Promise.resolve({ data: mockFeedbackData });
      }
      if (url.includes('/certificate') || url.includes('/report')) {
        return Promise.resolve({ data: new Blob() });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  it('renders loading state initially', async () => {
    // Mock API never resolves to keep loading state
    api.get.mockImplementationOnce(() => new Promise(() => {}));
    
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Look for any loading indicator
    const spinner = screen.getByRole('status') || screen.queryByText(/loading/i) || screen.getByTestId('loading-spinner');
    expect(spinner).toBeInTheDocument();
  });

  it('renders error state when session data cannot be fetched', async () => {
    // Mock API error for session data
    api.get.mockRejectedValueOnce(new Error('Failed to fetch session data'));
    
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for error handling
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        title: 'Error',
        description: 'Failed to load test results',
        type: 'error',
      });
    });
  });

  it('renders error state when no session or test data exists', async () => {
    // Mock null session data
    api.get.mockResolvedValueOnce({ data: null });
    
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText('Results Not Found')).toBeInTheDocument();
    });
    
    expect(screen.getByText('The requested test results could not be found or have been deleted.')).toBeInTheDocument();
    
    // Check Back button works
    fireEvent.click(screen.getByText('Back to Tests'));
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations');
  });

  it('renders test results page with correct data', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Check score display
    expect(screen.getByText('Score')).toBeInTheDocument();
    expect(screen.getByText('40 / 55 points')).toBeInTheDocument();
    
    // Check correct answers display
    expect(screen.getByText('Correct Answers')).toBeInTheDocument();
    expect(screen.getByText('3 / 5')).toBeInTheDocument();
    
    // Check time taken display
    expect(screen.getByText('Time Taken')).toBeInTheDocument();
    expect(screen.getByText('45m 0s')).toBeInTheDocument();
    
    // Check tabs exist
    expect(screen.getByText('Performance Overview')).toBeInTheDocument();
    expect(screen.getByText('Question Review')).toBeInTheDocument();
    expect(screen.getByText('AI Feedback')).toBeInTheDocument();
  });

  it('displays skills performance correctly in overview tab', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Check skills performance section
    expect(screen.getByText('Skills Performance')).toBeInTheDocument();
    
    // Check each skill is displayed
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('HTML')).toBeInTheDocument();
    expect(screen.getByText('CSS')).toBeInTheDocument();
    expect(screen.getByText('Web Development')).toBeInTheDocument();
    
    // Check strengths and improvement areas
    expect(screen.getByText('Strengths')).toBeInTheDocument();
    expect(screen.getByText('Areas for Improvement')).toBeInTheDocument();
  });

  it('changes tabs correctly when clicked', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Performance Overview tab should be active by default
    expect(screen.getByText('Skills Performance')).toBeInTheDocument();
    
    // Click on Question Review tab
    fireEvent.click(screen.getByText('Question Review'));
    
    // Question Review content should be visible
    expect(screen.getByText('Question 1')).toBeInTheDocument();
    expect(screen.getByText('What is JavaScript?')).toBeInTheDocument();
    
    // Click on AI Feedback tab
    fireEvent.click(screen.getByText('AI Feedback'));
    
    // AI Feedback content should be visible
    expect(screen.getByText('AI-Generated Feedback')).toBeInTheDocument();
    expect(screen.getByText('Overall Assessment')).toBeInTheDocument();
    expect(screen.getByText('You have a good understanding of web development concepts, but could improve in some areas.')).toBeInTheDocument();
  });

  it('displays question review correctly for multiple question types', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Click on Question Review tab
    fireEvent.click(screen.getByText('Question Review'));
    
    // Check Multiple Choice question
    expect(screen.getByText('What is JavaScript?')).toBeInTheDocument();
    expect(screen.getByText('A programming language')).toBeInTheDocument();
    
    // Check Text question
    expect(screen.getByText('What is a variable?')).toBeInTheDocument();
    expect(screen.getByText('Your Answer:')).toBeInTheDocument();
    expect(screen.getByText('Container for storing values')).toBeInTheDocument();
    expect(screen.getByText('Correct Answer:')).toBeInTheDocument();
    expect(screen.getByText('A container for storing data values')).toBeInTheDocument();
    
    // Check True/False question
    expect(screen.getByText('HTML is a programming language')).toBeInTheDocument();
    expect(screen.getByText('True')).toBeInTheDocument();
    expect(screen.getByText('False')).toBeInTheDocument();
    expect(screen.getByText('Correct answer: False')).toBeInTheDocument();
  });

  it('displays AI feedback correctly when available', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Click on AI Feedback tab
    fireEvent.click(screen.getByText('AI Feedback'));
    
    // Check feedback sections
    expect(screen.getByText('Overall Assessment')).toBeInTheDocument();
    expect(screen.getByText('You have a good understanding of web development concepts, but could improve in some areas.')).toBeInTheDocument();
    
    expect(screen.getByText('Strengths')).toBeInTheDocument();
    expect(screen.getByText('Strong understanding of JavaScript fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Solid grasp of programming concepts')).toBeInTheDocument();
    
    expect(screen.getByText('Areas for Improvement')).toBeInTheDocument();
    expect(screen.getByText('More practice with HTML concepts needed')).toBeInTheDocument();
    
    expect(screen.getByText('Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Complete additional HTML exercises')).toBeInTheDocument();
    
    // Check skill-specific feedback
    expect(screen.getByText('Your JavaScript knowledge is strong, scoring 90% in this area.')).toBeInTheDocument();
  });

  it('handles certificate download correctly for passing students', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Certificate button should be visible for passing student
    const certificateButton = screen.getByText('Certificate');
    expect(certificateButton).toBeInTheDocument();
    
    // Click certificate button
    fireEvent.click(certificateButton);
    
    // Check API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/evaluations/sessions/123/certificate', {
        responseType: 'blob',
      });
    });
    
    // Check download link was created and clicked
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(document.createElement).toHaveBeenCalledWith('a');
    const mockAnchor = document.createElement('a');
    expect(mockAnchor.setAttribute).toHaveBeenCalledWith('download', 'certificate-123.pdf');
    expect(mockAnchor.click).toHaveBeenCalled();
    expect(mockAnchor.remove).toHaveBeenCalled();
  });

  it('handles report download correctly', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Report button should be visible
    const reportButton = screen.getByText('Download Report');
    expect(reportButton).toBeInTheDocument();
    
    // Click report button
    fireEvent.click(reportButton);
    
    // Check API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/evaluations/sessions/123/report', {
        responseType: 'blob',
      });
    });
    
    // Check download link was created and clicked
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(document.createElement).toHaveBeenCalledWith('a');
    const mockAnchor = document.createElement('a');
    expect(mockAnchor.setAttribute).toHaveBeenCalledWith('download', 'test-report-123.pdf');
    expect(mockAnchor.click).toHaveBeenCalled();
    expect(mockAnchor.remove).toHaveBeenCalled();
  });

  it('handles download errors correctly', async () => {
    // Mock API error for certificate download
    api.get.mockImplementation((url) => {
      if (url.includes('/certificate')) {
        return Promise.reject(new Error('Download failed'));
      }
      if (url.includes('/session')) {
        return Promise.resolve({ data: mockSessionData });
      }
      if (url.includes('/evaluations/detail')) {
        return Promise.resolve({ data: mockTestData });
      }
      if (url.includes('/feedback')) {
        return Promise.resolve({ data: mockFeedbackData });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
    
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Click certificate button
    fireEvent.click(screen.getByText('Certificate'));
    
    // Check error toast
    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith({
        title: 'Error',
        description: 'Failed to download certificate',
        type: 'error',
      });
    });
  });

  it('navigates to AI analysis page correctly', async () => {
    render(
      <BrowserRouter>
        <TestResultsPage />
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Web Development Fundamentals - Results')).toBeInTheDocument();
    });
    
    // Click AI Analysis button
    fireEvent.click(screen.getByText('AI Analysis'));
    
    // Check navigation
    expect(mockNavigate).toHaveBeenCalledWith('/evaluations/sessions/123/analysis');
  });
});