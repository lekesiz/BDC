import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Users, Calendar, Clock, CheckCircle, 
  AlertCircle, FileText, Send, Settings, BarChart2, 
  Edit2, Trash2, RefreshCw, Download
} from 'lucide-react';
import { format, differenceInDays, isPast } from 'date-fns';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { Table } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui';
import { Input } from '@/components/ui/input';
import { DatePicker } from '@/components/ui/date-picker';

/**
 * TrainerAssignedAssessmentDetailPage displays detailed information about an assigned assessment
 * and provides management options for trainers
 */
const TrainerAssignedAssessmentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for assignment data
  const [assignment, setAssignment] = useState(null);
  const [template, setTemplate] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [recipients, setRecipients] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  
  // State for dialogs
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showExtendDialog, setShowExtendDialog] = useState(false);
  const [showReminderDialog, setShowReminderDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSending, setIsSending] = useState(false);
  
  // Extension form state
  const [newDueDate, setNewDueDate] = useState(null);
  const [extensionReason, setExtensionReason] = useState('');
  
  // Reminder form state
  const [reminderMessage, setReminderMessage] = useState('');
  
  // Fetch data
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        if (!isMounted) return;
        
        setIsLoading(true);
        setError(null);
        
        // Fetch assignment details
        const assignmentResponse = await fetch(`/api/assessment/assigned/${id}`);
        if (!isMounted) return;
        
        if (!assignmentResponse.ok) throw new Error('Failed to fetch assignment details');
        const assignmentData = await assignmentResponse.json();
        
        if (!isMounted) return;
        setAssignment(assignmentData);
        setNewDueDate(new Date(assignmentData.due_date));
        
        // Fetch template details
        const templateResponse = await fetch(`/api/assessment/templates/${assignmentData.template_id}`);
        if (!isMounted) return;
        
        if (!templateResponse.ok) throw new Error('Failed to fetch template details');
        const templateData = await templateResponse.json();
        
        if (!isMounted) return;
        setTemplate(templateData);
        
        // Fetch submissions
        const submissionsResponse = await fetch(`/api/assessment/assigned/${id}/submissions`);
        if (!isMounted) return;
        
        if (!submissionsResponse.ok) throw new Error('Failed to fetch submissions');
        const submissionsData = await submissionsResponse.json();
        
        if (!isMounted) return;
        setSubmissions(submissionsData);
        
        // Fetch recipients
        const recipientsResponse = await fetch(`/api/assessment/assigned/${id}/recipients`);
        if (!isMounted) return;
        
        if (!recipientsResponse.ok) throw new Error('Failed to fetch recipients');
        const recipientsData = await recipientsResponse.json();
        
        if (!isMounted) return;
        setRecipients(recipientsData);
        
        // Fetch analytics
        const analyticsResponse = await fetch(`/api/assessment/assigned/${id}/analytics`);
        if (!isMounted) return;
        
        if (!analyticsResponse.ok) throw new Error('Failed to fetch analytics');
        const analyticsData = await analyticsResponse.json();
        
        if (!isMounted) return;
        setAnalytics(analyticsData);
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Error fetching assignment data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load assignment details',
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
  
  // Handle assignment deletion
  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      
      const response = await fetch(`/api/assessment/assigned/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete assignment');
      
      toast({
        title: 'Success',
        description: 'Assignment deleted successfully',
        type: 'success',
      });
      
      navigate('/assessment');
    } catch (err) {
      console.error('Error deleting assignment:', err);
      toast({
        title: 'Error',
        description: 'Failed to delete assignment',
        type: 'error',
      });
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
    }
  };
  
  // Handle due date extension
  const handleExtendDueDate = async () => {
    if (!newDueDate || !extensionReason.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a new due date and reason',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsSending(true);
      
      const response = await fetch(`/api/assessment/assigned/${id}/extend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_due_date: newDueDate.toISOString(),
          reason: extensionReason,
        }),
      });
      
      if (!response.ok) throw new Error('Failed to extend due date');
      
      const updatedAssignment = await response.json();
      setAssignment(updatedAssignment);
      
      toast({
        title: 'Success',
        description: 'Due date extended successfully',
        type: 'success',
      });
      
      setShowExtendDialog(false);
      setExtensionReason('');
    } catch (err) {
      console.error('Error extending due date:', err);
      toast({
        title: 'Error',
        description: 'Failed to extend due date',
        type: 'error',
      });
    } finally {
      setIsSending(false);
    }
  };
  
  // Handle sending reminder
  const handleSendReminder = async () => {
    if (!reminderMessage.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a reminder message',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsSending(true);
      
      const response = await fetch(`/api/assessment/assigned/${id}/remind`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: reminderMessage,
          recipients: 'pending', // Send to students who haven't submitted
        }),
      });
      
      if (!response.ok) throw new Error('Failed to send reminder');
      
      toast({
        title: 'Success',
        description: 'Reminder sent successfully',
        type: 'success',
      });
      
      setShowReminderDialog(false);
      setReminderMessage('');
    } catch (err) {
      console.error('Error sending reminder:', err);
      toast({
        title: 'Error',
        description: 'Failed to send reminder',
        type: 'error',
      });
    } finally {
      setIsSending(false);
    }
  };
  
  // Calculate status
  const calculateStatus = () => {
    if (!assignment) return 'loading';
    
    const now = new Date();
    const dueDate = new Date(assignment.due_date);
    const availableFrom = new Date(assignment.available_from);
    
    if (now < availableFrom) return 'scheduled';
    if (now > dueDate) return 'overdue';
    
    const completionRate = (submissions.length / recipients.length) * 100;
    if (completionRate === 100) return 'completed';
    
    return 'active';
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
  if (error || !assignment || !template) {
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
            <AlertCircle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Assignment Not Found</h2>
          <p className="text-gray-600 mb-4">
            {error || "The requested assignment could not be found or has been deleted."}
          </p>
          <Button onClick={() => navigate('/assessment')}>Back to Assessments</Button>
        </Card>
      </div>
    );
  }
  
  // Calculate metrics
  const status = calculateStatus();
  const completionRate = recipients.length > 0 
    ? Math.round((submissions.length / recipients.length) * 100) 
    : 0;
  const daysRemaining = differenceInDays(new Date(assignment.due_date), new Date());
  const isOverdue = isPast(new Date(assignment.due_date));
  const averageScore = analytics?.average_score || 0;
  const passRate = analytics?.pass_rate || 0;
  
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
            <h1 className="text-2xl font-bold">{assignment.title}</h1>
            <p className="text-gray-600">{template.title}</p>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={() => navigate(`/assessment/assigned/${id}/results`)}
            className="flex items-center"
          >
            <BarChart2 className="w-4 h-4 mr-2" />
            View Results
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowReminderDialog(true)}
            className="flex items-center"
          >
            <Send className="w-4 h-4 mr-2" />
            Send Reminder
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowExtendDialog(true)}
            className="flex items-center"
          >
            <Calendar className="w-4 h-4 mr-2" />
            Extend Due Date
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate(`/assessment/assigned/${id}/edit`)}
            className="flex items-center"
          >
            <Edit2 className="w-4 h-4 mr-2" />
            Edit
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
      
      {/* Status Banner */}
      <Card className={`p-4 mb-6 ${
        status === 'completed' ? 'bg-green-50 border-green-200' :
        status === 'overdue' ? 'bg-red-50 border-red-200' :
        status === 'active' ? 'bg-blue-50 border-blue-200' :
        'bg-gray-50 border-gray-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {status === 'completed' ? (
              <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
            ) : status === 'overdue' ? (
              <AlertCircle className="w-6 h-6 text-red-600 mr-3" />
            ) : (
              <Clock className="w-6 h-6 text-blue-600 mr-3" />
            )}
            <div>
              <h3 className="font-semibold">
                {status === 'completed' ? 'Assignment Completed' :
                 status === 'overdue' ? 'Assignment Overdue' :
                 status === 'scheduled' ? 'Assignment Scheduled' :
                 'Assignment Active'}
              </h3>
              <p className="text-sm text-gray-600">
                {status === 'overdue' 
                  ? `Due date passed ${Math.abs(daysRemaining)} days ago`
                  : status === 'scheduled'
                  ? `Will be available from ${format(new Date(assignment.available_from), 'MMM d, yyyy')}`
                  : `${daysRemaining} days remaining`}
              </p>
            </div>
          </div>
          <Badge className={
            status === 'completed' ? 'bg-green-100 text-green-800' :
            status === 'overdue' ? 'bg-red-100 text-red-800' :
            status === 'active' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }>
            {status}
          </Badge>
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
          <Tabs.TabTrigger value="recipients">
            <Users className="w-4 h-4 mr-2" />
            Recipients ({recipients.length})
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="submissions">
            <FileText className="w-4 h-4 mr-2" />
            Submissions ({submissions.length})
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="settings">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        
        {/* Overview Tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Assignment Details */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-primary" />
                Assignment Details
              </h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Type</p>
                  <Badge className={template.type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                    {template.type}
                  </Badge>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Available From</p>
                  <p className="font-medium">{format(new Date(assignment.available_from), "MMM d, yyyy 'at' h:mm a")}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Due Date</p>
                  <p className="font-medium">{format(new Date(assignment.due_date), "MMM d, yyyy 'at' h:mm a")}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Created By</p>
                  <p className="font-medium">{assignment.created_by}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600">Total Points</p>
                  <p className="font-medium">
                    {template.type === 'quiz' 
                      ? template.questions?.reduce((sum, q) => sum + q.points, 0) || 0
                      : template.totalPoints || 100} points
                  </p>
                </div>
              </div>
            </Card>
            
            {/* Progress Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart2 className="w-5 h-5 mr-2 text-primary" />
                Progress
              </h3>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">Completion Rate</span>
                    <span className="text-sm text-gray-500">
                      {submissions.length} / {recipients.length} students
                    </span>
                  </div>
                  <Progress value={completionRate} className="h-2" />
                  <p className="text-sm text-gray-600 mt-1">{completionRate}% completed</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Submitted</p>
                    <p className="text-xl font-bold text-green-600">{submissions.length}</p>
                  </div>
                  
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Pending</p>
                    <p className="text-xl font-bold text-amber-600">
                      {recipients.length - submissions.length}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
            
            {/* Performance Card */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart2 className="w-5 h-5 mr-2 text-primary" />
                Performance
              </h3>
              
              <div className="space-y-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Average Score</p>
                  <p className="text-xl font-bold text-blue-600">
                    {averageScore ? `${averageScore}%` : 'N/A'}
                  </p>
                </div>
                
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Pass Rate</p>
                  <p className="text-xl font-bold text-green-600">
                    {passRate ? `${passRate}%` : 'N/A'}
                  </p>
                </div>
                
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Average Time</p>
                  <p className="text-xl font-bold">
                    {analytics?.average_time_spent ? `${analytics.average_time_spent} min` : 'N/A'}
                  </p>
                </div>
              </div>
            </Card>
            
            {/* Instructions Card */}
            {assignment.instructions && (
              <Card className="p-6 lg:col-span-3">
                <h3 className="text-lg font-semibold mb-4">Instructions</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{assignment.instructions}</p>
              </Card>
            )}
          </div>
        </Tabs.TabContent>
        
        {/* Recipients Tab */}
        <Tabs.TabContent value="recipients">
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Recipients List</h3>
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
            
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Name</Table.HeaderCell>
                  <Table.HeaderCell>Email</Table.HeaderCell>
                  <Table.HeaderCell>Status</Table.HeaderCell>
                  <Table.HeaderCell>Submitted</Table.HeaderCell>
                  <Table.HeaderCell>Score</Table.HeaderCell>
                  <Table.HeaderCell>Time Spent</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {recipients.map(recipient => {
                  const submission = submissions.find(s => s.student_id === recipient.id);
                  
                  return (
                    <Table.Row key={recipient.id}>
                      <Table.Cell>{recipient.name}</Table.Cell>
                      <Table.Cell>{recipient.email}</Table.Cell>
                      <Table.Cell>
                        <Badge className={
                          submission?.status === 'completed' ? 'bg-green-100 text-green-800' :
                          submission?.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }>
                          {submission?.status || 'Not Started'}
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>
                        {submission?.submitted_at 
                          ? format(new Date(submission.submitted_at), 'MMM d, yyyy h:mm a')
                          : '-'}
                      </Table.Cell>
                      <Table.Cell>
                        {submission?.score !== undefined 
                          ? `${submission.score}%`
                          : '-'}
                      </Table.Cell>
                      <Table.Cell>
                        {submission?.time_spent 
                          ? `${submission.time_spent} min`
                          : '-'}
                      </Table.Cell>
                    </Table.Row>
                  );
                })}
              </Table.Body>
            </Table>
          </Card>
        </Tabs.TabContent>
        
        {/* Submissions Tab */}
        <Tabs.TabContent value="submissions">
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Submissions</h3>
              <div className="flex gap-2">
                <Button variant="outline">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
            
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Student</Table.HeaderCell>
                  <Table.HeaderCell>Submitted</Table.HeaderCell>
                  <Table.HeaderCell>Score</Table.HeaderCell>
                  <Table.HeaderCell>Status</Table.HeaderCell>
                  <Table.HeaderCell>Time Spent</Table.HeaderCell>
                  <Table.HeaderCell>Actions</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {submissions.map(submission => (
                  <Table.Row key={submission.id}>
                    <Table.Cell>
                      <div>
                        <p className="font-medium">{submission.student_name}</p>
                        <p className="text-sm text-gray-600">{submission.student_email}</p>
                      </div>
                    </Table.Cell>
                    <Table.Cell>
                      {format(new Date(submission.submitted_at), 'MMM d, yyyy h:mm a')}
                    </Table.Cell>
                    <Table.Cell>
                      <div className="flex items-center">
                        <span className="font-medium">
                          {submission.score !== undefined ? `${submission.score}%` : 'Pending'}
                        </span>
                        {submission.passed !== undefined && (
                          <Badge className={`ml-2 ${submission.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {submission.passed ? 'Passed' : 'Failed'}
                          </Badge>
                        )}
                      </div>
                    </Table.Cell>
                    <Table.Cell>
                      <Badge className={
                        submission.status === 'graded' ? 'bg-green-100 text-green-800' :
                        submission.status === 'submitted' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }>
                        {submission.status}
                      </Badge>
                    </Table.Cell>
                    <Table.Cell>{submission.time_spent} min</Table.Cell>
                    <Table.Cell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/assessment/submissions/${submission.id}`)}
                      >
                        View
                      </Button>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
            
            {submissions.length === 0 && (
              <p className="text-gray-500 text-center py-8">
                No submissions yet
              </p>
            )}
          </Card>
        </Tabs.TabContent>
        
        {/* Settings Tab */}
        <Tabs.TabContent value="settings">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Assignment Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Assignment Settings</h3>
              
              <Table>
                <Table.Body>
                  <Table.Row>
                    <Table.Cell className="font-medium">Attempts Allowed</Table.Cell>
                    <Table.Cell>{assignment.settings?.attemptsAllowed || 1}</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Passing Score</Table.Cell>
                    <Table.Cell>{assignment.settings?.passingScore || 70}%</Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Allow Late Submission</Table.Cell>
                    <Table.Cell>
                      {assignment.settings?.allowLateSubmission ? 'Yes' : 'No'}
                    </Table.Cell>
                  </Table.Row>
                  {assignment.settings?.allowLateSubmission && (
                    <Table.Row>
                      <Table.Cell className="font-medium">Late Penalty</Table.Cell>
                      <Table.Cell>{assignment.settings?.latePenalty || 0}% per day</Table.Cell>
                    </Table.Row>
                  )}
                  <Table.Row>
                    <Table.Cell className="font-medium">Show Results</Table.Cell>
                    <Table.Cell>
                      {assignment.settings?.showResultsAfterCompletion ? 'After completion' : 'After grading'}
                    </Table.Cell>
                  </Table.Row>
                </Table.Body>
              </Table>
            </Card>
            
            {/* Assessment Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Assessment Settings</h3>
              
              <Table>
                <Table.Body>
                  {template.type === 'quiz' && (
                    <>
                      <Table.Row>
                        <Table.Cell className="font-medium">Time Limit</Table.Cell>
                        <Table.Cell>
                          {template.settings?.timeLimit ? `${template.settings.timeLimit} minutes` : 'No limit'}
                        </Table.Cell>
                      </Table.Row>
                      <Table.Row>
                        <Table.Cell className="font-medium">Shuffle Questions</Table.Cell>
                        <Table.Cell>
                          {template.settings?.shuffleQuestions ? 'Yes' : 'No'}
                        </Table.Cell>
                      </Table.Row>
                      <Table.Row>
                        <Table.Cell className="font-medium">Show Correct Answers</Table.Cell>
                        <Table.Cell>
                          {template.settings?.showCorrectAnswers ? 'Yes' : 'No'}
                        </Table.Cell>
                      </Table.Row>
                    </>
                  )}
                  <Table.Row>
                    <Table.Cell className="font-medium">Auto-grading</Table.Cell>
                    <Table.Cell>
                      {template.settings?.autoGrade ? 'Enabled' : 'Disabled'}
                    </Table.Cell>
                  </Table.Row>
                </Table.Body>
              </Table>
            </Card>
            
            {/* Notification Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Notifications</h3>
              
              <Table>
                <Table.Body>
                  <Table.Row>
                    <Table.Cell className="font-medium">Initial Notification</Table.Cell>
                    <Table.Cell>
                      {assignment.settings?.notifyImmediately ? 'Sent' : 'Not sent'}
                    </Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Reminder Before Due</Table.Cell>
                    <Table.Cell>
                      {assignment.settings?.reminderBeforeDue ? 'Enabled' : 'Disabled'}
                    </Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Submission Notification</Table.Cell>
                    <Table.Cell>
                      {template.settings?.notifyOnSubmission ? 'Enabled' : 'Disabled'}
                    </Table.Cell>
                  </Table.Row>
                  <Table.Row>
                    <Table.Cell className="font-medium">Grading Notification</Table.Cell>
                    <Table.Cell>
                      {template.settings?.notifyOnGrade ? 'Enabled' : 'Disabled'}
                    </Table.Cell>
                  </Table.Row>
                </Table.Body>
              </Table>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
      
      {/* Delete Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Assignment</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this assignment? This will remove it for all
              recipients and delete all submissions. This action cannot be undone.
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
      
      {/* Extend Due Date Dialog */}
      <Dialog open={showExtendDialog} onOpenChange={setShowExtendDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Extend Due Date</DialogTitle>
            <DialogDescription>
              Extend the due date for this assignment. All recipients will be notified.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="newDueDate">New Due Date</Label>
              <DatePicker
                id="newDueDate"
                value={newDueDate}
                onChange={setNewDueDate}
                minDate={new Date()}
                className="mt-1"
              />
              <p className="text-sm text-gray-600 mt-1">
                Current due date: {format(new Date(assignment.due_date), 'MMM d, yyyy')}
              </p>
            </div>
            
            <div>
              <Label htmlFor="reason">Reason for Extension</Label>
              <Textarea
                id="reason"
                value={extensionReason}
                onChange={(e) => setExtensionReason(e.target.value)}
                placeholder="Explain why the due date is being extended"
                rows={3}
                className="mt-1"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExtendDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleExtendDueDate}
              disabled={isSending}
            >
              {isSending ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
                  Extending...
                </>
              ) : (
                'Extend Due Date'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Send Reminder Dialog */}
      <Dialog open={showReminderDialog} onOpenChange={setShowReminderDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send Reminder</DialogTitle>
            <DialogDescription>
              Send a reminder to students who haven't submitted yet ({recipients.length - submissions.length} students).
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4">
            <Label htmlFor="reminder">Reminder Message</Label>
            <Textarea
              id="reminder"
              value={reminderMessage}
              onChange={(e) => setReminderMessage(e.target.value)}
              placeholder="Enter a custom reminder message for students"
              rows={4}
              className="mt-1"
            />
            
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                Default information will be included: assignment title, due date, and a link to the assessment.
              </p>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReminderDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSendReminder}
              disabled={isSending}
            >
              {isSending ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
                  Sending...
                </>
              ) : (
                'Send Reminder'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TrainerAssignedAssessmentDetailPage;