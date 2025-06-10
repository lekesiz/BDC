// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Award,
  Clock,
  Download,
  Printer,
  Share2,
  Loader,
  PieChart } from
'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
/**
 * PortalAssessmentResultsPage displays the results of a completed assessment
 */import { useTranslation } from "react-i18next";
const PortalAssessmentResultsPage = () => {const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [results, setResults] = useState(null);
  const [quiz, setQuiz] = useState(null);
  // Fetch assessment and results data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setErrorMessage(null);
        // Fetch assessment metadata
        const assessmentResponse = await api.get(`/api/portal/assessments/${id}`);
        setAssessment(assessmentResponse.data);
        // Fetch assessment results
        const resultsResponse = await api.get(`/api/portal/assessments/${id}/results`);
        setResults(resultsResponse.data);
        // Fetch quiz data to display questions and answers
        const quizResponse = await api.get(`/api/portal/quizzes/${id}`);
        setQuiz(quizResponse.data);
      } catch (error) {
        console.error('Error fetching assessment results:', error);
        setErrorMessage('Failed to load assessment results. Please try again later.');
        toast({
          title: 'Error',
          description: 'Failed to load assessment results',
          type: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [id, toast]);
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  // Format time spent
  const formatTimeSpent = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };
  // Get answer display for different question types
  const getAnswerDisplay = (question, answer) => {
    if (answer === undefined || answer === null) {
      return <span className="text-gray-500">{t("pages.not_answered")}</span>;
    }
    switch (question.type) {
      case 'multipleChoice':
        return <span>{question.options[answer]}</span>;
      case 'trueFalse':
        return <span>{answer ? 'True' : 'False'}</span>;
      case 'shortAnswer':
        return <span>{answer}</span>;
      case 'matching':
        return (
          <div className="space-y-1">
            {Object.entries(answer).map(([itemId, matchId]) => {
              const item = question.items.find((i) => i.id.toString() === itemId);
              return (
                <div key={itemId} className="flex">
                  <span className="font-medium mr-2">{item.text}:</span>
                  <span>{question.items[matchId]?.match || 'Invalid match'}</span>
                </div>);

            })}
          </div>);

      case 'multipleAnswer':
        return (
          <div className="space-y-1">
            {answer.map((optionIndex) =>
            <div key={optionIndex}>• {question.options[optionIndex]}</div>
            )}
          </div>);

      default:
        return <span>{JSON.stringify(answer)}</span>;
    }
  };
  // Check if an answer is correct
  const isAnswerCorrect = (question, answer) => {
    if (answer === undefined) return false;
    switch (question.type) {
      case 'multipleChoice':
        return answer === question.correctAnswer;
      case 'trueFalse':
        return answer === question.correctAnswer;
      case 'shortAnswer':
        if (Array.isArray(question.correctAnswer)) {
          return question.correctAnswer.some((ans) =>
          answer.toLowerCase().trim() === ans.toLowerCase().trim()
          );
        }
        return answer.toLowerCase().trim() === question.correctAnswer.toLowerCase().trim();
      case 'matching':
        return Object.keys(question.correctMatches).every(
          (itemId) => answer[itemId] === question.correctMatches[itemId]
        );
      case 'multipleAnswer':
        if (!answer || answer.length === 0) return false;
        if (answer.length !== question.correctAnswers.length) return false;
        return question.correctAnswers.every((ans) => answer.includes(ans)) &&
        answer.every((ans) => question.correctAnswers.includes(ans));
      default:
        return false;
    }
  };
  // Get correct answer display
  const getCorrectAnswerDisplay = (question) => {
    switch (question.type) {
      case 'multipleChoice':
        return <span>{question.options[question.correctAnswer]}</span>;
      case 'trueFalse':
        return <span>{question.correctAnswer ? 'True' : 'False'}</span>;
      case 'shortAnswer':
        if (Array.isArray(question.correctAnswer)) {
          return <span>{question.correctAnswer.join(' or ')}</span>;
        }
        return <span>{question.correctAnswer}</span>;
      case 'matching':
        return (
          <div className="space-y-1">
            {Object.entries(question.correctMatches).map(([itemId, matchId]) => {
              const item = question.items.find((i) => i.id.toString() === itemId);
              return (
                <div key={itemId} className="flex">
                  <span className="font-medium mr-2">{item.text}:</span>
                  <span>{question.items[matchId]?.match || 'Invalid match'}</span>
                </div>);

            })}
          </div>);

      case 'multipleAnswer':
        return (
          <div className="space-y-1">
            {question.correctAnswers.map((optionIndex) =>
            <div key={optionIndex}>• {question.options[optionIndex]}</div>
            )}
          </div>);

      default:
        return <span>N/A</span>;
    }
  };
  // Handle retry assessment
  const handleRetryAssessment = () => {
    navigate(`/portal/assessment/${id}`);
  };
  // Render loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>);

  }
  // Render error state
  if (errorMessage) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 max-w-lg mx-auto text-center">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">{t("pages.error_loading_results")}</h2>
          <p className="text-gray-600 mb-4">{errorMessage}</p>
          <Button onClick={() => navigate('/portal/assessment')}>{t("pages.back_to_assessments")}

          </Button>
        </Card>
      </div>);

  }
  const passingScore = assessment.passingScore || 0;
  const passed = results.score >= passingScore;
  return (
    <div className="container mx-auto py-6">
      {/* Page navigation */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/portal/assessment')}>

          <ArrowLeft className="h-4 w-4 mr-2" />{t("pages.back_to_assessments")}

        </Button>
      </div>
      {/* Results summary */}
      <Card className="p-6 mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">{assessment.title}{t("pages._results")}</h2>
            <p className="text-gray-600 mb-4">{assessment.description}</p>
            <div className="flex flex-wrap gap-4 mb-4">
              <div className="bg-gray-100 rounded-md px-3 py-2">
                <div className="text-sm text-gray-500">{t("components.completed")}</div>
                <div className="font-medium">{formatDate(results.completedAt)}</div>
              </div>
              <div className="bg-gray-100 rounded-md px-3 py-2">
                <div className="text-sm text-gray-500">{t("pages.time_spent")}</div>
                <div className="font-medium">{formatTimeSpent(results.timeSpent)}</div>
              </div>
              <div className="bg-gray-100 rounded-md px-3 py-2">
                <div className="text-sm text-gray-500">{t("pages.questions")}</div>
                <div className="font-medium">{results.correctCount} / {results.totalQuestions} correct</div>
              </div>
              <div className={`rounded-md px-3 py-2 ${
              passed ? 'bg-green-100' : 'bg-red-100'}`
              }>
                <div className={`text-sm ${passed ? 'text-green-600' : 'text-red-600'}`}>{t("components.status")}

                </div>
                <div className={`font-medium ${passed ? 'text-green-700' : 'text-red-700'}`}>
                  {passed ? 'Passed' : 'Failed'}
                </div>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-center">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center mb-2 ${
            passed ?
            'bg-green-100 text-green-700' :
            'bg-red-100 text-red-700'}`
            }>
              <div className="text-2xl font-bold">{results.score}%</div>
            </div>
            <div className="text-sm text-gray-500">{t("pages.passing_score")}
              {passingScore}%
            </div>
          </div>
        </div>
        {results.feedback &&
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-blue-800 mb-1">{t("pages.feedback")}</h3>
            <p className="text-blue-700">{results.feedback}</p>
          </div>
        }
        <div className="flex flex-wrap gap-2 mt-6">
          <Button variant="outline" onClick={handleRetryAssessment}>{t("pages.retry_assessment")}

          </Button>
          <Button variant="outline">
            <Printer className="h-4 w-4 mr-2" />{t("pages.print_results")}

          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />{t("pages.download_pdf")}

          </Button>
        </div>
      </Card>
      {/* Questions and answers review */}
      <h2 className="text-xl font-bold mb-4">{t("pages.review_questions")}</h2>
      <div className="space-y-6 mb-8">
        {quiz && quiz.questions.map((question, index) =>
        <Card key={index} className="overflow-hidden">
            <div className={`h-2 ${
          isAnswerCorrect(question, results.answers[index]) ?
          'bg-green-500' :
          'bg-red-500'}`
          }></div>
            <div className="p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
              isAnswerCorrect(question, results.answers[index]) ?
              'bg-green-100 text-green-600' :
              'bg-red-100 text-red-600'}`
              }>
                  {isAnswerCorrect(question, results.answers[index]) ?
                <CheckCircle className="h-4 w-4" /> :
                <XCircle className="h-4 w-4" />
                }
                </div>
                <div>
                  <h3 className="font-medium">{t("components.question")}{index + 1}</h3>
                  <p className="text-gray-700 mt-1">{question.question}</p>
                </div>
              </div>
              <div className="ml-9 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">{t("pages.your_answer")}</div>
                  <div className={`p-3 rounded-md ${
                isAnswerCorrect(question, results.answers[index]) ?
                'bg-green-50 border border-green-200' :
                'bg-red-50 border border-red-200'}`
                }>
                    {getAnswerDisplay(question, results.answers[index])}
                  </div>
                </div>
                {!isAnswerCorrect(question, results.answers[index]) &&
              <div>
                    <div className="text-sm font-medium text-gray-500 mb-1">{t("pages.correct_answer")}</div>
                    <div className="p-3 rounded-md bg-green-50 border border-green-200">
                      {getCorrectAnswerDisplay(question)}
                    </div>
                  </div>
              }
              </div>
              {question.explanation && !isAnswerCorrect(question, results.answers[index]) &&
            <div className="mt-4 ml-9 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <div className="text-sm font-medium text-blue-700 mb-1">{t("components.explanation")}</div>
                  <p className="text-blue-700 text-sm">{question.explanation}</p>
                </div>
            }
            </div>
          </Card>
        )}
      </div>
    </div>);

};
export default PortalAssessmentResultsPage;