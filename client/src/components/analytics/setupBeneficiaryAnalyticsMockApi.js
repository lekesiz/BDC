import { http, HttpResponse } from 'msw';
import { beneficiaries, beneficiaryAnalytics, getBeneficiariesList, getBeneficiaryAnalytics, exportBeneficiaryAnalytics } from './mockBeneficiaryData';
/**
 * Setup mock API handlers for beneficiary analytics
 */
export const setupBeneficiaryAnalyticsMockApi = (api, originalGet, originalPost) => {
  // Override API methods with mock implementations
  api.get = function(url, config) {
    // Get all beneficiaries
    if (url === '/api/beneficiaries') {
      return Promise.resolve({
        data: beneficiaries,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Get beneficiary details by ID
    const beneficiaryMatch = url.match(/^\/api\/beneficiaries\/(\d+)$/);
    if (beneficiaryMatch) {
      const id = beneficiaryMatch[1];
      const beneficiary = beneficiaries.find(b => b.id.toString() === id);
      if (!beneficiary) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Beneficiary not found' }
          }
        });
      }
      return Promise.resolve({
        data: beneficiary,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Get beneficiary analytics by ID
    const analyticsMatch = url.match(/^\/api\/analytics\/beneficiaries\/(\d+)(\?.*)?$/);
    if (analyticsMatch) {
      const id = analyticsMatch[1];
      const queryString = analyticsMatch[2] || '';
      const params = new URLSearchParams(queryString);
      const period = params.get('period') || '30d';
      const analytics = getBeneficiaryAnalytics(id, period);
      if (!analytics) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Beneficiary analytics not found' }
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
    if (url.startsWith('/api/analytics/beneficiaries')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const search = params.get('search') || '';
      const filter = params.get('filter') || 'all';
      const page = parseInt(params.get('page') || '1');
      const limit = parseInt(params.get('limit') || '10');
      const result = getBeneficiariesList(search, filter, page, limit);
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
    // Export beneficiary analytics
    const exportMatch = url.match(/^\/api\/analytics\/beneficiaries\/(\d+)\/export$/);
    if (exportMatch) {
      const id = exportMatch[1];
      const { format, period } = data;
      const result = exportBeneficiaryAnalytics(id, format, period);
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