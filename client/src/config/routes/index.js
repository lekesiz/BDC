// TODO: i18n - processed
/**
 * Centralized route configuration
 * This file consolidates all routes and eliminates duplicates
 */
import { lazy } from 'react';
import { ROUTE_ACCESS, ROLES } from '../roles';
// Lazy load components - using the latest/best versions
import { useTranslation } from "react-i18next";const DashboardPageEnhanced = lazy(() => import('../../pages/dashboard/DashboardPageEnhanced'));
// User Management
const UsersPage = lazy(() => import('../../pages/users/UsersPage'));
const UserFormPage = lazy(() => import('../../pages/users/UserFormPage'));
const UserDetailPage = lazy(() => import('../../pages/users/UserDetailPage'));
const ProfilePage = lazy(() => import('../../pages/profile/ProfilePage'));
// Beneficiary Management - using latest versions
const BeneficiariesPage = lazy(() => import('../../pages/beneficiaries/BeneficiariesPage'));
const BeneficiaryDetailPage = lazy(() => import('../../pages/beneficiaries/BeneficiaryDetailPage'));
const BeneficiaryFormPage = lazy(() => import('../../pages/beneficiaries/BeneficiaryFormPage'));
const TrainerAssignmentPage = lazy(() => import('../../pages/beneficiaries/TrainerAssignmentPage'));
const ProgressTrackingPage = lazy(() => import('../../pages/beneficiaries/ProgressTrackingPage'));
// Evaluation System - using V2 versions where available
const EvaluationsPage = lazy(() => import('../../pages/evaluation/EvaluationsPage'));
const MyEvaluationsPage = lazy(() => import('../../pages/evaluation/MyEvaluationsPage'));
const TestCreationPageV2 = lazy(() => import('../../pages/evaluation/TestCreationPageV2'));
const TestSessionPage = lazy(() => import('../../pages/evaluation/TestSessionPage'));
const TestResultsPageV2 = lazy(() => import('../../pages/evaluation/TestResultsPageV2'));
const AIAnalysisPageV2 = lazy(() => import('../../pages/evaluation/AIAnalysisPageV2'));
const TrainerEvaluationPage = lazy(() => import('../../pages/evaluation/TrainerEvaluationPage'));
const TrainerEvaluationDetailPage = lazy(() => import('../../pages/evaluation/TrainerEvaluationDetailPage'));
const EssayGradingPage = lazy(() => import('../../pages/evaluation/EssayGradingPage'));
// Assessment System (Trainer)
const TrainerAssessmentsPage = lazy(() => import('../../pages/assessment/TrainerAssessmentsPage'));
const TrainerAssessmentCreationPage = lazy(() => import('../../pages/assessment/TrainerAssessmentCreationPage'));
const TrainerAssessmentEditPage = lazy(() => import('../../pages/assessment/TrainerAssessmentEditPage'));
const TrainerAssessmentTemplateDetailPage = lazy(() => import('../../pages/assessment/TrainerAssessmentTemplateDetailPage'));
const TrainerAssessmentPreviewPage = lazy(() => import('../../pages/assessment/TrainerAssessmentPreviewPage'));
const TrainerAssignAssessmentPage = lazy(() => import('../../pages/assessment/TrainerAssignAssessmentPage'));
const TrainerAssignedAssessmentDetailPage = lazy(() => import('../../pages/assessment/TrainerAssignedAssessmentDetailPage'));
const TrainerAssignedAssessmentEditPage = lazy(() => import('../../pages/assessment/TrainerAssignedAssessmentEditPage'));
const TrainerAssessmentResultsPage = lazy(() => import('../../pages/assessment/TrainerAssessmentResultsPage'));
const TrainerAssessmentStatisticsPage = lazy(() => import('../../pages/assessment/TrainerAssessmentStatisticsPage'));
const TrainerSubmissionDetailPage = lazy(() => import('../../pages/assessment/TrainerSubmissionDetailPage'));
const TrainerBulkGradingPage = lazy(() => import('../../pages/assessment/TrainerBulkGradingPage'));
const TrainerRubricBuilderPage = lazy(() => import('../../pages/assessment/TrainerRubricBuilderPage'));
const TrainerQuestionBankPage = lazy(() => import('../../pages/assessment/TrainerQuestionBankPage'));
// Document Management - using V2 where available
const DocumentsPage = lazy(() => import('../../pages/document/DocumentsPage'));
const MyDocumentsPage = lazy(() => import('../../pages/document/MyDocumentsPage'));
const DocumentDetailPage = lazy(() => import('../../pages/document/DocumentDetailPage'));
const DocumentUploadPageV2 = lazy(() => import('../../pages/document/DocumentUploadPageV2'));
const DocumentViewerPageV2 = lazy(() => import('../../pages/document/DocumentViewerPageV2'));
const DocumentSharePageV2 = lazy(() => import('../../pages/document/DocumentSharePageV2'));
const DocumentCategoriesPageV2 = lazy(() => import('../../pages/document/DocumentCategoriesPageV2'));
const DocumentTemplatesPage = lazy(() => import('../../pages/document/DocumentTemplatesPage'));
// Calendar System - using V2 versions
const CalendarPageV2 = lazy(() => import('../../pages/calendar/CalendarPageV2'));
const AvailabilitySettingsPageV2 = lazy(() => import('../../pages/calendar/AvailabilitySettingsPageV2'));
const GoogleCalendarSyncPageV2 = lazy(() => import('../../pages/calendar/GoogleCalendarSyncPageV2'));
const GoogleCalendarIntegrationPage = lazy(() => import('../../pages/calendar/GoogleCalendarIntegrationPage'));
const EmailRemindersPage = lazy(() => import('../../pages/calendar/EmailRemindersPage'));
// Programs
const ProgramsListPage = lazy(() => import('../../pages/programs/ProgramsListPage'));
const CreateProgramPage = lazy(() => import('../../pages/programs/CreateProgramPage'));
const EditProgramPage = lazy(() => import('../../pages/programs/EditProgramPage'));
const ProgramDetailPage = lazy(() => import('../../pages/programs/ProgramDetailPage'));
const AssignBeneficiariesPage = lazy(() => import('../../pages/programs/AssignBeneficiariesPage'));
const ProgramSchedulePage = lazy(() => import('../../pages/programs/ProgramSchedulePage'));
// Messaging & Notifications - using V2 versions
const MessagingPageV2 = lazy(() => import('../../pages/messaging/MessagingPageV2'));
const NotificationCenterV2 = lazy(() => import('../../pages/notifications/NotificationCenterV2'));
// Analytics
const AnalyticsDashboardPage = lazy(() => import('../../pages/analytics/AnalyticsDashboardPage'));
const TrainerAnalyticsPage = lazy(() => import('../../pages/analytics/TrainerAnalyticsPage'));
const ProgramAnalyticsPageV2 = lazy(() => import('../../pages/analytics/ProgramAnalyticsPageV2'));
const BeneficiaryAnalyticsPage = lazy(() => import('../../pages/analytics/BeneficiaryAnalyticsPage'));
// Reports
const ReportsDashboardPage = lazy(() => import('../../pages/reports/ReportsDashboardPage'));
const ReportCreationPage = lazy(() => import('../../pages/reports/ReportCreationPage'));
const ReportSchedulePage = lazy(() => import('../../pages/reports/ReportSchedulePage'));
// Settings - consolidated
const SettingsPage = lazy(() => import('../../pages/settings/SettingsPage'));
const ThemeSettingsPage = lazy(() => import('../../pages/settings/ThemeSettingsPage'));
const NotificationPreferencesPageV2 = lazy(() => import('../../pages/settings/NotificationPreferencesPageV2'));
// Admin Pages
const TenantsPage = lazy(() => import('../../pages/admin/TenantsPage'));
const TenantDetailPage = lazy(() => import('../../pages/admin/TenantDetailPage'));
const TenantEditPage = lazy(() => import('../../pages/admin/TenantEditPage'));
const DatabaseOptimizationPage = lazy(() => import('../../pages/admin/DatabaseOptimizationPage'));
const CachingSystemPage = lazy(() => import('../../pages/admin/CachingSystemPage'));
const ImageOptimizationPage = lazy(() => import('../../pages/admin/ImageOptimizationPage'));
const CodeSplittingPage = lazy(() => import('../../pages/admin/CodeSplittingPage'));
const LazyLoadingPage = lazy(() => import('../../pages/admin/LazyLoadingPage'));
const CompressionPage = lazy(() => import('../../pages/admin/CompressionPage'));
const CDNSetupPage = lazy(() => import('../../pages/admin/CDNSetupPage'));
const PerformanceMonitoringPage = lazy(() => import('../../pages/admin/PerformanceMonitoringPage'));
// Integrations
const GoogleCalendarIntegrationV2Page = lazy(() => import('../../pages/integrations/GoogleCalendarIntegrationV2Page'));
const WedofIntegrationPage = lazy(() => import('../../pages/integrations/WedofIntegrationPage'));
const PennylaneIntegrationPage = lazy(() => import('../../pages/integrations/PennylaneIntegrationPage'));
const EmailIntegrationPage = lazy(() => import('../../pages/integrations/EmailIntegrationPage'));
const SMSIntegrationPage = lazy(() => import('../../pages/integrations/SMSIntegrationPage'));
const PaymentIntegrationPage = lazy(() => import('../../pages/integrations/PaymentIntegrationPage'));
const WebhooksPage = lazy(() => import('../../pages/integrations/WebhooksPage'));
const ZapierIntegrationPage = lazy(() => import('../../pages/integrations/ZapierIntegrationPage'));
// AI Features
const AIInsightsPage = lazy(() => import('../../pages/ai/AIInsightsPage'));
const AIRecommendationsPage = lazy(() => import('../../pages/ai/AIRecommendationsPage'));
const AIContentGenerationPage = lazy(() => import('../../pages/ai/AIContentGenerationPage'));
const AIPerformancePredictionsPage = lazy(() => import('../../pages/ai/AIPerformancePredictionsPage'));
const AILearningPathPage = lazy(() => import('../../pages/ai/AILearningPathPage'));
const AIAutomatedFeedbackPage = lazy(() => import('../../pages/ai/AIAutomatedFeedbackPage'));
const AIChatbotPage = lazy(() => import('../../pages/ai/AIChatbotPage'));
const NaturalLanguageProcessingPage = lazy(() => import('../../pages/ai/NaturalLanguageProcessingPage'));
// Compliance
const GDPRCompliancePage = lazy(() => import('../../pages/compliance/GDPRCompliancePage'));
const DataBackupPage = lazy(() => import('../../pages/compliance/DataBackupPage'));
const AuditLogsPage = lazy(() => import('../../pages/compliance/AuditLogsPage'));
const SecurityHeadersPage = lazy(() => import('../../pages/compliance/SecurityHeadersPage'));
const InputValidationPage = lazy(() => import('../../pages/compliance/InputValidationPage'));
// Student Portal - using V3 dashboard
const PortalDashboardV3 = lazy(() => import('../../pages/portal/PortalDashboardV3'));
const PortalCoursesPage = lazy(() => import('../../pages/portal/PortalCoursesPage'));
const PortalModuleDetailPage = lazy(() => import('../../pages/portal/PortalModuleDetailPage'));
const PortalCalendarPage = lazy(() => import('../../pages/portal/PortalCalendarPage'));
const PortalResourcesPage = lazy(() => import('../../pages/portal/PortalResourcesPage'));
const PortalAchievementsPage = lazy(() => import('../../pages/portal/PortalAchievementsPage'));
const PortalProfilePage = lazy(() => import('../../pages/portal/PortalProfilePage'));
const PortalSkillsPage = lazy(() => import('../../pages/portal/PortalSkillsPage'));
const PortalProgressPage = lazy(() => import('../../pages/portal/PortalProgressPage'));
const PortalNotificationsPage = lazy(() => import('../../pages/portal/PortalNotificationsPage'));
const PortalAssessmentsPage = lazy(() => import('../../pages/portal/assessment/PortalAssessmentsPage'));
const PortalQuizPage = lazy(() => import('../../pages/portal/assessment/PortalQuizPage'));
const PortalAssessmentResultsPage = lazy(() => import('../../pages/portal/assessment/PortalAssessmentResultsPage'));
const PortalAssessmentSubmissionPage = lazy(() => import('../../pages/portal/assessment/PortalAssessmentSubmissionPage'));
// Test Pages
const WebSocketTestPage = lazy(() => import('../../pages/test/WebSocketTestPage'));
const NotificationTestPage = lazy(() => import('../../pages/test/NotificationTestPage'));
const DebugPage = lazy(() => import('../../pages/debug/DebugPage'));
/**
 * Consolidated route configuration
 * Eliminates all duplicate routes and uses latest component versions
 */
export const ROUTE_CONFIG = {
  // Dashboard route (role-based redirection handled in RoleBasedRedirect)
  dashboard: {
    path: '/',
    component: DashboardPageEnhanced,
    access: ROUTE_ACCESS.AUTHENTICATED,
    exact: true
  },
  // User Management Routes
  users: {
    base: '/users',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      list: { path: '', component: UsersPage },
      create: { path: 'create', component: UserFormPage },
      detail: { path: ':id', component: UserDetailPage },
      edit: { path: ':id/edit', component: UserFormPage }
    }
  },
  // Profile (accessible to all users)
  profile: {
    path: '/profile',
    component: ProfilePage,
    access: ROUTE_ACCESS.AUTHENTICATED
  },
  // Beneficiary Management Routes
  beneficiaries: {
    base: '/beneficiaries',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      list: { path: '', component: BeneficiariesPage },
      detail: { path: ':id', component: BeneficiaryDetailPage },
      create: { path: 'new', component: BeneficiaryFormPage },
      edit: { path: ':id/edit', component: BeneficiaryFormPage },
      trainers: { path: ':id/trainers', component: TrainerAssignmentPage },
      progress: { path: ':id/progress', component: ProgressTrackingPage },
      evaluate: { path: ':id/evaluate', component: TrainerEvaluationPage }
    }
  },
  // Student-specific routes
  student: {
    myEvaluations: {
      path: '/my-evaluations',
      component: MyEvaluationsPage,
      access: ROUTE_ACCESS.STUDENT_ONLY
    },
    myDocuments: {
      path: '/my-documents',
      component: MyDocumentsPage,
      access: ROUTE_ACCESS.STUDENT_ONLY
    }
  },
  // Trainer Assessment Management Routes
  assessment: {
    base: '/assessment',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      list: { path: '', component: TrainerAssessmentsPage },
      create: { path: 'create', component: TrainerAssessmentCreationPage },
      edit: { path: 'edit/:id', component: TrainerAssessmentEditPage },
      templates: { path: 'templates/:id', component: TrainerAssessmentTemplateDetailPage },
      preview: { path: 'templates/:id/preview', component: TrainerAssessmentPreviewPage },
      assign: { path: 'assign/:id', component: TrainerAssignAssessmentPage },
      assignedDetail: { path: 'assigned/:id', component: TrainerAssignedAssessmentDetailPage },
      assignedEdit: { path: 'assigned/:id/edit', component: TrainerAssignedAssessmentEditPage },
      results: { path: 'assigned/:id/results', component: TrainerAssessmentResultsPage },
      statistics: { path: 'statistics', component: TrainerAssessmentStatisticsPage },
      submissions: { path: 'submissions/:id', component: TrainerSubmissionDetailPage },
      bulkGrading: { path: 'bulk-grading', component: TrainerBulkGradingPage },
      rubrics: { path: 'rubrics/new', component: TrainerRubricBuilderPage },
      rubricsEdit: { path: 'rubrics/:rubricId/edit', component: TrainerRubricBuilderPage },
      questionBank: { path: 'questions', component: TrainerQuestionBankPage }
    }
  },
  // Evaluation System Routes
  evaluations: {
    base: '/evaluations',
    access: ROUTE_ACCESS.AUTHENTICATED,
    routes: {
      list: { path: '', component: EvaluationsPage },
      create: { path: 'create', component: TestCreationPageV2, access: ROUTE_ACCESS.MANAGEMENT },
      detail: { path: ':id', component: TestCreationPageV2 },
      edit: { path: ':id/edit', component: TestCreationPageV2, access: ROUTE_ACCESS.MANAGEMENT },
      session: { path: 'sessions/:id', component: TestSessionPage },
      results: { path: 'sessions/:id/results', component: TestResultsPageV2 },
      analysis: { path: 'sessions/:id/analysis', component: AIAnalysisPageV2, access: ROUTE_ACCESS.MANAGEMENT },
      gradeEssays: { path: 'sessions/:sessionId/grade-essays', component: EssayGradingPage, access: ROUTE_ACCESS.MANAGEMENT },
      trainerEvaluation: { path: 'trainer-evaluations/:id', component: TrainerEvaluationDetailPage, access: ROUTE_ACCESS.MANAGEMENT }
    }
  },
  // Calendar Routes
  calendar: {
    base: '/calendar',
    access: ROUTE_ACCESS.AUTHENTICATED,
    routes: {
      main: { path: '', component: CalendarPageV2 },
      availability: { path: 'availability', component: AvailabilitySettingsPageV2 },
      googleSync: { path: 'google-sync', component: GoogleCalendarSyncPageV2 },
      googleIntegration: { path: 'google-integration', component: GoogleCalendarIntegrationPage },
      emailReminders: { path: 'email-reminders', component: EmailRemindersPage }
    }
  },
  // Document Management Routes
  documents: {
    base: '/documents',
    access: ROUTE_ACCESS.AUTHENTICATED,
    routes: {
      list: { path: '', component: DocumentsPage },
      detail: { path: ':id', component: DocumentViewerPageV2 },
      upload: { path: 'upload', component: DocumentUploadPageV2 },
      categories: { path: 'categories', component: DocumentCategoriesPageV2 },
      share: { path: ':id/share', component: DocumentSharePageV2 },
      templates: { path: 'templates', component: DocumentTemplatesPage }
    }
  },
  // Messaging & Notifications
  messaging: {
    path: '/messaging',
    component: MessagingPageV2,
    access: ROUTE_ACCESS.AUTHENTICATED
  },
  notifications: {
    path: '/notifications',
    component: NotificationCenterV2,
    access: ROUTE_ACCESS.AUTHENTICATED
  },
  // Analytics Routes
  analytics: {
    base: '/analytics',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      dashboard: { path: '', component: AnalyticsDashboardPage },
      trainers: { path: 'trainers', component: TrainerAnalyticsPage },
      trainerDetail: { path: 'trainers/:id', component: TrainerAnalyticsPage },
      programs: { path: 'programs', component: ProgramAnalyticsPageV2 },
      programDetail: { path: 'programs/:id', component: ProgramAnalyticsPageV2 },
      beneficiaries: { path: 'beneficiaries', component: BeneficiaryAnalyticsPage },
      beneficiaryDetail: { path: 'beneficiaries/:id', component: BeneficiaryAnalyticsPage }
    }
  },
  // Admin Routes (Super Admin and Tenant Admin only)
  admin: {
    base: '/admin',
    access: ROUTE_ACCESS.ADMIN_ONLY,
    routes: {
      users: { path: 'users', component: UsersPage },
      tenants: { path: 'tenants', component: TenantsPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      tenantDetail: { path: 'tenants/:id', component: TenantDetailPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      tenantEdit: { path: 'tenants/:id/edit', component: TenantEditPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      databaseOptimization: { path: 'database-optimization', component: DatabaseOptimizationPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      cachingSystem: { path: 'caching-system', component: CachingSystemPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      imageOptimization: { path: 'image-optimization', component: ImageOptimizationPage },
      codeSplitting: { path: 'code-splitting', component: CodeSplittingPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      lazyLoading: { path: 'lazy-loading', component: LazyLoadingPage },
      compression: { path: 'compression', component: CompressionPage },
      cdnSetup: { path: 'cdn-setup', component: CDNSetupPage, access: { roles: [ROLES.SUPER_ADMIN] } },
      performanceMonitoring: { path: 'performance-monitoring', component: PerformanceMonitoringPage }
    }
  },
  // Reports Routes
  reports: {
    base: '/reports',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      dashboard: { path: '', component: ReportsDashboardPage },
      create: { path: 'create', component: ReportCreationPage },
      detail: { path: ':id', component: ReportCreationPage },
      edit: { path: ':id/edit', component: ReportCreationPage },
      run: { path: ':id/run', component: ReportCreationPage },
      scheduleCreate: { path: 'schedules/create', component: ReportSchedulePage },
      scheduleDetail: { path: 'schedules/:id', component: ReportSchedulePage },
      scheduleEdit: { path: 'schedules/:id/edit', component: ReportSchedulePage }
    }
  },
  // Integrations Routes
  integrations: {
    base: '/integrations',
    access: ROUTE_ACCESS.ADMIN_ONLY,
    routes: {
      googleCalendar: { path: 'google-calendar', component: GoogleCalendarIntegrationV2Page },
      wedof: { path: 'wedof', component: WedofIntegrationPage },
      pennylane: { path: 'pennylane', component: PennylaneIntegrationPage },
      email: { path: 'email', component: EmailIntegrationPage },
      sms: { path: 'sms', component: SMSIntegrationPage },
      payment: { path: 'payment', component: PaymentIntegrationPage },
      webhooks: { path: 'webhooks', component: WebhooksPage },
      zapier: { path: 'zapier', component: ZapierIntegrationPage }
    }
  },
  // Programs Routes
  programs: {
    base: '/programs',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      list: { path: '', component: ProgramsListPage },
      create: { path: 'new', component: CreateProgramPage },
      detail: { path: ':id', component: ProgramDetailPage, access: ROUTE_ACCESS.AUTHENTICATED },
      edit: { path: ':id/edit', component: EditProgramPage },
      beneficiaries: { path: ':id/beneficiaries', component: AssignBeneficiariesPage },
      schedule: { path: ':id/schedule', component: ProgramSchedulePage }
    }
  },
  // AI Features Routes
  ai: {
    base: '/ai',
    access: ROUTE_ACCESS.MANAGEMENT,
    routes: {
      insights: { path: 'insights', component: AIInsightsPage },
      recommendations: { path: 'recommendations', component: AIRecommendationsPage },
      contentGeneration: { path: 'content-generation', component: AIContentGenerationPage },
      performancePredictions: { path: 'performance-predictions', component: AIPerformancePredictionsPage },
      learningPaths: { path: 'learning-paths', component: AILearningPathPage },
      automatedFeedback: { path: 'automated-feedback', component: AIAutomatedFeedbackPage },
      assistant: { path: 'assistant', component: AIChatbotPage, access: ROUTE_ACCESS.AUTHENTICATED },
      nlp: { path: 'nlp', component: NaturalLanguageProcessingPage }
    }
  },
  // Compliance Routes
  compliance: {
    base: '/compliance',
    access: ROUTE_ACCESS.AUTHENTICATED,
    routes: {
      gdpr: { path: 'gdpr', component: GDPRCompliancePage },
      backup: { path: 'backup', component: DataBackupPage, access: ROUTE_ACCESS.ADMIN_ONLY },
      auditLogs: { path: 'audit-logs', component: AuditLogsPage, access: ROUTE_ACCESS.ADMIN_ONLY },
      securityHeaders: { path: 'security-headers', component: SecurityHeadersPage, access: ROUTE_ACCESS.ADMIN_ONLY },
      inputValidation: { path: 'input-validation', component: InputValidationPage, access: ROUTE_ACCESS.ADMIN_ONLY }
    }
  },
  // Student Portal Routes
  portal: {
    base: '/portal',
    access: ROUTE_ACCESS.STUDENT_ONLY,
    routes: {
      dashboard: { path: '', component: PortalDashboardV3 },
      courses: { path: 'courses', component: PortalCoursesPage },
      courseDetail: { path: 'courses/:id', component: PortalCoursesPage },
      moduleDetail: { path: 'modules/:id', component: PortalModuleDetailPage },
      calendar: { path: 'calendar', component: PortalCalendarPage },
      session: { path: 'sessions/:id', component: PortalCalendarPage },
      resources: { path: 'resources', component: PortalResourcesPage },
      achievements: { path: 'achievements', component: PortalAchievementsPage },
      profile: { path: 'profile', component: PortalProfilePage },
      skills: { path: 'skills', component: PortalSkillsPage },
      progress: { path: 'progress', component: PortalProgressPage },
      notifications: { path: 'notifications', component: PortalNotificationsPage },
      assessment: { path: 'assessment', component: PortalAssessmentsPage },
      quiz: { path: 'assessment/quiz/:assessmentId/:assignmentId', component: PortalQuizPage },
      submit: { path: 'assessment/submit/:assessmentId/:assignmentId', component: PortalAssessmentSubmissionPage },
      results: { path: 'assessment/results/:assessmentId/:assignmentId', component: PortalAssessmentResultsPage }
    }
  },
  // Settings Routes
  settings: {
    base: '/settings',
    access: ROUTE_ACCESS.AUTHENTICATED,
    routes: {
      main: { path: '', component: SettingsPage },
      theme: { path: 'theme', component: ThemeSettingsPage },
      notifications: { path: 'notifications', component: NotificationPreferencesPageV2 }
    }
  },
  // Test Routes (for development)
  test: {
    base: '/test',
    access: ROUTE_ACCESS.AUTHENTICATED,
    routes: {
      websocket: { path: 'websocket', component: WebSocketTestPage },
      notifications: { path: 'notifications', component: NotificationTestPage }
    }
  },
  // Debug Route (for development)
  debug: {
    path: '/debug',
    component: DebugPage,
    access: ROUTE_ACCESS.AUTHENTICATED
  }
};
/**
 * Helper function to flatten route configuration for React Router
 */
export const getFlattenedRoutes = () => {
  const routes = [];
  Object.entries(ROUTE_CONFIG).forEach(([key, config]) => {
    if (config.routes) {
      // Nested routes
      Object.entries(config.routes).forEach(([routeKey, route]) => {
        routes.push({
          path: `${config.base}/${route.path}`.replace(/\/+/g, '/'), // Clean up double slashes
          component: route.component,
          access: route.access || config.access,
          key: `${key}.${routeKey}`
        });
      });
    } else {
      // Single route
      routes.push({
        path: config.path,
        component: config.component,
        access: config.access,
        key
      });
    }
  });
  return routes;
};
export default ROUTE_CONFIG;