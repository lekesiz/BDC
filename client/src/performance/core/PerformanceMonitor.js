// TODO: i18n - processed
/**
 * Performance Monitor
 * 
 * Real-time performance monitoring for React applications.
 */

import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';import { useTranslation } from "react-i18next";

class PerformanceMonitor {
  constructor(config = {}) {
    this.config = {
      enableWebVitals: true,
      enableResourceTiming: true,
      enableUserTiming: true,
      enableNavigationTiming: true,
      enableMemoryMonitoring: true,
      bufferSize: 1000,
      reportingInterval: 30000, // 30 seconds
      ...config
    };

    this.metrics = new Map();
    this.webVitalsData = {};
    this.resourceTimings = [];
    this.userTimings = [];
    this.memorySnapshots = [];
    this.isMonitoring = false;
    this.observers = [];
    this.reportingTimer = null;

    // Bind methods
    this.init = this.init.bind(this);
    this.startMonitoring = this.startMonitoring.bind(this);
    this.stopMonitoring = this.stopMonitoring.bind(this);
    this.recordMetrics = this.recordMetrics.bind(this);
  }

  /**
   * Initialize performance monitoring
   */
  async init() {
    console.log('📊 Initializing Performance Monitor...');

    try {
      // Initialize Web Vitals monitoring
      if (this.config.enableWebVitals) {
        await this._initWebVitals();
      }

      // Initialize Resource Timing monitoring
      if (this.config.enableResourceTiming) {
        this._initResourceTiming();
      }

      // Initialize User Timing monitoring
      if (this.config.enableUserTiming) {
        this._initUserTiming();
      }

      // Initialize Navigation Timing monitoring
      if (this.config.enableNavigationTiming) {
        this._initNavigationTiming();
      }

      // Initialize Memory monitoring
      if (this.config.enableMemoryMonitoring) {
        this._initMemoryMonitoring();
      }

      // Start monitoring
      this.startMonitoring();

      console.log('✅ Performance Monitor initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Performance Monitor:', error);
      throw error;
    }
  }

  /**
   * Start performance monitoring
   */
  startMonitoring() {
    if (this.isMonitoring) {
      console.warn('Performance monitoring already started');
      return;
    }

    this.isMonitoring = true;
    console.log('▶️ Starting performance monitoring...');

    // Start periodic reporting
    this.reportingTimer = setInterval(() => {
      this._generatePerformanceReport();
    }, this.config.reportingInterval);

    // Monitor page visibility changes
    document.addEventListener('visibilitychange', this._handleVisibilityChange.bind(this));

    // Monitor navigation events
    window.addEventListener('beforeunload', this._handleBeforeUnload.bind(this));
  }

  /**
   * Stop performance monitoring
   */
  stopMonitoring() {
    if (!this.isMonitoring) {
      return;
    }

    this.isMonitoring = false;
    console.log('⏹️ Stopping performance monitoring...');

    // Clear reporting timer
    if (this.reportingTimer) {
      clearInterval(this.reportingTimer);
      this.reportingTimer = null;
    }

    // Disconnect observers
    this.observers.forEach((observer) => {
      if (observer && observer.disconnect) {
        observer.disconnect();
      }
    });
    this.observers = [];

    // Remove event listeners
    document.removeEventListener('visibilitychange', this._handleVisibilityChange);
    window.removeEventListener('beforeunload', this._handleBeforeUnload);
  }

  /**
   * Record custom metrics
   */
  recordMetrics(metrics) {
    const timestamp = Date.now();

    Object.entries(metrics).forEach(([key, value]) => {
      if (!this.metrics.has(key)) {
        this.metrics.set(key, []);
      }

      const metricData = this.metrics.get(key);
      metricData.push({ timestamp, value });

      // Keep buffer size in check
      if (metricData.length > this.config.bufferSize) {
        metricData.shift();
      }
    });
  }

  /**
   * Mark performance timing
   */
  mark(name) {
    performance.mark(name);

    if (this.config.enableUserTiming) {
      this.userTimings.push({
        name,
        timestamp: performance.now(),
        type: 'mark'
      });
    }
  }

  /**
   * Measure performance between marks
   */
  measure(name, startMark, endMark) {
    try {
      performance.measure(name, startMark, endMark);

      if (this.config.enableUserTiming) {
        const measure = performance.getEntriesByName(name, 'measure')[0];
        this.userTimings.push({
          name,
          duration: measure.duration,
          startTime: measure.startTime,
          type: 'measure'
        });
      }
    } catch (error) {
      console.warn(`Failed to measure ${name}:`, error);
    }
  }

  /**
   * Get current performance metrics
   */
  getMetrics() {
    return {
      webVitals: this.webVitalsData,
      resourceTimings: this.resourceTimings.slice(-50), // Last 50 resources
      userTimings: this.userTimings.slice(-50), // Last 50 timings
      navigationTiming: this._getNavigationTiming(),
      memoryUsage: this._getCurrentMemoryUsage(),
      customMetrics: this._getCustomMetrics()
    };
  }

  /**
   * Get performance summary
   */
  getSummary() {
    const metrics = this.getMetrics();

    return {
      timestamp: Date.now(),
      webVitals: {
        lcp: metrics.webVitals.lcp?.value || 0,
        fid: metrics.webVitals.fid?.value || 0,
        cls: metrics.webVitals.cls?.value || 0,
        fcp: metrics.webVitals.fcp?.value || 0,
        ttfb: metrics.webVitals.ttfb?.value || 0
      },
      loadTimes: {
        domContentLoaded: metrics.navigationTiming?.domContentLoadedEventEnd || 0,
        loadComplete: metrics.navigationTiming?.loadEventEnd || 0,
        firstPaint: metrics.navigationTiming?.firstPaint || 0
      },
      resourceCounts: {
        total: metrics.resourceTimings.length,
        scripts: metrics.resourceTimings.filter((r) => r.initiatorType === 'script').length,
        stylesheets: metrics.resourceTimings.filter((r) => r.initiatorType === 'link').length,
        images: metrics.resourceTimings.filter((r) => r.initiatorType === 'img').length
      },
      memoryUsage: metrics.memoryUsage,
      performanceScore: this._calculatePerformanceScore(metrics)
    };
  }

  // Private methods

  async _initWebVitals() {
    console.log('📈 Initializing Web Vitals monitoring...');

    // Cumulative Layout Shift
    getCLS((metric) => {
      this.webVitalsData.cls = metric;
      this._reportWebVital('CLS', metric);
    });

    // First Input Delay
    getFID((metric) => {
      this.webVitalsData.fid = metric;
      this._reportWebVital('FID', metric);
    });

    // First Contentful Paint
    getFCP((metric) => {
      this.webVitalsData.fcp = metric;
      this._reportWebVital('FCP', metric);
    });

    // Largest Contentful Paint
    getLCP((metric) => {
      this.webVitalsData.lcp = metric;
      this._reportWebVital('LCP', metric);
    });

    // Time to First Byte
    getTTFB((metric) => {
      this.webVitalsData.ttfb = metric;
      this._reportWebVital('TTFB', metric);
    });
  }

  _initResourceTiming() {
    console.log('📦 Initializing Resource Timing monitoring...');

    // Create Performance Observer for resource timings
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();

        entries.forEach((entry) => {
          if (entry.entryType === 'resource') {
            this.resourceTimings.push({
              name: entry.name,
              duration: entry.duration,
              transferSize: entry.transferSize || 0,
              encodedBodySize: entry.encodedBodySize || 0,
              decodedBodySize: entry.decodedBodySize || 0,
              initiatorType: entry.initiatorType,
              startTime: entry.startTime,
              responseEnd: entry.responseEnd
            });

            // Keep buffer size in check
            if (this.resourceTimings.length > this.config.bufferSize) {
              this.resourceTimings.shift();
            }
          }
        });
      });

      observer.observe({ entryTypes: ['resource'] });
      this.observers.push(observer);
    }
  }

  _initUserTiming() {
    console.log('⏱️ Initializing User Timing monitoring...');

    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();

        entries.forEach((entry) => {
          if (entry.entryType === 'measure' || entry.entryType === 'mark') {
            this.userTimings.push({
              name: entry.name,
              duration: entry.duration || 0,
              startTime: entry.startTime,
              type: entry.entryType
            });

            // Keep buffer size in check
            if (this.userTimings.length > this.config.bufferSize) {
              this.userTimings.shift();
            }
          }
        });
      });

      observer.observe({ entryTypes: ['measure', 'mark'] });
      this.observers.push(observer);
    }
  }

  _initNavigationTiming() {
    console.log('🧭 Initializing Navigation Timing monitoring...');

    // Navigation timing is available immediately after page load
    window.addEventListener('load', () => {
      setTimeout(() => {
        const timing = this._getNavigationTiming();
        console.log('Navigation Timing:', timing);
      }, 0);
    });
  }

  _initMemoryMonitoring() {
    console.log('🧠 Initializing Memory monitoring...');

    // Take memory snapshots periodically
    setInterval(() => {
      const memoryUsage = this._getCurrentMemoryUsage();
      if (memoryUsage) {
        this.memorySnapshots.push({
          timestamp: Date.now(),
          ...memoryUsage
        });

        // Keep buffer size in check
        if (this.memorySnapshots.length > this.config.bufferSize) {
          this.memorySnapshots.shift();
        }
      }
    }, 5000); // Every 5 seconds
  }

  _getNavigationTiming() {
    if (!performance.timing) {
      return null;
    }

    const timing = performance.timing;
    const navigationStart = timing.navigationStart;

    return {
      domainLookupStart: timing.domainLookupStart - navigationStart,
      domainLookupEnd: timing.domainLookupEnd - navigationStart,
      connectStart: timing.connectStart - navigationStart,
      connectEnd: timing.connectEnd - navigationStart,
      requestStart: timing.requestStart - navigationStart,
      responseStart: timing.responseStart - navigationStart,
      responseEnd: timing.responseEnd - navigationStart,
      domLoading: timing.domLoading - navigationStart,
      domInteractive: timing.domInteractive - navigationStart,
      domContentLoadedEventStart: timing.domContentLoadedEventStart - navigationStart,
      domContentLoadedEventEnd: timing.domContentLoadedEventEnd - navigationStart,
      domComplete: timing.domComplete - navigationStart,
      loadEventStart: timing.loadEventStart - navigationStart,
      loadEventEnd: timing.loadEventEnd - navigationStart,
      firstPaint: this._getFirstPaint(),
      firstContentfulPaint: this._getFirstContentfulPaint()
    };
  }

  _getCurrentMemoryUsage() {
    if (performance.memory) {
      return {
        usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
        totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1048576), // MB
        jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) // MB
      };
    }
    return null;
  }

  _getCustomMetrics() {
    const customMetrics = {};

    this.metrics.forEach((values, key) => {
      if (values.length > 0) {
        const latest = values[values.length - 1];
        const average = values.reduce((sum, item) => sum + item.value, 0) / values.length;

        customMetrics[key] = {
          current: latest.value,
          average: Math.round(average * 100) / 100,
          count: values.length
        };
      }
    });

    return customMetrics;
  }

  _getFirstPaint() {
    const entries = performance.getEntriesByType('paint');
    const firstPaint = entries.find((entry) => entry.name === 'first-paint');
    return firstPaint ? firstPaint.startTime : null;
  }

  _getFirstContentfulPaint() {
    const entries = performance.getEntriesByType('paint');
    const firstContentfulPaint = entries.find((entry) => entry.name === 'first-contentful-paint');
    return firstContentfulPaint ? firstContentfulPaint.startTime : null;
  }

  _calculatePerformanceScore(metrics) {
    let score = 100;

    // Deduct points based on Web Vitals
    if (metrics.webVitals.lcp?.value > 2500) {
      score -= 20;
    } else if (metrics.webVitals.lcp?.value > 4000) {
      score -= 40;
    }

    if (metrics.webVitals.fid?.value > 100) {
      score -= 15;
    } else if (metrics.webVitals.fid?.value > 300) {
      score -= 30;
    }

    if (metrics.webVitals.cls?.value > 0.1) {
      score -= 15;
    } else if (metrics.webVitals.cls?.value > 0.25) {
      score -= 30;
    }

    // Deduct points for slow load times
    if (metrics.navigationTiming?.loadEventEnd > 3000) {
      score -= 10;
    }

    // Deduct points for high memory usage
    if (metrics.memoryUsage?.usedJSHeapSize > 100) {// > 100MB
      score -= 10;
    }

    return Math.max(0, Math.min(100, score));
  }

  _reportWebVital(name, metric) {
    console.log(`📊 Web Vital - ${name}:`, metric.value);

    // Check thresholds and warn if needed
    const thresholds = {
      LCP: 2500,
      FID: 100,
      CLS: 0.1,
      FCP: 1800,
      TTFB: 600
    };

    if (thresholds[name] && metric.value > thresholds[name]) {
      console.warn(`⚠️ ${name} is above recommended threshold: ${metric.value} > ${thresholds[name]}`);
    }
  }

  _generatePerformanceReport() {
    const summary = this.getSummary();
    console.log('📊 Performance Report:', summary);

    // You can send this data to your analytics service
    this._sendToAnalytics('performance-report', summary);
  }

  _handleVisibilityChange() {
    if (document.hidden) {
      console.log('📊 Page hidden - pausing detailed monitoring');
    } else {
      console.log('📊 Page visible - resuming detailed monitoring');
    }
  }

  _handleBeforeUnload() {
    // Final performance report before page unload
    const finalReport = this.getSummary();
    console.log('📊 Final Performance Report:', finalReport);
    this._sendToAnalytics('page-unload-performance', finalReport);
  }

  _sendToAnalytics(event, data) {
    // Placeholder for analytics integration
    if (this.config.analyticsCallback) {
      this.config.analyticsCallback(event, data);
    }
  }
}

export default PerformanceMonitor;