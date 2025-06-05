/**
 * Component-level permission validation utilities
 */
import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { hasPermission, hasRole } from '../../config/roles';
import { Lock } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Card } from '../ui/card';
/**
 * Higher-order component for permission-based rendering
 */
export const withPermission = (WrappedComponent, requiredPermission, fallbackComponent = null) => {
  return function PermissionWrappedComponent(props) {
    const { user } = useAuth();
    if (!user || !hasPermission(user.role, requiredPermission)) {
      return fallbackComponent || <div>Access denied</div>;
    }
    return <WrappedComponent {...props} />;
  };
};
/**
 * Higher-order component for role-based rendering
 */
export const withRole = (WrappedComponent, requiredRoles, fallbackComponent = null) => {
  return function RoleWrappedComponent(props) {
    const { user } = useAuth();
    if (!user || !hasRole(user.role, requiredRoles)) {
      return fallbackComponent || <div>Access denied</div>;
    }
    return <WrappedComponent {...props} />;
  };
};
/**
 * Conditional rendering component based on permissions
 */
export const IfPermission = ({ permission, children, fallback = null }) => {
  const { user } = useAuth();
  if (!user || !hasPermission(user.role, permission)) {
    return fallback;
  }
  return children;
};
/**
 * Conditional rendering component based on roles
 */
export const IfRole = ({ roles, children, fallback = null }) => {
  const { user } = useAuth();
  if (!user || !hasRole(user.role, roles)) {
    return fallback;
  }
  return children;
};
/**
 * Conditional rendering component with multiple permission checks
 */
export const IfAnyPermission = ({ permissions, children, fallback = null }) => {
  const { user } = useAuth();
  if (!user || !permissions.some(permission => hasPermission(user.role, permission))) {
    return fallback;
  }
  return children;
};
/**
 * Conditional rendering component requiring all permissions
 */
export const IfAllPermissions = ({ permissions, children, fallback = null }) => {
  const { user } = useAuth();
  if (!user || !permissions.every(permission => hasPermission(user.role, permission))) {
    return fallback;
  }
  return children;
};
/**
 * Component that shows access denied message
 */
export const AccessDenied = ({ 
  title = "Access Restricted", 
  message = "You do not have permission to access this feature.",
  showRole = true,
  className = "flex items-center justify-center min-h-[300px]"
}) => {
  const { user } = useAuth();
  return (
    <div className={className}>
      <Card className="p-8 text-center max-w-md">
        <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600 mb-4">{message}</p>
        {showRole && user?.role && (
          <p className="text-sm text-gray-500">
            Current role: <Badge variant="secondary">{user.role}</Badge>
          </p>
        )}
      </Card>
    </div>
  );
};
/**
 * Hook for checking permissions in components
 */
export const usePermissions = () => {
  const { user } = useAuth();
  const checkPermission = (permission) => {
    return user ? hasPermission(user.role, permission) : false;
  };
  const checkRole = (roles) => {
    return user ? hasRole(user.role, roles) : false;
  };
  const checkAnyPermission = (permissions) => {
    return user ? permissions.some(permission => hasPermission(user.role, permission)) : false;
  };
  const checkAllPermissions = (permissions) => {
    return user ? permissions.every(permission => hasPermission(user.role, permission)) : false;
  };
  return {
    user,
    checkPermission,
    checkRole,
    checkAnyPermission,
    checkAllPermissions,
    hasPermission: checkPermission,
    hasRole: checkRole
  };
};
/**
 * Component for secure feature sections
 */
export const SecureSection = ({ 
  permission, 
  roles, 
  children, 
  fallback = null,
  showAccessDenied = false,
  accessDeniedProps = {}
}) => {
  const { user } = useAuth();
  let hasAccess = false;
  if (permission && user) {
    hasAccess = hasPermission(user.role, permission);
  } else if (roles && user) {
    hasAccess = hasRole(user.role, roles);
  }
  if (!hasAccess) {
    if (showAccessDenied) {
      return <AccessDenied {...accessDeniedProps} />;
    }
    return fallback;
  }
  return children;
};
export default {
  withPermission,
  withRole,
  IfPermission,
  IfRole,
  IfAnyPermission,
  IfAllPermissions,
  AccessDenied,
  usePermissions,
  SecureSection
};