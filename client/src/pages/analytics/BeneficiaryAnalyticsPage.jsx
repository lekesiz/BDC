import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  BarChartIcon, 
  Users, 
  UserCheck,
  Calendar, 
  Clock, 
  Award,
  ArrowLeft, 
  Download,
  ChevronDown,
  Search,
  Filter,
  TrendingUp,
  Star,
  BookOpen,
  Target,
  Loader
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area
} from 'recharts';

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

/**
 * BeneficiaryAnalyticsPage displays detailed analytics for individual beneficiaries
 */
const BeneficiaryAnalyticsPage = () => {
  const { id } = useParams(); // Optional beneficiary ID for specific beneficiary view
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState('last30days');
  const [beneficiaryMetrics, setBeneficiaryMetrics] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);
  
  // Fetch beneficiaries and metrics
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch beneficiaries list
        const beneficiariesResponse = await api.get('/api/beneficiaries');
        setBeneficiaries(beneficiariesResponse.data);
        
        // If an ID is provided, fetch that specific beneficiary
        if (id) {
          const beneficiary = beneficiariesResponse.data.find(b => b.id.toString() === id);
          if (beneficiary) {
            setSelectedBeneficiary(beneficiary);
          } else {
            toast({
              title: 'Error',
              description: 'Beneficiary not found',
              type: 'error',
            });
            navigate('/analytics/beneficiaries');
          }
        }
        
        // Fetch beneficiary metrics if a beneficiary is selected
        if (selectedBeneficiary || id) {
          const beneficiaryId = selectedBeneficiary?.id || id;
          const metricsResponse = await api.get(`/api/analytics/beneficiaries/${beneficiaryId}`, {
            params: {
              date_range: dateRange
            }
          });
          
          setBeneficiaryMetrics(metricsResponse.data);
        }
      } catch (error) {
        console.error('Error fetching beneficiary data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load beneficiary data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [toast, id, selectedBeneficiary, dateRange, navigate]);
  
  // Handle date range change
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };
  
  // Filter beneficiaries based on search term
  const filteredBeneficiaries = beneficiaries.filter(beneficiary => 
    beneficiary.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (beneficiary.email && beneficiary.email.toLowerCase().includes(searchTerm.toLowerCase()))
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
  
  // Export beneficiary metrics
  const exportBeneficiaryMetrics = async (format) => {
    if (!selectedBeneficiary && !id) return;
    
    try {
      const beneficiaryId = selectedBeneficiary?.id || id;
      const response = await api.get(`/api/analytics/beneficiaries/${beneficiaryId}/export`, {
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
      link.setAttribute('download', `beneficiary_metrics_${beneficiaryId}_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: `Beneficiary metrics exported successfully as ${format.toUpperCase()}`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error exporting beneficiary metrics:', error);
      toast({
        title: 'Error',
        description: `Failed to export beneficiary metrics as ${format.toUpperCase()}`,
        type: 'error',
      });
    }
  };
  
  // Render specific beneficiary analytics view
  const renderBeneficiaryAnalytics = () => {
    if (!beneficiaryMetrics) {
      return (
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">No metrics available for this beneficiary</p>
        </div>
      );
    }
    
    const { 
      overview, 
      attendance, 
      progression,
      skillsAssessment,
      sessionEngagement,
      outcomes,
      trainers,
      milestones,
      actionPlan
    } = beneficiaryMetrics;
    
    // Prepare session type data
    const sessionTypeData = sessionEngagement?.byType 
      ? Object.entries(sessionEngagement.byType).map(([name, value]) => ({
          name,
          value
        }))
      : [];
    
    return (
      <div className="space-y-6">
        {/* Beneficiary overview stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Program Completion</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.programCompletion || 0}%
                </h3>
                <p className={`text-xs mt-1 ${overview?.completionTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.completionTrend !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.completionTrend >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.completionTrend)}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-blue-50 rounded-full">
                <Target className="w-5 h-5 text-blue-500" />
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Attendance Rate</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.attendanceRate || 0}%
                </h3>
                <p className={`text-xs mt-1 ${overview?.attendanceTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.attendanceTrend !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.attendanceTrend >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.attendanceTrend)}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-green-50 rounded-full">
                <UserCheck className="w-5 h-5 text-green-500" />
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Avg. Assessment Score</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.avgAssessmentScore || 0}%
                </h3>
                <p className={`text-xs mt-1 ${overview?.assessmentTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.assessmentTrend !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.assessmentTrend >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.assessmentTrend)}% from previous period
                    </span>
                  ) : ''}
                </p>
              </div>
              <div className="p-2 bg-purple-50 rounded-full">
                <BookOpen className="w-5 h-5 text-purple-500" />
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-500 text-sm">Engagement Score</p>
                <h3 className="text-2xl font-bold mt-1">
                  {overview?.engagementScore?.toFixed(1) || 0}/5
                </h3>
                <p className={`text-xs mt-1 ${overview?.engagementTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {overview?.engagementTrend !== undefined ? (
                    <span className="inline-flex items-center">
                      <TrendingUp className={`w-3 h-3 mr-1 ${overview.engagementTrend >= 0 ? '' : 'transform rotate-180'}`} />
                      {Math.abs(overview.engagementTrend)}% from previous period
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
        
        {/* Attendance and Progression */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Attendance History</h2>
            <div className="h-64">
              {attendance && attendance.history && attendance.history.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={attendance.history}
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
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="rate" name="Attendance Rate (%)" fill="#4f46e5" stroke="#4f46e5" />
                    <Area type="monotone" dataKey="avgRate" name="Program Average (%)" fill="#10b981" stroke="#10b981" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No attendance data available</p>
                </div>
              )}
            </div>
          </Card>
          
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Program Progression</h2>
            <div className="h-64">
              {progression && progression.timeline && progression.timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={progression.timeline}
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
                    <Tooltip formatter={(value) => [`${value}%`, 'Completion']} />
                    <Legend />
                    <Line type="monotone" dataKey="completion" name="Completion %" stroke="#4f46e5" activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="expected" name="Expected %" stroke="#f59e0b" strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No progression data available</p>
                </div>
              )}
            </div>
          </Card>
        </div>
        
        {/* Skills Assessment */}
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Skills Assessment</h2>
          <div className="h-80">
            {skillsAssessment && skillsAssessment.skills && skillsAssessment.skills.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={skillsAssessment.skills}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="name" />
                  <PolarRadiusAxis domain={[0, 100]} />
                  <Radar name="Current Level" dataKey="current" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.6} />
                  <Radar name="Initial Level" dataKey="initial" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.4} />
                  <Radar name="Target Level" dataKey="target" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-500">
                <p>No skills assessment data available</p>
              </div>
            )}
          </div>
        </Card>
        
        {/* Session Engagement and Progress by Module */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Session Engagement</h2>
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
                  <p>No session engagement data available</p>
                </div>
              )}
            </div>
          </Card>
          
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Module Progress</h2>
            <div className="h-64">
              {progression && progression.modules && progression.modules.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={progression.modules}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                    layout="vertical"
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="name" width={100} />
                    <Tooltip formatter={(value) => [`${value}%`, 'Completion']} />
                    <Legend />
                    <Bar dataKey="completion" name="Completion %" fill="#4f46e5" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <p>No module progress data available</p>
                </div>
              )}
            </div>
          </Card>
        </div>
        
        {/* Milestones */}
        {milestones && milestones.length > 0 && (
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Progress Milestones</h2>
            <div className="relative">
              <div className="absolute left-4 inset-y-0 w-0.5 bg-gray-200"></div>
              
              <div className="space-y-8 relative">
                {milestones.map((milestone, index) => (
                  <div key={index} className="relative pl-10">
                    <div className={`absolute left-0 p-1 rounded-full ${
                      milestone.status === 'completed' 
                        ? 'bg-green-100 text-green-600 border-2 border-green-200' 
                        : milestone.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-600 border-2 border-blue-200'
                        : 'bg-gray-100 text-gray-600 border-2 border-gray-200'
                    }`}>
                      <div className="w-6 h-6 flex items-center justify-center">
                        {milestone.status === 'completed' ? (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : milestone.status === 'in_progress' ? (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                        )}
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg border p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium">{milestone.title}</h3>
                          <p className="text-sm text-gray-500 mt-1">{milestone.description}</p>
                        </div>
                        <div className="flex items-center">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            milestone.status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : milestone.status === 'in_progress'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {milestone.status === 'completed' 
                              ? 'Completed' 
                              : milestone.status === 'in_progress'
                              ? 'In Progress'
                              : 'Upcoming'}
                          </span>
                          {milestone.date && (
                            <span className="text-sm text-gray-500 ml-2">{milestone.date}</span>
                          )}
                        </div>
                      </div>
                      
                      {milestone.achievements && milestone.achievements.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs font-medium text-gray-500 mb-1">Achievements:</p>
                          <ul className="text-sm list-disc list-inside pl-1 space-y-1">
                            {milestone.achievements.map((achievement, idx) => (
                              <li key={idx}>{achievement}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}
        
        {/* Action Plan */}
        {actionPlan && (
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Action Plan</h2>
            
            <div className="space-y-4">
              {actionPlan.objectives && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Key Objectives</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {actionPlan.objectives.map((objective, index) => (
                      <li key={index} className="text-sm">{objective}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {actionPlan.shortTermGoals && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Short-term Goals (1-3 months)</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {actionPlan.shortTermGoals.map((goal, index) => (
                      <li key={index} className="text-sm">{goal}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {actionPlan.longTermGoals && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Long-term Goals (4+ months)</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {actionPlan.longTermGoals.map((goal, index) => (
                      <li key={index} className="text-sm">{goal}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {actionPlan.recommendations && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Trainer Recommendations</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {actionPlan.recommendations.map((recommendation, index) => (
                      <li key={index} className="text-sm">{recommendation}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {actionPlan.nextReview && (
                <div className="mt-6 flex items-center justify-between px-4 py-3 bg-gray-50 rounded-lg">
                  <div className="text-sm">
                    <p className="font-medium text-gray-700">Next progress review:</p>
                    <p className="text-gray-500">{actionPlan.nextReview}</p>
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/beneficiaries/${id}/progress`)}
                  >
                    View Full Plan
                  </Button>
                </div>
              )}
            </div>
          </Card>
        )}
        
        {/* Assigned Trainers */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium">Assigned Trainers</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trainer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sessions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Session</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {trainers && trainers.length > 0 ? (
                  trainers.map((trainer, index) => (
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
                            <div className="text-sm text-gray-500">{trainer.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.role}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.sessionsCount}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.lastSession}</td>
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
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No trainers assigned to this beneficiary</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    );
  };
  
  // Render beneficiaries list
  const renderBeneficiariesList = () => {
    return (
      <div>
        <div className="mb-6 flex items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <Input
              type="text"
              placeholder="Search beneficiaries..."
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
                    Beneficiary
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Program
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assessment Score
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
                {filteredBeneficiaries.length > 0 ? (
                  filteredBeneficiaries.map((beneficiary) => (
                    <tr key={beneficiary.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-primary text-white flex items-center justify-center">
                              {beneficiary.name.charAt(0)}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{beneficiary.name}</div>
                            <div className="text-sm text-gray-500">{beneficiary.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {beneficiary.program}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div 
                            className="bg-primary h-2.5 rounded-full" 
                            style={{ width: `${beneficiary.progress || 0}%` }}
                          ></div>
                        </div>
                        <p className="text-xs mt-1 text-gray-500">{beneficiary.progress || 0}% completed</p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {beneficiary.assessmentScore || 0}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          beneficiary.status === 'Active' 
                            ? 'bg-green-100 text-green-800' 
                            : beneficiary.status === 'Completed' 
                            ? 'bg-blue-100 text-blue-800'
                            : beneficiary.status === 'On Leave'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {beneficiary.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button 
                          variant="link" 
                          onClick={() => navigate(`/analytics/beneficiaries/${beneficiary.id}`)}
                        >
                          View Analytics
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                      No beneficiaries found
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
          {(selectedBeneficiary || id) && (
            <button
              className="mr-4 p-2 rounded-full hover:bg-gray-100"
              onClick={() => {
                setSelectedBeneficiary(null);
                navigate('/analytics/beneficiaries');
              }}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          
          <div>
            <h1 className="text-2xl font-bold">
              {selectedBeneficiary || id 
                ? `Beneficiary Analytics: ${selectedBeneficiary?.name || beneficiaries.find(b => b.id.toString() === id)?.name || 'Beneficiary'}`
                : 'Beneficiary Analytics'}
            </h1>
            {(selectedBeneficiary || id) && (
              <p className="text-gray-500">
                Viewing metrics for {formatDateRange()}
              </p>
            )}
          </div>
        </div>
        
        {(selectedBeneficiary || id) && (
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
                  onClick={() => exportBeneficiaryMetrics('pdf')}
                >
                  Export as PDF
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportBeneficiaryMetrics('csv')}
                >
                  Export as CSV
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  onClick={() => exportBeneficiaryMetrics('xlsx')}
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
          {selectedBeneficiary || id ? renderBeneficiaryAnalytics() : renderBeneficiariesList()}
        </>
      )}
    </div>
  );
};

export default BeneficiaryAnalyticsPage;