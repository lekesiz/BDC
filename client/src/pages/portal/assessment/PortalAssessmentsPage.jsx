import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Clock, 
  Calendar, 
  CheckCircle, 
  AlertCircle, 
  BookOpen,
  Award,
  BarChart,
  ExternalLink,
  Filter,
  Search,
  Loader
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
/**
 * PortalAssessmentsPage displays all available assessments for the student
 */
const PortalAssessmentsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [assessmentsData, setAssessmentsData] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  // Fetch assessments data
  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/assessments');
        setAssessmentsData(response.data);
      } catch (error) {
        console.error('Error fetching assessments:', error);
        toast({
          title: 'Error',
          description: 'Failed to load assessments',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchAssessments();
  }, [toast]);
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  // Format time duration
  const formatDuration = (minutes) => {
    if (!minutes) return 'No time limit';
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours} ${hours === 1 ? 'hour' : 'hours'}${mins ? ` ${mins} min` : ''}`;
  };
  // Get status badge
  const getStatusBadge = (status) => {
    switch (status) {
      case 'available':
        return (
          <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
            Available
          </span>
        );
      case 'completed':
        return (
          <span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
            Completed
          </span>
        );
      case 'upcoming':
        return (
          <span className="px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
            Upcoming
          </span>
        );
      case 'expired':
        return (
          <span className="px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
            Expired
          </span>
        );
      default:
        return (
          <span className="px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">
            {status}
          </span>
        );
    }
  };
  // Get type icon
  const getTypeIcon = (type, className = "h-5 w-5") => {
    switch (type) {
      case 'quiz':
        return <FileText className={className} />;
      case 'exam':
        return <FileText className={className} />;
      case 'project':
        return <BookOpen className={className} />;
      case 'evaluation':
        return <BarChart className={className} />;
      default:
        return <FileText className={className} />;
    }
  };
  // Get color class based on assessment type
  const getTypeColorClass = (type) => {
    switch (type) {
      case 'quiz':
        return 'bg-blue-50 text-blue-600';
      case 'exam':
        return 'bg-purple-50 text-purple-600';
      case 'project':
        return 'bg-green-50 text-green-600';
      case 'evaluation':
        return 'bg-orange-50 text-orange-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };
  // Filter assessments
  const getFilteredAssessments = () => {
    if (!assessmentsData) return [];
    let allAssessments = [];
    // Handle different data structures
    if (Array.isArray(assessmentsData)) {
      // Direct array
      allAssessments = [...assessmentsData];
    } else if (assessmentsData.assessments) {
      // Object with assessments property
      allAssessments = [...assessmentsData.assessments];
    } else {
      // Original structure
      allAssessments = [
        ...(assessmentsData.moduleAssessments || []),
        ...(assessmentsData.programAssessments || []),
        ...(assessmentsData.skillAssessments || [])
      ];
    }
    // Apply status filter
    if (filter !== 'all') {
      allAssessments = allAssessments.filter(assessment => assessment.status === filter);
    }
    // Apply search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      allAssessments = allAssessments.filter(assessment => 
        assessment.title.toLowerCase().includes(search) ||
        assessment.description.toLowerCase().includes(search) ||
        (assessment.moduleName && assessment.moduleName.toLowerCase().includes(search)) ||
        (assessment.skillName && assessment.skillName.toLowerCase().includes(search))
      );
    }
    return allAssessments;
  };
  // Start an assessment
  const handleStartAssessment = (assessment) => {
    navigate(`/portal/assessment/${assessment.id}`);
  };
  // View assessment results
  const handleViewResults = (assessment) => {
    navigate(`/portal/assessment/${assessment.id}/results`);
  };
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  const filteredAssessments = getFilteredAssessments();
  return (
    <div className="container mx-auto py-6">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Assessments</h1>
        <p className="text-gray-600">
          Complete quizzes, exams, and projects to test your knowledge and track your progress
        </p>
      </div>
      {/* Search and filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Input
            type="text"
            placeholder="Search assessments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
        <div className="flex space-x-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
          >
            All
          </Button>
          <Button
            variant={filter === 'available' ? 'default' : 'outline'}
            onClick={() => setFilter('available')}
          >
            Available
          </Button>
          <Button
            variant={filter === 'completed' ? 'default' : 'outline'}
            onClick={() => setFilter('completed')}
          >
            Completed
          </Button>
          <Button
            variant={filter === 'upcoming' ? 'default' : 'outline'}
            onClick={() => setFilter('upcoming')}
          >
            Upcoming
          </Button>
        </div>
      </div>
      {/* Assessment cards */}
      {filteredAssessments.length === 0 ? (
        <Card className="p-8 text-center">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No assessments found</h3>
          <p className="text-gray-500">
            {searchTerm || filter !== 'all' 
              ? 'Try adjusting your search or filter criteria' 
              : 'Check back later for new assessments'
            }
          </p>
        </Card>
      ) : (
        <div className="space-y-6">
          {filteredAssessments.map(assessment => (
            <Card key={assessment.id} className="overflow-hidden">
              <div className="p-6">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                  <div className="mb-4 md:mb-0">
                    <div className="flex items-center mb-2">
                      <div className={`p-2 rounded-full mr-3 ${getTypeColorClass(assessment.type)}`}>
                        {getTypeIcon(assessment.type)}
                      </div>
                      <div>
                        <h3 className="text-lg font-medium">{assessment.title}</h3>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                          {getStatusBadge(assessment.status)}
                          {assessment.moduleName && (
                            <span className="text-sm text-gray-500">
                              {assessment.moduleName}
                            </span>
                          )}
                          {assessment.skillName && (
                            <span className="text-sm text-gray-500">
                              {assessment.skillName} Skill
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <p className="text-gray-600 mb-4 pl-11">
                      {assessment.description}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pl-11">
                      <div className="flex items-center text-sm text-gray-500">
                        <Clock className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{formatDuration(assessment.duration)}</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <FileText className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{assessment.questionCount || 'N/A'} questions</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                        <span>
                          {assessment.status === 'completed' 
                            ? `Completed: ${formatDate(assessment.completedDate)}`
                            : assessment.dueDate
                            ? `Due: ${formatDate(assessment.dueDate)}`
                            : 'No due date'
                          }
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="pl-11 md:pl-0 shrink-0">
                    {assessment.status === 'completed' && assessment.attempts?.bestScore !== null && (
                      <div className="flex flex-col items-center mb-4">
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-1 ${
                          assessment.attempts.bestScore >= (assessment.passingScore || 0)
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                          <span className="text-xl font-bold">{assessment.attempts.bestScore}%</span>
                        </div>
                        <span className="text-xs text-gray-500">Best Score</span>
                      </div>
                    )}
                    {assessment.status === 'available' && (
                      <Button 
                        onClick={() => handleStartAssessment(assessment)}
                        className="w-full"
                      >
                        {assessment.attempts?.completed > 0 ? 'Attempt Again' : 'Start'}
                      </Button>
                    )}
                    {assessment.status === 'completed' && (
                      <Button 
                        variant="outline"
                        onClick={() => handleViewResults(assessment)}
                        className="w-full"
                      >
                        View Results
                      </Button>
                    )}
                    {assessment.status === 'upcoming' && (
                      <Button 
                        variant="outline"
                        disabled
                        className="w-full"
                      >
                        {assessment.availableDate 
                          ? `Available ${formatDate(assessment.availableDate)}`
                          : 'Coming Soon'
                        }
                      </Button>
                    )}
                  </div>
                </div>
                {assessment.attempts && (
                  <div className="mt-4 pl-11 text-sm text-gray-500">
                    {assessment.attempts.completed}/{assessment.attempts.allowed} attempts used
                    {assessment.attempts.completed > 0 && assessment.attempts.scores && (
                      <span className="ml-2">
                        • Past scores: {assessment.attempts.scores.join('%, ')}%
                      </span>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
export default PortalAssessmentsPage;