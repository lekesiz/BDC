// Advanced Analytics Service
// Provides comprehensive analytics data aggregation and time-series processing

import api from '@/lib/api';
import { format, subDays, subMonths, subYears, startOfDay, endOfDay } from 'date-fns';

class AnalyticsService {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes cache
  }

  // Cache management
  _getCacheKey(endpoint, params) {
    return `${endpoint}_${JSON.stringify(params)}`;
  }

  _getFromCache(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }
    return null;
  }

  _setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // Date range utilities
  getDateRange(range) {
    const now = new Date();
    switch (range) {
      case 'last7days':
        return {
          start: format(subDays(now, 7), 'yyyy-MM-dd'),
          end: format(now, 'yyyy-MM-dd')
        };
      case 'last30days':
        return {
          start: format(subDays(now, 30), 'yyyy-MM-dd'),
          end: format(now, 'yyyy-MM-dd')
        };
      case 'last90days':
        return {
          start: format(subDays(now, 90), 'yyyy-MM-dd'),
          end: format(now, 'yyyy-MM-dd')
        };
      case 'last6months':
        return {
          start: format(subMonths(now, 6), 'yyyy-MM-dd'),
          end: format(now, 'yyyy-MM-dd')
        };
      case 'thisYear':
        return {
          start: format(new Date(now.getFullYear(), 0, 1), 'yyyy-MM-dd'),
          end: format(now, 'yyyy-MM-dd')
        };
      case 'lastYear':
        return {
          start: format(subYears(new Date(now.getFullYear(), 0, 1), 1), 'yyyy-MM-dd'),
          end: format(subDays(new Date(now.getFullYear(), 0, 1), 1), 'yyyy-MM-dd')
        };
      case 'allTime':
        return {
          start: '2020-01-01',
          end: format(now, 'yyyy-MM-dd')
        };
      default:
        return this.getDateRange('last30days');
    }
  }

  // Real-time metrics
  async getRealtimeMetrics() {
    try {
      const response = await api.get('/api/analytics/realtime/metrics');
      return response.data;
    } catch (error) {
      console.error('Error fetching realtime metrics:', error);
      throw error;
    }
  }

  // Dashboard overview data
  async getDashboardOverview(params = {}) {
    const cacheKey = this._getCacheKey('dashboard_overview', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/dashboard/overview', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching dashboard overview:', error);
      throw error;
    }
  }

  // Beneficiary analytics
  async getBeneficiaryAnalytics(params = {}) {
    const cacheKey = this._getCacheKey('beneficiary_analytics', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/beneficiaries', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching beneficiary analytics:', error);
      throw error;
    }
  }

  // Trainer performance analytics
  async getTrainerAnalytics(params = {}) {
    const cacheKey = this._getCacheKey('trainer_analytics', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/trainers', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching trainer analytics:', error);
      throw error;
    }
  }

  // Program analytics
  async getProgramAnalytics(params = {}) {
    const cacheKey = this._getCacheKey('program_analytics', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/programs', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching program analytics:', error);
      throw error;
    }
  }

  // Time-series data
  async getTimeSeriesData(metric, params = {}) {
    const cacheKey = this._getCacheKey(`timeseries_${metric}`, params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get(`/api/analytics/timeseries/${metric}`, { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching time series data:', error);
      throw error;
    }
  }

  // System health metrics
  async getSystemHealth() {
    try {
      const response = await api.get('/api/analytics/system/health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  }

  // Performance metrics
  async getPerformanceMetrics(params = {}) {
    const cacheKey = this._getCacheKey('performance_metrics', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/performance', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      throw error;
    }
  }

  // Usage patterns
  async getUsagePatterns(params = {}) {
    const cacheKey = this._getCacheKey('usage_patterns', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/usage-patterns', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching usage patterns:', error);
      throw error;
    }
  }

  // Cohort analysis
  async getCohortAnalysis(params = {}) {
    const cacheKey = this._getCacheKey('cohort_analysis', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/cohort-analysis', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching cohort analysis:', error);
      throw error;
    }
  }

  // Custom metrics calculation
  async calculateCustomMetric(metricDefinition, params = {}) {
    try {
      const response = await api.post('/api/analytics/custom-metrics', {
        metric: metricDefinition,
        ...params
      });
      return response.data;
    } catch (error) {
      console.error('Error calculating custom metric:', error);
      throw error;
    }
  }

  // Export functionality
  async exportData(format, dataType, params = {}) {
    try {
      const response = await api.get(`/api/analytics/export/${dataType}`, {
        params: { format, ...params },
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const timestamp = format(new Date(), 'yyyy-MM-dd_HH-mm-ss');
      const extension = format === 'pdf' ? 'pdf' : format === 'excel' ? 'xlsx' : 'csv';
      link.setAttribute('download', `${dataType}_analytics_${timestamp}.${extension}`);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Error exporting data:', error);
      throw error;
    }
  }

  // Advanced filtering
  async getFilteredData(filters, params = {}) {
    const cacheKey = this._getCacheKey('filtered_data', { filters, ...params });
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.post('/api/analytics/filtered-data', {
        filters,
        ...params
      });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching filtered data:', error);
      throw error;
    }
  }

  // Predictive analytics
  async getPredictions(model, params = {}) {
    try {
      const response = await api.post('/api/analytics/predictions', {
        model,
        ...params
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching predictions:', error);
      throw error;
    }
  }

  // Comparative analysis
  async getComparativeAnalysis(baseline, comparison, params = {}) {
    const cacheKey = this._getCacheKey('comparative_analysis', { baseline, comparison, ...params });
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.post('/api/analytics/comparative-analysis', {
        baseline,
        comparison,
        ...params
      });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching comparative analysis:', error);
      throw error;
    }
  }

  // Funnel analysis
  async getFunnelAnalysis(steps, params = {}) {
    const cacheKey = this._getCacheKey('funnel_analysis', { steps, ...params });
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.post('/api/analytics/funnel-analysis', {
        steps,
        ...params
      });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching funnel analysis:', error);
      throw error;
    }
  }

  // Geographic analytics
  async getGeographicAnalytics(params = {}) {
    const cacheKey = this._getCacheKey('geographic_analytics', params);
    const cached = this._getFromCache(cacheKey);
    if (cached) return cached;

    try {
      const response = await api.get('/api/analytics/geographic', { params });
      const data = response.data;
      this._setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching geographic analytics:', error);
      throw error;
    }
  }

  // Clear cache
  clearCache() {
    this.cache.clear();
  }

  // Get cache stats
  getCacheStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

export default new AnalyticsService();