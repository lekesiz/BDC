import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useTranslation } from '@/i18n/hooks/useTranslation';
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

const DashboardPageWithI18n = () => {
  const { user } = useAuth();
  const { t, format } = useTranslation();
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
        <span className="ml-2">{t('common.loading')}</span>
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
  const { t, format } = useTranslation();
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('dashboard.overview')}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setTimeRange('7days')}
            variant={timeRange === '7days' ? 'primary' : 'secondary'}
            size="sm"
          >
            {t('common.lastWeek')}
          </Button>
          <Button
            onClick={() => setTimeRange('30days')}
            variant={timeRange === '30days' ? 'primary' : 'secondary'}
            size="sm"
          >
            {t('common.lastMonth')}
          </Button>
          <Button
            onClick={() => setTimeRange('90days')}
            variant={timeRange === '90days' ? 'primary' : 'secondary'}
            size="sm"
          >
            {t('common.lastWeek')} 90
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.totalUsers')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {format.number(stats.total_users || 0)}
              </p>
              {stats.user_growth && (
                <p className="mt-2 text-sm text-green-600">
                  +{stats.user_growth}% {t('common.thisMonth')}
                </p>
              )}
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.activeBeneficiaries')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {format.number(stats.active_beneficiaries || 0)}
              </p>
              {stats.beneficiary_growth && (
                <p className="mt-2 text-sm text-green-600">
                  +{stats.beneficiary_growth}% {t('common.thisMonth')}
                </p>
              )}
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <UserCheck className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.activePrograms')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {format.number(stats.active_programs || 0)}
              </p>
              {stats.completion_rate && (
                <p className="mt-2 text-sm text-gray-600">
                  {stats.completion_rate}% {t('dashboard.completionRate')}
                </p>
              )}
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.completedEvaluations')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {format.number(stats.completed_evaluations || 0)}
              </p>
              {stats.average_score && (
                <p className="mt-2 text-sm text-gray-600">
                  {t('evaluations.analytics.averageScore')}: {stats.average_score}%
                </p>
              )}
            </div>
            <div className="p-3 bg-yellow-100 rounded-full">
              <ClipboardList className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Charts */}
      {chartData.userGrowth && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('dashboard.charts.userGrowth')}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.userGrowth}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={(date) => format.date(date, { month: 'short', day: 'numeric' })} />
              <YAxis />
              <Tooltip labelFormatter={(date) => format.date(date)} />
              <Area type="monotone" dataKey="users" stroke="#8884d8" fill="#8884d8" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">{t('dashboard.quickActions')}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link to="/beneficiaries/new">
            <Button variant="outline" className="w-full">
              <Users className="w-4 h-4 mr-2" />
              {t('dashboard.createBeneficiary')}
            </Button>
          </Link>
          <Link to="/programs/new">
            <Button variant="outline" className="w-full">
              <BookOpen className="w-4 h-4 mr-2" />
              {t('dashboard.createProgram')}
            </Button>
          </Link>
          <Link to="/evaluations/create">
            <Button variant="outline" className="w-full">
              <ClipboardList className="w-4 h-4 mr-2" />
              {t('evaluations.create')}
            </Button>
          </Link>
          <Link to="/reports">
            <Button variant="outline" className="w-full">
              <FileText className="w-4 h-4 mr-2" />
              {t('dashboard.viewReports')}
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
};

// Trainer Dashboard Component
const TrainerDashboard = ({ stats, chartData, recentTests, upcomingAppointments }) => {
  const { t, format } = useTranslation();
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <p className="mt-1 text-sm text-gray-500">{t('dashboard.welcome', { name: stats.trainer_name || t('users.roles.trainer') })}</p>
      </div>

      {/* Stats for Trainer */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('beneficiaries.title')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.my_beneficiaries || 0)}</p>
            </div>
            <UserCheck className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.activePrograms')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.active_programs || 0)}</p>
            </div>
            <Target className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.pendingEvaluations')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.pending_evaluations || 0)}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.todayAppointments')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.today_appointments || 0)}</p>
            </div>
            <Calendar className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>

      {/* Recent Tests */}
      {recentTests.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('evaluations.list')}</h3>
          <div className="space-y-4">
            {recentTests.map(test => (
              <div key={test.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{test.title}</p>
                  <p className="text-sm text-gray-600">{format.date(test.created_at)}</p>
                </div>
                <Link to={`/evaluations/${test.id}`}>
                  <Button size="sm" variant="outline">
                    {t('common.view')}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Upcoming Appointments */}
      {upcomingAppointments.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('dashboard.upcomingAppointments')}</h3>
          <div className="space-y-4">
            {upcomingAppointments.map(appointment => (
              <div key={appointment.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{appointment.title}</p>
                  <p className="text-sm text-gray-600">
                    {format.dateTime(appointment.start_time)}
                  </p>
                </div>
                <Link to={`/calendar?event=${appointment.id}`}>
                  <Button size="sm" variant="outline">
                    {t('common.view')}
                    <ArrowUpRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

// Student Dashboard Component
const StudentDashboard = ({ stats, recentTests, upcomingAppointments }) => {
  const { t, format } = useTranslation();
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <p className="mt-1 text-sm text-gray-500">{t('dashboard.welcome', { name: stats.student_name || t('users.roles.student') })}</p>
      </div>

      {/* Student Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('programs.enrollment.title')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.enrolled_programs || 0)}</p>
            </div>
            <BookOpen className="w-8 h-8 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('dashboard.completedPrograms')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.completed_programs || 0)}</p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('evaluations.analytics.averageScore')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.average_score || 0}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-yellow-600" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('programs.fields.certificates')}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{format.number(stats.certificates || 0)}</p>
            </div>
            <Award className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>

      {/* Recent Tests */}
      {recentTests.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{t('evaluations.list')}</h3>
          <div className="space-y-4">
            {recentTests.map(test => (
              <div key={test.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{test.title}</p>
                  <p className="text-sm text-gray-600">
                    {t('evaluations.fields.dueDate')}: {format.date(test.due_date)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {test.status === 'completed' && (
                    <span className="text-sm text-green-600">
                      {t('evaluations.grading.score')}: {test.score}%
                    </span>
                  )}
                  <Link to={`/portal/evaluations/${test.id}`}>
                    <Button size="sm" variant="outline">
                      {test.status === 'completed' ? t('evaluations.submission.viewResults') : t('common.continue')}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Quick Links */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">{t('dashboard.quickActions')}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link to="/portal/courses">
            <Button variant="outline" className="w-full">
              <BookOpen className="w-4 h-4 mr-2" />
              {t('navigation.programs')}
            </Button>
          </Link>
          <Link to="/portal/evaluations">
            <Button variant="outline" className="w-full">
              <ClipboardList className="w-4 h-4 mr-2" />
              {t('navigation.evaluations')}
            </Button>
          </Link>
          <Link to="/portal/documents">
            <Button variant="outline" className="w-full">
              <FileText className="w-4 h-4 mr-2" />
              {t('navigation.documents')}
            </Button>
          </Link>
          <Link to="/portal/calendar">
            <Button variant="outline" className="w-full">
              <Calendar className="w-4 h-4 mr-2" />
              {t('navigation.calendar')}
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default DashboardPageWithI18n;