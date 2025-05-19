import React, { lazy, Suspense } from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Lazy loading utilities for components and routes
 */

/**
 * Page loading component
 */
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="text-center">
      <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
      <p className="mt-4 text-gray-600">Loading...</p>
    </div>
  </div>
);

/**
 * Component loading component
 */
const ComponentLoader = () => (
  <div className="flex items-center justify-center p-8">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
);

/**
 * Error fallback component
 */
const ErrorFallback = ({ error, retry }) => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="text-center">
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Failed to load component
      </h2>
      <p className="text-gray-600 mb-4">{error.message}</p>
      <button
        onClick={retry}
        className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-hover"
      >
        Retry
      </button>
    </div>
  </div>
);

/**
 * Enhanced lazy loading with retry capability
 */
export function lazyLoadWithRetry(importFunction, componentName = 'Component') {
  const LazyComponent = lazy(() => {
    return new Promise((resolve, reject) => {
      importFunction()
        .then(resolve)
        .catch((error) => {
          // Retry once after a delay
          setTimeout(() => {
            importFunction()
              .then(resolve)
              .catch(reject);
          }, 1500);
        });
    });
  });

  return LazyComponent;
}

/**
 * Create a lazy loaded page component
 */
export function createLazyPage(importFunction, options = {}) {
  const {
    fallback = <PageLoader />,
    errorFallback = ErrorFallback,
    componentName = 'Page'
  } = options;

  const LazyComponent = lazyLoadWithRetry(importFunction, componentName);

  return (props) => (
    <Suspense fallback={fallback}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * Create a lazy loaded component
 */
export function createLazyComponent(importFunction, options = {}) {
  const {
    fallback = <ComponentLoader />,
    errorFallback = ErrorFallback,
    componentName = 'Component'
  } = options;

  const LazyComponent = lazyLoadWithRetry(importFunction, componentName);

  return (props) => (
    <Suspense fallback={fallback}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * Preload a component
 */
export function preloadComponent(importFunction) {
  importFunction();
}

/**
 * Create lazy routes configuration
 */
export function createLazyRoutes(routeConfig) {
  return routeConfig.map(route => {
    if (route.component && typeof route.component === 'function') {
      return {
        ...route,
        component: createLazyPage(route.component, {
          componentName: route.name || 'Page'
        })
      };
    }
    return route;
  });
}

/**
 * HOC for adding lazy loading to existing components
 */
export function withLazyLoading(importFunction, options = {}) {
  return createLazyComponent(importFunction, options);
}

/**
 * Lazy load with custom loading component
 */
export function lazyLoadWithCustomLoader(importFunction, LoadingComponent) {
  const LazyComponent = lazy(importFunction);
  
  return (props) => (
    <Suspense fallback={<LoadingComponent />}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * Batch lazy loading for multiple components
 */
export function createLazyBatch(imports) {
  const lazyComponents = {};
  
  Object.entries(imports).forEach(([name, importFunction]) => {
    lazyComponents[name] = createLazyComponent(importFunction, {
      componentName: name
    });
  });
  
  return lazyComponents;
}

/**
 * Progressive enhancement wrapper
 */
export function withProgressiveEnhancement(
  LazyEnhancedComponent,
  FallbackComponent
) {
  return (props) => {
    if (typeof window === 'undefined' || !window.requestIdleCallback) {
      return <FallbackComponent {...props} />;
    }
    
    return (
      <Suspense fallback={<FallbackComponent {...props} />}>
        <LazyEnhancedComponent {...props} />
      </Suspense>
    );
  };
}