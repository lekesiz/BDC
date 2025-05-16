/**
 * Lazy loading utilities for React applications
 */

import React, { useEffect, useState, useRef } from 'react';
import { Skeleton, Box } from '@mui/material';

/**
 * Intersection Observer hook for lazy loading
 */
export const useIntersectionObserver = (options = {}) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const targetRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
          observer.disconnect();
        }
      },
      {
        threshold: options.threshold || 0.1,
        rootMargin: options.rootMargin || '50px',
        ...options
      }
    );

    const currentTarget = targetRef.current;

    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [options]);

  return [targetRef, isIntersecting];
};

/**
 * Lazy image component
 */
export const LazyImage = ({
  src,
  alt,
  placeholder,
  width,
  height,
  className,
  style,
  onLoad,
  onError,
  ...props
}) => {
  const [targetRef, isIntersecting] = useIntersectionObserver();
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (isIntersecting && src) {
      const img = new Image();
      
      img.onload = () => {
        setIsLoaded(true);
        onLoad && onLoad();
      };
      
      img.onerror = () => {
        setHasError(true);
        onError && onError();
      };
      
      img.src = src;
    }
  }, [isIntersecting, src, onLoad, onError]);

  return (
    <div
      ref={targetRef}
      className={className}
      style={{
        width,
        height,
        position: 'relative',
        ...style
      }}
    >
      {!isLoaded && !hasError && (
        placeholder || (
          <Skeleton
            variant="rectangular"
            width={width}
            height={height}
            animation="wave"
          />
        )
      )}
      
      {isLoaded && (
        <img
          src={src}
          alt={alt}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
          {...props}
        />
      )}
      
      {hasError && (
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          width={width}
          height={height}
          bgcolor="grey.200"
          color="grey.600"
        >
          Failed to load image
        </Box>
      )}
    </div>
  );
};

/**
 * Lazy component wrapper
 */
export const LazyComponent = ({
  component: Component,
  fallback,
  threshold = 0.1,
  rootMargin = '50px',
  ...props
}) => {
  const [targetRef, isIntersecting] = useIntersectionObserver({
    threshold,
    rootMargin
  });

  return (
    <div ref={targetRef}>
      {isIntersecting ? (
        <Component {...props} />
      ) : (
        fallback || <Skeleton variant="rectangular" height={200} />
      )}
    </div>
  );
};

/**
 * Lazy list component for virtual scrolling
 */
export const LazyList = ({
  items,
  renderItem,
  itemHeight,
  overscan = 5,
  className,
  style
}) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 });
  const containerRef = useRef(null);
  const scrollTimeoutRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      scrollTimeoutRef.current = setTimeout(() => {
        if (!containerRef.current) return;

        const container = containerRef.current;
        const scrollTop = container.scrollTop;
        const containerHeight = container.clientHeight;

        const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
        const end = Math.min(
          items.length,
          Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
        );

        setVisibleRange({ start, end });
      }, 10);
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      handleScroll(); // Initial calculation
    }

    return () => {
      if (container) {
        container.removeEventListener('scroll', handleScroll);
      }
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [items.length, itemHeight, overscan]);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.start * itemHeight;

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        height: '100%',
        overflowY: 'auto',
        ...style
      }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {items.slice(visibleRange.start, visibleRange.end).map((item, index) => (
            <div
              key={visibleRange.start + index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, visibleRange.start + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Progressive image loading
 */
export const ProgressiveImage = ({
  src,
  placeholder,
  alt,
  width,
  height,
  className,
  style
}) => {
  const [currentSrc, setCurrentSrc] = useState(placeholder);
  const [isLoading, setIsLoading] = useState(true);
  const [targetRef, isIntersecting] = useIntersectionObserver();

  useEffect(() => {
    if (isIntersecting && src) {
      const img = new Image();
      
      img.onload = () => {
        setCurrentSrc(src);
        setIsLoading(false);
      };
      
      img.src = src;
    }
  }, [isIntersecting, src]);

  return (
    <div
      ref={targetRef}
      className={className}
      style={{
        position: 'relative',
        width,
        height,
        overflow: 'hidden',
        ...style
      }}
    >
      <img
        src={currentSrc}
        alt={alt}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          filter: isLoading ? 'blur(10px)' : 'none',
          transition: 'filter 0.3s ease-in-out'
        }}
      />
    </div>
  );
};

/**
 * Lazy load content based on scroll
 */
export const LazyContent = ({
  children,
  fallback,
  offset = 100,
  once = true
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const contentRef = useRef(null);

  useEffect(() => {
    if (hasLoaded && once) return;

    const handleScroll = () => {
      if (!contentRef.current) return;

      const rect = contentRef.current.getBoundingClientRect();
      const isInViewport = rect.top <= window.innerHeight + offset &&
                          rect.bottom >= -offset;

      if (isInViewport) {
        setIsVisible(true);
        if (once) {
          setHasLoaded(true);
          window.removeEventListener('scroll', handleScroll);
        }
      } else if (!once) {
        setIsVisible(false);
      }
    };

    handleScroll(); // Check initial position
    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [offset, once, hasLoaded]);

  return (
    <div ref={contentRef}>
      {isVisible ? children : fallback}
    </div>
  );
};

/**
 * Lazy iframe component
 */
export const LazyIframe = ({
  src,
  title,
  width,
  height,
  className,
  style,
  ...props
}) => {
  const [targetRef, isIntersecting] = useIntersectionObserver();
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <div
      ref={targetRef}
      className={className}
      style={{
        width,
        height,
        position: 'relative',
        ...style
      }}
    >
      {!isLoaded && (
        <Skeleton
          variant="rectangular"
          width={width}
          height={height}
          animation="wave"
        />
      )}
      
      {isIntersecting && (
        <iframe
          src={src}
          title={title}
          width={width}
          height={height}
          onLoad={() => setIsLoaded(true)}
          style={{
            border: 'none',
            display: isLoaded ? 'block' : 'none'
          }}
          {...props}
        />
      )}
    </div>
  );
};

/**
 * Lazy video component
 */
export const LazyVideo = ({
  src,
  poster,
  width,
  height,
  autoPlay = false,
  controls = true,
  className,
  style,
  ...props
}) => {
  const [targetRef, isIntersecting] = useIntersectionObserver();
  const videoRef = useRef(null);

  useEffect(() => {
    if (isIntersecting && autoPlay && videoRef.current) {
      videoRef.current.play();
    }
  }, [isIntersecting, autoPlay]);

  return (
    <div
      ref={targetRef}
      className={className}
      style={{
        width,
        height,
        position: 'relative',
        ...style
      }}
    >
      {isIntersecting ? (
        <video
          ref={videoRef}
          src={src}
          poster={poster}
          width={width}
          height={height}
          controls={controls}
          style={{ width: '100%', height: '100%' }}
          {...props}
        />
      ) : (
        <img
          src={poster}
          alt="Video thumbnail"
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      )}
    </div>
  );
};

/**
 * Lazy loading utilities
 */
export const lazyLoadingUtils = {
  /**
   * Preload images
   */
  preloadImages: (urls) => {
    return Promise.all(
      urls.map(url => {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(url);
          img.onerror = () => reject(new Error(`Failed to load ${url}`));
          img.src = url;
        });
      })
    );
  },

  /**
   * Lazy load script
   */
  loadScript: (src, options = {}) => {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      
      if (options.async) script.async = true;
      if (options.defer) script.defer = true;
      if (options.crossOrigin) script.crossOrigin = options.crossOrigin;
      
      script.onload = () => resolve(script);
      script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
      
      document.head.appendChild(script);
    });
  },

  /**
   * Lazy load CSS
   */
  loadCSS: (href, options = {}) => {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      
      if (options.media) link.media = options.media;
      if (options.crossOrigin) link.crossOrigin = options.crossOrigin;
      
      link.onload = () => resolve(link);
      link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
      
      document.head.appendChild(link);
    });
  },

  /**
   * Priority hints for resources
   */
  addPriorityHint: (resource, priority = 'low') => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource.href;
    link.as = resource.as || 'script';
    link.importance = priority;
    
    if (resource.type) link.type = resource.type;
    if (resource.crossOrigin) link.crossOrigin = resource.crossOrigin;
    
    document.head.appendChild(link);
  }
};

/**
 * Performance monitoring for lazy loading
 */
export const lazyLoadingMonitor = {
  metrics: {
    imagesLoaded: 0,
    imagesFailed: 0,
    scriptsLoaded: 0,
    scriptsFailed: 0,
    totalLoadTime: 0
  },

  trackImageLoad: (success, loadTime) => {
    if (success) {
      lazyLoadingMonitor.metrics.imagesLoaded++;
    } else {
      lazyLoadingMonitor.metrics.imagesFailed++;
    }
    lazyLoadingMonitor.metrics.totalLoadTime += loadTime;
  },

  trackScriptLoad: (success, loadTime) => {
    if (success) {
      lazyLoadingMonitor.metrics.scriptsLoaded++;
    } else {
      lazyLoadingMonitor.metrics.scriptsFailed++;
    }
    lazyLoadingMonitor.metrics.totalLoadTime += loadTime;
  },

  getMetrics: () => lazyLoadingMonitor.metrics,

  reset: () => {
    lazyLoadingMonitor.metrics = {
      imagesLoaded: 0,
      imagesFailed: 0,
      scriptsLoaded: 0,
      scriptsFailed: 0,
      totalLoadTime: 0
    };
  }
};

export default {
  useIntersectionObserver,
  LazyImage,
  LazyComponent,
  LazyList,
  ProgressiveImage,
  LazyContent,
  LazyIframe,
  LazyVideo,
  lazyLoadingUtils,
  lazyLoadingMonitor
};