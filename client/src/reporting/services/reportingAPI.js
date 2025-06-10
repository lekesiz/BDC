// TODO: i18n - processed
/**
 * Reporting API Service
 * 
 * Handles all API calls related to the reporting system
 */

import axios from 'axios';import { useTranslation } from "react-i18next";

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class ReportingAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response) {
          // Server responded with error status
          const { status, data } = error.response;
          const message = data.message || data.error || `HTTP ${status} Error`;
          throw new Error(message);
        } else if (error.request) {
          // Network error
          throw new Error('Network error - please check your connection');
        } else {
          // Other error
          throw new Error(error.message || 'An unexpected error occurred');
        }
      }
    );
  }

  // ==================== REPORT BUILDER ====================

  async getAvailableFields() {
    try {
      const response = await this.client.get('/reporting/fields');
      return response;
    } catch (error) {
      console.error('Failed to get available fields:', error);
      throw error;
    }
  }

  async createReportTemplate(templateData) {
    try {
      const response = await this.client.post('/reporting/templates', templateData);
      return response;
    } catch (error) {
      console.error('Failed to create report template:', error);
      throw error;
    }
  }

  async updateReportTemplate(templateId, templateData) {
    try {
      const response = await this.client.put(`/reporting/templates/${templateId}`, templateData);
      return response;
    } catch (error) {
      console.error('Failed to update report template:', error);
      throw error;
    }
  }

  async getReportTemplates(userId = null, category = null) {
    try {
      const params = {};
      if (userId) params.user_id = userId;
      if (category) params.category = category;

      const response = await this.client.get('/reporting/templates', { params });
      return response;
    } catch (error) {
      console.error('Failed to get report templates:', error);
      throw error;
    }
  }

  async deleteReportTemplate(templateId) {
    try {
      const response = await this.client.delete(`/reporting/templates/${templateId}`);
      return response;
    } catch (error) {
      console.error('Failed to delete report template:', error);
      throw error;
    }
  }

  async saveReport(reportData) {
    try {
      const response = await this.client.post('/reporting/reports', reportData);
      return response;
    } catch (error) {
      console.error('Failed to save report:', error);
      throw error;
    }
  }

  async previewReport(reportConfig, sampleSize = 10) {
    try {
      const response = await this.client.post('/reporting/preview', {
        ...reportConfig,
        sample_size: sampleSize
      });
      return response;
    } catch (error) {
      console.error('Failed to preview report:', error);
      throw error;
    }
  }

  async executeReport(reportConfig, limit = null, offset = null) {
    try {
      const response = await this.client.post('/reporting/execute', {
        ...reportConfig,
        limit,
        offset
      });
      return response;
    } catch (error) {
      console.error('Failed to execute report:', error);
      throw error;
    }
  }

  async validateReportConfig(reportConfig) {
    try {
      const response = await this.client.post('/reporting/validate', reportConfig);
      return response;
    } catch (error) {
      console.error('Failed to validate report config:', error);
      throw error;
    }
  }

  // ==================== DASHBOARDS ====================

  async createDashboard(dashboardData) {
    try {
      const response = await this.client.post('/reporting/dashboards', dashboardData);
      return response;
    } catch (error) {
      console.error('Failed to create dashboard:', error);
      throw error;
    }
  }

  async updateDashboard(dashboardId, dashboardData) {
    try {
      const response = await this.client.put(`/reporting/dashboards/${dashboardId}`, dashboardData);
      return response;
    } catch (error) {
      console.error('Failed to update dashboard:', error);
      throw error;
    }
  }

  async getDashboards(userId = null, tags = null) {
    try {
      const params = {};
      if (userId) params.user_id = userId;
      if (tags) params.tags = tags.join(',');

      const response = await this.client.get('/reporting/dashboards', { params });
      return response;
    } catch (error) {
      console.error('Failed to get dashboards:', error);
      throw error;
    }
  }

  async getDashboard(dashboardId) {
    try {
      const response = await this.client.get(`/reporting/dashboards/${dashboardId}`);
      return response;
    } catch (error) {
      console.error('Failed to get dashboard:', error);
      throw error;
    }
  }

  async deleteDashboard(dashboardId) {
    try {
      const response = await this.client.delete(`/reporting/dashboards/${dashboardId}`);
      return response;
    } catch (error) {
      console.error('Failed to delete dashboard:', error);
      throw error;
    }
  }

  async addWidget(dashboardId, widgetConfig) {
    try {
      const response = await this.client.post(`/reporting/dashboards/${dashboardId}/widgets`, widgetConfig);
      return response;
    } catch (error) {
      console.error('Failed to add widget:', error);
      throw error;
    }
  }

  async updateWidget(dashboardId, widgetId, widgetConfig) {
    try {
      const response = await this.client.put(`/reporting/dashboards/${dashboardId}/widgets/${widgetId}`, widgetConfig);
      return response;
    } catch (error) {
      console.error('Failed to update widget:', error);
      throw error;
    }
  }

  async removeWidget(dashboardId, widgetId) {
    try {
      const response = await this.client.delete(`/reporting/dashboards/${dashboardId}/widgets/${widgetId}`);
      return response;
    } catch (error) {
      console.error('Failed to remove widget:', error);
      throw error;
    }
  }

  async loadWidgetData(widgetConfig) {
    try {
      const response = await this.client.post('/reporting/widgets/data', widgetConfig);
      return response;
    } catch (error) {
      console.error('Failed to load widget data:', error);
      throw error;
    }
  }

  async duplicateDashboard(dashboardId, newName) {
    try {
      const response = await this.client.post(`/reporting/dashboards/${dashboardId}/duplicate`, {
        name: newName
      });
      return response;
    } catch (error) {
      console.error('Failed to duplicate dashboard:', error);
      throw error;
    }
  }

  async shareDashboard(dashboardId, userIds, permissions = 'view') {
    try {
      const response = await this.client.post(`/reporting/dashboards/${dashboardId}/share`, {
        user_ids: userIds,
        permissions
      });
      return response;
    } catch (error) {
      console.error('Failed to share dashboard:', error);
      throw error;
    }
  }

  async getDashboardAnalytics(dashboardId, days = 30) {
    try {
      const response = await this.client.get(`/reporting/dashboards/${dashboardId}/analytics`, {
        params: { days }
      });
      return response;
    } catch (error) {
      console.error('Failed to get dashboard analytics:', error);
      throw error;
    }
  }

  // ==================== VISUALIZATIONS ====================

  async createChart(data, chartConfig) {
    try {
      const response = await this.client.post('/reporting/visualizations/chart', {
        data,
        config: chartConfig
      });
      return response;
    } catch (error) {
      console.error('Failed to create chart:', error);
      throw error;
    }
  }

  async createMap(data, mapConfig) {
    try {
      const response = await this.client.post('/reporting/visualizations/map', {
        data,
        config: mapConfig
      });
      return response;
    } catch (error) {
      console.error('Failed to create map:', error);
      throw error;
    }
  }

  async getChartTypes() {
    try {
      const response = await this.client.get('/reporting/visualizations/chart-types');
      return response;
    } catch (error) {
      console.error('Failed to get chart types:', error);
      throw error;
    }
  }

  async getColorPalettes() {
    try {
      const response = await this.client.get('/reporting/visualizations/color-palettes');
      return response;
    } catch (error) {
      console.error('Failed to get color palettes:', error);
      throw error;
    }
  }

  async validateChartConfig(chartConfig, data) {
    try {
      const response = await this.client.post('/reporting/visualizations/validate-chart', {
        config: chartConfig,
        data
      });
      return response;
    } catch (error) {
      console.error('Failed to validate chart config:', error);
      throw error;
    }
  }

  // ==================== EXPORTS ====================

  async exportReport(reportConfig, format, options = {}) {
    try {
      const response = await this.client.post('/reporting/export', {
        report_config: reportConfig,
        format,
        options
      }, {
        responseType: format === 'json' || format === 'xml' ? 'json' : 'blob'
      });

      // Handle blob response for file downloads
      if (response instanceof Blob) {
        const url = window.URL.createObjectURL(response);
        const link = document.createElement('a');
        link.href = url;
        link.download = options.file_name || `report.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        return {
          success: true,
          download_url: url,
          file_name: link.download
        };
      }

      return response;
    } catch (error) {
      console.error('Failed to export report:', error);
      throw error;
    }
  }

  async getSupportedFormats() {
    try {
      const response = await this.client.get('/reporting/export/formats');
      return response;
    } catch (error) {
      console.error('Failed to get supported formats:', error);
      throw error;
    }
  }

  async validateExportConfig(format, config) {
    try {
      const response = await this.client.post('/reporting/export/validate', {
        format,
        config
      });
      return response;
    } catch (error) {
      console.error('Failed to validate export config:', error);
      throw error;
    }
  }

  // ==================== SCHEDULING ====================

  async createScheduledReport(scheduleData) {
    try {
      const response = await this.client.post('/reporting/schedule', scheduleData);
      return response;
    } catch (error) {
      console.error('Failed to create scheduled report:', error);
      throw error;
    }
  }

  async updateScheduledReport(scheduleId, scheduleData) {
    try {
      const response = await this.client.put(`/reporting/schedule/${scheduleId}`, scheduleData);
      return response;
    } catch (error) {
      console.error('Failed to update scheduled report:', error);
      throw error;
    }
  }

  async getScheduledReports(userId = null, includeInactive = false) {
    try {
      const params = {};
      if (userId) params.user_id = userId;
      if (includeInactive) params.include_inactive = true;

      const response = await this.client.get('/reporting/schedule', { params });
      return response;
    } catch (error) {
      console.error('Failed to get scheduled reports:', error);
      throw error;
    }
  }

  async getScheduledReport(scheduleId) {
    try {
      const response = await this.client.get(`/reporting/schedule/${scheduleId}`);
      return response;
    } catch (error) {
      console.error('Failed to get scheduled report:', error);
      throw error;
    }
  }

  async deleteScheduledReport(scheduleId) {
    try {
      const response = await this.client.delete(`/reporting/schedule/${scheduleId}`);
      return response;
    } catch (error) {
      console.error('Failed to delete scheduled report:', error);
      throw error;
    }
  }

  async executeScheduledReport(scheduleId, forceDelivery = false) {
    try {
      const response = await this.client.post(`/reporting/schedule/${scheduleId}/execute`, {
        force_delivery: forceDelivery
      });
      return response;
    } catch (error) {
      console.error('Failed to execute scheduled report:', error);
      throw error;
    }
  }

  async validateScheduleConfig(scheduleData) {
    try {
      const response = await this.client.post('/reporting/schedule/validate', scheduleData);
      return response;
    } catch (error) {
      console.error('Failed to validate schedule config:', error);
      throw error;
    }
  }

  // ==================== REAL-TIME ====================

  async getSystemStats() {
    try {
      const response = await this.client.get('/reporting/realtime/stats');
      return response;
    } catch (error) {
      console.error('Failed to get system stats:', error);
      throw error;
    }
  }

  async getActiveSubscriptions(clientId = null) {
    try {
      const params = {};
      if (clientId) params.client_id = clientId;

      const response = await this.client.get('/reporting/realtime/subscriptions', { params });
      return response;
    } catch (error) {
      console.error('Failed to get active subscriptions:', error);
      throw error;
    }
  }

  // ==================== UTILITY METHODS ====================

  async healthCheck() {
    try {
      const response = await this.client.get('/reporting/health');
      return response;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  async getApiInfo() {
    try {
      const response = await this.client.get('/reporting/info');
      return response;
    } catch (error) {
      console.error('Failed to get API info:', error);
      throw error;
    }
  }

  // Set authentication token
  setAuthToken(token) {
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }

  // Clear authentication token
  clearAuthToken() {
    localStorage.removeItem('authToken');
  }
}

// Create and export a singleton instance
const reportingAPI = new ReportingAPI();
export default reportingAPI;