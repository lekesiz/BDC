import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart, 
  PieChart, 
  TrendingUp, 
  Users, 
  Calendar, 
  FileText, 
  Award,
  Clock,
  Download,
  Filter,
  ChevronDown,
  AlertCircle,
  Loader
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { BeneficiaryStatistics } from '@/components/analytics/BeneficiaryStatistics';
import { TrainingProgress } from '@/components/analytics/TrainingProgress';
import { AppointmentMetrics } from '@/components/analytics/AppointmentMetrics';
import { EvaluationResults } from '@/components/analytics/EvaluationResults';
import { SkillsDistribution } from '@/components/analytics/SkillsDistribution';
import { ActivityTimeline } from '@/components/analytics/ActivityTimeline';

/**
 * AnalyticsDashboardPage provides a comprehensive view of program statistics and analytics
 */
const AnalyticsDashboardPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [dateRange, setDateRange] = useState('last30days');
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedTrainers, setSelectedTrainers] = useState([]);
  const [selectedPrograms, setSelectedPrograms] = useState([]);
  const [trainers, setTrainers] = useState([]);
  const [programs, setPrograms] = useState([]);

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch trainers and programs for filters
        const [trainersResponse, programsResponse] = await Promise.all([
          api.get('/api/analytics/trainers'),
          api.get('/api/analytics/programs')
        ]);
        
        setTrainers(trainersResponse.data.trainers || []);
        setPrograms(programsResponse.data.programs || []);
        
        // Set default selections if none are made
        if (selectedTrainers.length === 0) {
          setSelectedTrainers(trainersResponse.data.trainers.map(trainer => trainer.id));
        }
        
        if (selectedPrograms.length === 0) {
          setSelectedPrograms(programsResponse.data.programs.map(program => program.id));
        }
        
        // Fetch analytics data with filters
        const response = await api.get('/api/analytics/dashboard', {
          params: {
            date_range: dateRange,
            trainer_ids: selectedTrainers.join(','),
            program_ids: selectedPrograms.join(',')
          }
        });
        
        setAnalyticsData(response.data);
      } catch (error) {
        console.error('Error fetching analytics data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load analytics data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAnalyticsData();
  }, [toast, dateRange, selectedTrainers, selectedPrograms]);

  // Handle date range change
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };

  // Toggle trainer selection
  const toggleTrainer = (trainerId) => {
    setSelectedTrainers(prev => {
      if (prev.includes(trainerId)) {
        return prev.filter(id => id !== trainerId);
      } else {
        return [...prev, trainerId];
      }
    });
  };

  // Toggle program selection
  const toggleProgram = (programId) => {
    setSelectedPrograms(prev => {
      if (prev.includes(programId)) {
        return prev.filter(id => id !== programId);
      } else {
        return [...prev, programId];
      }
    });
  };

  // Select all trainers
  const selectAllTrainers = () => {
    setSelectedTrainers(trainers.map(trainer => trainer.id));
  };

  // Select all programs
  const selectAllPrograms = () => {
    setSelectedPrograms(programs.map(program => program.id));
  };

  // Clear all trainer selections
  const clearTrainerSelection = () => {
    setSelectedTrainers([]);
  };

  // Clear all program selections
  const clearProgramSelection = () => {
    setSelectedPrograms([]);
  };

  // Export analytics data
  const exportAnalyticsData = async (format) => {
    try {
      const response = await api.get(`/api/analytics/export`, {
        params: {
          format,
          date_range: dateRange,
          trainer_ids: selectedTrainers.join(','),
          program_ids: selectedPrograms.join(',')
        },
        responseType: 'blob'
      });
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bdc_analytics_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: `Analytics data exported successfully as ${format.toUpperCase()}`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error exporting analytics data:', error);
      toast({
        title: 'Error',
        description: `Failed to export analytics data as ${format.toUpperCase()}`,
        type: 'error',
      });
    }
  };

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

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
        
        <div className="flex space-x-2">
          <div className="relative">
            <Button
              variant="outline"
              onClick={() => setFilterOpen(!filterOpen)}
              className="flex items-center"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
              <ChevronDown className="w-4 h-4 ml-2" />
            </Button>
            
            {filterOpen && (
              <div className="absolute right-0 mt-2 w-96 bg-white rounded-md shadow-lg z-10 border p-4">
                <h3 className="text-sm font-medium mb-2">Date Range</h3>
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <Button
                    variant={dateRange === 'last7days' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleDateRangeChange('last7days')}
                  >
                    Last 7 Days
                  </Button>
                  <Button
                    variant={dateRange === 'last30days' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleDateRangeChange('last30days')}
                  >
                    Last 30 Days
                  </Button>
                  <Button
                    variant={dateRange === 'last90days' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleDateRangeChange('last90days')}
                  >
                    Last 90 Days
                  </Button>
                  <Button
                    variant={dateRange === 'thisYear' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleDateRangeChange('thisYear')}
                  >
                    This Year
                  </Button>
                  <Button
                    variant={dateRange === 'allTime' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleDateRangeChange('allTime')}
                    className="col-span-2"
                  >
                    All Time
                  </Button>
                </div>
                
                <div className="border-t pt-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium">Trainers</h3>
                    <div className="flex space-x-2">
                      <button
                        className="text-xs text-primary hover:underline"
                        onClick={selectAllTrainers}
                      >
                        Select All
                      </button>
                      <span className="text-gray-300">|</span>
                      <button
                        className="text-xs text-gray-500 hover:underline"
                        onClick={clearTrainerSelection}
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                  <div className="max-h-36 overflow-y-auto space-y-1">
                    {trainers.map(trainer => (
                      <div key={trainer.id} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`trainer-${trainer.id}`}
                          checked={selectedTrainers.includes(trainer.id)}
                          onChange={() => toggleTrainer(trainer.id)}
                          className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        />
                        <label htmlFor={`trainer-${trainer.id}`} className="ml-2 block text-sm text-gray-700">
                          {trainer.name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="border-t pt-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium">Programs</h3>
                    <div className="flex space-x-2">
                      <button
                        className="text-xs text-primary hover:underline"
                        onClick={selectAllPrograms}
                      >
                        Select All
                      </button>
                      <span className="text-gray-300">|</span>
                      <button
                        className="text-xs text-gray-500 hover:underline"
                        onClick={clearProgramSelection}
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                  <div className="max-h-36 overflow-y-auto space-y-1">
                    {programs.map(program => (
                      <div key={program.id} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`program-${program.id}`}
                          checked={selectedPrograms.includes(program.id)}
                          onChange={() => toggleProgram(program.id)}
                          className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        />
                        <label htmlFor={`program-${program.id}`} className="ml-2 block text-sm text-gray-700">
                          {program.name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-end">
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => setFilterOpen(false)}
                  >
                    Apply Filters
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
                onClick={() => exportAnalyticsData('pdf')}
              >
                Export as PDF
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                onClick={() => exportAnalyticsData('csv')}
              >
                Export as CSV
              </button>
              <button
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                onClick={() => exportAnalyticsData('xlsx')}
              >
                Export as Excel
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mb-6 bg-gray-50 rounded-lg p-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium">Analytics Overview</h2>
          <p className="text-gray-500 text-sm">
            Data shown for: <span className="font-medium">{formatDateRange()}</span>
          </p>
        </div>
        
        <div className="text-sm text-gray-500 flex items-center">
          <Clock className="w-4 h-4 mr-1" />
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>
      
      {(!selectedTrainers.length || !selectedPrograms.length) && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="w-5 h-5 text-amber-500 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-amber-800">Incomplete filter selection</h3>
            <p className="text-amber-700 mt-1">
              {!selectedTrainers.length && !selectedPrograms.length
                ? 'No trainers or programs selected. Select at least one trainer and one program to view data.'
                : !selectedTrainers.length
                ? 'No trainers selected. Select at least one trainer to view data.'
                : 'No programs selected. Select at least one program to view data.'}
            </p>
          </div>
        </div>
      )}
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Total Beneficiaries</p>
              <h3 className="text-3xl font-bold mt-1">
                {analyticsData?.metrics?.total_beneficiaries || 0}
              </h3>
              <p className={`text-sm mt-1 ${analyticsData?.metrics?.beneficiary_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <span className="inline-flex items-center">
                  <TrendingUp className={`w-3 h-3 mr-1 ${analyticsData?.metrics?.beneficiary_growth >= 0 ? '' : 'transform rotate-180'}`} />
                  {Math.abs(analyticsData?.metrics?.beneficiary_growth || 0)}% from previous period
                </span>
              </p>
            </div>
            <div className="p-3 bg-blue-50 rounded-full">
              <Users className="w-6 h-6 text-blue-500" />
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Total Sessions</p>
              <h3 className="text-3xl font-bold mt-1">
                {analyticsData?.metrics?.total_sessions || 0}
              </h3>
              <p className={`text-sm mt-1 ${analyticsData?.metrics?.session_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <span className="inline-flex items-center">
                  <TrendingUp className={`w-3 h-3 mr-1 ${analyticsData?.metrics?.session_growth >= 0 ? '' : 'transform rotate-180'}`} />
                  {Math.abs(analyticsData?.metrics?.session_growth || 0)}% from previous period
                </span>
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-full">
              <Calendar className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Total Programs</p>
              <h3 className="text-3xl font-bold mt-1">
                {analyticsData?.metrics?.total_programs || 0}
              </h3>
              <p className={`text-sm mt-1 ${analyticsData?.metrics?.program_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <span className="inline-flex items-center">
                  <TrendingUp className={`w-3 h-3 mr-1 ${analyticsData?.metrics?.program_growth >= 0 ? '' : 'transform rotate-180'}`} />
                  {Math.abs(analyticsData?.metrics?.program_growth || 0)}% from previous period
                </span>
              </p>
            </div>
            <div className="p-3 bg-purple-50 rounded-full">
              <FileText className="w-6 h-6 text-purple-500" />
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Completion Rate</p>
              <h3 className="text-3xl font-bold mt-1">
                {analyticsData?.metrics?.completion_rate || 0}%
              </h3>
              <p className={`text-sm mt-1 ${analyticsData?.metrics?.completion_rate_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <span className="inline-flex items-center">
                  <TrendingUp className={`w-3 h-3 mr-1 ${analyticsData?.metrics?.completion_rate_growth >= 0 ? '' : 'transform rotate-180'}`} />
                  {Math.abs(analyticsData?.metrics?.completion_rate_growth || 0)}% from previous period
                </span>
              </p>
            </div>
            <div className="p-3 bg-yellow-50 rounded-full">
              <Award className="w-6 h-6 text-yellow-500" />
            </div>
          </div>
        </Card>
      </div>
      
      {/* Main Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Beneficiary Statistics</h2>
          <BeneficiaryStatistics data={analyticsData?.beneficiary_statistics || []} />
        </Card>
        
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Training Progress</h2>
          <TrainingProgress data={analyticsData?.training_progress || []} />
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Appointment Metrics</h2>
          <AppointmentMetrics data={analyticsData?.appointment_metrics || {}} />
        </Card>
        
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Evaluation Results</h2>
          <EvaluationResults data={analyticsData?.evaluation_results || {}} />
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Skills Distribution</h2>
          <SkillsDistribution data={analyticsData?.skills_distribution || []} />
        </Card>
        
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Activity Timeline</h2>
          <ActivityTimeline data={analyticsData?.activity_timeline || []} />
        </Card>
      </div>
      
      {/* Program Performance Table */}
      <Card className="p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">Program Performance</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/analytics/programs')}
          >
            View All Programs
          </Button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Program Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Beneficiaries</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Completion Rate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg. Satisfaction</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {analyticsData?.program_performance ? (
                analyticsData.program_performance.map((program, index) => (
                  <tr key={program.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{program.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{program.beneficiaries}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{program.completion_rate}%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{program.avg_satisfaction}/5</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        program.status === 'Active' 
                          ? 'bg-green-100 text-green-800' 
                          : program.status === 'Completed' 
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {program.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No program data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
      
      {/* Trainer Performance Table */}
      <Card className="p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">Trainer Performance</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/analytics/trainers')}
          >
            View All Trainers
          </Button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trainer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned Beneficiaries</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sessions Conducted</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg. Rating</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {analyticsData?.trainer_performance ? (
                analyticsData.trainer_performance.map((trainer, index) => (
                  <tr key={trainer.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 relative">
                          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                            <span className="text-gray-600 font-medium text-sm">{trainer.name.charAt(0)}</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{trainer.name}</div>
                          <div className="text-sm text-gray-500">{trainer.specialization}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.assigned_beneficiaries}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.sessions_conducted}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.avg_rating}/5</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trainer.success_rate}%</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No trainer data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
      
      {/* Beneficiary Performance Table */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">Beneficiary Performance</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/analytics/beneficiaries')}
          >
            View All Beneficiaries
          </Button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Beneficiary</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Program</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Attendance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {analyticsData?.beneficiary_performance ? (
                analyticsData.beneficiary_performance.map((beneficiary, index) => (
                  <tr key={beneficiary.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 relative">
                          <div className="h-10 w-10 rounded-full bg-primary text-white flex items-center justify-center">
                            <span className="font-medium text-sm">{beneficiary.name.charAt(0)}</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{beneficiary.name}</div>
                          <div className="text-sm text-gray-500">{beneficiary.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{beneficiary.program}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="bg-primary h-2.5 rounded-full" 
                          style={{ width: `${beneficiary.progress || 0}%` }}
                        ></div>
                      </div>
                      <p className="text-xs mt-1 text-gray-500">{beneficiary.progress || 0}% completed</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{beneficiary.attendance_rate}%</td>
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
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No beneficiary data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default AnalyticsDashboardPage;