import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Real User Monitoring (RUM) Component
 * Tracks actual user performance metrics and sends to analytics
 */

class PerformanceTracker {
  constructor() {
    this.metrics = {
      navigation: {},
      resources: [],
      userTiming: [],
      errors: [],
      customMetrics: {}
    };
    
    this.observer = null;
    this.errorHandler = null;
  }

  init() {
    if (typeof window === 'undefined' || !('performance' in window)) {
      return;
    }

    // Track navigation timing
    this.trackNavigationTiming();
    
    // Setup performance observer
    this.setupPerformanceObserver();
    
    // Track errors
    this.setupErrorTracking();
    
    // Track page visibility changes
    this.trackPageVisibility();
    
    // Send metrics on page unload
    this.setupUnloadTracking();
  }

  trackNavigationTiming() {
    // Wait for page load to complete
    if (document.readyState === 'complete') {
      this.captureNavigationMetrics();
    } else {
      window.addEventListener('load', () => {
        this.captureNavigationMetrics();
      });
    }
  }

  captureNavigationMetrics() {
    const navigation = performance.getEntriesByType('navigation')[0];
    
    if (navigation) {
      this.metrics.navigation = {
        // Network timings
        dns: navigation.domainLookupEnd - navigation.domainLookupStart,
        tcp: navigation.connectEnd - navigation.connectStart,
        ssl: navigation.secureConnectionStart > 0 
          ? navigation.connectEnd - navigation.secureConnectionStart 
          : 0,
        ttfb: navigation.responseStart - navigation.requestStart,
        download: navigation.responseEnd - navigation.responseStart,
        
        // Document processing
        domInteractive: navigation.domInteractive - navigation.fetchStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
        domComplete: navigation.domComplete - navigation.fetchStart,
        loadComplete: navigation.loadEventEnd - navigation.fetchStart,
        
        // Core Web Vitals approximations
        fcp: this.getFirstContentfulPaint(),
        lcp: this.getLargestContentfulPaint(),
        fid: this.getFirstInputDelay(),
        cls: this.getCumulativeLayoutShift(),
        
        // Additional metrics
        redirects: navigation.redirectCount,
        navigationType: navigation.type,
        protocol: navigation.nextHopProtocol,
        transferSize: navigation.transferSize || 0,
        encodedBodySize: navigation.encodedBodySize || 0,
        decodedBodySize: navigation.decodedBodySize || 0,
      };
    }
  }

  setupPerformanceObserver() {
    if (!('PerformanceObserver' in window)) return;

    try {
      // Observe long tasks
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.metrics.customMetrics.longTasks = 
            (this.metrics.customMetrics.longTasks || 0) + 1;
          
          // Track tasks longer than 100ms
          if (entry.duration > 100) {
            console.warn('Long task detected:', {
              duration: entry.duration,
              startTime: entry.startTime
            });
          }
        }
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });

      // Observe layout shifts
      const layoutShiftObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            this.metrics.customMetrics.cls = 
              (this.metrics.customMetrics.cls || 0) + entry.value;
          }
        }
      });
      layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });

      // Observe largest contentful paint
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.metrics.customMetrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // Observe first input delay
      const fidObserver = new PerformanceObserver((list) => {
        const firstInput = list.getEntries()[0];
        this.metrics.customMetrics.fid = firstInput.processingStart - firstInput.startTime;
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

    } catch (e) {
      console.error('Failed to setup performance observers:', e);
    }
  }

  getFirstContentfulPaint() {
    const fcp = performance.getEntriesByName('first-contentful-paint')[0];
    return fcp ? fcp.startTime : 0;
  }

  getLargestContentfulPaint() {
    const entries = performance.getEntriesByType('largest-contentful-paint');
    const lastEntry = entries[entries.length - 1];
    return lastEntry ? (lastEntry.renderTime || lastEntry.loadTime) : 0;
  }

  getFirstInputDelay() {
    // This will be captured by the PerformanceObserver
    return this.metrics.customMetrics.fid || 0;
  }

  getCumulativeLayoutShift() {
    // This will be captured by the PerformanceObserver
    return this.metrics.customMetrics.cls || 0;
  }

  setupErrorTracking() {
    this.errorHandler = (event) => {
      this.metrics.errors.push({
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
        timestamp: Date.now(),
        stack: event.error?.stack
      });
    };

    window.addEventListener('error', this.errorHandler);

    // Track unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.metrics.errors.push({
        message: 'Unhandled Promise Rejection',
        reason: event.reason,
        timestamp: Date.now()
      });
    });
  }

  trackPageVisibility() {
    let hiddenTime = 0;
    let hiddenCount = 0;

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        hiddenTime = Date.now();
        hiddenCount++;
      } else if (hiddenTime) {
        const hiddenDuration = Date.now() - hiddenTime;
        this.metrics.customMetrics.totalHiddenTime = 
          (this.metrics.customMetrics.totalHiddenTime || 0) + hiddenDuration;
        this.metrics.customMetrics.hiddenCount = hiddenCount;
      }
    });
  }

  setupUnloadTracking() {
    // Use sendBeacon for reliable metric delivery
    const sendMetrics = () => {
      const data = this.getMetricsSummary();
      const endpoint = `${import.meta.env.VITE_API_URL || ''}/api/analytics/rum`;
      
      if (navigator.sendBeacon) {
        navigator.sendBeacon(endpoint, JSON.stringify(data));
      } else {
        // Fallback to fetch
        fetch(endpoint, {
          method: 'POST',
          body: JSON.stringify(data),
          headers: { 'Content-Type': 'application/json' },
          keepalive: true
        }).catch(() => {
          // Silently fail
        });
      }
    };

    // Send on page unload
    window.addEventListener('pagehide', sendMetrics);
    window.addEventListener('beforeunload', sendMetrics);

    // Also send periodically for long sessions
    setInterval(() => {
      if (document.visibilityState === 'visible') {
        sendMetrics();
      }
    }, 30000); // Every 30 seconds
  }

  getMetricsSummary() {
    return {
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: Date.now(),
      sessionId: this.getSessionId(),
      metrics: {
        ...this.metrics,
        // Device info
        deviceMemory: navigator.deviceMemory || null,
        hardwareConcurrency: navigator.hardwareConcurrency || null,
        connection: this.getConnectionInfo(),
        // Page info
        referrer: document.referrer,
        screenResolution: `${screen.width}x${screen.height}`,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        colorDepth: screen.colorDepth,
      }
    };
  }

  getSessionId() {
    let sessionId = sessionStorage.getItem('rum_session_id');
    if (!sessionId) {
      sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('rum_session_id', sessionId);
    }
    return sessionId;
  }

  getConnectionInfo() {
    if ('connection' in navigator) {
      const conn = navigator.connection;
      return {
        effectiveType: conn.effectiveType,
        downlink: conn.downlink,
        rtt: conn.rtt,
        saveData: conn.saveData
      };
    }
    return null;
  }

  // Custom metric tracking
  trackCustomMetric(name, value) {
    this.metrics.customMetrics[name] = value;
  }

  // Mark custom timing
  mark(name) {
    if (performance.mark) {
      performance.mark(name);
    }
  }

  // Measure between marks
  measure(name, startMark, endMark) {
    if (performance.measure) {
      try {
        performance.measure(name, startMark, endMark);
        const measure = performance.getEntriesByName(name, 'measure')[0];
        if (measure) {
          this.metrics.userTiming.push({
            name,
            duration: measure.duration,
            startTime: measure.startTime
          });
        }
      } catch (e) {
        console.error('Failed to measure:', e);
      }
    }
  }

  // Track resource loading
  trackResourceTiming() {
    const resources = performance.getEntriesByType('resource');
    
    // Group resources by type
    const resourcesByType = {};
    
    resources.forEach(resource => {
      const type = this.getResourceType(resource.name);
      
      if (!resourcesByType[type]) {
        resourcesByType[type] = {
          count: 0,
          totalDuration: 0,
          totalSize: 0,
          items: []
        };
      }
      
      const duration = resource.responseEnd - resource.startTime;
      resourcesByType[type].count++;
      resourcesByType[type].totalDuration += duration;
      resourcesByType[type].totalSize += resource.transferSize || 0;
      
      // Track slow resources
      if (duration > 1000) {
        resourcesByType[type].items.push({
          name: resource.name,
          duration,
          size: resource.transferSize || 0
        });
      }
    });
    
    this.metrics.resources = resourcesByType;
  }

  getResourceType(url) {
    if (/\.(js|mjs)(\?|$)/.test(url)) return 'script';
    if (/\.(css)(\?|$)/.test(url)) return 'style';
    if (/\.(jpg|jpeg|png|gif|webp|svg|ico)(\?|$)/.test(url)) return 'image';
    if (/\.(woff|woff2|ttf|otf|eot)(\?|$)/.test(url)) return 'font';
    if (/\.(mp4|webm|ogg|mp3|wav)(\?|$)/.test(url)) return 'media';
    if (/api\//.test(url)) return 'api';
    return 'other';
  }

  destroy() {
    if (this.errorHandler) {
      window.removeEventListener('error', this.errorHandler);
    }
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

// Singleton instance
let tracker = null;

export const useRealUserMonitoring = () => {
  const location = useLocation();

  useEffect(() => {
    // Initialize tracker on first load
    if (!tracker) {
      tracker = new PerformanceTracker();
      tracker.init();
    }

    // Track route changes
    tracker.mark(`route_start_${location.pathname}`);

    return () => {
      // Measure route duration when leaving
      tracker.mark(`route_end_${location.pathname}`);
      tracker.measure(
        `route_${location.pathname}`,
        `route_start_${location.pathname}`,
        `route_end_${location.pathname}`
      );
    };
  }, [location]);

  // Return tracking functions for component use
  return {
    trackMetric: (name, value) => tracker?.trackCustomMetric(name, value),
    mark: (name) => tracker?.mark(name),
    measure: (name, startMark, endMark) => tracker?.measure(name, startMark, endMark)
  };
};

// Export for use in non-React contexts
export const RUM = {
  trackMetric: (name, value) => tracker?.trackCustomMetric(name, value),
  mark: (name) => tracker?.mark(name),
  measure: (name, startMark, endMark) => tracker?.measure(name, startMark, endMark),
  trackResources: () => tracker?.trackResourceTiming()
};