import { 
  generateAnalyticsData, 
  generateAnalyticsReports,
  generateAnalyticsFilters,
  generateRealTimeAnalytics 
} from './mockAnalyticsData';

export const setupAnalyticsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };

  // Analytics endpoints
  api.get = function(url, ...args) {
    // General analytics endpoint
    if (url === '/api/analytics' || url === '/api/analytics/overview') {
      console.log('Mock API: Analytics overview request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const analyticsData = generateAnalyticsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: analyticsData
      });
    }
    
    // User analytics endpoint
    if (url === '/api/analytics/users' || url.startsWith('/api/analytics/users?')) {
      console.log('Mock API: User analytics request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const analyticsData = generateAnalyticsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: analyticsData.userMetrics
      });
    }
    
    // Course analytics endpoint
    if (url === '/api/analytics/courses' || url.startsWith('/api/analytics/courses?')) {
      console.log('Mock API: Course analytics request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const analyticsData = generateAnalyticsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: analyticsData.courseMetrics
      });
    }
    
    // Revenue analytics endpoint
    if (url === '/api/analytics/revenue' || url.startsWith('/api/analytics/revenue?')) {
      console.log('Mock API: Revenue analytics request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const analyticsData = generateAnalyticsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: analyticsData.revenueMetrics
      });
    }
    
    // Performance analytics endpoint
    if (url === '/api/analytics/performance' || url.startsWith('/api/analytics/performance?')) {
      console.log('Mock API: Performance analytics request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const analyticsData = generateAnalyticsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: analyticsData.performanceMetrics
      });
    }
    
    // Learning analytics endpoint
    if (url === '/api/analytics/learning' || url.startsWith('/api/analytics/learning?')) {
      console.log('Mock API: Learning analytics request');
      const userRole = localStorage.getItem('userRole') || 'student';
      const analyticsData = generateAnalyticsData(userRole);
      
      return Promise.resolve({
        status: 200,
        data: analyticsData.learningAnalytics
      });
    }
    
    // Trainer-specific analytics
    if (url === '/api/analytics/trainer' || url.startsWith('/api/analytics/trainer?')) {
      console.log('Mock API: Trainer analytics request');
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'trainer') {
        const analyticsData = generateAnalyticsData(userRole);
        return Promise.resolve({
          status: 200,
          data: analyticsData.trainerAnalytics
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    
    // Student-specific analytics
    if (url === '/api/analytics/student' || url.startsWith('/api/analytics/student?')) {
      console.log('Mock API: Student analytics request');
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'student') {
        const analyticsData = generateAnalyticsData(userRole);
        return Promise.resolve({
          status: 200,
          data: analyticsData.studentAnalytics
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    
    // Analytics reports endpoint
    if (url === '/api/analytics/reports') {
      console.log('Mock API: Analytics reports request');
      const reports = generateAnalyticsReports();
      
      return Promise.resolve({
        status: 200,
        data: {
          reports,
          total: reports.length
        }
      });
    }
    
    // Analytics filters endpoint
    if (url === '/api/analytics/filters') {
      console.log('Mock API: Analytics filters request');
      const filters = generateAnalyticsFilters();
      
      return Promise.resolve({
        status: 200,
        data: filters
      });
    }
    
    // Real-time analytics endpoint
    if (url === '/api/analytics/real-time') {
      console.log('Mock API: Real-time analytics request');
      const realTimeData = generateRealTimeAnalytics();
      
      return Promise.resolve({
        status: 200,
        data: realTimeData
      });
    }
    
    // Custom analytics query endpoint
    if (url === '/api/analytics/query' || url.startsWith('/api/analytics/query?')) {
      console.log('Mock API: Custom analytics query');
      
      // Parse query parameters
      const urlObj = new URL(url, 'http://localhost');
      const metric = urlObj.searchParams.get('metric');
      const dateRange = urlObj.searchParams.get('dateRange');
      const segment = urlObj.searchParams.get('segment');
      
      // Generate custom data based on query
      const customData = {
        metric,
        dateRange,
        segment,
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          values: [
            Math.floor(Math.random() * 100) + 50,
            Math.floor(Math.random() * 100) + 60,
            Math.floor(Math.random() * 100) + 70,
            Math.floor(Math.random() * 100) + 80,
            Math.floor(Math.random() * 100) + 90,
            Math.floor(Math.random() * 100) + 100
          ]
        }
      };
      
      return Promise.resolve({
        status: 200,
        data: customData
      });
    }
    
    // Analytics export endpoint
    if (url === '/api/analytics/export' || url.startsWith('/api/analytics/export?')) {
      console.log('Mock API: Analytics export request');
      
      const urlObj = new URL(url, 'http://localhost');
      const format = urlObj.searchParams.get('format') || 'csv';
      
      return Promise.resolve({
        status: 200,
        data: {
          downloadUrl: `/api/downloads/analytics-export-${Date.now()}.${format}`,
          format,
          expiresAt: new Date(Date.now() + 3600000).toISOString()
        }
      });
    }
    
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  
  // Analytics POST endpoints
  api.post = function(url, data, ...args) {
    // Generate analytics report
    if (url === '/api/analytics/reports/generate') {
      console.log('Mock API: Generate analytics report', data);
      
      const report = {
        id: Date.now(),
        title: data.title,
        type: data.type,
        dateRange: data.dateRange,
        status: 'generating',
        createdAt: new Date().toISOString(),
        estimatedTime: '2 minutes'
      };
      
      return Promise.resolve({
        status: 202,
        data: report
      });
    }
    
    // Save analytics dashboard
    if (url === '/api/analytics/dashboards') {
      console.log('Mock API: Save analytics dashboard', data);
      
      const dashboard = {
        id: Date.now(),
        name: data.name,
        widgets: data.widgets,
        filters: data.filters,
        createdAt: new Date().toISOString(),
        createdBy: data.userId || 'current_user'
      };
      
      return Promise.resolve({
        status: 201,
        data: dashboard
      });
    }
    
    // Track custom event
    if (url === '/api/analytics/events') {
      console.log('Mock API: Track custom event', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          eventId: Date.now(),
          tracked: true,
          timestamp: new Date().toISOString()
        }
      });
    }
    
    // Create analytics alert
    if (url === '/api/analytics/alerts') {
      console.log('Mock API: Create analytics alert', data);
      
      const alert = {
        id: Date.now(),
        name: data.name,
        metric: data.metric,
        condition: data.condition,
        threshold: data.threshold,
        enabled: true,
        createdAt: new Date().toISOString()
      };
      
      return Promise.resolve({
        status: 201,
        data: alert
      });
    }
    
    return originalFunctions.post.call(api, url, data, ...args);
  };
  
  // Analytics PUT endpoints
  api.put = function(url, data, ...args) {
    // Update dashboard
    if (url.match(/^\/api\/analytics\/dashboards\/\d+$/)) {
      console.log('Mock API: Update analytics dashboard', data);
      const dashboardId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: dashboardId,
          ...data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    
    // Update alert
    if (url.match(/^\/api\/analytics\/alerts\/\d+$/)) {
      console.log('Mock API: Update analytics alert', data);
      const alertId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: alertId,
          ...data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    
    // Update analytics settings
    if (url === '/api/analytics/settings') {
      console.log('Mock API: Update analytics settings', data);
      
      return Promise.resolve({
        status: 200,
        data: {
          settings: data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    
    return originalFunctions.put.call(api, url, data, ...args);
  };
  
  // Analytics DELETE endpoints
  api.delete = function(url, ...args) {
    // Delete dashboard
    if (url.match(/^\/api\/analytics\/dashboards\/\d+$/)) {
      console.log('Mock API: Delete analytics dashboard');
      const dashboardId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: dashboardId,
          deleted: true
        }
      });
    }
    
    // Delete alert
    if (url.match(/^\/api\/analytics\/alerts\/\d+$/)) {
      console.log('Mock API: Delete analytics alert');
      const alertId = parseInt(url.split('/').pop());
      
      return Promise.resolve({
        status: 200,
        data: {
          id: alertId,
          deleted: true
        }
      });
    }
    
    // Clear analytics cache
    if (url === '/api/analytics/cache') {
      console.log('Mock API: Clear analytics cache');
      
      return Promise.resolve({
        status: 200,
        data: {
          cleared: true,
          message: 'Analytics cache cleared successfully'
        }
      });
    }
    
    return originalFunctions.delete.call(api, url, ...args);
  };
};