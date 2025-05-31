/**
 * Enhanced ProtectedRoute component with centralized role and permission checking
 */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { canAccessRoute, hasRole, hasPermission } from '../../config/roles';
import LoadingSpinner from '../ui/LoadingSpinner';

/**
 * Enhanced ProtectedRoute that supports:
 * - Authentication checking
 * - Role-based access control
 * - Permission-based access control
 * - Custom access rules
 * - Loading states
 * - Unauthorized redirects
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if authorized
 * @param {string|string[]} [props.requiredRole] - Required role(s) (legacy support)
 * @param {string|string[]} [props.requiredPermission] - Required permission(s)
 * @param {Object} [props.access] - Access configuration object from route config
 * @param {Function} [props.customAccessCheck] - Custom access check function
 * @param {boolean} [props.requireAuth=true] - Whether authentication is required
 * @param {string} [props.redirectTo='/login'] - Where to redirect if not authorized
 * @param {string} [props.unauthorizedRedirect='/unauthorized'] - Where to redirect if unauthorized
 * @returns {React.ReactNode} The child components or a redirect
 */
const EnhancedProtectedRoute = ({ 
  children, 
  requiredRole, 
  requiredPermission,
  access,
  customAccessCheck,
  requireAuth = true,
  redirectTo = '/login',
  unauthorizedRedirect = '/unauthorized'
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  // Check authentication requirement
  if (requireAuth && !isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location.pathname }} replace />;
  }
  
  // Skip authorization checks if no authentication required and user not authenticated
  if (!requireAuth && !isAuthenticated) {
    return children;
  }
  
  // Perform authorization checks for authenticated users
  if (isAuthenticated && user) {
    let authorized = true;
    
    // Check access configuration (new centralized approach)
    if (access) {
      authorized = canAccessRoute(user.role, access);
    }
    // Check required role (legacy support)
    else if (requiredRole) {
      authorized = hasRole(user.role, requiredRole);
    }
    // Check required permission
    else if (requiredPermission) {
      if (Array.isArray(requiredPermission)) {
        authorized = requiredPermission.some(permission => hasPermission(user.role, permission));
      } else {
        authorized = hasPermission(user.role, requiredPermission);
      }
    }
    
    // Apply custom access check if provided
    if (authorized && customAccessCheck) {
      authorized = customAccessCheck(user);
    }
    
    // Redirect if not authorized
    if (!authorized) {
      return <Navigate to={unauthorizedRedirect} replace />;
    }
  }
  
  // Render children if all checks pass
  return children;
};

/**
 * Convenience wrapper for role-based protection
 */
export const RoleProtectedRoute = ({ children, roles, ...props }) => (
  <EnhancedProtectedRoute requiredRole={roles} {...props}>
    {children}
  </EnhancedProtectedRoute>
);

/**
 * Convenience wrapper for permission-based protection
 */
export const PermissionProtectedRoute = ({ children, permissions, ...props }) => (
  <EnhancedProtectedRoute requiredPermission={permissions} {...props}>
    {children}
  </EnhancedProtectedRoute>
);

/**
 * Convenience wrapper for admin-only routes
 */
export const AdminRoute = ({ children, ...props }) => (
  <EnhancedProtectedRoute 
    requiredRole={['super_admin', 'tenant_admin']} 
    {...props}
  >
    {children}
  </EnhancedProtectedRoute>
);

/**
 * Convenience wrapper for management routes (admin + trainer)
 */
export const ManagementRoute = ({ children, ...props }) => (
  <EnhancedProtectedRoute 
    requiredRole={['super_admin', 'tenant_admin', 'trainer']} 
    {...props}
  >
    {children}
  </EnhancedProtectedRoute>
);

/**
 * Convenience wrapper for student-only routes
 */
export const StudentRoute = ({ children, ...props }) => (
  <EnhancedProtectedRoute 
    requiredRole={['student', 'trainee']} 
    {...props}
  >
    {children}
  </EnhancedProtectedRoute>
);

/**
 * Public route wrapper (no authentication required)
 */
export const PublicRoute = ({ children, ...props }) => (
  <EnhancedProtectedRoute 
    requireAuth={false} 
    {...props}
  >
    {children}
  </EnhancedProtectedRoute>
);

export default EnhancedProtectedRoute;