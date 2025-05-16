import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Save, Plus, Trash2, GripVertical, 
  FileText, Settings, HelpCircle, ChevronRight
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

/**
 * TrainerAssessmentCreationPage allows trainers to create new assessment templates
 */
const TrainerAssessmentCreationPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('basic');
  const [isSaving, setIsSaving] = useState(false);
  const [isDraft, setIsDraft] = useState(true);
  
  // Basic info state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('quiz');
  const [category, setCategory] = useState('');
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  
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
        case 'matching':
          return {
            ...base,
            items: [
              { id: '1', text: '', match: '' },
              { id: '2', text: '', match: '' },
              { id: '3', text: '', match: '' },
              { id: '4', text: '', match: '' }
            ],
            correctMatches: {}
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
  
  // Save assessment
  const handleSave = async (publish = false) => {
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
        is_published: publish,
        settings,
        ...(type === 'quiz' ? { questions } : { requirements, rubric, resources }),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      const response = await fetch('/api/assessment/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });
      
      if (!response.ok) throw new Error('Failed to create assessment');
      
      const createdTemplate = await response.json();
      
      toast({
        title: 'Success',
        description: `Assessment ${publish ? 'published' : 'saved as draft'} successfully`,
        type: 'success',
      });
      
      navigate(`/assessment/templates/${createdTemplate.id}`);
    } catch (err) {
      console.error('Error creating assessment:', err);
      toast({
        title: 'Error',
        description: 'Failed to create assessment',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };
  
  // Tab validation indicators
  const isBasicInfoValid = title.trim() && description.trim();
  const isContentValid = type === 'quiz' ? questions.length > 0 : requirements.length > 0;
  
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
            <h1 className="text-2xl font-bold">Create New Assessment</h1>
            <p className="text-gray-600">Design a new assessment template</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => handleSave(false)}
            disabled={isSaving || !isBasicInfoValid}
          >
            {isSaving ? (
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save as Draft
          </Button>
          <Button
            onClick={() => handleSave(true)}
            disabled={isSaving || !isBasicInfoValid || !isContentValid}
          >
            {isSaving ? (
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-current"></div>
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Publish
          </Button>
        </div>
      </div>
      
      {/* Progress indicator */}
      <Card className="p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center ${isBasicInfoValid ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                isBasicInfoValid ? 'bg-green-100' : 'bg-gray-100'
              }`}>
                1
              </div>
              <span className="ml-2 font-medium">Basic Info</span>
            </div>
            
            <ChevronRight className="w-5 h-5 text-gray-400" />
            
            <div className={`flex items-center ${isContentValid ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                isContentValid ? 'bg-green-100' : 'bg-gray-100'
              }`}>
                2
              </div>
              <span className="ml-2 font-medium">Content</span>
            </div>
            
            <ChevronRight className="w-5 h-5 text-gray-400" />
            
            <div className="flex items-center text-gray-400">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                3
              </div>
              <span className="ml-2 font-medium">Settings</span>
            </div>
          </div>
        </div>
      </Card>
      
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
              
              {/* Type */}
              <div>
                <Label>Assessment Type *</Label>
                <RadioGroup
                  value={type}
                  onValueChange={setType}
                  className="mt-2"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroup.Item value="quiz" id="quiz" />
                    <Label htmlFor="quiz" className="font-normal cursor-pointer">
                      Quiz
                      <span className="text-sm text-gray-600 ml-2">
                        Multiple choice, true/false, short answer questions
                      </span>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroup.Item value="project" id="project" />
                    <Label htmlFor="project" className="font-normal cursor-pointer">
                      Project
                      <span className="text-sm text-gray-600 ml-2">
                        Practical assignment with requirements and rubric
                      </span>
                    </Label>
                  </div>
                </RadioGroup>
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
              {/* Add Question Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Add Question</h3>
                
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
                      <Select.Option value="multipleAnswer">Multiple Answer</Select.Option>
                      <Select.Option value="trueFalse">True/False</Select.Option>
                      <Select.Option value="shortAnswer">Short Answer</Select.Option>
                      <Select.Option value="matching">Matching</Select.Option>
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
                  
                  {/* Options for Multiple Choice/Answer */}
                  {(currentQuestion.type === 'multipleChoice' || currentQuestion.type === 'multipleAnswer') && (
                    <div>
                      <Label>Options</Label>
                      <div className="space-y-2 mt-1">
                        {currentQuestion.options.map((option, index) => (
                          <div key={index} className="flex items-center gap-2">
                            {currentQuestion.type === 'multipleChoice' ? (
                              <input
                                type="radio"
                                name="correctAnswer"
                                checked={currentQuestion.correctAnswer === index}
                                onChange={() => setCurrentQuestion({ ...currentQuestion, correctAnswer: index })}
                              />
                            ) : (
                              <Checkbox
                                checked={currentQuestion.correctAnswers?.includes(index) || false}
                                onCheckedChange={(checked) => {
                                  const answers = currentQuestion.correctAnswers || [];
                                  if (checked) {
                                    setCurrentQuestion({
                                      ...currentQuestion,
                                      correctAnswers: [...answers, index]
                                    });
                                  } else {
                                    setCurrentQuestion({
                                      ...currentQuestion,
                                      correctAnswers: answers.filter(a => a !== index)
                                    });
                                  }
                                }}
                              />
                            )}
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
                  
                  {/* Matching */}
                  {currentQuestion.type === 'matching' && (
                    <div>
                      <Label>Matching Pairs</Label>
                      <div className="space-y-2 mt-1">
                        {currentQuestion.items?.map((item, index) => (
                          <div key={item.id} className="flex items-center gap-2">
                            <Input
                              value={item.text}
                              onChange={(e) => {
                                const newItems = [...currentQuestion.items];
                                newItems[index] = { ...item, text: e.target.value };
                                setCurrentQuestion({ ...currentQuestion, items: newItems });
                              }}
                              placeholder="Item text"
                              className="flex-1"
                            />
                            <span>→</span>
                            <Input
                              value={item.match}
                              onChange={(e) => {
                                const newItems = [...currentQuestion.items];
                                newItems[index] = { ...item, match: e.target.value };
                                const newMatches = { ...currentQuestion.correctMatches };
                                newMatches[item.id] = index;
                                setCurrentQuestion({ 
                                  ...currentQuestion, 
                                  items: newItems,
                                  correctMatches: newMatches
                                });
                              }}
                              placeholder="Matching text"
                              className="flex-1"
                            />
                            {currentQuestion.items.length > 2 && (
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  const newItems = currentQuestion.items.filter((_, i) => i !== index);
                                  const newMatches = { ...currentQuestion.correctMatches };
                                  delete newMatches[item.id];
                                  setCurrentQuestion({ ...currentQuestion, items: newItems, correctMatches: newMatches });
                                }}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                      {currentQuestion.items?.length < 6 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="mt-2"
                          onClick={() => {
                            const newItem = { id: String(Date.now()), text: '', match: '' };
                            setCurrentQuestion({
                              ...currentQuestion,
                              items: [...currentQuestion.items, newItem]
                            });
                          }}
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Add Matching Pair
                        </Button>
                      )}
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
                              <p className="font-medium mb-1">{question.question}</p>
                              <div className="flex items-center gap-2 mb-2">
                                <Badge className="bg-blue-100 text-blue-800">
                                  {question.type}
                                </Badge>
                                <span className="text-sm text-gray-500">{question.points} points</span>
                              </div>
                              
                              {/* Display answer based on type */}
                              {question.type === 'multipleChoice' && (
                                <div className="text-sm text-gray-600">
                                  Correct: {question.options[question.correctAnswer]}
                                </div>
                              )}
                              
                              {question.type === 'trueFalse' && (
                                <div className="text-sm text-gray-600">
                                  Correct: {question.correctAnswer ? 'True' : 'False'}
                                </div>
                              )}
                              
                              {question.type === 'shortAnswer' && (
                                <div className="text-sm text-gray-600">
                                  Correct: {question.correctAnswer}
                                </div>
                              )}
                              
                              {question.explanation && (
                                <p className="text-sm text-gray-600 mt-1">
                                  <span className="font-medium">Explanation:</span> {question.explanation}
                                </p>
                              )}
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
            </div>
          ) : (
            // Project Content
            <div className="space-y-6">
              {/* Add Requirement Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Add Requirement</h3>
                
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
                              <p>{requirement.description}</p>
                              <p className="text-sm text-gray-500 mt-1">{requirement.points} points</p>
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
              
              {/* Resources */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Resources (Optional)</h3>
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
    </div>
  );
};

export default TrainerAssessmentCreationPage;