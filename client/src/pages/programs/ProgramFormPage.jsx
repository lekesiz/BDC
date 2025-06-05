import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { ArrowLeft, Save, Plus, Trash2, Calendar, Clock, Users, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import api from '@/lib/api';
const ProgramFormPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { addToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('details');
  const isEdit = Boolean(id);
  const { register, control, handleSubmit, formState: { errors }, watch, setValue, reset } = useForm({
    defaultValues: {
      name: '',
      description: '',
      objectives: '',
      duration_weeks: 12,
      category: 'skills',
      level: 'beginner',
      status: 'draft',
      max_participants: 25,
      prerequisites: '',
      certification: false,
      modules: [
        {
          name: '',
          description: '',
          duration_hours: 2,
          order: 1
        }
      ],
      schedule: {
        start_date: '',
        end_date: '',
        sessions_per_week: 2,
        session_duration: 2
      }
    }
  });
  const { fields: modules, append: addModule, remove: removeModule } = useFieldArray({
    control,
    name: 'modules'
  });
  // Load existing program if editing
  useEffect(() => {
    if (isEdit) {
      const fetchProgram = async () => {
        try {
          setIsLoading(true);
          const response = await api.get(`/api/programs/${id}`);
          const program = response.data;
          // Reset form with fetched data
          reset({
            name: program.name || '',
            description: program.description || '',
            objectives: program.objectives || '',
            duration_weeks: program.duration_weeks || 12,
            category: program.category || 'skills',
            level: program.level || 'beginner',
            status: program.status || 'draft',
            max_participants: program.max_participants || 25,
            prerequisites: program.prerequisites || '',
            certification: program.certification || false,
            modules: program.modules || [{ name: '', description: '', duration_hours: 2, order: 1 }],
            schedule: program.schedule || {
              start_date: '',
              end_date: '',
              sessions_per_week: 2,
              session_duration: 2
            }
          });
        } catch (error) {
          console.error('Error fetching program:', error);
          addToast({
            type: 'error',
            title: 'Failed to load program',
            message: error.response?.data?.message || 'Could not load program data.'
          });
          navigate('/programs');
        } finally {
          setIsLoading(false);
        }
      };
      fetchProgram();
    }
  }, [id, isEdit, reset, addToast, navigate]);
  const onSubmit = async (data) => {
    try {
      setIsSubmitting(true);
      // Validate modules
      if (!data.modules || data.modules.length === 0) {
        addToast({
          type: 'error',
          title: 'Validation Error',
          message: 'At least one module is required.'
        });
        return;
      }
      const endpoint = isEdit ? `/api/programs/${id}` : '/api/programs';
      const method = isEdit ? 'put' : 'post';
      const response = await api[method](endpoint, data);
      addToast({
        type: 'success',
        title: isEdit ? 'Program Updated' : 'Program Created',
        message: `Program has been ${isEdit ? 'updated' : 'created'} successfully!`
      });
      navigate('/programs');
    } catch (error) {
      console.error('Error saving program:', error);
      addToast({
        type: 'error',
        title: 'Save Failed',
        message: error.response?.data?.message || `Failed to ${isEdit ? 'update' : 'create'} program. Please try again.`
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  const addNewModule = () => {
    const newOrder = modules.length + 1;
    addModule({
      name: '',
      description: '',
      duration_hours: 2,
      order: newOrder
    });
  };
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/programs')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Programs
        </Button>
        <h1 className="text-2xl font-bold">
          {isEdit ? 'Edit Program' : 'Create New Program'}
        </h1>
        <p className="text-gray-600 mt-1">
          {isEdit ? 'Update program details and modules' : 'Design a comprehensive training program for your beneficiaries'}
        </p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabTrigger value="details" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Program Details
            </TabTrigger>
            <TabTrigger value="modules" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Modules ({modules.length})
            </TabTrigger>
            <TabTrigger value="schedule" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Schedule & Settings
            </TabTrigger>
          </TabsList>
          <TabContent value="details" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Program Name *</label>
                    <Input
                      {...register('name', { required: 'Program name is required' })}
                      placeholder="Enter program name"
                      className={errors.name ? 'border-red-500' : ''}
                    />
                    {errors.name && (
                      <p className="text-red-500 text-sm">{errors.name.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Category</label>
                    <Select 
                      onValueChange={(value) => setValue('category', value)}
                      value={watch('category')}
                      options={[
                        { value: 'skills', label: 'Skills Development' },
                        { value: 'language', label: 'Language Learning' },
                        { value: 'technical', label: 'Technical Training' },
                        { value: 'business', label: 'Business Skills' },
                        { value: 'personal', label: 'Personal Development' },
                        { value: 'academic', label: 'Academic Support' }
                      ]}
                      placeholder="Select category"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description *</label>
                  <Textarea
                    {...register('description', { required: 'Description is required' })}
                    placeholder="Describe the program's purpose and content"
                    rows={3}
                    className={errors.description ? 'border-red-500' : ''}
                  />
                  {errors.description && (
                    <p className="text-red-500 text-sm">{errors.description.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Learning Objectives</label>
                  <Textarea
                    {...register('objectives')}
                    placeholder="What will participants learn or achieve?"
                    rows={3}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Prerequisites</label>
                  <Textarea
                    {...register('prerequisites')}
                    placeholder="Any requirements or prior knowledge needed"
                    rows={2}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Level</label>
                    <Select 
                      onValueChange={(value) => setValue('level', value)}
                      value={watch('level')}
                      options={[
                        { value: 'beginner', label: 'Beginner' },
                        { value: 'intermediate', label: 'Intermediate' },
                        { value: 'advanced', label: 'Advanced' }
                      ]}
                      placeholder="Select level"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Duration (weeks)</label>
                    <Input
                      type="number"
                      min="1"
                      max="52"
                      {...register('duration_weeks', { valueAsNumber: true })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Max Participants</label>
                    <Input
                      type="number"
                      min="1"
                      max="100"
                      {...register('max_participants', { valueAsNumber: true })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabContent>
          <TabContent value="modules" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Program Modules</h3>
              <Button
                type="button"
                onClick={addNewModule}
                size="sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Module
              </Button>
            </div>
            {modules.map((module, moduleIndex) => (
              <Card key={module.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base">Module {moduleIndex + 1}</CardTitle>
                    {modules.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeModule(moduleIndex)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Module Name *</label>
                    <Input
                      {...register(`modules.${moduleIndex}.name`, {
                        required: 'Module name is required'
                      })}
                      placeholder="Enter module name"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Description</label>
                    <Textarea
                      {...register(`modules.${moduleIndex}.description`)}
                      placeholder="Describe what this module covers"
                      rows={2}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Duration (hours)</label>
                      <Input
                        type="number"
                        min="1"
                        max="40"
                        {...register(`modules.${moduleIndex}.duration_hours`, {
                          valueAsNumber: true,
                          min: 1
                        })}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Order</label>
                      <Input
                        type="number"
                        min="1"
                        {...register(`modules.${moduleIndex}.order`, {
                          valueAsNumber: true,
                          min: 1
                        })}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {modules.length === 0 && (
              <Card className="border-dashed">
                <CardContent className="py-8 text-center">
                  <p className="text-gray-500 mb-4">No modules added yet</p>
                  <Button type="button" onClick={addNewModule}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add First Module
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabContent>
          <TabContent value="schedule" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Program Schedule</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Start Date</label>
                    <Input
                      type="date"
                      {...register('schedule.start_date')}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">End Date</label>
                    <Input
                      type="date"
                      {...register('schedule.end_date')}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Sessions per Week</label>
                    <Input
                      type="number"
                      min="1"
                      max="7"
                      {...register('schedule.sessions_per_week', { valueAsNumber: true })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Session Duration (hours)</label>
                    <Input
                      type="number"
                      min="1"
                      max="8"
                      {...register('schedule.session_duration', { valueAsNumber: true })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Program Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Status</label>
                  <Select 
                    onValueChange={(value) => setValue('status', value)}
                    value={watch('status')}
                    options={[
                      { value: 'draft', label: 'Draft' },
                      { value: 'active', label: 'Active' },
                      { value: 'completed', label: 'Completed' },
                      { value: 'archived', label: 'Archived' }
                    ]}
                    placeholder="Select status"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="certification"
                    {...register('certification')}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="certification" className="text-sm font-medium">
                    Offers certification upon completion
                  </label>
                </div>
              </CardContent>
            </Card>
          </TabContent>
        </Tabs>
        <div className="flex justify-between items-center pt-6 border-t">
          <div className="flex items-center gap-2">
            <Badge variant="outline">
              {modules.length} Module{modules.length !== 1 ? 's' : ''}
            </Badge>
            <Badge variant="outline">
              {modules.reduce((total, m) => total + (m.duration_hours || 0), 0)} Total Hours
            </Badge>
          </div>
          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/programs')}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
            >
              <Save className="h-4 w-4 mr-2" />
              {isSubmitting ? (isEdit ? 'Updating...' : 'Creating...') : (isEdit ? 'Update Program' : 'Create Program')}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};
export default ProgramFormPage;