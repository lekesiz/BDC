import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { ArrowLeft, Plus, Trash2, Save, Eye, Clock, Users, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import api from '@/lib/api';
const TestCreationPageSimple = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('details');
  const { register, control, handleSubmit, formState: { errors }, watch, setValue } = useForm({
    defaultValues: {
      title: '',
      description: '',
      instructions: '',
      passing_score: 70,
      time_limit: 60,
      difficulty: 'medium',
      category: 'general',
      questions: [
        {
          question_text: '',
          question_type: 'multiple_choice',
          points: 1,
          options: [
            { text: '', is_correct: false },
            { text: '', is_correct: false }
          ]
        }
      ]
    }
  });
  const { fields: questions, append: addQuestion, remove: removeQuestion } = useFieldArray({
    control,
    name: 'questions'
  });
  const watchedQuestions = watch('questions');
  const addOption = (questionIndex) => {
    const currentOptions = watchedQuestions[questionIndex].options || [];
    setValue(`questions.${questionIndex}.options`, [
      ...currentOptions,
      { text: '', is_correct: false }
    ]);
  };
  const removeOption = (questionIndex, optionIndex) => {
    const currentOptions = watchedQuestions[questionIndex].options || [];
    const newOptions = currentOptions.filter((_, index) => index !== optionIndex);
    setValue(`questions.${questionIndex}.options`, newOptions);
  };
  const onSubmit = async (data) => {
    try {
      setIsSubmitting(true);
      // Validate questions
      if (!data.questions || data.questions.length === 0) {
        addToast({
          type: 'error',
          title: 'Validation Error',
          message: 'At least one question is required.'
        });
        return;
      }
      // Create test
      const response = await api.post('/api/tests', {
        ...data,
        status: 'draft'
      });
      addToast({
        type: 'success',
        title: 'Test Created',
        message: 'Test has been created successfully!'
      });
      navigate('/evaluations');
    } catch (error) {
      console.error('Error creating test:', error);
      addToast({
        type: 'error',
        title: 'Creation Failed',
        message: error.response?.data?.message || 'Failed to create test. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  const addNewQuestion = () => {
    addQuestion({
      question_text: '',
      question_type: 'multiple_choice',
      points: 1,
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ]
    });
  };
  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/evaluations')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Evaluations
        </Button>
        <h1 className="text-2xl font-bold">Create New Test</h1>
        <p className="text-gray-600 mt-1">Design a comprehensive evaluation for your beneficiaries</p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabTrigger value="details" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Test Details
            </TabTrigger>
            <TabTrigger value="questions" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Questions ({questions.length})
            </TabTrigger>
            <TabTrigger value="settings" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Settings
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
                    <label className="text-sm font-medium">Test Title *</label>
                    <Input
                      {...register('title', { required: 'Title is required' })}
                      placeholder="Enter test title"
                      className={errors.title ? 'border-red-500' : ''}
                    />
                    {errors.title && (
                      <p className="text-red-500 text-sm">{errors.title.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Category</label>
                    <Select 
                      onValueChange={(value) => setValue('category', value)}
                      options={[
                        { value: 'general', label: 'General Knowledge' },
                        { value: 'language', label: 'Language Skills' },
                        { value: 'mathematics', label: 'Mathematics' },
                        { value: 'science', label: 'Science' },
                        { value: 'social', label: 'Social Studies' },
                        { value: 'technical', label: 'Technical Skills' }
                      ]}
                      placeholder="Select category"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description *</label>
                  <Textarea
                    {...register('description', { required: 'Description is required' })}
                    placeholder="Describe the purpose and content of this test"
                    rows={3}
                    className={errors.description ? 'border-red-500' : ''}
                  />
                  {errors.description && (
                    <p className="text-red-500 text-sm">{errors.description.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Instructions</label>
                  <Textarea
                    {...register('instructions')}
                    placeholder="Provide instructions for test takers"
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>
          </TabContent>
          <TabContent value="questions" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Test Questions</h3>
              <Button
                type="button"
                onClick={addNewQuestion}
                size="sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Question
              </Button>
            </div>
            {questions.map((question, questionIndex) => (
              <Card key={question.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base">Question {questionIndex + 1}</CardTitle>
                    {questions.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeQuestion(questionIndex)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Question Text *</label>
                    <Textarea
                      {...register(`questions.${questionIndex}.question_text`, {
                        required: 'Question text is required'
                      })}
                      placeholder="Enter your question"
                      rows={2}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Question Type</label>
                      <Select
                        onValueChange={(value) => setValue(`questions.${questionIndex}.question_type`, value)}
                        value={watchedQuestions[questionIndex]?.question_type || 'multiple_choice'}
                        options={[
                          { value: 'multiple_choice', label: 'Multiple Choice' },
                          { value: 'true_false', label: 'True/False' },
                          { value: 'text', label: 'Text Answer' }
                        ]}
                        placeholder="Select question type"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Points</label>
                      <Input
                        type="number"
                        min="1"
                        {...register(`questions.${questionIndex}.points`, {
                          valueAsNumber: true,
                          min: 1
                        })}
                        defaultValue={1}
                      />
                    </div>
                  </div>
                  {/* Options for multiple choice */}
                  {watchedQuestions[questionIndex]?.question_type === 'multiple_choice' && (
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <label className="text-sm font-medium">Answer Options</label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => addOption(questionIndex)}
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add Option
                        </Button>
                      </div>
                      {watchedQuestions[questionIndex]?.options?.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center gap-2">
                          <input
                            type="radio"
                            name={`question_${questionIndex}_correct`}
                            onChange={() => {
                              const currentOptions = watchedQuestions[questionIndex].options;
                              const newOptions = currentOptions.map((opt, idx) => ({
                                ...opt,
                                is_correct: idx === optionIndex
                              }));
                              setValue(`questions.${questionIndex}.options`, newOptions);
                            }}
                            className="mt-1"
                          />
                          <Input
                            {...register(`questions.${questionIndex}.options.${optionIndex}.text`)}
                            placeholder={`Option ${optionIndex + 1}`}
                            className="flex-1"
                          />
                          {watchedQuestions[questionIndex]?.options?.length > 2 && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeOption(questionIndex, optionIndex)}
                              className="text-red-500"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  {/* True/False options */}
                  {watchedQuestions[questionIndex]?.question_type === 'true_false' && (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Correct Answer</label>
                      <Select
                        onValueChange={(value) => setValue(`questions.${questionIndex}.correct_answer`, value)}
                        value={watchedQuestions[questionIndex]?.correct_answer}
                        options={[
                          { value: 'true', label: 'True' },
                          { value: 'false', label: 'False' }
                        ]}
                        placeholder="Select correct answer"
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
            {questions.length === 0 && (
              <Card className="border-dashed">
                <CardContent className="py-8 text-center">
                  <p className="text-gray-500 mb-4">No questions added yet</p>
                  <Button type="button" onClick={addNewQuestion}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add First Question
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabContent>
          <TabContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Test Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Passing Score (%)</label>
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      {...register('passing_score', { valueAsNumber: true })}
                      defaultValue={70}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Time Limit (minutes)</label>
                    <Input
                      type="number"
                      min="0"
                      {...register('time_limit', { valueAsNumber: true })}
                      defaultValue={60}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Difficulty Level</label>
                    <Select 
                      onValueChange={(value) => setValue('difficulty', value)}
                      options={[
                        { value: 'easy', label: 'Easy' },
                        { value: 'medium', label: 'Medium' },
                        { value: 'hard', label: 'Hard' }
                      ]}
                      placeholder="Select difficulty"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabContent>
        </Tabs>
        <div className="flex justify-between items-center pt-6 border-t">
          <div className="flex items-center gap-2">
            <Badge variant="outline">
              {questions.length} Question{questions.length !== 1 ? 's' : ''}
            </Badge>
            <Badge variant="outline">
              {questions.reduce((total, q) => total + (q.points || 1), 0)} Total Points
            </Badge>
          </div>
          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/evaluations')}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={isSubmitting}
            >
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
            >
              <Save className="h-4 w-4 mr-2" />
              {isSubmitting ? 'Creating...' : 'Create Test'}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};
export default TestCreationPageSimple;