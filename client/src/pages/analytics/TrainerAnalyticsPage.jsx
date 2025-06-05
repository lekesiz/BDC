import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  BarChart as BarChartIcon, 
  UserCheck, 
  Calendar, 
  Clock, 
  ArrowLeft, 
  Download,
  ChevronDown,
  Search,
  Filter,
  User,
  Star,
  Loader
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
/**
 * TrainerAnalyticsPage displays performance metrics for trainers
 */
const TrainerAnalyticsPage = () => {
  const { id } = useParams(); // Optional trainer ID for specific trainer view
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [trainers, setTrainers] = useState([]);
  const [selectedTrainer, setSelectedTrainer] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState('last30days');
  const [trainerMetrics, setTrainerMetrics] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);
  // Fetch trainers and metrics
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Fetch trainers list
        const trainersResponse = await api.get('/api/users?role=trainer');
        setTrainers(trainersResponse.data);
        // If an ID is provided, fetch that specific trainer
        if (id) {
          const trainer = trainersResponse.data.find(t => t.id.toString() === id);
          if (trainer) {
            setSelectedTrainer(trainer);
          } else {
            toast({
              title: 'Error',
              description: 'Trainer not found',
              type: 'error',
            });
            navigate('/analytics/trainers');
          }
        }
        // Fetch trainer metrics if a trainer is selected
        if (selectedTrainer || id) {
          const trainerId = selectedTrainer?.id || id;
          const metricsResponse = await api.get(`/api/analytics/trainers/${trainerId}`, {
            params: {
              date_range: dateRange
            }
          });
          setTrainerMetrics(metricsResponse.data);
        }
      } catch (error) {
        console.error('Error fetching trainer data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load trainer data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [toast, id, selectedTrainer, dateRange, navigate]);
  // Handle date range change
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };
  // Filter trainers based on search term
  const filteredTrainers = trainers.filter(trainer => 
    trainer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trainer.email.toLowerCase().includes(searchTerm.toLowerCase())
  );
  // Format date range for display
  const formatDateRange = () => {
    switch(dateRange) {
      case 'last7days':
        return 'Last 7 Days';
      case 'last30days':
        return 'Last 30 Days';
      case 'last90days':
        return 'Last 90 Days';
      case 'thisYear':
        return 'This Year';
      case 'allTime':
        return 'All Time';
      default:
        return 'Last 30 Days';
    }
  };
  // Export trainer metrics
  const exportTrainerMetrics = async (format) => {
    if (!selectedTrainer && !id) return;
    try {
      const trainerId = selectedTrainer?.id || id;
      const response = await api.get(`/api/analytics/trainers/${trainerId}/export`, {
        params: {
          format,
          date_range: dateRange
        },
        responseType: 'blob'
      });
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `trainer_metrics_${trainerId}_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast({
        title: 'Success',
        description: `Trainer metrics exported successfully as ${format.toUpperCase()}`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error exporting trainer metrics:', error);
      toast({
        title: 'Error',
        description: `Failed to export trainer metrics as ${format.toUpperCase()}`,
        type: 'error',
      });
    }
  };
  // Render specific trainer analytics view
  const renderTrainerAnalytics = () => {
    if (!trainerMetrics) {
      return (
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">No metrics available for this trainer</p>
        </div>
      );
    }
    const { 
      performance, 
      beneficiaryMetrics, 
      sessionMetrics,
      evaluationMetrics,
      timeAllocation,
      skillsRating
    } = trainerMetrics;
    // Prepare session type data
    const sessionTypeData = sessionMetrics?.byType 
      ? Object.entries(sessionMetrics.byType).map(([name, value]) => ({
          name,
          value
        }))
      : [];
    // Prepare time allocation data
    const timeAllocationData = timeAllocation
      ? Object.entries(timeAllocation).map(([name, value]) => ({
          name,
          value
        }))
      : [];
    // Prepare skills rating data
    const skillsRatingData = skillsRating || [];
    return (
      <div className="space-y-6">
        {/* Trainer overview stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Beneficiaries</p>
                <h3 className="text-2xl font-bold mt-1">
                  {beneficiaryMetrics?.total || 0}
                </h3>
                <p className={`text-xs mt-1 ${beneficiaryMetrics?.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {beneficiaryMetrics?.growth !== undefined ? (
                    <span className="inline-flex items-center">
                      {beneficiaryMetrics.growth >= 0 ? '+' : ''}
                      {beneficiaryMetrics.growth}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-blue-50 rounded-full">
                <UserCheck className="w-5 h-5 text-blue-500" />
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Sessions</p>
                <h3 className="text-2xl font-bold mt-1">
                  {sessionMetrics?.total || 0}
                </h3>
                <p className={`text-xs mt-1 ${sessionMetrics?.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {sessionMetrics?.growth !== undefined ? (
                    <span className="inline-flex items-center">
                      {sessionMetrics.growth >= 0 ? '+' : ''}
                      {sessionMetrics.growth}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-green-50 rounded-full">
                <Calendar className="w-5 h-5 text-green-500" />
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Hours Delivered</p>
                <h3 className="text-2xl font-bold mt-1">
                  {sessionMetrics?.totalHours || 0}
                </h3>
                <p className={`text-xs mt-1 ${sessionMetrics?.hoursGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {sessionMetrics?.hoursGrowth !== undefined ? (
                    <span className="inline-flex items-center">
                      {sessionMetrics.hoursGrowth >= 0 ? '+' : ''}
                      {sessionMetrics.hoursGrowth}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-purple-50 rounded-full">
                <Clock className="w-5 h-5 text-purple-500" />
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Avg. Rating</p>
                <h3 className="text-2xl font-bold mt-1">
                  {performance?.avgRating?.toFixed(1) || 0}/5
                </h3>
                <p className={`text-xs mt-1 ${performance?.ratingGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {performance?.ratingGrowth !== undefined ? (
                    <span className="inline-flex items-center">
                      {performance.ratingGrowth >= 0 ? '+' : ''}
                      {performance.ratingGrowth}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-yellow-50 rounded-full">
                <Star className="w-5 h-5 text-yellow-500" />
              </div>
            </div>
          </Card>
        </div>
        {/* Performance metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Session Types</h2>
            <div className="h-64">
              {sessionTypeData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sessionTypeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {sessionTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No session type data available</p>
                </div>
              )}
            </div>
          </Card>
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Time Allocation</h2>
            <div className="h-64">
              {timeAllocationData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={timeAllocationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {timeAllocationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No time allocation data available</p>
                </div>
              )}
            </div>
          </Card>
        </div>
        {/* Skills rating */}
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Skills Rating</h2>
          <div className="h-80">
            {skillsRatingData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={skillsRatingData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 5]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="rating" name="Rating" fill="#4f46e5" />
                  <Bar dataKey="average" name="Trainer Average" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-500">
                <p>No skills rating data available</p>
              </div>
            )}
          </div>
        </Card>
        {/* Beneficiary outcomes */}
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Beneficiary Outcomes</h2>
          {beneficiaryMetrics?.outcomes ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Completion Rate</h3>
                <div className="text-3xl font-bold text-primary">
                  {beneficiaryMetrics.outcomes.completionRate}%
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  of beneficiaries completed their program
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Skill Improvement</h3>
                <div className="text-3xl font-bold text-green-600">
                  +{beneficiaryMetrics.outcomes.skillImprovement}%
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  average skill improvement
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Placement Rate</h3>
                <div className="text-3xl font-bold text-blue-600">
                  {beneficiaryMetrics.outcomes.placementRate}%
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  of graduates placed in jobs/internships
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-24 text-gray-500">
              <p>No beneficiary outcome data available</p>
            </div>
          )}
        </Card>
        {/* Evaluation metrics */}
        {evaluationMetrics && (
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Evaluation Insights</h2>
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="w-40 text-sm text-gray-500">Pass Rate</div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full" 
                      style={{ width: `${evaluationMetrics.passRate}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-right font-medium">{evaluationMetrics.passRate}%</div>
              </div>
              <div className="flex items-center">
                <div className="w-40 text-sm text-gray-500">Avg. Score</div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 rounded-full" 
                      style={{ width: `${evaluationMetrics.avgScore}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-right font-medium">{evaluationMetrics.avgScore}%</div>
              </div>
              <div className="flex items-center">
                <div className="w-40 text-sm text-gray-500">Improvement Rate</div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full" 
                      style={{ width: `${evaluationMetrics.improvementRate}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-right font-medium">{evaluationMetrics.improvementRate}%</div>
              </div>
              <div className="flex items-center">
                <div className="w-40 text-sm text-gray-500">Feedback Quality</div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500 rounded-full" 
                      style={{ width: `${(evaluationMetrics.feedbackQuality / 5) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-16 text-right font-medium">{evaluationMetrics.feedbackQuality}/5</div>
              </div>
            </div>
            {evaluationMetrics.insights && (
              <div className="mt-6 bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Key Insights</h3>
                <ul className="text-sm space-y-1 list-disc pl-4">
                  {evaluationMetrics.insights.map((insight, index) => (
                    <li key={index}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        )}
      </div>
    );
  };
  // Render trainers list
  const renderTrainersList = () => {
    return (
      <div>
        <div className="mb-6 flex items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <Input
              type="text"
              placeholder="Search trainers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trainer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Specialization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Beneficiaries
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rating
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredTrainers.length > 0 ? (
                  filteredTrainers.map((trainer) => (
                    <tr key={trainer.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-primary text-white flex items-center justify-center">
                              {trainer.name.charAt(0)}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{trainer.name}</div>
                            <div className="text-sm text-gray-500">{trainer.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {trainer.specialization || 'Not specified'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {trainer.beneficiaryCount || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm text-gray-900 mr-2">{trainer.rating || 0}/5</div>
                          <div className="flex">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                className={`w-4 h-4 ${i < Math.round(trainer.rating || 0) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} 
                              />
                            ))}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button 
                          variant="link" 
                          onClick={() => navigate(`/analytics/trainers/${trainer.id}`)}
                        >
                          View Analytics
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                      No trainers found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    );
  };
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          {(selectedTrainer || id) && (
            <button
              className="mr-4 p-2 rounded-full hover:bg-gray-100"
              onClick={() => {
                setSelectedTrainer(null);
                navigate('/analytics/trainers');
              }}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <div>
            <h1 className="text-2xl font-bold">
              {selectedTrainer || id 
                ? `Trainer Analytics: ${selectedTrainer?.name || trainers.find(t => t.id.toString() === id)?.name || 'Trainer'}`
                : 'Trainer Analytics'}
            </h1>
            {(selectedTrainer || id) && (
              <p className="text-gray-500">
                Viewing metrics for {formatDateRange()}
              </p>
            )}
          </div>
        </div>
        {(selectedTrainer || id) && (
          <div className="flex space-x-2">
            <div className="relative">
              <Button
                variant="outline"
                onClick={() => setFilterOpen(!filterOpen)}
                className="flex items-center"
              >
                <Filter className="w-4 h-4 mr-2" />
                Date Range
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
              {filterOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border p-4">
                  <div className="grid grid-cols-1 gap-2">
                    <Button
                      variant={dateRange === 'last7days' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        handleDateRangeChange('last7days');
                        setFilterOpen(false);
                      }}
                    >
                      Last 7 Days
                    </Button>
                    <Button
                      variant={dateRange === 'last30days' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        handleDateRangeChange('last30days');
                        setFilterOpen(false);
                      }}
                    >
                      Last 30 Days
                    </Button>
                    <Button
                      variant={dateRange === 'last90days' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        handleDateRangeChange('last90days');
                        setFilterOpen(false);
                      }}
                    >
                      Last 90 Days
                    </Button>
                    <Button
                      variant={dateRange === 'thisYear' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        handleDateRangeChange('thisYear');
                        setFilterOpen(false);
                      }}
                    >
                      This Year
                    </Button>
                    <Button
                      variant={dateRange === 'allTime' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        handleDateRangeChange('allTime');
                        setFilterOpen(false);
                      }}
                    >
                      All Time
                    </Button>
                  </div>
                </div>
              )}
            </div>
            <div className="relative">
              <Button
                variant="outline"
                onClick={() => {}}
                className="flex items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border p-2 hidden group-hover:block">
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportTrainerMetrics('pdf')}
                >
                  Export as PDF
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportTrainerMetrics('csv')}
                >
                  Export as CSV
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportTrainerMetrics('xlsx')}
                >
                  Export as Excel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <Loader className="w-10 h-10 text-primary animate-spin" />
        </div>
      ) : (
        <>
          {selectedTrainer || id ? renderTrainerAnalytics() : renderTrainersList()}
        </>
      )}
    </div>
  );
};
export default TrainerAnalyticsPage;