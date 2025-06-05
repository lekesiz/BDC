/**
 * Code splitting utilities for React applications
 */
import React, { lazy, Suspense } from 'react';
import { LinearProgress, CircularProgress } from '@mui/material';
/**
 * Loading fallback components
 */
export const LoadingFallbacks = {
  // Full page loader
  FullPage: () => (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}>
      <CircularProgress />
    </div>
  ),
  // Inline loader
  Inline: () => (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <CircularProgress size={24} />
    </div>
  ),
  // Linear progress bar
  Linear: () => (
    <LinearProgress />
  ),
  // Custom skeleton loader
  Skeleton: ({ height = 200 }) => (
    <div style={{
      height,
      background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
      backgroundSize: '200% 100%',
      animation: 'loading 1.5s infinite'
    }} />
  )
};
/**
 * Route-based code splitting
 */
export const routeBasedSplitting = {
  // Lazy load route components
  routes: {
    // Authentication routes
    Login: lazy(() => import('../../pages/auth/LoginPage')),
    Register: lazy(() => import('../../pages/auth/RegisterPage')),
    ForgotPassword: lazy(() => import('../../pages/auth/ForgotPasswordPage')),
    // Dashboard routes
    Dashboard: lazy(() => import('../../pages/dashboard/DashboardPage')),
    AdminDashboard: lazy(() => import('../../pages/dashboard/AdminDashboard')),
    TrainerDashboard: lazy(() => import('../../pages/dashboard/TrainerDashboard')),
    StudentDashboard: lazy(() => import('../../pages/dashboard/StudentDashboard')),
    // User management
    UserList: lazy(() => import('../../pages/users/UserListPage')),
    UserProfile: lazy(() => import('../../pages/users/UserProfilePage')),
    UserEdit: lazy(() => import('../../pages/users/UserEditPage')),
    // Beneficiary management
    BeneficiaryList: lazy(() => import('../../pages/beneficiaries/BeneficiaryListPage')),
    BeneficiaryDetail: lazy(() => import('../../pages/beneficiaries/BeneficiaryDetailPage')),
    BeneficiaryForm: lazy(() => import('../../pages/beneficiaries/BeneficiaryFormPage')),
    // Assessment system
    AssessmentList: lazy(() => import('../../pages/assessments/AssessmentListPage')),
    AssessmentCreate: lazy(() => import('../../pages/assessments/AssessmentCreatePage')),
    AssessmentTake: lazy(() => import('../../pages/assessments/AssessmentTakePage')),
    AssessmentResults: lazy(() => import('../../pages/assessments/AssessmentResultsPage')),
    // Documents
    DocumentList: lazy(() => import('../../pages/documents/DocumentListPage')),
    DocumentUpload: lazy(() => import('../../pages/documents/DocumentUploadPage')),
    DocumentViewer: lazy(() => import('../../pages/documents/DocumentViewerPage')),
    // Reports
    Reports: lazy(() => import('../../pages/reports/ReportsPage')),
    ReportViewer: lazy(() => import('../../pages/reports/ReportViewerPage')),
    // Settings
    Settings: lazy(() => import('../../pages/settings/SettingsPage')),
    ProfileSettings: lazy(() => import('../../pages/settings/ProfileSettingsPage')),
    SystemSettings: lazy(() => import('../../pages/settings/SystemSettingsPage'))
  },
  /**
   * Create route with code splitting
   */
  createRoute: (path, component, options = {}) => ({
    path,
    element: (
      <Suspense fallback={options.fallback || <LoadingFallbacks.FullPage />}>
        {React.createElement(component)}
      </Suspense>
    ),
    ...options
  })
};
/**
 * Component-based code splitting
 */
export const componentBasedSplitting = {
  // Heavy components that should be split
  heavyComponents: {
    // Charts and visualizations
    ChartComponents: {
      LineChart: lazy(() => import('../../components/charts/LineChart')),
      BarChart: lazy(() => import('../../components/charts/BarChart')),
      PieChart: lazy(() => import('../../components/charts/PieChart')),
      RadarChart: lazy(() => import('../../components/charts/RadarChart')),
      Dashboard: lazy(() => import('../../components/analytics/AnalyticsDashboard'))
    },
    // Rich text editors
    Editors: {
      RichTextEditor: lazy(() => import('../../components/editors/RichTextEditor')),
      MarkdownEditor: lazy(() => import('../../components/editors/MarkdownEditor')),
      CodeEditor: lazy(() => import('../../components/editors/CodeEditor'))
    },
    // File handling
    FileHandlers: {
      FileUploader: lazy(() => import('../../components/upload/FileUploader')),
      ImageCropper: lazy(() => import('../../components/upload/ImageCropper')),
      PDFViewer: lazy(() => import('../../components/viewers/PDFViewer'))
    },
    // Complex forms
    Forms: {
      AssessmentBuilder: lazy(() => import('../../components/forms/AssessmentBuilder')),
      SurveyBuilder: lazy(() => import('../../components/forms/SurveyBuilder')),
      FormBuilder: lazy(() => import('../../components/forms/FormBuilder'))
    }
  },
  /**
   * Wrap component with lazy loading
   */
  withLazyLoading: (importFunc, fallback = <LoadingFallbacks.Inline />) => {
    const LazyComponent = lazy(importFunc);
    return (props) => (
      <Suspense fallback={fallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  }
};
/**
 * Library-based code splitting
 */
export const libraryBasedSplitting = {
  // Split large libraries into separate chunks
  libraries: {
    // Chart libraries
    chartLibraries: () => ({
      recharts: () => import('recharts'),
      chartjs: () => import('chart.js'),
      d3: () => import('d3')
    }),
    // Date/time libraries
    dateLibraries: () => ({
      moment: () => import('moment'),
      dateFns: () => import('date-fns'),
      dayjs: () => import('dayjs')
    }),
    // Rich content libraries
    contentLibraries: () => ({
      quill: () => import('quill'),
      draftJs: () => import('draft-js'),
      slate: () => import('slate')
    }),
    // Utility libraries
    utilityLibraries: () => ({
      lodash: () => import('lodash'),
      ramda: () => import('ramda'),
      axios: () => import('axios')
    })
  },
  /**
   * Dynamic import with error handling
   */
  dynamicImport: async (library, retries = 3) => {
    let attempt = 0;
    while (attempt < retries) {
      try {
        const module = await library();
        return module;
      } catch (error) {
        attempt++;
        if (attempt === retries) {
          console.error(`Failed to load library after ${retries} attempts:`, error);
          throw error;
        }
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }
};
/**
 * Advanced code splitting strategies
 */
export const advancedStrategies = {
  /**
   * Intersection Observer based loading
   */
  intersectionObserverLoading: (componentImport, options = {}) => {
    const LazyComponent = lazy(componentImport);
    return React.forwardRef((props, ref) => {
      const [isIntersecting, setIsIntersecting] = React.useState(false);
      const observerRef = React.useRef(null);
      React.useEffect(() => {
        const observer = new IntersectionObserver(
          ([entry]) => {
            if (entry.isIntersecting) {
              setIsIntersecting(true);
              observer.disconnect();
            }
          },
          {
            rootMargin: options.rootMargin || '50px',
            threshold: options.threshold || 0.01
          }
        );
        if (observerRef.current) {
          observer.observe(observerRef.current);
        }
        return () => observer.disconnect();
      }, []);
      return (
        <div ref={observerRef}>
          {isIntersecting ? (
            <Suspense fallback={options.fallback || <LoadingFallbacks.Skeleton />}>
              <LazyComponent ref={ref} {...props} />
            </Suspense>
          ) : (
            options.placeholder || <LoadingFallbacks.Skeleton />
          )}
        </div>
      );
    });
  },
  /**
   * Prefetch components
   */
  prefetchComponent: (componentImport) => {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        componentImport();
      });
    } else {
      setTimeout(() => {
        componentImport();
      }, 1);
    }
  },
  /**
   * Progressive loading
   */
  progressiveLoading: {
    // Load critical components first
    critical: [
      () => import('../../components/layout/Header'),
      () => import('../../components/layout/Navigation'),
      () => import('../../components/auth/AuthProvider')
    ],
    // Load enhanced features later
    enhanced: [
      () => import('../../components/analytics/AnalyticsDashboard'),
      () => import('../../components/charts/AdvancedCharts'),
      () => import('../../components/ai/AIAssistant')
    ],
    // Load optional features on demand
    optional: [
      () => import('../../components/themes/ThemeCustomizer'),
      () => import('../../components/export/ExportOptions'),
      () => import('../../components/settings/AdvancedSettings')
    ]
  }
};
/**
 * Performance optimization helpers
 */
export const performanceHelpers = {
  /**
   * Measure component load time
   */
  measureLoadTime: (componentName, startTime) => {
    const endTime = performance.now();
    const loadTime = endTime - startTime;
    if (process.env.NODE_ENV === 'development') {
      // Component loaded
    }
    // Report to analytics
    if (window.analytics) {
      window.analytics.track('Component Load Time', {
        component: componentName,
        loadTime: loadTime
      });
    }
  },
  /**
   * Resource hints for preloading
   */
  addResourceHints: (resources) => {
    resources.forEach(resource => {
      const link = document.createElement('link');
      link.rel = resource.rel || 'prefetch';
      link.href = resource.href;
      if (resource.as) {
        link.as = resource.as;
      }
      if (resource.crossOrigin) {
        link.crossOrigin = resource.crossOrigin;
      }
      document.head.appendChild(link);
    });
  },
  /**
   * Bundle size monitor
   */
  monitorBundleSize: () => {
    if (process.env.NODE_ENV === 'development') {
      // Get all script tags
      const scripts = document.getElementsByTagName('script');
      let totalSize = 0;
      Array.from(scripts).forEach(script => {
        if (script.src) {
          fetch(script.src)
            .then(response => response.text())
            .then(content => {
              const size = new Blob([content]).size;
              totalSize += size;
            });
        }
      });
      setTimeout(() => {}, 2000);
    }
  }
};
/**
 * Error boundaries for code splitting
 */
export class CodeSplitErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error('Code splitting error:', error, errorInfo);
    // Report to error tracking service
    if (window.Sentry) {
      window.Sentry.captureException(error);
    }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Failed to load this section</h2>
          <p>Please refresh the page to try again.</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
export default {
  LoadingFallbacks,
  routeBasedSplitting,
  componentBasedSplitting,
  libraryBasedSplitting,
  advancedStrategies,
  performanceHelpers,
  CodeSplitErrorBoundary
};