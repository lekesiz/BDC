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
      console.log('Mock API: Dashboard overview request');
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
      console.log('Mock API: Dashboard metrics request');
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
      console.log('Mock API: Dashboard activity request');
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
      console.log('Mock API: Dashboard notifications request');
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
      console.log('Mock API: Dashboard quick actions request');
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
      console.log('Mock API: Tenant dashboard request');
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
      console.log('Mock API: Trainer dashboard request');
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
      console.log('Mock API: Student dashboard request');
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
      console.log('Mock API: Dashboard widgets request');
      
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
      console.log('Mock API: Update dashboard widgets', data);
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