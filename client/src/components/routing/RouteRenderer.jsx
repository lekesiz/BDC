/**
 * Enhanced route renderer with centralized protection and lazy loading
 */
import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { canAccessRoute } from '../../config/roles';
import { getFlattenedRoutes } from '../../config/routes';
import ProtectedRoute from '../common/ProtectedRoute';
import RoleBasedRedirect from '../common/RoleBasedRedirect';
import DashboardLayout from '../layout/DashboardLayout';
import LoadingSpinner from '../ui/LoadingSpinner';
import LazyWrapper from '../common/LazyWrapper';
// Auth pages (not lazy-loaded for faster auth flow)
import LoginPage from '../../pages/auth/LoginPage';
import RegisterPage from '../../pages/auth/RegisterPage';
import ForgotPasswordPage from '../../pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '../../pages/auth/ResetPasswordPage';
import SimpleLoginPage from '../../pages/auth/SimpleLoginPage';
// Test pages - removed for production build
/**
 * Component that renders a protected route with role checking
 */
const ProtectedRouteWrapper = ({ route }) => {
  const { user } = useAuth();
  // Check if user can access this route
  const canAccess = canAccessRoute(user?.role, route.access);
  if (!canAccess) {
    return <Navigate to="/unauthorized" replace />;
  }
  const Component = route.component;
  return (
    <LazyWrapper>
      <Component />
    </LazyWrapper>
  );
};
/**
 * Main route renderer component
 */
const RouteRenderer = () => {
  const { isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  // Get all flattened routes from configuration
  const routes = getFlattenedRoutes();
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
        }
      >
        {/* Dashboard root with role-based redirection */}
        <Route index element={<RoleBasedRedirect />} />
        <Route path="dashboard" element={<Navigate to="/" replace />} />
        {/* Dynamically render all configured routes */}
        {routes.map((route) => (
          <Route
            key={route.key}
            path={route.path}
            element={<ProtectedRouteWrapper route={route} />}
          />
        ))}
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
export default RouteRenderer;