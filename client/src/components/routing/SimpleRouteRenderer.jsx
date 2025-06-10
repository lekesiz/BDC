// TODO: i18n - processed
/**
 * Simplified route renderer for testing clean architecture
 * Uses only confirmed existing components
 */
import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ProtectedRoute from '../common/ProtectedRoute';
import EnhancedProtectedRoute, { AdminRoute, ManagementRoute, StudentRoute } from '../common/EnhancedProtectedRoute';
import RoleBasedRedirect from '../common/RoleBasedRedirect';
import DashboardLayout from '../layout/DashboardLayout';
import LoadingSpinner from '../ui/LoadingSpinner';
import { ROUTE_ACCESS } from '../../config/roles';
// Auth pages (not lazy-loaded for faster auth flow)
import LoginPage from '../../pages/auth/LoginPage';
import RegisterPage from '../../pages/auth/RegisterPage';
import ForgotPasswordPage from '../../pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '../../pages/auth/ResetPasswordPage';
import SimpleLoginPage from '../../pages/auth/SimpleLoginPage';
// Test pages - removed for production build
// Lazy load confirmed components
import { useTranslation } from "react-i18next";const DashboardPageEnhanced = lazy(() => import('../../pages/dashboard/DashboardPageEnhanced'));
const SettingsPage = lazy(() => import('../../pages/settings/SettingsPage'));
const ProfilePage = lazy(() => import('../../pages/profile/ProfilePage'));
const UsersPage = lazy(() => import('../../pages/users/UsersPage'));
const UserFormPage = lazy(() => import('../../pages/users/UserFormPage'));
const UserDetailPage = lazy(() => import('../../pages/users/UserDetailPage'));
const PortalDashboardV3 = lazy(() => import('../../pages/portal/PortalDashboardV3'));
const BeneficiariesPage = lazy(() => import('../../pages/beneficiaries/BeneficiariesPage'));
const BeneficiaryDetailPage = lazy(() => import('../../pages/beneficiaries/BeneficiaryDetailPage'));
const BeneficiaryFormPage = lazy(() => import('../../pages/beneficiaries/BeneficiaryFormPage'));
// Additional key pages
const EvaluationsPage = lazy(() => import('../../pages/evaluation/EvaluationsPage'));
const MyEvaluationsPage = lazy(() => import('../../pages/evaluation/MyEvaluationsPage'));
const TestCreationPageSimple = lazy(() => import('../../pages/evaluation/TestCreationPageSimple'));
const TrainerEvaluationDetailPage = lazy(() => import('../../pages/evaluation/TrainerEvaluationDetailPage'));
const DocumentsPage = lazy(() => import('../../pages/document/DocumentsPage'));
const MyDocumentsPage = lazy(() => import('../../pages/document/MyDocumentsPage'));
const CalendarPage = lazy(() => import('../../pages/calendar/CalendarPage'));
const AppointmentCreationPage = lazy(() => import('../../pages/appointment/AppointmentCreationPage'));
const MessagingPage = lazy(() => import('../../pages/messaging/MessagingPage'));
const NotificationsPage = lazy(() => import('../../pages/notifications/NotificationsPage'));
const ProgramsListPage = lazy(() => import('../../pages/programs/ProgramsListPage'));
const AnalyticsDashboardPage = lazy(() => import('../../pages/analytics/AnalyticsDashboardPage'));
const ReportsDashboardPage = lazy(() => import('../../pages/reports/ReportsDashboardPage'));
const TenantsPage = lazy(() => import('../../pages/admin/TenantsPage'));
const ProgressTrackingPage = lazy(() => import('../../pages/beneficiaries/ProgressTrackingPage'));
const ProgramFormPage = lazy(() => import('../../pages/programs/ProgramFormPage'));
const ProgramDetailPage = lazy(() => import('../../pages/programs/ProgramDetailPage'));
// Integration Pages
const WedofIntegrationPage = lazy(() => import('../../pages/integrations/WedofIntegrationPage'));
const GoogleCalendarIntegrationV2Page = lazy(() => import('../../pages/integrations/GoogleCalendarIntegrationV2Page'));
const EmailIntegrationPage = lazy(() => import('../../pages/integrations/EmailIntegrationPage'));
const SMSIntegrationPage = lazy(() => import('../../pages/integrations/SMSIntegrationPage'));
const PaymentIntegrationPage = lazy(() => import('../../pages/integrations/PaymentIntegrationPage'));
const WebhooksPage = lazy(() => import('../../pages/integrations/WebhooksPage'));
const ZapierIntegrationPage = lazy(() => import('../../pages/integrations/ZapierIntegrationPage'));
const PennylaneIntegrationPage = lazy(() => import('../../pages/integrations/PennylaneIntegrationPage'));
// AI Pages
const AIInsightsPage = lazy(() => import('../../pages/ai/AIInsightsPage'));
const AIContentGenerationPage = lazy(() => import('../../pages/ai/AIContentGenerationPage'));
const AIChatbotPage = lazy(() => import('../../pages/ai/AIChatbotPage'));
const AIRecommendationsPage = lazy(() => import('../../pages/ai/AIRecommendationsPage'));
/**
 * Simple route renderer for testing
 */
const SimpleRouteRenderer = () => {const { t } = useTranslation();
  const { isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading application..." />
      </div>);

  }
  return (
    <Routes>
      {/* Test routes - removed for production build */}
      <Route path="/simple-login" element={<SimpleLoginPage />} />
      {/* Public auth routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      {/* Protected routes within dashboard layout */}
      <Route
        path="/"
        element={
        <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <DashboardLayout />
            </Suspense>
          </ProtectedRoute>
        }>

        {/* Dashboard root with role-based redirection */}
        <Route index element={<RoleBasedRedirect />} />
        <Route path="dashboard" element={<Navigate to="/" replace />} />
        {/* Basic routes for testing */}
        <Route
          path="profile"
          element={
          <Suspense fallback={<LoadingSpinner />}>
              <ProfilePage />
            </Suspense>
          } />

        <Route
          path="settings"
          element={
          <Suspense fallback={<LoadingSpinner />}>
              <SettingsPage />
            </Suspense>
          } />

        {/* User Management Routes */}
        <Route
          path="users"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <UsersPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="users/create"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <UserFormPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="users/:id"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <UserDetailPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="users/:id/edit"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <UserFormPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="portal"
          element={
          <StudentRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <PortalDashboardV3 />
              </Suspense>
            </StudentRoute>
          } />

        {/* Beneficiaries Management Routes */}
        <Route
          path="beneficiaries"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiariesPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="beneficiaries/new"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiaryFormPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="beneficiaries/:id"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiaryDetailPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="beneficiaries/:id/edit"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiaryFormPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="beneficiaries/:id/progress"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ProgressTrackingPage />
              </Suspense>
            </ManagementRoute>
          } />

        {/* Evaluations Routes */}
        <Route
          path="evaluations"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <EvaluationsPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="evaluations/create"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <TestCreationPageSimple />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="evaluations/:id"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <TrainerEvaluationDetailPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="my-evaluations"
          element={
          <StudentRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <MyEvaluationsPage />
              </Suspense>
            </StudentRoute>
          } />

        {/* Test Routes */}
        <Route path="tests" element={<Navigate to="/evaluations" replace />} />
        <Route
          path="tests/create"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <TestCreationPageSimple />
              </Suspense>
            </ManagementRoute>
          } />

        {/* Documents Routes */}
        <Route
          path="documents"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <DocumentsPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="my-documents"
          element={
          <StudentRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <MyDocumentsPage />
              </Suspense>
            </StudentRoute>
          } />

        {/* Calendar & Communication */}
        <Route
          path="calendar"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <CalendarPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="calendar/google-integration"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <GoogleCalendarIntegrationV2Page />
              </Suspense>
            </ManagementRoute>
          } />

        {/* Appointment Routes */}
        <Route path="appointments" element={<Navigate to="/calendar" replace />} />
        <Route
          path="appointments/new"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <AppointmentCreationPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="messaging"
          element={
          <EnhancedProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer', 'student']}>
              <Suspense fallback={<LoadingSpinner />}>
                <MessagingPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        <Route
          path="notifications"
          element={
          <EnhancedProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer', 'student']}>
              <Suspense fallback={<LoadingSpinner />}>
                <NotificationsPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        {/* Programs & Analytics */}
        <Route
          path="programs"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ProgramsListPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="programs/new"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ProgramFormPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="programs/:id"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ProgramDetailPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="programs/:id/edit"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ProgramFormPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="analytics"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <AnalyticsDashboardPage />
              </Suspense>
            </ManagementRoute>
          } />

        <Route
          path="reports"
          element={
          <ManagementRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ReportsDashboardPage />
              </Suspense>
            </ManagementRoute>
          } />

        {/* AI Routes */}
        <Route
          path="ai/insights"
          element={
          <EnhancedProtectedRoute access={ROUTE_ACCESS.AI_ACCESS}>
              <Suspense fallback={<LoadingSpinner />}>
                <AIInsightsPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        <Route
          path="ai/content"
          element={
          <EnhancedProtectedRoute access={ROUTE_ACCESS.AI_ACCESS}>
              <Suspense fallback={<LoadingSpinner />}>
                <AIContentGenerationPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        <Route
          path="ai/chatbot"
          element={
          <EnhancedProtectedRoute access={ROUTE_ACCESS.AI_ACCESS}>
              <Suspense fallback={<LoadingSpinner />}>
                <AIChatbotPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        <Route
          path="ai/recommendations"
          element={
          <EnhancedProtectedRoute access={ROUTE_ACCESS.AI_ACCESS}>
              <Suspense fallback={<LoadingSpinner />}>
                <AIRecommendationsPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        {/* Admin Routes */}
        <Route
          path="admin/tenants"
          element={
          <EnhancedProtectedRoute requiredRole={['super_admin']}>
              <Suspense fallback={<LoadingSpinner />}>
                <TenantsPage />
              </Suspense>
            </EnhancedProtectedRoute>
          } />

        {/* Integration Routes */}
        <Route
          path="integrations/wedof"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <WedofIntegrationPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/google-calendar"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <GoogleCalendarIntegrationV2Page />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/email"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <EmailIntegrationPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/sms"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <SMSIntegrationPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/payment"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <PaymentIntegrationPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/webhooks"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <WebhooksPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/zapier"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ZapierIntegrationPage />
              </Suspense>
            </AdminRoute>
          } />

        <Route
          path="integrations/pennylane"
          element={
          <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <PennylaneIntegrationPage />
              </Suspense>
            </AdminRoute>
          } />

      </Route>
      {/* Error routes */}
      <Route
        path="/unauthorized"
        element={
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-red-600 mb-4">{t("components.access_denied")}</h1>
              <p className="text-gray-600 mb-4">{t("components.you_dont_have_permission_to_access_this_page")}</p>
              <button
              onClick={() => window.history.back()}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">{t("components.go_back")}


            </button>
            </div>
          </div>
        } />

      <Route
        path="*"
        element={
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-800 mb-4">{t("components.page_not_found")}</h1>
              <p className="text-gray-600 mb-4">{t("components.the_page_youre_looking_for_doesnt_exist")}</p>
              <button
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">{t("components.go_home")}


            </button>
            </div>
          </div>
        } />

    </Routes>);

};
export default SimpleRouteRenderer;