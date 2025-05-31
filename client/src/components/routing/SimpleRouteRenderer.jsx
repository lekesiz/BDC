/**
 * Simplified route renderer for testing clean architecture
 * Uses only confirmed existing components
 */

import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ProtectedRoute from '../common/ProtectedRoute';
import RoleBasedRedirect from '../common/RoleBasedRedirect';
import DashboardLayout from '../layout/DashboardLayout';
import LoadingSpinner from '../ui/LoadingSpinner';

// Auth pages (not lazy-loaded for faster auth flow)
import LoginPage from '../../pages/auth/LoginPage';
import RegisterPage from '../../pages/auth/RegisterPage';
import ForgotPasswordPage from '../../pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '../../pages/auth/ResetPasswordPage';
import SimpleLoginPage from '../../pages/auth/SimpleLoginPage';

// Test pages
import TestLogin from '../../TestLogin';
import TestAuth from '../../TestAuth';

// Lazy load confirmed components
const DashboardPageEnhanced = lazy(() => import('../../pages/dashboard/DashboardPageEnhanced'));
const SettingsPage = lazy(() => import('../../pages/settings/SettingsPage'));
const ProfilePage = lazy(() => import('../../pages/profile/ProfilePage'));
const UsersPage = lazy(() => import('../../pages/users/UsersPage'));
const PortalDashboardV3 = lazy(() => import('../../pages/portal/PortalDashboardV3'));
const BeneficiariesPage = lazy(() => import('../../pages/beneficiaries/BeneficiariesPage'));
const BeneficiaryDetailPage = lazy(() => import('../../pages/beneficiaries/BeneficiaryDetailPage'));
const BeneficiaryFormPage = lazy(() => import('../../pages/beneficiaries/BeneficiaryFormPage'));

// Additional key pages
const EvaluationsPage = lazy(() => import('../../pages/evaluation/EvaluationsPage'));
const MyEvaluationsPage = lazy(() => import('../../pages/evaluation/MyEvaluationsPage'));
const DocumentsPage = lazy(() => import('../../pages/document/DocumentsPage'));
const MyDocumentsPage = lazy(() => import('../../pages/document/MyDocumentsPage'));
const CalendarPage = lazy(() => import('../../pages/calendar/CalendarPage'));
const MessagingPage = lazy(() => import('../../pages/messaging/MessagingPage'));
const NotificationsPage = lazy(() => import('../../pages/notifications/NotificationsPage'));
const ProgramsListPage = lazy(() => import('../../pages/programs/ProgramsListPage'));
const AnalyticsDashboardPage = lazy(() => import('../../pages/analytics/AnalyticsDashboardPage'));
const ReportsDashboardPage = lazy(() => import('../../pages/reports/ReportsDashboardPage'));
const TenantsPage = lazy(() => import('../../pages/admin/TenantsPage'));

/**
 * Simple route renderer for testing
 */
const SimpleRouteRenderer = () => {
  const { isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading application..." />
      </div>
    );
  }
  
  return (
    <Routes>
      {/* Test routes */}
      <Route path="/test-login" element={<TestLogin />} />
      <Route path="/test-auth" element={<TestAuth />} />
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
        }
      >
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
          } 
        />
        
        <Route 
          path="settings" 
          element={
            <Suspense fallback={<LoadingSpinner />}>
              <SettingsPage />
            </Suspense>
          } 
        />
        
        <Route 
          path="users" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin']}>
              <Suspense fallback={<LoadingSpinner />}>
                <UsersPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="portal" 
          element={
            <ProtectedRoute requiredRole={['student', 'trainee']}>
              <Suspense fallback={<LoadingSpinner />}>
                <PortalDashboardV3 />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        {/* Beneficiaries Management Routes */}
        <Route 
          path="beneficiaries" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiariesPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="beneficiaries/new" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiaryFormPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="beneficiaries/:id" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiaryDetailPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="beneficiaries/:id/edit" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <BeneficiaryFormPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        {/* Evaluations Routes */}
        <Route 
          path="evaluations" 
          element={
            <ProtectedRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <EvaluationsPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="my-evaluations" 
          element={
            <ProtectedRoute requiredRole={['student', 'trainee']}>
              <Suspense fallback={<LoadingSpinner />}>
                <MyEvaluationsPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        {/* Documents Routes */}
        <Route 
          path="documents" 
          element={
            <ProtectedRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <DocumentsPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="my-documents" 
          element={
            <ProtectedRoute requiredRole={['student', 'trainee']}>
              <Suspense fallback={<LoadingSpinner />}>
                <MyDocumentsPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        {/* Calendar & Communication */}
        <Route 
          path="calendar" 
          element={
            <ProtectedRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <CalendarPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="messaging" 
          element={
            <ProtectedRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <MessagingPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="notifications" 
          element={
            <ProtectedRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <NotificationsPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        {/* Programs & Analytics */}
        <Route 
          path="programs" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <ProgramsListPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="analytics" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <AnalyticsDashboardPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="reports" 
          element={
            <ProtectedRoute requiredRole={['super_admin', 'tenant_admin', 'trainer']}>
              <Suspense fallback={<LoadingSpinner />}>
                <ReportsDashboardPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
        
        {/* Admin Routes */}
        <Route 
          path="admin/tenants" 
          element={
            <ProtectedRoute requiredRole={['super_admin']}>
              <Suspense fallback={<LoadingSpinner />}>
                <TenantsPage />
              </Suspense>
            </ProtectedRoute>
          } 
        />
      </Route>
      
      {/* Error routes */}
      <Route 
        path="/unauthorized" 
        element={
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
              <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
              <button 
                onClick={() => window.history.back()}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Go Back
              </button>
            </div>
          </div>
        } 
      />
      
      <Route 
        path="*" 
        element={
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-800 mb-4">Page Not Found</h1>
              <p className="text-gray-600 mb-4">The page you're looking for doesn't exist.</p>
              <button 
                onClick={() => window.location.href = '/'}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Go Home
              </button>
            </div>
          </div>
        } 
      />
    </Routes>
  );
};

export default SimpleRouteRenderer;