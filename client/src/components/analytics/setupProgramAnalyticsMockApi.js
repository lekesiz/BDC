import { http, HttpResponse } from 'msw';
import { programs, programAnalytics, getProgramsList, getProgramAnalytics, exportProgramAnalytics } from './mockProgramData';

/**
 * Setup mock API handlers for program analytics
 */
export const setupProgramAnalyticsMockApi = (api, originalGet, originalPost) => {
  // Override API methods with mock implementations
  api.get = function(url, config) {
    // Get all programs
    if (url === '/api/programs') {
      return Promise.resolve({
        data: programs,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get program details by ID
    const programMatch = url.match(/^\/api\/programs\/(\d+)$/);
    if (programMatch) {
      const id = programMatch[1];
      const program = programs.find(p => p.id.toString() === id);
      
      if (!program) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Program not found' }
          }
        });
      }
      
      return Promise.resolve({
        data: program,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get program analytics by ID
    const analyticsMatch = url.match(/^\/api\/analytics\/programs\/(\d+)(\?.*)?$/);
    if (analyticsMatch) {
      const id = analyticsMatch[1];
      const queryString = analyticsMatch[2] || '';
      const params = new URLSearchParams(queryString);
      const period = params.get('period') || '30d';
      const analytics = getProgramAnalytics(id, period);
      
      if (!analytics) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Program analytics not found' }
          }
        });
      }
      
      return Promise.resolve({
        data: analytics,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get analytics data list
    if (url.startsWith('/api/analytics/programs')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const search = params.get('search') || '';
      const page = parseInt(params.get('page') || '1');
      const limit = parseInt(params.get('limit') || '10');
      
      const result = getProgramsList(search, page, limit);
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Fall back to original get method
    return originalGet(url, config);
  };
  
  api.post = function(url, data, config) {
    // Export program analytics
    const exportMatch = url.match(/^\/api\/analytics\/programs\/(\d+)\/export$/);
    if (exportMatch) {
      const id = exportMatch[1];
      const { format, period } = data;
      
      const result = exportProgramAnalytics(id, format, period);
      
      if (!result) {
        return Promise.reject({
          response: {
            status: 500,
            data: { message: 'Failed to export analytics' }
          }
        });
      }
      
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Fall back to original post method
    return originalPost(url, data, config);
  };
};