// Performance optimization utilities

/**
 * Debounce function to limit function calls
 */
export const debounce = (func, delay) => {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
};

/**
 * Throttle function to limit function calls
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Request Idle Callback polyfill
 */
export const requestIdleCallback =
  window.requestIdleCallback ||
  function (cb) {
    const start = Date.now();
    return setTimeout(() => {
      cb({
        didTimeout: false,
        timeRemaining: () => Math.max(0, 50 - (Date.now() - start)),
      });
    }, 1);
  };

/**
 * Cancel Idle Callback polyfill
 */
export const cancelIdleCallback =
  window.cancelIdleCallback ||
  function (id) {
    clearTimeout(id);
  };

/**
 * Defer non-critical work
 */
export const deferWork = (work) => {
  return new Promise((resolve) => {
    requestIdleCallback(() => {
      const result = work();
      resolve(result);
    });
  });
};

/**
 * Batch DOM updates
 */
export const batchDOMUpdates = (updates) => {
  return new Promise((resolve) => {
    requestAnimationFrame(() => {
      updates.forEach(update => update());
      resolve();
    });
  });
};

/**
 * Preload critical resources
 */
export const preloadResource = (href, as, type) => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;
  if (type) link.type = type;
  document.head.appendChild(link);
};

/**
 * Lazy load images with Intersection Observer
 */
export const lazyLoadImages = (selector = 'img[data-lazy]') => {
  const images = document.querySelectorAll(selector);
  
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    });
    
    images.forEach(img => imageObserver.observe(img));
  } else {
    // Fallback for browsers without IntersectionObserver
    images.forEach(img => {
      img.src = img.dataset.src;
      img.classList.add('loaded');
    });
  }
};

/**
 * Measure performance of a function
 */
export const measurePerformance = async (name, fn) => {
  const startMark = `${name}-start`;
  const endMark = `${name}-end`;
  const measureName = `${name}-duration`;
  
  performance.mark(startMark);
  
  try {
    const result = await fn();
    
    performance.mark(endMark);
    performance.measure(measureName, startMark, endMark);
    
    const measure = performance.getEntriesByName(measureName)[0];
    if (process.env.NODE_ENV === 'development') {
      console.log(`${name} took ${measure.duration.toFixed(2)}ms`);
    }
    
    // Clean up
    performance.clearMarks(startMark);
    performance.clearMarks(endMark);
    performance.clearMeasures(measureName);
    
    return result;
  } catch (error) {
    performance.clearMarks(startMark);
    throw error;
  }
};

/**
 * Web Vitals monitoring
 */
export const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

/**
 * Memory usage monitoring
 */
export const getMemoryUsage = () => {
  if (performance.memory) {
    return {
      usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2),
      totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2),
      jsHeapSizeLimit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2),
    };
  }
  return null;
};

/**
 * FPS monitoring
 */
export class FPSMonitor {
  constructor(callback) {
    this.callback = callback;
    this.fps = 0;
    this.frames = 0;
    this.lastTime = performance.now();
    this.running = false;
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.measure();
  }

  stop() {
    this.running = false;
  }

  measure = () => {
    if (!this.running) return;

    const currentTime = performance.now();
    this.frames++;

    if (currentTime >= this.lastTime + 1000) {
      this.fps = Math.round((this.frames * 1000) / (currentTime - this.lastTime));
      this.callback(this.fps);
      this.frames = 0;
      this.lastTime = currentTime;
    }

    requestAnimationFrame(this.measure);
  };
}

/**
 * Prefetch navigation routes
 */
export const prefetchRoute = (path) => {
  if ('prefetch' in HTMLLinkElement.prototype) {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = path;
    document.head.appendChild(link);
  }
};

/**
 * Network connection monitoring
 */
export const getConnectionInfo = () => {
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  
  if (connection) {
    return {
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      saveData: connection.saveData,
    };
  }
  
  return null;
};

/**
 * Adaptive loading based on network and device
 */
export const shouldReduceMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

export const shouldLoadHighQuality = () => {
  const connection = getConnectionInfo();
  
  if (!connection) return true; // Default to high quality if unknown
  
  // Check for save data mode
  if (connection.saveData) return false;
  
  // Check connection quality
  const slowConnections = ['slow-2g', '2g'];
  if (slowConnections.includes(connection.effectiveType)) return false;
  
  return true;
};