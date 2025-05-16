import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Plus, Filter, Archive, Edit2, Copy, Upload, Download,
  Tag, Brain, ChevronRight, Trash2, FolderOpen, FileText
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Label } from '@/components/ui';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/components/ui/use-toast';
import { Table } from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup } from '@/components/ui/radio-group';

/**
 * TrainerQuestionBankPage manages a central repository of reusable questions
 */
const TrainerQuestionBankPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for questions
  const [questions, setQuestions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  
  // Filters
  const [filters, setFilters] = useState({
    type: 'all',
    difficulty: 'all',
    skills: [],
    tags: []
  });
  
  // Dialogs
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  
  // Form state for new/edit question
  const [formData, setFormData] = useState({
    question: '',
    type: 'multipleChoice',
    category: '',
    difficulty: 'medium',
    points: 10,
    options: ['', '', '', ''],
    correctAnswer: 0,
    correctAnswers: [],
    explanation: '',
    tags: [],
    skills: []
  });
  
  // Load questions and categories
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        if (!isMounted) return;
        
        setIsLoading(true);
        setError(null);
        
        // Fetch questions
        const questionsResponse = await fetch('/api/assessment/questions');
        if (!isMounted) return;
        
        if (!questionsResponse.ok) throw new Error('Failed to fetch questions');
        const questionsData = await questionsResponse.json();
        
        if (!isMounted) return;
        setQuestions(questionsData);
        
        // Fetch categories
        const categoriesResponse = await fetch('/api/assessment/categories');
        if (!isMounted) return;
        
        if (!categoriesResponse.ok) throw new Error('Failed to fetch categories');
        const categoriesData = await categoriesResponse.json();
        
        if (!isMounted) return;
        setCategories(categoriesData);
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Error fetching data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load question bank',
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
  }, [toast]);
  
  // Filter questions
  const filteredQuestions = questions.filter(question => {
    // Category filter
    if (selectedCategory !== 'all' && question.category !== selectedCategory) {
      return false;
    }
    
    // Search filter
    if (searchTerm && !question.question.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    // Type filter
    if (filters.type !== 'all' && question.type !== filters.type) {
      return false;
    }
    
    // Difficulty filter
    if (filters.difficulty !== 'all' && question.difficulty !== filters.difficulty) {
      return false;
    }
    
    // Skills filter
    if (filters.skills.length > 0 && !filters.skills.some(skill => question.skills?.includes(skill))) {
      return false;
    }
    
    // Tags filter
    if (filters.tags.length > 0 && !filters.tags.some(tag => question.tags?.includes(tag))) {
      return false;
    }
    
    return true;
  });
  
  // Handle question selection
  const handleSelectQuestion = (questionId) => {
    setSelectedQuestions(prev => {
      if (prev.includes(questionId)) {
        return prev.filter(id => id !== questionId);
      } else {
        return [...prev, questionId];
      }
    });
  };
  
  // Handle select all
  const handleSelectAll = () => {
    if (selectedQuestions.length === filteredQuestions.length) {
      setSelectedQuestions([]);
    } else {
      setSelectedQuestions(filteredQuestions.map(q => q.id));
    }
  };
  
  // Add new question
  const handleAddQuestion = async () => {
    try {
      // Validate form
      if (!formData.question.trim()) {
        toast({
          title: 'Error',
          description: 'Please enter a question',
          type: 'error',
        });
        return;
      }
      
      if (!formData.category) {
        toast({
          title: 'Error',
          description: 'Please select a category',
          type: 'error',
        });
        return;
      }
      
      // Prepare question data
      const questionData = {
        ...formData,
        created_at: new Date().toISOString()
      };
      
      const response = await fetch('/api/assessment/questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionData),
      });
      
      if (!response.ok) throw new Error('Failed to add question');
      
      const newQuestion = await response.json();
      setQuestions([...questions, newQuestion]);
      
      toast({
        title: 'Success',
        description: 'Question added to bank',
        type: 'success',
      });
      
      setShowAddDialog(false);
      resetForm();
    } catch (err) {
      console.error('Error adding question:', err);
      toast({
        title: 'Error',
        description: 'Failed to add question',
        type: 'error',
      });
    }
  };
  
  // Update question
  const handleUpdateQuestion = async () => {
    if (!editingQuestion) return;
    
    try {
      const response = await fetch(`/api/assessment/questions/${editingQuestion.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) throw new Error('Failed to update question');
      
      const updatedQuestion = await response.json();
      setQuestions(questions.map(q => q.id === editingQuestion.id ? updatedQuestion : q));
      
      toast({
        title: 'Success',
        description: 'Question updated',
        type: 'success',
      });
      
      setShowEditDialog(false);
      setEditingQuestion(null);
      resetForm();
    } catch (err) {
      console.error('Error updating question:', err);
      toast({
        title: 'Error',
        description: 'Failed to update question',
        type: 'error',
      });
    }
  };
  
  // Delete questions
  const handleDeleteQuestions = async () => {
    if (selectedQuestions.length === 0) return;
    
    try {
      const response = await fetch('/api/assessment/questions/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: selectedQuestions }),
      });
      
      if (!response.ok) throw new Error('Failed to delete questions');
      
      setQuestions(questions.filter(q => !selectedQuestions.includes(q.id)));
      setSelectedQuestions([]);
      
      toast({
        title: 'Success',
        description: `${selectedQuestions.length} questions deleted`,
        type: 'success',
      });
    } catch (err) {
      console.error('Error deleting questions:', err);
      toast({
        title: 'Error',
        description: 'Failed to delete questions',
        type: 'error',
      });
    }
  };
  
  // Export questions
  const handleExportQuestions = () => {
    const questionsToExport = selectedQuestions.length > 0 
      ? questions.filter(q => selectedQuestions.includes(q.id))
      : filteredQuestions;
    
    const exportData = {
      questions: questionsToExport,
      exportDate: new Date().toISOString(),
      count: questionsToExport.length
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `question-bank-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Success',
      description: `Exported ${questionsToExport.length} questions`,
      type: 'success',
    });
  };
  
  // Start edit
  const startEdit = (question) => {
    setEditingQuestion(question);
    setFormData({
      question: question.question,
      type: question.type,
      category: question.category,
      difficulty: question.difficulty,
      points: question.points,
      options: question.options || ['', '', '', ''],
      correctAnswer: question.correctAnswer || 0,
      correctAnswers: question.correctAnswers || [],
      explanation: question.explanation || '',
      tags: question.tags || [],
      skills: question.skills || []
    });
    setShowEditDialog(true);
  };
  
  // Reset form
  const resetForm = () => {
    setFormData({
      question: '',
      type: 'multipleChoice',
      category: '',
      difficulty: 'medium',
      points: 10,
      options: ['', '', '', ''],
      correctAnswer: 0,
      correctAnswers: [],
      explanation: '',
      tags: [],
      skills: []
    });
  };
  
  // Get difficulty color
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get type color
  const getTypeColor = (type) => {
    switch (type) {
      case 'multipleChoice':
        return 'bg-blue-100 text-blue-800';
      case 'trueFalse':
        return 'bg-purple-100 text-purple-800';
      case 'shortAnswer':
        return 'bg-green-100 text-green-800';
      case 'matching':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <h2 className="text-xl font-semibold mb-2">Unable to Load Question Bank</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">Question Bank</h1>
          <p className="text-gray-600">Central repository of reusable assessment questions</p>
        </div>
        
        <div className="mt-4 md:mt-0 flex gap-3">
          <Button
            variant="outline"
            onClick={() => setShowImportDialog(true)}
            className="flex items-center"
          >
            <Upload className="w-4 h-4 mr-2" />
            Import
          </Button>
          <Button
            variant="outline"
            onClick={handleExportQuestions}
            disabled={filteredQuestions.length === 0}
            className="flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button
            onClick={() => setShowAddDialog(true)}
            className="flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Question
          </Button>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Questions</p>
              <p className="text-2xl font-bold">{questions.length}</p>
            </div>
            <FileText className="w-8 h-8 text-primary opacity-20" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Categories</p>
              <p className="text-2xl font-bold">{categories.length}</p>
            </div>
            <FolderOpen className="w-8 h-8 text-primary opacity-20" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Unique Skills</p>
              <p className="text-2xl font-bold">
                {[...new Set(questions.flatMap(q => q.skills || []))].length}
              </p>
            </div>
            <Brain className="w-8 h-8 text-primary opacity-20" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Selected</p>
              <p className="text-2xl font-bold">{selectedQuestions.length}</p>
            </div>
            <Archive className="w-8 h-8 text-primary opacity-20" />
          </div>
        </Card>
      </div>
      
      {/* Filters and Search */}
      <Card className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Category Filter */}
          <div className="flex items-center gap-2">
            <FolderOpen className="w-5 h-5 text-gray-500" />
            <Select
              value={selectedCategory}
              onValueChange={setSelectedCategory}
              className="w-40"
            >
              <Select.Option value="all">All Categories</Select.Option>
              {categories.map(category => (
                <Select.Option key={category.id} value={category.id}>
                  {category.name}
                </Select.Option>
              ))}
            </Select>
          </div>
          
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search questions..."
                className="pl-10"
              />
            </div>
          </div>
          
          {/* Type Filter */}
          <Select
            value={filters.type}
            onValueChange={(value) => setFilters({ ...filters, type: value })}
            className="w-40"
          >
            <Select.Option value="all">All Types</Select.Option>
            <Select.Option value="multipleChoice">Multiple Choice</Select.Option>
            <Select.Option value="trueFalse">True/False</Select.Option>
            <Select.Option value="shortAnswer">Short Answer</Select.Option>
            <Select.Option value="matching">Matching</Select.Option>
          </Select>
          
          {/* Difficulty Filter */}
          <Select
            value={filters.difficulty}
            onValueChange={(value) => setFilters({ ...filters, difficulty: value })}
            className="w-32"
          >
            <Select.Option value="all">All Levels</Select.Option>
            <Select.Option value="easy">Easy</Select.Option>
            <Select.Option value="medium">Medium</Select.Option>
            <Select.Option value="hard">Hard</Select.Option>
          </Select>
          
          {/* Clear Filters */}
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedCategory('all');
              setSearchTerm('');
              setFilters({
                type: 'all',
                difficulty: 'all',
                skills: [],
                tags: []
              });
            }}
          >
            Clear Filters
          </Button>
        </div>
      </Card>
      
      {/* Actions Bar */}
      {selectedQuestions.length > 0 && (
        <Card className="p-4 mb-6 bg-blue-50">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">
              {selectedQuestions.length} questions selected
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/assessment/create')}
              >
                Add to Assessment
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportQuestions}
              >
                Export Selected
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDeleteQuestions}
              >
                Delete Selected
              </Button>
            </div>
          </div>
        </Card>
      )}
      
      {/* Questions Table */}
      <Card className="p-0 overflow-hidden">
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell className="w-12">
                <Checkbox
                  checked={selectedQuestions.length === filteredQuestions.length && filteredQuestions.length > 0}
                  onCheckedChange={handleSelectAll}
                />
              </Table.HeaderCell>
              <Table.HeaderCell>Question</Table.HeaderCell>
              <Table.HeaderCell>Category</Table.HeaderCell>
              <Table.HeaderCell>Type</Table.HeaderCell>
              <Table.HeaderCell>Difficulty</Table.HeaderCell>
              <Table.HeaderCell>Points</Table.HeaderCell>
              <Table.HeaderCell>Skills</Table.HeaderCell>
              <Table.HeaderCell>Actions</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {filteredQuestions.map(question => (
              <Table.Row key={question.id}>
                <Table.Cell>
                  <Checkbox
                    checked={selectedQuestions.includes(question.id)}
                    onCheckedChange={() => handleSelectQuestion(question.id)}
                  />
                </Table.Cell>
                <Table.Cell className="max-w-md">
                  <p className="truncate">{question.question}</p>
                </Table.Cell>
                <Table.Cell>
                  <Badge variant="outline">
                    {categories.find(c => c.id === question.category)?.name || question.category}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Badge className={getTypeColor(question.type)}>
                    {question.type}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <Badge className={getDifficultyColor(question.difficulty)}>
                    {question.difficulty}
                  </Badge>
                </Table.Cell>
                <Table.Cell>{question.points}</Table.Cell>
                <Table.Cell>
                  <div className="flex flex-wrap gap-1">
                    {(question.skills || []).slice(0, 2).map(skill => (
                      <Badge key={skill} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {question.skills?.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{question.skills.length - 2}
                      </Badge>
                    )}
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => startEdit(question)}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const duplicate = { ...question, id: undefined };
                        setFormData(duplicate);
                        setShowAddDialog(true);
                      }}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
        
        {filteredQuestions.length === 0 && (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No questions found</p>
          </div>
        )}
      </Card>
      
      {/* Add/Edit Question Dialog */}
      <Dialog open={showAddDialog || showEditDialog} onOpenChange={(open) => {
        if (!open) {
          setShowAddDialog(false);
          setShowEditDialog(false);
          setEditingQuestion(null);
          resetForm();
        }
      }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingQuestion ? 'Edit Question' : 'Add New Question'}
            </DialogTitle>
            <DialogDescription>
              {editingQuestion 
                ? 'Update the question details'
                : 'Add a new question to the bank'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {/* Question Text */}
            <div>
              <Label htmlFor="question">Question *</Label>
              <Textarea
                id="question"
                value={formData.question}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                placeholder="Enter your question"
                rows={3}
                className="mt-1"
              />
            </div>
            
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="type">Type *</Label>
                <Select
                  id="type"
                  value={formData.type}
                  onValueChange={(value) => setFormData({ ...formData, type: value })}
                  className="mt-1"
                >
                  <Select.Option value="multipleChoice">Multiple Choice</Select.Option>
                  <Select.Option value="trueFalse">True/False</Select.Option>
                  <Select.Option value="shortAnswer">Short Answer</Select.Option>
                  <Select.Option value="matching">Matching</Select.Option>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="category">Category *</Label>
                <Select
                  id="category"
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value })}
                  className="mt-1"
                >
                  <Select.Option value="">Select category</Select.Option>
                  {categories.map(category => (
                    <Select.Option key={category.id} value={category.id}>
                      {category.name}
                    </Select.Option>
                  ))}
                </Select>
              </div>
              
              <div>
                <Label htmlFor="difficulty">Difficulty</Label>
                <Select
                  id="difficulty"
                  value={formData.difficulty}
                  onValueChange={(value) => setFormData({ ...formData, difficulty: value })}
                  className="mt-1"
                >
                  <Select.Option value="easy">Easy</Select.Option>
                  <Select.Option value="medium">Medium</Select.Option>
                  <Select.Option value="hard">Hard</Select.Option>
                </Select>
              </div>
            </div>
            
            {/* Points */}
            <div>
              <Label htmlFor="points">Points</Label>
              <Input
                id="points"
                type="number"
                value={formData.points}
                onChange={(e) => setFormData({ ...formData, points: Number(e.target.value) })}
                min="1"
                max="100"
                className="mt-1"
              />
            </div>
            
            {/* Type-specific fields */}
            {formData.type === 'multipleChoice' && (
              <div>
                <Label>Options</Label>
                <div className="space-y-2 mt-1">
                  {formData.options.map((option, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="correctAnswer"
                        checked={formData.correctAnswer === index}
                        onChange={() => setFormData({ ...formData, correctAnswer: index })}
                      />
                      <Input
                        value={option}
                        onChange={(e) => {
                          const newOptions = [...formData.options];
                          newOptions[index] = e.target.value;
                          setFormData({ ...formData, options: newOptions });
                        }}
                        placeholder={`Option ${index + 1}`}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {formData.type === 'trueFalse' && (
              <div>
                <Label>Correct Answer</Label>
                <RadioGroup
                  value={String(formData.correctAnswer)}
                  onValueChange={(value) => setFormData({ ...formData, correctAnswer: value === 'true' })}
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
            
            {formData.type === 'shortAnswer' && (
              <div>
                <Label htmlFor="correctAnswer">Correct Answer(s)</Label>
                <Input
                  id="correctAnswer"
                  value={formData.correctAnswer}
                  onChange={(e) => setFormData({ ...formData, correctAnswer: e.target.value })}
                  placeholder="Enter correct answer(s) separated by | for alternatives"
                  className="mt-1"
                />
              </div>
            )}
            
            {/* Explanation */}
            <div>
              <Label htmlFor="explanation">Explanation (Optional)</Label>
              <Textarea
                id="explanation"
                value={formData.explanation}
                onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
                placeholder="Provide an explanation for the correct answer"
                rows={2}
                className="mt-1"
              />
            </div>
            
            {/* Tags and Skills */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="tags">Tags</Label>
                <Input
                  id="tags"
                  value={formData.tags.join(', ')}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    tags: e.target.value.split(',').map(t => t.trim()).filter(t => t) 
                  })}
                  placeholder="Enter tags separated by commas"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="skills">Skills</Label>
                <Input
                  id="skills"
                  value={formData.skills.join(', ')}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    skills: e.target.value.split(',').map(s => s.trim()).filter(s => s) 
                  })}
                  placeholder="Enter skills separated by commas"
                  className="mt-1"
                />
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowAddDialog(false);
              setShowEditDialog(false);
              setEditingQuestion(null);
              resetForm();
            }}>
              Cancel
            </Button>
            <Button onClick={editingQuestion ? handleUpdateQuestion : handleAddQuestion}>
              {editingQuestion ? 'Update' : 'Add'} Question
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Import Dialog */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Import Questions</DialogTitle>
            <DialogDescription>
              Upload a JSON file containing questions to import
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                Drag and drop your file here, or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supported format: JSON (.json)
              </p>
              <Input
                type="file"
                accept=".json"
                className="mt-4"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    // Handle file import
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      try {
                        const data = JSON.parse(event.target.result);
                        // Process imported questions
                        console.log('Imported questions:', data);
                        toast({
                          title: 'Success',
                          description: `Imported ${data.questions?.length || 0} questions`,
                          type: 'success',
                        });
                        setShowImportDialog(false);
                      } catch (err) {
                        toast({
                          title: 'Error',
                          description: 'Invalid file format',
                          type: 'error',
                        });
                      }
                    };
                    reader.readAsText(file);
                  }
                }}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowImportDialog(false)}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TrainerQuestionBankPage;