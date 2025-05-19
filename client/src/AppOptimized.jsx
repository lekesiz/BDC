import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { ErrorProvider } from './contexts/ErrorContext';
import { Toaster } from './components/ui/toaster';
import { PerformanceMonitor } from './components/performance/PerformanceMonitor';
import { FullPageLoader } from './components/common/LoadingStates';
import ErrorBoundary from './components/common/ErrorBoundary';
import { lazyLoadWithRetry, createLazyPage } from './utils/lazyLoad';
import { 
  preloadCriticalResources, 
  addResourceHints, 
  lazyLoadImages,
  checkPerformanceBudget 
} from './utils/bundleOptimization';

// Lazy load pages with retry capability
const LoginPage = createLazyPage(() => import('./pages/auth/LoginPage'));
const DashboardPage = createLazyPage(() => import('./pages/dashboard/DashboardPageEnhanced'));
const BeneficiariesPage = createLazyPage(() => import('./pages/beneficiaries/BeneficiariesPageEnhanced'));
const UsersPage = createLazyPage(() => import('./pages/users/UsersPage'));
const TenantsPage = createLazyPage(() => import('./pages/admin/TenantsPage'));
const ProgramsPage = createLazyPage(() => import('./pages/programs/ProgramsListPage'));
const CalendarPage = createLazyPage(() => import('./pages/calendar/CalendarPage'));
const DocumentsPage = createLazyPage(() => import('./pages/document/DocumentsPage'));
const MessagingPage = createLazyPage(() => import('./pages/messaging/MessagingPage'));
const NotificationsPage = createLazyPage(() => import('./pages/notifications/NotificationsPage'));
const AnalyticsPage = createLazyPage(() => import('./pages/analytics/AnalyticsDashboardPage'));
const ReportsPage = createLazyPage(() => import('./pages/reports/ReportsDashboardPage'));
const SettingsPage = createLazyPage(() => import('./pages/settings/SettingsPage'));
const ProfilePage = createLazyPage(() => import('./pages/profile/ProfilePage'));

// Lazy load layouts
const MainLayout = lazy(() => import('./components/layout/MainLayout'));
const AuthLayout = lazy(() => import('./components/layout/AuthLayout'));

// Protected route wrapper
const ProtectedRoute = lazy(() => import('./components/common/ProtectedRoute'));

function AppOptimized() {
  useEffect(() => {
    // Performance optimizations on mount
    preloadCriticalResources();
    addResourceHints();
    
    // Lazy load images after initial render
    requestIdleCallback(() => {
      lazyLoadImages();
    });
    
    // Register service worker
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          console.log('Service Worker registered:', registration);
        })
        .catch(error => {
          console.error('Service Worker registration failed:', error);
        });
    }
    
    // Check performance budget in development
    if (process.env.NODE_ENV === 'development') {
      window.addEventListener('load', () => {
        checkPerformanceBudget();
      });
    }
  }, []);

  return (
    <ErrorProvider>
      <ThemeProvider>
        <AuthProvider>
          <ErrorBoundary>
            <Router>
              <Suspense fallback={<FullPageLoader />}>
                <Routes>
                  {/* Public routes */}
                  <Route element={<AuthLayout />}>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                  </Route>

                  {/* Protected routes */}
                  <Route element={
                    <ProtectedRoute>
                      <MainLayout />
                    </ProtectedRoute>
                  }>
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    
                    {/* Beneficiaries */}
                    <Route path="/beneficiaries" element={<BeneficiariesPage />} />
                    <Route path="/beneficiaries/:id" element={<BeneficiaryDetailPage />} />
                    
                    {/* Users */}
                    <Route path="/users" element={<UsersPage />} />
                    <Route path="/users/:id" element={<UserDetailPage />} />
                    
                    {/* Admin */}
                    <Route path="/admin/tenants" element={<TenantsPage />} />
                    <Route path="/admin/tenants/:id" element={<TenantDetailPage />} />
                    
                    {/* Programs */}
                    <Route path="/programs" element={<ProgramsPage />} />
                    <Route path="/programs/:id" element={<ProgramDetailPage />} />
                    
                    {/* Calendar */}
                    <Route path="/calendar" element={<CalendarPage />} />
                    
                    {/* Documents */}
                    <Route path="/documents" element={<DocumentsPage />} />
                    <Route path="/documents/:id" element={<DocumentDetailPage />} />
                    
                    {/* Communication */}
                    <Route path="/messaging" element={<MessagingPage />} />
                    <Route path="/notifications" element={<NotificationsPage />} />
                    
                    {/* Analytics & Reports */}
                    <Route path="/analytics" element={<AnalyticsPage />} />
                    <Route path="/reports" element={<ReportsPage />} />
                    
                    {/* User */}
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                  </Route>

                  {/* 404 page */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>
            </Router>

            <Toaster />
            
            {/* Performance monitoring in development */}
            {process.env.NODE_ENV === 'development' && (
              <PerformanceMonitor 
                position="bottom-right"
                autoHide={false}
              />
            )}
          </ErrorBoundary>
        </AuthProvider>
      </ThemeProvider>
    </ErrorProvider>
  );
}

export default AppOptimized;

// Preload critical routes on hover/focus
document.addEventListener('DOMContentLoaded', () => {
  const criticalRoutes = [
    { path: '/dashboard', component: () => import('./pages/dashboard/DashboardPageEnhanced') },
    { path: '/beneficiaries', component: () => import('./pages/beneficiaries/BeneficiariesPageEnhanced') },
  ];

  criticalRoutes.forEach(({ path, component }) => {
    const links = document.querySelectorAll(`a[href="${path}"]`);
    links.forEach(link => {
      link.addEventListener('mouseenter', () => component(), { once: true });
      link.addEventListener('focus', () => component(), { once: true });
    });
  });
});