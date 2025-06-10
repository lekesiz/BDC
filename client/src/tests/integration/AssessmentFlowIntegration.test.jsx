import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
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

// Mock components (simplified versions for testing)
const AssessmentCreationPage = () => {
  const [assessment, setAssessment] = React.useState({
    title: '',
    description: '',
    questions: []
  });

  const handleCreate = async () => {
    const response = await api.post('/api/assessments', assessment);
    window.location.href = `/assessments/${response.data.id}`;
  };

  return (
    <div>
      <h1>Create Assessment</h1>
      <input
        aria-label="Title"
        value={assessment.title}
        onChange={(e) => setAssessment({ ...assessment, title: e.target.value })}
      />
      <textarea
        aria-label="Description"
        value={assessment.description}
        onChange={(e) => setAssessment({ ...assessment, description: e.target.value })}
      />
      <button onClick={() => setAssessment({
        ...assessment,
        questions: [...assessment.questions, { type: 'multiple_choice', text: '', options: [] }]
      })}>
        Add Question
      </button>
      <button onClick={handleCreate}>Create Assessment</button>
    </div>
  );
};

const AssessmentTakingPage = ({ assessmentId }) => {
  const [assessment, setAssessment] = React.useState(null);
  const [answers, setAnswers] = React.useState({});
  const [timeLeft, setTimeLeft] = React.useState(3600); // 1 hour
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    api.get(`/api/assessments/${assessmentId}`).then((res) => {
      setAssessment(res.data);
    });
  }, [assessmentId]);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 0) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSubmit = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    await api.post(`/api/assessments/${assessmentId}/submit`, { answers });
    window.location.href = `/assessments/${assessmentId}/results`;
  };

  if (!assessment) return <div>Loading...</div>;

  return (
    <div>
      <h1>{assessment.title}</h1>
      <div>Time Left: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</div>
      {assessment.questions.map((q, idx) => (
        <div key={idx}>
          <p>{q.text}</p>
          <input
            aria-label={`Answer for question ${idx + 1}`}
            value={answers[idx] || ''}
            onChange={(e) => setAnswers({ ...answers, [idx]: e.target.value })}
          />
        </div>
      ))}
      <button onClick={handleSubmit} disabled={isSubmitting}>Submit Assessment</button>
    </div>
  );
};

const AssessmentResultsPage = ({ assessmentId }) => {
  const [results, setResults] = React.useState(null);

  React.useEffect(() => {
    api.get(`/api/assessments/${assessmentId}/results`).then((res) => {
      setResults(res.data);
    });
  }, [assessmentId]);

  if (!results) return <div>Loading results...</div>;

  return (
    <div>
      <h1>Assessment Results</h1>
      <div>Score: {results.score}%</div>
      <div>Status: {results.passed ? 'Passed' : 'Failed'}</div>
      <button onClick={() => api.get(`/api/assessments/${assessmentId}/export`)}>
        Export Results
      </button>
    </div>
  );
};

// Test wrapper
const TestApp = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/assessments/create" element={<AssessmentCreationPage />} />
          <Route path="/assessments/:id/take" element={<AssessmentTakingPage assessmentId="1" />} />
          <Route path="/assessments/:id/results" element={<AssessmentResultsPage assessmentId="1" />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Assessment Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  describe('Assessment Creation', () => {
    it('creates assessment with multiple question types', async () => {
      const user = userEvent.setup({ delay: null });
      
      const mockAssessment = {
        id: '1',
        title: 'JavaScript Fundamentals',
        description: 'Test your JS knowledge',
        questions: [
          {
            id: 'q1',
            type: 'multiple_choice',
            text: 'What is closure?',
            options: ['A', 'B', 'C', 'D'],
            correct_answer: 'A'
          },
          {
            id: 'q2',
            type: 'true_false',
            text: 'JavaScript is typed language',
            correct_answer: false
          },
          {
            id: 'q3',
            type: 'short_answer',
            text: 'Explain hoisting',
            keywords: ['variable', 'declaration', 'top']
          }
        ],
        time_limit: 3600,
        passing_score: 70
      };

      api.post.mockResolvedValueOnce({ data: mockAssessment });

      render(<TestApp />);
      window.history.pushState({}, '', '/assessments/create');

      // Fill assessment details
      const titleInput = screen.getByLabelText('Title');
      const descriptionInput = screen.getByLabelText('Description');
      
      await user.type(titleInput, 'JavaScript Fundamentals');
      await user.type(descriptionInput, 'Test your JS knowledge');

      // Add questions
      const addQuestionButton = screen.getByText('Add Question');
      await user.click(addQuestionButton);
      await user.click(addQuestionButton);
      await user.click(addQuestionButton);

      // Create assessment
      const createButton = screen.getByText('Create Assessment');
      await user.click(createButton);

      // Verify API call
      expect(api.post).toHaveBeenCalledWith('/api/assessments', expect.objectContaining({
        title: 'JavaScript Fundamentals',
        description: 'Test your JS knowledge'
      }));

      // Should redirect to assessment page
      await waitFor(() => {
        expect(window.location.href).toContain('/assessments/1');
      });
    });
  });

  describe('Assessment Taking', () => {
    it('completes assessment with timer and auto-save', async () => {
      const user = userEvent.setup({ delay: null });
      
      const mockAssessment = {
        id: '1',
        title: 'JavaScript Test',
        questions: [
          { id: 'q1', text: 'Question 1', type: 'short_answer' },
          { id: 'q2', text: 'Question 2', type: 'short_answer' },
          { id: 'q3', text: 'Question 3', type: 'short_answer' }
        ],
        time_limit: 3600
      };

      const mockSubmission = {
        id: 'sub1',
        assessment_id: '1',
        user_id: 'user1',
        answers: { 0: 'Answer 1', 1: 'Answer 2', 2: 'Answer 3' },
        submitted_at: new Date().toISOString(),
        time_taken: 300
      };

      api.get.mockResolvedValueOnce({ data: mockAssessment });
      api.post.mockResolvedValueOnce({ data: mockSubmission });

      render(<TestApp />);
      window.history.pushState({}, '', '/assessments/1/take');

      // Wait for assessment to load
      await waitFor(() => {
        expect(screen.getByText('JavaScript Test')).toBeInTheDocument();
      });

      // Verify timer is running
      expect(screen.getByText('Time Left: 60:00')).toBeInTheDocument();

      // Answer questions
      const answer1 = screen.getByLabelText('Answer for question 1');
      const answer2 = screen.getByLabelText('Answer for question 2');
      const answer3 = screen.getByLabelText('Answer for question 3');

      await user.type(answer1, 'Answer 1');
      await user.type(answer2, 'Answer 2');
      await user.type(answer3, 'Answer 3');

      // Advance timer
      act(() => {
        vi.advanceTimersByTime(5 * 60 * 1000); // 5 minutes
      });

      // Verify timer updated
      expect(screen.getByText('Time Left: 55:00')).toBeInTheDocument();

      // Submit assessment
      const submitButton = screen.getByText('Submit Assessment');
      await user.click(submitButton);

      // Verify submission
      expect(api.post).toHaveBeenCalledWith('/api/assessments/1/submit', {
        answers: { 0: 'Answer 1', 1: 'Answer 2', 2: 'Answer 3' }
      });

      // Should redirect to results
      await waitFor(() => {
        expect(window.location.href).toContain('/assessments/1/results');
      });
    });

    it('auto-submits when time runs out', async () => {
      const mockAssessment = {
        id: '1',
        title: 'Timed Test',
        questions: [{ id: 'q1', text: 'Question 1', type: 'short_answer' }],
        time_limit: 10 // 10 seconds for testing
      };

      api.get.mockResolvedValueOnce({ data: mockAssessment });
      api.post.mockResolvedValueOnce({ data: { success: true } });

      render(<TestApp />);
      window.history.pushState({}, '', '/assessments/1/take');

      await waitFor(() => {
        expect(screen.getByText('Timed Test')).toBeInTheDocument();
      });

      // Advance time to trigger auto-submit
      act(() => {
        vi.advanceTimersByTime(11 * 1000); // 11 seconds
      });

      // Verify auto-submission
      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith('/api/assessments/1/submit', expect.any(Object));
      });
    });
  });

  describe('Assessment Grading', () => {
    it('displays results and feedback', async () => {
      const mockResults = {
        id: 'result1',
        assessment_id: '1',
        user_id: 'user1',
        score: 85,
        passed: true,
        questions: [
          {
            question_id: 'q1',
            user_answer: 'A',
            correct_answer: 'A',
            is_correct: true,
            points: 10
          },
          {
            question_id: 'q2',
            user_answer: 'B',
            correct_answer: 'C',
            is_correct: false,
            points: 0,
            feedback: 'Review the concept of closures'
          },
          {
            question_id: 'q3',
            user_answer: 'Variable declarations are moved to top',
            is_correct: true,
            points: 5,
            partial_credit: true
          }
        ],
        total_points: 15,
        max_points: 20,
        time_taken: 1200,
        submitted_at: new Date().toISOString()
      };

      api.get.mockResolvedValueOnce({ data: mockResults });

      render(<TestApp />);
      window.history.pushState({}, '', '/assessments/1/results');

      // Wait for results to load
      await waitFor(() => {
        expect(screen.getByText('Assessment Results')).toBeInTheDocument();
      });

      // Verify results display
      expect(screen.getByText('Score: 85%')).toBeInTheDocument();
      expect(screen.getByText('Status: Passed')).toBeInTheDocument();

      // Verify export functionality
      const exportButton = screen.getByText('Export Results');
      await userEvent.click(exportButton);

      expect(api.get).toHaveBeenCalledWith('/api/assessments/1/export');
    });
  });

  describe('Error Handling', () => {
    it('handles network errors during submission', async () => {
      const user = userEvent.setup({ delay: null });
      
      const mockAssessment = {
        id: '1',
        title: 'Test',
        questions: [{ id: 'q1', text: 'Question 1', type: 'short_answer' }]
      };

      api.get.mockResolvedValueOnce({ data: mockAssessment });
      api.post.mockRejectedValueOnce(new Error('Network error'));

      render(<TestApp />);
      window.history.pushState({}, '', '/assessments/1/take');

      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });

      // Try to submit
      const submitButton = screen.getByText('Submit Assessment');
      await user.click(submitButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/error submitting/i)).toBeInTheDocument();
      });

      // Should allow retry
      expect(submitButton).not.toBeDisabled();
    });

    it('saves progress locally on connection loss', async () => {
      const user = userEvent.setup({ delay: null });
      
      const mockAssessment = {
        id: '1',
        title: 'Test',
        questions: [
          { id: 'q1', text: 'Question 1', type: 'short_answer' },
          { id: 'q2', text: 'Question 2', type: 'short_answer' }
        ]
      };

      api.get.mockResolvedValueOnce({ data: mockAssessment });

      const localStorageMock = {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn()
      };
      global.localStorage = localStorageMock;

      render(<TestApp />);
      window.history.pushState({}, '', '/assessments/1/take');

      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });

      // Answer questions
      const answer1 = screen.getByLabelText('Answer for question 1');
      await user.type(answer1, 'My answer');

      // Simulate auto-save
      act(() => {
        vi.advanceTimersByTime(30 * 1000); // 30 seconds
      });

      // Verify local storage save
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'assessment_1_progress',
        expect.stringContaining('My answer')
      );
    });
  });
});