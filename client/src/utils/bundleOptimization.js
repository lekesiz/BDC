/**
 * Bundle optimization utilities and configurations
 */
/**
 * Webpack optimization configuration
 */
export const webpackOptimizations = {
  splitChunks: {
    chunks: 'all',
    cacheGroups: {
      // React and related libraries
      react: {
        test: /[\\/]node_modules[\\/](react|react-dom|react-router-dom)[\\/]/,
        name: 'react',
        priority: 30,
        reuseExistingChunk: true
      },
      // UI libraries
      ui: {
        test: /[\\/]node_modules[\\/](@radix-ui|@headlessui|framer-motion)[\\/]/,
        name: 'ui',
        priority: 25,
        reuseExistingChunk: true
      },
      // Chart libraries
      charts: {
        test: /[\\/]node_modules[\\/](recharts|d3|victory)[\\/]/,
        name: 'charts',
        priority: 20,
        reuseExistingChunk: true
      },
      // Utility libraries
      utils: {
        test: /[\\/]node_modules[\\/](lodash|moment|date-fns|axios)[\\/]/,
        name: 'utils',
        priority: 15,
        reuseExistingChunk: true
      },
      // All other vendor libraries
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendor',
        priority: 10,
        reuseExistingChunk: true
      },
      // Common modules
      common: {
        minChunks: 2,
        priority: 5,
        reuseExistingChunk: true
      }
    }
  },
  // Runtime chunk
  runtimeChunk: {
    name: 'runtime'
  },
  // Module IDs
  moduleIds: 'deterministic',
  // Minimize in production
  minimize: process.env.NODE_ENV === 'production',
  // Performance hints
  performance: {
    hints: 'warning',
    maxEntrypointSize: 512000, // 500KB
    maxAssetSize: 256000, // 250KB
    assetFilter: (assetFilename) => {
      return assetFilename.endsWith('.js') || assetFilename.endsWith('.css');
    }
  }
};
/**
 * Dynamic import wrapper with error handling
 */
export const dynamicImport = (importFn, options = {}) => {
  const {
    retry = 3,
    delay = 1000,
    onError = console.error
  } = options;
  const attemptImport = async (attempt = 1) => {
    try {
      return await importFn();
    } catch (error) {
      if (attempt < retry) {
        console.warn(`Import failed, retrying (${attempt}/${retry})...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return attemptImport(attempt + 1);
      }
      onError(error);
      throw error;
    }
  };
  return attemptImport();
};
/**
 * Preload critical resources
 */
export const preloadCriticalResources = () => {
  const resources = [
    // Preload fonts
    { href: '/fonts/inter-var.woff2', as: 'font', type: 'font/woff2', crossOrigin: 'anonymous' },
    // Preload critical CSS
    { href: '/css/critical.css', as: 'style' },
    // Preload critical JS
    { href: '/js/app.js', as: 'script' }
  ];
  resources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource.href;
    link.as = resource.as;
    if (resource.type) link.type = resource.type;
    if (resource.crossOrigin) link.crossOrigin = resource.crossOrigin;
    document.head.appendChild(link);
  });
};
/**
 * Prefetch resources for future navigation
 */
export const prefetchResources = (resources = []) => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      resources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = resource;
        document.head.appendChild(link);
      });
    });
  }
};
/**
 * Resource hints for DNS prefetch
 */
export const addResourceHints = () => {
  const domains = [
    'https://api.bdc.com',
    'https://cdn.bdc.com',
    'https://analytics.bdc.com'
  ];
  domains.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'dns-prefetch';
    link.href = domain;
    document.head.appendChild(link);
    // Also add preconnect for critical domains
    const preconnect = document.createElement('link');
    preconnect.rel = 'preconnect';
    preconnect.href = domain;
    preconnect.crossOrigin = 'anonymous';
    document.head.appendChild(preconnect);
  });
};
/**
 * Load script with performance optimization
 */
export const loadScript = (src, options = {}) => {
  const {
    async = true,
    defer = false,
    onLoad = () => {},
    onError = () => {},
    attributes = {}
  } = options;
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.async = async;
    script.defer = defer;
    // Add custom attributes
    Object.entries(attributes).forEach(([key, value]) => {
      script.setAttribute(key, value);
    });
    script.onload = () => {
      onLoad();
      resolve();
    };
    script.onerror = (error) => {
      onError(error);
      reject(error);
    };
    document.head.appendChild(script);
  });
};
/**
 * Lazy load images with Intersection Observer
 */
export const lazyLoadImages = (selector = 'img[data-lazy]') => {
  const images = document.querySelectorAll(selector);
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.lazy;
          img.removeAttribute('data-lazy');
          imageObserver.unobserve(img);
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    });
    images.forEach(img => imageObserver.observe(img));
  } else {
    // Fallback for browsers without Intersection Observer
    images.forEach(img => {
      img.src = img.dataset.lazy;
      img.removeAttribute('data-lazy');
    });
  }
};
/**
 * Create performance budget checker
 */
export const checkPerformanceBudget = () => {
  const budgets = {
    js: 300 * 1024, // 300KB
    css: 100 * 1024, // 100KB
    img: 200 * 1024, // 200KB per image
    total: 1024 * 1024 // 1MB total
  };
  const violations = [];
  // Check JavaScript size
  const jsSize = performance.getEntriesByType('resource')
    .filter(entry => entry.name.endsWith('.js'))
    .reduce((total, entry) => total + entry.transferSize, 0);
  if (jsSize > budgets.js) {
    violations.push(`JavaScript: ${Math.round(jsSize / 1024)}KB exceeds budget of ${budgets.js / 1024}KB`);
  }
  // Check CSS size
  const cssSize = performance.getEntriesByType('resource')
    .filter(entry => entry.name.endsWith('.css'))
    .reduce((total, entry) => total + entry.transferSize, 0);
  if (cssSize > budgets.css) {
    violations.push(`CSS: ${Math.round(cssSize / 1024)}KB exceeds budget of ${budgets.css / 1024}KB`);
  }
  // Check total size
  const totalSize = performance.getEntriesByType('resource')
    .reduce((total, entry) => total + entry.transferSize, 0);
  if (totalSize > budgets.total) {
    violations.push(`Total: ${Math.round(totalSize / 1024)}KB exceeds budget of ${budgets.total / 1024}KB`);
  }
  if (violations.length > 0) {
    console.warn('Performance budget violations:', violations);
  }
  return violations;
};