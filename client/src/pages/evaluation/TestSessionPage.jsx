import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Clock, Save, CheckSquare, AlertTriangle, Loader } from 'lucide-react';
import api from '@/lib/api';
import { API_ENDPOINTS, QUESTION_TYPES, TEST_STATUS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import ConfirmationDialog from '@/components/ui/confirmation-dialog';

/**
 * TestSessionPage component for taking a test/evaluation
 */
const TestSessionPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [test, setTest] = useState(null);
  const [session, setSession] = useState({
    status: TEST_STATUS.IN_PROGRESS,
    responses: [],
    current_question: 0,
    started_at: new Date().toISOString(),
  });
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showExitConfirmation, setShowExitConfirmation] = useState(false);
  const [showSubmitConfirmation, setShowSubmitConfirmation] = useState(false);
  const intervalRef = useRef(null);

  // Fetch test details and create or resume a session
  useEffect(() => {
    const fetchTestAndCreateSession = async () => {
      try {
        setIsLoading(true);
        // Fetch test details
        const response = await api.get(API_ENDPOINTS.EVALUATIONS.DETAIL(id));
        setTest(response.data);
        
        // Check for existing session or create new one
        const existingSession = localStorage.getItem(`test_session_${id}`);
        
        if (existingSession) {
          const parsedSession = JSON.parse(existingSession);
          setSession(parsedSession);
          setCurrentQuestionIndex(parsedSession.current_question || 0);
        } else {
          // Initialize responses array with empty values
          const initialResponses = response.data.questions.map(() => ({
            question_id: null,
            response_data: null,
            is_answered: false,
          }));
          
          const newSession = {
            test_id: id,
            status: TEST_STATUS.IN_PROGRESS,
            responses: initialResponses,
            current_question: 0,
            started_at: new Date().toISOString(),
          };
          
          setSession(newSession);
          localStorage.setItem(`test_session_${id}`, JSON.stringify(newSession));
        }
        
        // Set time limit if applicable
        if (response.data.time_limit > 0) {
          const startTime = new Date(session.started_at || new Date().toISOString());
          const endTime = new Date(startTime.getTime() + response.data.time_limit * 60000);
          const now = new Date();
          
          if (now > endTime) {
            // Time already expired
            handleTimeExpired();
          } else {
            setTimeRemaining(Math.floor((endTime - now) / 1000));
          }
        }
      } catch (error) {
        console.error('Error fetching test:', error);
        toast({
          title: 'Error',
          description: 'Failed to load test',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchTestAndCreateSession();
    
    // Set up beforeunload event to warn about leaving
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [id]);

  // Set up timer for time limit
  useEffect(() => {
    if (timeRemaining !== null && timeRemaining > 0) {
      intervalRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            clearInterval(intervalRef.current);
            handleTimeExpired();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [timeRemaining]);

  // Format time remaining in MM:SS format
  const formatTimeRemaining = () => {
    if (timeRemaining === null) return '';
    
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  // Handle beforeunload event
  const handleBeforeUnload = (e) => {
    if (session?.status === TEST_STATUS.IN_PROGRESS) {
      e.preventDefault();
      e.returnValue = '';
      return '';
    }
  };

  // Handle time expired
  const handleTimeExpired = () => {
    toast({
      title: 'Time Expired',
      description: 'Your time for this test has expired. Your answers have been automatically submitted.',
      type: 'warning',
    });
    
    handleSubmitTest();
  };

  // Navigate to previous question
  const goToPrevious = () => {
    if (currentQuestionIndex > 0) {
      saveResponse();
      setCurrentQuestionIndex(prev => prev - 1);
      updateSession({ current_question: currentQuestionIndex - 1 });
    }
  };

  // Navigate to next question
  const goToNext = () => {
    if (test && currentQuestionIndex < test.questions.length - 1) {
      saveResponse();
      setCurrentQuestionIndex(prev => prev + 1);
      updateSession({ current_question: currentQuestionIndex + 1 });
    }
  };

  // Jump to a specific question
  const jumpToQuestion = (index) => {
    if (index >= 0 && index < test.questions.length) {
      saveResponse();
      setCurrentQuestionIndex(index);
      updateSession({ current_question: index });
    }
  };

  // Update response for current question
  const updateResponse = (responseData, isAnswered = true) => {
    if (!test) return;
    
    const updatedResponses = [...session.responses];
    updatedResponses[currentQuestionIndex] = {
      question_id: test.questions[currentQuestionIndex].id,
      response_data: responseData,
      is_answered: isAnswered,
    };
    
    setSession(prev => ({
      ...prev,
      responses: updatedResponses,
    }));
  };

  // Save current response to local storage
  const saveResponse = () => {
    if (!test) return;
    
    localStorage.setItem(`test_session_${id}`, JSON.stringify(session));
  };

  // Update session data
  const updateSession = (partialData) => {
    setSession(prev => {
      const updated = { ...prev, ...partialData };
      localStorage.setItem(`test_session_${id}`, JSON.stringify(updated));
      return updated;
    });
  };

  // Handle multiple choice selection
  const handleMultipleChoiceSelect = (optionIndex) => {
    updateResponse(optionIndex);
  };

  // Handle text answer change
  const handleTextAnswerChange = (e) => {
    updateResponse(e.target.value, e.target.value.trim() !== '');
  };

  // Handle true/false selection
  const handleTrueFalseSelect = (value) => {
    updateResponse(value);
  };

  // Handle matching selection
  const handleMatchingSelect = (leftIndex, rightValue) => {
    const currentMatches = session.responses[currentQuestionIndex]?.response_data || [];
    const updatedMatches = [...currentMatches];
    updatedMatches[leftIndex] = rightValue;
    
    // Check if all matches are selected
    const isAnswered = updatedMatches.length === test.questions[currentQuestionIndex].matches.length && 
                      !updatedMatches.includes(undefined);
    
    updateResponse(updatedMatches, isAnswered);
  };

  // Handle ordering selection
  const handleOrderingSelect = (position, itemIndex) => {
    const currentOrder = session.responses[currentQuestionIndex]?.response_data || [];
    const updatedOrder = [...currentOrder];
    
    // If this position already has an item, remove it
    const existingPosition = updatedOrder.findIndex(item => item === itemIndex);
    if (existingPosition !== -1) {
      updatedOrder[existingPosition] = null;
    }
    
    updatedOrder[position] = itemIndex;
    
    // Check if all positions are filled
    const isAnswered = updatedOrder.length === test.questions[currentQuestionIndex].order_items.length && 
                      !updatedOrder.includes(null) && 
                      !updatedOrder.includes(undefined);
    
    updateResponse(updatedOrder, isAnswered);
  };

  // Handle submit test
  const handleSubmitTest = async () => {
    try {
      setIsSubmitting(true);
      
      // Save any unsaved responses
      saveResponse();
      
      // Update session status
      updateSession({
        status: TEST_STATUS.COMPLETED,
        completed_at: new Date().toISOString(),
      });
      
      // Submit to server
      const response = await api.post(API_ENDPOINTS.EVALUATIONS.SESSIONS, {
        test_id: id,
        responses: session.responses,
        started_at: session.started_at,
        completed_at: new Date().toISOString(),
      });
      
      toast({
        title: 'Success',
        description: 'Your test has been submitted successfully',
        type: 'success',
      });
      
      // Clear session from localStorage
      localStorage.removeItem(`test_session_${id}`);
      
      // Navigate to results page
      navigate(`/evaluations/sessions/${response.data.id}/results`);
    } catch (error) {
      console.error('Error submitting test:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit test. Your responses have been saved locally.',
        type: 'error',
      });
      setIsSubmitting(false);
    }
  };

  // Handle exit test
  const handleExitTest = () => {
    // Save current progress
    saveResponse();
    
    // Navigate back to evaluations list
    navigate('/evaluations');
  };

  // Get current question
  const currentQuestion = test?.questions[currentQuestionIndex];
  const currentResponse = session?.responses[currentQuestionIndex];

  // Count answered questions
  const answeredCount = session?.responses?.filter(response => response.is_answered).length || 0;
  const totalQuestions = test?.questions?.length || 0;
  const progressPercentage = Math.round((answeredCount / totalQuestions) * 100) || 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  if (!test) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Test Not Found</h2>
          <p className="text-gray-600 mb-4">The requested test could not be found or has been deleted.</p>
          <Button onClick={() => navigate('/evaluations')}>Back to Tests</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 max-w-4xl">
      {/* Header */}
      <Card className="mb-4 p-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 className="text-xl font-bold">{test.title}</h1>
            <p className="text-sm text-gray-600 mt-1">
              {answeredCount} of {totalQuestions} questions answered ({progressPercentage}%)
            </p>
          </div>
          
          <div className="flex items-center space-x-4 mt-2 md:mt-0">
            {timeRemaining !== null && (
              <div className="flex items-center text-sm font-medium">
                <Clock className="w-4 h-4 mr-1 text-amber-500" />
                <span className={timeRemaining < 60 ? 'text-red-500 animate-pulse font-bold' : ''}>
                  {formatTimeRemaining()}
                </span>
              </div>
            )}
            
            <Button
              variant="outline"
              onClick={() => setShowExitConfirmation(true)}
              disabled={isSubmitting}
            >
              Save & Exit
            </Button>
            
            <Button
              onClick={() => setShowSubmitConfirmation(true)}
              disabled={isSubmitting}
              className="flex items-center"
            >
              {isSubmitting ? (
                <Loader className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <CheckSquare className="w-4 h-4 mr-2" />
              )}
              Submit Test
            </Button>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </Card>
      
      {/* Question navigation */}
      <div className="mb-4 grid grid-cols-8 sm:grid-cols-10 gap-2">
        {test.questions.map((question, index) => (
          <button
            key={index}
            onClick={() => jumpToQuestion(index)}
            className={`p-2 text-center rounded-md ${
              index === currentQuestionIndex
                ? 'bg-primary text-white'
                : session.responses[index]?.is_answered
                ? 'bg-green-100 text-green-800 border border-green-300'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
            aria-label={`Question ${index + 1}`}
          >
            {index + 1}
          </button>
        ))}
      </div>
      
      {/* Current question */}
      <Card className="p-6 mb-4">
        <div className="mb-4">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-medium">
              Question {currentQuestionIndex + 1} of {totalQuestions}
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({currentQuestion?.points || 0} {currentQuestion?.points === 1 ? 'point' : 'points'})
              </span>
            </h2>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={saveResponse}
                className="text-sm"
              >
                <Save className="w-3 h-3 mr-1" />
                Save
              </Button>
            </div>
          </div>
          
          <p className="text-gray-800">{currentQuestion?.question_text}</p>
        </div>
        
        {/* Question response area */}
        <div className="mt-6">
          {/* Multiple choice */}
          {currentQuestion?.question_type === QUESTION_TYPES.MULTIPLE_CHOICE && (
            <div className="space-y-2">
              {currentQuestion.options?.map((option, optionIndex) => (
                <label
                  key={optionIndex}
                  className={`flex items-start p-3 rounded-lg border ${
                    currentResponse?.response_data === optionIndex
                      ? 'border-primary bg-primary-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  } cursor-pointer transition-colors`}
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestionIndex}`}
                    className="mt-0.5 h-4 w-4 text-primary border-gray-300 focus:ring-primary"
                    checked={currentResponse?.response_data === optionIndex}
                    onChange={() => handleMultipleChoiceSelect(optionIndex)}
                  />
                  <span className={`ml-3 ${currentResponse?.response_data === optionIndex ? 'text-primary-900' : ''}`}>
                    {option.text}
                  </span>
                </label>
              ))}
            </div>
          )}
          
          {/* Text answer */}
          {currentQuestion?.question_type === QUESTION_TYPES.TEXT && (
            <div>
              <textarea
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary"
                rows="6"
                placeholder="Enter your answer here..."
                value={currentResponse?.response_data || ''}
                onChange={handleTextAnswerChange}
              ></textarea>
            </div>
          )}
          
          {/* True/False */}
          {currentQuestion?.question_type === QUESTION_TYPES.TRUE_FALSE && (
            <div className="space-y-2">
              <label
                className={`flex items-start p-3 rounded-lg border ${
                  currentResponse?.response_data === true
                    ? 'border-primary bg-primary-50'
                    : 'border-gray-200 hover:bg-gray-50'
                } cursor-pointer transition-colors`}
              >
                <input
                  type="radio"
                  name={`question-tf-${currentQuestionIndex}`}
                  className="mt-0.5 h-4 w-4 text-primary border-gray-300 focus:ring-primary"
                  checked={currentResponse?.response_data === true}
                  onChange={() => handleTrueFalseSelect(true)}
                />
                <span className={`ml-3 ${currentResponse?.response_data === true ? 'text-primary-900' : ''}`}>
                  True
                </span>
              </label>
              
              <label
                className={`flex items-start p-3 rounded-lg border ${
                  currentResponse?.response_data === false
                    ? 'border-primary bg-primary-50'
                    : 'border-gray-200 hover:bg-gray-50'
                } cursor-pointer transition-colors`}
              >
                <input
                  type="radio"
                  name={`question-tf-${currentQuestionIndex}`}
                  className="mt-0.5 h-4 w-4 text-primary border-gray-300 focus:ring-primary"
                  checked={currentResponse?.response_data === false}
                  onChange={() => handleTrueFalseSelect(false)}
                />
                <span className={`ml-3 ${currentResponse?.response_data === false ? 'text-primary-900' : ''}`}>
                  False
                </span>
              </label>
            </div>
          )}
          
          {/* Matching */}
          {currentQuestion?.question_type === QUESTION_TYPES.MATCHING && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h3 className="font-medium text-gray-700">Left Items</h3>
                {currentQuestion.matches?.map((match, leftIndex) => (
                  <div key={leftIndex} className="p-3 rounded-lg border border-gray-200 bg-white">
                    {match.left}
                  </div>
                ))}
              </div>
              
              <div className="space-y-3">
                <h3 className="font-medium text-gray-700">Right Items</h3>
                {currentQuestion.matches?.map((_, leftIndex) => (
                  <div key={leftIndex} className="p-3 rounded-lg border border-gray-200 bg-white">
                    <select
                      className="w-full bg-transparent focus:ring-0 border-0 p-0 focus:outline-none"
                      value={
                        Array.isArray(currentResponse?.response_data) && currentResponse.response_data[leftIndex] !== undefined
                          ? currentResponse.response_data[leftIndex]
                          : ''
                      }
                      onChange={(e) => handleMatchingSelect(leftIndex, e.target.value === '' ? undefined : parseInt(e.target.value))}
                    >
                      <option value="">Select a match</option>
                      {currentQuestion.matches?.map((match, rightIndex) => (
                        <option key={rightIndex} value={rightIndex}>
                          {match.right}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Ordering */}
          {currentQuestion?.question_type === QUESTION_TYPES.ORDERING && (
            <div className="space-y-3">
              <h3 className="font-medium text-gray-700">Arrange items in the correct order:</h3>
              {currentQuestion.order_items?.map((_, position) => (
                <div key={position} className="flex items-center p-3 rounded-lg border border-gray-200 bg-white">
                  <span className="mr-3 text-gray-500 font-medium">{position + 1}</span>
                  <select
                    className="w-full bg-transparent focus:ring-0 border-0 p-0 focus:outline-none"
                    value={
                      Array.isArray(currentResponse?.response_data) && currentResponse.response_data[position] !== undefined
                        ? currentResponse.response_data[position]
                        : ''
                    }
                    onChange={(e) => handleOrderingSelect(position, e.target.value === '' ? undefined : parseInt(e.target.value))}
                  >
                    <option value="">Select an item</option>
                    {currentQuestion.order_items?.map((item, itemIndex) => (
                      <option key={itemIndex} value={itemIndex}>
                        {item.text}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
      
      {/* Navigation buttons */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={goToPrevious}
          disabled={currentQuestionIndex === 0}
          className="flex items-center"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </Button>
        
        <div className="text-sm text-gray-500">
          Question {currentQuestionIndex + 1} of {totalQuestions}
        </div>
        
        {currentQuestionIndex < totalQuestions - 1 ? (
          <Button
            onClick={goToNext}
            className="flex items-center"
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        ) : (
          <Button
            onClick={() => setShowSubmitConfirmation(true)}
            className="flex items-center"
          >
            <CheckSquare className="w-4 h-4 mr-2" />
            Submit Test
          </Button>
        )}
      </div>
      
      {/* Exit Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showExitConfirmation}
        onClose={() => setShowExitConfirmation(false)}
        onConfirm={handleExitTest}
        title="Exit Test"
        description="Are you sure you want to exit? Your progress will be saved, and you can resume later."
        confirmText="Save & Exit"
        cancelText="Continue Test"
      />
      
      {/* Submit Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showSubmitConfirmation}
        onClose={() => setShowSubmitConfirmation(false)}
        onConfirm={handleSubmitTest}
        title="Submit Test"
        description={`Are you sure you want to submit? You have answered ${answeredCount} out of ${totalQuestions} questions. Once submitted, you cannot make changes.`}
        confirmText="Submit Test"
        cancelText="Continue Test"
        isDanger={answeredCount < totalQuestions}
      />
    </div>
  );
};

export default TestSessionPage;