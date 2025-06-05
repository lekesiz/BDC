// Performance monitoring utilities for production
// import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals' // Disabled for Docker build
/**
 * Web Vitals monitoring for production
 */
export const reportWebVitals = (onPerfEntry) => {
  // Disabled for Docker build - web-vitals import issues
  }
/**
 * Performance observer for monitoring
 */
export class PerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.observers = new Map()
    this.init()
  }
  init() {
    if (typeof window === 'undefined') return
    // Monitor navigation timing
    this.observeNavigation()
    // Monitor resource loading
    this.observeResources()
    // Monitor long tasks
    this.observeLongTasks()
    // Monitor layout shifts
    this.observeLayoutShift()
  }
  observeNavigation() {
    if ('performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0]
      if (navigation) {
        this.metrics.set('navigation', {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          load: navigation.loadEventEnd - navigation.loadEventStart,
          ttfb: navigation.responseStart - navigation.requestStart
        })
      }
    }
  }
  observeResources() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.duration > 100) { // Only track slow resources
            this.logMetric('slow-resource', {
              name: entry.name,
              duration: entry.duration,
              size: entry.transferSize
            })
          }
        })
      })
      observer.observe({ entryTypes: ['resource'] })
      this.observers.set('resource', observer)
    }
  }
  observeLongTasks() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.logMetric('long-task', {
            duration: entry.duration,
            startTime: entry.startTime
          })
        })
      })
      observer.observe({ entryTypes: ['longtask'] })
      this.observers.set('longtask', observer)
    }
  }
  observeLayoutShift() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        let clsValue = 0
        list.getEntries().forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        })
        if (clsValue > 0.1) { // Only report significant shifts
          this.logMetric('layout-shift', { value: clsValue })
        }
      })
      observer.observe({ entryTypes: ['layout-shift'] })
      this.observers.set('layout-shift', observer)
    }
  }
  logMetric(type, data) {
    // In production, send to analytics service
    if (process.env.NODE_ENV === 'production') {
      // Send to your analytics endpoint
      this.sendToAnalytics(type, data)
    } else if (process.env.NODE_ENV === 'development') {}
  }
  sendToAnalytics(type, data) {
    // Implement your analytics endpoint here
    // Example: Google Analytics, Sentry, custom endpoint
    if (window.gtag) {
      window.gtag('event', 'performance_metric', {
        metric_type: type,
        metric_data: JSON.stringify(data)
      })
    }
  }
  getMetrics() {
    return Object.fromEntries(this.metrics)
  }
  disconnect() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers.clear()
  }
}
/**
 * FPS Monitor for animations
 */
export class FPSMonitor {
  constructor() {
    this.fps = 0
    this.frameCount = 0
    this.lastTime = performance.now()
    this.isRunning = false
  }
  start() {
    if (this.isRunning) return
    this.isRunning = true
    this.tick()
  }
  stop() {
    this.isRunning = false
  }
  tick() {
    if (!this.isRunning) return
    const now = performance.now()
    this.frameCount++
    if (now >= this.lastTime + 1000) {
      this.fps = Math.round((this.frameCount * 1000) / (now - this.lastTime))
      this.frameCount = 0
      this.lastTime = now
      // Log low FPS in development
      if (process.env.NODE_ENV === 'development' && this.fps < 30) {
        console.warn(`[Performance] Low FPS detected: ${this.fps}`)
      }
    }
    requestAnimationFrame(() => this.tick())
  }
  getFPS() {
    return this.fps
  }
}
/**
 * Memory monitoring
 */
export const getMemoryInfo = () => {
  if (performance.memory) {
    return {
      used: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
      total: Math.round(performance.memory.totalJSHeapSize / 1048576), // MB
      limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) // MB
    }
  }
  return null
}
/**
 * Bundle size monitoring
 */
export const getBundleMetrics = () => {
  if ('performance' in window) {
    const resources = performance.getEntriesByType('resource')
    const jsResources = resources.filter(r => r.name.endsWith('.js'))
    const cssResources = resources.filter(r => r.name.endsWith('.css'))
    return {
      totalJS: jsResources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
      totalCSS: cssResources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
      resourceCount: resources.length
    }
  }
  return null
}
/**
 * Network-aware loading
 */
export const getConnectionInfo = () => {
  if ('connection' in navigator) {
    return {
      effectiveType: navigator.connection.effectiveType,
      downlink: navigator.connection.downlink,
      rtt: navigator.connection.rtt,
      saveData: navigator.connection.saveData
    }
  }
  return null
}
/**
 * Adaptive loading based on connection
 */
export const shouldLoadLowQuality = () => {
  const connection = getConnectionInfo()
  if (!connection) return false
  return connection.saveData || 
         connection.effectiveType === 'slow-2g' || 
         connection.effectiveType === '2g' ||
         connection.downlink < 1
}
// Global performance monitor instance
let globalMonitor = null
export const startPerformanceMonitoring = () => {
  if (!globalMonitor) {
    globalMonitor = new PerformanceMonitor()
  }
  return globalMonitor
}
export const stopPerformanceMonitoring = () => {
  if (globalMonitor) {
    globalMonitor.disconnect()
    globalMonitor = null
  }
}