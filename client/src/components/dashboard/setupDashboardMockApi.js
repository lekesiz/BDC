import { generateDashboardData, generateDashboardNotifications, generateQuickActions } from './mockDashboardData';
export const setupDashboardMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };
  // Dashboard overview endpoint
  api.get = function(url, ...args) {
    if (url === '/api/dashboard' || url === '/api/dashboard/overview') {
      // Get user role from context or default to student
      const userRole = localStorage.getItem('userRole') || 'student';
      const dashboardData = generateDashboardData(userRole);
      return Promise.resolve({
        status: 200,
        data: dashboardData
      });
    }
    // Dashboard metrics endpoint
    if (url === '/api/dashboard/metrics') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const data = generateDashboardData(userRole);
      return Promise.resolve({
        status: 200,
        data: {
          overview: data.overview,
          performanceMetrics: data.performanceMetrics,
          quickStats: data.quickStats
        }
      });
    }
    // Dashboard activity endpoint
    if (url === '/api/dashboard/activity') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const data = generateDashboardData(userRole);
      return Promise.resolve({
        status: 200,
        data: {
          recentActivity: data.recentActivity
        }
      });
    }
    // Dashboard notifications endpoint
    if (url === '/api/dashboard/notifications') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const notifications = generateDashboardNotifications(userRole);
      return Promise.resolve({
        status: 200,
        data: {
          notifications,
          unreadCount: notifications.filter(n => !n.read).length
        }
      });
    }
    // Dashboard quick actions endpoint
    if (url === '/api/dashboard/quick-actions') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const actions = generateQuickActions(userRole);
      return Promise.resolve({
        status: 200,
        data: {
          actions
        }
      });
    }
    // Tenant dashboard endpoint (for admin/tenant_admin)
    if (url === '/api/dashboard/tenant') {
      const userRole = localStorage.getItem('userRole') || 'admin';
      const data = generateDashboardData(userRole);
      return Promise.resolve({
        status: 200,
        data: {
          tenantOverview: data.tenantOverview,
          tenantSpecific: data.tenantSpecific,
          departmentMetrics: data.departmentMetrics
        }
      });
    }
    // Trainer dashboard endpoint
    if (url === '/api/dashboard/trainer') {
      const data = generateDashboardData('trainer');
      return Promise.resolve({
        status: 200,
        data: {
          trainerSpecific: data.trainerSpecific,
          classMetrics: data.classMetrics,
          upcomingSchedule: data.upcomingSchedule
        }
      });
    }
    // Student dashboard endpoint
    if (url === '/api/dashboard/student') {
      const data = generateDashboardData('student');
      return Promise.resolve({
        status: 200,
        data: {
          studentSpecific: data.studentSpecific,
          learningPath: data.learningPath,
          performanceChart: data.performanceChart
        }
      });
    }
    // Dashboard widgets configuration
    if (url === '/api/dashboard/widgets') {
      return Promise.resolve({
        status: 200,
        data: {
          widgets: [
            { id: 'overview', name: 'Overview', enabled: true, order: 1 },
            { id: 'quickStats', name: 'Quick Stats', enabled: true, order: 2 },
            { id: 'recentActivity', name: 'Recent Activity', enabled: true, order: 3 },
            { id: 'performanceChart', name: 'Performance', enabled: true, order: 4 },
            { id: 'notifications', name: 'Notifications', enabled: true, order: 5 }
          ]
        }
      });
    }
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  // Widget configuration update
  api.put = function(url, data, ...args) {
    if (url === '/api/dashboard/widgets') {
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          widgets: data.widgets
        }
      });
    }
    return originalFunctions.put.call(api, url, data, ...args);
  };
};