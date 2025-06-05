import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Textarea } from '../../components/ui/textarea';
import { Input } from '../../components/ui/input';
import {
  Loader2,
  ArrowLeft,
  Save,
  CheckCircle,
  Clock,
  FileText,
  Award,
  MessageSquare
} from 'lucide-react';
const EssayGradingPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [session, setSession] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [currentSubmission, setCurrentSubmission] = useState(0);
  const [feedback, setFeedback] = useState({});
  const [scores, setScores] = useState({});
  useEffect(() => {
    fetchSessionData();
    fetchSubmissions();
  }, [sessionId]);
  const fetchSessionData = async () => {
    try {
      const res = await fetch(`/api/tests/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch session');
      const data = await res.json();
      setSession(data);
    } catch (error) {
      console.error('Error fetching session:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch test session',
        variant: 'destructive'
      });
    }
  };
  const fetchSubmissions = async () => {
    try {
      const res = await fetch(`/api/tests/sessions/${sessionId}/essay-submissions`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch submissions');
      const data = await res.json();
      setSubmissions(data);
      // Initialize feedback and scores
      const initialFeedback = {};
      const initialScores = {};
      data.forEach(submission => {
        initialFeedback[submission.id] = submission.feedback || '';
        initialScores[submission.id] = submission.score || 0;
      });
      setFeedback(initialFeedback);
      setScores(initialScores);
    } catch (error) {
      console.error('Error fetching submissions:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch essay submissions',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleSaveGrade = async (submissionId) => {
    setSaving(true);
    try {
      const res = await fetch(`/api/tests/submissions/${submissionId}/grade`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          score: scores[submissionId],
          feedback: feedback[submissionId]
        })
      });
      if (!res.ok) throw new Error('Failed to save grade');
      toast({
        title: 'Success',
        description: 'Grade saved successfully'
      });
      // Update submission status
      const updatedSubmissions = submissions.map(sub => 
        sub.id === submissionId 
          ? { ...sub, graded: true, score: scores[submissionId], feedback: feedback[submissionId] }
          : sub
      );
      setSubmissions(updatedSubmissions);
    } catch (error) {
      console.error('Error saving grade:', error);
      toast({
        title: 'Error',
        description: 'Failed to save grade',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };
  const handleNext = () => {
    if (currentSubmission < submissions.length - 1) {
      setCurrentSubmission(currentSubmission + 1);
    }
  };
  const handlePrevious = () => {
    if (currentSubmission > 0) {
      setCurrentSubmission(currentSubmission - 1);
    }
  };
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  if (submissions.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No essay submissions to grade</p>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    );
  }
  const currentSub = submissions[currentSubmission];
  const gradedCount = submissions.filter(s => s.graded).length;
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold text-gray-900">Essay Grading</h1>
          <Badge variant="outline">
            {gradedCount} of {submissions.length} graded
          </Badge>
        </div>
      </div>
      {/* Progress Bar */}
      <div className="bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary h-2 rounded-full transition-all"
          style={{ width: `${(gradedCount / submissions.length) * 100}%` }}
        />
      </div>
      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Essay Content */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                Submission {currentSubmission + 1} of {submissions.length}
              </h2>
              {currentSub.graded && (
                <Badge variant="success">
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Graded
                </Badge>
              )}
            </div>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Student Information</h3>
                <p className="text-sm text-gray-600">
                  Name: {currentSub.student_name}
                </p>
                <p className="text-sm text-gray-600">
                  Email: {currentSub.student_email}
                </p>
                <p className="text-sm text-gray-600">
                  Submitted: {new Date(currentSub.submitted_at).toLocaleString()}
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Essay Question</h3>
                <p className="text-gray-700 bg-gray-50 p-3 rounded">
                  {currentSub.question}
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Student Answer</h3>
                <div className="bg-gray-50 p-4 rounded whitespace-pre-wrap">
                  {currentSub.answer}
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">
                  Word count: {currentSub.answer.split(/\s+/).length} words
                </p>
              </div>
            </div>
          </Card>
        </div>
        {/* Grading Panel */}
        <div>
          <Card className="p-6 sticky top-6">
            <h2 className="text-lg font-semibold mb-4">Grading</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Score ({currentSub.max_score} points max)
                </label>
                <Input
                  type="number"
                  value={scores[currentSub.id] || 0}
                  onChange={(e) => setScores({
                    ...scores,
                    [currentSub.id]: Math.min(parseInt(e.target.value) || 0, currentSub.max_score)
                  })}
                  min="0"
                  max={currentSub.max_score}
                  className="w-32"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Feedback
                </label>
                <Textarea
                  value={feedback[currentSub.id] || ''}
                  onChange={(e) => setFeedback({
                    ...feedback,
                    [currentSub.id]: e.target.value
                  })}
                  rows={6}
                  placeholder="Provide feedback for the student..."
                />
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Grading Rubric</h3>
                <div className="text-sm text-gray-600 space-y-1 bg-gray-50 p-3 rounded">
                  <p>• Content accuracy and relevance</p>
                  <p>• Writing clarity and structure</p>
                  <p>• Critical thinking demonstrated</p>
                  <p>• Use of examples and evidence</p>
                  <p>• Grammar and spelling</p>
                </div>
              </div>
              <Button
                onClick={() => handleSaveGrade(currentSub.id)}
                disabled={saving}
                className="w-full"
              >
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Grade
                  </>
                )}
              </Button>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={currentSubmission === 0}
                  className="flex-1"
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={handleNext}
                  disabled={currentSubmission === submissions.length - 1}
                  className="flex-1"
                >
                  Next
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
export default EssayGradingPage;