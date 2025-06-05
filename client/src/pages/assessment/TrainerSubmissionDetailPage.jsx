import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, CheckCircle, XCircle, Award, Clock, 
  FileText, User, Calendar, BarChart2, MessageSquare
} from 'lucide-react';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Progress } from '@/components/ui/progress';
import { Table } from '@/components/ui/table';
/**
 * TrainerSubmissionDetailPage displays detailed information about a student's 
 * assessment submission and allows trainers to review, grade, and provide feedback
 */
const TrainerSubmissionDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // State for submission data
  const [submission, setSubmission] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [template, setTemplate] = useState(null);
  // State for grading
  const [feedback, setFeedback] = useState('');
  const [manualScore, setManualScore] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  // Fetch data
  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        if (!isMounted) return;
        setIsLoading(true);
        setError(null);
        // Fetch submission details
        const submissionResponse = await fetch(`/api/assessment/submissions/${id}`);
        if (!isMounted) return;
        if (!submissionResponse.ok) throw new Error('Failed to fetch submission details');
        const submissionData = await submissionResponse.json();
        if (!isMounted) return;
        setSubmission(submissionData);
        // Initialize feedback from existing data if available
        if (submissionData.feedback?.general) {
          setFeedback(submissionData.feedback.general);
        }
        if (submissionData.score) {
          setManualScore(submissionData.score);
        }
        // Fetch assessment details
        const assessmentResponse = await fetch(`/api/assessment/assigned/${submissionData.assessment_id}`);
        if (!isMounted) return;
        if (!assessmentResponse.ok) throw new Error('Failed to fetch assessment details');
        const assessmentData = await assessmentResponse.json();
        if (!isMounted) return;
        setAssessment(assessmentData);
        // Fetch template details
        const templateResponse = await fetch(`/api/assessment/templates/${submissionData.template_id}`);
        if (!isMounted) return;
        if (!templateResponse.ok) throw new Error('Failed to fetch template details');
        const templateData = await templateResponse.json();
        if (!isMounted) return;
        setTemplate(templateData);
      } catch (err) {
        if (!isMounted) return;
        console.error('Error fetching submission data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load submission details',
          type: 'error',
        });
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    fetchData();
    // Cleanup function to prevent state updates after unmount
    return () => {
      isMounted = false;
    };
  }, [id, toast, setFeedback, setManualScore]);
  // Handle saving feedback without grading
  const handleSaveFeedback = async () => {
    if (!submission) return;
    try {
      setIsSaving(true);
      // Format feedback data
      const feedbackData = {
        ...submission.feedback,
        general: feedback
      };
      // Send feedback update request
      const response = await fetch(`/api/assessment/submissions/${id}/feedback`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feedback: feedbackData }),
      });
      if (!response.ok) throw new Error('Failed to save feedback');
      toast({
        title: 'Success',
        description: 'Feedback saved successfully',
        type: 'success',
      });
      // Update local state
      setSubmission(prev => ({
        ...prev,
        feedback: feedbackData
      }));
    } catch (err) {
      console.error('Error saving feedback:', err);
      toast({
        title: 'Error',
        description: 'Failed to save feedback',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };
  // Handle grading submission
  const handleGradeSubmission = async () => {
    if (!submission) return;
    try {
      setIsSaving(true);
      // Format grading data
      const totalPoints = template?.totalPoints || 100;
      const gradingData = {
        score: manualScore,
        percentage: Math.round((manualScore / totalPoints) * 100),
        passed: (manualScore / totalPoints) * 100 >= assessment?.settings?.passingScore || 70,
        feedback: {
          ...submission.feedback,
          general: feedback
        },
        graded_at: new Date().toISOString(),
        status: 'graded'
      };
      // Send grading request
      const response = await fetch(`/api/assessment/submissions/${id}/grade`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gradingData),
      });
      if (!response.ok) throw new Error('Failed to grade submission');
      const updatedSubmission = await response.json();
      toast({
        title: 'Success',
        description: 'Submission graded successfully',
        type: 'success',
      });
      // Update local state
      setSubmission(updatedSubmission);
    } catch (err) {
      console.error('Error grading submission:', err);
      toast({
        title: 'Error',
        description: 'Failed to grade submission',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
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
  // Render error state
  if (error || !submission || !assessment || !template) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/assessment')}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Assessments
          </Button>
        </div>
        <Card className="p-6 text-center">
          <div className="text-red-500 mb-4">
            <XCircle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Submission Not Found</h2>
          <p className="text-gray-600 mb-4">
            {error || "The requested submission could not be found or has been deleted."}
          </p>
          <Button onClick={() => navigate('/assessment')}>Back to Assessments</Button>
        </Card>
      </div>
    );
  }
  // Calculate score percentage
  const scorePercentage = submission.percentage || 0;
  const isQuiz = template.type === 'quiz';
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <Button
            variant="ghost"
            onClick={() => navigate(`/assessment/assigned/${assessment.id}/results`)}
            className="flex items-center mr-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Results
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{template.title}</h1>
            <p className="text-gray-600">Student Submission Review</p>
          </div>
        </div>
        <div>
          {submission.status !== 'graded' && (
            <Button
              onClick={handleGradeSubmission}
              disabled={isSaving}
              className="flex items-center"
            >
              {isSaving ? (
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
              ) : (
                <CheckCircle className="w-4 h-4 mr-2" />
              )}
              {isSaving ? 'Grading...' : 'Grade Submission'}
            </Button>
          )}
        </div>
      </div>
      {/* Student Info Card */}
      <Card className="p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="flex items-center">
            <User className="w-8 h-8 text-primary mr-4" />
            <div>
              <p className="text-sm text-gray-600">Student</p>
              <p className="font-semibold">{submission.student_name}</p>
              <p className="text-xs text-gray-500">{submission.student_id}</p>
            </div>
          </div>
          <div className="flex items-center">
            <Calendar className="w-8 h-8 text-primary mr-4" />
            <div>
              <p className="text-sm text-gray-600">Submitted</p>
              <p className="font-semibold">
                {submission.submitted_at ? format(new Date(submission.submitted_at), "MMM d, yyyy 'at' h:mm a") : 'Not submitted'}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-primary mr-4" />
            <div>
              <p className="text-sm text-gray-600">Time Spent</p>
              <p className="font-semibold">
                {submission.time_spent ? `${submission.time_spent} minutes` : 'N/A'}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <Award className="w-8 h-8 text-primary mr-4" />
            <div>
              <p className="text-sm text-gray-600">Score</p>
              <div className="flex items-center">
                <p className="font-semibold">
                  {submission.score !== undefined ? `${submission.score} points (${scorePercentage}%)` : 'Not graded'}
                </p>
                {submission.passed !== undefined && (
                  <Badge className={`ml-2 ${submission.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {submission.passed ? 'Passed' : 'Failed'}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList className="mb-6">
          <Tabs.TabTrigger value="overview">
            <BarChart2 className="w-4 h-4 mr-2" />
            Overview
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="answers">
            <FileText className="w-4 h-4 mr-2" />
            Answers
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="feedback">
            <MessageSquare className="w-4 h-4 mr-2" />
            Feedback
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Overview Tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Score Card */}
            {submission.score !== undefined && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-primary" />
                  Score Summary
                </h3>
                <div className="space-y-6">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Total Score</span>
                      <span className="text-sm text-gray-500">
                        {submission.score} / {isQuiz ? template.questions?.length * 10 : 100} points
                      </span>
                    </div>
                    <Progress 
                      value={scorePercentage} 
                      className={`h-3 bg-gray-200 ${
                        scorePercentage >= 90 ? '[&>div]:bg-green-500' :
                        scorePercentage >= 80 ? '[&>div]:bg-blue-500' :
                        scorePercentage >= 70 ? '[&>div]:bg-yellow-500' :
                        scorePercentage >= 60 ? '[&>div]:bg-orange-500' :
                        '[&>div]:bg-red-500'
                      }`} 
                    />
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg flex items-center justify-between">
                    <span className="font-medium">Passing Score</span>
                    <span>{assessment.settings.passingScore}%</span>
                  </div>
                  {/* Score classification */}
                  <div className={`p-4 rounded-lg ${
                    scorePercentage >= 90 ? 'bg-green-50 text-green-800' :
                    scorePercentage >= 80 ? 'bg-blue-50 text-blue-800' :
                    scorePercentage >= 70 ? 'bg-yellow-50 text-yellow-800' :
                    scorePercentage >= 60 ? 'bg-orange-50 text-orange-800' :
                    'bg-red-50 text-red-800'
                  }`}>
                    <p className="font-medium text-center">
                      {scorePercentage >= 90 ? 'Excellent' :
                       scorePercentage >= 80 ? 'Very Good' :
                       scorePercentage >= 70 ? 'Good' :
                       scorePercentage >= 60 ? 'Satisfactory' :
                       'Needs Improvement'}
                    </p>
                  </div>
                </div>
              </Card>
            )}
            {/* Assessment Details */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-primary" />
                Assessment Details
              </h3>
              <Table>
                <Table.Body>
                  <Table.Row>
                    <Table.Cell className="font-medium">Type</Table.Cell>
                    <Table.Cell>
                      <Badge className={isQuiz ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                        {template.type}
                      </Badge>
                    </Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Duration</Table.Cell>
                    <Table.Cell>{isQuiz ? `${template.settings.timeLimit} minutes` : 'No time limit'}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">{isQuiz ? 'Questions' : 'Requirements'}</Table.Cell>
                    <Table.Cell>{isQuiz ? template.questions?.length || 0 : template.requirements?.length || 0}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Due Date</Table.Cell>
                    <Table.Cell>{format(new Date(assessment.due_date), "MMM d, yyyy")}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Skills</Table.Cell>
                    <Table.Cell>
                      <div className="flex flex-wrap gap-2">
                        {template.skills?.map(skill => (
                          <Badge key={skill} variant="outline" className="bg-gray-100">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </Table.Cell>
                  </Table.Row>
                </Table.Body>
              </Table>
            </Card>
            {/* Submission Overview */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-primary" />
                Submission Overview
              </h3>
              <div className="space-y-4">
                {isQuiz ? (
                  <>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Correct Answers</p>
                      <p className="font-bold text-green-600">
                        {submission.correctCount || 0} / {template.questions?.length || 0}
                      </p>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Question Types</p>
                      <div>
                        {/* Count question types */}
                        {template.questions && (
                          <div className="flex gap-2">
                            {Object.entries(template.questions.reduce((acc, q) => {
                              acc[q.type] = (acc[q.type] || 0) + 1;
                              return acc;
                            }, {})).map(([type, count]) => (
                              <Badge key={type} className="bg-blue-100 text-blue-800">
                                {type}: {count}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Attempted Questions</p>
                      <p className="font-bold">
                        {submission.answers ? Object.keys(submission.answers).length : 0} / {template.questions?.length || 0}
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    {/* Project submission details */}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Submission Type</p>
                      <p>{submission.submission_url ? 'URL' : submission.repository_url ? 'Repository' : 'File Upload'}</p>
                    </div>
                    {submission.submission_url && (
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <p className="font-medium">Project URL</p>
                        <a 
                          href={submission.submission_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          Open Project
                        </a>
                      </div>
                    )}
                    {submission.repository_url && (
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <p className="font-medium">Repository URL</p>
                        <a 
                          href={submission.repository_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          View Repository
                        </a>
                      </div>
                    )}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Requirements Met</p>
                      <p className="font-bold">
                        {submission.requirements_met?.filter(r => r.met).length || 0} / {template.requirements?.length || 0}
                      </p>
                    </div>
                  </>
                )}
              </div>
            </Card>
            {/* Feedback Summary */}
            {submission.feedback && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <MessageSquare className="w-5 h-5 mr-2 text-primary" />
                  Feedback Summary
                </h3>
                <div className="space-y-4">
                  {submission.feedback.general && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">General Feedback</h4>
                      <p className="text-gray-800">{submission.feedback.general}</p>
                    </div>
                  )}
                  {submission.feedback.strengths && submission.feedback.strengths.length > 0 && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Strengths</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {submission.feedback.strengths.map((strength, index) => (
                          <li key={index} className="text-gray-800">{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {submission.feedback.areas_for_improvement && submission.feedback.areas_for_improvement.length > 0 && (
                    <div className="p-4 bg-amber-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Areas for Improvement</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {submission.feedback.areas_for_improvement.map((area, index) => (
                          <li key={index} className="text-gray-800">{area}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </Card>
            )}
          </div>
        </Tabs.TabContent>
        {/* Answers Tab */}
        <Tabs.TabContent value="answers">
          {isQuiz ? (
            // Quiz answers
            <div className="space-y-6">
              {template.questions?.map((question, index) => {
                const answer = submission.answers?.[index];
                const isCorrect = submission.answers && index in submission.answers ? 
                  submission.answers[index].correct : false;
                return (
                  <Card key={index} className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-start">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
                          {index + 1}
                        </div>
                        <div>
                          <h3 className="text-lg font-medium mb-1">{question.question}</h3>
                          <Badge className="bg-blue-100 text-blue-800">
                            {question.type}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center">
                        {answer !== undefined ? (
                          isCorrect ? (
                            <div className="flex items-center text-green-600">
                              <CheckCircle className="w-5 h-5 mr-1" />
                              <span className="font-medium">Correct</span>
                            </div>
                          ) : (
                            <div className="flex items-center text-red-600">
                              <XCircle className="w-5 h-5 mr-1" />
                              <span className="font-medium">Incorrect</span>
                            </div>
                          )
                        ) : (
                          <Badge className="bg-amber-100 text-amber-800">
                            Not Answered
                          </Badge>
                        )}
                      </div>
                    </div>
                    {/* Display answer based on question type */}
                    {question.type === 'multipleChoice' && (
                      <div className="space-y-2 mt-4">
                        {question.options.map((option, optionIndex) => {
                          const isSelected = answer === optionIndex;
                          const isOptionCorrect = optionIndex === question.correctAnswer;
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
                              <span className="ml-3">{option}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                    {question.type === 'multipleAnswer' && (
                      <div className="space-y-2 mt-4">
                        {question.options.map((option, optionIndex) => {
                          const isSelected = answer && Array.isArray(answer) && answer.includes(optionIndex);
                          const isOptionCorrect = question.correctAnswers.includes(optionIndex);
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
                              <span className="ml-3">{option}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                    {question.type === 'trueFalse' && (
                      <div className="flex items-center space-x-4 mt-4">
                        <div className={`flex items-center p-2 rounded-lg ${
                          answer === true
                            ? (question.correctAnswer === true ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800")
                            : question.correctAnswer === true ? "bg-green-100 text-green-800 opacity-60" : "bg-gray-100 text-gray-800"
                        }`}>
                          <span className="font-medium">True</span>
                          {answer === true && (
                            question.correctAnswer === true
                              ? <CheckCircle className="w-4 h-4 ml-2" />
                              : <XCircle className="w-4 h-4 ml-2" />
                          )}
                        </div>
                        <div className={`flex items-center p-2 rounded-lg ${
                          answer === false
                            ? (question.correctAnswer === false ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800")
                            : question.correctAnswer === false ? "bg-green-100 text-green-800 opacity-60" : "bg-gray-100 text-gray-800"
                        }`}>
                          <span className="font-medium">False</span>
                          {answer === false && (
                            question.correctAnswer === false
                              ? <CheckCircle className="w-4 h-4 ml-2" />
                              : <XCircle className="w-4 h-4 ml-2" />
                          )}
                        </div>
                      </div>
                    )}
                    {question.type === 'shortAnswer' && (
                      <div className="space-y-4 mt-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Student's Answer:</h4>
                          <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                            {answer || <span className="text-gray-400">No answer provided</span>}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Correct Answer:</h4>
                          <div className="p-3 rounded-lg border border-green-200 bg-green-50">
                            {Array.isArray(question.correctAnswer) 
                              ? question.correctAnswer.join(' or ') 
                              : question.correctAnswer}
                          </div>
                        </div>
                      </div>
                    )}
                    {question.type === 'matching' && (
                      <div className="mt-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                          {question.items.map((item, itemIndex) => {
                            const matchedIndex = answer && typeof answer === 'object' ? answer[item.id] : null;
                            const correctMatchIndex = question.correctMatches[item.id];
                            const isMatchCorrect = matchedIndex === correctMatchIndex;
                            return (
                              <div key={itemIndex} className="flex items-center space-x-2">
                                <div className="flex-1 p-3 rounded-lg border border-gray-200">
                                  {item.text}
                                </div>
                                <div className="flex items-center">
                                  <div className="w-6 h-0.5 bg-gray-300"></div>
                                  {matchedIndex !== undefined ? (
                                    isMatchCorrect ? (
                                      <CheckCircle className="w-5 h-5 text-green-600" />
                                    ) : (
                                      <XCircle className="w-5 h-5 text-red-600" />
                                    )
                                  ) : (
                                    <div className="w-5 h-5 rounded-full border border-gray-300"></div>
                                  )}
                                  <div className="w-6 h-0.5 bg-gray-300"></div>
                                </div>
                                <div className="flex-1 p-3 rounded-lg border border-gray-200">
                                  {matchedIndex !== undefined && question.items
                                    ? question.items.find(i => i.id === matchedIndex)?.match || "Not matched"
                                    : "Not matched"}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Correct Matches:</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {question.items.map((item, itemIndex) => (
                              <div key={itemIndex} className="flex items-center space-x-2">
                                <div className="flex-1 p-2 rounded-lg bg-green-50 border border-green-200">
                                  {item.text}
                                </div>
                                <div className="flex-none">→</div>
                                <div className="flex-1 p-2 rounded-lg bg-green-50 border border-green-200">
                                  {item.match}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                    {/* Explanation if available */}
                    {question.explanation && (
                      <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200">
                        <h4 className="text-sm font-medium text-blue-700 mb-1">Explanation:</h4>
                        <p className="text-sm text-blue-800">{question.explanation}</p>
                      </div>
                    )}
                    {/* Individual feedback if available */}
                    {submission.answers && 
                     submission.answers[index] && 
                     submission.answers[index].feedback && (
                      <div className="mt-4 p-3 rounded-lg bg-purple-50 border border-purple-200">
                        <h4 className="text-sm font-medium text-purple-700 mb-1">Feedback:</h4>
                        <p className="text-sm text-purple-800">{submission.answers[index].feedback}</p>
                      </div>
                    )}
                  </Card>
                );
              })}
            </div>
          ) : (
            // Project submission
            <div className="space-y-6">
              {/* Project Submission Details */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Submission Details</h3>
                {submission.submission_url && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Project URL</h4>
                    <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                      <a 
                        href={submission.submission_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {submission.submission_url}
                      </a>
                    </div>
                  </div>
                )}
                {submission.repository_url && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Repository URL</h4>
                    <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                      <a 
                        href={submission.repository_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {submission.repository_url}
                      </a>
                    </div>
                  </div>
                )}
                {submission.notes && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Student Notes</h4>
                    <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                      {submission.notes}
                    </div>
                  </div>
                )}
              </Card>
              {/* Project Requirements */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Project Requirements</h3>
                <div className="space-y-4">
                  {template.requirements?.map((requirement, index) => {
                    const reqResult = submission.requirements_met?.find(r => r.requirement_id === requirement.id);
                    const isMet = reqResult?.met || false;
                    return (
                      <div key={index} className={`p-4 rounded-lg border ${
                        isMet 
                          ? 'border-green-200 bg-green-50' 
                          : reqResult 
                            ? 'border-red-200 bg-red-50'
                            : 'border-gray-200 bg-gray-50'
                      }`}>
                        <div className="flex justify-between items-start">
                          <div className="flex items-start">
                            <div className="pt-0.5">
                              {isMet ? (
                                <CheckCircle className="w-5 h-5 text-green-600" />
                              ) : reqResult ? (
                                <XCircle className="w-5 h-5 text-red-600" />
                              ) : (
                                <div className="w-5 h-5 rounded-full border border-gray-300"></div>
                              )}
                            </div>
                            <div className="ml-3">
                              <p className="font-medium">{requirement.description}</p>
                              {reqResult?.feedback && (
                                <p className="text-sm text-gray-600 mt-1">{reqResult.feedback}</p>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="font-medium">
                              {reqResult ? `${reqResult.points_earned} / ${requirement.points}` : `0 / ${requirement.points}`}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Card>
              {/* Rubric Scores */}
              {template.rubric && submission.rubric_scores && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Rubric Evaluation</h3>
                  <div className="space-y-6">
                    {Object.entries(template.rubric).map(([category, rubricData]) => {
                      const score = submission.rubric_scores[category];
                      if (!score) return null;
                      const percentage = Math.round((score.points_earned / score.points_possible) * 100);
                      return (
                        <div key={category}>
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="text-md font-medium">{rubricData.description}</h4>
                              <p className="text-sm text-gray-600">
                                {score.points_earned} / {score.points_possible} points
                              </p>
                            </div>
                            <Badge className={`${
                              percentage >= 90 ? 'bg-green-100 text-green-800' :
                              percentage >= 80 ? 'bg-blue-100 text-blue-800' :
                              percentage >= 70 ? 'bg-yellow-100 text-yellow-800' :
                              percentage >= 60 ? 'bg-orange-100 text-orange-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {percentage}%
                            </Badge>
                          </div>
                          <Progress 
                            value={percentage} 
                            className={`h-2 bg-gray-200 mb-2 ${
                              percentage >= 90 ? '[&>div]:bg-green-500' :
                              percentage >= 80 ? '[&>div]:bg-blue-500' :
                              percentage >= 70 ? '[&>div]:bg-yellow-500' :
                              percentage >= 60 ? '[&>div]:bg-orange-500' :
                              '[&>div]:bg-red-500'
                            }`} 
                          />
                          {score.feedback && (
                            <div className="p-3 rounded-lg bg-gray-50 text-sm mt-2">
                              {score.feedback}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </Card>
              )}
            </div>
          )}
        </Tabs.TabContent>
        {/* Feedback Tab */}
        <Tabs.TabContent value="feedback">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Grading Section */}
            {submission.status !== 'graded' && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-primary" />
                  Grade Submission
                </h3>
                {isQuiz ? (
                  <div className="text-gray-600 mb-4">
                    <p>This quiz has been auto-graded based on the provided answers.</p>
                    <p className="mt-2">You can review the auto-grading and provide feedback before finalizing the grade.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="score" className="block text-sm font-medium text-gray-700 mb-1">
                        Score (out of 100)
                      </label>
                      <Input
                        id="score"
                        type="number"
                        min="0"
                        max="100"
                        value={manualScore}
                        onChange={(e) => setManualScore(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="font-medium">Score: {manualScore} / 100</p>
                      <p className="text-sm text-gray-600">
                        Percentage: {Math.round((manualScore / 100) * 100)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        Status: {Math.round((manualScore / 100) * 100) >= assessment.settings.passingScore ? 'Passed' : 'Failed'}
                      </p>
                    </div>
                  </div>
                )}
                <div className="mt-6">
                  <Button 
                    onClick={handleGradeSubmission}
                    disabled={isSaving}
                    className="w-full"
                  >
                    {isSaving ? (
                      <>
                        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
                        Grading...
                      </>
                    ) : (
                      'Grade and Provide Feedback'
                    )}
                  </Button>
                </div>
              </Card>
            )}
            {/* Feedback Section */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <MessageSquare className="w-5 h-5 mr-2 text-primary" />
                Feedback
              </h3>
              <div className="space-y-4">
                <div>
                  <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-1">
                    General Feedback
                  </label>
                  <Textarea
                    id="feedback"
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder="Provide feedback on the overall submission..."
                    rows={6}
                    className="w-full"
                  />
                </div>
                <div className="flex justify-end">
                  <Button 
                    variant="outline" 
                    onClick={handleSaveFeedback}
                    disabled={isSaving}
                  >
                    {isSaving ? (
                      <>
                        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
                        Saving...
                      </>
                    ) : (
                      'Save Feedback'
                    )}
                  </Button>
                </div>
              </div>
            </Card>
            {/* Previous Feedback */}
            {submission.feedback && (
              <Card className="p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4">Previous Feedback</h3>
                <div className="space-y-4">
                  {submission.feedback.general && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">General Feedback</h4>
                      <p className="text-gray-800">{submission.feedback.general}</p>
                    </div>
                  )}
                  {submission.feedback.strengths && submission.feedback.strengths.length > 0 && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Strengths</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {submission.feedback.strengths.map((strength, index) => (
                          <li key={index} className="text-gray-800">{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {submission.feedback.areas_for_improvement && submission.feedback.areas_for_improvement.length > 0 && (
                    <div className="p-4 bg-amber-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Areas for Improvement</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {submission.feedback.areas_for_improvement.map((area, index) => (
                          <li key={index} className="text-gray-800">{area}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </Card>
            )}
          </div>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};
export default TrainerSubmissionDetailPage;