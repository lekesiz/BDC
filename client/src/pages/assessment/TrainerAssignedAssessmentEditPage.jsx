import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Save, Calendar, Clock, AlertCircle
} from 'lucide-react';
import { format } from 'date-fns';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Label } from '@/components/ui';
import { useToast } from '@/components/ui/use-toast';
import { DatePicker } from '@/components/ui/date-picker';
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
 * TrainerAssignedAssessmentEditPage allows trainers to edit assigned assessment settings
 */
const TrainerAssignedAssessmentEditPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  
  // State for assignment data
  const [originalAssignment, setOriginalAssignment] = useState(null);
  const [template, setTemplate] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState(null);
  const [availableFrom, setAvailableFrom] = useState(null);
  const [instructions, setInstructions] = useState('');
  
  // Settings state
  const [settings, setSettings] = useState({
    attemptsAllowed: 1,
    passingScore: 70,
    allowLateSubmission: false,
    latePenalty: 5,
    showResultsAfterCompletion: true,
    notifyImmediately: true,
    reminderBeforeDue: true
  });
  
  // Dialog state
  const [showDiscardDialog, setShowDiscardDialog] = useState(false);
  
  // Load assignment data
  useEffect(() => {
    let isMounted = true;
    
    const fetchAssignment = async () => {
      try {
        if (!isMounted) return;
        
        setIsLoading(true);
        setError(null);
        
        // Fetch assignment details
        const assignmentResponse = await fetch(`/api/assessment/assigned/${id}`);
        if (!isMounted) return;
        
        if (!assignmentResponse.ok) throw new Error('Failed to fetch assignment');
        const assignmentData = await assignmentResponse.json();
        
        if (!isMounted) return;
        setOriginalAssignment(assignmentData);
        
        // Initialize form fields
        setTitle(assignmentData.title || '');
        setDescription(assignmentData.description || '');
        setDueDate(new Date(assignmentData.due_date));
        setAvailableFrom(new Date(assignmentData.available_from));
        setInstructions(assignmentData.instructions || '');
        setSettings({
          ...settings,
          ...assignmentData.settings
        });
        
        // Fetch template details
        const templateResponse = await fetch(`/api/assessment/templates/${assignmentData.template_id}`);
        if (!isMounted) return;
        
        if (!templateResponse.ok) throw new Error('Failed to fetch template');
        const templateData = await templateResponse.json();
        
        if (!isMounted) return;
        setTemplate(templateData);
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Error fetching assignment:', err);
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
    
    fetchAssignment();
    
    return () => {
      isMounted = false;
    };
  }, [id, toast]);
  
  // Check if there are unsaved changes
  const hasUnsavedChanges = () => {
    if (!originalAssignment) return false;
    
    return (
      title !== originalAssignment.title ||
      description !== originalAssignment.description ||
      dueDate?.toISOString() !== originalAssignment.due_date ||
      availableFrom?.toISOString() !== originalAssignment.available_from ||
      instructions !== originalAssignment.instructions ||
      JSON.stringify(settings) !== JSON.stringify(originalAssignment.settings)
    );
  };
  
  // Handle navigation with unsaved changes
  const handleNavigate = (path) => {
    if (hasUnsavedChanges()) {
      setShowDiscardDialog(true);
    } else {
      navigate(path);
    }
  };
  
  // Handle save
  const handleSave = async () => {
    // Validate required fields
    if (!title.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a title',
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
    
    if (!availableFrom) {
      toast({
        title: 'Error',
        description: 'Please select an available from date',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsSaving(true);
      
      const updatedAssignment = {
        title,
        description,
        due_date: dueDate.toISOString(),
        available_from: availableFrom.toISOString(),
        instructions,
        settings,
        updated_at: new Date().toISOString()
      };
      
      const response = await fetch(`/api/assessment/assigned/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedAssignment),
      });
      
      if (!response.ok) throw new Error('Failed to update assignment');
      
      const updated = await response.json();
      setOriginalAssignment(updated);
      
      toast({
        title: 'Success',
        description: 'Assignment updated successfully',
        type: 'success',
      });
      
      navigate(`/assessment/assigned/${id}`);
    } catch (err) {
      console.error('Error updating assignment:', err);
      toast({
        title: 'Error',
        description: 'Failed to update assignment',
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
  if (error || !originalAssignment || !template) {
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
  
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <Button
            variant="ghost"
            onClick={() => handleNavigate(`/assessment/assigned/${id}`)}
            className="flex items-center mr-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Assignment
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Edit Assignment</h1>
            <p className="text-gray-600">{template.title}</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => handleNavigate(`/assessment/assigned/${id}`)}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving || !hasUnsavedChanges()}
          >
            {isSaving ? (
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save Changes
          </Button>
        </div>
      </div>
      
      {/* Template info card */}
      <Card className="p-6 mb-6 bg-gray-50">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-2">{template.title}</h3>
            <p className="text-gray-600 mb-3">{template.description}</p>
            <div className="flex items-center gap-3">
              <Badge className={template.type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                {template.type}
              </Badge>
              {template.type === 'quiz' ? (
                <>
                  <span className="text-sm text-gray-500">{template.questions?.length || 0} questions</span>
                  <span className="text-sm text-gray-500">•</span>
                  <span className="text-sm text-gray-500">{template.questions?.reduce((sum, q) => sum + q.points, 0) || 0} points</span>
                </>
              ) : (
                <>
                  <span className="text-sm text-gray-500">{template.requirements?.length || 0} requirements</span>
                  <span className="text-sm text-gray-500">•</span>
                  <span className="text-sm text-gray-500">{template.totalPoints || 100} points</span>
                </>
              )}
            </div>
          </div>
        </div>
      </Card>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Assignment Details */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Assignment Details</h3>
            
            <div className="space-y-4">
              {/* Title */}
              <div>
                <Label htmlFor="title">Assignment Title *</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter assignment title"
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
              
              {/* Dates */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="available">Available From *</Label>
                  <DatePicker
                    id="available"
                    value={availableFrom}
                    onChange={setAvailableFrom}
                    className="mt-1"
                  />
                  <p className="text-sm text-gray-600 mt-1">
                    Current: {originalAssignment && format(new Date(originalAssignment.available_from), 'MMM d, yyyy')}
                  </p>
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
                  <p className="text-sm text-gray-600 mt-1">
                    Current: {originalAssignment && format(new Date(originalAssignment.due_date), 'MMM d, yyyy')}
                  </p>
                </div>
              </div>
              
              {/* Instructions */}
              <div>
                <Label htmlFor="instructions">Instructions for Students</Label>
                <Textarea
                  id="instructions"
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Add any specific instructions or guidelines"
                  rows={4}
                  className="mt-1"
                />
              </div>
            </div>
          </Card>
        </div>
        
        {/* Settings */}
        <div className="space-y-6">
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
                  <Switch
                    id="late"
                    checked={settings.allowLateSubmission}
                    onCheckedChange={(checked) => setSettings({ ...settings, allowLateSubmission: checked })}
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
                <Switch
                  id="results"
                  checked={settings.showResultsAfterCompletion}
                  onCheckedChange={(checked) => setSettings({ ...settings, showResultsAfterCompletion: checked })}
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
                <Switch
                  id="notify"
                  checked={settings.notifyImmediately}
                  onCheckedChange={(checked) => setSettings({ ...settings, notifyImmediately: checked })}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="reminder">Send Reminder Before Due</Label>
                <Switch
                  id="reminder"
                  checked={settings.reminderBeforeDue}
                  onCheckedChange={(checked) => setSettings({ ...settings, reminderBeforeDue: checked })}
                />
              </div>
            </div>
          </Card>
          
          {/* Status Info */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Assignment Status</h3>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Created</p>
                <p className="font-medium">
                  {format(new Date(originalAssignment.created_at), "MMM d, yyyy 'at' h:mm a")}
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-600">Last Updated</p>
                <p className="font-medium">
                  {originalAssignment.updated_at 
                    ? format(new Date(originalAssignment.updated_at), "MMM d, yyyy 'at' h:mm a")
                    : 'Never'}
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-600">Created By</p>
                <p className="font-medium">{originalAssignment.created_by}</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
      
      {/* Discard Changes Dialog */}
      <Dialog open={showDiscardDialog} onOpenChange={setShowDiscardDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Discard Changes?</DialogTitle>
            <DialogDescription>
              You have unsaved changes. Are you sure you want to leave without saving?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDiscardDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                setShowDiscardDialog(false);
                navigate(`/assessment/assigned/${id}`);
              }}
            >
              Discard Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TrainerAssignedAssessmentEditPage;