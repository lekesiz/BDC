import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader, AlertTriangle, Clock, CheckCircle, AlertCircle, Info } from 'lucide-react';
import axios from '../../../lib/api';
import { Button } from '../../../components/ui/button';
import { Card } from '../../../components/ui/card';
import { Alert } from '../../../components/ui/alert';
import { Badge } from '../../../components/ui/badge';
import { toast } from '../../../hooks/useToast';
import Quiz from '../../../components/portal/assessment/Quiz';

/**
 * PortalQuizPage handles the quiz-taking experience with improved UX
 */
const PortalQuizPage = () => {
  const { assessmentId, assignmentId } = useParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(true);
  const [quizStarted, setQuizStarted] = useState(false);
  const [previousAttempt, setPreviousAttempt] = useState(null);
  
  // Fetch assessment and quiz data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);
        
        // Fetch assessment metadata and quiz data
        const [assessmentRes, quizRes, attemptRes] = await Promise.all([
          axios.get(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}`),
          axios.get(`/api/portal/assessments/${assessmentId}/quiz`),
          axios.get(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/last-attempt`)
        ]);
        
        setAssessment(assessmentRes.data);
        setQuizData(quizRes.data);
        setPreviousAttempt(attemptRes.data);
        
        // If there's an incomplete attempt, resume it
        if (attemptRes.data?.status === 'in_progress') {
          setShowConfirmation(false);
          setQuizStarted(true);
        }
      } catch (error) {
        console.error('Error fetching quiz data:', error);
        setErrorMessage('Failed to load quiz data. Please try again later.');
        toast({
          title: 'Error',
          description: 'Failed to load quiz data',
          variant: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [assessmentId, assignmentId]);
  
  // Handle quiz start
  const handleStartQuiz = async () => {
    try {
      // Initiate quiz attempt
      await axios.post(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/start`);
      setShowConfirmation(false);
      setQuizStarted(true);
    } catch (error) {
      console.error('Error starting quiz:', error);
      toast({
        title: 'Error',
        description: 'Failed to start quiz',
        variant: 'error',
      });
    }
  };
  
  // Handle quiz completion
  const handleQuizComplete = async (results) => {
    try {
      // Submit results to server
      await axios.post(`/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/submit`, results);
      
      // Show success message
      toast({
        title: 'Success',
        description: 'Quiz completed successfully',
        variant: 'success',
      });
      
      // Navigate to results page
      navigate(`/portal/assessments/results/${assessmentId}/${assignmentId}`);
    } catch (error) {
      console.error('Error submitting quiz results:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit quiz results',
        variant: 'error',
      });
    }
  };
  
  // Handle exit quiz
  const handleExitQuiz = () => {
    if (quizStarted) {
      const confirmExit = window.confirm('Are you sure you want to exit? Your progress will be saved.');
      if (confirmExit) {
        navigate('/portal/assessments');
      }
    } else {
      navigate('/portal/assessments');
    }
  };
  
  // Render loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-blue-600 animate-spin" />
      </div>
    );
  }
  
  // Render error state
  if (errorMessage) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 max-w-lg mx-auto text-center">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Error Loading Quiz</h2>
          <p className="text-gray-600 mb-4">{errorMessage}</p>
          <Button onClick={() => navigate('/portal/assessments')}>
            Back to Assessments
          </Button>
        </Card>
      </div>
    );
  }
  
  // Render confirmation screen
  if (showConfirmation && !quizStarted) {
    const attemptsUsed = previousAttempt?.attemptNumber || 0;
    const attemptsRemaining = assessment.attemptsAllowed - attemptsUsed;
    const canRetake = attemptsRemaining > 0;
    
    return (
      <div className="container mx-auto py-6 px-4 max-w-4xl">
        <Card className="p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-2">{assessment.title}</h1>
            <p className="text-gray-600">{assessment.description}</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Quiz Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-3">Quiz Details</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium">Questions</p>
                    <p className="text-sm text-gray-600">{quizData.questions.length} questions</p>
                  </div>
                </div>
                
                {assessment.timeLimit && (
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                      <Clock className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">Time Limit</p>
                      <p className="text-sm text-gray-600">{Math.floor(assessment.timeLimit / 60)} minutes</p>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="font-medium">Passing Score</p>
                    <p className="text-sm text-gray-600">{assessment.passingScore}%</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                    <Info className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="font-medium">Attempts</p>
                    <p className="text-sm text-gray-600">
                      {attemptsUsed} of {assessment.attemptsAllowed} used
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Instructions */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold mb-3">Instructions</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Navigate between questions using Previous and Next buttons</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Your progress is automatically saved as you answer</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>You can flag questions to review later</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Review all answers before submitting</span>
                </li>
                {assessment.timeLimit && (
                  <li className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    <span>Timer starts when you begin the quiz</span>
                  </li>
                )}
              </ul>
            </div>
          </div>
          
          {/* Previous Attempt Info */}
          {previousAttempt && previousAttempt.status === 'completed' && (
            <Alert className="mb-6">
              <Info className="h-4 w-4" />
              <div>
                <h4 className="font-semibold">Previous Attempt</h4>
                <p>
                  Score: {previousAttempt.score}% • 
                  Completed: {new Date(previousAttempt.completedAt).toLocaleDateString()}
                </p>
              </div>
            </Alert>
          )}
          
          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 justify-between">
            <Button 
              variant="outline" 
              onClick={handleExitQuiz}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Assessments
            </Button>
            
            {canRetake ? (
              <Button 
                onClick={handleStartQuiz}
                size="lg"
              >
                {previousAttempt?.status === 'in_progress' ? 'Resume Quiz' : 'Start Quiz'}
              </Button>
            ) : (
              <div className="text-right">
                <Badge variant="error" className="mb-2">No attempts remaining</Badge>
                <p className="text-sm text-gray-600">
                  You've used all available attempts for this quiz.
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>
    );
  }
  
  // Render quiz component with improved props
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="sticky top-0 z-50 bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{assessment.title}</h2>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleExitQuiz}
            >
              Save & Exit
            </Button>
          </div>
        </div>
      </div>
      
      <div className="container mx-auto py-6 px-4 max-w-4xl">
        <Quiz 
          quizData={quizData}
          assessment={assessment}
          previousAttempt={previousAttempt}
          onComplete={handleQuizComplete}
          onExit={handleExitQuiz}
          onSaveProgress={async (progress) => {
            try {
              await axios.post(
                `/api/portal/assessments/${assessmentId}/assignments/${assignmentId}/save-progress`,
                progress
              );
            } catch (error) {
              console.error('Error saving progress:', error);
            }
          }}
          timedMode={Boolean(assessment.timeLimit)}
          timeLimit={assessment.timeLimit}
        />
      </div>
    </div>
  );
};

export default PortalQuizPage;