import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Users,
  ClipboardList,
  FileText,
  Calendar,
  ArrowUpRight,
  Activity,
  Clock,
  CheckCircle2,
  ArrowRight,
  BookOpen,
  TrendingUp,
  Award,
  Loader,
  BarChart,
  Target,
  AlertCircle
} from 'lucide-react';

/**
 * Dashboard page component - shows different content based on user role
 */
const DashboardPageV2 = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [recentTests, setRecentTests] = useState([]);
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [chartData, setChartData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!user) return;
      
      try {
        setIsLoading(true);
        
        // Get dashboard analytics
        const analyticsResponse = await api.get(API_ENDPOINTS.ANALYTICS.DASHBOARD, {
          params: { range: '7days' }
        });
        setStats(analyticsResponse.data.statistics || {});
        setChartData(analyticsResponse.data.charts || {});
        
        // Get recent reports
        const reportsResponse = await api.get(API_ENDPOINTS.REPORTS.RECENT);
        setRecentReports(reportsResponse.data || []);
        
        // Get upcoming events
        const eventsResponse = await api.get('/api/calendar/events', {
          params: {
            start: new Date().toISOString().split('T')[0],
            end: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          }
        });
        setUpcomingEvents(eventsResponse.data.events || []);
        
        // Get programs
        const programsResponse = await api.get('/api/programs');
        setPrograms(programsResponse.data || []);
        
        // Get recent tests
        const testsResponse = await api.get('/api/tests', {
          params: { per_page: 5 }
        });
        setRecentTests(testsResponse.data.tests || []);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [user]);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }
  
  // Render dashboard based on user role
  if (user?.role === 'super_admin' || user?.role === 'tenant_admin') {
    return <AdminDashboard stats={stats} chartData={chartData} recentReports={recentReports} />;
  } else if (user?.role === 'trainer') {
    return <TrainerDashboard stats={stats} upcomingEvents={upcomingEvents} recentTests={recentTests} />;
  } else {
    return <StudentDashboard stats={stats} programs={programs} upcomingEvents={upcomingEvents} />;
  }
};

// Admin Dashboard Component
const AdminDashboard = ({ stats, chartData, recentReports }) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor your organization's performance and activities
        </p>
      </div>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Users"
          value={stats.total_users || 0}
          change={stats.user_growth || '0%'}
          trend="up"
          icon={<Users className="w-6 h-6" />}
          linkTo="/admin/users"
        />
        <StatsCard
          title="Active Beneficiaries"
          value={stats.total_beneficiaries || 0}
          change={stats.beneficiary_growth || '0%'}
          trend="up"
          icon={<Target className="w-6 h-6" />}
          linkTo="/beneficiaries"
        />
        <StatsCard
          title="Total Trainers"
          value={stats.total_trainers || 0}
          icon={<BookOpen className="w-6 h-6" />}
          linkTo="/admin/users?role=trainer"
        />
        <StatsCard
          title="Active Programs"
          value={stats.active_programs || 0}
          icon={<ClipboardList className="w-6 h-6" />}
          linkTo="/programs"
        />
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* User growth chart */}
        <Card className="p-6">
          <h3 className="text-lg font-medium mb-4">User Growth</h3>
          <div className="h-64 bg-gray-50 rounded flex items-center justify-center">
            <BarChart className="w-12 h-12 text-gray-400" />
            <span className="ml-2 text-gray-500">Chart coming soon</span>
          </div>
        </Card>
        
        {/* Recent reports */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium">Recent Reports</h3>
            <Link to="/reports" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {recentReports.slice(0, 5).map((report) => (
              <div key={report.id} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium">{report.name}</p>
                    <p className="text-xs text-gray-500">{report.type}</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => window.open(`/api/reports/${report.id}/download`)}
                >
                  Download
                </Button>
              </div>
            ))}
          </div>
        </Card>
      </div>
      
      {/* Activity summary */}
      <Card className="p-6">
        <h3 className="text-lg font-medium mb-4">Weekly Activity Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">
              {stats.recent_activity?.new_users_week || 0}
            </div>
            <p className="text-sm text-gray-500 mt-1">New Users</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {stats.recent_activity?.evaluations_completed_week || 0}
            </div>
            <p className="text-sm text-gray-500 mt-1">Evaluations Completed</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {stats.recent_activity?.new_beneficiaries_week || 0}
            </div>
            <p className="text-sm text-gray-500 mt-1">New Beneficiaries</p>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Trainer Dashboard Component
const TrainerDashboard = ({ stats, upcomingEvents, recentTests }) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trainer Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your beneficiaries and track their progress
        </p>
      </div>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Assigned Beneficiaries"
          value={stats.assigned_beneficiaries || 0}
          icon={<Users className="w-6 h-6" />}
          linkTo="/beneficiaries"
        />
        <StatsCard
          title="Upcoming Sessions"
          value={stats.upcoming_sessions || 0}
          icon={<Calendar className="w-6 h-6" />}
          linkTo="/calendar"
        />
        <StatsCard
          title="Completed Evaluations"
          value={stats.completed_evaluations || 0}
          icon={<CheckCircle2 className="w-6 h-6" />}
          linkTo="/evaluations"
        />
        <StatsCard
          title="Total Sessions"
          value={stats.total_sessions || 0}
          icon={<Activity className="w-6 h-6" />}
          linkTo="/sessions"
        />
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Upcoming events */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium">Upcoming Events</h3>
            <Link to="/calendar" className="text-sm text-primary hover:underline">
              View calendar
            </Link>
          </div>
          <div className="space-y-3">
            {upcomingEvents.slice(0, 5).map((event) => (
              <div key={event.id} className="flex items-start space-x-3">
                <div className="p-2 bg-primary-50 rounded-lg">
                  <Calendar className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{event.title}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(event.start).toLocaleDateString()} at{' '}
                    {new Date(event.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  {event.beneficiary && (
                    <p className="text-xs text-gray-500">
                      With {event.beneficiary.name}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
        
        {/* Recent tests */}
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium">Recent Tests</h3>
            <Link to="/evaluations" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {recentTests.map((test) => (
              <div key={test.id} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">{test.title}</p>
                  <p className="text-xs text-gray-500">{test.category}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  test.status === 'active' 
                    ? 'bg-green-100 text-green-800'
                    : test.status === 'draft'
                    ? 'bg-gray-100 text-gray-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {test.status}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

// Student Dashboard Component
const StudentDashboard = ({ stats, programs, upcomingEvents }) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Track your progress and upcoming activities
        </p>
      </div>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Completed Tests"
          value={stats.completed_tests || 0}
          icon={<CheckCircle2 className="w-6 h-6" />}
          linkTo="/my-tests"
        />
        <StatsCard
          title="Average Score"
          value={`${stats.average_score || 0}%`}
          icon={<TrendingUp className="w-6 h-6" />}
        />
        <StatsCard
          title="Upcoming Sessions"
          value={stats.upcoming_sessions || 0}
          icon={<Calendar className="w-6 h-6" />}
          linkTo="/my-schedule"
        />
        <StatsCard
          title="Certificates Earned"
          value={stats.certificates_earned || 0}
          icon={<Award className="w-6 h-6" />}
          linkTo="/my-certificates"
        />
      </div>
      
      {/* Enrolled programs */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">My Programs</h3>
          <Link to="/programs" className="text-sm text-primary hover:underline">
            Browse all
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {programs.slice(0, 4).map((program) => (
            <div key={program.id} className="border rounded-lg p-4">
              <h4 className="font-medium">{program.name}</h4>
              <p className="text-sm text-gray-500 mt-1">{program.category}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-sm text-gray-500">{program.duration} days</span>
                <Button size="sm" variant="outline">
                  Continue
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
      
      {/* Upcoming events */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Upcoming Events</h3>
          <Link to="/calendar" className="text-sm text-primary hover:underline">
            View calendar
          </Link>
        </div>
        <div className="space-y-3">
          {upcomingEvents.slice(0, 5).map((event) => (
            <div key={event.id} className="flex items-start space-x-3">
              <div className="p-2 bg-primary-50 rounded-lg">
                <Calendar className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{event.title}</p>
                <p className="text-xs text-gray-500">
                  {new Date(event.start).toLocaleDateString()} at{' '}
                  {new Date(event.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
                {event.location && (
                  <p className="text-xs text-gray-500">{event.location}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

// Stats Card Component
const StatsCard = ({ title, value, change, trend, icon, linkTo }) => {
  const content = (
    <div className="p-5 bg-white rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-1 text-3xl font-semibold text-gray-900">{value}</p>
          {change && (
            <p className={`mt-1 text-sm ${
              trend === 'up' ? 'text-green-600' : 'text-red-600'
            }`}>
              {trend === 'up' ? '+' : '-'}{change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full ${
          linkTo ? 'bg-primary-50' : 'bg-gray-50'
        }`}>
          <div className={linkTo ? 'text-primary' : 'text-gray-400'}>
            {icon}
          </div>
        </div>
      </div>
    </div>
  );
  
  if (linkTo) {
    return (
      <Link to={linkTo} className="group">
        <div className="relative">
          {content}
          <ArrowUpRight className="absolute top-2 right-2 w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </Link>
    );
  }
  
  return content;
};

export default DashboardPageV2;