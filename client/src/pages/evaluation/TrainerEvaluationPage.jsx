import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Save, Clock, User, Users, Calendar, FileEdit, CheckCircle, AlertTriangle, Award, BarChart2, PlusCircle, Trash2, Send } from 'lucide-react';
import api from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/toast';
import { Input } from '@/components/ui/input';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
/**
 * TrainerEvaluationPage allows trainers to manually evaluate beneficiaries
 */
const TrainerEvaluationPage = () => {
  const { id } = useParams(); // beneficiary ID
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [beneficiary, setBeneficiary] = useState(null);
  const [session, setSession] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [activeTab, setActiveTab] = useState('manual');
  // Define validation schema for evaluation form
  const evaluationSchema = z.object({
    title: z.string().min(3, { message: 'Title must be at least 3 characters' }),
    description: z.string().min(10, { message: 'Description must be at least 10 characters' }),
    competencies: z.array(
      z.object({
        name: z.string(),
        score: z.number().min(1).max(5),
        notes: z.string().optional(),
      })
    ).min(1),
    strengths: z.array(z.string()).min(1, { message: 'At least one strength is required' }),
    areas_for_improvement: z.array(z.string()).min(1, { message: 'At least one area for improvement is required' }),
    action_plan: z.string().min(20, { message: 'Action plan must be at least 20 characters' }),
    goals: z.array(
      z.object({
        description: z.string().min(5),
        timeline: z.string().min(2),
        success_criteria: z.string().min(5),
      })
    ).min(1, { message: 'At least one goal is required' }),
    overall_feedback: z.string().min(20, { message: 'Overall feedback must be at least 20 characters' }),
  });
  // Initialize form with default values
  const {
    register,
    handleSubmit,
    control,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(evaluationSchema),
    defaultValues: {
      title: '',
      description: '',
      competencies: [
        { name: 'Technical Skills', score: 3, notes: '' },
        { name: 'Communication', score: 3, notes: '' },
        { name: 'Problem Solving', score: 3, notes: '' },
        { name: 'Teamwork', score: 3, notes: '' },
        { name: 'Leadership', score: 3, notes: '' },
      ],
      strengths: [''],
      areas_for_improvement: [''],
      action_plan: '',
      goals: [
        {
          description: '',
          timeline: '1 month',
          success_criteria: '',
        }
      ],
      overall_feedback: '',
    }
  });
  // Watch form values for dynamic UI
  const watchedCompetencies = watch('competencies');
  const watchedStrengths = watch('strengths');
  const watchedAreasForImprovement = watch('areas_for_improvement');
  const watchedGoals = watch('goals');
  // Fetch beneficiary data, session data if available, and past evaluations
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Fetch beneficiary data
        const beneficiaryResponse = await api.get(API_ENDPOINTS.BENEFICIARIES.BASE + '/' + id);
        setBeneficiary(beneficiaryResponse.data);
        // Fetch session data if a session ID is provided
        if (sessionId) {
          try {
            const sessionResponse = await api.get(API_ENDPOINTS.EVALUATIONS.SESSION(sessionId));
            setSession(sessionResponse.data);
            // Pre-fill form with session-related data if available
            if (sessionResponse.data.test) {
              setValue('title', `Evaluation following ${sessionResponse.data.test.title}`);
              setValue('description', `Evaluation based on test results and observed performance.`);
            }
          } catch (error) {
            console.error('Error fetching session:', error);
          }
        }
        // Fetch past evaluations
        const evaluationsResponse = await api.get(`/api/beneficiaries/${id}/evaluations`);
        setEvaluations(evaluationsResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load beneficiary data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [id, sessionId, toast, setValue]);
  // Handle adding a new competency
  const handleAddCompetency = () => {
    const currentCompetencies = watch('competencies') || [];
    setValue('competencies', [
      ...currentCompetencies,
      { name: '', score: 3, notes: '' }
    ]);
  };
  // Handle removing a competency
  const handleRemoveCompetency = (index) => {
    const currentCompetencies = watch('competencies') || [];
    if (currentCompetencies.length <= 1) return;
    setValue('competencies', currentCompetencies.filter((_, i) => i !== index));
  };
  // Handle adding a new strength
  const handleAddStrength = () => {
    const currentStrengths = watch('strengths') || [];
    setValue('strengths', [...currentStrengths, '']);
  };
  // Handle removing a strength
  const handleRemoveStrength = (index) => {
    const currentStrengths = watch('strengths') || [];
    if (currentStrengths.length <= 1) return;
    setValue('strengths', currentStrengths.filter((_, i) => i !== index));
  };
  // Handle adding a new area for improvement
  const handleAddAreaForImprovement = () => {
    const current = watch('areas_for_improvement') || [];
    setValue('areas_for_improvement', [...current, '']);
  };
  // Handle removing an area for improvement
  const handleRemoveAreaForImprovement = (index) => {
    const current = watch('areas_for_improvement') || [];
    if (current.length <= 1) return;
    setValue('areas_for_improvement', current.filter((_, i) => i !== index));
  };
  // Handle adding a new goal
  const handleAddGoal = () => {
    const currentGoals = watch('goals') || [];
    setValue('goals', [
      ...currentGoals,
      {
        description: '',
        timeline: '1 month',
        success_criteria: '',
      }
    ]);
  };
  // Handle removing a goal
  const handleRemoveGoal = (index) => {
    const currentGoals = watch('goals') || [];
    if (currentGoals.length <= 1) return;
    setValue('goals', currentGoals.filter((_, i) => i !== index));
  };
  // Handle form submission
  const onSubmit = async (data) => {
    try {
      setIsSaving(true);
      const payload = {
        ...data,
        beneficiary_id: id,
        session_id: sessionId || null,
        evaluation_date: new Date().toISOString(),
      };
      const response = await api.post('/api/trainer-evaluations', payload);
      toast({
        title: 'Success',
        description: 'Evaluation has been saved successfully',
        type: 'success',
      });
      // If session ID was provided, mark it as trainer-evaluated
      if (sessionId) {
        await api.put(`/api/evaluations/sessions/${sessionId}/mark-evaluated`, {
          trainer_evaluated: true,
        });
      }
      navigate(`/beneficiaries/${id}`);
    } catch (error) {
      console.error('Error submitting evaluation:', error);
      toast({
        title: 'Error',
        description: 'Failed to save evaluation',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };
  // Generate a template evaluation based on session data
  const generateTemplateFromSession = () => {
    if (!session) return;
    const testTitle = session.test?.title || 'recent test';
    const score = session.score || 0;
    const testSkills = session.test?.skills || [];
    // Set default values based on session data
    setValue('title', `Evaluation following ${testTitle}`);
    setValue('description', `Evaluation based on ${testTitle} where the beneficiary scored ${score}%. This evaluation covers observed performance and future development areas.`);
    // Set competencies based on test skills if available
    if (testSkills.length > 0) {
      const competencies = testSkills.map(skill => ({
        name: skill,
        score: Math.min(5, Math.max(1, Math.round(session.score / 20))), // Convert percentage to 1-5 scale
        notes: `Based on ${testTitle} performance`,
      }));
      setValue('competencies', competencies);
    }
    // Set default strengths based on successful areas
    if (session.strengths && session.strengths.length > 0) {
      setValue('strengths', session.strengths);
    }
    // Set default areas for improvement
    if (session.areas_for_improvement && session.areas_for_improvement.length > 0) {
      setValue('areas_for_improvement', session.areas_for_improvement);
    }
    // Set a default action plan
    setValue('action_plan', `Based on the ${testTitle} results, we recommend focusing on ${
      session.areas_for_improvement?.[0] || 'key development areas'
    } through targeted exercises and regular check-ins. We will reassess progress in 4 weeks.`);
    // Set default goals
    setValue('goals', [
      {
        description: `Improve ${session.areas_for_improvement?.[0] || 'key skill area'}`,
        timeline: '1 month',
        success_criteria: 'Demonstrating improvement through practical application and follow-up assessment',
      }
    ]);
    // Set default overall feedback
    setValue('overall_feedback', `Overall, the beneficiary has demonstrated ${
      session.score >= 80 ? 'excellent' : 
      session.score >= 60 ? 'good' : 
      session.score >= 40 ? 'satisfactory' : 'developing'
    } performance in ${testTitle}. We have identified clear strengths and areas for development which will be the focus of upcoming training sessions.`);
  };
  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }
  // Render empty state if no beneficiary data
  if (!beneficiary) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Beneficiary Not Found</h2>
          <p className="text-gray-600 mb-4">The requested beneficiary could not be found.</p>
          <Button onClick={() => navigate('/beneficiaries')}>Back to Beneficiaries</Button>
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
            onClick={() => navigate(`/beneficiaries/${id}`)}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Beneficiary
          </Button>
          <h1 className="text-2xl font-bold">Trainer Evaluation</h1>
        </div>
        {session && (
          <Button
            variant="outline"
            onClick={generateTemplateFromSession}
            className="flex items-center"
          >
            <FileEdit className="w-4 h-4 mr-2" />
            Generate from Test Results
          </Button>
        )}
      </div>
      {/* Beneficiary info card */}
      <Card className="mb-6 p-4">
        <div className="flex items-center">
          <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold text-xl mr-4">
            {beneficiary.first_name?.[0] || 'B'}
          </div>
          <div>
            <h2 className="text-lg font-semibold">{beneficiary.first_name} {beneficiary.last_name}</h2>
            <p className="text-gray-600">{beneficiary.email}</p>
          </div>
          {session && (
            <div className="ml-auto flex items-center text-gray-600">
              <Clock className="w-4 h-4 mr-1" />
              <span>Test: {session.test?.title} - Score: {session.score}%</span>
            </div>
          )}
        </div>
      </Card>
      {/* Evaluation tabs */}
      <Tabs 
        value={activeTab} 
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList>
          <Tabs.TabTrigger value="manual">
            <FileEdit className="w-4 h-4 mr-2" />
            Manual Evaluation
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="history">
            <Clock className="w-4 h-4 mr-2" />
            Evaluation History
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="template">
            <FileEdit className="w-4 h-4 mr-2" />
            Templates
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Manual evaluation tab */}
        <Tabs.TabContent value="manual">
          <form onSubmit={handleSubmit(onSubmit)}>
            <Card className="mb-6 p-6">
              <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Evaluation Title*
                  </label>
                  <Input
                    {...register('title')}
                    placeholder="E.g., Quarterly Progress Evaluation"
                    error={errors.title?.message}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date
                  </label>
                  <Input
                    type="text"
                    value={new Date().toLocaleDateString()}
                    readOnly
                    className="bg-gray-50"
                  />
                </div>
              </div>
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description*
                </label>
                <textarea
                  {...register('description')}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm h-24"
                  placeholder="Provide a brief description of this evaluation"
                ></textarea>
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>
            </Card>
            {/* Competencies */}
            <Card className="mb-6 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Competencies</h2>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddCompetency}
                  className="flex items-center"
                >
                  <PlusCircle className="w-4 h-4 mr-1" />
                  Add Competency
                </Button>
              </div>
              <div className="space-y-4">
                {watchedCompetencies.map((competency, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex justify-between">
                      <div className="flex-1">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Competency Name
                            </label>
                            <Input
                              {...register(`competencies.${index}.name`)}
                              placeholder="E.g., Communication, Problem Solving"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Score (1-5)
                            </label>
                            <select
                              {...register(`competencies.${index}.score`, { valueAsNumber: true })}
                              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                            >
                              <option value={1}>1 - Needs Significant Improvement</option>
                              <option value={2}>2 - Developing</option>
                              <option value={3}>3 - Meets Expectations</option>
                              <option value={4}>4 - Exceeds Expectations</option>
                              <option value={5}>5 - Outstanding</option>
                            </select>
                          </div>
                          <div className="flex items-end">
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveCompetency(index)}
                              disabled={watchedCompetencies.length <= 1}
                              className="text-red-500 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                        <div className="mt-3">
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Notes
                          </label>
                          <textarea
                            {...register(`competencies.${index}.notes`)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm h-20"
                            placeholder="Additional observations or notes about this competency"
                          ></textarea>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
            {/* Strengths & Areas for Improvement */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Strengths */}
              <Card className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold">Strengths</h2>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleAddStrength}
                    className="flex items-center"
                  >
                    <PlusCircle className="w-4 h-4 mr-1" />
                    Add
                  </Button>
                </div>
                <div className="space-y-3">
                  {watchedStrengths.map((strength, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <Input
                        {...register(`strengths.${index}`)}
                        placeholder="Describe a strength"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveStrength(index)}
                        disabled={watchedStrengths.length <= 1}
                        className="text-red-500 hover:text-red-700 flex-shrink-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
                {errors.strengths && (
                  <p className="mt-1 text-sm text-red-600">{errors.strengths.message}</p>
                )}
              </Card>
              {/* Areas for Improvement */}
              <Card className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold">Areas for Improvement</h2>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleAddAreaForImprovement}
                    className="flex items-center"
                  >
                    <PlusCircle className="w-4 h-4 mr-1" />
                    Add
                  </Button>
                </div>
                <div className="space-y-3">
                  {watchedAreasForImprovement.map((area, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <Input
                        {...register(`areas_for_improvement.${index}`)}
                        placeholder="Describe an area for improvement"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveAreaForImprovement(index)}
                        disabled={watchedAreasForImprovement.length <= 1}
                        className="text-red-500 hover:text-red-700 flex-shrink-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
                {errors.areas_for_improvement && (
                  <p className="mt-1 text-sm text-red-600">{errors.areas_for_improvement.message}</p>
                )}
              </Card>
            </div>
            {/* Action Plan */}
            <Card className="mb-6 p-6">
              <h2 className="text-xl font-semibold mb-4">Action Plan</h2>
              <p className="text-gray-600 mb-4">
                Outline the specific actions that will be taken to address areas for improvement and build on strengths.
              </p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Action Plan Details*
                </label>
                <textarea
                  {...register('action_plan')}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm h-32"
                  placeholder="Describe the action plan for this beneficiary..."
                ></textarea>
                {errors.action_plan && (
                  <p className="mt-1 text-sm text-red-600">{errors.action_plan.message}</p>
                )}
              </div>
            </Card>
            {/* Goals */}
            <Card className="mb-6 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Development Goals</h2>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddGoal}
                  className="flex items-center"
                >
                  <PlusCircle className="w-4 h-4 mr-1" />
                  Add Goal
                </Button>
              </div>
              <div className="space-y-6">
                {watchedGoals.map((goal, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="font-medium">Goal {index + 1}</h3>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveGoal(index)}
                        disabled={watchedGoals.length <= 1}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Goal Description
                        </label>
                        <Input
                          {...register(`goals.${index}.description`)}
                          placeholder="What should be achieved?"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Timeline
                        </label>
                        <Input
                          {...register(`goals.${index}.timeline`)}
                          placeholder="E.g., 2 weeks, 1 month, Q3 2023"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Success Criteria
                      </label>
                      <Input
                        {...register(`goals.${index}.success_criteria`)}
                        placeholder="How will we know the goal has been achieved?"
                      />
                    </div>
                  </div>
                ))}
              </div>
              {errors.goals && (
                <p className="mt-1 text-sm text-red-600">{errors.goals.message}</p>
              )}
            </Card>
            {/* Overall Feedback */}
            <Card className="mb-6 p-6">
              <h2 className="text-xl font-semibold mb-4">Overall Feedback</h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Summary and Additional Observations*
                </label>
                <textarea
                  {...register('overall_feedback')}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm h-32"
                  placeholder="Provide overall feedback and any additional observations..."
                ></textarea>
                {errors.overall_feedback && (
                  <p className="mt-1 text-sm text-red-600">{errors.overall_feedback.message}</p>
                )}
              </div>
            </Card>
            {/* Form actions */}
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(`/beneficiaries/${id}`)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSaving}
                className="flex items-center"
              >
                {isSaving ? (
                  <>
                    <span className="animate-spin mr-2">○</span>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save Evaluation
                  </>
                )}
              </Button>
            </div>
          </form>
        </Tabs.TabContent>
        {/* Evaluation history tab */}
        <Tabs.TabContent value="history">
          {evaluations.length === 0 ? (
            <Card className="p-6 text-center">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">No Previous Evaluations</h2>
              <p className="text-gray-600 mb-4">
                This beneficiary has not been evaluated yet. Create their first evaluation using the Manual Evaluation tab.
              </p>
            </Card>
          ) : (
            <div className="space-y-4">
              {evaluations.map((evaluation, index) => (
                <Card key={index} className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold">{evaluation.title}</h3>
                      <p className="text-sm text-gray-600">
                        {new Date(evaluation.evaluation_date).toLocaleDateString()} by {evaluation.trainer_name || 'Unknown Trainer'}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/evaluations/trainer-evaluations/${evaluation.id}`)}
                    >
                      View Details
                    </Button>
                  </div>
                  <div className="mb-4">
                    <p className="text-gray-700">{evaluation.description}</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-green-50 p-3 rounded-lg">
                      <h4 className="font-medium text-green-800 mb-1 flex items-center">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Strengths
                      </h4>
                      <ul className="space-y-1 text-sm">
                        {evaluation.strengths.map((strength, i) => (
                          <li key={i} className="text-gray-700">• {strength}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-amber-50 p-3 rounded-lg">
                      <h4 className="font-medium text-amber-800 mb-1 flex items-center">
                        <AlertTriangle className="w-4 h-4 mr-1" />
                        Areas for Improvement
                      </h4>
                      <ul className="space-y-1 text-sm">
                        {evaluation.areas_for_improvement.map((area, i) => (
                          <li key={i} className="text-gray-700">• {area}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <h4 className="font-medium text-blue-800 mb-1 flex items-center">
                        <Award className="w-4 h-4 mr-1" />
                        Goals
                      </h4>
                      <ul className="space-y-1 text-sm">
                        {evaluation.goals.map((goal, i) => (
                          <li key={i} className="text-gray-700">• {goal.description}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Tabs.TabContent>
        {/* Templates tab */}
        <Tabs.TabContent value="template">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="p-6 hover:border-primary cursor-pointer transition-colors" onClick={() => {
              setValue('title', 'Monthly Progress Evaluation');
              setValue('description', 'Standard monthly evaluation to track progress against development goals and identify new areas for growth.');
              setValue('action_plan', 'We will continue with the existing training schedule, adding focused exercises on the identified areas for improvement. Weekly check-ins will track progress, with a comprehensive reassessment in one month.');
              setValue('overall_feedback', 'The beneficiary has shown consistent engagement with the program. While demonstrating strengths in several areas, there are clear opportunities for growth that we will address in the coming month.');
              setActiveTab('manual');
            }}>
              <div className="flex items-center mb-4">
                <Calendar className="w-12 h-12 text-primary mr-4" />
                <div>
                  <h3 className="font-semibold text-lg">Monthly Progress Evaluation</h3>
                  <p className="text-sm text-gray-600">Standard template for monthly progress tracking</p>
                </div>
              </div>
              <p className="text-gray-700">
                Use this template for regular monthly evaluations. Includes sections for competency assessment,
                strengths, areas for improvement, and development goals.
              </p>
              <Button className="mt-4 w-full">Use Template</Button>
            </Card>
            <Card className="p-6 hover:border-primary cursor-pointer transition-colors" onClick={() => {
              setValue('title', 'Quarterly Comprehensive Evaluation');
              setValue('description', 'In-depth quarterly assessment covering all development areas, measuring progress against established goals, and setting new objectives for the next quarter.');
              setValue('action_plan', 'Based on this comprehensive evaluation, we will adjust the development plan to focus on both technical and soft skills. The beneficiary will attend specialized workshops in problem-solving and receive one-on-one mentoring for leadership development.');
              setValue('overall_feedback', 'This quarter has shown significant growth in several competency areas. The beneficiary has successfully achieved most of the previously set goals and is ready to take on more challenging objectives. We will focus on stretching their capabilities while providing necessary support structures.');
              setActiveTab('manual');
            }}>
              <div className="flex items-center mb-4">
                <BarChart2 className="w-12 h-12 text-purple-600 mr-4" />
                <div>
                  <h3 className="font-semibold text-lg">Quarterly Comprehensive Evaluation</h3>
                  <p className="text-sm text-gray-600">Detailed assessment for quarterly reviews</p>
                </div>
              </div>
              <p className="text-gray-700">
                Use this template for in-depth quarterly evaluations. Provides comprehensive assessment framework
                with goal tracking and detailed planning sections.
              </p>
              <Button className="mt-4 w-full">Use Template</Button>
            </Card>
            <Card className="p-6 hover:border-primary cursor-pointer transition-colors" onClick={() => {
              setValue('title', 'Technical Skills Assessment');
              setValue('description', 'Focused evaluation of technical competencies related to the beneficiary\'s field of study or career path.');
              setValue('competencies', [
                { name: 'Technical Knowledge', score: 3, notes: '' },
                { name: 'Practical Application', score: 3, notes: '' },
                { name: 'Problem-Solving Approach', score: 3, notes: '' },
                { name: 'Tool Proficiency', score: 3, notes: '' },
                { name: 'Technical Communication', score: 3, notes: '' },
              ]);
              setValue('action_plan', 'We will create a specialized technical development plan focusing on hands-on projects to build practical experience. Regular code reviews and technical challenges will be incorporated into the training schedule.');
              setValue('overall_feedback', 'The technical assessment reveals a solid foundational understanding with opportunities to develop more advanced skills through practical application. Focused technical exercises will help bridge the gap between theoretical knowledge and practical implementation.');
              setActiveTab('manual');
            }}>
              <div className="flex items-center mb-4">
                <FileEdit className="w-12 h-12 text-blue-600 mr-4" />
                <div>
                  <h3 className="font-semibold text-lg">Technical Skills Assessment</h3>
                  <p className="text-sm text-gray-600">Technical competency-focused evaluation</p>
                </div>
              </div>
              <p className="text-gray-700">
                Use this template for evaluating technical skills and competencies. Includes technical-specific
                assessment criteria and development planning for technical roles.
              </p>
              <Button className="mt-4 w-full">Use Template</Button>
            </Card>
            <Card className="p-6 hover:border-primary cursor-pointer transition-colors" onClick={() => {
              setValue('title', 'Soft Skills Development Evaluation');
              setValue('description', 'Assessment focused on communication, teamwork, leadership, and other interpersonal skills critical for professional success.');
              setValue('competencies', [
                { name: 'Communication', score: 3, notes: '' },
                { name: 'Teamwork', score: 3, notes: '' },
                { name: 'Leadership', score: 3, notes: '' },
                { name: 'Adaptability', score: 3, notes: '' },
                { name: 'Emotional Intelligence', score: 3, notes: '' },
              ]);
              setValue('action_plan', 'We will implement role-playing exercises, group projects, and communication workshops to develop these critical soft skills. Regular feedback sessions will help track progress and adjust approaches as needed.');
              setValue('overall_feedback', 'The beneficiary shows promise in interpersonal skills, particularly in one-on-one interactions. Group dynamics and public speaking represent growth opportunities that will be addressed through targeted exercises and gradual exposure to more challenging social scenarios.');
              setActiveTab('manual');
            }}>
              <div className="flex items-center mb-4">
                <Users className="w-12 h-12 text-green-600 mr-4" />
                <div>
                  <h3 className="font-semibold text-lg">Soft Skills Development Evaluation</h3>
                  <p className="text-sm text-gray-600">Interpersonal and professional skills assessment</p>
                </div>
              </div>
              <p className="text-gray-700">
                Use this template for evaluating soft skills and interpersonal competencies. Focuses on communication,
                teamwork, leadership, and professional behavior.
              </p>
              <Button className="mt-4 w-full">Use Template</Button>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};
export default TrainerEvaluationPage;