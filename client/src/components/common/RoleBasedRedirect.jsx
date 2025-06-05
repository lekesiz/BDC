import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import DashboardPageEnhanced from '@/pages/dashboard/DashboardPageEnhanced';
/**
 * Component that redirects users based on their role
 * Students go to /portal, others see the main dashboard
 */
const RoleBasedRedirect = () => {
  const { user, isLoading } = useAuth();
  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }
  // Redirect students to portal
  if (user?.role === 'student' || user?.role === 'trainee') {
    return <Navigate to="/portal" replace />;
  }
  // Show dashboard for other roles
  return <DashboardPageEnhanced />;
};
export default RoleBasedRedirect;