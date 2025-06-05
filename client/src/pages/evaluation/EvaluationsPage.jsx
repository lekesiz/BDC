import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter, FilePlus, Clock, Activity, Edit, Eye, Trash2 } from 'lucide-react';
import api from '@/lib/api';
import { API_ENDPOINTS, EVALUATION_STATUS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
/**
 * EvaluationsPage displays a list of all evaluations/tests
 */
const EvaluationsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [evaluations, setEvaluations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: 'all',
    search: '',
  });
  // Fetch evaluations from the API
  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        setIsLoading(true);
        const response = await api.get(API_ENDPOINTS.EVALUATIONS.BASE);
        setEvaluations(response.data.items || []);
      } catch (error) {
        console.error('Error fetching evaluations:', error);
        toast({
          title: 'Error',
          description: 'Failed to load evaluations',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchEvaluations();
  }, []); // Remove toast dependency to prevent infinite loop
  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };
  // Filter evaluations based on current filters
  const filteredEvaluations = (evaluations || []).filter(evaluation => {
    // Status filter
    if (filters.status !== 'all' && evaluation.status !== filters.status) {
      return false;
    }
    // Search filter
    if (filters.search && !evaluation.title.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    return true;
  });
  // Delete an evaluation
  const handleDelete = async (id) => {
    if (confirm('Are you sure you want to delete this evaluation? This action cannot be undone.')) {
      try {
        await api.delete(API_ENDPOINTS.EVALUATIONS.DETAIL(id));
        setEvaluations(prev => prev.filter(evaluation => evaluation.id !== id));
        toast({
          title: 'Success',
          description: 'Evaluation deleted successfully',
          type: 'success',
        });
      } catch (error) {
        console.error('Error deleting evaluation:', error);
        toast({
          title: 'Error',
          description: 'Failed to delete evaluation',
          type: 'error',
        });
      }
    }
  };
  // Get the label and color for a status
  const getStatusLabel = (status) => {
    switch (status) {
      case EVALUATION_STATUS.DRAFT:
        return { label: 'Draft', color: 'bg-gray-100 text-gray-800' };
      case EVALUATION_STATUS.ACTIVE:
        return { label: 'Active', color: 'bg-green-100 text-green-800' };
      case EVALUATION_STATUS.ARCHIVED:
        return { label: 'Archived', color: 'bg-amber-100 text-amber-800' };
      default:
        return { label: 'Unknown', color: 'bg-gray-100 text-gray-800' };
    }
  };
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Evaluations & Tests</h1>
        <Button
          onClick={() => navigate('/evaluations/create')}
          className="flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Test
        </Button>
      </div>
      <Card className="p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <Input
              type="text"
              placeholder="Search evaluations..."
              className="pl-10"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium">Status:</span>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
            >
              <option value="all">All</option>
              <option value={EVALUATION_STATUS.DRAFT}>Draft</option>
              <option value={EVALUATION_STATUS.ACTIVE}>Active</option>
              <option value={EVALUATION_STATUS.ARCHIVED}>Archived</option>
            </select>
          </div>
        </div>
      </Card>
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
        </div>
      ) : filteredEvaluations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(filteredEvaluations || []).map((evaluation) => {
            const { label, color } = getStatusLabel(evaluation.status);
            return (
              <Card key={evaluation.id} className="overflow-hidden flex flex-col">
                <div className="p-5 flex-1">
                  <div className="flex justify-between items-start mb-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>
                      {label}
                    </span>
                    <div className="flex items-center text-xs text-gray-500">
                      <Clock className="w-3 h-3 mr-1" />
                      <span>{evaluation.time_limit ? `${evaluation.time_limit} min` : 'No time limit'}</span>
                    </div>
                  </div>
                  <h2 className="text-lg font-semibold mb-2 line-clamp-2">{evaluation.title}</h2>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-3">{evaluation.description}</p>
                  <div className="flex items-center space-x-4 text-sm mb-4">
                    <div className="flex items-center text-gray-600">
                      <FilePlus className="w-3 h-3 mr-1" />
                      <span>{evaluation.questions?.length || 0} Questions</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Activity className="w-3 h-3 mr-1" />
                      <span>{evaluation.passing_score || 0}% to Pass</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {evaluation.skills?.map((skill, index) => (
                      <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 border-t border-gray-100 flex justify-between">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/evaluations/${evaluation.id}`)}
                    className="text-gray-700"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    View
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/evaluations/${evaluation.id}/edit`)}
                    className="text-blue-600"
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(evaluation.id)}
                    className="text-red-600"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card className="p-8 text-center">
          <div className="mb-4 flex justify-center">
            <FilePlus className="h-12 w-12 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">No evaluations found</h3>
          <p className="text-gray-500 mb-4">
            {filters.search || filters.status !== 'all'
              ? 'Try adjusting your filters or search term'
              : 'Get started by creating your first evaluation'}
          </p>
          <Button
            onClick={() => navigate('/evaluations/create')}
            className="flex items-center mx-auto"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create New Test
          </Button>
        </Card>
      )}
    </div>
  );
};
export default EvaluationsPage;