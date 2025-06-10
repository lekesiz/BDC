// TODO: i18n - processed
import React, { Suspense, lazy, useState, useEffect, useRef } from 'react';
import { useIntersectionObserver } from 'react-intersection-observer';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';

/**
 * LazyMobileComponent - Optimized lazy loading for mobile devices
 * Features intersection observer, preloading, and fallback components
 */import { useTranslation } from "react-i18next";
export const LazyMobileComponent = ({
  component,
  fallback,
  preload = false,
  threshold = 0.1,
  rootMargin = '50px',
  triggerOnce = true,
  className,
  children,
  ...props
}) => {const { t } = useTranslation();
  const { shouldReduceAnimations, performance } = useMobile();
  const [shouldLoad, setShouldLoad] = useState(preload);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const componentRef = useRef(null);

  // Use intersection observer to trigger loading
  const { ref, inView } = useIntersectionObserver({
    threshold,
    rootMargin,
    triggerOnce,
    skip: shouldLoad
  });

  // Load component when in view
  useEffect(() => {
    if (inView && !shouldLoad) {
      setShouldLoad(true);
    }
  }, [inView, shouldLoad]);

  // Preload on hover/touch for better UX (only on good performance devices)
  const handlePreload = () => {
    if (!shouldLoad && !performance.isSlowDevice) {
      setShouldLoad(true);
    }
  };

  // Error boundary functionality
  useEffect(() => {
    const handleError = () => setHasError(true);
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return (
      <div className={cn('p-4 text-center text-muted-foreground', className)}>
        <p>{t("mobile.failed_to_load_component")}</p>
        <button
          onClick={() => {
            setHasError(false);
            setShouldLoad(false);
            setTimeout(() => setShouldLoad(true), 100);
          }}
          className="mt-2 text-primary underline">{t("archive-components.retry")}


        </button>
      </div>);

  }

  return (
    <div
      ref={ref}
      className={className}
      onMouseEnter={handlePreload}
      onTouchStart={handlePreload}
      {...props}>

      {shouldLoad ?
      <Suspense
        fallback={
        fallback || <LazyLoadingFallback reducedMotion={shouldReduceAnimations} />
        }>

          <LazyComponentWrapper
          component={component}
          onLoad={() => setIsLoaded(true)}
          onError={() => setHasError(true)} />

        </Suspense> :

      <LazyPlaceholder />
      }
      {children}
    </div>);

};

/**
 * LazyComponentWrapper - Wraps the lazy component with error handling
 */
const LazyComponentWrapper = ({ component: Component, onLoad, onError }) => {const { t } = useTranslation();
  useEffect(() => {
    onLoad();
  }, [onLoad]);

  try {
    return <Component />;
  } catch (error) {
    onError(error);
    return null;
  }
};

/**
 * LazyLoadingFallback - Default loading fallback
 */
const LazyLoadingFallback = ({ reducedMotion }) =>
<div className="flex items-center justify-center p-8">
    <div className={cn(
    'w-6 h-6 border-2 border-primary border-t-transparent rounded-full',
    !reducedMotion && 'animate-spin'
  )} />
  </div>;


/**
 * LazyPlaceholder - Placeholder shown before component loads
 */
const LazyPlaceholder = () =>
<div className="bg-muted/30 rounded-lg animate-pulse" style={{ minHeight: '200px' }} />;


/**
 * LazyImage - Optimized image loading with lazy loading
 */
export const LazyImage = ({
  src,
  alt,
  className,
  fallbackSrc,
  placeholder,
  threshold = 0.1,
  rootMargin = '50px',
  loading = 'lazy',
  ...props
}) => {const { t } = useTranslation();
  const { performance, networkStatus } = useMobile();
  const [imageSrc, setImageSrc] = useState(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const { ref, inView } = useIntersectionObserver({
    threshold,
    rootMargin,
    triggerOnce: true
  });

  // Load image when in view
  useEffect(() => {
    if (inView) {
      // Use lower quality on slow connections
      const shouldUseHighQuality = !networkStatus.saveData &&
      networkStatus.effectiveType !== 'slow-2g' &&
      networkStatus.effectiveType !== '2g';

      setImageSrc(shouldUseHighQuality ? src : fallbackSrc || src);
    }
  }, [inView, src, fallbackSrc, networkStatus]);

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const handleImageError = () => {
    setImageError(true);
    if (fallbackSrc && imageSrc !== fallbackSrc) {
      setImageSrc(fallbackSrc);
      setImageError(false);
    }
  };

  return (
    <div ref={ref} className={cn('relative overflow-hidden', className)}>
      {imageSrc ?
      <>
          {/* Placeholder while loading */}
          {!imageLoaded &&
        <div className="absolute inset-0 bg-muted animate-pulse flex items-center justify-center">
              {placeholder || <div className="w-8 h-8 bg-muted-foreground/20 rounded" />}
            </div>
        }
          
          {/* Actual image */}
          <img
          src={imageSrc}
          alt={alt}
          loading={loading}
          onLoad={handleImageLoad}
          onError={handleImageError}
          className={cn(
            'transition-opacity duration-300',
            imageLoaded ? 'opacity-100' : 'opacity-0',
            imageError && 'hidden'
          )}
          {...props} />

          
          {/* Error fallback */}
          {imageError && !fallbackSrc &&
        <div className="absolute inset-0 bg-muted flex items-center justify-center text-muted-foreground">
              <span className="text-sm">{t("components.failed_to_load_image")}</span>
            </div>
        }
        </> :

      // Initial placeholder
      <div className="bg-muted animate-pulse" style={{ paddingBottom: '56.25%' }} />
      }
    </div>);

};

/**
 * LazyList - Virtualized list for large datasets
 */
export const LazyList = ({
  items,
  renderItem,
  itemHeight = 60,
  containerHeight = 400,
  overscan = 5,
  className,
  ...props
}) => {const { t } = useTranslation();
  const { performance } = useMobile();
  const [scrollTop, setScrollTop] = useState(0);
  const [containerRef, setContainerRef] = useState(null);

  // Calculate visible range
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };

  // Disable virtualization on slow devices for simpler rendering
  if (performance.isSlowDevice) {
    return (
      <div
        className={cn('overflow-auto', className)}
        style={{ height: containerHeight }}
        {...props}>

        {items.map((item, index) => renderItem(item, index))}
      </div>);

  }

  return (
    <div
      ref={setContainerRef}
      className={cn('overflow-auto', className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
      {...props}>

      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) =>
          renderItem(item, startIndex + index)
          )}
        </div>
      </div>
    </div>);

};

/**
 * withLazyLoading - HOC to add lazy loading to any component
 */
export const withLazyLoading = (Component, options = {}) => {
  return React.forwardRef((props, ref) =>
  <LazyMobileComponent
    component={() => <Component ref={ref} {...props} />}
    {...options} />

  );
};

/**
 * useLazyLoading - Hook for manual lazy loading control
 */
export const useLazyLoading = (options = {}) => {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    triggerOnce = true
  } = options;

  const { performance } = useMobile();
  const [shouldLoad, setShouldLoad] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const { ref, inView } = useIntersectionObserver({
    threshold,
    rootMargin,
    triggerOnce,
    skip: shouldLoad
  });

  useEffect(() => {
    if (inView && !shouldLoad) {
      setShouldLoad(true);
    }
  }, [inView, shouldLoad]);

  const load = () => setShouldLoad(true);
  const markLoaded = () => setIsLoaded(true);

  return {
    ref,
    shouldLoad,
    isLoaded,
    inView,
    load,
    markLoaded,
    isSlowDevice: performance.isSlowDevice
  };
};

export default LazyMobileComponent;