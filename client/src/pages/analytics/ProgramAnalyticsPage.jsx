import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  BarChartIcon, 
  Users, 
  Briefcase, 
  Calendar, 
  Clock, 
  Award,
  ArrowLeft, 
  Download,
  ChevronDown,
  Search,
  Filter,
  Bookmark,
  TrendingUp,
  Star,
  Loader
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, AreaChart, Area } from 'recharts';

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

/**
 * ProgramAnalyticsPage displays detailed analytics for training programs
 */
const ProgramAnalyticsPage = () => {
  const { id } = useParams(); // Optional program ID for specific program view
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [programs, setPrograms] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState('last30days');
  const [programMetrics, setProgramMetrics] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);
  
  // Fetch programs and metrics
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch programs list
        const programsResponse = await api.get('/api/programs');
        setPrograms(programsResponse.data);
        
        // If an ID is provided, fetch that specific program
        if (id) {
          const program = programsResponse.data?.find(p => p.id.toString() === id);
          if (program) {
            setSelectedProgram(program);
          } else {
            toast({
              title: 'Error',
              description: 'Program not found',
              type: 'error',
            });
            navigate('/analytics/programs');
          }
        }
        
        // Fetch program metrics if a program is selected
        if (selectedProgram || id) {
          const programId = selectedProgram?.id || id;
          const metricsResponse = await api.get(`/api/analytics/programs/${programId}`, {
            params: {
              date_range: dateRange
            }
          });
          
          setProgramMetrics(metricsResponse.data);
        }
      } catch (error) {
        console.error('Error fetching program data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load program data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [toast, id, selectedProgram, dateRange, navigate]);
  
  // Handle date range change
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };
  
  // Filter programs based on search term
  const filteredPrograms = programs.filter(program => 
    program.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (program.description && program.description.toLowerCase().includes(searchTerm.toLowerCase()))
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
  
  // Export program metrics
  const exportProgramMetrics = async (format) => {
    if (!selectedProgram && !id) return;
    
    try {
      const programId = selectedProgram?.id || id;
      const response = await api.get(`/api/analytics/programs/${programId}/export`, {
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
      link.setAttribute('download', `program_metrics_${programId}_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: `Program metrics exported successfully as ${format.toUpperCase()}`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error exporting program metrics:', error);
      toast({
        title: 'Error',
        description: `Failed to export program metrics as ${format.toUpperCase()}`,
        type: 'error',
      });
    }
  };
  
  // Render specific program analytics view
  const renderProgramAnalytics = () => {
    if (!programMetrics) {
      return (
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">No metrics available for this program</p>
        </div>
      );
    }
    
    const { 
      overview, 
      enrollmentTrends, 
      completionRates,
      skillsProgress,
      outcomes,
      satisfactionScores,
      trainers,
      sessionDistribution
    } = programMetrics;
    
    // Prepare session type data
    const sessionTypeData = sessionDistribution?.byType 
      ? Object.entries(sessionDistribution.byType).map(([name, value]) => ({
          name,
          value
        }))
      : [];
    
    // Prepare satisfaction data
    const satisfactionData = satisfactionScores?.history || [];
    
    // Prepare skills progress data
    const skillsProgressData = skillsProgress || [];
    
    return (
      <div className="space-y-6">
        {/* Program overview stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Total Beneficiaries</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.totalBeneficiaries || 0}
                </h3>
                <p className={`text-xs mt-1 ${overview?.beneficiaryGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.beneficiaryGrowth !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.beneficiaryGrowth >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.beneficiaryGrowth)}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-blue-50 rounded-full">
                <Users className="w-5 h-5 text-blue-500" />
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Sessions</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.totalSessions || 0}
                </h3>
                <p className={`text-xs mt-1 ${overview?.sessionGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.sessionGrowth !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.sessionGrowth >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.sessionGrowth)}% from previous period
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
                <p className="text-gray-500 text-sm">Completion Rate</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.completionRate || 0}%
                </h3>
                <p className={`text-xs mt-1 ${overview?.completionRateGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.completionRateGrowth !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.completionRateGrowth >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.completionRateGrowth)}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-purple-50 rounded-full">
                <Award className="w-5 h-5 text-purple-500" />
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Avg. Satisfaction</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.avgSatisfaction?.toFixed(1) || 0}/5
                </h3>
                <p className={`text-xs mt-1 ${overview?.satisfactionGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.satisfactionGrowth !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.satisfactionGrowth >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.satisfactionGrowth)}% from previous period
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
        
        {/* Enrollment and Completion Trends */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Enrollment Trends</h2>
            <div className="h-64">
              {enrollmentTrends && enrollmentTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={enrollmentTrends}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="newEnrollments" name="New Enrollments" fill="#4f46e5" stroke="#4f46e5" />
                    <Area type="monotone" dataKey="totalActive" name="Total Active" fill="#10b981" stroke="#10b981" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No enrollment trend data available</p>
                </div>
              )}
            </div>
          </Card>
          
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Completion Rates</h2>
            <div className="h-64">
              {completionRates && completionRates.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={completionRates}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip formatter={(value) => [`${value}%`, 'Completion Rate']} />
                    <Legend />
                    <Line type="monotone" dataKey="rate" name="Completion Rate" stroke="#4f46e5" activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="benchmark" name="Benchmark" stroke="#f59e0b" strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No completion rate data available</p>
                </div>
              )}
            </div>
          </Card>
        </div>
        
        {/* Session Distribution and Satisfaction */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Session Distribution</h2>
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
                      {(sessionTypeData || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No session distribution data available</p>
                </div>
              )}
            </div>
          </Card>
          
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Satisfaction Trends</h2>
            <div className="h-64">
              {satisfactionData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={satisfactionData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis domain={[0, 5]} />
                    <Tooltip formatter={(value) => [`${value}/5`, 'Satisfaction Score']} />
                    <Legend />
                    <Line type="monotone" dataKey="score" name="Satisfaction Score" stroke="#f59e0b" activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="avgAllPrograms" name="Avg. All Programs" stroke="#8b5cf6" strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No satisfaction data available</p>
                </div>
              )}
            </div>
          </Card>
        </div>
        
        {/* Skills Progress */}
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Skills Progress</h2>
          <div className="h-80">
            {skillsProgressData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={skillsProgressData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="baseline" name="Baseline" fill="#9ca3af" />
                  <Bar dataKey="current" name="Current" fill="#4f46e5" />
                  <Bar dataKey="target" name="Target" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-500">
                <p>No skills progress data available</p>
              </div>
            )}
          </div>
        </Card>
        
        {/* Outcomes */}
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Program Outcomes</h2>
          
          {outcomes ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Employment Rate</h3>
                <div className="text-3xl font-bold text-primary">
                  {outcomes.employmentRate}%
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  of graduates secured employment
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Skill Certification</h3>
                <div className="text-3xl font-bold text-green-600">
                  {outcomes.skillCertificationRate}%
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  of participants earned certifications
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">ROI Score</h3>
                <div className="text-3xl font-bold text-blue-600">
                  {outcomes.roiScore}/10
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  program return on investment rating
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-24 text-gray-500">
              <p>No outcome data available</p>
            </div>
          )}
        </Card>
        
        {/* Program Trainers */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium">Program Trainers</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trainer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sessions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Beneficiaries</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg. Rating</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {trainers && trainers.length > 0 ? (
                  (trainers || []).map((trainer, index) => (
                    <tr key={trainer.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-primary text-white flex items-center justify-center">
                              {trainer.name.charAt(0)}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{trainer.name}</div>
                            <div className="text-sm text-gray-500">{trainer.role}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.sessions}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.beneficiaries}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm text-gray-900 mr-2">{trainer.rating}/5</div>
                          <div className="flex">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                className={`w-4 h-4 ${i < Math.round(trainer.rating) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} 
                              />
                            ))}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          trainer.status === 'Active' 
                            ? 'bg-green-100 text-green-800' 
                            : trainer.status === 'On Leave' 
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {trainer.status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No trainers assigned to this program</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
        
        {/* Key Insights */}
        {programMetrics.insights && (
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Key Insights</h2>
            <div className="bg-gray-50 p-4 rounded-lg">
              <ul className="space-y-2">
                {(programMetrics?.insights || []).map((insight, index) => (
                  <li key={index} className="flex items-start">
                    <span className="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs mr-2 mt-0.5">{index + 1}</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        )}
      </div>
    );
  };
  
  // Render programs list
  const renderProgramsList = () => {
    return (
      <div>
        <div className="mb-6 flex items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <Input
              type="text"
              placeholder="Search programs..."
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
                    Program
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Enrolled
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Completion Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredPrograms.length > 0 ? (
                  (filteredPrograms || []).map((program) => (
                    <tr key={program.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-primary text-white flex items-center justify-center">
                              <Briefcase className="h-5 w-5" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{program.name}</div>
                            <div className="text-sm text-gray-500">{program.category || 'General'}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {program.duration || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {program.enrolledCount || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {program.completionRate || 0}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          program.status === 'Active' 
                            ? 'bg-green-100 text-green-800' 
                            : program.status === 'Completed' 
                            ? 'bg-blue-100 text-blue-800'
                            : program.status === 'Upcoming'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {program.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button 
                          variant="link" 
                          onClick={() => navigate(`/analytics/programs/${program.id}`)}
                        >
                          View Analytics
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                      No programs found
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
          {(selectedProgram || id) && (
            <button
              className="mr-4 p-2 rounded-full hover:bg-gray-100"
              onClick={() => {
                setSelectedProgram(null);
                navigate('/analytics/programs');
              }}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          
          <div>
            <h1 className="text-2xl font-bold">
              {selectedProgram || id 
                ? `Program Analytics: ${selectedProgram?.name || programs.find(p => p.id.toString() === id)?.name || 'Program'}`
                : 'Program Analytics'}
            </h1>
            {(selectedProgram || id) && (
              <p className="text-gray-500">
                Viewing metrics for {formatDateRange()}
              </p>
            )}
          </div>
        </div>
        
        {(selectedProgram || id) && (
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
                  onClick={() => exportProgramMetrics('pdf')}
                >
                  Export as PDF
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportProgramMetrics('csv')}
                >
                  Export as CSV
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportProgramMetrics('xlsx')}
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
          {selectedProgram || id ? renderProgramAnalytics() : renderProgramsList()}
        </>
      )}
    </div>
  );
};

export default ProgramAnalyticsPage;