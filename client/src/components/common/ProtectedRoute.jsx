import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * ProtectedRoute component that ensures a user is authenticated before 
 * rendering children components. Redirects to login if not authenticated.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @param {string|string[]} [props.requiredRole] - Optional role(s) required to access the route
 * @returns {React.ReactNode} The child components or a redirect
 */
const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, isLoading, user, hasRole } = useAuth();
  const location = useLocation();
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  
  // Check for required role if specified
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  // Render children if authenticated and authorized
  return children;
};

export default ProtectedRoute;