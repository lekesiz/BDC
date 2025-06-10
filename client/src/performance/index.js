// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Performance Optimization Module for BDC Frontend
 * 
 * This module provides comprehensive frontend performance optimization including:
 * - Code splitting and lazy loading
 * - Caching strategies
 * - Bundle optimization
 * - Real-time performance monitoring
 * - Asset optimization
 */

// Core optimization utilities
export { default as PerformanceMonitor } from './core/PerformanceMonitor';
export { default as CodeSplitter } from './core/CodeSplitter';
export { default as LazyLoader } from './core/LazyLoader';

// Caching utilities
export { default as CacheManager } from './caching/CacheManager';
export { default as ServiceWorkerCache } from './caching/ServiceWorkerCache';
export { default as MemoryCache } from './caching/MemoryCache';

// Bundle optimization
export { default as BundleOptimizer } from './optimization/BundleOptimizer';
export { default as TreeShaker } from './optimization/TreeShaker';
export { default as AssetOptimizer } from './optimization/AssetOptimizer';

// Monitoring and analytics
export { default as WebVitalsMonitor } from './monitoring/WebVitalsMonitor';
export { default as UserExperienceTracker } from './monitoring/UserExperienceTracker';
export { default as PerformanceAnalytics } from './monitoring/PerformanceAnalytics';

// Utilities
export { default as ImageOptimizer } from './utils/ImageOptimizer';
export { default as NetworkOptimizer } from './utils/NetworkOptimizer';
export { default as RenderOptimizer } from './utils/RenderOptimizer';

// Configuration
export { default as PerformanceConfig } from './config/PerformanceConfig';

// Main performance optimization orchestrator
export { default as PerformanceOptimizer } from './PerformanceOptimizer';

// Helper functions
export {
  measurePerformance,
  debounce,
  throttle,
  memoize,
  preloadResource,
  preconnectToOrigin } from
'./utils/helpers';

// Performance constants
export const PERFORMANCE_THRESHOLDS = {
  LCP: 2500, // Largest Contentful Paint
  FID: 100, // First Input Delay
  CLS: 0.1, // Cumulative Layout Shift
  TTFB: 600, // Time to First Byte
  FCP: 1800 // First Contentful Paint
};

export const OPTIMIZATION_LEVELS = {
  BASIC: 'basic',
  MODERATE: 'moderate',
  AGGRESSIVE: 'aggressive'
};