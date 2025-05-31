import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Sparkles, Bot, RefreshCw, Plus, Trash2, Copy, Check } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../ui/LoadingSpinner';
import { Badge } from '../ui/badge';
import api from '../../lib/api';

const AIQuestionGenerator = ({ onQuestionsGenerated, testId }) => {
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [questionType, setQuestionType] = useState('multiple_choice');
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [context, setContext] = useState('');
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const { toast } = useToast();

  const handleGenerateQuestions = async () => {
    if (!topic) {
      toast({
        title: "Error",
        description: "Please enter a topic for question generation",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/ai/generate-questions', {
        topic,
        difficulty,
        question_type: questionType,
        number_of_questions: numberOfQuestions,
        context,
        test_id: testId
      });

      setGeneratedQuestions(response.data.questions || []);
      toast({
        title: "Success",
        description: `Generated ${response.data.questions?.length || 0} questions successfully`
      });
    } catch (error) {
      console.error('Error generating questions:', error);
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to generate questions",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddQuestion = (question) => {
    if (onQuestionsGenerated) {
      onQuestionsGenerated([question]);
      toast({
        title: "Success",
        description: "Question added successfully"
      });
    }
  };

  const handleAddAllQuestions = () => {
    if (onQuestionsGenerated && generatedQuestions.length > 0) {
      onQuestionsGenerated(generatedQuestions);
      toast({
        title: "Success",
        description: `Added ${generatedQuestions.length} questions successfully`
      });
      setGeneratedQuestions([]);
    }
  };

  const handleRemoveQuestion = (index) => {
    setGeneratedQuestions(prev => prev.filter((_, i) => i !== index));
  };

  const handleCopyQuestion = (question, index) => {
    const questionText = `${question.question}\n\nOptions:\n${question.options?.map((opt, i) => `${i + 1}. ${opt}`).join('\n') || ''}\n\nCorrect Answer: ${question.correct_answer || ''}\nExplanation: ${question.explanation || ''}`;
    
    navigator.clipboard.writeText(questionText);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
    
    toast({
      title: "Copied",
      description: "Question copied to clipboard"
    });
  };

  const questionTypeOptions = [
    { value: 'multiple_choice', label: 'Multiple Choice' },
    { value: 'true_false', label: 'True/False' },
    { value: 'short_answer', label: 'Short Answer' },
    { value: 'essay', label: 'Essay' },
    { value: 'matching', label: 'Matching' },
    { value: 'fill_blank', label: 'Fill in the Blank' }
  ];

  const difficultyOptions = [
    { value: 'easy', label: 'Easy', color: 'bg-green-100 text-green-800' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'hard', label: 'Hard', color: 'bg-red-100 text-red-800' }
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            AI Question Generator
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="topic">Topic</Label>
              <Input
                id="topic"
                placeholder="e.g., Python programming, World History, etc."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="difficulty">Difficulty Level</Label>
              <Select value={difficulty} onValueChange={setDifficulty}>
                <SelectTrigger id="difficulty">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {difficultyOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="questionType">Question Type</Label>
              <Select value={questionType} onValueChange={setQuestionType}>
                <SelectTrigger id="questionType">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {questionTypeOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="numberOfQuestions">Number of Questions</Label>
              <Input
                id="numberOfQuestions"
                type="number"
                min="1"
                max="20"
                value={numberOfQuestions}
                onChange={(e) => setNumberOfQuestions(parseInt(e.target.value) || 5)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="context">Additional Context (Optional)</Label>
            <Textarea
              id="context"
              placeholder="Provide any specific context, learning objectives, or requirements for the questions..."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              rows={3}
            />
          </div>

          <Button
            onClick={handleGenerateQuestions}
            disabled={loading || !topic}
            className="w-full"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Generating Questions...
              </>
            ) : (
              <>
                <Bot className="h-4 w-4 mr-2" />
                Generate Questions
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {generatedQuestions.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Generated Questions ({generatedQuestions.length})</CardTitle>
              <Button
                onClick={handleAddAllQuestions}
                size="sm"
                variant="primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add All Questions
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {generatedQuestions.map((question, index) => (
                <Card key={index} className="p-4">
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge 
                            variant="outline"
                            className={difficultyOptions.find(d => d.value === question.difficulty)?.color || ''}
                          >
                            {question.difficulty || difficulty}
                          </Badge>
                          <Badge variant="outline">
                            {questionTypeOptions.find(t => t.value === question.type)?.label || questionType}
                          </Badge>
                        </div>
                        <h4 className="font-medium text-gray-900">
                          {index + 1}. {question.question}
                        </h4>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyQuestion(question, index)}
                        >
                          {copiedIndex === index ? (
                            <Check className="h-4 w-4 text-green-600" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleAddQuestion(question)}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveQuestion(index)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    </div>

                    {question.options && question.options.length > 0 && (
                      <div className="ml-4 space-y-1">
                        <p className="text-sm text-gray-600">Options:</p>
                        <ol className="list-decimal list-inside text-sm text-gray-700 space-y-1">
                          {question.options.map((option, optIndex) => (
                            <li key={optIndex} className={option === question.correct_answer ? 'font-medium text-green-700' : ''}>
                              {option}
                              {option === question.correct_answer && (
                                <span className="ml-2 text-xs text-green-600">(Correct)</span>
                              )}
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {question.correct_answer && question.type !== 'multiple_choice' && (
                      <div className="ml-4">
                        <p className="text-sm text-gray-600">Correct Answer:</p>
                        <p className="text-sm font-medium text-green-700">{question.correct_answer}</p>
                      </div>
                    )}

                    {question.explanation && (
                      <div className="ml-4">
                        <p className="text-sm text-gray-600">Explanation:</p>
                        <p className="text-sm text-gray-700">{question.explanation}</p>
                      </div>
                    )}

                    {question.points && (
                      <div className="ml-4">
                        <p className="text-sm text-gray-600">
                          Points: <span className="font-medium">{question.points}</span>
                        </p>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIQuestionGenerator;