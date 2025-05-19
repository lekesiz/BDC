import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClipboardList, Clock, CheckCircle, AlertCircle, Play } from 'lucide-react';
import api from '@/lib/api';
import { API_ENDPOINTS, EVALUATION_STATUS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import { formatDate } from '@/lib/utils';

/**
 * MyEvaluationsPage displays evaluations for student users
 */
const MyEvaluationsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [evaluations, setEvaluations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch student's evaluations
  useEffect(() => {
    const fetchMyEvaluations = async () => {
      try {
        setIsLoading(true);
        // For students, the API will automatically filter by their beneficiary profile
        const response = await api.get(API_ENDPOINTS.EVALUATIONS.BASE);
        setEvaluations(response.data.items || []);
      } catch (error) {
        console.error('Error fetching evaluations:', error);
        toast({
          title: 'Error',
          description: 'Failed to load your evaluations',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchMyEvaluations();
  }, [toast]);

  // Start an evaluation
  const handleStartEvaluation = (evaluationId) => {
    navigate(`/evaluations/sessions/new?evaluation_id=${evaluationId}`);
  };

  // View results
  const handleViewResults = (sessionId) => {
    navigate(`/evaluations/sessions/${sessionId}/results`);
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4" />;
      case 'in_progress':
        return <AlertCircle className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <ClipboardList className="h-4 w-4" />;
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'in_progress':
        return 'warning';
      case 'completed':
        return 'success';
      default:
        return 'secondary';
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Evaluations</h1>
        <p className="text-gray-600 mt-1">View and take your assigned evaluations</p>
      </div>

      {evaluations.length === 0 ? (
        <Card className="p-8 text-center">
          <ClipboardList className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Evaluations Assigned</h3>
          <p className="text-gray-500">You don't have any evaluations assigned to you yet.</p>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {evaluations.map((evaluation) => (
            <Card key={evaluation.id} className="hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {evaluation.title}
                  </h3>
                  <Badge color={getStatusColor(evaluation.status || 'pending')}>
                    <span className="flex items-center gap-1">
                      {getStatusIcon(evaluation.status || 'pending')}
                      {evaluation.status || 'Pending'}
                    </span>
                  </Badge>
                </div>

                <p className="text-gray-600 text-sm mb-4">
                  {evaluation.description}
                </p>

                <div className="space-y-2 text-sm text-gray-500">
                  {evaluation.time_limit && (
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      <span>Time limit: {evaluation.time_limit} minutes</span>
                    </div>
                  )}
                  {evaluation.passing_score && (
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      <span>Passing score: {evaluation.passing_score}%</span>
                    </div>
                  )}
                  {evaluation.due_date && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>Due: {formatDate(evaluation.due_date)}</span>
                    </div>
                  )}
                </div>

                <div className="mt-6">
                  {evaluation.status === 'completed' && evaluation.latest_session_id ? (
                    <Button
                      onClick={() => handleViewResults(evaluation.latest_session_id)}
                      className="w-full"
                      variant="outline"
                    >
                      View Results
                    </Button>
                  ) : evaluation.status === 'in_progress' ? (
                    <Button
                      onClick={() => handleStartEvaluation(evaluation.id)}
                      className="w-full"
                      variant="secondary"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Continue
                    </Button>
                  ) : (
                    <Button
                      onClick={() => handleStartEvaluation(evaluation.id)}
                      className="w-full"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Start Evaluation
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyEvaluationsPage;