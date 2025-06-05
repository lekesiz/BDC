import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Clock, FileText, CheckCircle, 
  AlertCircle, ChevronLeft, ChevronRight, Eye
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { RadioGroup } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
/**
 * TrainerAssessmentPreviewPage allows trainers to preview assessments as students would see them
 */
const TrainerAssessmentPreviewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // Template data
  const [template, setTemplate] = useState(null);
  // Preview state
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [showFinishDialog, setShowFinishDialog] = useState(false);
  // Project submission state
  const [projectFiles, setProjectFiles] = useState([]);
  const [projectUrl, setProjectUrl] = useState('');
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [notes, setNotes] = useState('');
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
        setTemplate(templateData);
        // Initialize timer if quiz has time limit
        if (templateData.type === 'quiz' && templateData.settings?.timeLimit) {
          setTimeRemaining(templateData.settings.timeLimit * 60); // Convert to seconds
          setIsTimerActive(true);
        }
      } catch (err) {
        if (!isMounted) return;
        console.error('Error fetching template:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load assessment preview',
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
  }, [id, toast]);
  // Timer effect
  useEffect(() => {
    if (!isTimerActive || !timeRemaining) return;
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          setIsTimerActive(false);
          handleFinishAssessment();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [isTimerActive, timeRemaining]);
  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  // Handle answer change
  const handleAnswerChange = (value) => {
    setAnswers({
      ...answers,
      [currentQuestion]: value
    });
  };
  // Navigate between questions
  const goToQuestion = (index) => {
    if (index >= 0 && index < template.questions.length) {
      setCurrentQuestion(index);
    }
  };
  // Calculate progress
  const calculateProgress = () => {
    if (template?.type === 'quiz') {
      const answeredCount = Object.keys(answers).length;
      return Math.round((answeredCount / template.questions.length) * 100);
    }
    return 0;
  };
  // Handle assessment completion
  const handleFinishAssessment = () => {
    setShowFinishDialog(false);
    setShowResults(true);
    // In a real app, this would submit the assessment
    toast({
      title: 'Preview Mode',
      description: 'Assessment preview completed. This is preview mode only.',
      type: 'info',
    });
  };
  // Calculate score (for preview only)
  const calculateScore = () => {
    let correct = 0;
    let total = 0;
    template.questions.forEach((question, index) => {
      const answer = answers[index];
      total += question.points || 10;
      if (question.type === 'multipleChoice' && answer === question.correctAnswer) {
        correct += question.points || 10;
      } else if (question.type === 'trueFalse' && answer === question.correctAnswer) {
        correct += question.points || 10;
      }
    });
    return {
      correct,
      total,
      percentage: Math.round((correct / total) * 100)
    };
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
            onClick={() => navigate(`/assessment/templates/${id}`)}
            className="flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Template
          </Button>
        </div>
        <Card className="p-6 text-center">
          <div className="text-red-500 mb-4">
            <AlertCircle className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Unable to Load Preview</h2>
          <p className="text-gray-600 mb-4">
            {error || "The assessment template could not be loaded."}
          </p>
          <Button onClick={() => navigate(`/assessment/templates/${id}`)}>
            Back to Template
          </Button>
        </Card>
      </div>
    );
  }
  const isQuiz = template.type === 'quiz';
  // Render results view
  if (showResults) {
    const score = isQuiz ? calculateScore() : null;
    return (
      <div className="container mx-auto py-6">
        <div className="max-w-3xl mx-auto">
          <Card className="p-8">
            <div className="text-center mb-8">
              <div className="mb-4">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Preview Completed</h2>
              <p className="text-gray-600">
                This is how students will see their results
              </p>
            </div>
            {isQuiz && score && (
              <div className="mb-8">
                <div className="text-center mb-6">
                  <div className="text-4xl font-bold text-primary mb-2">
                    {score.percentage}%
                  </div>
                  <p className="text-gray-600">
                    {score.correct} out of {score.total} points
                  </p>
                </div>
                <Progress value={score.percentage} className="h-4 mb-6" />
                <div className="flex justify-center gap-4 mb-6">
                  <Badge className={score.percentage >= 70 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                    {score.percentage >= 70 ? 'Passed' : 'Failed'}
                  </Badge>
                  <Badge>Passing Score: {template.settings?.passingScore || 70}%</Badge>
                </div>
              </div>
            )}
            <div className="flex justify-center gap-4">
              <Button
                variant="outline"
                onClick={() => navigate(`/assessment/templates/${id}`)}
              >
                Back to Template
              </Button>
              <Button
                onClick={() => {
                  setShowResults(false);
                  setCurrentQuestion(0);
                  setAnswers({});
                }}
              >
                Preview Again
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <Button
                variant="ghost"
                onClick={() => navigate(`/assessment/templates/${id}`)}
                className="mr-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Exit Preview
              </Button>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-semibold">{template.title}</h1>
                  <Badge className="bg-amber-100 text-amber-800">
                    <Eye className="w-3 h-3 mr-1" />
                    Preview Mode
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">
                  {isQuiz ? `${template.questions?.length || 0} questions` : 'Project Assessment'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {isQuiz && timeRemaining && (
                <div className="flex items-center text-amber-600">
                  <Clock className="w-5 h-5 mr-2" />
                  <span className="font-mono font-medium">{formatTime(timeRemaining)}</span>
                </div>
              )}
              <Button
                onClick={() => setShowFinishDialog(true)}
                className="bg-primary"
              >
                Finish Preview
              </Button>
            </div>
          </div>
        </div>
      </div>
      {/* Progress bar */}
      {isQuiz && (
        <div className="bg-white border-b">
          <div className="container mx-auto">
            <Progress value={calculateProgress()} className="h-2" />
          </div>
        </div>
      )}
      {/* Main content */}
      <div className="container mx-auto py-8">
        <div className="max-w-3xl mx-auto">
          {isQuiz ? (
            <div>
              {/* Question card */}
              <Card className="p-6 mb-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Question {currentQuestion + 1} of {template.questions.length}
                    </h3>
                    <Badge>{template.questions[currentQuestion].type}</Badge>
                  </div>
                  <div className="text-sm text-gray-600">
                    {template.questions[currentQuestion].points || 10} points
                  </div>
                </div>
                <div className="mb-6">
                  <p className="text-lg">{template.questions[currentQuestion].question}</p>
                </div>
                {/* Answer area based on question type */}
                {template.questions[currentQuestion].type === 'multipleChoice' && (
                  <RadioGroup
                    value={answers[currentQuestion] || ''}
                    onValueChange={handleAnswerChange}
                  >
                    {template.questions[currentQuestion].options.map((option, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-3">
                        <RadioGroup.Item value={index} id={`option-${index}`} />
                        <Label htmlFor={`option-${index}`} className="cursor-pointer flex-1">
                          {option}
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                )}
                {template.questions[currentQuestion].type === 'trueFalse' && (
                  <RadioGroup
                    value={String(answers[currentQuestion] || '')}
                    onValueChange={(value) => handleAnswerChange(value === 'true')}
                  >
                    <div className="flex items-center space-x-2 mb-3">
                      <RadioGroup.Item value="true" id="true" />
                      <Label htmlFor="true" className="cursor-pointer">True</Label>
                    </div>
                    <div className="flex items-center space-x-2 mb-3">
                      <RadioGroup.Item value="false" id="false" />
                      <Label htmlFor="false" className="cursor-pointer">False</Label>
                    </div>
                  </RadioGroup>
                )}
                {template.questions[currentQuestion].type === 'shortAnswer' && (
                  <Textarea
                    value={answers[currentQuestion] || ''}
                    onChange={(e) => handleAnswerChange(e.target.value)}
                    placeholder="Enter your answer"
                    rows={3}
                  />
                )}
                {/* Navigation */}
                <div className="flex justify-between items-center mt-6">
                  <Button
                    variant="outline"
                    onClick={() => goToQuestion(currentQuestion - 1)}
                    disabled={currentQuestion === 0}
                  >
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>
                  <div className="flex gap-2">
                    {template.questions.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => goToQuestion(index)}
                        className={`w-10 h-10 rounded-lg border transition-colors ${
                          index === currentQuestion
                            ? 'bg-primary text-white border-primary'
                            : answers[index] !== undefined
                            ? 'bg-green-100 text-green-800 border-green-300'
                            : 'bg-white hover:bg-gray-50 border-gray-300'
                        }`}
                      >
                        {index + 1}
                      </button>
                    ))}
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => goToQuestion(currentQuestion + 1)}
                    disabled={currentQuestion === template.questions.length - 1}
                  >
                    Next
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            // Project assessment preview
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-6">Project Submission Preview</h2>
              <div className="space-y-6">
                {/* Requirements */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">Requirements</h3>
                  <div className="space-y-2">
                    {template.requirements?.map((requirement, index) => (
                      <div key={index} className="flex items-start">
                        <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium mr-3 flex-shrink-0 mt-0.5">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p>{requirement.description}</p>
                          <p className="text-sm text-gray-500">{requirement.points} points</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Submission form preview */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold mb-3">Submission</h3>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="projectUrl">Project URL</Label>
                      <Input
                        id="projectUrl"
                        value={projectUrl}
                        onChange={(e) => setProjectUrl(e.target.value)}
                        placeholder="https://your-project.com"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="repositoryUrl">Repository URL (optional)</Label>
                      <Input
                        id="repositoryUrl"
                        value={repositoryUrl}
                        onChange={(e) => setRepositoryUrl(e.target.value)}
                        placeholder="https://github.com/username/repo"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="notes">Additional Notes</Label>
                      <Textarea
                        id="notes"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Any additional information about your submission"
                        rows={4}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label>File Upload</Label>
                      <div className="mt-1 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600">Drag and drop files here or click to upload</p>
                        <p className="text-sm text-gray-500 mt-1">Max file size: 10MB</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
      {/* Finish Dialog */}
      <Dialog open={showFinishDialog} onOpenChange={setShowFinishDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Finish Preview</DialogTitle>
            <DialogDescription>
              Are you ready to finish the assessment preview? In the actual assessment,
              students would submit their answers at this point.
            </DialogDescription>
          </DialogHeader>
          {isQuiz && (
            <div className="py-4">
              <p className="text-sm text-gray-600">
                Questions answered: {Object.keys(answers).length} of {template.questions.length}
              </p>
              <Progress 
                value={calculateProgress()} 
                className="h-2 mt-2"
              />
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowFinishDialog(false)}>
              Continue Assessment
            </Button>
            <Button onClick={handleFinishAssessment}>
              Finish Preview
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
export default TrainerAssessmentPreviewPage;