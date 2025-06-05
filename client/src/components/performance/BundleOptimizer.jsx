import React, { lazy, Suspense } from 'react';
import { LoadingSpinner } from '../ui/LoadingSpinner';
/**
 * Bundle Optimizer - Utility components for code splitting and lazy loading
 */
// Error boundary for lazy loaded components
export class LazyBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-8">
          <p className="text-red-600 mb-4">Failed to load component</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
// Lazy load wrapper with retry logic
export function lazyWithRetry(componentImport) {
  return lazy(async () => {
    const pageHasAlreadyBeenForceRefreshed = JSON.parse(
      window.sessionStorage.getItem('page-has-been-force-refreshed') || 'false'
    );
    try {
      const component = await componentImport();
      window.sessionStorage.setItem('page-has-been-force-refreshed', 'false');
      return component;
    } catch (error) {
      if (!pageHasAlreadyBeenForceRefreshed) {
        window.sessionStorage.setItem('page-has-been-force-refreshed', 'true');
        window.location.reload();
      }
      throw error;
    }
  });
}
// Preload component function
export function preloadComponent(componentImport) {
  componentImport();
}
// Loading fallback component
export const PageLoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="lg" />
  </div>
);
// Optimized lazy imports for all major routes
export const LazyComponents = {
  // Auth pages
  LoginPage: lazyWithRetry(() => import('../../pages/auth/LoginPage')),
  RegisterPage: lazyWithRetry(() => import('../../pages/auth/RegisterPage')),
  ForgotPasswordPage: lazyWithRetry(() => import('../../pages/auth/ForgotPasswordPage')),
  ResetPasswordPage: lazyWithRetry(() => import('../../pages/auth/ResetPasswordPage')),
  // Dashboard pages
  DashboardPage: lazyWithRetry(() => import('../../pages/dashboard/DashboardPage')),
  // Beneficiary pages
  BeneficiariesPage: lazyWithRetry(() => import('../../pages/beneficiaries/BeneficiariesPage')),
  BeneficiaryDetailPage: lazyWithRetry(() => import('../../pages/beneficiaries/BeneficiaryDetailPage')),
  BeneficiaryFormPage: lazyWithRetry(() => import('../../pages/beneficiaries/BeneficiaryFormPage')),
  // Program pages
  ProgramsListPage: lazyWithRetry(() => import('../../pages/programs/ProgramsListPage')),
  ProgramDetailPage: lazyWithRetry(() => import('../../pages/programs/ProgramDetailPage')),
  CreateProgramPage: lazyWithRetry(() => import('../../pages/programs/CreateProgramPage')),
  EditProgramPage: lazyWithRetry(() => import('../../pages/programs/EditProgramPage')),
  // Evaluation pages
  EvaluationsPage: lazyWithRetry(() => import('../../pages/evaluation/EvaluationsPage')),
  TestCreationPage: lazyWithRetry(() => import('../../pages/evaluation/TestCreationPage')),
  TestResultsPage: lazyWithRetry(() => import('../../pages/evaluation/TestResultsPage')),
  // Document pages
  DocumentsPage: lazyWithRetry(() => import('../../pages/document/DocumentsPage')),
  DocumentUploadPage: lazyWithRetry(() => import('../../pages/document/DocumentUploadPage')),
  DocumentDetailPage: lazyWithRetry(() => import('../../pages/document/DocumentDetailPage')),
  // Calendar pages
  CalendarPage: lazyWithRetry(() => import('../../pages/calendar/CalendarPage')),
  // Messaging pages
  MessagingPage: lazyWithRetry(() => import('../../pages/messaging/MessagingPage')),
  // Notification pages
  NotificationsPage: lazyWithRetry(() => import('../../pages/notifications/NotificationsPage')),
  // Settings pages
  SettingsPage: lazyWithRetry(() => import('../../pages/settings/SettingsPage')),
  // User pages
  UsersPage: lazyWithRetry(() => import('../../pages/users/UsersPage')),
  UserDetailPage: lazyWithRetry(() => import('../../pages/users/UserDetailPage')),
  UserFormPage: lazyWithRetry(() => import('../../pages/users/UserFormPage')),
  // Profile pages
  ProfilePage: lazyWithRetry(() => import('../../pages/profile/ProfilePage')),
  // Analytics pages
  AnalyticsDashboardPage: lazyWithRetry(() => import('../../pages/analytics/AnalyticsDashboardPage')),
  BeneficiaryAnalyticsPage: lazyWithRetry(() => import('../../pages/analytics/BeneficiaryAnalyticsPage')),
  ProgramAnalyticsPage: lazyWithRetry(() => import('../../pages/analytics/ProgramAnalyticsPage')),
  // Reports pages
  ReportsDashboardPage: lazyWithRetry(() => import('../../pages/reports/ReportsDashboardPage')),
  ReportCreationPage: lazyWithRetry(() => import('../../pages/reports/ReportCreationPage')),
  // Portal pages
  PortalDashboardPage: lazyWithRetry(() => import('../../pages/portal/PortalDashboardPage')),
  PortalCoursesPage: lazyWithRetry(() => import('../../pages/portal/PortalCoursesPage')),
  PortalProgressPage: lazyWithRetry(() => import('../../pages/portal/PortalProgressPage')),
  PortalResourcesPage: lazyWithRetry(() => import('../../pages/portal/PortalResourcesPage')),
};
// Route-based code splitting wrapper
export const LazyRoute = ({ component: Component, ...props }) => (
  <LazyBoundary>
    <Suspense fallback={<PageLoadingFallback />}>
      <Component {...props} />
    </Suspense>
  </LazyBoundary>
);
// Preload critical routes
export const preloadCriticalRoutes = () => {
  // Preload dashboard and common pages
  preloadComponent(() => import('../../pages/dashboard/DashboardPage'));
  preloadComponent(() => import('../../pages/beneficiaries/BeneficiariesPage'));
  preloadComponent(() => import('../../pages/programs/ProgramsListPage'));
};
// Resource hints for critical assets
export const ResourceHints = () => (
  <>
    {/* Preconnect to API server */}
    <link rel="preconnect" href={import.meta.env.VITE_API_URL || 'http://localhost:5000'} />
    {/* DNS prefetch for external resources */}
    <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
    <link rel="dns-prefetch" href="https://fonts.gstatic.com" />
    {/* Preload critical fonts */}
    <link
      rel="preload"
      href="/fonts/inter-var.woff2"
      as="font"
      type="font/woff2"
      crossOrigin="anonymous"
    />
  </>
);
// Performance observer for monitoring
export const setupPerformanceObserver = () => {
  if ('PerformanceObserver' in window) {
    // Monitor long tasks
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) {
            console.warn('Long task detected:', {
              duration: entry.duration,
              startTime: entry.startTime,
              name: entry.name,
            });
          }
        }
      });
      observer.observe({ entryTypes: ['longtask'] });
    } catch (e) {
      console.error('Failed to setup performance observer:', e);
    }
    // Monitor layout shifts
    try {
      const observer = new PerformanceObserver((list) => {
        let clsValue = 0;
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        }
        if (clsValue > 0.1) {
          console.warn('High CLS detected:', clsValue);
        }
      });
      observer.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      console.error('Failed to setup CLS observer:', e);
    }
    // Monitor largest contentful paint
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
      });
      observer.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      console.error('Failed to setup LCP observer:', e);
    }
  }
};
// Export utility to measure component render time
export const measureComponentPerformance = (componentName) => {
  if (process.env.NODE_ENV === 'development') {
    return {
      onRender: (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
        // Performance timing for development
        if (process.env.NODE_ENV === 'development') {
            :`, {
            actualDuration,
            baseDuration,
            startTime,
            commitTime,
          });
        }
      },
    };
  }
  return {};
};