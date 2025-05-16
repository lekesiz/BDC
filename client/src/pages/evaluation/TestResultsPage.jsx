import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, CheckCircle, XCircle, Award, Clock, BarChart2, FileText, Info, Brain } from 'lucide-react';
import { API_ENDPOINTS, QUESTION_TYPES } from '@/lib/constants';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/toast';

/**
 * TestResultsPage displays the results of a completed test session
 */
const TestResultsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [test, setTest] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch session details
  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch session data
        const sessionResponse = await api.get(API_ENDPOINTS.EVALUATIONS.SESSION(id));
        setSession(sessionResponse.data);
        
        // Fetch test data
        const testResponse = await api.get(API_ENDPOINTS.EVALUATIONS.DETAIL(sessionResponse.data.test_id));
        setTest(testResponse.data);
        
        // Fetch AI feedback if available
        try {
          const feedbackResponse = await api.get(API_ENDPOINTS.EVALUATIONS.FEEDBACK(id));
          setFeedback(feedbackResponse.data);
        } catch (error) {
          console.log('Feedback not available yet');
        }
      } catch (error) {
        console.error('Error fetching session data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load test results',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessionData();
  }, [id, toast]);

  // Calculate score and statistics
  const calculateStats = () => {
    if (!session || !test) return null;
    
    const totalQuestions = test.questions.length;
    const totalPoints = test.questions.reduce((sum, q) => sum + q.points, 0);
    const correctAnswers = session.responses.filter(r => r.is_correct).length;
    const earnedPoints = session.responses.reduce((sum, r) => sum + (r.is_correct ? r.points : 0), 0);
    const scorePercentage = Math.round((earnedPoints / totalPoints) * 100);
    const isPassing = scorePercentage >= test.passing_score;
    
    // Calculate time taken
    const startTime = new Date(session.started_at);
    const endTime = new Date(session.completed_at);
    const timeTakenMs = endTime - startTime;
    const timeTakenMinutes = Math.floor(timeTakenMs / 60000);
    const timeTakenSeconds = Math.floor((timeTakenMs % 60000) / 1000);
    
    // Calculate per skill performance
    const skillPerformance = {};
    
    test.skills.forEach(skill => {
      skillPerformance[skill] = {
        total: 0,
        earned: 0,
        percentage: 0,
      };
    });
    
    // Assume each question has skills assigned to it
    test.questions.forEach((question, index) => {
      const response = session.responses[index];
      const questionSkills = question.skills || test.skills; // Fallback to test skills if question doesn't have specific skills
      
      questionSkills.forEach(skill => {
        if (skillPerformance[skill]) {
          skillPerformance[skill].total += question.points;
          if (response && response.is_correct) {
            skillPerformance[skill].earned += question.points;
          }
        }
      });
    });
    
    // Calculate percentages for each skill
    Object.keys(skillPerformance).forEach(skill => {
      if (skillPerformance[skill].total > 0) {
        skillPerformance[skill].percentage = Math.round(
          (skillPerformance[skill].earned / skillPerformance[skill].total) * 100
        );
      }
    });
    
    return {
      totalQuestions,
      totalPoints,
      correctAnswers,
      earnedPoints,
      scorePercentage,
      isPassing,
      timeTakenMinutes,
      timeTakenSeconds,
      skillPerformance,
    };
  };

  const stats = calculateStats();

  // Handle downloading certificate
  const handleDownloadCertificate = async () => {
    try {
      const response = await api.get(`/api/evaluations/sessions/${id}/certificate`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading certificate:', error);
      toast({
        title: 'Error',
        description: 'Failed to download certificate',
        type: 'error',
      });
    }
  };

  // Handle downloading full report
  const handleDownloadReport = async () => {
    try {
      const response = await api.get(`/api/evaluations/sessions/${id}/report`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `test-report-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading report:', error);
      toast({
        title: 'Error',
        description: 'Failed to download report',
        type: 'error',
      });
    }
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Render error state if no session or test data
  if (!session || !test) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <div className="text-red-500 mb-4">
            <XCircle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Results Not Found</h2>
          <p className="text-gray-600 mb-4">The requested test results could not be found or have been deleted.</p>
          <Button onClick={() => navigate('/evaluations')}>Back to Tests</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/evaluations')}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Tests
          </Button>
          <h1 className="text-2xl font-bold">{test.title} - Results</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          {stats && stats.isPassing && (
            <Button
              variant="outline"
              onClick={handleDownloadCertificate}
              className="flex items-center"
            >
              <Award className="w-4 h-4 mr-2" />
              Certificate
            </Button>
          )}
          
          <Button
            variant="outline"
            onClick={handleDownloadReport}
            className="flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Download Report
          </Button>
          
          {/* Only show for trainers and admins */}
          {/* In a real app, this would be conditionally rendered based on user role */}
          <Button
            onClick={() => navigate(`/evaluations/sessions/${id}/analysis`)}
            className="flex items-center"
          >
            <Brain className="w-4 h-4 mr-2" />
            AI Analysis
          </Button>
        </div>
      </div>
      
      {/* Result overview card */}
      {stats && (
        <Card className="mb-6 overflow-hidden">
          <div className={`p-4 text-white ${stats.isPassing ? 'bg-green-600' : 'bg-amber-600'}`}>
            <div className="flex items-center">
              {stats.isPassing ? (
                <CheckCircle className="w-6 h-6 mr-2" />
              ) : (
                <Info className="w-6 h-6 mr-2" />
              )}
              <h2 className="text-lg font-semibold">
                {stats.isPassing
                  ? `Congratulations! You passed with ${stats.scorePercentage}%`
                  : `You scored ${stats.scorePercentage}%. The passing score is ${test.passing_score}%`}
              </h2>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex items-center">
                <Award className="w-8 h-8 text-primary mr-4" />
                <div>
                  <p className="text-sm text-gray-600">Score</p>
                  <p className="text-xl font-bold">
                    {stats.earnedPoints} / {stats.totalPoints} points
                  </p>
                  <p className="text-sm text-gray-600">
                    {stats.scorePercentage}%
                  </p>
                </div>
              </div>
              
              <div className="flex items-center">
                <CheckCircle className="w-8 h-8 text-green-500 mr-4" />
                <div>
                  <p className="text-sm text-gray-600">Correct Answers</p>
                  <p className="text-xl font-bold">
                    {stats.correctAnswers} / {stats.totalQuestions}
                  </p>
                  <p className="text-sm text-gray-600">
                    {Math.round((stats.correctAnswers / stats.totalQuestions) * 100)}%
                  </p>
                </div>
              </div>
              
              <div className="flex items-center">
                <Clock className="w-8 h-8 text-blue-500 mr-4" />
                <div>
                  <p className="text-sm text-gray-600">Time Taken</p>
                  <p className="text-xl font-bold">
                    {stats.timeTakenMinutes}m {stats.timeTakenSeconds}s
                  </p>
                  <p className="text-sm text-gray-600">
                    {test.time_limit ? `Out of ${test.time_limit}m limit` : 'No time limit'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
      
      {/* Tabs for results */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList>
          <Tabs.TabTrigger value="overview">
            <BarChart2 className="w-4 h-4 mr-2" />
            Performance Overview
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="questions">
            <FileText className="w-4 h-4 mr-2" />
            Question Review
          </Tabs.TabTrigger>
          {feedback && (
            <Tabs.TabTrigger value="feedback">
              <Info className="w-4 h-4 mr-2" />
              AI Feedback
            </Tabs.TabTrigger>
          )}
        </Tabs.TabsList>
        
        <Tabs.TabContent value="overview">
          {stats && (
            <div className="space-y-6">
              {/* Skills performance */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Skills Performance</h3>
                <div className="space-y-4">
                  {Object.entries(stats.skillPerformance).map(([skill, data]) => (
                    <div key={skill}>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">{skill}</span>
                        <span className="text-sm text-gray-500">
                          {data.earned} / {data.total} points ({data.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            data.percentage >= 80
                              ? 'bg-green-500'
                              : data.percentage >= 60
                              ? 'bg-blue-500'
                              : data.percentage >= 40
                              ? 'bg-amber-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${data.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Time analysis */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Time Analysis</h3>
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">Total time: {stats.timeTakenMinutes}m {stats.timeTakenSeconds}s</p>
                  <p className="text-sm text-gray-600">Average time per question: {Math.round((stats.timeTakenMinutes * 60 + stats.timeTakenSeconds) / stats.totalQuestions)} seconds</p>
                </div>
                
                {/* Time bar chart could be added here */}
                <div className="p-6 bg-gray-50 rounded-lg text-center text-gray-500">
                  <p>Detailed time analysis available in the downloaded report</p>
                </div>
              </Card>
              
              {/* Performance summary */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Performance Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">Strengths</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                      {Object.entries(stats.skillPerformance)
                        .filter(([_, data]) => data.percentage >= 70)
                        .map(([skill]) => (
                          <li key={skill}>{skill}</li>
                        ))}
                      {Object.entries(stats.skillPerformance).filter(([_, data]) => data.percentage >= 70).length === 0 && (
                        <li>No particular strengths identified</li>
                      )}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">Areas for Improvement</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                      {Object.entries(stats.skillPerformance)
                        .filter(([_, data]) => data.percentage < 70)
                        .map(([skill]) => (
                          <li key={skill}>{skill}</li>
                        ))}
                      {Object.entries(stats.skillPerformance).filter(([_, data]) => data.percentage < 70).length === 0 && (
                        <li>No significant areas for improvement identified</li>
                      )}
                    </ul>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </Tabs.TabContent>
        
        <Tabs.TabContent value="questions">
          <div className="space-y-6">
            {test.questions.map((question, index) => {
              const response = session.responses[index];
              const isCorrect = response?.is_correct || false;
              
              return (
                <Card key={index} className="p-6 border-l-4 border-l-solid border-l-gray-300">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-medium">Question {index + 1}</h3>
                    <div className="flex items-center">
                      {isCorrect ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-5 h-5 mr-1" />
                          <span className="font-medium">Correct</span>
                        </div>
                      ) : (
                        <div className="flex items-center text-red-600">
                          <XCircle className="w-5 h-5 mr-1" />
                          <span className="font-medium">Incorrect</span>
                        </div>
                      )}
                      <span className="ml-3 text-sm text-gray-500">
                        {isCorrect ? response.points : 0} / {question.points} points
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-gray-800 mb-4">{question.question_text}</p>
                  
                  {/* Multiple choice */}
                  {question.question_type === QUESTION_TYPES.MULTIPLE_CHOICE && (
                    <div className="space-y-2">
                      {question.options.map((option, optionIndex) => {
                        const isSelected = response?.response_data === optionIndex;
                        const isOptionCorrect = option.is_correct;
                        
                        let optionClassName = "flex items-start p-3 rounded-lg border ";
                        if (isSelected && isOptionCorrect) {
                          optionClassName += "border-green-300 bg-green-50";
                        } else if (isSelected && !isOptionCorrect) {
                          optionClassName += "border-red-300 bg-red-50";
                        } else if (!isSelected && isOptionCorrect) {
                          optionClassName += "border-green-300 bg-green-50 opacity-60";
                        } else {
                          optionClassName += "border-gray-200";
                        }
                        
                        return (
                          <div key={optionIndex} className={optionClassName}>
                            <div className="flex items-center h-5">
                              {isSelected ? (
                                isOptionCorrect ? (
                                  <CheckCircle className="w-5 h-5 text-green-600" />
                                ) : (
                                  <XCircle className="w-5 h-5 text-red-600" />
                                )
                              ) : isOptionCorrect ? (
                                <CheckCircle className="w-5 h-5 text-green-600 opacity-60" />
                              ) : (
                                <div className="w-5 h-5 rounded-full border border-gray-300"></div>
                              )}
                            </div>
                            <span className="ml-3">{option.text}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                  
                  {/* Text answer */}
                  {question.question_type === QUESTION_TYPES.TEXT && (
                    <div className="space-y-2">
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-1">Your Answer:</h4>
                        <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                          {response?.response_data || <span className="text-gray-400">No answer provided</span>}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-1">Correct Answer:</h4>
                        <div className="p-3 rounded-lg border border-green-200 bg-green-50">
                          {question.correct_answer}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* True/False */}
                  {question.question_type === QUESTION_TYPES.TRUE_FALSE && (
                    <div className="space-y-2">
                      <div className="flex items-center space-x-4">
                        <div className={`flex items-center p-2 rounded-lg ${
                          response?.response_data === true
                            ? (question.options[0].is_correct ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800")
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          <span className="font-medium">True</span>
                          {response?.response_data === true && (
                            question.options[0].is_correct
                              ? <CheckCircle className="w-4 h-4 ml-2" />
                              : <XCircle className="w-4 h-4 ml-2" />
                          )}
                        </div>
                        
                        <div className={`flex items-center p-2 rounded-lg ${
                          response?.response_data === false
                            ? (question.options[1].is_correct ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800")
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          <span className="font-medium">False</span>
                          {response?.response_data === false && (
                            question.options[1].is_correct
                              ? <CheckCircle className="w-4 h-4 ml-2" />
                              : <XCircle className="w-4 h-4 ml-2" />
                          )}
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-600 mt-2">
                        <span className="font-medium">Correct answer: </span>
                        {question.options[0].is_correct ? "True" : "False"}
                      </div>
                    </div>
                  )}
                  
                  {/* Matching */}
                  {question.question_type === QUESTION_TYPES.MATCHING && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {question.matches.map((match, matchIndex) => {
                        const userMatchedIndex = response?.response_data?.[matchIndex];
                        const isMatchCorrect = userMatchedIndex === matchIndex;
                        
                        return (
                          <div key={matchIndex} className="flex items-center space-x-2">
                            <div className="flex-1 p-3 rounded-lg border border-gray-200">
                              {match.left}
                            </div>
                            <div className="flex items-center">
                              <div className="w-10 h-0.5 bg-gray-300"></div>
                              {isMatchCorrect ? (
                                <CheckCircle className="w-5 h-5 text-green-600" />
                              ) : (
                                <XCircle className="w-5 h-5 text-red-600" />
                              )}
                              <div className="w-10 h-0.5 bg-gray-300"></div>
                            </div>
                            <div className="flex-1 p-3 rounded-lg border border-gray-200">
                              {userMatchedIndex !== undefined
                                ? question.matches[userMatchedIndex]?.right || "Not matched"
                                : "Not matched"}
                            </div>
                          </div>
                        );
                      })}
                      
                      <div className="col-span-1 md:col-span-2 mt-2">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Correct Matches:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {question.matches.map((match, matchIndex) => (
                            <div key={matchIndex} className="flex items-center space-x-2">
                              <div className="flex-1 p-2 rounded-lg bg-green-50 border border-green-200">
                                {match.left}
                              </div>
                              <div className="flex-none">→</div>
                              <div className="flex-1 p-2 rounded-lg bg-green-50 border border-green-200">
                                {match.right}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Ordering */}
                  {question.question_type === QUESTION_TYPES.ORDERING && (
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Your Order:</h4>
                        <div className="space-y-2">
                          {response?.response_data?.map((itemIndex, position) => (
                            <div key={position} className="flex items-center">
                              <span className="flex-none w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center mr-2">
                                {position + 1}
                              </span>
                              <div className="flex-1 p-3 rounded-lg border border-gray-200">
                                {itemIndex !== undefined && itemIndex !== null
                                  ? question.order_items[itemIndex]?.text || "Item not selected"
                                  : "Item not selected"}
                              </div>
                              <div className="flex-none ml-2">
                                {position === question.order_items[itemIndex]?.position ? (
                                  <CheckCircle className="w-5 h-5 text-green-600" />
                                ) : (
                                  <XCircle className="w-5 h-5 text-red-600" />
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Correct Order:</h4>
                        <div className="space-y-2">
                          {question.order_items
                            .sort((a, b) => a.position - b.position)
                            .map((item, position) => (
                              <div key={position} className="flex items-center">
                                <span className="flex-none w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mr-2">
                                  {position + 1}
                                </span>
                                <div className="flex-1 p-3 rounded-lg border border-green-200 bg-green-50">
                                  {item.text}
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {response?.explanation && (
                    <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200">
                      <h4 className="text-sm font-medium text-blue-700 mb-1">Explanation:</h4>
                      <p className="text-sm text-blue-800">{response.explanation}</p>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </Tabs.TabContent>
        
        {feedback && (
          <Tabs.TabContent value="feedback">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">AI-Generated Feedback</h3>
              
              {/* Overall Assessment */}
              <div className="mb-6">
                <h4 className="text-md font-medium text-gray-800 mb-2">Overall Assessment</h4>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-700">{feedback.overall_assessment}</p>
                </div>
              </div>
              
              {/* Strengths */}
              <div className="mb-6">
                <h4 className="text-md font-medium text-gray-800 mb-2">Strengths</h4>
                <ul className="list-disc list-inside space-y-2 p-4 bg-green-50 rounded-lg">
                  {feedback.strengths?.map((strength, index) => (
                    <li key={index} className="text-gray-700">{strength}</li>
                  ))}
                </ul>
              </div>
              
              {/* Areas for Improvement */}
              <div className="mb-6">
                <h4 className="text-md font-medium text-gray-800 mb-2">Areas for Improvement</h4>
                <ul className="list-disc list-inside space-y-2 p-4 bg-amber-50 rounded-lg">
                  {feedback.areas_for_improvement?.map((area, index) => (
                    <li key={index} className="text-gray-700">{area}</li>
                  ))}
                </ul>
              </div>
              
              {/* Recommendations */}
              <div className="mb-6">
                <h4 className="text-md font-medium text-gray-800 mb-2">Recommendations</h4>
                <ul className="list-disc list-inside space-y-2 p-4 bg-blue-50 rounded-lg">
                  {feedback.recommendations?.map((recommendation, index) => (
                    <li key={index} className="text-gray-700">{recommendation}</li>
                  ))}
                </ul>
              </div>
              
              {/* Skill-Specific Feedback */}
              {feedback.skill_feedback && (
                <div>
                  <h4 className="text-md font-medium text-gray-800 mb-2">Skill-Specific Feedback</h4>
                  <div className="space-y-4">
                    {Object.entries(feedback.skill_feedback).map(([skill, feedbackText]) => (
                      <div key={skill} className="p-4 bg-purple-50 rounded-lg">
                        <h5 className="font-medium text-purple-800 mb-2">{skill}</h5>
                        <p className="text-gray-700">{feedbackText}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </Tabs.TabContent>
        )}
      </Tabs>
    </div>
  );
};

export default TestResultsPage;