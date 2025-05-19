import { EVALUATION_STATUS, QUESTION_TYPES } from '@/lib/constants';
import { 
  mockAnalysisData, 
  getMockAnalysis, 
  generateMockAnalysis,
  updateMockAnalysisStatus,
  updateMockTrainerFeedback 
} from './mockAnalysisData';
import {
  mockTrainerEvaluations,
  fetchMockTrainerEvaluations,
  fetchMockTrainerEvaluation,
  createMockTrainerEvaluation,
  shareMockTrainerEvaluation,
  downloadMockTrainerEvaluationPDF
} from './mockTrainerEvaluationsData';
import {
  mockAppointments,
  fetchMockAppointments,
  fetchMockAppointment,
  createMockAppointment,
  updateMockAppointment,
  deleteMockAppointment,
  notifyMockParticipants,
  fetchMockAvailability,
  updateMockAvailability,
  fetchMockGoogleCalendarSync,
  updateMockGoogleCalendarSync
} from '../appointment/mockAppointmentsData';

// Sample evaluations data for development and testing
export const mockEvaluations = [
  {
    id: 1,
    title: 'Communication Skills Assessment',
    description: 'A comprehensive test to evaluate verbal and written communication skills.',
    instructions: 'Answer all questions to the best of your ability. There is no time limit for this test.',
    passing_score: 70,
    time_limit: 0,
    skills: ['Communication', 'Leadership'],
    status: EVALUATION_STATUS.ACTIVE,
    questions: [
      {
        id: 1,
        question_text: 'Which of the following is most important for effective communication?',
        question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
        points: 2,
        options: [
          { text: 'Speaking loudly', is_correct: false },
          { text: 'Using complex vocabulary', is_correct: false },
          { text: 'Active listening', is_correct: true },
          { text: 'Quick responses', is_correct: false },
        ],
      },
      {
        id: 2,
        question_text: 'True or False: Non-verbal cues are less important than verbal communication.',
        question_type: QUESTION_TYPES.TRUE_FALSE,
        points: 1,
        options: [
          { text: 'True', is_correct: false },
          { text: 'False', is_correct: true },
        ],
      },
    ],
  },
  {
    id: 2,
    title: 'Problem Solving Abilities',
    description: 'This test evaluates your critical thinking and problem-solving strategies.',
    instructions: 'Read each scenario carefully before selecting your answer. You have 45 minutes to complete this test.',
    passing_score: 75,
    time_limit: 45,
    skills: ['Problem Solving', 'Critical Thinking'],
    status: EVALUATION_STATUS.DRAFT,
    questions: [
      {
        id: 3,
        question_text: 'A team is consistently missing deadlines. What should be the first step in addressing this issue?',
        question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
        points: 2,
        options: [
          { text: 'Replace team members', is_correct: false },
          { text: 'Extend all future deadlines', is_correct: false },
          { text: 'Identify the root causes of delays', is_correct: true },
          { text: 'Implement stricter oversight', is_correct: false },
        ],
      },
    ],
  },
  {
    id: 3,
    title: 'Technical Skills Assessment',
    description: 'Evaluation of fundamental technical skills required for the position.',
    instructions: 'This test includes multiple-choice questions and practical exercises. Complete all sections.',
    passing_score: 80,
    time_limit: 60,
    skills: ['Technical Skills', 'Problem Solving'],
    status: EVALUATION_STATUS.ARCHIVED,
    questions: [
      {
        id: 4,
        question_text: 'Match the following technologies with their primary uses:',
        question_type: QUESTION_TYPES.MATCHING,
        points: 3,
        matches: [
          { left: 'JavaScript', right: 'Web interactivity' },
          { left: 'SQL', right: 'Database management' },
          { left: 'Python', right: 'Data analysis' },
          { left: 'HTML', right: 'Web structure' },
        ],
      },
    ],
  },
];

// Mock data for test sessions
export const mockSessions = [
  {
    id: 1,
    test_id: 1,
    user_id: 1,
    started_at: '2023-06-15T14:30:00Z',
    completed_at: '2023-06-15T15:15:00Z',
    status: 'completed',
    score: 85,
    responses: [
      {
        question_id: 1,
        response_data: 2, // Index of selected option
        is_correct: true,
        points: 2,
        explanation: 'Active listening is essential for effective communication as it ensures that the message is properly understood and the speaker feels heard and valued.',
      },
      {
        question_id: 2,
        response_data: false, // False selected
        is_correct: true,
        points: 1,
        explanation: 'Non-verbal cues such as body language, facial expressions, and tone of voice are crucial components of effective communication and often convey more meaning than words alone.',
      },
    ],
  }
];

// Mock feedback data
export const mockFeedback = {
  overall_assessment: 'You demonstrated good communication skills with particular strength in understanding the importance of active listening. Your responses indicate a solid grasp of both verbal and non-verbal communication principles.',
  strengths: [
    'Strong understanding of active listening as a key component of effective communication',
    'Good recognition of the importance of non-verbal cues in communication',
  ],
  areas_for_improvement: [
    'Further development in understanding complex communication scenarios',
    'More practice in distinguishing between different communication strategies',
  ],
  recommendations: [
    'Practice active listening techniques in daily conversations',
    'Observe and analyze non-verbal cues in professional settings',
    'Consider taking the advanced communication course for more in-depth learning',
  ],
  skill_feedback: {
    'Communication': 'Your communication skills are above average. You understand core concepts but could benefit from practical application.',
    'Leadership': 'Your leadership communication shows promise. Focus on developing more advanced techniques for team communication.',
  }
};

// Mock API responses
export const mockApiResponses = {
  getEvaluations: () => {
    return {
      status: 200,
      data: {
        items: mockEvaluations,
        total: mockEvaluations.length,
        page: 1,
        per_page: 10
      },
    };
  },
  
  getEvaluation: (id) => {
    const evaluation = mockEvaluations.find(e => e.id === parseInt(id));
    
    if (evaluation) {
      return {
        status: 200,
        data: evaluation,
      };
    }
    
    return {
      status: 404,
      data: { message: 'Evaluation not found' },
    };
  },
  
  createEvaluation: (data) => {
    // In a real implementation, this would add to the database
    return {
      status: 201,
      data: {
        ...data,
        id: mockEvaluations.length + 1,
        created_at: new Date().toISOString(),
      },
    };
  },
  
  updateEvaluation: (id, data) => {
    const evaluation = mockEvaluations.find(e => e.id === parseInt(id));
    
    if (evaluation) {
      return {
        status: 200,
        data: {
          ...evaluation,
          ...data,
          updated_at: new Date().toISOString(),
        },
      };
    }
    
    return {
      status: 404,
      data: { message: 'Evaluation not found' },
    };
  },
  
  deleteEvaluation: (id) => {
    const evaluation = mockEvaluations.find(e => e.id === parseInt(id));
    
    if (evaluation) {
      return {
        status: 204,
        data: null,
      };
    }
    
    return {
      status: 404,
      data: { message: 'Evaluation not found' },
    };
  },

  // Session API responses
  getSession: (id) => {
    const session = mockSessions.find(s => s.id === parseInt(id));
    
    if (session) {
      return {
        status: 200,
        data: session,
      };
    }
    
    return {
      status: 404,
      data: { message: 'Session not found' },
    };
  },
  
  createSession: (data) => {
    return {
      status: 201,
      data: {
        ...data,
        id: mockSessions.length + 1,
        status: 'completed',
        score: 85, // Mock score
      },
    };
  },
  
  getFeedback: (id) => {
    // In a real app, this would retrieve feedback specific to the session
    return {
      status: 200,
      data: mockFeedback,
    };
  },
};

// This function can be used to intercept API calls during development
export const setupMockApi = (api) => {
  // Store the original get/post/put/delete methods
  const originalGet = api.get;
  const originalPost = api.post;
  const originalPut = api.put;
  const originalDelete = api.delete;

  // Mock API endpoints
  api.get = function(url, config) {
    // Evaluations list
    if (url === '/api/evaluations') {
      return Promise.resolve(mockApiResponses.getEvaluations());
    }
    
    // Analysis report download (return empty blob)
    if (url.includes('/analysis/report')) {
      return Promise.resolve({
        status: 200,
        data: new Blob(['Mock Analysis PDF content'], { type: 'application/pdf' }),
      });
    }
    
    // Appointments list
    const appointmentsMatch = url.match(/\/api\/appointments/);
    if (appointmentsMatch && !url.includes('/api/appointments/')) {
      // Get query parameters
      const urlObj = new URL(url, 'http://example.com');
      const start = urlObj.searchParams.get('start');
      const end = urlObj.searchParams.get('end');
      
      return Promise.resolve(fetchMockAppointments(start, end));
    }
    
    // Appointment detail
    const appointmentDetailMatch = url.match(/\/api\/appointments\/(\d+)$/);
    if (appointmentDetailMatch) {
      return Promise.resolve(fetchMockAppointment(appointmentDetailMatch[1]));
    }
    
    // Trainer evaluations list for a beneficiary
    const trainerEvaluationsMatch = url.match(/\/api\/beneficiaries\/(\d+)\/evaluations/);
    if (trainerEvaluationsMatch) {
      return Promise.resolve(fetchMockTrainerEvaluations(trainerEvaluationsMatch[1]));
    }
    
    // Trainer evaluation detail
    const trainerEvaluationMatch = url.match(/\/api\/trainer-evaluations\/(\d+)$/);
    if (trainerEvaluationMatch) {
      return Promise.resolve(fetchMockTrainerEvaluation(trainerEvaluationMatch[1]));
    }
    
    // Trainer evaluation PDF download
    const evaluationPdfMatch = url.match(/\/api\/trainer-evaluations\/(\d+)\/pdf/);
    if (evaluationPdfMatch) {
      return Promise.resolve(downloadMockTrainerEvaluationPDF());
    }
    
    // AI Analysis for a session
    const analysisMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)\/analysis/);
    if (analysisMatch) {
      return Promise.resolve(getMockAnalysis(analysisMatch[1]));
    }
    
    // Evaluation session feedback
    const feedbackMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)\/feedback/);
    if (feedbackMatch) {
      return Promise.resolve(mockApiResponses.getFeedback(feedbackMatch[1]));
    }
    
    // Availability settings
    if (url === '/api/availability') {
      return Promise.resolve(fetchMockAvailability());
    }
    
    // Google Calendar sync settings
    if (url === '/api/calendar/google-sync') {
      return Promise.resolve(fetchMockGoogleCalendarSync());
    }
    
    // Certificate and report downloads (return empty blob)
    if (url.includes('/certificate') || url.includes('/report')) {
      return Promise.resolve({
        status: 200,
        data: new Blob(['Mock PDF content'], { type: 'application/pdf' }),
      });
    }
    
    // Evaluation session
    const sessionMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)$/);
    if (sessionMatch) {
      return Promise.resolve(mockApiResponses.getSession(sessionMatch[1]));
    }
    
    // Evaluation detail
    const evaluationDetailMatch = url.match(/\/api\/evaluations\/(\d+)/);
    if (evaluationDetailMatch) {
      return Promise.resolve(mockApiResponses.getEvaluation(evaluationDetailMatch[1]));
    }
    
    // Fallback to original implementation
    return originalGet.call(this, url, config);
  };
  
  api.post = function(url, data, config) {
    // Create appointment
    if (url === '/api/appointments') {
      return Promise.resolve(createMockAppointment(data));
    }
    
    // Notify appointment participants
    const notifyParticipantsMatch = url.match(/\/api\/appointments\/(\d+)\/notify/);
    if (notifyParticipantsMatch) {
      return Promise.resolve(notifyMockParticipants(notifyParticipantsMatch[1]));
    }
    
    // Create trainer evaluation
    if (url === '/api/trainer-evaluations') {
      return Promise.resolve(createMockTrainerEvaluation(data));
    }
    
    // Share trainer evaluation with beneficiary
    const shareEvaluationMatch = url.match(/\/api\/trainer-evaluations\/(\d+)\/share/);
    if (shareEvaluationMatch) {
      return Promise.resolve(shareMockTrainerEvaluation(shareEvaluationMatch[1]));
    }
    
    // Generate AI analysis
    const generateAnalysisMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)\/generate-analysis/);
    if (generateAnalysisMatch) {
      return Promise.resolve(generateMockAnalysis());
    }
    
    // Create evaluation
    if (url === '/api/evaluations') {
      return Promise.resolve(mockApiResponses.createEvaluation(data));
    }
    
    // Create session
    if (url === '/api/evaluations/sessions') {
      return Promise.resolve(mockApiResponses.createSession(data));
    }
    
    // Fallback to original implementation
    return originalPost.call(this, url, data, config);
  };
  
  api.put = function(url, data, config) {
    // Update appointment
    const updateAppointmentMatch = url.match(/\/api\/appointments\/(\d+)/);
    if (updateAppointmentMatch) {
      return Promise.resolve(updateMockAppointment(updateAppointmentMatch[1], data));
    }
    
    // Mark session as evaluated by trainer
    const markEvaluatedMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)\/mark-evaluated/);
    if (markEvaluatedMatch) {
      return Promise.resolve({
        status: 200,
        data: {
          id: markEvaluatedMatch[1],
          trainer_evaluated: true,
          updated_at: new Date().toISOString()
        }
      });
    }
    
    // Update analysis status
    const analysisStatusMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)\/analysis\/status/);
    if (analysisStatusMatch) {
      return Promise.resolve(updateMockAnalysisStatus(analysisStatusMatch[1], data));
    }
    
    // Update trainer feedback
    const trainerFeedbackMatch = url.match(/\/api\/evaluations\/sessions\/(\d+)\/analysis\/trainer-feedback/);
    if (trainerFeedbackMatch) {
      return Promise.resolve(updateMockTrainerFeedback(trainerFeedbackMatch[1], data));
    }
    
    // Update evaluation 
    const evaluationDetailMatch = url.match(/\/api\/evaluations\/(\d+)/);
    if (evaluationDetailMatch) {
      return Promise.resolve(mockApiResponses.updateEvaluation(evaluationDetailMatch[1], data));
    }
    
    // Update availability settings
    if (url === '/api/availability') {
      return Promise.resolve(updateMockAvailability(data));
    }
    
    // Update Google Calendar sync settings
    if (url === '/api/calendar/google-sync') {
      return Promise.resolve(updateMockGoogleCalendarSync(data));
    }
    
    // Fallback to original implementation
    return originalPut.call(this, url, data, config);
  };
  
  api.delete = function(url, config) {
    // Delete appointment
    const deleteAppointmentMatch = url.match(/\/api\/appointments\/(\d+)/);
    if (deleteAppointmentMatch) {
      return Promise.resolve(deleteMockAppointment(deleteAppointmentMatch[1]));
    }
    
    // Delete evaluation
    const evaluationDetailMatch = url.match(/\/api\/evaluations\/(\d+)/);
    if (evaluationDetailMatch) {
      return Promise.resolve(mockApiResponses.deleteEvaluation(evaluationDetailMatch[1]));
    }
    
    // Fallback to original implementation
    return originalDelete.call(this, url, config);
  };
  
  return () => {
    // Restore original methods when needed
    api.get = originalGet;
    api.post = originalPost;
    api.put = originalPut;
    api.delete = originalDelete;
  };
};