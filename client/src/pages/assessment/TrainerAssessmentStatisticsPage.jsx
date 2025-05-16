import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart2, TrendingUp, Users, Award, Clock, 
  FileText, Filter, Download, Calendar, Brain
} from 'lucide-react';
import { format, subDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth } from 'date-fns';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { DatePicker } from '@/components/ui/date-picker';
import { Tabs } from '@/components/ui/tabs';
import { Table } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

/**
 * TrainerAssessmentStatisticsPage provides comprehensive analytics and reporting
 * for assessments across the organization
 */
const TrainerAssessmentStatisticsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Date range filter
  const [dateRange, setDateRange] = useState('30');
  const [startDate, setStartDate] = useState(subDays(new Date(), 30));
  const [endDate, setEndDate] = useState(new Date());
  
  // Filters
  const [filters, setFilters] = useState({
    assessmentType: 'all',
    courseId: 'all',
    trainerId: 'all',
    status: 'all'
  });
  
  // Statistics data
  const [overviewStats, setOverviewStats] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  const [completionData, setCompletionData] = useState(null);
  const [assessmentStats, setAssessmentStats] = useState(null);
  const [studentStats, setStudentStats] = useState(null);
  const [questionStats, setQuestionStats] = useState(null);
  
  // Load statistics data
  useEffect(() => {
    let isMounted = true;
    
    const fetchStatistics = async () => {
      try {
        if (!isMounted) return;
        
        setIsLoading(true);
        setError(null);
        
        // Fetch overview statistics
        const overviewResponse = await fetch(`/api/assessment/statistics/overview?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
        if (!isMounted) return;
        
        if (!overviewResponse.ok) throw new Error('Failed to fetch overview statistics');
        const overviewData = await overviewResponse.json();
        
        if (!isMounted) return;
        setOverviewStats(overviewData);
        
        // Fetch performance data
        const performanceResponse = await fetch(`/api/assessment/statistics/performance?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
        if (!isMounted) return;
        
        if (!performanceResponse.ok) throw new Error('Failed to fetch performance data');
        const performanceData = await performanceResponse.json();
        
        if (!isMounted) return;
        setPerformanceData(performanceData);
        
        // Fetch completion data
        const completionResponse = await fetch(`/api/assessment/statistics/completion?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
        if (!isMounted) return;
        
        if (!completionResponse.ok) throw new Error('Failed to fetch completion data');
        const completionData = await completionResponse.json();
        
        if (!isMounted) return;
        setCompletionData(completionData);
        
        // Fetch assessment statistics
        const assessmentResponse = await fetch(`/api/assessment/statistics/assessments?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
        if (!isMounted) return;
        
        if (!assessmentResponse.ok) throw new Error('Failed to fetch assessment statistics');
        const assessmentData = await assessmentResponse.json();
        
        if (!isMounted) return;
        setAssessmentStats(assessmentData);
        
        // Fetch student statistics
        const studentResponse = await fetch(`/api/assessment/statistics/students?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
        if (!isMounted) return;
        
        if (!studentResponse.ok) throw new Error('Failed to fetch student statistics');
        const studentData = await studentResponse.json();
        
        if (!isMounted) return;
        setStudentStats(studentData);
        
        // Fetch question statistics
        const questionResponse = await fetch(`/api/assessment/statistics/questions?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
        if (!isMounted) return;
        
        if (!questionResponse.ok) throw new Error('Failed to fetch question statistics');
        const questionData = await questionResponse.json();
        
        if (!isMounted) return;
        setQuestionStats(questionData);
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Error fetching statistics:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load assessment statistics',
          type: 'error',
        });
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    
    fetchStatistics();
    
    return () => {
      isMounted = false;
    };
  }, [startDate, endDate, filters, toast]);
  
  // Handle date range change
  const handleDateRangeChange = (range) => {
    setDateRange(range);
    const now = new Date();
    
    switch (range) {
      case '7':
        setStartDate(subDays(now, 7));
        setEndDate(now);
        break;
      case '30':
        setStartDate(subDays(now, 30));
        setEndDate(now);
        break;
      case '90':
        setStartDate(subDays(now, 90));
        setEndDate(now);
        break;
      case 'week':
        setStartDate(startOfWeek(now));
        setEndDate(endOfWeek(now));
        break;
      case 'month':
        setStartDate(startOfMonth(now));
        setEndDate(endOfMonth(now));
        break;
      case 'custom':
        // Custom dates handled separately
        break;
      default:
        setStartDate(subDays(now, 30));
        setEndDate(now);
    }
  };
  
  // Export report
  const handleExportReport = () => {
    // In a real app, this would generate and download a report
    toast({
      title: 'Report Export',
      description: 'Generating assessment statistics report...',
      type: 'info',
    });
  };
  
  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <h2 className="text-xl font-semibold mb-2">Unable to Load Statistics</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </Card>
      </div>
    );
  }
  
  // Chart colors
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
  
  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">Assessment Statistics</h1>
          <p className="text-gray-600">Comprehensive analytics and reporting</p>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleExportReport}
            className="flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>
      
      {/* Date Range Filter */}
      <Card className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <Select
              value={dateRange}
              onValueChange={handleDateRangeChange}
              className="w-40"
            >
              <Select.Option value="7">Last 7 days</Select.Option>
              <Select.Option value="30">Last 30 days</Select.Option>
              <Select.Option value="90">Last 90 days</Select.Option>
              <Select.Option value="week">This week</Select.Option>
              <Select.Option value="month">This month</Select.Option>
              <Select.Option value="custom">Custom range</Select.Option>
            </Select>
          </div>
          
          {dateRange === 'custom' && (
            <div className="flex items-center gap-2">
              <DatePicker
                value={startDate}
                onChange={setStartDate}
                placeholder="Start date"
              />
              <span>to</span>
              <DatePicker
                value={endDate}
                onChange={setEndDate}
                placeholder="End date"
              />
            </div>
          )}
          
          <div className="flex-1"></div>
          
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <Select
              value={filters.assessmentType}
              onValueChange={(value) => setFilters({ ...filters, assessmentType: value })}
              className="w-32"
            >
              <Select.Option value="all">All Types</Select.Option>
              <Select.Option value="quiz">Quiz</Select.Option>
              <Select.Option value="project">Project</Select.Option>
            </Select>
          </div>
        </div>
      </Card>
      
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <FileText className="w-8 h-8 text-primary" />
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
          <h3 className="text-sm text-gray-600 mb-1">Total Assessments</h3>
          <p className="text-2xl font-bold">{overviewStats?.totalAssessments || 0}</p>
          <p className="text-sm text-green-600 mt-2">+12% from last period</p>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Users className="w-8 h-8 text-primary" />
            <TrendingUp className="w-5 h-5 text-green-500" />
          </div>
          <h3 className="text-sm text-gray-600 mb-1">Active Students</h3>
          <p className="text-2xl font-bold">{overviewStats?.activeStudents || 0}</p>
          <p className="text-sm text-green-600 mt-2">+8% from last period</p>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Award className="w-8 h-8 text-primary" />
            <span className="text-lg font-bold text-blue-600">
              {overviewStats?.averageScore || 0}%
            </span>
          </div>
          <h3 className="text-sm text-gray-600 mb-1">Average Score</h3>
          <Progress value={overviewStats?.averageScore || 0} className="h-2" />
          <p className="text-sm text-blue-600 mt-2">Above target by 5%</p>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Clock className="w-8 h-8 text-primary" />
            <span className="text-lg font-bold">
              {overviewStats?.completionRate || 0}%
            </span>
          </div>
          <h3 className="text-sm text-gray-600 mb-1">Completion Rate</h3>
          <Progress value={overviewStats?.completionRate || 0} className="h-2" />
          <p className="text-sm text-amber-600 mt-2">Target: 85%</p>
        </Card>
      </div>
      
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList className="mb-6">
          <Tabs.TabTrigger value="overview">
            <BarChart2 className="w-4 h-4 mr-2" />
            Overview
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="performance">
            <TrendingUp className="w-4 h-4 mr-2" />
            Performance
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="assessments">
            <FileText className="w-4 h-4 mr-2" />
            Assessments
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="students">
            <Users className="w-4 h-4 mr-2" />
            Students
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="insights">
            <Brain className="w-4 h-4 mr-2" />
            Insights
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        
        {/* Overview Tab */}
        <Tabs.TabContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Completion Trends */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Completion Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={completionData?.trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="completed" stroke="#10B981" name="Completed" />
                  <Line type="monotone" dataKey="pending" stroke="#F59E0B" name="Pending" />
                  <Line type="monotone" dataKey="overdue" stroke="#EF4444" name="Overdue" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
            
            {/* Assessment Type Distribution */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Assessment Type Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={assessmentStats?.typeDistribution || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {(assessmentStats?.typeDistribution || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
            
            {/* Score Distribution */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Score Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData?.scoreDistribution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            
            {/* Time to Complete */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Average Time to Complete</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData?.timeToComplete || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="minutes" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </Tabs.TabContent>
        
        {/* Performance Tab */}
        <Tabs.TabContent value="performance">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance by Course */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performance by Course</h3>
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Course</Table.HeaderCell>
                    <Table.HeaderCell>Assessments</Table.HeaderCell>
                    <Table.HeaderCell>Avg Score</Table.HeaderCell>
                    <Table.HeaderCell>Pass Rate</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {performanceData?.byCourse?.map(course => (
                    <Table.Row key={course.id}>
                      <Table.Cell>{course.name}</Table.Cell>
                      <Table.Cell>{course.assessmentCount}</Table.Cell>
                      <Table.Cell>
                        <span className="font-medium">{course.averageScore}%</span>
                      </Table.Cell>
                      <Table.Cell>
                        <Badge className={course.passRate >= 80 ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}>
                          {course.passRate}%
                        </Badge>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Card>
            
            {/* Performance by Trainer */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performance by Trainer</h3>
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Trainer</Table.HeaderCell>
                    <Table.HeaderCell>Students</Table.HeaderCell>
                    <Table.HeaderCell>Avg Score</Table.HeaderCell>
                    <Table.HeaderCell>Completion</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {performanceData?.byTrainer?.map(trainer => (
                    <Table.Row key={trainer.id}>
                      <Table.Cell>{trainer.name}</Table.Cell>
                      <Table.Cell>{trainer.studentCount}</Table.Cell>
                      <Table.Cell>
                        <span className="font-medium">{trainer.averageScore}%</span>
                      </Table.Cell>
                      <Table.Cell>
                        <Progress value={trainer.completionRate} className="h-2" />
                        <span className="text-sm">{trainer.completionRate}%</span>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Card>
            
            {/* Pass Rate Trends */}
            <Card className="p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Pass Rate Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData?.passRateTrends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="quiz" stroke="#3B82F6" name="Quiz" />
                  <Line type="monotone" dataKey="project" stroke="#8B5CF6" name="Project" />
                  <Line type="monotone" dataKey="overall" stroke="#10B981" name="Overall" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </Tabs.TabContent>
        
        {/* Assessments Tab */}
        <Tabs.TabContent value="assessments">
          <div className="space-y-6">
            {/* Top Assessments */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Top Performing Assessments</h3>
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Assessment</Table.HeaderCell>
                    <Table.HeaderCell>Type</Table.HeaderCell>
                    <Table.HeaderCell>Completions</Table.HeaderCell>
                    <Table.HeaderCell>Avg Score</Table.HeaderCell>
                    <Table.HeaderCell>Pass Rate</Table.HeaderCell>
                    <Table.HeaderCell>Actions</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {assessmentStats?.topAssessments?.map(assessment => (
                    <Table.Row key={assessment.id}>
                      <Table.Cell>{assessment.title}</Table.Cell>
                      <Table.Cell>
                        <Badge className={assessment.type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                          {assessment.type}
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>{assessment.completions}</Table.Cell>
                      <Table.Cell>
                        <span className="font-medium">{assessment.averageScore}%</span>
                      </Table.Cell>
                      <Table.Cell>
                        <Badge className={assessment.passRate >= 80 ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}>
                          {assessment.passRate}%
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/assessment/templates/${assessment.id}`)}
                        >
                          View
                        </Button>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Card>
            
            {/* Most Challenging Questions */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Most Challenging Questions</h3>
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Question</Table.HeaderCell>
                    <Table.HeaderCell>Assessment</Table.HeaderCell>
                    <Table.HeaderCell>Attempts</Table.HeaderCell>
                    <Table.HeaderCell>Success Rate</Table.HeaderCell>
                    <Table.HeaderCell>Avg Time</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {questionStats?.mostChallenging?.map(question => (
                    <Table.Row key={question.id}>
                      <Table.Cell className="max-w-xs truncate">{question.text}</Table.Cell>
                      <Table.Cell>{question.assessmentTitle}</Table.Cell>
                      <Table.Cell>{question.attempts}</Table.Cell>
                      <Table.Cell>
                        <Badge className={question.successRate < 50 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}>
                          {question.successRate}%
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>{question.avgTime}s</Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Card>
          </div>
        </Tabs.TabContent>
        
        {/* Students Tab */}
        <Tabs.TabContent value="students">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Students */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Top Performing Students</h3>
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Student</Table.HeaderCell>
                    <Table.HeaderCell>Assessments</Table.HeaderCell>
                    <Table.HeaderCell>Avg Score</Table.HeaderCell>
                    <Table.HeaderCell>Badges</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {studentStats?.topStudents?.map(student => (
                    <Table.Row key={student.id}>
                      <Table.Cell>
                        <div>
                          <p className="font-medium">{student.name}</p>
                          <p className="text-sm text-gray-600">{student.email}</p>
                        </div>
                      </Table.Cell>
                      <Table.Cell>{student.assessmentCount}</Table.Cell>
                      <Table.Cell>
                        <span className="font-medium">{student.averageScore}%</span>
                      </Table.Cell>
                      <Table.Cell>
                        <div className="flex gap-1">
                          {student.badges?.map((badge, index) => (
                            <Award key={index} className="w-5 h-5 text-yellow-500" />
                          ))}
                        </div>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Card>
            
            {/* Students Needing Support */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Students Needing Support</h3>
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Student</Table.HeaderCell>
                    <Table.HeaderCell>Failed</Table.HeaderCell>
                    <Table.HeaderCell>Avg Score</Table.HeaderCell>
                    <Table.HeaderCell>Actions</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {studentStats?.needingSupport?.map(student => (
                    <Table.Row key={student.id}>
                      <Table.Cell>
                        <div>
                          <p className="font-medium">{student.name}</p>
                          <p className="text-sm text-gray-600">{student.email}</p>
                        </div>
                      </Table.Cell>
                      <Table.Cell>
                        <Badge className="bg-red-100 text-red-800">
                          {student.failedCount}
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>
                        <span className="font-medium text-red-600">{student.averageScore}%</span>
                      </Table.Cell>
                      <Table.Cell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate('/messaging')}
                        >
                          Contact
                        </Button>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            </Card>
            
            {/* Engagement Metrics */}
            <Card className="p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Student Engagement Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={studentStats?.engagementTrends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="active" stroke="#10B981" name="Active Students" />
                  <Line type="monotone" dataKey="inactive" stroke="#EF4444" name="Inactive Students" />
                  <Line type="monotone" dataKey="new" stroke="#3B82F6" name="New Students" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </Tabs.TabContent>
        
        {/* Insights Tab */}
        <Tabs.TabContent value="insights">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* AI-Generated Insights */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                <Brain className="w-5 h-5 inline mr-2 text-primary" />
                AI-Generated Insights
              </h3>
              
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Trending Upward</h4>
                  <p className="text-sm text-blue-700">
                    Quiz completion rates have increased by 15% in the past week, 
                    particularly in the Python programming course.
                  </p>
                </div>
                
                <div className="p-4 bg-amber-50 rounded-lg">
                  <h4 className="font-medium text-amber-800 mb-2">Attention Needed</h4>
                  <p className="text-sm text-amber-700">
                    The JavaScript project assessment has a 40% failure rate. 
                    Consider reviewing the difficulty level or providing additional resources.
                  </p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Success Story</h4>
                  <p className="text-sm text-green-700">
                    Students who complete practice quizzes score 25% higher on final assessments.
                  </p>
                </div>
                
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-medium text-purple-800 mb-2">Recommendation</h4>
                  <p className="text-sm text-purple-700">
                    Creating more intermediate-level assessments could help bridge the gap 
                    between beginner and advanced content.
                  </p>
                </div>
              </div>
            </Card>
            
            {/* Predictive Analytics */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Predictive Analytics</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-medium mb-3">Likely to Succeed</h4>
                  <div className="space-y-2">
                    {[
                      { name: 'Sarah Johnson', probability: 92 },
                      { name: 'Mike Chen', probability: 88 },
                      { name: 'Emily Davis', probability: 85 }
                    ].map(student => (
                      <div key={student.name} className="flex items-center justify-between">
                        <span className="text-sm">{student.name}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={student.probability} className="w-24 h-2" />
                          <span className="text-sm font-medium">{student.probability}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-3">At Risk</h4>
                  <div className="space-y-2">
                    {[
                      { name: 'John Smith', probability: 35 },
                      { name: 'Lisa Brown', probability: 42 },
                      { name: 'David Wilson', probability: 48 }
                    ].map(student => (
                      <div key={student.name} className="flex items-center justify-between">
                        <span className="text-sm">{student.name}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={student.probability} className="w-24 h-2" />
                          <span className="text-sm font-medium text-red-600">{student.probability}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
            
            {/* Recommendations */}
            <Card className="p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Actionable Recommendations</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-blue-600 font-bold">1</span>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">Increase Practice Opportunities</h4>
                      <p className="text-sm text-gray-600">
                        Add more practice assessments for courses with high failure rates.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-green-600 font-bold">2</span>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">Implement Peer Review</h4>
                      <p className="text-sm text-gray-600">
                        Enable peer review for project assessments to improve engagement.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-purple-600 font-bold">3</span>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">Adaptive Difficulty</h4>
                      <p className="text-sm text-gray-600">
                        Consider implementing adaptive assessments based on student performance.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-amber-600 font-bold">4</span>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">Schedule Optimization</h4>
                      <p className="text-sm text-gray-600">
                        Spread assessment due dates to avoid student overload periods.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};

export default TrainerAssessmentStatisticsPage;