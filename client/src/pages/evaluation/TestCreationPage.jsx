import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PlusCircle, X, Save, ArrowLeft, Play, Trash2 } from 'lucide-react';
import api from '@/lib/api';
import { EVALUATION_STATUS, QUESTION_TYPES, API_ENDPOINTS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import QuestionEditor from '@/components/evaluation/QuestionEditor';
import PreviewTest from '@/components/evaluation/PreviewTest';
import { useToast } from '@/components/ui/toast';
import { AuthContext } from '@/contexts/AuthContext';

// Validation schema for test creation
const testSchema = z.object({
  title: z.string().min(3, { message: 'Title must be at least 3 characters' }),
  description: z.string().min(10, { message: 'Description must be at least 10 characters' }),
  instructions: z.string().optional(),
  passing_score: z.number().min(0).max(100).default(70),
  time_limit: z.number().min(0).optional(),
  skills: z.array(z.string()).optional(),
  status: z.enum([EVALUATION_STATUS.DRAFT, EVALUATION_STATUS.ACTIVE, EVALUATION_STATUS.ARCHIVED]).default(EVALUATION_STATUS.DRAFT),
  questions: z.array(
    z.object({
      question_text: z.string().min(3, { message: 'Question text is required' }),
      question_type: z.enum([
        QUESTION_TYPES.MULTIPLE_CHOICE,
        QUESTION_TYPES.TEXT,
        QUESTION_TYPES.TRUE_FALSE,
        QUESTION_TYPES.MATCHING,
        QUESTION_TYPES.ORDERING
      ]),
      points: z.number().min(1).default(1),
      options: z.array(
        z.object({
          text: z.string().min(1, { message: 'Option text is required' }),
          is_correct: z.boolean().default(false),
        })
      ).optional(),
      matches: z.array(
        z.object({
          left: z.string().min(1, { message: 'Left match is required' }),
          right: z.string().min(1, { message: 'Right match is required' }),
        })
      ).optional(),
      order_items: z.array(
        z.object({
          text: z.string().min(1, { message: 'Item text is required' }),
          position: z.number().min(0),
        })
      ).optional(),
      correct_answer: z.string().optional(),
    })
  ).min(1, { message: 'At least one question is required' }),
});

const TestCreationPage = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('editor');
  
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
    trigger,
  } = useForm({
    resolver: zodResolver(testSchema),
    defaultValues: {
      title: 'Test Evaluation',
      description: 'This is a test evaluation for debugging purposes',
      instructions: 'Please complete all questions',
      passing_score: 70,
      time_limit: 60,
      skills: ['Communication', 'Problem Solving'],
      status: EVALUATION_STATUS.DRAFT,
      questions: [
        {
          question_text: 'What is 2 + 2?',
          question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
          points: 1,
          options: [
            { text: '3', is_correct: false },
            { text: '4', is_correct: true },
            { text: '5', is_correct: false },
            { text: '6', is_correct: false },
          ],
        },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'questions',
  });

  const watchAllFields = watch();

  const handleAddQuestion = () => {
    append({
      question_text: '',
      question_type: QUESTION_TYPES.MULTIPLE_CHOICE,
      points: 1,
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
      ],
    });
  };

  const handleRemoveQuestion = (index) => {
    if (fields.length > 1) {
      remove(index);
    } else {
      addToast({
        title: 'Error',
        message: 'Test must have at least one question',
        type: 'error',
      });
    }
  };

  const onSubmit = async (data) => {
    try {
      // Transform data to match backend schema
      const evaluationData = {
        title: data.title,
        description: data.description,
        instructions: data.instructions,
        passing_score: data.passing_score,
        time_limit: data.time_limit,
        type: 'test',
        status: data.status,
        is_template: false,
        tenant_id: user?.tenants?.[0]?.id || 1, // Get from user context
        questions: data.questions.map(q => {
          const baseQuestion = {
            text: q.question_text,
            type: q.question_type,
            points: q.points,
          };

          // Handle different question types
          if (q.question_type === 'multiple_choice' && q.options) {
            baseQuestion.options = {};
            const correctAnswers = [];
            
            q.options.forEach((opt, idx) => {
              const key = `option_${idx + 1}`;
              baseQuestion.options[key] = opt.text;
              if (opt.is_correct) {
                correctAnswers.push(key);
              }
            });
            
            baseQuestion.correct_answer = correctAnswers.length > 0 ? correctAnswers[0] : null;
          } else if (q.question_type === 'true_false') {
            baseQuestion.correct_answer = q.correct_answer || false;
          } else if (q.question_type === 'text') {
            baseQuestion.correct_answer = q.correct_answer || '';
          }
          
          return baseQuestion;
        })
      };
      const response = await api.post(API_ENDPOINTS.EVALUATIONS.BASE, evaluationData);
      addToast({
        title: 'Success',
        message: 'Test has been created successfully',
        type: 'success',
      });
      navigate('/evaluations');
    } catch (error) {
      console.error('Error creating test:', error);
      addToast({
        title: 'Error',
        message: error.response?.data?.message || 'Failed to create test',
        type: 'error',
      });
    }
  };

  const skillOptions = [
    'Communication',
    'Problem Solving',
    'Critical Thinking',
    'Teamwork',
    'Leadership',
    'Technical Skills',
    'Time Management',
    'Adaptability',
    'Creativity',
  ];

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/evaluations')}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Tests
          </Button>
          <h1 className="text-2xl font-bold">Create New Test</h1>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => handleSubmit((data) => onSubmit({ ...data, status: EVALUATION_STATUS.DRAFT }))()}
            disabled={isSubmitting}
            className="flex items-center"
          >
            <Save className="w-4 h-4 mr-2" />
            Save as Draft
          </Button>
          <Button
            type="button"
            onClick={() => handleSubmit((data) => onSubmit({ ...data, status: EVALUATION_STATUS.ACTIVE }))()}
            disabled={isSubmitting}
            className="flex items-center"
          >
            <Play className="w-4 h-4 mr-2" />
            Save and Activate
          </Button>
        </div>
      </div>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <TabsList>
          <TabTrigger value="editor">Editor</TabTrigger>
          <TabTrigger value="preview">Preview</TabTrigger>
        </TabsList>
        <TabContent value="editor">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Test Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                      Title*
                    </label>
                    <Input
                      id="title"
                      {...register('title')}
                      error={errors.title?.message}
                    />
                  </div>
                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                      Description*
                    </label>
                    <textarea
                      id="description"
                      {...register('description')}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm h-32"
                    />
                    {errors.description && (
                      <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                    )}
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="instructions" className="block text-sm font-medium text-gray-700">
                      Instructions
                    </label>
                    <textarea
                      id="instructions"
                      {...register('instructions')}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm h-32"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="passing_score" className="block text-sm font-medium text-gray-700">
                        Passing Score (%)
                      </label>
                      <Input
                        id="passing_score"
                        type="number"
                        min="0"
                        max="100"
                        {...register('passing_score', { valueAsNumber: true })}
                        error={errors.passing_score?.message}
                      />
                    </div>
                    <div>
                      <label htmlFor="time_limit" className="block text-sm font-medium text-gray-700">
                        Time Limit (minutes, 0 for no limit)
                      </label>
                      <Input
                        id="time_limit"
                        type="number"
                        min="0"
                        {...register('time_limit', { valueAsNumber: true })}
                        error={errors.time_limit?.message}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">Skills*</label>
                <div className="mt-2 flex flex-wrap gap-2">
                  {skillOptions.map((skill) => (
                    <label key={skill} className="inline-flex items-center">
                      <input
                        type="checkbox"
                        value={skill}
                        {...register('skills')}
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <span className="ml-2 text-sm text-gray-700">{skill}</span>
                    </label>
                  ))}
                </div>
                {errors.skills && (
                  <p className="mt-1 text-sm text-red-600">{errors.skills.message}</p>
                )}
              </div>
            </Card>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Questions</h2>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleAddQuestion}
                  className="flex items-center"
                >
                  <PlusCircle className="w-4 h-4 mr-2" />
                  Add Question
                </Button>
              </div>

              {fields.map((field, index) => (
                <Card key={field.id} className="p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium">Question {index + 1}</h3>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveQuestion(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                  <QuestionEditor
                    register={register}
                    control={control}
                    index={index}
                    errors={errors}
                    watch={watch}
                    setValue={setValue}
                    trigger={trigger}
                  />
                </Card>
              ))}
            </div>
          </form>
        </TabContent>
        <TabContent value="preview">
          <PreviewTest test={watchAllFields} />
        </TabContent>
      </Tabs>
    </div>
  );
};

export default TestCreationPage;