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
  Loader
} from 'lucide-react';

/**
 * Dashboard page component - shows different content based on user role
 */
const DashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [recentTests, setRecentTests] = useState([]);
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // Get dashboard analytics
        const analyticsResponse = await api.get(API_ENDPOINTS.ANALYTICS.DASHBOARD);
        const statistics = analyticsResponse.data.statistics || {};
        
        // Map backend response to frontend format
        const mappedStats = {
          totalBeneficiaries: statistics.total_beneficiaries || statistics.assigned_beneficiaries || 0,
          activeEvaluations: statistics.total_evaluations || statistics.completed_evaluations || 0,
          documentsGenerated: statistics.documents_generated || 0,
          upcomingAppointments: statistics.upcoming_sessions || statistics.upcoming_appointments || 0,
          completedEvaluations: statistics.completed_evaluations || 0,
          ...statistics
        };
        
        setStats(mappedStats);
        
        // Get recent reports
        const reportsResponse = await api.get(API_ENDPOINTS.REPORTS.RECENT);
        setRecentReports(reportsResponse.data || []);
        
        // Get upcoming appointments
        const appointmentsResponse = await api.get('/api/calendar/events', {
          params: {
            start: new Date().toISOString().split('T')[0],
            end: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          }
        });
        setUpcomingAppointments(appointmentsResponse.data.events || []);
        
        // Get programs for students
        if (user?.role === 'student' || user?.role === 'trainee') {
          const programsResponse = await api.get('/api/programs');
          setPrograms(programsResponse.data || []);
        }
        
        // Get recent tests
        const testsResponse = await api.get('/api/tests', {
          params: { per_page: 4 }
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
  
  // Render different dashboard based on user role
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back, {user?.first_name}! Here's what's happening today.
        </p>
      </div>
      
      {/* Stats cards */}
      {(user?.role === 'super_admin' || user?.role === 'tenant_admin' || user?.role === 'trainer') && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Beneficiaries"
            value={stats.totalBeneficiaries}
            icon={<Users className="w-6 h-6" />}
            linkTo="/beneficiaries"
          />
          <StatsCard
            title="Active Evaluations"
            value={stats.activeEvaluations}
            icon={<ClipboardList className="w-6 h-6" />}
            linkTo="/evaluations"
          />
          <StatsCard
            title="Documents Generated"
            value={stats.documentsGenerated}
            icon={<FileText className="w-6 h-6" />}
            linkTo="/documents"
          />
          <StatsCard
            title="Upcoming Appointments"
            value={stats.upcomingAppointments}
            icon={<Calendar className="w-6 h-6" />}
            linkTo="/appointments"
          />
        </div>
      )}
      
      {/* Student-specific stats */}
      {user?.role === 'student' && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatsCard
            title="Active Evaluations"
            value={stats.activeEvaluations}
            icon={<ClipboardList className="w-6 h-6" />}
            linkTo="/my-evaluations"
          />
          <StatsCard
            title="Completed Evaluations"
            value={stats.completedEvaluations}
            icon={<CheckCircle2 className="w-6 h-6" />}
            linkTo="/my-evaluations?status=completed"
          />
          <StatsCard
            title="Upcoming Appointments"
            value={stats.upcomingAppointments}
            icon={<Calendar className="w-6 h-6" />}
            linkTo="/my-appointments"
          />
        </div>
      )}
      
      {/* Main content area */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent tests/evaluations */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Recent Evaluations</h3>
            <Link
              to={user?.role === 'student' ? '/my-evaluations' : '/evaluations'}
              className="text-sm font-medium text-primary hover:text-primary-dark flex items-center"
            >
              View all
              <ArrowRight className="ml-1 w-4 h-4" />
            </Link>
          </div>
          <div className="border-t border-gray-200 divide-y divide-gray-200">
            {recentTests.length > 0 ? (
              recentTests.map((test) => (
                <div key={test.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <Link 
                      to={`/evaluations/${test.id}`}
                      className="text-sm font-medium text-primary hover:text-primary-dark truncate"
                    >
                      {test.title}
                    </Link>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${test.status === 'completed' 
                          ? 'bg-green-100 text-green-800' 
                          : test.status === 'in_progress' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-yellow-100 text-yellow-800'}`}
                      >
                        {test.status === 'completed' 
                          ? 'Completed' 
                          : test.status === 'in_progress' 
                            ? 'In Progress' 
                            : 'Pending'}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        {test.status === 'completed' ? (
                          <>
                            <Activity className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            Score: {test.score}%
                          </>
                        ) : (
                          <>
                            <Clock className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            Continue test
                          </>
                        )}
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <Calendar className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                      <p>
                        {new Date(test.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-4 py-5 sm:px-6 text-center text-sm text-gray-500">
                No recent evaluations found.
              </div>
            )}
          </div>
        </div>
        
        {/* Upcoming appointments */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Upcoming Appointments</h3>
            <Link
              to={user?.role === 'student' ? '/my-appointments' : '/appointments'}
              className="text-sm font-medium text-primary hover:text-primary-dark flex items-center"
            >
              View all
              <ArrowRight className="ml-1 w-4 h-4" />
            </Link>
          </div>
          <div className="border-t border-gray-200 divide-y divide-gray-200">
            {upcomingAppointments.length > 0 ? (
              upcomingAppointments.map((appointment) => (
                <div key={appointment.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {appointment.title}
                    </p>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        <Calendar className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                        {new Date(appointment.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                        {' at '}
                        {appointment.time}
                      </p>
                    </div>
                    {user?.role !== 'student' && (
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <Users className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                        <p>{appointment.beneficiary}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="px-4 py-5 sm:px-6 text-center text-sm text-gray-500">
                No upcoming appointments found.
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Quick actions */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {user?.role === 'student' ? (
              <>
                <QuickActionButton
                  title="Take Evaluation"
                  description="Start a new evaluation"
                  icon={<ClipboardList className="w-5 h-5" />}
                  to="/evaluations"
                />
                <QuickActionButton
                  title="Schedule Appointment"
                  description="Book time with your trainer"
                  icon={<Calendar className="w-5 h-5" />}
                  to="/schedule"
                />
                <QuickActionButton
                  title="View Documents"
                  description="Access your reports"
                  icon={<FileText className="w-5 h-5" />}
                  to="/my-documents"
                />
                <QuickActionButton
                  title="Update Profile"
                  description="Edit your information"
                  icon={<Users className="w-5 h-5" />}
                  to="/profile"
                />
              </>
            ) : (
              <>
                <QuickActionButton
                  title="Create Evaluation"
                  description="Design a new test"
                  icon={<ClipboardList className="w-5 h-5" />}
                  to="/evaluations/create"
                />
                <QuickActionButton
                  title="Add Beneficiary"
                  description="Register a new student"
                  icon={<Users className="w-5 h-5" />}
                  to="/beneficiaries/create"
                />
                <QuickActionButton
                  title="Schedule Appointment"
                  description="Book time with a beneficiary"
                  icon={<Calendar className="w-5 h-5" />}
                  to="/appointments/create"
                />
                <QuickActionButton
                  title="Generate Report"
                  description="Create a new document"
                  icon={<FileText className="w-5 h-5" />}
                  to="/documents/create"
                />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Stats card component
const StatsCard = ({ title, value, icon, linkTo }) => {
  return (
    <Link
      to={linkTo}
      className="bg-white overflow-hidden shadow rounded-lg transition duration-200 hover:shadow-md"
    >
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0 bg-primary-50 rounded-md p-3">
            {icon}
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd>
                <div className="text-lg font-medium text-gray-900">{value}</div>
              </dd>
            </dl>
          </div>
          <div className="ml-4 flex-shrink-0">
            <ArrowUpRight className="h-5 w-5 text-gray-400" />
          </div>
        </div>
      </div>
    </Link>
  );
};

// Quick action button component
const QuickActionButton = ({ title, description, icon, to }) => {
  return (
    <Link
      to={to}
      className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-primary hover:bg-primary-50 transition duration-200"
    >
      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <span className="absolute inset-0" aria-hidden="true" />
        <p className="text-sm font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-500 truncate">{description}</p>
      </div>
    </Link>
  );
};

export default DashboardPage;