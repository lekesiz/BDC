import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Edit2, Copy, Trash2, Users, Calendar, Clock, 
  FileText, Award, BarChart2, Settings, Share2, Eye
} from 'lucide-react';
import { format } from 'date-fns';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { Table } from '@/components/ui/table';
import { Label } from '@/components/ui';
import { Switch } from '@/components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

/**
 * TrainerAssessmentTemplateDetailPage displays detailed information about an assessment template
 * and provides options to edit, duplicate, assign, or delete the template
 */
const TrainerAssessmentTemplateDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for template data
  const [template, setTemplate] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  
  // State for dialogs
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDuplicating, setIsDuplicating] = useState(false);
  
  // Fetch data
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        if (!isMounted) return;
        
        setIsLoading(true);
        setError(null);
        
        // Fetch template details
        const templateResponse = await fetch(`/api/assessment/templates/${id}`);
        if (!isMounted) return;
        
        if (!templateResponse.ok) throw new Error('Failed to fetch template details');
        const templateData = await templateResponse.json();
        
        if (!isMounted) return;
        setTemplate(templateData);
        
        // Fetch assignments using this template
        const assignmentsResponse = await fetch(`/api/assessment/templates/${id}/assignments`);
        if (!isMounted) return;
        
        if (!assignmentsResponse.ok) throw new Error('Failed to fetch assignments');
        const assignmentsData = await assignmentsResponse.json();
        
        if (!isMounted) return;
        setAssignments(assignmentsData);
        
        // Fetch analytics for this template
        const analyticsResponse = await fetch(`/api/assessment/templates/${id}/analytics`);
        if (!isMounted) return;
        
        if (!analyticsResponse.ok) throw new Error('Failed to fetch analytics');
        const analyticsData = await analyticsResponse.json();
        
        if (!isMounted) return;
        setAnalytics(analyticsData);
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Error fetching template data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load template details',
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
  }, [id, toast]);
  
  // Handle template deletion
  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      
      const response = await fetch(`/api/assessment/templates/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete template');
      
      toast({
        title: 'Success',
        description: 'Template deleted successfully',
        type: 'success',
      });
      
      navigate('/assessment');
    } catch (err) {
      console.error('Error deleting template:', err);
      toast({
        title: 'Error',
        description: 'Failed to delete template',
        type: 'error',
      });
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
    }
  };
  
  // Handle template duplication
  const handleDuplicate = async () => {
    try {
      setIsDuplicating(true);
      
      const response = await fetch(`/api/assessment/templates/${id}/duplicate`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to duplicate template');
      
      const duplicatedTemplate = await response.json();
      
      toast({
        title: 'Success',
        description: 'Template duplicated successfully',
        type: 'success',
      });
      
      navigate(`/assessment/templates/${duplicatedTemplate.id}`);
    } catch (err) {
      console.error('Error duplicating template:', err);
      toast({
        title: 'Error',
        description: 'Failed to duplicate template',
        type: 'error',
      });
    } finally {
      setIsDuplicating(false);
      setShowDuplicateDialog(false);
    }
  };
  
  // Handle template publish/unpublish
  const handleTogglePublish = async () => {
    if (!template) return;
    
    try {
      const response = await fetch(`/api/assessment/templates/${id}/publish`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_published: !template.is_published }),
      });
      
      if (!response.ok) throw new Error('Failed to update template');
      
      const updatedTemplate = await response.json();
      setTemplate(updatedTemplate);
      
      toast({
        title: 'Success',
        description: `Template ${updatedTemplate.is_published ? 'published' : 'unpublished'} successfully`,
        type: 'success',
      });
    } catch (err) {
      console.error('Error updating template:', err);
      toast({
        title: 'Error',
        description: 'Failed to update template',
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
  
  // Render error state
  if (error || !template) {
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
            <FileText className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Template Not Found</h2>
          <p className="text-gray-600 mb-4">
            {error || "The requested template could not be found or has been deleted."}
          </p>
          <Button onClick={() => navigate('/assessment')}>Back to Assessments</Button>
        </Card>
      </div>
    );
  }
  
  const isQuiz = template.type === 'quiz';
  
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <Button
            variant="ghost"
            onClick={() => navigate('/assessment')}
            className="flex items-center mr-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Assessments
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{template.title}</h1>
              <Badge className={isQuiz ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                {template.type}
              </Badge>
              <Badge className={template.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                {template.is_published ? 'Published' : 'Draft'}
              </Badge>
            </div>
            <p className="text-gray-600">{template.description}</p>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={() => navigate(`/assessment/templates/${id}/preview`)}
            className="flex items-center"
          >
            <Eye className="w-4 h-4 mr-2" />
            Preview
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate(`/assessment/edit/${id}`)}
            className="flex items-center"
          >
            <Edit2 className="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowDuplicateDialog(true)}
            className="flex items-center"
          >
            <Copy className="w-4 h-4 mr-2" />
            Duplicate
          </Button>
          <Button
            onClick={() => navigate(`/assessment/assign/${id}`)}
            className="flex items-center"
          >
            <Users className="w-4 h-4 mr-2" />
            Assign
          </Button>
          <Button
            variant="destructive"
            onClick={() => setShowDeleteDialog(true)}
            className="flex items-center"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>
      
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
          <Tabs.TabTrigger value="content">
            <FileText className="w-4 h-4 mr-2" />
            Content
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="assignments">
            <Users className="w-4 h-4 mr-2" />
            Assignments ({assignments.length})
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="settings">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        
        {/* Overview Tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Template Details Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-primary" />
                Template Details
              </h3>
              
              <Table>
                <Table.Body>
                  <Table.Row>
                    <Table.Cell className="font-medium">Created By</Table.Cell>
                    <Table.Cell>{template.created_by}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Created</Table.Cell>
                    <Table.Cell>{format(new Date(template.created_at), "MMM d, yyyy")}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Last Modified</Table.Cell>
                    <Table.Cell>{format(new Date(template.updated_at), "MMM d, yyyy")}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Total Points</Table.Cell>
                    <Table.Cell>
                      {isQuiz ? template.questions?.length * 10 || 0 : template.totalPoints || 100} points
                    </Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">
                      {isQuiz ? 'Questions' : 'Requirements'}
                    </Table.Cell>
                    <Table.Cell>
                      {isQuiz ? template.questions?.length || 0 : template.requirements?.length || 0}
                    </Table.Cell>
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
            
            {/* Analytics Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart2 className="w-5 h-5 mr-2 text-primary" />
                Usage Analytics
              </h3>
              
              {analytics ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">Total Assignments</p>
                    <p className="font-bold text-primary">{analytics.total_assignments}</p>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">Completed Submissions</p>
                    <p className="font-bold text-green-600">{analytics.completed_submissions}</p>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">Average Score</p>
                    <p className="font-bold text-blue-600">
                      {analytics.average_score ? `${analytics.average_score}%` : 'N/A'}
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">Pass Rate</p>
                    <p className="font-bold text-purple-600">
                      {analytics.pass_rate ? `${analytics.pass_rate}%` : 'N/A'}
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">Average Time</p>
                    <p className="font-bold">
                      {analytics.average_time_spent ? `${analytics.average_time_spent} min` : 'N/A'}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No analytics data available</p>
              )}
            </Card>
            
            {/* Settings Overview Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Settings className="w-5 h-5 mr-2 text-primary" />
                Settings Overview
              </h3>
              
              <div className="space-y-4">
                {isQuiz && (
                  <>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Time Limit</p>
                      <p>{template.settings?.timeLimit ? `${template.settings.timeLimit} minutes` : 'No limit'}</p>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Shuffle Questions</p>
                      <p>{template.settings?.shuffleQuestions ? 'Yes' : 'No'}</p>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Show Correct Answers</p>
                      <p>{template.settings?.showCorrectAnswers ? 'Yes' : 'No'}</p>
                    </div>
                  </>
                )}
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">Allow Late Submission</p>
                  <p>{template.settings?.allowLateSubmission ? 'Yes' : 'No'}</p>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">Auto-grading</p>
                  <p>{template.settings?.autoGrade ? 'Enabled' : 'Disabled'}</p>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">Passing Score</p>
                  <p>{template.settings?.passingScore || 70}%</p>
                </div>
              </div>
            </Card>
            
            {/* Recent Activity Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Clock className="w-5 h-5 mr-2 text-primary" />
                Recent Activity
              </h3>
              
              <div className="space-y-3">
                {/* Mock recent activity - would be real data in production */}
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">Template assigned</p>
                    <p className="text-sm text-gray-600">To Data Engineering Group</p>
                  </div>
                  <p className="text-sm text-gray-500">2 hours ago</p>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">Template edited</p>
                    <p className="text-sm text-gray-600">Questions updated</p>
                  </div>
                  <p className="text-sm text-gray-500">1 day ago</p>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">Template published</p>
                    <p className="text-sm text-gray-600">Made available for assignment</p>
                  </div>
                  <p className="text-sm text-gray-500">3 days ago</p>
                </div>
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
        
        {/* Content Tab */}
        <Tabs.TabContent value="content">
          {isQuiz ? (
            // Quiz content
            <div className="space-y-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Quiz Questions</h3>
                
                {template.questions && template.questions.length > 0 ? (
                  <div className="space-y-4">
                    {template.questions.map((question, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-start">
                            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
                              {index + 1}
                            </div>
                            <div>
                              <p className="font-medium">{question.question}</p>
                              <Badge className="mt-1 bg-blue-100 text-blue-800">
                                {question.type}
                              </Badge>
                            </div>
                          </div>
                          <p className="text-sm text-gray-500">{question.points || 10} points</p>
                        </div>
                        
                        {/* Display options based on question type */}
                        {question.type === 'multipleChoice' && (
                          <div className="ml-11 space-y-1">
                            {question.options.map((option, optionIndex) => (
                              <div key={optionIndex} className="flex items-center">
                                <div className={`w-5 h-5 rounded-full border mr-2 ${
                                  optionIndex === question.correctAnswer
                                    ? 'border-green-500 bg-green-100'
                                    : 'border-gray-300'
                                }`}></div>
                                <span className={optionIndex === question.correctAnswer ? 'text-green-700 font-medium' : ''}>
                                  {option}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {question.type === 'trueFalse' && (
                          <div className="ml-11">
                            <p className="text-sm text-gray-600">
                              Correct answer: <span className="font-medium">{question.correctAnswer ? 'True' : 'False'}</span>
                            </p>
                          </div>
                        )}
                        
                        {question.type === 'shortAnswer' && (
                          <div className="ml-11">
                            <p className="text-sm text-gray-600">
                              Correct answer(s): 
                              <span className="font-medium">
                                {Array.isArray(question.correctAnswer) 
                                  ? question.correctAnswer.join(' | ') 
                                  : question.correctAnswer}
                              </span>
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No questions added</p>
                )}
              </Card>
            </div>
          ) : (
            // Project content
            <div className="space-y-6">
              {/* Requirements */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Project Requirements</h3>
                
                {template.requirements && template.requirements.length > 0 ? (
                  <div className="space-y-3">
                    {template.requirements.map((requirement, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex items-start">
                            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0 mt-0.5">
                              {index + 1}
                            </div>
                            <p>{requirement.description}</p>
                          </div>
                          <p className="text-sm text-gray-500 font-medium">{requirement.points} points</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No requirements specified</p>
                )}
              </Card>
              
              {/* Rubric */}
              {template.rubric && Object.keys(template.rubric).length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Evaluation Rubric</h3>
                  
                  <div className="space-y-4">
                    {Object.entries(template.rubric).map(([category, details]) => (
                      <div key={category} className="p-4 border rounded-lg">
                        <h4 className="font-medium mb-2">{category}</h4>
                        <p className="text-gray-600 mb-3">{details.description}</p>
                        
                        <div className="space-y-2">
                          {Object.entries(details.levels).map(([level, criteria]) => (
                            <div key={level} className="flex items-start">
                              <Badge className={`mr-2 ${
                                level === 'excellent' ? 'bg-green-100 text-green-800' :
                                level === 'good' ? 'bg-blue-100 text-blue-800' :
                                level === 'satisfactory' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {level}
                              </Badge>
                              <p className="text-sm text-gray-600">{criteria}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
              
              {/* Resources */}
              {template.resources && template.resources.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Resources</h3>
                  
                  <div className="space-y-2">
                    {template.resources.map((resource, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <a href={resource.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {resource.title}
                        </a>
                        <Badge variant="outline">{resource.type}</Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </div>
          )}
        </Tabs.TabContent>
        
        {/* Assignments Tab */}
        <Tabs.TabContent value="assignments">
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Active Assignments</h3>
              <Button
                onClick={() => navigate(`/assessment/assign/${id}`)}
                className="flex items-center"
              >
                <Users className="w-4 h-4 mr-2" />
                New Assignment
              </Button>
            </div>
            
            {assignments.length > 0 ? (
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Course/Group</Table.HeaderCell>
                    <Table.HeaderCell>Students</Table.HeaderCell>
                    <Table.HeaderCell>Due Date</Table.HeaderCell>
                    <Table.HeaderCell>Completion</Table.HeaderCell>
                    <Table.HeaderCell>Status</Table.HeaderCell>
                    <Table.HeaderCell>Actions</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {assignments.map(assignment => (
                    <Table.Row key={assignment.id}>
                      <Table.Cell>{assignment.course_name}</Table.Cell>
                      <Table.Cell>{assignment.student_count}</Table.Cell>
                      <Table.Cell>{format(new Date(assignment.due_date), "MMM d, yyyy")}</Table.Cell>
                      <Table.Cell>
                        <div className="flex items-center">
                          <span className="mr-2">{assignment.completion_rate}%</span>
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full"
                              style={{ width: `${assignment.completion_rate}%` }}
                            ></div>
                          </div>
                        </div>
                      </Table.Cell>
                      <Table.Cell>
                        <Badge className={
                          assignment.status === 'active' ? 'bg-green-100 text-green-800' :
                          assignment.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }>
                          {assignment.status}
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/assessment/assigned/${assignment.id}/results`)}
                        >
                          View Results
                        </Button>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No active assignments for this template
              </p>
            )}
          </Card>
        </Tabs.TabContent>
        
        {/* Settings Tab */}
        <Tabs.TabContent value="settings">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* General Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">General Settings</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="published">Published</Label>
                    <p className="text-sm text-gray-600">Make this template available for assignment</p>
                  </div>
                  <Switch
                    id="published"
                    checked={template.is_published}
                    onCheckedChange={handleTogglePublish}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="sharable">Sharable</Label>
                    <p className="text-sm text-gray-600">Allow other trainers to use this template</p>
                  </div>
                  <Switch
                    id="sharable"
                    checked={template.settings?.sharable || false}
                    disabled
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="require-approval">Require Approval</Label>
                    <p className="text-sm text-gray-600">Submissions need trainer approval</p>
                  </div>
                  <Switch
                    id="require-approval"
                    checked={template.settings?.requireApproval || false}
                    disabled
                  />
                </div>
              </div>
            </Card>
            
            {/* Assessment Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Assessment Settings</h3>
              
              <div className="space-y-4">
                {isQuiz && (
                  <>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Time Limit</p>
                      <p className="text-sm text-gray-600">
                        {template.settings?.timeLimit ? `${template.settings.timeLimit} minutes` : 'No time limit'}
                      </p>
                    </div>
                    
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">Attempts Allowed</p>
                      <p className="text-sm text-gray-600">
                        {template.settings?.attemptsAllowed || 'Unlimited'}
                      </p>
                    </div>
                  </>
                )}
                
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">Passing Score</p>
                  <p className="text-sm text-gray-600">{template.settings?.passingScore || 70}%</p>
                </div>
                
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">Allow Late Submission</p>
                  <p className="text-sm text-gray-600">
                    {template.settings?.allowLateSubmission ? 'Yes' : 'No'}
                  </p>
                </div>
                
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">Late Penalty</p>
                  <p className="text-sm text-gray-600">
                    {template.settings?.latePenalty ? `${template.settings.latePenalty}% per day` : 'None'}
                  </p>
                </div>
              </div>
            </Card>
            
            {/* Notification Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Notification Settings</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notify-submission">Notify on Submission</Label>
                    <p className="text-sm text-gray-600">Get notified when students submit</p>
                  </div>
                  <Switch
                    id="notify-submission"
                    checked={template.settings?.notifyOnSubmission || false}
                    disabled
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notify-due">Notify Before Due Date</Label>
                    <p className="text-sm text-gray-600">Remind students before due date</p>
                  </div>
                  <Switch
                    id="notify-due"
                    checked={template.settings?.notifyBeforeDue || false}
                    disabled
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notify-grade">Notify on Grading</Label>
                    <p className="text-sm text-gray-600">Notify students when graded</p>
                  </div>
                  <Switch
                    id="notify-grade"
                    checked={template.settings?.notifyOnGrade || false}
                    disabled
                  />
                </div>
              </div>
            </Card>
            
            {/* Sharing Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sharing Settings</h3>
              
              <div className="space-y-4">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  disabled
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  Generate Share Link
                </Button>
                
                <p className="text-sm text-gray-600">
                  Share this template with other trainers in your organization
                </p>
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
      
      {/* Delete Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Template</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this template? This action cannot be undone.
              All assignments using this template will also be affected.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Duplicate Dialog */}
      <Dialog open={showDuplicateDialog} onOpenChange={setShowDuplicateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Duplicate Template</DialogTitle>
            <DialogDescription>
              Create a copy of this template. The duplicate will be created as a draft
              and you can edit it before publishing.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDuplicateDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleDuplicate}
              disabled={isDuplicating}
            >
              {isDuplicating ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
                  Duplicating...
                </>
              ) : (
                'Duplicate'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TrainerAssessmentTemplateDetailPage;