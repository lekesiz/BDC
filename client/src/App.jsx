import { Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './components/ui/toast';
import { useAuth } from './hooks/useAuth';
import ProtectedRoute from './components/common/ProtectedRoute';
import RoleBasedRedirect from './components/common/RoleBasedRedirect';
import TestLogin from './TestLogin';
import TestAuth from './TestAuth';
import { SocketProvider } from './contexts/SocketContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Layouts
import DashboardLayout from './components/layout/DashboardLayout';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';

// Beneficiary Pages
import BeneficiariesPage from './pages/beneficiaries/BeneficiariesPage';
import BeneficiaryDetailPage from './pages/beneficiaries/BeneficiaryDetailPage';
import BeneficiaryFormPage from './pages/beneficiaries/BeneficiaryFormPage';
import TrainerAssignmentPage from './pages/beneficiaries/TrainerAssignmentPage';
import ProgressTrackingPage from './pages/beneficiaries/ProgressTrackingPage';

// User Pages
import ProfilePage from './pages/profile/ProfilePage';
import SettingsPage from './pages/settings/SettingsPage';
import UsersPage from './pages/users/UsersPage';
import UserFormPage from './pages/users/UserFormPage';
import UserDetailPage from './pages/users/UserDetailPage';
import ThemeSettingsPage from './pages/settings/ThemeSettingsPage';

// Admin Pages
import TenantsPage from './pages/admin/TenantsPage';
import TenantDetailPage from './pages/admin/TenantDetailPage';
import TenantEditPage from './pages/admin/TenantEditPage';
import DatabaseOptimizationPage from './pages/admin/DatabaseOptimizationPage';
import CachingSystemPage from './pages/admin/CachingSystemPage';
import ImageOptimizationPage from './pages/admin/ImageOptimizationPage';
import CodeSplittingPage from './pages/admin/CodeSplittingPage';
import LazyLoadingPage from './pages/admin/LazyLoadingPage';
import CompressionPage from './pages/admin/CompressionPage';
import CDNSetupPage from './pages/admin/CDNSetupPage';
import PerformanceMonitoringPage from './pages/admin/PerformanceMonitoringPage';

// Integration Pages
import GoogleCalendarIntegrationV2Page from './pages/integrations/GoogleCalendarIntegrationV2Page';
import WedofIntegrationPage from './pages/integrations/WedofIntegrationPage';
import PennylaneIntegrationPage from './pages/integrations/PennylaneIntegrationPage';
import EmailIntegrationPage from './pages/integrations/EmailIntegrationPage';
import SMSIntegrationPage from './pages/integrations/SMSIntegrationPage';
import PaymentIntegrationPage from './pages/integrations/PaymentIntegrationPage';
import WebhooksPage from './pages/integrations/WebhooksPage';
import ZapierIntegrationPage from './pages/integrations/ZapierIntegrationPage';

// Evaluation Pages
import EvaluationsPage from './pages/evaluation/EvaluationsPage';
import MyEvaluationsPage from './pages/evaluation/MyEvaluationsPage';
import TestCreationPage from './pages/evaluation/TestCreationPage';
import TestSessionPage from './pages/evaluation/TestSessionPage';
import TestResultsPage from './pages/evaluation/TestResultsPage';
import AIAnalysisPage from './pages/evaluation/AIAnalysisPage';
import TrainerEvaluationPage from './pages/evaluation/TrainerEvaluationPage';
import TrainerEvaluationDetailPage from './pages/evaluation/TrainerEvaluationDetailPage';
import EssayGradingPage from './pages/evaluation/EssayGradingPage';

// Calendar Page
import CalendarPage from './pages/calendar/CalendarPage';
import AvailabilitySettingsPage from './pages/calendar/AvailabilitySettingsPage';
import GoogleCalendarSyncPage from './pages/calendar/GoogleCalendarSyncPage';
import CalendarPageV2 from './pages/calendar/CalendarPageV2';
import AvailabilitySettingsPageV2 from './pages/calendar/AvailabilitySettingsPageV2';
import GoogleCalendarSyncPageV2 from './pages/calendar/GoogleCalendarSyncPageV2';
import GoogleCalendarIntegrationPage from './pages/calendar/GoogleCalendarIntegrationPage';
import EmailRemindersPage from './pages/calendar/EmailRemindersPage';

// Document Pages
import DocumentsPage from './pages/document/DocumentsPage';
import MyDocumentsPage from './pages/document/MyDocumentsPage';
import DocumentDetailPage from './pages/document/DocumentDetailPage';
import DocumentSharePage from './pages/document/DocumentSharePage';
import DocumentUploadPage from './pages/document/DocumentUploadPage';
import DocumentUploadPageV2 from './pages/document/DocumentUploadPageV2';
import DocumentViewerPageV2 from './pages/document/DocumentViewerPageV2';
import DocumentCategoriesPageV2 from './pages/document/DocumentCategoriesPageV2';
import DocumentSharePageV2 from './pages/document/DocumentSharePageV2';
import DocumentTemplatesPage from './pages/document/DocumentTemplatesPage';

// Messaging and Notifications
import MessagingPage from './pages/messaging/MessagingPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import NotificationSettingsPage from './pages/settings/NotificationSettingsPage';
import MessagingPageV2 from './pages/messaging/MessagingPageV2';
import NotificationCenterV2 from './pages/notifications/NotificationCenterV2';
import NotificationPreferencesPageV2 from './pages/settings/NotificationPreferencesPageV2';
import NotificationProviderV2 from './providers/NotificationProviderV2';
import ThemeProvider from './providers/ThemeProvider';
import GlobalErrorHandler from './components/common/GlobalErrorHandler';

// Dashboard
import DashboardPage from './pages/dashboard/DashboardPage';
import DashboardPageV3 from './pages/dashboard/DashboardPageV3';
import DashboardPageEnhanced from './pages/dashboard/DashboardPageEnhanced';

// Test Pages
import WebSocketTestPage from './pages/test/WebSocketTestPage';
import NotificationTestPage from './pages/test/NotificationTestPage';

// Analytics
import AnalyticsDashboardPage from './pages/analytics/AnalyticsDashboardPage';
import TrainerAnalyticsPage from './pages/analytics/TrainerAnalyticsPage';
import ProgramAnalyticsPage from './pages/analytics/ProgramAnalyticsPage';
import ProgramAnalyticsPageV2 from './pages/analytics/ProgramAnalyticsPageV2';
import BeneficiaryAnalyticsPage from './pages/analytics/BeneficiaryAnalyticsPage';

// Reports
import ReportsDashboardPage from './pages/reports/ReportsDashboardPage';
import ReportCreationPage from './pages/reports/ReportCreationPage';
import ReportSchedulePage from './pages/reports/ReportSchedulePage';

// Programs
import ProgramsListPage from './pages/programs/ProgramsListPage';
import CreateProgramPage from './pages/programs/CreateProgramPage';
import EditProgramPage from './pages/programs/EditProgramPage';
import ProgramDetailPage from './pages/programs/ProgramDetailPage';
import AssignBeneficiariesPage from './pages/programs/AssignBeneficiariesPage';
import ProgramSchedulePage from './pages/programs/ProgramSchedulePage';

// AI Pages
import AIInsightsPage from './pages/ai/AIInsightsPage';
import AIRecommendationsPage from './pages/ai/AIRecommendationsPage';
import AIContentGenerationPage from './pages/ai/AIContentGenerationPage';
import AIPerformancePredictionsPage from './pages/ai/AIPerformancePredictionsPage';
import AILearningPathPage from './pages/ai/AILearningPathPage';
import AIAutomatedFeedbackPage from './pages/ai/AIAutomatedFeedbackPage';
import AIChatbotPage from './pages/ai/AIChatbotPage';
import NaturalLanguageProcessingPage from './pages/ai/NaturalLanguageProcessingPage';

// Compliance Pages
import GDPRCompliancePage from './pages/compliance/GDPRCompliancePage';
import DataBackupPage from './pages/compliance/DataBackupPage';
import AuditLogsPage from './pages/compliance/AuditLogsPage';
import SecurityHeadersPage from './pages/compliance/SecurityHeadersPage';
import InputValidationPage from './pages/compliance/InputValidationPage';

// Student Portal
import PortalDashboardPage from './pages/portal/PortalDashboardPage';
import PortalDashboardV2 from './pages/portal/PortalDashboardV2';
import PortalDashboardV3 from './pages/portal/PortalDashboardV3';
import PortalCoursesPage from './pages/portal/PortalCoursesPage';
import PortalModuleDetailPage from './pages/portal/PortalModuleDetailPage';
import PortalCalendarPage from './pages/portal/PortalCalendarPage';
import PortalResourcesPage from './pages/portal/PortalResourcesPage';
import PortalAchievementsPage from './pages/portal/PortalAchievementsPage';
import PortalProfilePage from './pages/portal/PortalProfilePage';
import PortalSkillsPage from './pages/portal/PortalSkillsPage';
import PortalProgressPage from './pages/portal/PortalProgressPage';
import PortalNotificationsPage from './pages/portal/PortalNotificationsPage';
import PortalAssessmentsPage from './pages/portal/assessment/PortalAssessmentsPage';
import PortalQuizPage from './pages/portal/assessment/PortalQuizPage';
import PortalAssessmentResultsPage from './pages/portal/assessment/PortalAssessmentResultsPage';
import PortalAssessmentSubmissionPage from './pages/portal/assessment/PortalAssessmentSubmissionPage';

// Trainer Assessment Pages
import TrainerAssessmentsPage from './pages/assessment/TrainerAssessmentsPage';
import TrainerAssessmentResultsPage from './pages/assessment/TrainerAssessmentResultsPage';
import TrainerSubmissionDetailPage from './pages/assessment/TrainerSubmissionDetailPage';
import TrainerAssessmentTemplateDetailPage from './pages/assessment/TrainerAssessmentTemplateDetailPage';
import TrainerAssessmentCreationPage from './pages/assessment/TrainerAssessmentCreationPage';
import TrainerAssessmentEditPage from './pages/assessment/TrainerAssessmentEditPage';
import TrainerAssignAssessmentPage from './pages/assessment/TrainerAssignAssessmentPage';
import TrainerAssignedAssessmentDetailPage from './pages/assessment/TrainerAssignedAssessmentDetailPage';
import TrainerAssessmentPreviewPage from './pages/assessment/TrainerAssessmentPreviewPage';
import TrainerAssignedAssessmentEditPage from './pages/assessment/TrainerAssignedAssessmentEditPage';
import TrainerAssessmentStatisticsPage from './pages/assessment/TrainerAssessmentStatisticsPage';
import TrainerQuestionBankPage from './pages/assessment/TrainerQuestionBankPage';
import TrainerBulkGradingPage from './pages/assessment/TrainerBulkGradingPage';
import TrainerRubricBuilderPage from './pages/assessment/TrainerRubricBuilderPage';

// Improved Evaluation Pages
import TestCreationPageV2 from './pages/evaluation/TestCreationPageV2';
import TestResultsPageV2 from './pages/evaluation/TestResultsPageV2';
import AIAnalysisPageV2 from './pages/evaluation/AIAnalysisPageV2';

function App() {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <ThemeProvider>
      <ToastProvider>
        <GlobalErrorHandler />
        <NotificationProviderV2>
          <SocketProvider>
            <Routes>
        {/* Test routes */}
        <Route path="/test-login" element={<TestLogin />} />
        <Route path="/test-auth" element={<TestAuth />} />
        
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* Protected routes within dashboard layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<RoleBasedRedirect />} />
          <Route path="dashboard" element={<Navigate to="/" replace />} />

          {/* User routes */}
          <Route path="profile" element={<ProfilePage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="settings/theme" element={<ThemeSettingsPage />} />
          <Route path="users">
            <Route index element={<UsersPage />} />
            <Route path="create" element={<UserFormPage />} />
            <Route path=":id" element={<UserDetailPage />} />
            <Route path=":id/edit" element={<UserFormPage />} />
          </Route>

          {/* Beneficiary routes */}
          <Route path="beneficiaries">
            <Route
              index
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <BeneficiariesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <BeneficiaryDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="new"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <BeneficiaryFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id/edit"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <BeneficiaryFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id/trainers"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssignmentPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id/progress"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <ProgressTrackingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id/evaluate"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerEvaluationPage />
                </ProtectedRoute>
              }
            />
            {/* Add other beneficiary routes as they are developed */}
          </Route>

          {/* My Evaluations route for students */}
          <Route 
            path="my-evaluations" 
            element={
              <ProtectedRoute requiredRole={['student']}>
                <MyEvaluationsPage />
              </ProtectedRoute>
            } 
          />

          {/* My Documents route for students */}
          <Route 
            path="my-documents" 
            element={
              <ProtectedRoute requiredRole={['student']}>
                <MyDocumentsPage />
              </ProtectedRoute>
            } 
          />

          {/* Trainer Assessment Management routes */}
          <Route path="assessment">
            <Route
              index
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="create"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentCreationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="edit/:id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentEditPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="templates/:id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentTemplateDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="templates/:id/preview"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentPreviewPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="assign/:id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssignAssessmentPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="assigned/:id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssignedAssessmentDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="assigned/:id/edit"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssignedAssessmentEditPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="assigned/:id/results"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentResultsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="statistics"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerAssessmentStatisticsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="submissions/:id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerSubmissionDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="bulk-grading"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerBulkGradingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="rubrics/new"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerRubricBuilderPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="rubrics/:rubricId/edit"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerRubricBuilderPage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Evaluation routes */}
          <Route path="evaluations">
            <Route
              index
              element={
                <ProtectedRoute>
                  <EvaluationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="create"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TestCreationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id"
              element={
                <ProtectedRoute>
                  <TestCreationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id/edit"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TestCreationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="sessions/:id"
              element={
                <ProtectedRoute>
                  <TestSessionPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="sessions/:id/results"
              element={
                <ProtectedRoute>
                  <TestResultsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="sessions/:id/analysis"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIAnalysisPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="sessions/:sessionId/grade-essays"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <EssayGradingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="trainer-evaluations/:id"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TrainerEvaluationDetailPage />
                </ProtectedRoute>
              }
            />
            
            {/* Improved V2 Routes */}
            <Route
              path="tests/new-v2"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TestCreationPageV2 />
                </ProtectedRoute>
              }
            />
            <Route
              path="tests/:id/edit-v2"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TestCreationPageV2 />
                </ProtectedRoute>
              }
            />
            <Route
              path="sessions/:sessionId/results-v2"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <TestResultsPageV2 />
                </ProtectedRoute>
              }
            />
            <Route
              path="sessions/:sessionId/analysis-v2"
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIAnalysisPageV2 />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Calendar routes */}
          <Route path="calendar">
            <Route index element={<CalendarPage />} />
            <Route path="availability" element={<AvailabilitySettingsPage />} />
            <Route path="google-sync" element={<GoogleCalendarSyncPage />} />
            <Route path="google-integration" element={<GoogleCalendarIntegrationPage />} />
            <Route path="email-reminders" element={<EmailRemindersPage />} />
            
            {/* V2 Calendar Routes */}
            <Route path="v2" element={<CalendarPageV2 />} />
            <Route path="v2/availability" element={<AvailabilitySettingsPageV2 />} />
            <Route path="v2/google-sync" element={<GoogleCalendarSyncPageV2 />} />
          </Route>
          
          {/* Document routes */}
          <Route path="documents">
            <Route index element={<DocumentsPage />} />
            <Route path=":id" element={<DocumentDetailPage />} />
            <Route path=":id/edit" element={<DocumentUploadPage />} />
            <Route path=":id/share" element={<DocumentSharePage />} />
            <Route path="upload" element={<DocumentUploadPage />} />
            <Route path="share" element={<DocumentSharePage />} />
            
            {/* V2 Document Routes */}
            <Route path="v2/upload" element={<DocumentUploadPageV2 />} />
            <Route path="v2/:id" element={<DocumentViewerPageV2 />} />
            <Route path="v2/categories" element={<DocumentCategoriesPageV2 />} />
            <Route path="v2/:id/share" element={<DocumentSharePageV2 />} />
            <Route path="templates" element={<DocumentTemplatesPage />} />
          </Route>
          
          {/* Messaging and Notifications routes */}
          <Route path="messaging" element={<MessagingPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="settings/notifications" element={<NotificationSettingsPage />} />
          
          {/* V2 Messaging and Notifications Routes */}
          <Route path="messaging/v2" element={<MessagingPageV2 />} />
          <Route path="notifications/v2" element={<NotificationCenterV2 />} />
          <Route path="settings/notifications/v2" element={<NotificationPreferencesPageV2 />} />
          
          {/* Analytics routes */}
          <Route path="analytics">
            <Route index element={<AnalyticsDashboardPage />} />
            <Route path="trainers" element={<TrainerAnalyticsPage />} />
            <Route path="trainers/:id" element={<TrainerAnalyticsPage />} />
            <Route path="programs" element={<ProgramAnalyticsPage />} />
            <Route path="programs/:id" element={<ProgramAnalyticsPageV2 />} />
            <Route path="beneficiaries" element={<BeneficiaryAnalyticsPage />} />
            <Route path="beneficiaries/:id" element={<BeneficiaryAnalyticsPage />} />
          </Route>
          
          {/* Admin routes */}
          <Route path="admin">
            <Route path="users" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <UsersPage />
              </ProtectedRoute>
            } />
            <Route path="tenants" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <TenantsPage />
              </ProtectedRoute>
            } />
            <Route path="tenants/:id" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <TenantDetailPage />
              </ProtectedRoute>
            } />
            <Route path="tenants/:id/edit" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <TenantEditPage />
              </ProtectedRoute>
            } />
            <Route path="database-optimization" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <DatabaseOptimizationPage />
              </ProtectedRoute>
            } />
            <Route path="caching-system" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <CachingSystemPage />
              </ProtectedRoute>
            } />
            <Route path="image-optimization" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <ImageOptimizationPage />
              </ProtectedRoute>
            } />
            <Route path="code-splitting" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <CodeSplittingPage />
              </ProtectedRoute>
            } />
            <Route path="lazy-loading" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <LazyLoadingPage />
              </ProtectedRoute>
            } />
            <Route path="compression" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <CompressionPage />
              </ProtectedRoute>
            } />
            <Route path="cdn-setup" element={
              <ProtectedRoute requiredRole={['super_admin']}>
                <CDNSetupPage />
              </ProtectedRoute>
            } />
            <Route path="performance-monitoring" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <PerformanceMonitoringPage />
              </ProtectedRoute>
            } />
          </Route>
          
          {/* Reports routes */}
          <Route path="reports">
            <Route index element={<ReportsDashboardPage />} />
            <Route path="create" element={<ReportCreationPage />} />
            <Route path=":id" element={<ReportCreationPage />} />
            <Route path=":id/edit" element={<ReportCreationPage />} />
            <Route path=":id/run" element={<ReportCreationPage />} />
            <Route path="schedules/create" element={<ReportSchedulePage />} />
            <Route path="schedules/:id" element={<ReportSchedulePage />} />
            <Route path="schedules/:id/edit" element={<ReportSchedulePage />} />
          </Route>
          
          {/* Integrations routes */}
          <Route path="integrations">
            <Route path="google-calendar" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <GoogleCalendarIntegrationV2Page />
              </ProtectedRoute>
            } />
            <Route path="wedof" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <WedofIntegrationPage />
              </ProtectedRoute>
            } />
            <Route path="pennylane" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <PennylaneIntegrationPage />
              </ProtectedRoute>
            } />
            <Route path="email" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <EmailIntegrationPage />
              </ProtectedRoute>
            } />
            <Route path="sms" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <SMSIntegrationPage />
              </ProtectedRoute>
            } />
            <Route path="payment" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <PaymentIntegrationPage />
              </ProtectedRoute>
            } />
            <Route path="webhooks" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <WebhooksPage />
              </ProtectedRoute>
            } />
            <Route path="zapier" element={
              <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                <ZapierIntegrationPage />
              </ProtectedRoute>
            } />
          </Route>
          
          {/* Programs routes */}
          <Route path="programs">
            <Route 
              index 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <ProgramsListPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="new" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <CreateProgramPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path=":id" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer', 'student']}>
                  <ProgramDetailPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path=":id/edit" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <EditProgramPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path=":id/beneficiaries" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AssignBeneficiariesPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path=":id/schedule" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <ProgramSchedulePage />
                </ProtectedRoute>
              } 
            />
          </Route>
          
          {/* AI routes */}
          <Route path="ai">
            <Route 
              path="insights" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIInsightsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="recommendations" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIRecommendationsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="content-generation" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIContentGenerationPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="performance-predictions" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIPerformancePredictionsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="learning-paths" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AILearningPathPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="automated-feedback" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <AIAutomatedFeedbackPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="assistant" 
              element={
                <ProtectedRoute>
                  <AIChatbotPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="nlp" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
                  <NaturalLanguageProcessingPage />
                </ProtectedRoute>
              } 
            />
          </Route>
          
          {/* Compliance routes */}
          <Route path="compliance">
            <Route 
              path="gdpr" 
              element={
                <ProtectedRoute>
                  <GDPRCompliancePage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="backup" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                  <DataBackupPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="audit-logs" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                  <AuditLogsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="security-headers" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                  <SecurityHeadersPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="input-validation" 
              element={
                <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
                  <InputValidationPage />
                </ProtectedRoute>
              } 
            />
          </Route>
          
          {/* Student Portal routes */}
          <Route path="portal">
            <Route index element={<PortalDashboardV3 />} />
            <Route path="courses" element={<PortalCoursesPage />} />
            <Route path="courses/:id" element={<PortalCoursesPage />} />
            <Route path="modules/:id" element={<PortalModuleDetailPage />} />
            <Route path="calendar" element={<PortalCalendarPage />} />
            <Route path="sessions/:id" element={<PortalCalendarPage />} />
            <Route path="resources" element={<PortalResourcesPage />} />
            <Route path="achievements" element={<PortalAchievementsPage />} />
            <Route path="profile" element={<PortalProfilePage />} />
            <Route path="skills" element={<PortalSkillsPage />} />
            <Route path="progress" element={<PortalProgressPage />} />
            <Route path="notifications" element={<PortalNotificationsPage />} />
            <Route path="assessment" element={<PortalAssessmentsPage />} />
            <Route path="assessment/quiz/:assessmentId/:assignmentId" element={<PortalQuizPage />} />
            <Route path="assessment/submit/:assessmentId/:assignmentId" element={<PortalAssessmentSubmissionPage />} />
            <Route path="assessment/results/:assessmentId/:assignmentId" element={<PortalAssessmentResultsPage />} />
          </Route>
          
          {/* Test routes */}
          <Route path="test/websocket" element={<WebSocketTestPage />} />
          <Route path="test/notifications" element={<NotificationTestPage />} />
        </Route>

        {/* Error routes */}
        <Route path="/unauthorized" element={<div>Unauthorized</div>} />
        <Route path="*" element={<div>Page Not Found</div>} />
      </Routes>
          </SocketProvider>
        </NotificationProviderV2>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;