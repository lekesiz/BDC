import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Switch } from '../../components/ui/switch';
import { Textarea } from '../../components/ui/textarea';
import {
  Loader2,
  MessageSquare,
  Bot,
  CheckCircle,
  XCircle,
  Clock,
  User,
  Settings,
  RefreshCw,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  Edit
} from 'lucide-react';

const AIAutomatedFeedbackPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [feedbacks, setFeedbacks] = useState([]);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [editingFeedback, setEditingFeedback] = useState(null);
  const [feedbackSettings, setFeedbackSettings] = useState({
    auto_generate: true,
    auto_approve_threshold: 0.8,
    include_suggestions: true,
    tone: 'professional',
    max_length: 500
  });
  const [showSettings, setShowSettings] = useState(false);
  const [filter, setFilter] = useState('pending');

  useEffect(() => {
    fetchFeedbacks();
    fetchSettings();
  }, [filter]);

  const fetchFeedbacks = async () => {
    try {
      const res = await fetch(`/api/ai/automated-feedback?status=${filter}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch feedbacks');

      const data = await res.json();
      setFeedbacks(data);
    } catch (error) {
      console.error('Error fetching feedbacks:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch automated feedbacks',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/ai/feedback-settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch settings');

      const data = await res.json();
      setFeedbackSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleSaveSettings = async () => {
    try {
      const res = await fetch('/api/ai/feedback-settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(feedbackSettings)
      });

      if (!res.ok) throw new Error('Failed to save settings');

      toast({
        title: 'Success',
        description: 'Feedback settings saved successfully'
      });
      setShowSettings(false);
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save settings',
        variant: 'destructive'
      });
    }
  };

  const handleApproveFeedback = async (feedbackId) => {
    try {
      const feedbackToApprove = editingFeedback || feedbacks.find(f => f.id === feedbackId);
      
      const res = await fetch(`/api/ai/automated-feedback/${feedbackId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          content: feedbackToApprove.content
        })
      });

      if (!res.ok) throw new Error('Failed to approve feedback');

      toast({
        title: 'Success',
        description: 'Feedback approved and sent'
      });

      setEditingFeedback(null);
      fetchFeedbacks();
    } catch (error) {
      console.error('Error approving feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to approve feedback',
        variant: 'destructive'
      });
    }
  };

  const handleRejectFeedback = async (feedbackId) => {
    if (!confirm('Are you sure you want to reject this feedback?')) return;

    try {
      const res = await fetch(`/api/ai/automated-feedback/${feedbackId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to reject feedback');

      toast({
        title: 'Success',
        description: 'Feedback rejected'
      });

      fetchFeedbacks();
    } catch (error) {
      console.error('Error rejecting feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to reject feedback',
        variant: 'destructive'
      });
    }
  };

  const handleRegenerateFeedback = async (feedbackId) => {
    try {
      const res = await fetch(`/api/ai/automated-feedback/${feedbackId}/regenerate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to regenerate feedback');

      const data = await res.json();
      
      // Update the feedback in the list
      setFeedbacks(feedbacks.map(f => f.id === feedbackId ? data : f));
      setSelectedFeedback(data);

      toast({
        title: 'Success',
        description: 'Feedback regenerated successfully'
      });
    } catch (error) {
      console.error('Error regenerating feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to regenerate feedback',
        variant: 'destructive'
      });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'edited':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">AI Automated Feedback</h1>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Feedback Generation Settings</h2>
          <div className="space-y-4">
            <label className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto-generate feedback</p>
                <p className="text-sm text-gray-600">
                  Automatically generate feedback for test submissions
                </p>
              </div>
              <Switch
                checked={feedbackSettings.auto_generate}
                onCheckedChange={(checked) => 
                  setFeedbackSettings({ ...feedbackSettings, auto_generate: checked })
                }
              />
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Auto-approval threshold
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={feedbackSettings.auto_approve_threshold}
                onChange={(e) => 
                  setFeedbackSettings({ 
                    ...feedbackSettings, 
                    auto_approve_threshold: parseFloat(e.target.value) 
                  })
                }
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-600">
                <span>0%</span>
                <span>Current: {(feedbackSettings.auto_approve_threshold * 100).toFixed(0)}%</span>
                <span>100%</span>
              </div>
            </div>

            <label className="flex items-center justify-between">
              <div>
                <p className="font-medium">Include improvement suggestions</p>
                <p className="text-sm text-gray-600">
                  Add personalized suggestions in feedback
                </p>
              </div>
              <Switch
                checked={feedbackSettings.include_suggestions}
                onCheckedChange={(checked) => 
                  setFeedbackSettings({ ...feedbackSettings, include_suggestions: checked })
                }
              />
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Feedback tone
              </label>
              <select
                value={feedbackSettings.tone}
                onChange={(e) => 
                  setFeedbackSettings({ ...feedbackSettings, tone: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="professional">Professional</option>
                <option value="encouraging">Encouraging</option>
                <option value="constructive">Constructive</option>
                <option value="friendly">Friendly</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maximum length (words)
              </label>
              <input
                type="number"
                value={feedbackSettings.max_length}
                onChange={(e) => 
                  setFeedbackSettings({ ...feedbackSettings, max_length: parseInt(e.target.value) })
                }
                min="100"
                max="1000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>

            <div className="flex justify-end">
              <Button onClick={handleSaveSettings}>
                Save Settings
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {['pending', 'approved', 'rejected', 'all'].map((status) => (
          <Button
            key={status}
            variant={filter === status ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(status)}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Button>
        ))}
      </div>

      {/* Feedback List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Feedback Queue</h2>
          
          {feedbacks.length === 0 ? (
            <div className="text-center py-8">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No feedbacks to review</p>
            </div>
          ) : (
            <div className="space-y-4">
              {feedbacks.map((feedback) => (
                <div
                  key={feedback.id}
                  className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow ${
                    selectedFeedback?.id === feedback.id ? 'border-primary' : ''
                  }`}
                  onClick={() => {
                    setSelectedFeedback(feedback);
                    setEditingFeedback(null);
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {feedback.beneficiary_name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {feedback.test_title}
                      </p>
                    </div>
                    <Badge className={getStatusColor(feedback.status)}>
                      {feedback.status}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{new Date(feedback.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Bot className="h-4 w-4" />
                      <span className={getConfidenceColor(feedback.confidence_score)}>
                        {(feedback.confidence_score * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>

                  {feedback.status === 'pending' && (
                    <div className="flex gap-2 mt-3">
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleApproveFeedback(feedback.id);
                        }}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRejectFeedback(feedback.id);
                        }}
                      >
                        <XCircle className="h-4 w-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Selected Feedback Details */}
        {selectedFeedback && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Feedback Details</h2>
              <div className="flex gap-2">
                {selectedFeedback.status === 'pending' && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditingFeedback({ ...selectedFeedback })}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRegenerateFeedback(selectedFeedback.id)}
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700">Student</p>
                <p className="text-gray-900">{selectedFeedback.beneficiary_name}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700">Test</p>
                <p className="text-gray-900">{selectedFeedback.test_title}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700">Score</p>
                <p className="text-gray-900">{selectedFeedback.score}%</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Generated Feedback</p>
                {editingFeedback ? (
                  <Textarea
                    value={editingFeedback.content}
                    onChange={(e) => 
                      setEditingFeedback({ ...editingFeedback, content: e.target.value })
                    }
                    rows={10}
                    className="w-full"
                  />
                ) : (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="whitespace-pre-wrap">{selectedFeedback.content}</p>
                  </div>
                )}
              </div>

              {selectedFeedback.suggestions && selectedFeedback.suggestions.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Improvement Suggestions</p>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedFeedback.suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-gray-600">
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">AI Analysis</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Confidence Score:</span>
                    <span className={getConfidenceColor(selectedFeedback.confidence_score)}>
                      {(selectedFeedback.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Sentiment:</span>
                    <Badge variant="secondary">{selectedFeedback.sentiment}</Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Areas Covered:</span>
                    <span>{selectedFeedback.areas_covered?.length || 0}</span>
                  </div>
                </div>
              </div>

              {editingFeedback && (
                <div className="flex gap-2 pt-4">
                  <Button
                    onClick={() => handleApproveFeedback(selectedFeedback.id)}
                  >
                    Save & Approve
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setEditingFeedback(null)}
                  >
                    Cancel
                  </Button>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AIAutomatedFeedbackPage;