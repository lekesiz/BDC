import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';
import { AnimatedCard, AnimatedButton, AnimatedPage } from '@/components/animations';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import { useAsync } from '@/hooks/useAsync';
import AsyncBoundary from '@/components/common/AsyncBoundary';
import { CardLoader, SkeletonCard } from '@/components/common/LoadingStates';
import { ErrorDisplay } from '@/components/common/ErrorBoundary';
import { staggerContainer, staggerItem } from '@/lib/animations';
import { motion } from 'framer-motion';
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
 * Enhanced Dashboard page component with proper loading and error handling
 */
const DashboardPageEnhanced = () => {
  const { user } = useAuth();
  const { addToast } = useToast();
  
  // Use async hooks for different data fetches
  const analyticsAsync = useAsync(async () => {
    try {
      const response = await api.get(API_ENDPOINTS.ANALYTICS.DASHBOARD);
      const statistics = response.data.statistics || {};
      return {
        totalBeneficiaries: statistics.total_beneficiaries || statistics.assigned_beneficiaries || 0,
        activeEvaluations: statistics.total_evaluations || statistics.completed_evaluations || 0,
        documentsGenerated: statistics.documents_generated || 0,
        upcomingAppointments: statistics.upcoming_sessions || statistics.upcoming_appointments || 0,
        completedEvaluations: statistics.completed_evaluations || 0,
        ...statistics
      };
    } catch (error) {
      // Return default values on error
      console.error('Analytics error:', error);
      return {
        totalBeneficiaries: 0,
        activeEvaluations: 0,
        documentsGenerated: 0,
        upcomingAppointments: 0,
        completedEvaluations: 0,
        enrolledPrograms: 0,
        averageScore: 0,
        achievements: 0
      };
    }
  }, [user], true);

  const reportsAsync = useAsync(async () => {
    const response = await api.get(API_ENDPOINTS.REPORTS.RECENT);
    return response.data || [];
  }, [user], true);

  const appointmentsAsync = useAsync(async () => {
    try {
      const response = await api.get('/api/calendar/events', {
        params: {
          start: new Date().toISOString().split('T')[0],
          end: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        }
      });
      return response.data.events || [];
    } catch (error) {
      // Handle Google Calendar not connected error gracefully
      if (error.response?.data?.error === 'not_connected') {
        return []; // Return empty array instead of throwing
      }
      throw error; // Re-throw other errors
    }
  }, [user], true);

  const programsAsync = useAsync(async () => {
    if (user?.role === 'student' || user?.role === 'trainee') {
      const response = await api.get('/api/programs');
      return response.data || [];
    }
    return [];
  }, [user], user?.role === 'student' || user?.role === 'trainee');

  const testsAsync = useAsync(async () => {
    const response = await api.get('/api/tests', {
      params: { per_page: 4 }
    });
    return response.data.tests || [];
  }, [user], true);

  // Refresh all data
  const refreshData = async () => {
    try {
      await Promise.all([
        analyticsAsync.execute(),
        reportsAsync.execute(),
        appointmentsAsync.execute(),
        programsAsync.execute(),
        testsAsync.execute()
      ]);
      addToast({
        type: 'success',
        title: 'Data refreshed',
        message: 'Dashboard data has been refreshed successfully'
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Refresh failed',
        message: 'Failed to refresh dashboard data'
      });
    }
  };

  // Check overall loading state
  const isLoading = analyticsAsync.loading || reportsAsync.loading || 
                   appointmentsAsync.loading || programsAsync.loading || 
                   testsAsync.loading;

  // QuickActionButton component
  const QuickActionButton = ({ title, description, icon: Icon, href }) => (
    <Link to={href}>
      <AnimatedButton
        variant="outline"
        className="h-auto flex-col items-start w-full text-left hover:bg-gray-50"
      >
        <Icon className="h-6 w-6 text-primary mb-2" />
        <span className="font-medium">{title}</span>
        <span className="text-sm text-gray-600 line-clamp-2">
          {description}
        </span>
      </AnimatedButton>
    </Link>
  );

  // StatsCard component
  const StatsCard = ({ title, value, icon: Icon, change, href }) => (
    <Link to={href || '#'}>
      <AnimatedCard className="hover:shadow-lg transition-shadow cursor-pointer">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Icon className="h-6 w-6 text-primary" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  {title}
                </dt>
                <dd className="flex items-baseline">
                  <div className="text-2xl font-semibold text-gray-900">
                    {value}
                  </div>
                  {change && (
                    <span
                      className={`ml-2 text-sm font-medium ${
                        change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {change >= 0 ? '+' : ''}{change}%
                    </span>
                  )}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </AnimatedCard>
    </Link>
  );

  // StatusChip component
  const StatusChip = ({ status }) => {
    const statusColors = {
      completed: 'bg-green-100 text-green-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      not_started: 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status] || statusColors.not_started}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  // Role-specific dashboard content
  const renderDashboardContent = () => {
    if (!user) return null;

    return (
      <>
        {/* Stats cards */}
        <motion.div 
          className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          <AsyncBoundary 
            loading={analyticsAsync.loading} 
            error={analyticsAsync.error} 
            loadingComponent={<SkeletonCard />}
          >
            {user.role === 'student' ? (
              <>
                <StatsCard
                  title="Enrolled Programs"
                  value={analyticsAsync.data?.enrolledPrograms || 0}
                  icon={BookOpen}
                  href="/portal/programs"
                />
                <StatsCard
                  title="Tests Completed"
                  value={analyticsAsync.data?.completedEvaluations || 0}
                  icon={CheckCircle2}
                  href="/portal/evaluations"
                />
                <StatsCard
                  title="Average Score"
                  value={`${analyticsAsync.data?.averageScore || 0}%`}
                  icon={TrendingUp}
                  href="/portal/progress"
                />
                <StatsCard
                  title="Achievements"
                  value={analyticsAsync.data?.achievements || 0}
                  icon={Award}
                  href="/portal/achievements"
                />
              </>
            ) : (
              <>
                <StatsCard
                  title="Total Beneficiaries"
                  value={analyticsAsync.data?.totalBeneficiaries || 0}
                  icon={ClipboardList}
                  change={analyticsAsync.data?.beneficiariesChange}
                  href="/beneficiaries"
                />
                <StatsCard
                  title="Active Evaluations"
                  value={analyticsAsync.data?.activeEvaluations || 0}
                  icon={Activity}
                  change={analyticsAsync.data?.evaluationsChange}
                  href="/evaluations"
                />
                <StatsCard
                  title="Documents Generated"
                  value={analyticsAsync.data?.documentsGenerated || 0}
                  icon={FileText}
                  change={analyticsAsync.data?.reportsChange}
                  href="/reports"
                />
                <StatsCard
                  title="Upcoming Appointments"
                  value={analyticsAsync.data?.upcomingAppointments || 0}
                  icon={Calendar}
                  href="/appointments"
                />
              </>
            )}
          </AsyncBoundary>
        </motion.div>

        {/* Main content grid */}
        <motion.div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Recent Tests Section */}
          <AsyncBoundary
            loading={testsAsync.loading}
            error={testsAsync.error}
            loadingComponent={<CardLoader />}
            errorComponent={<ErrorDisplay error={testsAsync.error} onRetry={testsAsync.execute} />}
          >
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Recent Evaluations</h3>
                <Link
                  to={user.role === 'student' ? '/portal/evaluations' : '/evaluations'}
                  className="text-sm font-medium text-primary hover:text-primary-dark flex items-center"
                >
                  View all
                  <ArrowRight className="ml-1 w-4 h-4" />
                </Link>
              </div>
              <div className="border-t border-gray-200 divide-y divide-gray-200">
                {testsAsync.data?.length > 0 ? (
                  testsAsync.data.map((test) => (
                    <div key={test.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {test.title}
                        </p>
                        <StatusChip status={test.status} />
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
          </AsyncBoundary>

          {/* Upcoming Appointments Section */}
          <AsyncBoundary
            loading={appointmentsAsync.loading}
            error={appointmentsAsync.error}
            loadingComponent={<CardLoader />}
            errorComponent={<ErrorDisplay error={appointmentsAsync.error} onRetry={appointmentsAsync.execute} />}
          >
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Upcoming Appointments</h3>
                <Link
                  to={user.role === 'student' ? '/my-appointments' : '/appointments'}
                  className="text-sm font-medium text-primary hover:text-primary-dark flex items-center"
                >
                  View all
                  <ArrowRight className="ml-1 w-4 h-4" />
                </Link>
              </div>
              <div className="border-t border-gray-200 divide-y divide-gray-200">
                {appointmentsAsync.data?.length > 0 ? (
                  appointmentsAsync.data.map((appointment) => (
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
                        {user.role !== 'student' && (
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
          </AsyncBoundary>
        </motion.div>

        {/* Quick Actions */}
        <motion.div 
          className="bg-white shadow rounded-lg overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
            <motion.div 
              className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
              variants={staggerContainer}
              initial="initial"
              animate="animate"
            >
              {user.role === 'student' ? (
                <>
                  <QuickActionButton
                    title="Take Evaluation"
                    description="Start a new assessment or continue an existing one"
                    icon={ClipboardList}
                    href="/portal/evaluations"
                  />
                  <QuickActionButton
                    title="View Progress"
                    description="Check your learning progress and achievements"
                    icon={TrendingUp}
                    href="/portal/progress"
                  />
                  <QuickActionButton
                    title="My Documents"
                    description="Access your files and resources"
                    icon={FileText}
                    href="/my-documents"
                  />
                  <QuickActionButton
                    title="Messages"
                    description="Check messages from trainers"
                    icon={Activity}
                    href="/portal/messages"
                  />
                </>
              ) : (
                <>
                  <QuickActionButton
                    title="Create Test"
                    description="Design a new evaluation or assessment"
                    icon={ClipboardList}
                    href="/tests/create"
                  />
                  <QuickActionButton
                    title="Schedule Appointment"
                    description="Book a session with a beneficiary"
                    icon={Calendar}
                    href="/appointments/new"
                  />
                  <QuickActionButton
                    title="Add Beneficiary"
                    description="Register a new beneficiary"
                    icon={Users}
                    href="/beneficiaries/create"
                  />
                  <QuickActionButton
                    title="Generate Report"
                    description="Create progress reports"
                    icon={FileText}
                    href="/reports/create"
                  />
                </>
              )}
            </motion.div>
          </div>
        </motion.div>
      </>
    );
  };

  return (
    <AnimatedPage className="space-y-6">
      {/* Page header with refresh button */}
      <motion.div 
        className="flex justify-between items-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <AnimatedButton
          onClick={refreshData}
          disabled={isLoading}
          variant="outline"
          size="sm"
        >
          {isLoading ? (
            <Loader className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <Activity className="h-4 w-4 mr-2" />
          )}
          Refresh
        </AnimatedButton>
      </motion.div>
      
      {/* Dashboard content */}
      {renderDashboardContent()}
    </AnimatedPage>
  );
};

export default DashboardPageEnhanced;