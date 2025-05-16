import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Calendar, User, Users, Clock, 
  Send, HelpCircle, ChevronRight
} from 'lucide-react';
import { format, addDays, addWeeks } from 'date-fns';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Label } from '@/components/ui';
import { useToast } from '@/components/ui/use-toast';
import { Table } from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { DatePicker } from '@/components/ui/date-picker';
import { Tabs } from '@/components/ui/tabs';

/**
 * TrainerAssignAssessmentPage allows trainers to assign assessments to courses, groups, or individuals
 */
const TrainerAssignAssessmentPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('course');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAssigning, setIsAssigning] = useState(false);
  
  // Template data
  const [template, setTemplate] = useState(null);
  
  // Assignment data
  const [assignmentTitle, setAssignmentTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState(null);
  const [availableFrom, setAvailableFrom] = useState(new Date());
  const [instructions, setInstructions] = useState('');
  
  // Recipients
  const [courses, setCourses] = useState([]);
  const [groups, setGroups] = useState([]);
  const [individuals, setIndividuals] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [selectedIndividuals, setSelectedIndividuals] = useState([]);
  
  // Settings
  const [settings, setSettings] = useState({
    attemptsAllowed: 1,
    passingScore: 70,
    allowLateSubmission: false,
    latePenalty: 5,
    notifyImmediately: true,
    reminderBeforeDue: true,
    showResultsAfterCompletion: true
  });
  
  // Load template and recipients data
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
        
        if (!templateResponse.ok) throw new Error('Failed to fetch template');
        const templateData = await templateResponse.json();
        
        if (!isMounted) return;
        setTemplate(templateData);
        
        // Set default values from template
        setAssignmentTitle(templateData.title);
        setDescription(templateData.description);
        setSettings(prev => ({
          ...prev,
          ...templateData.settings,
          attemptsAllowed: templateData.settings?.attemptsAllowed || 1,
          passingScore: templateData.settings?.passingScore || 70
        }));
        
        // Fetch available courses
        const coursesResponse = await fetch('/api/courses');
        if (!isMounted) return;
        
        if (!coursesResponse.ok) throw new Error('Failed to fetch courses');
        const coursesData = await coursesResponse.json();
        
        if (!isMounted) return;
        setCourses(coursesData);
        
        // Fetch available groups
        const groupsResponse = await fetch('/api/groups');
        if (!isMounted) return;
        
        if (!groupsResponse.ok) throw new Error('Failed to fetch groups');
        const groupsData = await groupsResponse.json();
        
        if (!isMounted) return;
        setGroups(groupsData);
        
        // Fetch individuals (students/trainees)
        const individualsResponse = await fetch('/api/users?role=student');
        if (!isMounted) return;
        
        if (!individualsResponse.ok) throw new Error('Failed to fetch students');
        const individualsData = await individualsResponse.json();
        
        if (!isMounted) return;
        setIndividuals(individualsData);
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Error fetching data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load assignment data',
          type: 'error',
        });
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    
    fetchData();
    
    return () => {
      isMounted = false;
    };
  }, [id, toast]);
  
  // Handle assignment
  const handleAssign = async () => {
    // Validate required fields
    if (!assignmentTitle.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter an assignment title',
        type: 'error',
      });
      return;
    }
    
    if (!dueDate) {
      toast({
        title: 'Error',
        description: 'Please select a due date',
        type: 'error',
      });
      return;
    }
    
    // Validate recipients
    const hasRecipients = selectedCourse || selectedGroups.length > 0 || selectedIndividuals.length > 0;
    if (!hasRecipients) {
      toast({
        title: 'Error',
        description: 'Please select at least one recipient',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsAssigning(true);
      
      const assignmentData = {
        template_id: id,
        title: assignmentTitle,
        description,
        due_date: dueDate.toISOString(),
        available_from: availableFrom.toISOString(),
        instructions,
        settings,
        recipients: {
          course_id: selectedCourse || null,
          group_ids: selectedGroups,
          individual_ids: selectedIndividuals
        },
        created_at: new Date().toISOString()
      };
      
      const response = await fetch('/api/assessment/assign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assignmentData),
      });
      
      if (!response.ok) throw new Error('Failed to assign assessment');
      
      const assignment = await response.json();
      
      toast({
        title: 'Success',
        description: 'Assessment assigned successfully',
        type: 'success',
      });
      
      navigate(`/assessment/assigned/${assignment.id}`);
    } catch (err) {
      console.error('Error assigning assessment:', err);
      toast({
        title: 'Error',
        description: 'Failed to assign assessment',
        type: 'error',
      });
    } finally {
      setIsAssigning(false);
    }
  };
  
  // Calculate total recipients
  const calculateTotalRecipients = () => {
    let total = 0;
    
    if (selectedCourse) {
      const course = courses.find(c => c.id === selectedCourse);
      total += course?.student_count || 0;
    }
    
    selectedGroups.forEach(groupId => {
      const group = groups.find(g => g.id === groupId);
      total += group?.member_count || 0;
    });
    
    total += selectedIndividuals.length;
    
    return total;
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
            <HelpCircle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Unable to Load Assignment Page</h2>
          <p className="text-gray-600 mb-4">
            {error || "The assessment template could not be found or has been deleted."}
          </p>
          <Button onClick={() => navigate('/assessment')}>Back to Assessments</Button>
        </Card>
      </div>
    );
  }
  
  const totalRecipients = calculateTotalRecipients();
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
            <h1 className="text-2xl font-bold">Assign Assessment</h1>
            <p className="text-gray-600">{template.title}</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => navigate(`/assessment/templates/${id}`)}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAssign}
            disabled={isAssigning || !totalRecipients}
          >
            {isAssigning ? (
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            Assign to {totalRecipients} {totalRecipients === 1 ? 'Student' : 'Students'}
          </Button>
        </div>
      </div>
      
      {/* Assessment info card */}
      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-semibold">{template.title}</h3>
              <Badge className={isQuiz ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                {template.type}
              </Badge>
            </div>
            <p className="text-gray-600 mb-3">{template.description}</p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              {isQuiz ? (
                <>
                  <span>{template.questions?.length || 0} questions</span>
                  <span>{template.questions?.reduce((sum, q) => sum + q.points, 0) || 0} points</span>
                  {template.settings?.timeLimit && (
                    <span>{template.settings.timeLimit} minutes</span>
                  )}
                </>
              ) : (
                <>
                  <span>{template.requirements?.length || 0} requirements</span>
                  <span>{template.requirements?.reduce((sum, r) => sum + r.points, 0) || 0} points</span>
                </>
              )}
            </div>
          </div>
        </div>
      </Card>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Assignment Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Assignment Details</h3>
            
            <div className="space-y-4">
              {/* Title */}
              <div>
                <Label htmlFor="title">Assignment Title *</Label>
                <Input
                  id="title"
                  value={assignmentTitle}
                  onChange={(e) => setAssignmentTitle(e.target.value)}
                  placeholder="Enter a title for this assignment"
                  className="mt-1"
                />
              </div>
              
              {/* Description */}
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Provide additional context for this assignment"
                  rows={3}
                  className="mt-1"
                />
              </div>
              
              {/* Due Date */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="available">Available From</Label>
                  <DatePicker
                    id="available"
                    value={availableFrom}
                    onChange={setAvailableFrom}
                    minDate={new Date()}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="due">Due Date *</Label>
                  <DatePicker
                    id="due"
                    value={dueDate}
                    onChange={setDueDate}
                    minDate={availableFrom || new Date()}
                    className="mt-1"
                  />
                </div>
              </div>
              
              {/* Quick date options */}
              <div className="flex gap-2">
                <span className="text-sm text-gray-600">Quick set:</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDueDate(addDays(new Date(), 7))}
                >
                  1 week
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDueDate(addWeeks(new Date(), 2))}
                >
                  2 weeks
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDueDate(addWeeks(new Date(), 4))}
                >
                  1 month
                </Button>
              </div>
              
              {/* Instructions */}
              <div>
                <Label htmlFor="instructions">Instructions for Students</Label>
                <Textarea
                  id="instructions"
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Add any specific instructions or guidelines for this assignment"
                  rows={4}
                  className="mt-1"
                />
              </div>
            </div>
          </Card>
          
          {/* Recipients */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Recipients</h3>
            
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="mb-4"
            >
              <Tabs.TabsList>
                <Tabs.TabTrigger value="course">
                  <Users className="w-4 h-4 mr-2" />
                  Course
                </Tabs.TabTrigger>
                <Tabs.TabTrigger value="groups">
                  <Users className="w-4 h-4 mr-2" />
                  Groups
                </Tabs.TabTrigger>
                <Tabs.TabTrigger value="individuals">
                  <User className="w-4 h-4 mr-2" />
                  Individuals
                </Tabs.TabTrigger>
              </Tabs.TabsList>
              
              {/* Course Tab */}
              <Tabs.TabContent value="course">
                <div>
                  <Label htmlFor="course">Select Course</Label>
                  <Select
                    id="course"
                    value={selectedCourse}
                    onValueChange={setSelectedCourse}
                    className="mt-1"
                  >
                    <Select.Option value="">Select a course</Select.Option>
                    {courses.map(course => (
                      <Select.Option key={course.id} value={course.id}>
                        {course.name} ({course.student_count} students)
                      </Select.Option>
                    ))}
                  </Select>
                  
                  {selectedCourse && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">
                        Assignment will be given to all {courses.find(c => c.id === selectedCourse)?.student_count} students 
                        in {courses.find(c => c.id === selectedCourse)?.name}
                      </p>
                    </div>
                  )}
                </div>
              </Tabs.TabContent>
              
              {/* Groups Tab */}
              <Tabs.TabContent value="groups">
                <div>
                  <Label>Select Groups</Label>
                  <div className="mt-2 space-y-2 max-h-60 overflow-y-auto">
                    {groups.length > 0 ? (
                      groups.map(group => (
                        <label
                          key={group.id}
                          className="flex items-center p-3 rounded-lg border hover:bg-gray-50 cursor-pointer"
                        >
                          <Checkbox
                            checked={selectedGroups.includes(group.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedGroups([...selectedGroups, group.id]);
                              } else {
                                setSelectedGroups(selectedGroups.filter(g => g !== group.id));
                              }
                            }}
                            className="mr-3"
                          />
                          <div className="flex-1">
                            <p className="font-medium">{group.name}</p>
                            <p className="text-sm text-gray-600">{group.member_count} members</p>
                          </div>
                        </label>
                      ))
                    ) : (
                      <p className="text-gray-500 text-center py-4">No groups available</p>
                    )}
                  </div>
                  
                  {selectedGroups.length > 0 && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">
                        Selected {selectedGroups.length} group{selectedGroups.length > 1 ? 's' : ''} 
                        ({groups.filter(g => selectedGroups.includes(g.id)).reduce((sum, g) => sum + g.member_count, 0)} students)
                      </p>
                    </div>
                  )}
                </div>
              </Tabs.TabContent>
              
              {/* Individuals Tab */}
              <Tabs.TabContent value="individuals">
                <div>
                  <Label>Select Students</Label>
                  <div className="mb-3">
                    <Input
                      placeholder="Search students..."
                      className="w-full"
                    />
                  </div>
                  
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {individuals.length > 0 ? (
                      individuals.map(individual => (
                        <label
                          key={individual.id}
                          className="flex items-center p-3 rounded-lg border hover:bg-gray-50 cursor-pointer"
                        >
                          <Checkbox
                            checked={selectedIndividuals.includes(individual.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedIndividuals([...selectedIndividuals, individual.id]);
                              } else {
                                setSelectedIndividuals(selectedIndividuals.filter(i => i !== individual.id));
                              }
                            }}
                            className="mr-3"
                          />
                          <div className="flex-1">
                            <p className="font-medium">{individual.name}</p>
                            <p className="text-sm text-gray-600">{individual.email}</p>
                          </div>
                        </label>
                      ))
                    ) : (
                      <p className="text-gray-500 text-center py-4">No students available</p>
                    )}
                  </div>
                  
                  {selectedIndividuals.length > 0 && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">
                        Selected {selectedIndividuals.length} student{selectedIndividuals.length > 1 ? 's' : ''}
                      </p>
                    </div>
                  )}
                </div>
              </Tabs.TabContent>
            </Tabs>
          </Card>
        </div>
        
        {/* Settings Sidebar */}
        <div className="space-y-6">
          {/* Assignment Settings */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Assignment Settings</h3>
            
            <div className="space-y-4">
              {/* Attempts */}
              <div>
                <Label htmlFor="attempts">Attempts Allowed</Label>
                <Input
                  id="attempts"
                  type="number"
                  value={settings.attemptsAllowed}
                  onChange={(e) => setSettings({ ...settings, attemptsAllowed: Number(e.target.value) })}
                  min="1"
                  className="mt-1"
                />
              </div>
              
              {/* Passing Score */}
              <div>
                <Label htmlFor="passing">Passing Score (%)</Label>
                <Input
                  id="passing"
                  type="number"
                  value={settings.passingScore}
                  onChange={(e) => setSettings({ ...settings, passingScore: Number(e.target.value) })}
                  min="0"
                  max="100"
                  className="mt-1"
                />
              </div>
              
              {/* Late Submission */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="late">Allow Late Submission</Label>
                  <input
                    id="late"
                    type="checkbox"
                    checked={settings.allowLateSubmission}
                    onChange={(e) => setSettings({ ...settings, allowLateSubmission: e.target.checked })}
                    className="h-4 w-4 rounded border-gray-300"
                  />
                </div>
                
                {settings.allowLateSubmission && (
                  <div>
                    <Label htmlFor="penalty">Late Penalty (% per day)</Label>
                    <Input
                      id="penalty"
                      type="number"
                      value={settings.latePenalty}
                      onChange={(e) => setSettings({ ...settings, latePenalty: Number(e.target.value) })}
                      min="0"
                      max="100"
                      className="mt-1"
                    />
                  </div>
                )}
              </div>
              
              {/* Show Results */}
              <div className="flex items-center justify-between">
                <Label htmlFor="results">Show Results After Completion</Label>
                <input
                  id="results"
                  type="checkbox"
                  checked={settings.showResultsAfterCompletion}
                  onChange={(e) => setSettings({ ...settings, showResultsAfterCompletion: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>
          </Card>
          
          {/* Notification Settings */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Notifications</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="notify">Notify Students Immediately</Label>
                <input
                  id="notify"
                  type="checkbox"
                  checked={settings.notifyImmediately}
                  onChange={(e) => setSettings({ ...settings, notifyImmediately: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="reminder">Send Reminder Before Due</Label>
                <input
                  id="reminder"
                  type="checkbox"
                  checked={settings.reminderBeforeDue}
                  onChange={(e) => setSettings({ ...settings, reminderBeforeDue: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300"
                />
              </div>
            </div>
          </Card>
          
          {/* Summary */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Assignment Summary</h3>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Recipients</span>
                <span className="font-medium">{totalRecipients} students</span>
              </div>
              
              {dueDate && (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Due Date</span>
                    <span className="font-medium">{format(dueDate, 'MMM d, yyyy')}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Duration</span>
                    <span className="font-medium">
                      {Math.ceil((dueDate - (availableFrom || new Date())) / (1000 * 60 * 60 * 24))} days
                    </span>
                  </div>
                </>
              )}
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Attempts</span>
                <span className="font-medium">{settings.attemptsAllowed}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Passing Score</span>
                <span className="font-medium">{settings.passingScore}%</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TrainerAssignAssessmentPage;