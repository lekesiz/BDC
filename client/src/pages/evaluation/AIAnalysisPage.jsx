import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Download, ThumbsUp, ThumbsDown, MessageSquare, Brain, FileText, PieChart, BarChart2, LineChart, Target, ArrowUpRight, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import api from '@/lib/api';
import { API_ENDPOINTS, FEEDBACK_STATUS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/toast';

/**
 * AIAnalysisPage displays comprehensive AI analysis for a test session
 */
const AIAnalysisPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [session, setSession] = useState(null);
  const [test, setTest] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [feedbackStatus, setFeedbackStatus] = useState(FEEDBACK_STATUS.DRAFT);
  const [trainerFeedback, setTrainerFeedback] = useState('');

  // Fetch session and analysis data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch session data
        const sessionResponse = await api.get(API_ENDPOINTS.EVALUATIONS.SESSION(id));
        setSession(sessionResponse.data);
        
        // Fetch test data
        const testResponse = await api.get(API_ENDPOINTS.EVALUATIONS.DETAIL(sessionResponse.data.test_id));
        setTest(testResponse.data);
        
        // Fetch AI analysis if available
        try {
          const analysisResponse = await api.get(`/api/evaluations/sessions/${id}/analysis`);
          setAnalysis(analysisResponse.data);
          setFeedbackStatus(analysisResponse.data.status || FEEDBACK_STATUS.DRAFT);
          setTrainerFeedback(analysisResponse.data.trainer_feedback || '');
        } catch (error) {
          console.log('Analysis not available yet');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load analysis data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [id, toast]);

  // Generate or regenerate AI analysis
  const handleGenerateAnalysis = async () => {
    try {
      setIsGenerating(true);
      
      const response = await api.post(`/api/evaluations/sessions/${id}/generate-analysis`);
      setAnalysis(response.data);
      setFeedbackStatus(response.data.status || FEEDBACK_STATUS.DRAFT);
      
      toast({
        title: 'Success',
        description: 'AI analysis generated successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error generating analysis:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate AI analysis',
        type: 'error',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  // Approve AI feedback
  const handleApproveFeedback = async () => {
    try {
      const response = await api.put(`/api/evaluations/sessions/${id}/analysis/status`, {
        status: FEEDBACK_STATUS.APPROVED,
        trainer_feedback: trainerFeedback
      });
      
      setFeedbackStatus(FEEDBACK_STATUS.APPROVED);
      toast({
        title: 'Success',
        description: 'Feedback approved successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error approving feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to approve feedback',
        type: 'error',
      });
    }
  };

  // Reject AI feedback
  const handleRejectFeedback = async () => {
    try {
      const response = await api.put(`/api/evaluations/sessions/${id}/analysis/status`, {
        status: FEEDBACK_STATUS.REJECTED,
        trainer_feedback: trainerFeedback
      });
      
      setFeedbackStatus(FEEDBACK_STATUS.REJECTED);
      toast({
        title: 'Success',
        description: 'Feedback rejected',
        type: 'success',
      });
    } catch (error) {
      console.error('Error rejecting feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to reject feedback',
        type: 'error',
      });
    }
  };

  // Handle trainer feedback change
  const handleTrainerFeedbackChange = (e) => {
    setTrainerFeedback(e.target.value);
  };

  // Handle downloading PDF report
  const handleDownloadReport = async () => {
    try {
      const response = await api.get(`/api/evaluations/sessions/${id}/analysis/report`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ai-analysis-${id}.pdf`);
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

  // Render empty state if no session or test data
  if (!session || !test) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <div className="text-red-500 mb-4">
            <XCircle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Session Not Found</h2>
          <p className="text-gray-600 mb-4">The requested test session could not be found.</p>
          <Button onClick={() => navigate('/evaluations')}>Back to Tests</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate(`/evaluations/sessions/${id}/results`)}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Results
          </Button>
          <h1 className="text-2xl font-bold">AI Analysis</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={handleGenerateAnalysis}
            disabled={isGenerating}
            className="flex items-center"
          >
            {isGenerating ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                {analysis ? 'Regenerate Analysis' : 'Generate Analysis'}
              </>
            )}
          </Button>
          
          {analysis && (
            <Button
              onClick={handleDownloadReport}
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Report
            </Button>
          )}
        </div>
      </div>
      
      {/* Session info */}
      <Card className="mb-6 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-gray-500 text-sm">Test</h3>
            <p className="font-medium text-lg">{test.title}</p>
          </div>
          <div>
            <h3 className="text-gray-500 text-sm">Student</h3>
            <p className="font-medium text-lg">{session.user_name || 'Unknown Student'}</p>
          </div>
          <div>
            <h3 className="text-gray-500 text-sm">Score</h3>
            <p className="font-medium text-lg">{session.score}%</p>
          </div>
        </div>
      </Card>
      
      {!analysis ? (
        <Card className="p-6 text-center">
          <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No AI Analysis Available</h2>
          <p className="text-gray-600 mb-4">
            Click the "Generate Analysis" button above to create an AI-powered assessment of this test session.
          </p>
        </Card>
      ) : (
        <>
          {/* Status bar for trainers */}
          <Card className={`mb-6 p-4 ${
            feedbackStatus === FEEDBACK_STATUS.APPROVED 
              ? 'bg-green-50 border-green-200' 
              : feedbackStatus === FEEDBACK_STATUS.REJECTED
                ? 'bg-red-50 border-red-200'
                : 'bg-amber-50 border-amber-200'
          }`}>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
              <div className="flex items-center">
                {feedbackStatus === FEEDBACK_STATUS.APPROVED ? (
                  <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                ) : feedbackStatus === FEEDBACK_STATUS.REJECTED ? (
                  <XCircle className="w-5 h-5 text-red-600 mr-2" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-amber-600 mr-2" />
                )}
                <div>
                  <h3 className="font-medium">
                    {feedbackStatus === FEEDBACK_STATUS.APPROVED
                      ? 'AI Feedback Approved'
                      : feedbackStatus === FEEDBACK_STATUS.REJECTED
                        ? 'AI Feedback Rejected'
                        : 'AI Feedback Pending Review'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {feedbackStatus === FEEDBACK_STATUS.APPROVED
                      ? 'This analysis has been reviewed and approved by a trainer.'
                      : feedbackStatus === FEEDBACK_STATUS.REJECTED
                        ? 'This analysis has been reviewed and rejected by a trainer.'
                        : 'This AI-generated analysis requires review by a trainer before being shared with the student.'}
                  </p>
                </div>
              </div>
              
              {feedbackStatus === FEEDBACK_STATUS.DRAFT && (
                <div className="flex items-center space-x-2 mt-4 md:mt-0">
                  <Button
                    variant="outline"
                    onClick={handleRejectFeedback}
                    className="flex items-center"
                  >
                    <ThumbsDown className="w-4 h-4 mr-2" />
                    Reject
                  </Button>
                  
                  <Button
                    onClick={handleApproveFeedback}
                    className="flex items-center"
                  >
                    <ThumbsUp className="w-4 h-4 mr-2" />
                    Approve
                  </Button>
                </div>
              )}
            </div>
          </Card>
          
          {/* Trainer feedback input */}
          <Card className="mb-6 p-6">
            <h3 className="text-lg font-medium mb-2">Trainer Feedback</h3>
            <p className="text-sm text-gray-600 mb-4">
              Add your comments or suggestions to supplement the AI-generated analysis.
            </p>
            <textarea
              value={trainerFeedback}
              onChange={handleTrainerFeedbackChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
              rows="4"
              placeholder="Enter your feedback here..."
            ></textarea>
            <div className="flex justify-end mt-2">
              <Button
                onClick={async () => {
                  try {
                    await api.put(`/api/evaluations/sessions/${id}/analysis/trainer-feedback`, {
                      trainer_feedback: trainerFeedback
                    });
                    
                    toast({
                      title: 'Success',
                      description: 'Trainer feedback saved',
                      type: 'success',
                    });
                  } catch (error) {
                    console.error('Error saving feedback:', error);
                    toast({
                      title: 'Error',
                      description: 'Failed to save feedback',
                      type: 'error',
                    });
                  }
                }}
                variant="outline"
                size="sm"
              >
                Save Feedback
              </Button>
            </div>
          </Card>
          
          {/* Analysis content in tabs */}
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="mb-6"
          >
            <Tabs.TabsList className="mb-4">
              <Tabs.TabTrigger value="overview">
                <FileText className="w-4 h-4 mr-2" />
                Overview
              </Tabs.TabTrigger>
              <Tabs.TabTrigger value="skills">
                <Target className="w-4 h-4 mr-2" />
                Skills Analysis
              </Tabs.TabTrigger>
              <Tabs.TabTrigger value="patterns">
                <PieChart className="w-4 h-4 mr-2" />
                Response Patterns
              </Tabs.TabTrigger>
              <Tabs.TabTrigger value="trends">
                <LineChart className="w-4 h-4 mr-2" />
                Growth Trends
              </Tabs.TabTrigger>
              <Tabs.TabTrigger value="recommendations">
                <ArrowUpRight className="w-4 h-4 mr-2" />
                Recommendations
              </Tabs.TabTrigger>
            </Tabs.TabsList>
            
            {/* Overview tab */}
            <Tabs.TabContent value="overview">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Performance Summary</h2>
                <div className="prose max-w-none">
                  <p className="mb-4">{analysis.summary}</p>
                  
                  <h3 className="font-medium text-lg mt-6 mb-2">Key Observations</h3>
                  <ul className="space-y-2">
                    {analysis.key_observations.map((observation, index) => (
                      <li key={index} className="flex items-start">
                        <div className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-2">
                          {index + 1}
                        </div>
                        {observation}
                      </li>
                    ))}
                  </ul>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div>
                      <h3 className="font-medium text-lg mb-2">Strengths</h3>
                      <ul className="space-y-2 text-green-800">
                        {analysis.strengths.map((strength, index) => (
                          <li key={index} className="flex items-start bg-green-50 p-3 rounded-lg">
                            <CheckCircle className="w-5 h-5 mr-2 flex-shrink-0 text-green-600" />
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="font-medium text-lg mb-2">Areas for Improvement</h3>
                      <ul className="space-y-2 text-amber-800">
                        {analysis.areas_for_improvement.map((area, index) => (
                          <li key={index} className="flex items-start bg-amber-50 p-3 rounded-lg">
                            <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0 text-amber-600" />
                            <span>{area}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <h3 className="font-medium text-lg mt-6 mb-2">Learning Style Analysis</h3>
                  <p>{analysis.learning_style_analysis}</p>
                  
                  <h3 className="font-medium text-lg mt-6 mb-2">Performance Relative to Peers</h3>
                  <p>{analysis.peer_comparison}</p>
                </div>
              </Card>
            </Tabs.TabContent>
            
            {/* Skills Analysis tab */}
            <Tabs.TabContent value="skills">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Skills Analysis</h2>
                
                <div className="space-y-6">
                  {Object.entries(analysis.skills_analysis).map(([skill, data]) => (
                    <div key={skill} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="font-medium text-lg">{skill}</h3>
                        <div className={`px-2 py-1 rounded-full text-sm font-medium ${
                          data.proficiency >= 80 ? 'bg-green-100 text-green-800' :
                          data.proficiency >= 60 ? 'bg-blue-100 text-blue-800' :
                          data.proficiency >= 40 ? 'bg-amber-100 text-amber-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {data.proficiency >= 80 ? 'Advanced' :
                           data.proficiency >= 60 ? 'Proficient' :
                           data.proficiency >= 40 ? 'Developing' :
                           'Beginner'}
                        </div>
                      </div>
                      
                      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                        <div
                          className={`h-2.5 rounded-full ${
                            data.proficiency >= 80 ? 'bg-green-600' :
                            data.proficiency >= 60 ? 'bg-blue-600' :
                            data.proficiency >= 40 ? 'bg-amber-500' :
                            'bg-red-600'
                          }`}
                          style={{ width: `${data.proficiency}%` }}
                        ></div>
                      </div>
                      
                      <p className="text-gray-700 mb-4">{data.analysis}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Strengths</h4>
                          <ul className="space-y-1">
                            {data.strengths.map((item, idx) => (
                              <li key={idx} className="text-sm flex items-start">
                                <CheckCircle className="w-4 h-4 text-green-600 mr-1 flex-shrink-0" />
                                <span>{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Areas to Work On</h4>
                          <ul className="space-y-1">
                            {data.areas_to_work_on.map((item, idx) => (
                              <li key={idx} className="text-sm flex items-start">
                                <AlertTriangle className="w-4 h-4 text-amber-600 mr-1 flex-shrink-0" />
                                <span>{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </Tabs.TabContent>
            
            {/* Response Patterns tab */}
            <Tabs.TabContent value="patterns">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Response Patterns</h2>
                
                <div className="mb-6">
                  <h3 className="font-medium text-lg mb-2">Answer Strategy</h3>
                  <p className="text-gray-700 mb-4">{analysis.response_patterns.answer_strategy}</p>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Key Patterns Observed</h4>
                    <ul className="space-y-2">
                      {analysis.response_patterns.key_patterns.map((pattern, index) => (
                        <li key={index} className="flex items-start">
                          <div className="flex-shrink-0 w-5 h-5 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 mr-2">
                            {index + 1}
                          </div>
                          {pattern}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="mb-6">
                  <h3 className="font-medium text-lg mb-2">Question Type Analysis</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(analysis.response_patterns.question_types).map(([type, data]) => (
                      <div key={type} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-medium">{type}</h4>
                          <span className="text-sm font-medium">{data.accuracy}% Accuracy</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                          <div
                            className={`h-2 rounded-full ${
                              data.accuracy >= 80 ? 'bg-green-600' :
                              data.accuracy >= 60 ? 'bg-blue-600' :
                              data.accuracy >= 40 ? 'bg-amber-500' :
                              'bg-red-600'
                            }`}
                            style={{ width: `${data.accuracy}%` }}
                          ></div>
                        </div>
                        <p className="text-sm text-gray-700">{data.analysis}</p>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-medium text-lg mb-2">Time Management</h3>
                  <p className="text-gray-700 mb-4">{analysis.response_patterns.time_management.analysis}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-blue-700 mb-1">Average Time per Question</h4>
                      <p className="text-lg font-bold text-blue-800">{analysis.response_patterns.time_management.avg_time_per_question} seconds</p>
                    </div>
                    
                    <div className="bg-purple-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-purple-700 mb-1">Fastest Question Type</h4>
                      <p className="text-lg font-bold text-purple-800">{analysis.response_patterns.time_management.fastest_question_type}</p>
                    </div>
                    
                    <div className="bg-indigo-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-indigo-700 mb-1">Slowest Question Type</h4>
                      <p className="text-lg font-bold text-indigo-800">{analysis.response_patterns.time_management.slowest_question_type}</p>
                    </div>
                  </div>
                </div>
              </Card>
            </Tabs.TabContent>
            
            {/* Growth Trends tab */}
            <Tabs.TabContent value="trends">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Growth Trends</h2>
                
                <div className="mb-6">
                  <h3 className="font-medium text-lg mb-2">Longitudinal Analysis</h3>
                  <p className="text-gray-700 mb-4">{analysis.growth_trends.longitudinal_analysis}</p>
                  
                  <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <div className="mb-2 flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-700">Skill Progress Over Time</h4>
                      <span className="text-xs text-gray-500">Last 3 assessments</span>
                    </div>
                    
                    {/* Mock bar chart for skill progress */}
                    <div className="space-y-4">
                      {Object.entries(analysis.growth_trends.skill_progress).map(([skill, data]) => (
                        <div key={skill}>
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium">{skill}</span>
                            <span className="text-xs text-gray-500">
                              {data.previous} → {data.current} ({data.change >= 0 ? '+' : ''}{data.change}%)
                            </span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <div className="h-4 bg-gray-300 rounded" style={{ width: `${data.previous}%` }}></div>
                            <ArrowRight className="w-4 h-4 text-gray-500" />
                            <div className={`h-4 rounded ${data.change >= 0 ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${data.current}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="mb-6">
                  <h3 className="font-medium text-lg mb-2">Mastery Path</h3>
                  <p className="text-gray-700 mb-4">{analysis.growth_trends.mastery_path.description}</p>
                  
                  <div className="relative">
                    <div className="absolute left-5 inset-y-0 w-0.5 bg-gray-200"></div>
                    
                    <div className="space-y-8">
                      {analysis.growth_trends.mastery_path.milestones.map((milestone, index) => (
                        <div key={index} className="relative pl-8">
                          <div className={`absolute left-0 w-10 h-10 rounded-full ${
                            milestone.achieved 
                              ? 'bg-green-100 text-green-600 border-2 border-green-500' 
                              : 'bg-gray-100 text-gray-400 border-2 border-gray-300'
                          } flex items-center justify-center`}>
                            {milestone.achieved ? <CheckCircle className="w-5 h-5" /> : index + 1}
                          </div>
                          
                          <div className={`rounded-lg p-4 ${milestone.achieved ? 'bg-green-50 border border-green-200' : 'bg-white border border-gray-200'}`}>
                            <h4 className="font-medium mb-1">{milestone.title}</h4>
                            <p className="text-sm text-gray-700">{milestone.description}</p>
                            {milestone.achieved && (
                              <div className="mt-2 text-xs font-medium text-green-600 flex items-center">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Achieved
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-medium text-lg mb-2">Learning Velocity</h3>
                  <p className="text-gray-700 mb-4">{analysis.growth_trends.learning_velocity.analysis}</p>
                  
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-blue-700 mb-1">Current Velocity</h4>
                        <div className="flex items-baseline">
                          <span className="text-2xl font-bold text-blue-800">{analysis.growth_trends.learning_velocity.current_velocity}</span>
                          <span className="text-sm text-blue-600 ml-1">points/month</span>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-blue-700 mb-1">Projected Timeline</h4>
                        <div className="flex items-baseline">
                          <span className="text-2xl font-bold text-blue-800">{analysis.growth_trends.learning_velocity.projected_timeline}</span>
                          <span className="text-sm text-blue-600 ml-1">months to mastery</span>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-blue-700 mb-1">Comparison to Peers</h4>
                        <div className="flex items-baseline">
                          <span className="text-2xl font-bold text-blue-800">{analysis.growth_trends.learning_velocity.peer_comparison}</span>
                          <span className="text-sm text-blue-600 ml-1">percentile</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </Tabs.TabContent>
            
            {/* Recommendations tab */}
            <Tabs.TabContent value="recommendations">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Recommendations</h2>
                
                <div className="mb-6">
                  <h3 className="font-medium text-lg mb-2">Next Steps</h3>
                  <div className="space-y-4">
                    {analysis.recommendations.next_steps.map((step, index) => (
                      <div key={index} className="flex items-start">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-3">
                          {index + 1}
                        </div>
                        <div>
                          <h4 className="font-medium mb-1">{step.title}</h4>
                          <p className="text-sm text-gray-700">{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="mb-6">
                  <h3 className="font-medium text-lg mb-2">Learning Resources</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {analysis.recommendations.resources.map((resource, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start">
                          {resource.type === 'video' && <FileVideo className="w-5 h-5 text-red-600 mr-2 flex-shrink-0" />}
                          {resource.type === 'article' && <FileText className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0" />}
                          {resource.type === 'exercise' && <FilePlay className="w-5 h-5 text-green-600 mr-2 flex-shrink-0" />}
                          {resource.type === 'course' && <BookOpen className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0" />}
                          
                          <div>
                            <h4 className="font-medium">{resource.title}</h4>
                            <p className="text-sm text-gray-700 mt-1">{resource.description}</p>
                            
                            <div className="flex items-center mt-2">
                              <span className="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-600 mr-2">
                                {resource.duration}
                              </span>
                              <span className="text-xs bg-blue-100 px-2 py-0.5 rounded text-blue-600">
                                {resource.skill}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-medium text-lg mb-2">Personalized Learning Plan</h3>
                  <p className="text-gray-700 mb-4">{analysis.recommendations.learning_plan.description}</p>
                  
                  <div className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 p-3 font-medium">Weekly Focus Areas</div>
                    <div className="divide-y divide-gray-200">
                      {analysis.recommendations.learning_plan.weekly_focus.map((week, index) => (
                        <div key={index} className="p-4">
                          <h4 className="font-medium mb-2">Week {week.week}: {week.focus}</h4>
                          <p className="text-sm text-gray-700 mb-2">{week.description}</p>
                          
                          <div className="flex items-center space-x-2 text-sm">
                            <div className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                              {week.skills.join(', ')}
                            </div>
                            <div className="bg-green-100 text-green-800 px-2 py-0.5 rounded">
                              {week.hours} hours
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            </Tabs.TabContent>
          </Tabs>
        </>
      )}
    </div>
  );
};

// Arrow component for progress visualization
const ArrowRight = (props) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M5 12h14" />
      <path d="m12 5 7 7-7 7" />
    </svg>
  );
};

// File icons for recommendations
const FileVideo = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
    <polyline points="14 2 14 8 20 8" />
    <path d="m10 11 5 3-5 3v-6Z" />
  </svg>
);

const FilePlay = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
    <polyline points="14 2 14 8 20 8" />
    <circle cx="12" cy="15" r="4" />
    <path d="M14 15l-4 2v-4l4 2z" />
  </svg>
);

const BookOpen = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
);

export default AIAnalysisPage;