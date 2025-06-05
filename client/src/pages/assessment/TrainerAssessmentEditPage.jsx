import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Save, Plus, Trash2, GripVertical, 
  FileText, Settings, HelpCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Label } from '@/components/ui';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/components/ui/use-toast';
import { RadioGroup } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
/**
 * TrainerAssessmentEditPage allows trainers to edit existing assessment templates
 */
const TrainerAssessmentEditPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('basic');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [originalTemplate, setOriginalTemplate] = useState(null);
  const [showDiscardDialog, setShowDiscardDialog] = useState(false);
  // Basic info state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('quiz');
  const [category, setCategory] = useState('');
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  const [isPublished, setIsPublished] = useState(false);
  // Quiz state
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState({
    type: 'multipleChoice',
    question: '',
    options: ['', '', '', ''],
    correctAnswer: 0,
    points: 10,
    explanation: ''
  });
  // Project state
  const [requirements, setRequirements] = useState([]);
  const [currentRequirement, setCurrentRequirement] = useState({
    description: '',
    points: 10
  });
  const [rubric, setRubric] = useState({});
  const [resources, setResources] = useState([]);
  // Settings state
  const [settings, setSettings] = useState({
    timeLimit: 0,
    attemptsAllowed: 1,
    passingScore: 70,
    shuffleQuestions: false,
    showCorrectAnswers: true,
    allowLateSubmission: false,
    latePenalty: 0,
    autoGrade: true,
    notifyOnSubmission: true,
    notifyBeforeDue: true,
    notifyOnGrade: true
  });
  // Load template data
  useEffect(() => {
    let isMounted = true;
    const fetchTemplate = async () => {
      try {
        if (!isMounted) return;
        setIsLoading(true);
        setError(null);
        const response = await fetch(`/api/assessment/templates/${id}`);
        if (!isMounted) return;
        if (!response.ok) throw new Error('Failed to fetch template');
        const templateData = await response.json();
        if (!isMounted) return;
        // Store original template for comparison
        setOriginalTemplate(templateData);
        // Populate state with template data
        setTitle(templateData.title || '');
        setDescription(templateData.description || '');
        setType(templateData.type || 'quiz');
        setCategory(templateData.category || '');
        setSkills(templateData.skills || []);
        setIsPublished(templateData.is_published || false);
        if (templateData.type === 'quiz') {
          setQuestions(templateData.questions || []);
        } else {
          setRequirements(templateData.requirements || []);
          setRubric(templateData.rubric || {});
          setResources(templateData.resources || []);
        }
        setSettings({
          ...settings,
          ...templateData.settings
        });
      } catch (err) {
        if (!isMounted) return;
        console.error('Error fetching template:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load template',
          type: 'error',
        });
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    fetchTemplate();
    return () => {
      isMounted = false;
    };
  }, [id]);
  // Check if there are unsaved changes
  const hasUnsavedChanges = () => {
    if (!originalTemplate) return false;
    // Compare current state with original template
    return (
      title !== originalTemplate.title ||
      description !== originalTemplate.description ||
      category !== originalTemplate.category ||
      JSON.stringify(skills) !== JSON.stringify(originalTemplate.skills) ||
      isPublished !== originalTemplate.is_published ||
      JSON.stringify(questions) !== JSON.stringify(originalTemplate.questions || []) ||
      JSON.stringify(requirements) !== JSON.stringify(originalTemplate.requirements || []) ||
      JSON.stringify(settings) !== JSON.stringify(originalTemplate.settings || {})
    );
  };
  // Handle navigation away with unsaved changes
  const handleNavigate = (path) => {
    if (hasUnsavedChanges()) {
      setShowDiscardDialog(true);
    } else {
      navigate(path);
    }
  };
  // Add skill
  const handleAddSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill('');
    }
  };
  // Remove skill
  const handleRemoveSkill = (skillToRemove) => {
    setSkills(skills.filter(skill => skill !== skillToRemove));
  };
  // Add question
  const handleAddQuestion = () => {
    if (!currentQuestion.question.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a question',
        type: 'error',
      });
      return;
    }
    // Validate based on question type
    if (currentQuestion.type === 'multipleChoice' || currentQuestion.type === 'multipleAnswer') {
      const validOptions = currentQuestion.options.filter(opt => opt.trim());
      if (validOptions.length < 2) {
        toast({
          title: 'Error',
          description: 'Please provide at least 2 options',
          type: 'error',
        });
        return;
      }
      currentQuestion.options = validOptions;
    }
    setQuestions([...questions, { ...currentQuestion, id: Date.now() }]);
    setCurrentQuestion({
      type: 'multipleChoice',
      question: '',
      options: ['', '', '', ''],
      correctAnswer: 0,
      points: 10,
      explanation: ''
    });
  };
  // Remove question
  const handleRemoveQuestion = (questionId) => {
    setQuestions(questions.filter(q => q.id !== questionId));
  };
  // Update existing question
  const handleUpdateQuestion = (questionId, updatedQuestion) => {
    setQuestions(questions.map(q => q.id === questionId ? updatedQuestion : q));
  };
  // Update question type
  const handleQuestionTypeChange = (newType) => {
    setCurrentQuestion(prev => {
      const base = {
        ...prev,
        type: newType
      };
      switch (newType) {
        case 'multipleChoice':
          return {
            ...base,
            options: ['', '', '', ''],
            correctAnswer: 0
          };
        case 'multipleAnswer':
          return {
            ...base,
            options: ['', '', '', ''],
            correctAnswers: []
          };
        case 'trueFalse':
          return {
            ...base,
            correctAnswer: true
          };
        case 'shortAnswer':
          return {
            ...base,
            correctAnswer: ''
          };
        default:
          return base;
      }
    });
  };
  // Add requirement
  const handleAddRequirement = () => {
    if (!currentRequirement.description.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a requirement description',
        type: 'error',
      });
      return;
    }
    setRequirements([...requirements, { ...currentRequirement, id: Date.now() }]);
    setCurrentRequirement({
      description: '',
      points: 10
    });
  };
  // Remove requirement
  const handleRemoveRequirement = (requirementId) => {
    setRequirements(requirements.filter(r => r.id !== requirementId));
  };
  // Update existing requirement
  const handleUpdateRequirement = (requirementId, updatedRequirement) => {
    setRequirements(requirements.map(r => r.id === requirementId ? updatedRequirement : r));
  };
  // Save assessment
  const handleSave = async (publish = null) => {
    // Validate basic info
    if (!title.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a title for the assessment',
        type: 'error',
      });
      setActiveTab('basic');
      return;
    }
    if (!description.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a description for the assessment',
        type: 'error',
      });
      setActiveTab('basic');
      return;
    }
    // Validate content
    if (type === 'quiz' && questions.length === 0) {
      toast({
        title: 'Error',
        description: 'Please add at least one question',
        type: 'error',
      });
      setActiveTab('content');
      return;
    }
    if (type === 'project' && requirements.length === 0) {
      toast({
        title: 'Error',
        description: 'Please add at least one requirement',
        type: 'error',
      });
      setActiveTab('content');
      return;
    }
    try {
      setIsSaving(true);
      const templateData = {
        title,
        description,
        type,
        category,
        skills,
        is_published: publish !== null ? publish : isPublished,
        settings,
        ...(type === 'quiz' ? { questions } : { requirements, rubric, resources }),
        updated_at: new Date().toISOString()
      };
      const response = await fetch(`/api/assessment/templates/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });
      if (!response.ok) throw new Error('Failed to update assessment');
      const updatedTemplate = await response.json();
      setOriginalTemplate(updatedTemplate);
      toast({
        title: 'Success',
        description: 'Assessment updated successfully',
        type: 'success',
      });
      if (publish !== null) {
        setIsPublished(publish);
      }
    } catch (err) {
      console.error('Error updating assessment:', err);
      toast({
        title: 'Error',
        description: 'Failed to update assessment',
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
  if (error || !originalTemplate) {
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
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <Button
            variant="ghost"
            onClick={() => handleNavigate('/assessment')}
            className="flex items-center mr-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Assessments
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Edit Assessment</h1>
            <p className="text-gray-600">{originalTemplate.title}</p>
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
            onClick={() => handleSave()}
            disabled={isSaving || !hasUnsavedChanges()}
          >
            {isSaving ? (
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save Changes
          </Button>
          {!isPublished && (
            <Button
              onClick={() => handleSave(true)}
              disabled={isSaving}
              variant="primary"
            >
              {isSaving ? (
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Save & Publish
            </Button>
          )}
        </div>
      </div>
      {/* Status badges */}
      <div className="flex gap-2 mb-6">
        <Badge className={isPublished ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
          {isPublished ? 'Published' : 'Draft'}
        </Badge>
        <Badge className={type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
          {type}
        </Badge>
        {hasUnsavedChanges() && (
          <Badge className="bg-yellow-100 text-yellow-800">
            Unsaved Changes
          </Badge>
        )}
      </div>
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList className="mb-6">
          <Tabs.TabTrigger value="basic">
            <FileText className="w-4 h-4 mr-2" />
            Basic Information
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="content">
            <FileText className="w-4 h-4 mr-2" />
            Content
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="settings">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Basic Information Tab */}
        <Tabs.TabContent value="basic">
          <Card className="p-6">
            <div className="space-y-6">
              {/* Title */}
              <div>
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter assessment title"
                  className="mt-1"
                />
              </div>
              {/* Description */}
              <div>
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe what this assessment covers"
                  rows={3}
                  className="mt-1"
                />
              </div>
              {/* Type - Read only for existing assessments */}
              <div>
                <Label>Assessment Type</Label>
                <div className="mt-2">
                  <Badge className={type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                    {type === 'quiz' ? 'Quiz' : 'Project'}
                  </Badge>
                  <p className="text-sm text-gray-600 mt-1">
                    Assessment type cannot be changed after creation
                  </p>
                </div>
              </div>
              {/* Category */}
              <div>
                <Label htmlFor="category">Category</Label>
                <Select
                  id="category"
                  value={category}
                  onValueChange={setCategory}
                  className="mt-1"
                >
                  <Select.Option value="">Select category</Select.Option>
                  <Select.Option value="programming">Programming</Select.Option>
                  <Select.Option value="data-science">Data Science</Select.Option>
                  <Select.Option value="web-development">Web Development</Select.Option>
                  <Select.Option value="mobile-development">Mobile Development</Select.Option>
                  <Select.Option value="cloud-computing">Cloud Computing</Select.Option>
                  <Select.Option value="cybersecurity">Cybersecurity</Select.Option>
                  <Select.Option value="soft-skills">Soft Skills</Select.Option>
                  <Select.Option value="other">Other</Select.Option>
                </Select>
              </div>
              {/* Skills */}
              <div>
                <Label htmlFor="skills">Skills</Label>
                <div className="mt-1 flex gap-2">
                  <Input
                    id="skills"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                    placeholder="Add a skill"
                  />
                  <Button
                    type="button"
                    onClick={handleAddSkill}
                    variant="outline"
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
                {skills.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {skills.map(skill => (
                      <Badge key={skill} className="bg-blue-100 text-blue-800">
                        {skill}
                        <button
                          onClick={() => handleRemoveSkill(skill)}
                          className="ml-2 hover:text-blue-900"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        </Tabs.TabContent>
        {/* Content Tab */}
        <Tabs.TabContent value="content">
          {type === 'quiz' ? (
            // Quiz Content
            <div className="space-y-6">
              {/* Questions List */}
              {questions.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Questions ({questions.length})</h3>
                  <div className="space-y-4">
                    {questions.map((question, index) => (
                      <div key={question.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex items-start flex-1">
                            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0">
                              {index + 1}
                            </div>
                            <div className="flex-1">
                              <Input
                                value={question.question}
                                onChange={(e) => handleUpdateQuestion(question.id, { ...question, question: e.target.value })}
                                placeholder="Question text"
                                className="mb-2"
                              />
                              <div className="flex items-center gap-2 mb-2">
                                <Select
                                  value={question.type}
                                  onValueChange={(value) => handleUpdateQuestion(question.id, { ...question, type: value })}
                                  className="w-40"
                                >
                                  <Select.Option value="multipleChoice">Multiple Choice</Select.Option>
                                  <Select.Option value="trueFalse">True/False</Select.Option>
                                  <Select.Option value="shortAnswer">Short Answer</Select.Option>
                                </Select>
                                <Input
                                  type="number"
                                  value={question.points}
                                  onChange={(e) => handleUpdateQuestion(question.id, { ...question, points: Number(e.target.value) })}
                                  min="1"
                                  max="100"
                                  className="w-20"
                                />
                                <span className="text-sm text-gray-500">points</span>
                              </div>
                              {/* Question specific fields */}
                              {question.type === 'multipleChoice' && (
                                <div className="space-y-2">
                                  {question.options.map((option, optionIndex) => (
                                    <div key={optionIndex} className="flex items-center gap-2">
                                      <input
                                        type="radio"
                                        name={`correct-${question.id}`}
                                        checked={question.correctAnswer === optionIndex}
                                        onChange={() => handleUpdateQuestion(question.id, { ...question, correctAnswer: optionIndex })}
                                      />
                                      <Input
                                        value={option}
                                        onChange={(e) => {
                                          const newOptions = [...question.options];
                                          newOptions[optionIndex] = e.target.value;
                                          handleUpdateQuestion(question.id, { ...question, options: newOptions });
                                        }}
                                        placeholder={`Option ${optionIndex + 1}`}
                                      />
                                    </div>
                                  ))}
                                </div>
                              )}
                              {question.type === 'trueFalse' && (
                                <RadioGroup
                                  value={String(question.correctAnswer)}
                                  onValueChange={(value) => handleUpdateQuestion(question.id, { ...question, correctAnswer: value === 'true' })}
                                  className="flex gap-4"
                                >
                                  <div className="flex items-center space-x-2">
                                    <RadioGroup.Item value="true" id={`true-${question.id}`} />
                                    <Label htmlFor={`true-${question.id}`}>True</Label>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <RadioGroup.Item value="false" id={`false-${question.id}`} />
                                    <Label htmlFor={`false-${question.id}`}>False</Label>
                                  </div>
                                </RadioGroup>
                              )}
                              {question.type === 'shortAnswer' && (
                                <Input
                                  value={question.correctAnswer}
                                  onChange={(e) => handleUpdateQuestion(question.id, { ...question, correctAnswer: e.target.value })}
                                  placeholder="Correct answer(s) separated by | for alternatives"
                                />
                              )}
                              <div className="mt-2">
                                <Input
                                  value={question.explanation || ''}
                                  onChange={(e) => handleUpdateQuestion(question.id, { ...question, explanation: e.target.value })}
                                  placeholder="Explanation (optional)"
                                />
                              </div>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveQuestion(question.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600">
                      Total Points: {questions.reduce((sum, q) => sum + q.points, 0)}
                    </p>
                  </div>
                </Card>
              )}
              {/* Add Question Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Add New Question</h3>
                <div className="space-y-4">
                  {/* Question Type */}
                  <div>
                    <Label htmlFor="questionType">Question Type</Label>
                    <Select
                      id="questionType"
                      value={currentQuestion.type}
                      onValueChange={handleQuestionTypeChange}
                      className="mt-1"
                    >
                      <Select.Option value="multipleChoice">Multiple Choice</Select.Option>
                      <Select.Option value="trueFalse">True/False</Select.Option>
                      <Select.Option value="shortAnswer">Short Answer</Select.Option>
                    </Select>
                  </div>
                  {/* Question Text */}
                  <div>
                    <Label htmlFor="questionText">Question</Label>
                    <Textarea
                      id="questionText"
                      value={currentQuestion.question}
                      onChange={(e) => setCurrentQuestion({ ...currentQuestion, question: e.target.value })}
                      placeholder="Enter your question"
                      rows={2}
                      className="mt-1"
                    />
                  </div>
                  {/* Options for Multiple Choice */}
                  {currentQuestion.type === 'multipleChoice' && (
                    <div>
                      <Label>Options</Label>
                      <div className="space-y-2 mt-1">
                        {currentQuestion.options.map((option, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <input
                              type="radio"
                              name="correctAnswer"
                              checked={currentQuestion.correctAnswer === index}
                              onChange={() => setCurrentQuestion({ ...currentQuestion, correctAnswer: index })}
                            />
                            <Input
                              value={option}
                              onChange={(e) => {
                                const newOptions = [...currentQuestion.options];
                                newOptions[index] = e.target.value;
                                setCurrentQuestion({ ...currentQuestion, options: newOptions });
                              }}
                              placeholder={`Option ${index + 1}`}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {/* True/False Options */}
                  {currentQuestion.type === 'trueFalse' && (
                    <div>
                      <Label>Correct Answer</Label>
                      <RadioGroup
                        value={String(currentQuestion.correctAnswer)}
                        onValueChange={(value) => setCurrentQuestion({ ...currentQuestion, correctAnswer: value === 'true' })}
                        className="mt-1"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroup.Item value="true" id="true" />
                          <Label htmlFor="true">True</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroup.Item value="false" id="false" />
                          <Label htmlFor="false">False</Label>
                        </div>
                      </RadioGroup>
                    </div>
                  )}
                  {/* Short Answer */}
                  {currentQuestion.type === 'shortAnswer' && (
                    <div>
                      <Label htmlFor="correctAnswer">Correct Answer(s)</Label>
                      <Input
                        id="correctAnswer"
                        value={currentQuestion.correctAnswer}
                        onChange={(e) => setCurrentQuestion({ ...currentQuestion, correctAnswer: e.target.value })}
                        placeholder="Enter correct answer(s) separated by | for alternatives"
                        className="mt-1"
                      />
                    </div>
                  )}
                  {/* Points */}
                  <div>
                    <Label htmlFor="points">Points</Label>
                    <Input
                      id="points"
                      type="number"
                      value={currentQuestion.points}
                      onChange={(e) => setCurrentQuestion({ ...currentQuestion, points: Number(e.target.value) })}
                      min="1"
                      max="100"
                      className="mt-1"
                    />
                  </div>
                  {/* Explanation */}
                  <div>
                    <Label htmlFor="explanation">Explanation (Optional)</Label>
                    <Textarea
                      id="explanation"
                      value={currentQuestion.explanation}
                      onChange={(e) => setCurrentQuestion({ ...currentQuestion, explanation: e.target.value })}
                      placeholder="Provide an explanation for the correct answer"
                      rows={2}
                      className="mt-1"
                    />
                  </div>
                  <Button onClick={handleAddQuestion} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Question
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            // Project Content
            <div className="space-y-6">
              {/* Requirements List */}
              {requirements.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Requirements ({requirements.length})</h3>
                  <div className="space-y-3">
                    {requirements.map((requirement, index) => (
                      <div key={requirement.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex items-start flex-1">
                            <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0 mt-0.5">
                              {index + 1}
                            </div>
                            <div className="flex-1">
                              <Textarea
                                value={requirement.description}
                                onChange={(e) => handleUpdateRequirement(requirement.id, { ...requirement, description: e.target.value })}
                                placeholder="Requirement description"
                                rows={2}
                                className="mb-2"
                              />
                              <div className="flex items-center gap-2">
                                <Input
                                  type="number"
                                  value={requirement.points}
                                  onChange={(e) => handleUpdateRequirement(requirement.id, { ...requirement, points: Number(e.target.value) })}
                                  min="1"
                                  max="100"
                                  className="w-20"
                                />
                                <span className="text-sm text-gray-500">points</span>
                              </div>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveRequirement(requirement.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600">
                      Total Points: {requirements.reduce((sum, r) => sum + r.points, 0)}
                    </p>
                  </div>
                </Card>
              )}
              {/* Add Requirement Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Add New Requirement</h3>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="requirementDesc">Requirement Description</Label>
                    <Textarea
                      id="requirementDesc"
                      value={currentRequirement.description}
                      onChange={(e) => setCurrentRequirement({ ...currentRequirement, description: e.target.value })}
                      placeholder="Describe what the student needs to do"
                      rows={3}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="requirementPoints">Points</Label>
                    <Input
                      id="requirementPoints"
                      type="number"
                      value={currentRequirement.points}
                      onChange={(e) => setCurrentRequirement({ ...currentRequirement, points: Number(e.target.value) })}
                      min="1"
                      max="100"
                      className="mt-1"
                    />
                  </div>
                  <Button onClick={handleAddRequirement} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Requirement
                  </Button>
                </div>
              </Card>
              {/* Resources */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Resources</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Add helpful resources for students working on this project
                </p>
                <Button variant="outline" className="w-full" disabled>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Resource
                </Button>
              </Card>
            </div>
          )}
        </Tabs.TabContent>
        {/* Settings Tab */}
        <Tabs.TabContent value="settings">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Basic Settings</h3>
              <div className="space-y-4">
                {type === 'quiz' && (
                  <>
                    <div>
                      <Label htmlFor="timeLimit">Time Limit (minutes)</Label>
                      <Input
                        id="timeLimit"
                        type="number"
                        value={settings.timeLimit}
                        onChange={(e) => setSettings({ ...settings, timeLimit: Number(e.target.value) })}
                        min="0"
                        className="mt-1"
                      />
                      <p className="text-sm text-gray-600 mt-1">0 = No time limit</p>
                    </div>
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
                  </>
                )}
                <div>
                  <Label htmlFor="passingScore">Passing Score (%)</Label>
                  <Input
                    id="passingScore"
                    type="number"
                    value={settings.passingScore}
                    onChange={(e) => setSettings({ ...settings, passingScore: Number(e.target.value) })}
                    min="0"
                    max="100"
                    className="mt-1"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="allowLate">Allow Late Submission</Label>
                    <p className="text-sm text-gray-600">Students can submit after due date</p>
                  </div>
                  <Switch
                    id="allowLate"
                    checked={settings.allowLateSubmission}
                    onCheckedChange={(checked) => setSettings({ ...settings, allowLateSubmission: checked })}
                  />
                </div>
                {settings.allowLateSubmission && (
                  <div>
                    <Label htmlFor="latePenalty">Late Penalty (% per day)</Label>
                    <Input
                      id="latePenalty"
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
            </Card>
            {/* Quiz Settings */}
            {type === 'quiz' && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Quiz Settings</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="shuffleQuestions">Shuffle Questions</Label>
                      <p className="text-sm text-gray-600">Randomize question order</p>
                    </div>
                    <Switch
                      id="shuffleQuestions"
                      checked={settings.shuffleQuestions}
                      onCheckedChange={(checked) => setSettings({ ...settings, shuffleQuestions: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="showCorrectAnswers">Show Correct Answers</Label>
                      <p className="text-sm text-gray-600">After submission</p>
                    </div>
                    <Switch
                      id="showCorrectAnswers"
                      checked={settings.showCorrectAnswers}
                      onCheckedChange={(checked) => setSettings({ ...settings, showCorrectAnswers: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="autoGrade">Auto-grading</Label>
                      <p className="text-sm text-gray-600">Grade automatically on submission</p>
                    </div>
                    <Switch
                      id="autoGrade"
                      checked={settings.autoGrade}
                      onCheckedChange={(checked) => setSettings({ ...settings, autoGrade: checked })}
                    />
                  </div>
                </div>
              </Card>
            )}
            {/* Notification Settings */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Notifications</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notifySubmission">On Submission</Label>
                    <p className="text-sm text-gray-600">Notify when students submit</p>
                  </div>
                  <Switch
                    id="notifySubmission"
                    checked={settings.notifyOnSubmission}
                    onCheckedChange={(checked) => setSettings({ ...settings, notifyOnSubmission: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notifyDue">Before Due Date</Label>
                    <p className="text-sm text-gray-600">Remind students</p>
                  </div>
                  <Switch
                    id="notifyDue"
                    checked={settings.notifyBeforeDue}
                    onCheckedChange={(checked) => setSettings({ ...settings, notifyBeforeDue: checked })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="notifyGrade">On Grading</Label>
                    <p className="text-sm text-gray-600">Notify students when graded</p>
                  </div>
                  <Switch
                    id="notifyGrade"
                    checked={settings.notifyOnGrade}
                    onCheckedChange={(checked) => setSettings({ ...settings, notifyOnGrade: checked })}
                  />
                </div>
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
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
                navigate('/assessment');
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
export default TrainerAssessmentEditPage;