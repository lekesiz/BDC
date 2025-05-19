import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './components/ui/toast';
import { useAuth } from './hooks/useAuth';
import ProtectedRoute from './components/common/ProtectedRoute';
import { SocketProvider } from './contexts/SocketContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { FullPageLoader } from './components/common/LoadingStates';
import ErrorBoundary from './components/common/ErrorBoundary';
import GlobalErrorHandler from './components/common/GlobalErrorHandler';
import NotificationProviderV2 from './providers/NotificationProviderV2';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('./pages/auth/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/auth/ResetPasswordPage'));

// Dashboard Pages
const DashboardPage = lazy(() => import('./pages/dashboard/DashboardPageEnhanced'));
const PortalDashboard = lazy(() => import('./pages/portal/PortalDashboardV3'));

// Layouts
const DashboardLayout = lazy(() => import('./components/layout/DashboardLayout'));

// User Pages
const ProfilePage = lazy(() => import('./pages/profile/ProfilePage'));
const SettingsPage = lazy(() => import('./pages/settings/SettingsPage'));
const UsersPage = lazy(() => import('./pages/users/UsersPage'));
const UserFormPage = lazy(() => import('./pages/users/UserFormPage'));
const UserDetailPage = lazy(() => import('./pages/users/UserDetailPage'));

// Beneficiary Pages
const BeneficiariesPage = lazy(() => import('./pages/beneficiaries/BeneficiariesPageEnhanced'));
const BeneficiaryDetailPage = lazy(() => import('./pages/beneficiaries/BeneficiaryDetailPage'));
const BeneficiaryFormPage = lazy(() => import('./pages/beneficiaries/BeneficiaryFormPage'));

// Admin Pages
const TenantsPage = lazy(() => import('./pages/admin/TenantsPage'));
const TenantDetailPage = lazy(() => import('./pages/admin/TenantDetailPage'));
const TenantEditPage = lazy(() => import('./pages/admin/TenantEditPage'));

// Other Pages
const ProgramsPage = lazy(() => import('./pages/programs/ProgramsListPage'));
const CalendarPage = lazy(() => import('./pages/calendar/CalendarPage'));
const DocumentsPage = lazy(() => import('./pages/document/DocumentsPage'));
const MessagingPage = lazy(() => import('./pages/messaging/MessagingPage'));
const NotificationsPage = lazy(() => import('./pages/notifications/NotificationsPage'));
const AnalyticsPage = lazy(() => import('./pages/analytics/AnalyticsDashboardPage'));
const ReportsPage = lazy(() => import('./pages/reports/ReportsDashboardPage'));

// Portal Pages
const PortalCalendarPage = lazy(() => import('./pages/portal/PortalCalendarPage'));
const PortalCoursesPage = lazy(() => import('./pages/portal/PortalCoursesPage'));
const PortalResourcesPage = lazy(() => import('./pages/portal/PortalResourcesPage'));
const PortalAssessmentsPage = lazy(() => import('./pages/portal/assessment/PortalAssessmentsPage'));
const PortalProgressPage = lazy(() => import('./pages/portal/PortalProgressPage'));
const PortalProfilePage = lazy(() => import('./pages/portal/PortalProfilePage'));

// Test Pages
const TestLogin = lazy(() => import('./TestLogin'));
const TestAuth = lazy(() => import('./TestAuth'));

// Role-based dashboard component
const RoleDashboard = () => {
  const { user } = useAuth();
  
  if (user?.role === 'student') {
    return <PortalDashboard />;
  }
  
  return <DashboardPage />;
};

// Role-based redirect after login
const AuthRedirect = () => {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // Students go to portal
  if (user.role === 'student') {
    return <Navigate to="/portal" replace />;
  }
  
  // All other roles go to dashboard
  return <Navigate to="/dashboard" replace />;
};

function AppWithProperRouting() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <ErrorBoundary>
          <GlobalErrorHandler />
          <NotificationProviderV2>
            <SocketProvider>
              <Suspense fallback={<FullPageLoader />}>
                <Routes>
                  {/* Test routes */}
                  <Route path="/test-login" element={<TestLogin />} />
                  <Route path="/test-auth" element={<TestAuth />} />
                  
                  {/* Public routes */}
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                  <Route path="/reset-password" element={<ResetPasswordPage />} />
                  
                  {/* Root redirect based on auth */}
                  <Route path="/" element={<AuthRedirect />} />
                  
                  {/* Main app routes with dashboard layout */}
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <DashboardLayout />
                      </ProtectedRoute>
                    }
                  >
                    <Route index element={<RoleDashboard />} />
                    
                    {/* User management */}
                    <Route path="profile" element={<ProfilePage />} />
                    <Route path="settings" element={<SettingsPage />} />
                    <Route path="users">
                      <Route index element={<UsersPage />} />
                      <Route path="create" element={<UserFormPage />} />
                      <Route path=":id" element={<UserDetailPage />} />
                      <Route path=":id/edit" element={<UserFormPage />} />
                    </Route>
                    
                    {/* Beneficiaries */}
                    <Route path="beneficiaries">
                      <Route
                        index
                        element={
                          <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                            <BeneficiariesPage />
                          </ProtectedRoute>
                        }
                      />
                      <Route path=":id" element={<BeneficiaryDetailPage />} />
                      <Route path="create" element={<BeneficiaryFormPage />} />
                      <Route path=":id/edit" element={<BeneficiaryFormPage />} />
                    </Route>
                    
                    {/* Admin routes */}
                    <Route path="admin">
                      <Route path="tenants">
                        <Route
                          index
                          element={
                            <ProtectedRoute requiredRole={['super_admin']}>
                              <TenantsPage />
                            </ProtectedRoute>
                          }
                        />
                        <Route path=":id" element={<TenantDetailPage />} />
                        <Route path=":id/edit" element={<TenantEditPage />} />
                      </Route>
                    </Route>
                    
                    {/* Other features */}
                    <Route path="programs" element={<ProgramsPage />} />
                    <Route path="calendar" element={<CalendarPage />} />
                    <Route path="documents" element={<DocumentsPage />} />
                    <Route path="messaging" element={<MessagingPage />} />
                    <Route path="notifications" element={<NotificationsPage />} />
                    <Route path="analytics" element={<AnalyticsPage />} />
                    <Route path="reports" element={<ReportsPage />} />
                  </Route>
                  
                  {/* Student portal routes */}
                  <Route
                    path="/portal"
                    element={
                      <ProtectedRoute requiredRole={['student']}>
                        <DashboardLayout />
                      </ProtectedRoute>
                    }
                  >
                    <Route index element={<PortalDashboard />} />
                    <Route path="calendar" element={<PortalCalendarPage />} />
                    <Route path="courses" element={<PortalCoursesPage />} />
                    <Route path="resources" element={<PortalResourcesPage />} />
                    <Route path="assessments" element={<PortalAssessmentsPage />} />
                    <Route path="progress" element={<PortalProgressPage />} />
                    <Route path="profile" element={<PortalProfilePage />} />
                  </Route>
                  
                  {/* 404 page */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Suspense>
            </SocketProvider>
          </NotificationProviderV2>
        </ErrorBoundary>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default AppWithProperRouting;