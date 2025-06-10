import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ResponsiveContainer as ResponsiveLayout, ResponsiveGrid, ResponsiveCard } from '@/components/responsive/ResponsiveContainer';
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
  Loader2,
  UserCheck,
  Target,
  GraduationCap
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
const DashboardPageV3 = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [chartData, setChartData] = useState({});
  const [recentTests, setRecentTests] = useState([]);
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7days');
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        // Get dashboard analytics with time range
        const analyticsResponse = await api.get(API_ENDPOINTS.ANALYTICS.DASHBOARD, {
          params: { range: timeRange }
        });
        const data = analyticsResponse.data;
        setStats(data.statistics || {});
        setChartData(data.charts || {});
        // Get recent reports
        try {
          const reportsResponse = await api.get(API_ENDPOINTS.REPORTS.RECENT);
          setRecentReports(reportsResponse.data.reports || []);
        } catch (error) {
          console.error('Error fetching reports:', error);
        }
        // Get upcoming appointments
        try {
          const appointmentsResponse = await api.get('/api/appointments', {
            params: {
              start_date: new Date().toISOString().split('T')[0],
              end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
              status: 'scheduled'
            }
          });
          setUpcomingAppointments(appointmentsResponse.data.appointments || []);
        } catch (error) {
          console.error('Error fetching appointments:', error);
        }
        // Get recent tests
        try {
          const testsResponse = await api.get('/api/tests/sessions', {
            params: { 
              per_page: 5,
              sort: 'created_at',
              order: 'desc'
            }
          });
          setRecentTests(testsResponse.data.sessions || []);
        } catch (error) {
          console.error('Error fetching tests:', error);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, [user, timeRange]);
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }
  // Render different content based on role
  if (user?.role === 'super_admin' || user?.role === 'tenant_admin') {
    return <AdminDashboard stats={stats} chartData={chartData} timeRange={timeRange} setTimeRange={setTimeRange} />;
  } else if (user?.role === 'trainer') {
    return <TrainerDashboard stats={stats} chartData={chartData} recentTests={recentTests} upcomingAppointments={upcomingAppointments} />;
  } else {
    return <StudentDashboard stats={stats} recentTests={recentTests} upcomingAppointments={upcomingAppointments} />;
  }
};
// Admin Dashboard Component
const AdminDashboard = ({ stats, chartData, timeRange, setTimeRange }) => {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
  return (
    <ResponsiveLayout>
      <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            System overview and analytics
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setTimeRange('7days')}
            variant={timeRange === '7days' ? 'primary' : 'secondary'}
            size="sm"
          >
            7 Days
          </Button>
          <Button
            onClick={() => setTimeRange('30days')}
            variant={timeRange === '30days' ? 'primary' : 'secondary'}
            size="sm"
          >
            30 Days
          </Button>
          <Button
            onClick={() => setTimeRange('90days')}
            variant={timeRange === '90days' ? 'primary' : 'secondary'}
            size="sm"
          >
            90 Days
          </Button>
        </div>
      </div>
      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Users"
          value={stats.total_users || 0}
          change={stats.recent_activity?.new_users_week || 0}
          changeText="new this week"
          icon={<Users className="w-6 h-6" />}
          color="bg-blue-500"
        />
        <StatsCard
          title="Total Beneficiaries"
          value={stats.total_beneficiaries || 0}
          change={stats.recent_activity?.new_beneficiaries_week || 0}
          changeText="new this week"
          icon={<GraduationCap className="w-6 h-6" />}
          color="bg-green-500"
        />
        <StatsCard
          title="Active Trainers"
          value={stats.total_trainers || 0}
          icon={<UserCheck className="w-6 h-6" />}
          color="bg-purple-500"
        />
        <StatsCard
          title="Evaluations"
          value={stats.total_evaluations || 0}
          change={stats.recent_activity?.evaluations_completed_week || 0}
          changeText="completed this week"
          icon={<ClipboardList className="w-6 h-6" />}
          color="bg-orange-500"
        />
      </div>
      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* User Growth Chart */}
        <ResponsiveCard className="p-6">
          <h3 className="text-lg font-medium mb-4">User Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.user_growth || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#8884d8" name="New Users" />
            </LineChart>
          </ResponsiveContainer>
        </ResponsiveCard>
        {/* Evaluation Completion Chart */}
        <ResponsiveCard className="p-6">
          <h3 className="text-lg font-medium mb-4">Evaluation Completions</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.evaluation_completion || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="count" stroke="#82ca9d" fill="#82ca9d" name="Completed" />
            </AreaChart>
          </ResponsiveContainer>
        </ResponsiveCard>
      </div>
      {/* Role Distribution */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <ResponsiveCard className="p-6">
          <h3 className="text-lg font-medium mb-4">User Role Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Students', value: stats.student_count || 0 },
                  { name: 'Trainers', value: stats.total_trainers || 0 },
                  { name: 'Admins', value: stats.admin_count || 0 }
                ]}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {COLORS.map((color, index) => (
                  <Cell key={`cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ResponsiveCard>
        {/* Recent Activity */}
        <ResponsiveCard className="p-6 col-span-2">
          <h3 className="text-lg font-medium mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <ActivityItem
              title="New Users"
              count={stats.recent_activity?.new_users_week || 0}
              description="registered this week"
              icon={<Users className="w-5 h-5" />}
              trend="up"
            />
            <ActivityItem
              title="New Beneficiaries"
              count={stats.recent_activity?.new_beneficiaries_week || 0}
              description="enrolled this week"
              icon={<GraduationCap className="w-5 h-5" />}
              trend="up"
            />
            <ActivityItem
              title="Evaluations Completed"
              count={stats.recent_activity?.evaluations_completed_week || 0}
              description="finished this week"
              icon={<CheckCircle2 className="w-5 h-5" />}
              trend="up"
            />
          </div>
        </ResponsiveCard>
      </div>
      </div>
    </ResponsiveLayout>
  );
};
// Trainer Dashboard Component
const TrainerDashboard = ({ stats, chartData, recentTests, upcomingAppointments }) => {
  return (
    <ResponsiveLayout>
      <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trainer Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your beneficiaries and track progress
        </p>
      </div>
      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Assigned Beneficiaries"
          value={stats.assigned_beneficiaries || 0}
          icon={<Users className="w-6 h-6" />}
          color="bg-blue-500"
        />
        <StatsCard
          title="Total Sessions"
          value={stats.total_sessions || 0}
          icon={<Calendar className="w-6 h-6" />}
          color="bg-green-500"
        />
        <StatsCard
          title="Completed Evaluations"
          value={stats.completed_evaluations || 0}
          icon={<CheckCircle2 className="w-6 h-6" />}
          color="bg-purple-500"
        />
        <StatsCard
          title="Upcoming Sessions"
          value={stats.upcoming_sessions || 0}
          icon={<Clock className="w-6 h-6" />}
          color="bg-orange-500"
        />
      </div>
      {/* Session Activity Chart */}
      <ResponsiveCard className="p-6">
        <h3 className="text-lg font-medium mb-4">Session Activity</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData.session_completion || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#8884d8" name="Completed Sessions" />
          </BarChart>
        </ResponsiveContainer>
      </ResponsiveCard>
      {/* Recent Evaluations and Appointments */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RecentTestsCard tests={recentTests} />
        <UpcomingAppointmentsCard appointments={upcomingAppointments} />
      </div>
      </div>
    </ResponsiveLayout>
  );
};
// Student Dashboard Component
const StudentDashboard = ({ stats, recentTests, upcomingAppointments }) => {
  return (
    <ResponsiveLayout>
      <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Track your progress and upcoming activities
        </p>
      </div>
      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatsCard
          title="Completed Tests"
          value={stats.completed_tests || 0}
          icon={<CheckCircle2 className="w-6 h-6" />}
          color="bg-green-500"
        />
        <StatsCard
          title="Upcoming Sessions"
          value={stats.upcoming_sessions || 0}
          icon={<Calendar className="w-6 h-6" />}
          color="bg-blue-500"
        />
        <StatsCard
          title="Average Score"
          value={`${Math.round(stats.average_score || 0)}%`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="bg-purple-500"
        />
      </div>
      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RecentTestsCard tests={recentTests} userRole="student" />
        <UpcomingAppointmentsCard appointments={upcomingAppointments} userRole="student" />
      </div>
      </div>
    </ResponsiveLayout>
  );
};
// Reusable Components
const StatsCard = ({ title, value, change, changeText, icon, color }) => {
  return (
    <ResponsiveCard className="overflow-hidden">
      <div className="p-6">
        <div className="flex items-center">
          <div className={`p-3 rounded-lg ${color} bg-opacity-10`}>
            <div className={`${color} text-white`}>{icon}</div>
          </div>
          <div className="ml-4 flex-1">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-semibold text-gray-900">{value}</p>
            {change !== undefined && (
              <p className="text-sm text-green-600">
                +{change} {changeText}
              </p>
            )}
          </div>
        </div>
      </div>
    </ResponsiveCard>
  );
};
const ActivityItem = ({ title, count, description, icon, trend }) => {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center">
        <div className="p-2 bg-white rounded-lg">
          {icon}
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-2xl font-semibold text-gray-900">{count}</p>
        {trend === 'up' && (
          <ArrowUpRight className="w-4 h-4 text-green-500 inline" />
        )}
      </div>
    </div>
  );
};
const RecentTestsCard = ({ tests, userRole }) => {
  return (
    <ResponsiveCard className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Recent Evaluations</h3>
        <Link to="/evaluations" className="text-sm text-primary hover:underline">
          View all
        </Link>
      </div>
      <div className="space-y-3">
        {tests.length > 0 ? (
          tests.map((test) => (
            <div key={test.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{test.title || test.evaluation?.title}</p>
                <p className="text-sm text-gray-500">
                  {new Date(test.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full
                  ${test.status === 'completed' ? 'bg-green-100 text-green-800' :
                    test.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'}`}>
                  {test.status}
                </span>
                {test.score !== null && (
                  <p className="text-sm font-medium text-gray-900 mt-1">{test.score}%</p>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-500 text-center py-4">No recent evaluations</p>
        )}
      </div>
    </ResponsiveCard>
  );
};
const UpcomingAppointmentsCard = ({ appointments, userRole }) => {
  return (
    <ResponsiveCard className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Upcoming Appointments</h3>
        <Link to="/appointments" className="text-sm text-primary hover:underline">
          View all
        </Link>
      </div>
      <div className="space-y-3">
        {appointments.length > 0 ? (
          appointments.map((appointment) => (
            <div key={appointment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{appointment.title}</p>
                <p className="text-sm text-gray-500">
                  {userRole !== 'student' && appointment.beneficiary && (
                    <span>{appointment.beneficiary.first_name} {appointment.beneficiary.last_name} • </span>
                  )}
                  {new Date(appointment.datetime).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {new Date(appointment.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                  {appointment.status}
                </span>
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-500 text-center py-4">No upcoming appointments</p>
        )}
      </div>
    </ResponsiveCard>
  );
};
export default DashboardPageV3;