// TODO: i18n - processed
import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import DashboardWidgetGrid from '@/components/portal/DashboardWidgetGrid';
/**
 * PortalDashboardPage provides the main dashboard interface for student beneficiaries
 * with customizable widgets
 */import { useTranslation } from "react-i18next";
const PortalDashboardPage = () => {const { t } = useTranslation();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    dashboard: null,
    skills: null,
    profile: null,
    achievements: null,
    notifications: null,
    resources: null
  });
  // Load dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        // Use Promise.allSettled to fetch all data in parallel
        // and continue even if some requests fail
        const [
        dashboardResponse,
        skillsResponse,
        profileResponse,
        achievementsResponse,
        notificationsResponse,
        resourcesResponse] =
        await Promise.allSettled([
        api.get('/api/portal/dashboard'),
        api.get('/api/portal/skills'),
        api.get('/api/portal/profile'),
        api.get('/api/portal/achievements'),
        api.get('/api/portal/notifications'),
        api.get('/api/portal/resources')]
        );
        setDashboardData({
          dashboard: dashboardResponse.status === 'fulfilled' ? dashboardResponse.value.data : null,
          skills: skillsResponse.status === 'fulfilled' ? skillsResponse.value.data : null,
          profile: profileResponse.status === 'fulfilled' ? profileResponse.value.data : null,
          achievements: achievementsResponse.status === 'fulfilled' ? achievementsResponse.value.data : null,
          notifications: notificationsResponse.status === 'fulfilled' ? notificationsResponse.value.data : null,
          resources: resourcesResponse.status === 'fulfilled' ? resourcesResponse.value.data : null
        });
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
        toast({
          title: 'Error',
          description: 'Failed to load dashboard data',
          type: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []); // Remove toast dependency to prevent infinite loop
  // Load saved layout from localStorage
  const getSavedLayout = () => {
    try {
      return localStorage.getItem('portal-dashboard-layout');
    } catch (error) {
      console.error('Error loading dashboard layout:', error);
      return null;
    }
  };
  // Save layout to localStorage
  const handleSaveLayout = (layoutData) => {
    try {
      localStorage.setItem('portal-dashboard-layout', layoutData);
      toast({
        title: 'Success',
        description: 'Dashboard layout saved',
        type: 'success'
      });
    } catch (error) {
      console.error('Error saving dashboard layout:', error);
      toast({
        title: 'Error',
        description: 'Failed to save dashboard layout',
        type: 'error'
      });
    }
  };
  return (
    <div className="container mx-auto py-6">
      <DashboardWidgetGrid
        dashboardData={dashboardData}
        isLoading={isLoading}
        error={error}
        onSaveLayout={handleSaveLayout}
        savedLayout={getSavedLayout()} />

    </div>);

};
export default PortalDashboardPage;