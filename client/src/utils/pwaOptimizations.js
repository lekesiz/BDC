// TODO: i18n - processed
// PWA Performance Optimization Utilities
import { pwaService } from '../services/pwa.service';
/**
 * Resource Preloader
 * Preloads critical resources for better performance
 */import { useTranslation } from "react-i18next";
export class ResourcePreloader {
  constructor() {
    this.preloadedResources = new Set();
    this.preloadQueue = [];
    this.isPreloading = false;
  }
  /**
   * Preload critical resources
   */
  async preloadCritical() {
    const criticalResources = [
    '/src/App.jsx',
    '/src/components/layout/Header.jsx',
    '/src/components/layout/Sidebar.jsx',
    '/src/components/common/LoadingStates.jsx',
    '/api/auth/me',
    '/api/dashboard'];

    await this.preload(criticalResources, { priority: 'high' });
  }
  /**
   * Preload route-specific resources
   */
  async preloadRoute(route) {
    const routeResources = this.getRouteResources(route);
    await this.preload(routeResources, { priority: 'medium' });
  }
  /**
   * Preload resources with different strategies
   */
  async preload(resources, options = {}) {
    const { priority = 'medium', cache = true } = options;
    for (const resource of resources) {
      if (this.preloadedResources.has(resource)) {
        continue;
      }
      this.preloadQueue.push({ resource, priority, cache });
    }
    if (!this.isPreloading) {
      this.processPreloadQueue();
    }
  }
  async processPreloadQueue() {
    this.isPreloading = true;
    // Sort by priority
    this.preloadQueue.sort((a, b) => {
      const priorities = { high: 3, medium: 2, low: 1 };
      return priorities[b.priority] - priorities[a.priority];
    });
    while (this.preloadQueue.length > 0) {
      const { resource, cache } = this.preloadQueue.shift();
      try {
        await this.preloadResource(resource, cache);
        this.preloadedResources.add(resource);
      } catch (error) {
        console.warn('Failed to preload resource:', resource, error);
      }
    }
    this.isPreloading = false;
  }
  async preloadResource(resource, cache = true) {
    // Determine resource type
    const resourceType = this.getResourceType(resource);
    switch (resourceType) {
      case 'script':
        return this.preloadScript(resource);
      case 'style':
        return this.preloadStyle(resource);
      case 'image':
        return this.preloadImage(resource);
      case 'api':
        return this.preloadAPI(resource, cache);
      case 'font':
        return this.preloadFont(resource);
      default:
        return this.preloadGeneric(resource);
    }
  }
  preloadScript(src) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'modulepreload';
      link.href = src;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }
  preloadStyle(href) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'style';
      link.href = href;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }
  preloadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = resolve;
      img.onerror = reject;
      img.src = src;
    });
  }
  async preloadAPI(url, cache = true) {
    try {
      const response = await fetch(url);
      if (cache && response.ok) {
        await pwaService.cacheUrls([url]);
      }
      return response;
    } catch (error) {
      console.warn('API preload failed:', url, error);
      throw error;
    }
  }
  preloadFont(href) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'font';
      link.type = 'font/woff2';
      link.crossOrigin = 'anonymous';
      link.href = href;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }
  preloadGeneric(href) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = href;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }
  getResourceType(resource) {
    if (resource.startsWith('/api/')) return 'api';
    if (resource.includes('.js') || resource.includes('.jsx')) return 'script';
    if (resource.includes('.css')) return 'style';
    if (resource.match(/\.(png|jpg|jpeg|gif|webp|svg)$/)) return 'image';
    if (resource.match(/\.(woff|woff2|ttf|eot)$/)) return 'font';
    return 'generic';
  }
  getRouteResources(route) {
    const routeResourceMap = {
      '/dashboard': [
      '/src/pages/dashboard/DashboardPage.jsx',
      '/src/components/dashboard/ResponsiveWidget.jsx',
      '/api/dashboard',
      '/api/notifications'],

      '/beneficiaries': [
      '/src/pages/beneficiaries/BeneficiariesPage.jsx',
      '/src/components/beneficiaries/ResponsiveBeneficiariesTable.jsx',
      '/api/beneficiaries'],

      '/evaluations': [
      '/src/pages/evaluation/EvaluationsPage.jsx',
      '/src/components/evaluation/QuestionEditor.jsx',
      '/api/evaluations'],

      '/calendar': [
      '/src/pages/calendar/CalendarPage.jsx',
      '/src/components/calendar/AppointmentModal.jsx',
      '/api/appointments']

    };
    return routeResourceMap[route] || [];
  }
}
/**
 * Lazy Loading Utilities
 */
export class LazyLoader {
  constructor() {
    this.intersectionObserver = null;
    this.loadedElements = new WeakSet();
    this.setupIntersectionObserver();
  }
  setupIntersectionObserver() {
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver not supported');
      return;
    }
    this.intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !this.loadedElements.has(entry.target)) {
            this.loadElement(entry.target);
            this.loadedElements.add(entry.target);
          }
        });
      },
      {
        rootMargin: '50px 0px',
        threshold: 0.1
      }
    );
  }
  observeElement(element) {
    if (this.intersectionObserver && element) {
      this.intersectionObserver.observe(element);
    }
  }
  unobserveElement(element) {
    if (this.intersectionObserver && element) {
      this.intersectionObserver.unobserve(element);
    }
  }
  loadElement(element) {
    const elementType = element.dataset.lazyType;
    switch (elementType) {
      case 'image':
        this.loadImage(element);
        break;
      case 'component':
        this.loadComponent(element);
        break;
      case 'iframe':
        this.loadIframe(element);
        break;
      default:
        this.loadGenericContent(element);
    }
  }
  loadImage(img) {
    const src = img.dataset.src;
    const srcset = img.dataset.srcset;
    if (src) {
      img.src = src;
    }
    if (srcset) {
      img.srcset = srcset;
    }
    img.classList.remove('lazy');
    img.classList.add('loaded');
  }
  loadComponent(element) {
    const componentName = element.dataset.component;
    const loadEvent = new CustomEvent('lazyload', {
      detail: { componentName, element }
    });
    element.dispatchEvent(loadEvent);
  }
  loadIframe(iframe) {
    const src = iframe.dataset.src;
    if (src) {
      iframe.src = src;
      iframe.classList.remove('lazy');
      iframe.classList.add('loaded');
    }
  }
  loadGenericContent(element) {
    const src = element.dataset.src;
    if (src) {
      fetch(src).
      then((response) => response.text()).
      then((html) => {
        element.innerHTML = html;
        element.classList.remove('lazy');
        element.classList.add('loaded');
      }).
      catch((error) => {
        console.error('Failed to load lazy content:', error);
      });
    }
  }
  destroy() {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
    }
  }
}
/**
 * Code Splitting Utilities
 */
export class CodeSplitter {
  constructor() {
    this.loadedChunks = new Set();
    this.chunkCache = new Map();
  }
  /**
   * Dynamically import a module with error handling and caching
   */
  async importModule(modulePath, options = {}) {
    const { cache = true, retry = 2 } = options;
    if (cache && this.chunkCache.has(modulePath)) {
      return this.chunkCache.get(modulePath);
    }
    let lastError;
    for (let attempt = 0; attempt <= retry; attempt++) {
      try {
        const module = await import(modulePath);
        if (cache) {
          this.chunkCache.set(modulePath, module);
        }
        this.loadedChunks.add(modulePath);
        return module;
      } catch (error) {
        lastError = error;
        console.warn(`Import attempt ${attempt + 1} failed for ${modulePath}:`, error);
        if (attempt < retry) {
          await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
        }
      }
    }
    throw lastError;
  }
  /**
   * Preload a module without executing it
   */
  async preloadModule(modulePath) {
    try {
      const link = document.createElement('link');
      link.rel = 'modulepreload';
      link.href = modulePath;
      document.head.appendChild(link);
      return new Promise((resolve, reject) => {
        link.onload = resolve;
        link.onerror = reject;
      });
    } catch (error) {
      console.warn('Module preload failed:', modulePath, error);
    }
  }
  /**
   * Get loading status for a module
   */
  isModuleLoaded(modulePath) {
    return this.loadedChunks.has(modulePath);
  }
  /**
   * Clear module cache
   */
  clearCache() {
    this.chunkCache.clear();
  }
  /**
   * Get cache size information
   */
  getCacheInfo() {
    return {
      cachedModules: this.chunkCache.size,
      loadedChunks: this.loadedChunks.size,
      cacheKeys: Array.from(this.chunkCache.keys())
    };
  }
  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
/**
 * Critical Resource Prioritizer
 */
export class ResourcePrioritizer {
  constructor() {
    this.priorities = new Map();
    this.setupPerformanceObserver();
  }
  setupPerformanceObserver() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.analyzeCriticalResource(entry);
        });
      });
      observer.observe({ entryTypes: ['navigation', 'resource'] });
    }
  }
  analyzeCriticalResource(entry) {
    const { name, duration, startTime } = entry;
    // Resources that load early and take significant time are critical
    const isCritical = startTime < 1000 && duration > 100;
    if (isCritical) {
      this.priorities.set(name, {
        priority: 'critical',
        loadTime: duration,
        timestamp: Date.now()
      });
    }
  }
  getPriority(resourcePath) {
    return this.priorities.get(resourcePath)?.priority || 'normal';
  }
  getCriticalResources() {
    return Array.from(this.priorities.entries()).
    filter(([, data]) => data.priority === 'critical').
    map(([path]) => path);
  }
}
// Export singleton instances
export const resourcePreloader = new ResourcePreloader();
export const lazyLoader = new LazyLoader();
export const codeSplitter = new CodeSplitter();
export const resourcePrioritizer = new ResourcePrioritizer();
// Export utilities for manual use
export const PWAOptimizations = {
  resourcePreloader,
  lazyLoader,
  codeSplitter,
  resourcePrioritizer,
  // Convenience methods
  preloadCritical: () => resourcePreloader.preloadCritical(),
  preloadRoute: (route) => resourcePreloader.preloadRoute(route),
  observeElement: (element) => lazyLoader.observeElement(element),
  importModule: (path, options) => codeSplitter.importModule(path, options),
  // Performance monitoring
  getPerformanceInfo: () => ({
    preloaded: resourcePreloader.preloadedResources.size,
    lazyLoaded: lazyLoader.loadedElements ? 'WeakSet (size unknown)' : 0,
    codeSplitting: codeSplitter.getCacheInfo(),
    critical: resourcePrioritizer.getCriticalResources()
  })
};
export default PWAOptimizations;