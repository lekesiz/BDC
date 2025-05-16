import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  BarChart2, 
  LineChart, 
  TrendingUp, 
  Award, 
  Calendar, 
  Download, 
  FileText, 
  Filter,
  Info,
  MessageCircle,
  AlertTriangle,
  CheckCircle,
  Printer,
  Share2,
  HelpCircle
} from 'lucide-react';
import Chart from 'chart.js/auto';

import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '@/components/ui/modal';
import { Alert } from '@/components/ui/alert';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import api from '@/lib/api';

/**
 * ProgressTrackingPage component for visualizing beneficiary progress
 */
const ProgressTrackingPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const { addToast } = useToast();
  
  // Chart references
  const overviewChartRef = useRef(null);
  const skillsChartRef = useRef(null);
  const sessionsChartRef = useRef(null);
  const comparisonChartRef = useRef(null);
  
  // Chart instances
  const [overviewChart, setOverviewChart] = useState(null);
  const [skillsChart, setSkillsChart] = useState(null);
  const [sessionsChart, setSessionsChart] = useState(null);
  const [comparisonChart, setComparisonChart] = useState(null);
  
  // State
  const [beneficiary, setBeneficiary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isTabLoading, setIsTabLoading] = useState(false);
  const [progressData, setProgressData] = useState({});
  const [evaluations, setEvaluations] = useState([]);
  const [skillsData, setSkillsData] = useState([]);
  const [sessionsData, setSessionsData] = useState([]);
  const [comparisonData, setComparisonData] = useState({});
  
  // Filters
  const [dateRange, setDateRange] = useState('last3months');
  const [skillsFilter, setSkillsFilter] = useState('all');
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  
  // Check if user can manage progress
  const canManage = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  
  // Fetch beneficiary data
  useEffect(() => {
    const fetchBeneficiary = async () => {
      try {
        setIsLoading(true);
        
        const response = await api.get(`/api/beneficiaries/${id}`);
        setBeneficiary(response.data);
        
      } catch (error) {
        console.error('Error fetching beneficiary:', error);
        addToast({
          type: 'error',
          title: 'Failed to load beneficiary',
          message: error.response?.data?.message || 'An unexpected error occurred'
        });
        
        // Navigate back on error
        navigate('/beneficiaries');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchBeneficiary();
  }, [id, navigate, addToast]);
  
  // Fetch overview data
  useEffect(() => {
    if (beneficiary && activeTab === 'overview') {
      const fetchOverviewData = async () => {
        try {
          setIsTabLoading(true);
          
          const response = await api.get(`/api/beneficiaries/${id}/progress`, {
            params: { date_range: dateRange }
          });
          
          setProgressData(response.data);
          
          // Also fetch evaluations for the overview
          const evaluationsResponse = await api.get(`/api/beneficiaries/${id}/evaluations`, {
            params: { limit: 5, sort_by: 'evaluation_date', sort_direction: 'desc' }
          });
          
          setEvaluations(evaluationsResponse.data);
          
        } catch (error) {
          console.error('Error fetching progress data:', error);
          addToast({
            type: 'error',
            title: 'Failed to load progress data',
            message: 'Could not fetch progress overview.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      
      fetchOverviewData();
    }
  }, [beneficiary, id, activeTab, dateRange, addToast]);
  
  // Fetch skills data
  useEffect(() => {
    if (beneficiary && activeTab === 'skills') {
      const fetchSkillsData = async () => {
        try {
          setIsTabLoading(true);
          
          const response = await api.get(`/api/beneficiaries/${id}/skills`, {
            params: { 
              date_range: dateRange,
              category: skillsFilter !== 'all' ? skillsFilter : undefined
            }
          });
          
          setSkillsData(response.data);
          
        } catch (error) {
          console.error('Error fetching skills data:', error);
          addToast({
            type: 'error',
            title: 'Failed to load skills data',
            message: 'Could not fetch skills progress.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      
      fetchSkillsData();
    }
  }, [beneficiary, id, activeTab, dateRange, skillsFilter, addToast]);
  
  // Fetch sessions data
  useEffect(() => {
    if (beneficiary && activeTab === 'sessions') {
      const fetchSessionsData = async () => {
        try {
          setIsTabLoading(true);
          
          const response = await api.get(`/api/beneficiaries/${id}/sessions/analytics`, {
            params: { date_range: dateRange }
          });
          
          setSessionsData(response.data);
          
        } catch (error) {
          console.error('Error fetching sessions data:', error);
          addToast({
            type: 'error',
            title: 'Failed to load sessions data',
            message: 'Could not fetch sessions analytics.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      
      fetchSessionsData();
    }
  }, [beneficiary, id, activeTab, dateRange, addToast]);
  
  // Fetch comparison data
  useEffect(() => {
    if (beneficiary && activeTab === 'comparison') {
      const fetchComparisonData = async () => {
        try {
          setIsTabLoading(true);
          
          const response = await api.get(`/api/beneficiaries/${id}/comparison`, {
            params: { date_range: dateRange }
          });
          
          setComparisonData(response.data);
          
        } catch (error) {
          console.error('Error fetching comparison data:', error);
          addToast({
            type: 'error',
            title: 'Failed to load comparison data',
            message: 'Could not fetch peer comparison data.'
          });
        } finally {
          setIsTabLoading(false);
        }
      };
      
      fetchComparisonData();
    }
  }, [beneficiary, id, activeTab, dateRange, addToast]);

  // Initialize and update overview chart
  useEffect(() => {
    if (activeTab === 'overview' && !isTabLoading && progressData.progress_history && overviewChartRef.current) {
      // Destroy existing chart if it exists
      if (overviewChart) {
        overviewChart.destroy();
      }
      
      const labels = progressData.progress_history.map(item => formatDate(item.date));
      const scores = progressData.progress_history.map(item => item.score);
      
      // Create new chart
      const newChart = new Chart(overviewChartRef.current, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Overall Progress',
            data: scores,
            borderColor: '#4F46E5',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#4F46E5',
            pointBorderColor: '#fff',
            pointBorderWidth: 1,
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%';
                }
              },
              title: {
                display: true,
                text: 'Progress Score'
              }
            },
            x: {
              grid: {
                display: false
              },
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
      
      setOverviewChart(newChart);
      
      return () => {
        newChart.destroy();
      };
    }
  }, [activeTab, isTabLoading, progressData, overviewChart]);
  
  // Initialize and update skills chart
  useEffect(() => {
    if (activeTab === 'skills' && !isTabLoading && skillsData.length > 0 && skillsChartRef.current) {
      // Destroy existing chart if it exists
      if (skillsChart) {
        skillsChart.destroy();
      }
      
      const labels = skillsData.map(skill => skill.name);
      const currentScores = skillsData.map(skill => skill.current_score);
      const previousScores = skillsData.map(skill => skill.previous_score);
      
      // Create new chart
      const newChart = new Chart(skillsChartRef.current, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Current Score',
              data: currentScores,
              backgroundColor: 'rgba(79, 70, 229, 0.8)',
              borderColor: 'rgba(79, 70, 229, 1)',
              borderWidth: 1,
              borderRadius: 4,
            },
            {
              label: 'Previous Score',
              data: previousScores,
              backgroundColor: 'rgba(156, 163, 175, 0.5)',
              borderColor: 'rgba(156, 163, 175, 0.8)',
              borderWidth: 1,
              borderRadius: 4,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%';
                }
              },
              title: {
                display: true,
                text: 'Skill Level'
              }
            },
            x: {
              grid: {
                display: false
              },
              title: {
                display: true,
                text: 'Skills'
              }
            }
          }
        }
      });
      
      setSkillsChart(newChart);
      
      return () => {
        newChart.destroy();
      };
    }
  }, [activeTab, isTabLoading, skillsData, skillsChart]);
  
  // Initialize and update sessions chart
  useEffect(() => {
    if (activeTab === 'sessions' && !isTabLoading && sessionsData.attendance_history && sessionsChartRef.current) {
      // Destroy existing chart if it exists
      if (sessionsChart) {
        sessionsChart.destroy();
      }
      
      const labels = sessionsData.attendance_history.map(item => formatDate(item.date));
      const attended = sessionsData.attendance_history.map(item => item.attended);
      const missed = sessionsData.attendance_history.map(item => item.missed);
      
      // Create new chart
      const newChart = new Chart(sessionsChartRef.current, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Attended',
              data: attended,
              backgroundColor: 'rgba(16, 185, 129, 0.8)',
              borderColor: 'rgba(16, 185, 129, 1)',
              borderWidth: 1,
              borderRadius: 4,
            },
            {
              label: 'Missed',
              data: missed,
              backgroundColor: 'rgba(239, 68, 68, 0.8)',
              borderColor: 'rgba(239, 68, 68, 1)',
              borderWidth: 1,
              borderRadius: 4,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                precision: 0
              },
              title: {
                display: true,
                text: 'Number of Sessions'
              },
              stacked: true
            },
            x: {
              grid: {
                display: false
              },
              title: {
                display: true,
                text: 'Date'
              },
              stacked: true
            }
          }
        }
      });
      
      setSessionsChart(newChart);
      
      return () => {
        newChart.destroy();
      };
    }
  }, [activeTab, isTabLoading, sessionsData, sessionsChart]);
  
  // Initialize and update comparison chart
  useEffect(() => {
    if (activeTab === 'comparison' && !isTabLoading && comparisonData.skill_comparison && comparisonChartRef.current) {
      // Destroy existing chart if it exists
      if (comparisonChart) {
        comparisonChart.destroy();
      }
      
      const labels = comparisonData.skill_comparison.map(item => item.skill_name);
      const beneficiaryScores = comparisonData.skill_comparison.map(item => item.beneficiary_score);
      const averageScores = comparisonData.skill_comparison.map(item => item.average_score);
      const topScores = comparisonData.skill_comparison.map(item => item.top_score);
      
      // Create new chart
      const newChart = new Chart(comparisonChartRef.current, {
        type: 'radar',
        data: {
          labels: labels,
          datasets: [
            {
              label: beneficiary.first_name,
              data: beneficiaryScores,
              backgroundColor: 'rgba(79, 70, 229, 0.2)',
              borderColor: 'rgba(79, 70, 229, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(79, 70, 229, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(79, 70, 229, 1)',
              pointRadius: 4
            },
            {
              label: 'Group Average',
              data: averageScores,
              backgroundColor: 'rgba(107, 114, 128, 0.2)',
              borderColor: 'rgba(107, 114, 128, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(107, 114, 128, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(107, 114, 128, 1)',
              pointRadius: 4
            },
            {
              label: 'Top Performers',
              data: topScores,
              backgroundColor: 'rgba(245, 158, 11, 0.2)',
              borderColor: 'rgba(245, 158, 11, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(245, 158, 11, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(245, 158, 11, 1)',
              pointRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              angleLines: {
                display: true
              },
              min: 0,
              max: 100,
              ticks: {
                stepSize: 20,
                callback: function(value) {
                  return value + '%';
                }
              }
            }
          },
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return context.dataset.label + ': ' + context.formattedValue + '%';
                }
              }
            }
          }
        }
      });
      
      setComparisonChart(newChart);
      
      return () => {
        newChart.destroy();
      };
    }
  }, [activeTab, isTabLoading, comparisonData, comparisonChart, beneficiary]);
  
  // Handle date range change
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };
  
  // Handle skills filter change
  const handleSkillsFilterChange = (category) => {
    setSkillsFilter(category);
  };
  
  // Handle export progress report
  const handleExportReport = () => {
    setIsReportModalOpen(true);
  };
  
  // Generate and download report
  const generateReport = async (format) => {
    try {
      setIsLoading(true);
      
      const response = await api.get(`/api/beneficiaries/${id}/report`, {
        params: { format, date_range: dateRange },
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      const extension = format === 'pdf' ? 'pdf' : 'xlsx';
      link.href = url;
      link.setAttribute('download', `progress_report_${beneficiary.first_name}_${beneficiary.last_name}.${extension}`);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      link.remove();
      window.URL.revokeObjectURL(url);
      
      addToast({
        type: 'success',
        title: 'Report generated',
        message: 'Progress report has been downloaded successfully.'
      });
      
      setIsReportModalOpen(false);
      
    } catch (error) {
      console.error('Error generating report:', error);
      addToast({
        type: 'error',
        title: 'Report generation failed',
        message: 'Failed to generate progress report. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Render loading state
  if (isLoading && !beneficiary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  // Render not found state
  if (!beneficiary) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Beneficiary Not Found</h1>
          <p className="text-gray-600 mb-6">The beneficiary you're looking for doesn't exist or has been removed.</p>
          <Button 
            onClick={() => navigate('/beneficiaries')}
            leftIcon={<ArrowLeft className="h-4 w-4" />}
          >
            Back to Beneficiaries
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header with navigation */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate(`/beneficiaries/${id}`)}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Beneficiary
        </Button>
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 className="text-2xl font-bold">Progress Tracking</h1>
            <p className="text-gray-600">
              Monitor progress for {beneficiary.first_name} {beneficiary.last_name}
            </p>
          </div>
          
          <div className="flex gap-2 mt-4 md:mt-0">
            <Button
              variant="outline"
              onClick={handleExportReport}
            >
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
            
            <select
              value={dateRange}
              onChange={(e) => handleDateRangeChange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="last3months">Last 3 Months</option>
              <option value="last6months">Last 6 Months</option>
              <option value="lastyear">Last Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Beneficiary summary card */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-4">
            <Avatar 
              src={beneficiary.profile_picture}
              alt={`${beneficiary.first_name} ${beneficiary.last_name}`}
              initials={`${beneficiary.first_name?.[0] || ''}${beneficiary.last_name?.[0] || ''}`}
              size="lg"
            />
            
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-xl font-semibold">
                {beneficiary.first_name} {beneficiary.last_name}
              </h2>
              <p className="text-gray-600">{beneficiary.email}</p>
              
              <div className="flex flex-wrap gap-2 mt-2 justify-center md:justify-start">
                <Badge color={
                  beneficiary.status === 'active' ? 'green' :
                  beneficiary.status === 'inactive' ? 'gray' :
                  beneficiary.status === 'pending' ? 'yellow' :
                  beneficiary.status === 'completed' ? 'blue' : 'gray'
                }>
                  {beneficiary.status.charAt(0).toUpperCase() + beneficiary.status.slice(1)}
                </Badge>
                
                {beneficiary.category && (
                  <Badge color="purple">{beneficiary.category}</Badge>
                )}
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xl font-semibold">{progressData.overview?.overall_progress || '0%'}</div>
                <div className="text-xs text-gray-500">Overall Progress</div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xl font-semibold">{progressData.overview?.evaluation_count || 0}</div>
                <div className="text-xs text-gray-500">Evaluations</div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xl font-semibold">{progressData.overview?.sessions_completed || 0}</div>
                <div className="text-xs text-gray-500">Sessions</div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xl font-semibold">{progressData.overview?.improvement_rate || '0%'}</div>
                <div className="text-xs text-gray-500">Improvement Rate</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Tabs container */}
      <Card>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <CardHeader className="pb-0">
            <TabsList>
              <TabTrigger value="overview">
                <BarChart2 className="h-4 w-4 mr-2" />
                Overview
              </TabTrigger>
              <TabTrigger value="skills">
                <Award className="h-4 w-4 mr-2" />
                Skills Analysis
              </TabTrigger>
              <TabTrigger value="sessions">
                <Calendar className="h-4 w-4 mr-2" />
                Session Analytics
              </TabTrigger>
              <TabTrigger value="comparison">
                <TrendingUp className="h-4 w-4 mr-2" />
                Peer Comparison
              </TabTrigger>
            </TabsList>
          </CardHeader>
          
          {/* Overview Tab */}
          <TabContent value="overview">
            <CardContent className="pt-6">
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading progress data...</p>
                </div>
              ) : !progressData.overview ? (
                <div className="text-center py-8 border rounded-md">
                  <BarChart2 className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No progress data available</h4>
                  <p className="text-gray-400 text-sm mt-1">This beneficiary doesn't have any evaluation data yet.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Progress Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Card className="bg-green-50">
                      <CardContent className="p-4 flex items-center">
                        <div className="rounded-full bg-green-100 p-3 mr-4">
                          <TrendingUp className="h-6 w-6 text-green-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Current Progress</p>
                          <p className="text-2xl font-bold">{progressData.overview.overall_progress}</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-blue-50">
                      <CardContent className="p-4 flex items-center">
                        <div className="rounded-full bg-blue-100 p-3 mr-4">
                          <Award className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Top Skill</p>
                          <p className="text-lg font-bold">{progressData.overview.top_skill || 'N/A'}</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-yellow-50">
                      <CardContent className="p-4 flex items-center">
                        <div className="rounded-full bg-yellow-100 p-3 mr-4">
                          <AlertTriangle className="h-6 w-6 text-yellow-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Area to Improve</p>
                          <p className="text-lg font-bold">{progressData.overview.area_to_improve || 'N/A'}</p>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-purple-50">
                      <CardContent className="p-4 flex items-center">
                        <div className="rounded-full bg-purple-100 p-3 mr-4">
                          <Calendar className="h-6 w-6 text-purple-600" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Next Evaluation</p>
                          <p className="text-lg font-bold">{progressData.overview.next_evaluation_date ? formatDate(progressData.overview.next_evaluation_date) : 'Not scheduled'}</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {/* Progress Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Progress Over Time</CardTitle>
                      <CardDescription>
                        Overall progress score based on evaluations and sessions
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-80">
                        <canvas ref={overviewChartRef}></canvas>
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Recent Evaluations */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Evaluations</CardTitle>
                      <CardDescription>
                        Latest evaluation results and scores
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {evaluations.length === 0 ? (
                        <p className="text-gray-500 italic text-center py-4">No evaluations available</p>
                      ) : (
                        <div className="space-y-4">
                          {evaluations.map((evaluation) => (
                            <div key={evaluation.id} className="border-b pb-4 last:border-b-0">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h4 className="font-medium">{evaluation.title}</h4>
                                  <p className="text-sm text-gray-500">{formatDate(evaluation.evaluation_date)}</p>
                                </div>
                                <Badge color={
                                  evaluation.status === 'completed' ? 'green' :
                                  evaluation.status === 'in_progress' ? 'yellow' :
                                  evaluation.status === 'pending' ? 'blue' : 'gray'
                                }>
                                  {evaluation.status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                                </Badge>
                              </div>
                              
                              {evaluation.status === 'completed' && (
                                <div className="mt-3">
                                  <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm font-medium">Overall Score</span>
                                    <span className="text-sm font-medium">{evaluation.percentage_score}%</span>
                                  </div>
                                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                                    <div 
                                      className={`h-2.5 rounded-full ${
                                        evaluation.percentage_score >= 70 ? 'bg-green-600' :
                                        evaluation.percentage_score >= 40 ? 'bg-yellow-500' :
                                        'bg-red-500'
                                      }`}
                                      style={{ width: `${evaluation.percentage_score}%` }}
                                    ></div>
                                  </div>
                                </div>
                              )}
                              
                              <div className="mt-3 text-right">
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => navigate(`/evaluations/${evaluation.id}`)}
                                >
                                  View Details
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                    <CardFooter className="border-t pt-4">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="ml-auto"
                        onClick={() => navigate(`/beneficiaries/${id}/evaluations`)}
                      >
                        View All Evaluations
                      </Button>
                    </CardFooter>
                  </Card>
                  
                  {/* AI Insights */}
                  {progressData.ai_insights && (
                    <Card>
                      <CardHeader>
                        <CardTitle>AI-Powered Insights</CardTitle>
                        <CardDescription>
                          Personalized insights based on progress analysis
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {progressData.ai_insights.map((insight, index) => (
                            <div key={index} className="flex items-start gap-3 p-3 rounded-md bg-gray-50">
                              <div className={`rounded-full p-2 ${
                                insight.type === 'strength' ? 'bg-green-100 text-green-600' :
                                insight.type === 'improvement' ? 'bg-yellow-100 text-yellow-600' :
                                insight.type === 'suggestion' ? 'bg-blue-100 text-blue-600' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                {insight.type === 'strength' ? <CheckCircle className="h-5 w-5" /> :
                                 insight.type === 'improvement' ? <AlertTriangle className="h-5 w-5" /> :
                                 insight.type === 'suggestion' ? <MessageCircle className="h-5 w-5" /> :
                                 <Info className="h-5 w-5" />}
                              </div>
                              <div>
                                <h4 className="font-medium">{insight.title}</h4>
                                <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </CardContent>
          </TabContent>
          
          {/* Skills Analysis Tab */}
          <TabContent value="skills">
            <CardContent className="pt-6">
              <div className="mb-6 flex justify-between items-center">
                <h3 className="text-lg font-medium">Skills Breakdown</h3>
                
                <select
                  value={skillsFilter}
                  onChange={(e) => handleSkillsFilterChange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="all">All Skills</option>
                  <option value="language">Language</option>
                  <option value="mathematics">Mathematics</option>
                  <option value="science">Science</option>
                  <option value="social">Social</option>
                  <option value="technical">Technical</option>
                </select>
              </div>
              
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading skills data...</p>
                </div>
              ) : skillsData.length === 0 ? (
                <div className="text-center py-8 border rounded-md">
                  <Award className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No skills data available</h4>
                  <p className="text-gray-400 text-sm mt-1">This beneficiary hasn't been evaluated on any skills yet.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Skills Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Skills Comparison</CardTitle>
                      <CardDescription>
                        Current vs previous evaluation scores for each skill
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-80">
                        <canvas ref={skillsChartRef}></canvas>
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Skills Detail */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {skillsData.map((skill) => (
                      <Card key={skill.id}>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div className="flex items-center gap-3">
                              <div className={`rounded-full p-2 ${
                                skill.category === 'language' ? 'bg-blue-100 text-blue-600' :
                                skill.category === 'mathematics' ? 'bg-green-100 text-green-600' :
                                skill.category === 'science' ? 'bg-purple-100 text-purple-600' :
                                skill.category === 'social' ? 'bg-yellow-100 text-yellow-600' :
                                skill.category === 'technical' ? 'bg-gray-100 text-gray-600' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                <Award className="h-5 w-5" />
                              </div>
                              <div>
                                <h4 className="font-medium">{skill.name}</h4>
                                <Badge className="mt-1">{skill.category}</Badge>
                              </div>
                            </div>
                            
                            <div className="text-right">
                              <span className="text-sm font-medium">{skill.current_score}%</span>
                              <div className="text-xs text-gray-500">
                                {skill.change_percentage > 0 && '+'}{skill.change_percentage}% change
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-3">
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div 
                                className={`h-2.5 rounded-full ${
                                  skill.current_score >= 70 ? 'bg-green-600' :
                                  skill.current_score >= 40 ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`}
                                style={{ width: `${skill.current_score}%` }}
                              ></div>
                            </div>
                          </div>
                          
                          <div className="mt-3 text-sm">
                            <p className="text-gray-600">
                              {skill.description || `Proficiency level in ${skill.name}.`}
                            </p>
                            {skill.last_evaluated_at && (
                              <p className="text-gray-500 mt-1">
                                Last evaluated: {formatDate(skill.last_evaluated_at)}
                              </p>
                            )}
                          </div>
                          
                          {skill.recommendation && (
                            <div className="mt-3 p-2 bg-blue-50 rounded-md text-sm text-blue-700">
                              <strong>Recommendation:</strong> {skill.recommendation}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </TabContent>
          
          {/* Session Analytics Tab */}
          <TabContent value="sessions">
            <CardContent className="pt-6">
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading session data...</p>
                </div>
              ) : !sessionsData.summary ? (
                <div className="text-center py-8 border rounded-md">
                  <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No session data available</h4>
                  <p className="text-gray-400 text-sm mt-1">This beneficiary hasn't participated in any sessions yet.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Session Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Total Sessions</p>
                            <p className="text-2xl font-bold">{sessionsData.summary.total_sessions}</p>
                          </div>
                          <div className="rounded-full bg-gray-100 p-3">
                            <Calendar className="h-5 w-5 text-gray-600" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Attendance Rate</p>
                            <p className="text-2xl font-bold">{sessionsData.summary.attendance_rate}%</p>
                          </div>
                          <div className="rounded-full bg-green-100 p-3">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Hours Completed</p>
                            <p className="text-2xl font-bold">{sessionsData.summary.total_hours}</p>
                          </div>
                          <div className="rounded-full bg-blue-100 p-3">
                            <Clock className="h-5 w-5 text-blue-600" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Upcoming Sessions</p>
                            <p className="text-2xl font-bold">{sessionsData.summary.upcoming_sessions}</p>
                          </div>
                          <div className="rounded-full bg-purple-100 p-3">
                            <Calendar className="h-5 w-5 text-purple-600" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {/* Attendance Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Session Attendance</CardTitle>
                      <CardDescription>
                        Attended vs missed sessions over time
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-80">
                        <canvas ref={sessionsChartRef}></canvas>
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Session Details */}
                  {sessionsData.session_details && sessionsData.session_details.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Session Details</CardTitle>
                        <CardDescription>
                          Recent sessions and outcomes
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {sessionsData.session_details.map((session) => (
                            <div key={session.id} className="flex items-start gap-4 pb-4 border-b last:border-b-0">
                              <div className="flex-shrink-0 w-12 text-center">
                                <div className="text-xs font-medium text-gray-500">
                                  {formatDate(session.date).split(' ')[0]}
                                </div>
                                <div className="text-sm font-medium">
                                  {formatDate(session.date).split(' ')[1]}
                                </div>
                              </div>
                              
                              <div className="flex-1">
                                <div className="flex justify-between items-start">
                                  <div>
                                    <h4 className="font-medium">{session.title}</h4>
                                    <p className="text-sm text-gray-500">
                                      {session.trainer_name} • {session.duration} minutes
                                    </p>
                                  </div>
                                  <Badge color={
                                    session.status === 'completed' ? 'green' :
                                    session.status === 'missed' ? 'red' :
                                    session.status === 'upcoming' ? 'blue' : 'gray'
                                  }>
                                    {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                                  </Badge>
                                </div>
                                
                                {session.notes && (
                                  <div className="mt-2 text-sm text-gray-600">
                                    <p>{session.notes}</p>
                                  </div>
                                )}
                                
                                {session.skills?.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-gray-500">Skills covered:</p>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {session.skills.map((skill, idx) => (
                                        <Badge key={idx} variant="outline" className="text-xs">{skill}</Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                      <CardFooter className="border-t pt-4">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="ml-auto"
                          onClick={() => navigate(`/sessions?beneficiary=${id}`)}
                        >
                          View All Sessions
                        </Button>
                      </CardFooter>
                    </Card>
                  )}
                </div>
              )}
            </CardContent>
          </TabContent>
          
          {/* Peer Comparison Tab */}
          <TabContent value="comparison">
            <CardContent className="pt-6">
              {isTabLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading comparison data...</p>
                </div>
              ) : !comparisonData.skill_comparison ? (
                <div className="text-center py-8 border rounded-md">
                  <TrendingUp className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-500">No comparison data available</h4>
                  <p className="text-gray-400 text-sm mt-1">Insufficient data to generate peer comparisons.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Info Alert */}
                  <Alert type="info" title="About Peer Comparison">
                    <p>Peer comparisons help contextualize progress against similar beneficiaries. All data is anonymized.</p>
                  </Alert>
                  
                  {/* Comparison Radar Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Skill Comparison</CardTitle>
                      <CardDescription>
                        Comparison of skills against peers in similar program
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-96">
                        <canvas ref={comparisonChartRef}></canvas>
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Percentile Ranks */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Percentile Ranks</CardTitle>
                      <CardDescription>
                        How this beneficiary ranks compared to peers
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {comparisonData.percentile_ranks?.map((item) => (
                          <div key={item.category} className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{item.category}</span>
                              <span className="text-sm">{item.percentile}th percentile</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div 
                                className={`h-2.5 rounded-full ${
                                  item.percentile >= 75 ? 'bg-green-600' :
                                  item.percentile >= 50 ? 'bg-blue-600' :
                                  item.percentile >= 25 ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`}
                                style={{ width: `${item.percentile}%` }}
                              ></div>
                            </div>
                            <p className="text-xs text-gray-500">{item.description}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Group Comparison */}
                  {comparisonData.group_comparison && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Group Comparison</CardTitle>
                        <CardDescription>
                          How this beneficiary compares to different groups
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {comparisonData.group_comparison.map((group) => (
                            <Card key={group.group_name}>
                              <CardContent className="p-4">
                                <h4 className="font-medium">{group.group_name}</h4>
                                <div className="mt-2 flex justify-between items-center">
                                  <span className="text-sm text-gray-500">Average Score</span>
                                  <span className="font-medium">{group.group_average}%</span>
                                </div>
                                <div className="mt-1 flex justify-between items-center">
                                  <span className="text-sm text-gray-500">{beneficiary.first_name}'s Score</span>
                                  <span className="font-medium">{group.beneficiary_score}%</span>
                                </div>
                                <div className="mt-2 text-sm">
                                  <span className={`font-medium ${
                                    group.difference > 0 ? 'text-green-600' : 
                                    group.difference < 0 ? 'text-red-600' : 
                                    'text-gray-600'
                                  }`}>
                                    {group.difference > 0 ? '+' : ''}{group.difference}%
                                  </span>
                                  <span className="text-gray-500 ml-1">difference</span>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </CardContent>
          </TabContent>
        </Tabs>
      </Card>
      
      {/* Report Export Modal */}
      <Modal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
      >
        <ModalHeader>
          <h3 className="text-lg font-medium">Export Progress Report</h3>
        </ModalHeader>
        
        <ModalBody>
          <p className="text-gray-600 mb-4">
            Choose a format to export the progress report for {beneficiary.first_name} {beneficiary.last_name}.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card 
              className="cursor-pointer hover:border-primary"
              onClick={() => generateReport('pdf')}
            >
              <CardContent className="p-4 text-center">
                <FileText className="h-12 w-12 mx-auto mb-2 text-red-600" />
                <h4 className="font-medium">PDF Format</h4>
                <p className="text-sm text-gray-500">
                  Printable document with all progress data.
                </p>
              </CardContent>
            </Card>
            
            <Card 
              className="cursor-pointer hover:border-primary"
              onClick={() => generateReport('excel')}
            >
              <CardContent className="p-4 text-center">
                <FileText className="h-12 w-12 mx-auto mb-2 text-green-600" />
                <h4 className="font-medium">Excel Format</h4>
                <p className="text-sm text-gray-500">
                  Spreadsheet with detailed data for analysis.
                </p>
              </CardContent>
            </Card>
          </div>
          
          <div className="mt-4 flex gap-2 text-gray-500 text-sm">
            <HelpCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <p>
              Reports include progress data, skills analysis, session records, and peer comparisons
              for the selected date range.
            </p>
          </div>
        </ModalBody>
        
        <ModalFooter>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setIsReportModalOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              variant="outline"
              disabled={isLoading}
              onClick={() => window.print()}
            >
              <Printer className="h-4 w-4 mr-2" />
              Print View
            </Button>
            <Button
              variant="outline"
              disabled={isLoading}
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </ModalFooter>
      </Modal>
    </div>
  );
};

export default ProgressTrackingPage;