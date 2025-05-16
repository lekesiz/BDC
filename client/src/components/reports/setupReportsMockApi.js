import { 
  reports, 
  scheduledReports, 
  getReportFields, 
  getReportFilters, 
  getReportPreview, 
  saveReport,
  getScheduledReport,
  saveScheduledReport,
  users
} from './mockReportsData';

/**
 * Setup mock API handlers for reports system
 */
export const setupReportsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Override API methods with mock implementations
  api.get = function(url, config) {
    // Get all reports
    if (url === '/api/reports') {
      return Promise.resolve({
        data: reports,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get recent reports
    if (url === '/api/reports/recent') {
      const recentReports = reports.slice(0, 3);
      return Promise.resolve({
        data: recentReports,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get saved reports
    if (url === '/api/reports/saved') {
      const savedReports = reports.filter(report => report.is_saved);
      return Promise.resolve({
        data: savedReports,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get report templates
    if (url === '/api/reports/templates') {
      const templates = reports.filter(report => report.is_template);
      return Promise.resolve({
        data: templates,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get scheduled reports
    if (url === '/api/reports/scheduled') {
      return Promise.resolve({
        data: scheduledReports,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get report fields
    if (url.startsWith('/api/reports/fields')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const reportType = params.get('type');
      const fields = getReportFields(reportType);
      
      return Promise.resolve({
        data: fields,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get report filters
    if (url.startsWith('/api/reports/filters')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const reportType = params.get('type');
      const filters = getReportFilters(reportType);
      
      return Promise.resolve({
        data: filters,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get report preview
    if (url === '/api/reports/preview') {
      const preview = getReportPreview();
      
      return Promise.resolve({
        data: preview,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get report by ID
    const reportMatch = url.match(/^\/api\/reports\/(\d+)$/);
    if (reportMatch) {
      const id = reportMatch[1];
      const report = reports.find(r => r.id.toString() === id);
      
      if (!report) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Report not found' }
          }
        });
      }
      
      return Promise.resolve({
        data: report,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Get scheduled report by ID
    const scheduledMatch = url.match(/^\/api\/reports\/scheduled\/(\d+)$/);
    if (scheduledMatch) {
      const id = scheduledMatch[1];
      const report = getScheduledReport(id);
      
      if (!report) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Scheduled report not found' }
          }
        });
      }
      
      return Promise.resolve({
        data: report,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Search users
    if (url.startsWith('/api/users/search')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const query = params.get('q') || '';
      
      const filteredUsers = users.filter(user => 
        user.first_name.toLowerCase().includes(query.toLowerCase()) ||
        user.last_name.toLowerCase().includes(query.toLowerCase()) ||
        user.email.toLowerCase().includes(query.toLowerCase())
      );
      
      return Promise.resolve({
        data: filteredUsers,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Export report by ID
    const exportMatch = url.match(/^\/api\/reports\/(\d+)\/export$/);
    if (exportMatch) {
      return Promise.resolve({
        data: { message: 'Report export initiated' },
        status: 200,
        statusText: 'OK',
        headers: {
          'Content-Type': 'application/octet-stream',
          'Content-Disposition': 'attachment; filename="report.xlsx"'
        },
        config: config
      });
    }
    
    // Fall back to original get method
    return originalGet(url, config);
  };
  
  api.post = function(url, data, config) {
    // Save report
    if (url === '/api/reports/save') {
      const savedReport = saveReport(data);
      
      return Promise.resolve({
        data: savedReport,
        status: 201,
        statusText: 'Created',
        headers: {},
        config: config
      });
    }
    
    // Save scheduled report
    if (url === '/api/reports/scheduled') {
      const scheduledReport = saveScheduledReport(data);
      
      return Promise.resolve({
        data: scheduledReport,
        status: 201,
        statusText: 'Created',
        headers: {},
        config: config
      });
    }
    
    // Share report
    const shareMatch = url.match(/^\/api\/reports\/(\d+)\/share$/);
    if (shareMatch) {
      const id = shareMatch[1];
      const updatedReport = reports.find(r => r.id.toString() === id);
      
      if (!updatedReport) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Report not found' }
          }
        });
      }
      
      return Promise.resolve({
        data: updatedReport,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Fall back to original post method
    return originalPost(url, data, config);
  };
  
  api.put = function(url, data, config) {
    // Update report
    const reportMatch = url.match(/^\/api\/reports\/(\d+)$/);
    if (reportMatch) {
      const id = reportMatch[1];
      const report = reports.find(r => r.id.toString() === id);
      
      if (!report) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Report not found' }
          }
        });
      }
      
      Object.assign(report, data);
      
      return Promise.resolve({
        data: report,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Update scheduled report
    const scheduledMatch = url.match(/^\/api\/reports\/scheduled\/(\d+)$/);
    if (scheduledMatch) {
      const id = scheduledMatch[1];
      const report = scheduledReports.find(r => r.id.toString() === id);
      
      if (!report) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Scheduled report not found' }
          }
        });
      }
      
      Object.assign(report, data);
      
      return Promise.resolve({
        data: report,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Fall back to original put method
    return originalPut(url, data, config);
  };
  
  api.delete = function(url, config) {
    // Delete report
    const reportMatch = url.match(/^\/api\/reports\/(\d+)$/);
    if (reportMatch) {
      const id = reportMatch[1];
      const index = reports.findIndex(r => r.id.toString() === id);
      
      if (index === -1) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Report not found' }
          }
        });
      }
      
      reports.splice(index, 1);
      
      return Promise.resolve({
        data: { message: 'Report deleted successfully' },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Delete scheduled report
    const scheduledMatch = url.match(/^\/api\/reports\/scheduled\/(\d+)$/);
    if (scheduledMatch) {
      const id = scheduledMatch[1];
      const index = scheduledReports.findIndex(r => r.id.toString() === id);
      
      if (index === -1) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Scheduled report not found' }
          }
        });
      }
      
      scheduledReports.splice(index, 1);
      
      return Promise.resolve({
        data: { message: 'Scheduled report deleted successfully' },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    
    // Fall back to original delete method
    return originalDelete(url, config);
  };
};