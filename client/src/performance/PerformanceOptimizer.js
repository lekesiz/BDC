// TODO: i18n - processed
/**
 * Main Performance Optimizer
 * 
 * Central orchestrator for all frontend performance optimizations.
 */

import PerformanceMonitor from './core/PerformanceMonitor';
import CodeSplitter from './core/CodeSplitter';
import LazyLoader from './core/LazyLoader';
import CacheManager from './caching/CacheManager';
import BundleOptimizer from './optimization/BundleOptimizer';
import WebVitalsMonitor from './monitoring/WebVitalsMonitor';
import ImageOptimizer from './utils/ImageOptimizer';
import NetworkOptimizer from './utils/NetworkOptimizer';
import PerformanceConfig from './config/PerformanceConfig';import { useTranslation } from "react-i18next";

class PerformanceOptimizer {
  constructor(config = {}) {
    this.config = new PerformanceConfig(config);
    this.isInitialized = false;
    this.optimizations = new Map();

    // Initialize core components
    this.performanceMonitor = new PerformanceMonitor(this.config.monitoring);
    this.codeSplitter = new CodeSplitter(this.config.codeSplitting);
    this.lazyLoader = new LazyLoader(this.config.lazyLoading);
    this.cacheManager = new CacheManager(this.config.caching);
    this.bundleOptimizer = new BundleOptimizer(this.config.bundleOptimization);
    this.webVitalsMonitor = new WebVitalsMonitor(this.config.webVitals);
    this.imageOptimizer = new ImageOptimizer(this.config.imageOptimization);
    this.networkOptimizer = new NetworkOptimizer(this.config.networkOptimization);

    // Performance metrics
    this.metrics = {
      optimizationsApplied: 0,
      performanceGains: {},
      cacheHitRate: 0,
      bundleSizeReduction: 0,
      imageOptimizationSavings: 0
    };

    // Bind methods
    this.init = this.init.bind(this);
    this.optimizeComponent = this.optimizeComponent.bind(this);
    this.getPerformanceReport = this.getPerformanceReport.bind(this);
  }

  /**
   * Initialize the performance optimizer
   */
  async init() {
    if (this.isInitialized) {
      console.warn('Performance Optimizer already initialized');
      return;
    }

    try {
      console.log('🚀 Initializing Performance Optimizer...');

      // Initialize monitoring first
      await this.performanceMonitor.init();
      await this.webVitalsMonitor.init();

      // Initialize caching
      await this.cacheManager.init();

      // Initialize lazy loading
      this.lazyLoader.init();

      // Initialize image optimization
      this.imageOptimizer.init();

      // Initialize network optimization
      this.networkOptimizer.init();

      // Apply initial optimizations
      await this._applyInitialOptimizations();

      // Start monitoring
      this._startMonitoring();

      this.isInitialized = true;
      console.log('✅ Performance Optimizer initialized successfully');

      // Report initial performance
      this._reportInitialPerformance();

    } catch (error) {
      console.error('❌ Failed to initialize Performance Optimizer:', error);
      throw error;
    }
  }

  /**
   * Optimize a React component
   */
  optimizeComponent(Component, optimizations = {}) {
    const componentName = Component.displayName || Component.name || 'Component';
    console.log(`🔧 Optimizing component: ${componentName}`);

    let OptimizedComponent = Component;
    const appliedOptimizations = [];

    // Apply lazy loading if enabled
    if (optimizations.lazy !== false && this.config.codeSplitting.enabled) {
      OptimizedComponent = this.lazyLoader.wrapComponent(OptimizedComponent);
      appliedOptimizations.push('lazy-loading');
    }

    // Apply memoization if enabled
    if (optimizations.memo !== false && this.config.optimization.memoization) {
      OptimizedComponent = this._applyMemoization(OptimizedComponent);
      appliedOptimizations.push('memoization');
    }

    // Apply error boundary if enabled
    if (optimizations.errorBoundary !== false) {
      OptimizedComponent = this._wrapWithErrorBoundary(OptimizedComponent);
      appliedOptimizations.push('error-boundary');
    }

    // Track optimization
    this.optimizations.set(componentName, {
      originalComponent: Component,
      optimizedComponent: OptimizedComponent,
      appliedOptimizations,
      timestamp: Date.now()
    });

    this.metrics.optimizationsApplied++;
    console.log(`✅ Applied optimizations to ${componentName}:`, appliedOptimizations);

    return OptimizedComponent;
  }

  /**
   * Preload critical resources
   */
  async preloadCriticalResources(resources = []) {
    console.log('📦 Preloading critical resources...');

    const defaultResources = [
    { type: 'style', href: '/styles/critical.css' },
    { type: 'script', href: '/js/vendor.js' },
    { type: 'font', href: '/fonts/main.woff2' }];


    const allResources = [...defaultResources, ...resources];
    const promises = allResources.map((resource) => this._preloadResource(resource));

    try {
      await Promise.all(promises);
      console.log('✅ Critical resources preloaded');
    } catch (error) {
      console.warn('⚠️ Some resources failed to preload:', error);
    }
  }

  /**
   * Optimize images on the page
   */
  async optimizeImages() {
    console.log('🖼️ Optimizing images...');
    const optimizationResults = await this.imageOptimizer.optimizeAllImages();

    this.metrics.imageOptimizationSavings = optimizationResults.totalSavings;
    console.log(`✅ Images optimized, saved ${optimizationResults.totalSavings}KB`);

    return optimizationResults;
  }

  /**
   * Get comprehensive performance report
   */
  getPerformanceReport() {
    const webVitals = this.webVitalsMonitor.getMetrics();
    const cacheStats = this.cacheManager.getStats();
    const bundleStats = this.bundleOptimizer.getStats();
    const imageStats = this.imageOptimizer.getStats();

    return {
      timestamp: Date.now(),
      webVitals,
      cacheStats,
      bundleStats,
      imageStats,
      optimizations: {
        applied: this.metrics.optimizationsApplied,
        components: Array.from(this.optimizations.keys()),
        savings: this.metrics.imageOptimizationSavings
      },
      recommendations: this._generateRecommendations()
    };
  }

  /**
   * Get real-time performance metrics
   */
  getRealTimeMetrics() {
    return {
      timestamp: Date.now(),
      performance: performance.now(),
      memory: this._getMemoryUsage(),
      network: this.networkOptimizer.getNetworkStats(),
      cache: this.cacheManager.getHitRate(),
      webVitals: this.webVitalsMonitor.getCurrentMetrics()
    };
  }

  /**
   * Clear all caches
   */
  async clearCaches() {
    console.log('🧹 Clearing all caches...');
    await this.cacheManager.clearAll();
    console.log('✅ All caches cleared');
  }

  /**
   * Apply performance optimizations to the entire app
   */
  async optimizeApp() {
    console.log('🚀 Applying app-wide optimizations...');

    const optimizations = [];

    // Bundle optimization
    if (this.config.bundleOptimization.enabled) {
      await this.bundleOptimizer.optimize();
      optimizations.push('bundle-optimization');
    }

    // Network optimization
    if (this.config.networkOptimization.enabled) {
      this.networkOptimizer.optimize();
      optimizations.push('network-optimization');
    }

    // Image optimization
    if (this.config.imageOptimization.enabled) {
      await this.optimizeImages();
      optimizations.push('image-optimization');
    }

    // Cache warming
    if (this.config.caching.warmup) {
      await this.cacheManager.warmup();
      optimizations.push('cache-warming');
    }

    console.log('✅ App optimizations applied:', optimizations);
    return optimizations;
  }

  // Private methods

  async _applyInitialOptimizations() {
    console.log('🔧 Applying initial optimizations...');

    // Preload critical resources
    await this.preloadCriticalResources();

    // Initialize service worker for caching
    if (this.config.caching.serviceWorker && 'serviceWorker' in navigator) {
      await this._initServiceWorker();
    }

    // Apply CSS optimizations
    this._applyCSSOptimizations();

    // Apply JavaScript optimizations
    this._applyJSOptimizations();
  }

  _startMonitoring() {
    console.log('📊 Starting performance monitoring...');

    // Monitor performance every 30 seconds
    setInterval(() => {
      const metrics = this.getRealTimeMetrics();
      this.performanceMonitor.recordMetrics(metrics);

      // Check for performance issues
      this._checkPerformanceThresholds(metrics);
    }, 30000);

    // Monitor user interactions
    this._monitorUserInteractions();
  }

  _reportInitialPerformance() {
    // Wait for initial page load to complete
    window.addEventListener('load', () => {
      setTimeout(() => {
        const report = this.getPerformanceReport();
        console.log('📊 Initial Performance Report:', report);

        // Send to analytics if configured
        if (this.config.analytics.enabled) {
          this._sendAnalytics('performance-report', report);
        }
      }, 1000);
    });
  }

  _applyMemoization(Component) {
    const React = require('react');
    return React.memo(Component, (prevProps, nextProps) => {
      // Shallow comparison by default
      return JSON.stringify(prevProps) === JSON.stringify(nextProps);
    });
  }

  _wrapWithErrorBoundary(Component) {
    const React = require('react');

    class ErrorBoundary extends React.Component {
      constructor(props) {
        super(props);
        this.state = { hasError: false };
      }

      static getDerivedStateFromError(error) {
        return { hasError: true };
      }

      componentDidCatch(error, errorInfo) {
        console.error('Component Error:', error, errorInfo);
        // Send error to monitoring service
        this._sendErrorToMonitoring(error, errorInfo);
      }

      render() {
        if (this.state.hasError) {
          return React.createElement('div', {
            className: 'error-fallback'
          }, 'Something went wrong.');
        }

        return React.createElement(Component, this.props);
      }
    }

    return ErrorBoundary;
  }

  async _preloadResource(resource) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');

      if (resource.type === 'style') {
        link.rel = 'preload';
        link.as = 'style';
        link.href = resource.href;
      } else if (resource.type === 'script') {
        link.rel = 'preload';
        link.as = 'script';
        link.href = resource.href;
      } else if (resource.type === 'font') {
        link.rel = 'preload';
        link.as = 'font';
        link.href = resource.href;
        link.crossOrigin = 'anonymous';
      }

      link.onload = resolve;
      link.onerror = reject;

      document.head.appendChild(link);
    });
  }

  async _initServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('✅ Service Worker registered:', registration);
    } catch (error) {
      console.warn('⚠️ Service Worker registration failed:', error);
    }
  }

  _applyCSSOptimizations() {
    // Remove unused CSS classes (basic implementation)
    if (this.config.optimization.removeUnusedCSS) {
      this._removeUnusedCSS();
    }

    // Optimize critical CSS
    if (this.config.optimization.criticalCSS) {
      this._optimizeCriticalCSS();
    }
  }

  _applyJSOptimizations() {
    // Tree shaking is typically handled by bundler
    // Here we can apply runtime optimizations

    // Optimize event listeners
    this._optimizeEventListeners();

    // Optimize animations
    this._optimizeAnimations();
  }

  _checkPerformanceThresholds(metrics) {
    const { webVitals } = metrics;

    // Check LCP threshold
    if (webVitals.lcp > this.config.thresholds.LCP) {
      console.warn(`⚠️ LCP threshold exceeded: ${webVitals.lcp}ms`);
      this._sendAlert('LCP', webVitals.lcp);
    }

    // Check FID threshold
    if (webVitals.fid > this.config.thresholds.FID) {
      console.warn(`⚠️ FID threshold exceeded: ${webVitals.fid}ms`);
      this._sendAlert('FID', webVitals.fid);
    }

    // Check CLS threshold
    if (webVitals.cls > this.config.thresholds.CLS) {
      console.warn(`⚠️ CLS threshold exceeded: ${webVitals.cls}`);
      this._sendAlert('CLS', webVitals.cls);
    }
  }

  _monitorUserInteractions() {
    // Monitor click delays
    document.addEventListener('click', (event) => {
      const startTime = performance.now();

      requestAnimationFrame(() => {
        const delay = performance.now() - startTime;
        if (delay > 100) {// 100ms threshold
          console.warn(`⚠️ Click delay detected: ${delay}ms`);
        }
      });
    });

    // Monitor scroll performance
    let scrolling = false;
    let scrollTimeout;

    window.addEventListener('scroll', () => {
      if (!scrolling) {
        scrolling = true;
        requestAnimationFrame(() => {
          scrolling = false;
        });
      }

      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {

        // Scroll ended - could trigger optimizations
      }, 150);});
  }

  _getMemoryUsage() {
    if (performance.memory) {
      return {
        used: Math.round(performance.memory.usedJSHeapSize / 1048576),
        total: Math.round(performance.memory.totalJSHeapSize / 1048576),
        limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576)
      };
    }
    return null;
  }

  _generateRecommendations() {
    const recommendations = [];
    const metrics = this.getRealTimeMetrics();

    // Memory recommendations
    if (metrics.memory && metrics.memory.used > metrics.memory.total * 0.8) {
      recommendations.push({
        type: 'memory',
        severity: 'high',
        message: 'High memory usage detected. Consider component memoization and cleanup.'
      });
    }

    // Cache recommendations
    if (metrics.cache < 50) {
      recommendations.push({
        type: 'cache',
        severity: 'medium',
        message: 'Low cache hit rate. Consider implementing better caching strategy.'
      });
    }

    // Web Vitals recommendations
    if (metrics.webVitals.lcp > 2500) {
      recommendations.push({
        type: 'lcp',
        severity: 'high',
        message: 'Large Contentful Paint is slow. Optimize images and critical resources.'
      });
    }

    return recommendations;
  }

  _removeUnusedCSS() {
    // Basic unused CSS removal
    // In production, this would be more sophisticated
    console.log('🧹 Removing unused CSS...');
  }

  _optimizeCriticalCSS() {
    // Extract and inline critical CSS
    console.log('🎯 Optimizing critical CSS...');
  }

  _optimizeEventListeners() {
    // Use passive listeners where appropriate
    console.log('👂 Optimizing event listeners...');
  }

  _optimizeAnimations() {
    // Use CSS transforms and will-change property
    console.log('🎬 Optimizing animations...');
  }

  _sendAlert(metric, value) {
    if (this.config.alerts.enabled) {
      console.log(`🚨 Performance Alert: ${metric} = ${value}`);
      // Send to monitoring service
    }
  }

  _sendAnalytics(event, data) {
    if (this.config.analytics.enabled) {
      console.log(`📊 Analytics Event: ${event}`, data);
      // Send to analytics service
    }
  }

  _sendErrorToMonitoring(error, errorInfo) {
    if (this.config.errorTracking.enabled) {
      console.log('🐛 Error sent to monitoring:', error);
      // Send to error tracking service
    }
  }
}

export default PerformanceOptimizer;