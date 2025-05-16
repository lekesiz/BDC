/**
 * Bundle optimization utilities
 */

import { lazy } from 'react';

/**
 * Dynamically import React components
 * @param {string} componentPath - Path to the component
 * @returns {React.lazy} Lazy-loaded component
 */
export const lazyLoadComponent = (componentPath) => {
  return lazy(() => import(componentPath));
};

/**
 * Bundle size analysis utilities
 */
export const bundleAnalysis = {
  /**
   * Check if bundle analyzer is available
   */
  isAnalyzerAvailable: () => {
    return process.env.NODE_ENV === 'development' && 
           process.env.ANALYZE === 'true';
  },

  /**
   * Get bundle size limit recommendations
   */
  getSizeLimits: () => ({
    js: {
      main: 250, // KB
      vendor: 150, // KB
      perRoute: 50 // KB
    },
    css: {
      main: 100, // KB
      perRoute: 20 // KB
    }
  }),

  /**
   * Optimize imports for tree shaking
   */
  optimizeImports: {
    // Material-UI optimized imports
    mui: {
      // Instead of: import { Button } from '@mui/material';
      // Use: import Button from '@mui/material/Button';
      components: [
        'Button',
        'TextField',
        'Dialog',
        'Card',
        'Typography',
        'Box',
        'Grid',
        'IconButton',
        'Alert',
        'CircularProgress'
      ]
    },
    
    // Lodash optimized imports
    lodash: {
      // Instead of: import _ from 'lodash';
      // Use: import debounce from 'lodash/debounce';
      methods: [
        'debounce',
        'throttle',
        'cloneDeep',
        'isEqual',
        'get',
        'set',
        'merge',
        'pick',
        'omit'
      ]
    },

    // Date-fns optimized imports
    dateFns: {
      // Instead of: import * as dateFns from 'date-fns';
      // Use: import { format } from 'date-fns';
      functions: [
        'format',
        'parse',
        'addDays',
        'subDays',
        'differenceInDays',
        'isValid',
        'startOfDay',
        'endOfDay'
      ]
    }
  }
};

/**
 * Webpack optimization configuration
 */
export const webpackOptimizations = {
  /**
   * Split chunks configuration
   */
  splitChunks: {
    chunks: 'all',
    cacheGroups: {
      default: false,
      vendors: false,
      
      // Vendor splitting
      vendor: {
        name: 'vendor',
        test: /[\\/]node_modules[\\/]/,
        priority: 1
      },
      
      // Common components
      common: {
        name: 'common',
        minChunks: 2,
        priority: 2,
        reuseExistingChunk: true,
        enforce: true
      },
      
      // React ecosystem
      react: {
        name: 'react',
        test: /[\\/]node_modules[\\/](react|react-dom|react-router)[\\/]/,
        priority: 3
      },
      
      // Material-UI
      mui: {
        name: 'mui',
        test: /[\\/]node_modules[\\/](@mui)[\\/]/,
        priority: 4
      },
      
      // Charts and visualizations
      charts: {
        name: 'charts',
        test: /[\\/]node_modules[\\/](recharts|chartjs|react-chartjs-2)[\\/]/,
        priority: 5
      }
    }
  },

  /**
   * Optimization settings
   */
  optimization: {
    usedExports: true, // Tree shaking
    sideEffects: false, // Mark packages as side-effect free
    concatenateModules: true, // Module concatenation
    minimize: true, // Minification
    
    // Runtime chunk
    runtimeChunk: {
      name: 'runtime'
    }
  },

  /**
   * Performance hints
   */
  performance: {
    hints: 'warning',
    maxAssetSize: 512000, // 500 KB
    maxEntrypointSize: 512000 // 500 KB
  }
};

/**
 * Image optimization utilities
 */
export const imageOptimization = {
  /**
   * Supported formats in priority order
   */
  formats: ['webp', 'avif', 'jpg', 'png'],

  /**
   * Generate responsive image srcset
   */
  generateSrcSet: (imagePath, sizes = [320, 640, 1024, 1920]) => {
    const basePath = imagePath.replace(/\.[^/.]+$/, '');
    const extension = imagePath.split('.').pop();
    
    return sizes
      .map(size => `${basePath}-${size}w.${extension} ${size}w`)
      .join(', ');
  },

  /**
   * Get optimized image component props
   */
  getOptimizedProps: (src, alt, options = {}) => ({
    src,
    alt,
    loading: options.priority ? 'eager' : 'lazy',
    decoding: 'async',
    sizes: options.sizes || '(max-width: 768px) 100vw, 50vw',
    srcSet: imageOptimization.generateSrcSet(src),
    ...options
  })
};

/**
 * CSS optimization utilities
 */
export const cssOptimization = {
  /**
   * Critical CSS extraction
   */
  extractCritical: {
    // Paths to extract critical CSS from
    paths: ['/', '/login', '/dashboard'],
    
    // Options for critical CSS
    options: {
      minify: true,
      inline: true,
      width: 1300,
      height: 900
    }
  },

  /**
   * PurgeCSS configuration
   */
  purgeUnused: {
    content: [
      './src/**/*.js',
      './src/**/*.jsx',
      './public/index.html'
    ],
    safelist: [
      // Dynamic classes
      /^bg-/,
      /^text-/,
      /^border-/,
      // Animation classes
      /^animate-/,
      // State classes
      /^hover:/,
      /^focus:/,
      /^active:/
    ]
  }
};

/**
 * Font optimization utilities
 */
export const fontOptimization = {
  /**
   * Preload critical fonts
   */
  preloadFonts: [
    {
      href: '/fonts/inter-var.woff2',
      type: 'font/woff2',
      crossOrigin: 'anonymous'
    }
  ],

  /**
   * Font display strategy
   */
  fontDisplay: 'swap', // Show fallback immediately

  /**
   * Subset fonts for specific character sets
   */
  subsets: {
    latin: 'U+0020-007F',
    latinExtended: 'U+0100-024F',
    turkish: 'U+011E-011F, U+0130-0131, U+015E-015F'
  }
};

/**
 * Service Worker caching strategies
 */
export const cachingStrategies = {
  /**
   * Static assets caching
   */
  staticAssets: {
    strategy: 'cache-first',
    maxAge: 30 * 24 * 60 * 60, // 30 days
    maxEntries: 100
  },

  /**
   * API responses caching
   */
  apiResponses: {
    strategy: 'network-first',
    maxAge: 5 * 60, // 5 minutes
    maxEntries: 50
  },

  /**
   * Image caching
   */
  images: {
    strategy: 'cache-first',
    maxAge: 7 * 24 * 60 * 60, // 7 days
    maxEntries: 200
  }
};

/**
 * Performance monitoring
 */
export const performanceMonitoring = {
  /**
   * Core Web Vitals thresholds
   */
  webVitals: {
    LCP: { good: 2500, poor: 4000 }, // Largest Contentful Paint
    FID: { good: 100, poor: 300 },   // First Input Delay
    CLS: { good: 0.1, poor: 0.25 }   // Cumulative Layout Shift
  },

  /**
   * Custom performance metrics
   */
  customMetrics: {
    // Time to Interactive
    TTI: (callback) => {
      if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              callback(entry.startTime);
              observer.disconnect();
            }
          }
        });
        observer.observe({ entryTypes: ['paint'] });
      }
    },

    // Bundle load time
    bundleLoadTime: (callback) => {
      window.addEventListener('load', () => {
        const loadTime = performance.timing.loadEventEnd - 
                        performance.timing.navigationStart;
        callback(loadTime);
      });
    }
  },

  /**
   * Report performance metrics
   */
  reportMetrics: (metrics) => {
    if (process.env.NODE_ENV === 'production') {
      // Send to analytics service
      console.log('Performance metrics:', metrics);
    }
  }
};

/**
 * Development utilities
 */
export const developmentUtils = {
  /**
   * Check for bundle size warnings
   */
  checkBundleSize: async () => {
    if (process.env.NODE_ENV === 'development') {
      const { exec } = require('child_process');
      
      exec('npm run build -- --stats', (error, stdout, stderr) => {
        if (error) {
          console.error('Bundle size check failed:', error);
          return;
        }
        
        // Parse stats and check against limits
        const stats = JSON.parse(stdout);
        const limits = bundleAnalysis.getSizeLimits();
        
        // Check main bundle
        const mainSize = stats.assets.find(a => a.name.includes('main'))?.size;
        if (mainSize > limits.js.main * 1024) {
          console.warn(`Main bundle exceeds limit: ${mainSize / 1024}KB > ${limits.js.main}KB`);
        }
      });
    }
  },

  /**
   * Generate bundle report
   */
  generateReport: () => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Generate bundle report with: npm run build -- --analyze');
    }
  }
};

export default {
  lazyLoadComponent,
  bundleAnalysis,
  webpackOptimizations,
  imageOptimization,
  cssOptimization,
  fontOptimization,
  cachingStrategies,
  performanceMonitoring,
  developmentUtils
};