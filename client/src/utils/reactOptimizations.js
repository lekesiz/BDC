import React, { 
  memo, 
  useMemo, 
  useCallback, 
  useRef, 
  useEffect,
  useState 
} from 'react';
import { debounce, throttle } from 'lodash';

/**
 * React performance optimization utilities
 */

/**
 * Enhanced memo with deep comparison
 */
export const deepMemo = (Component, propsAreEqual) => {
  return memo(Component, propsAreEqual || deepEqual);
};

/**
 * Deep equality check for props
 */
function deepEqual(prevProps, nextProps) {
  return JSON.stringify(prevProps) === JSON.stringify(nextProps);
}

/**
 * Debounced value hook
 */
export function useDebouncedValue(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Debounced callback hook
 */
export function useDebouncedCallback(callback, delay = 300, deps = []) {
  return useCallback(
    debounce(callback, delay),
     
    deps
  );
}

/**
 * Throttled callback hook
 */
export function useThrottledCallback(callback, delay = 300, deps = []) {
  return useCallback(
    throttle(callback, delay),
     
    deps
  );
}

/**
 * Intersection observer hook for lazy loading
 */
export function useIntersectionObserver(options = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
        if (entry.isIntersecting) {
          setHasIntersected(true);
          if (options.once) {
            observer.disconnect();
          }
        }
      },
      {
        threshold: options.threshold || 0,
        rootMargin: options.rootMargin || '0px',
        root: options.root || null
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [options.once, options.root, options.rootMargin, options.threshold]);

  return { ref: elementRef, isIntersecting, hasIntersected };
}

/**
 * Window size hook with debouncing
 */
export function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0
  });

  useEffect(() => {
    const handleResize = debounce(() => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    }, 150);

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

/**
 * Previous value hook
 */
export function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

/**
 * Virtual scrolling hook
 */
export function useVirtualScroll({
  items,
  itemHeight,
  containerHeight,
  overscan = 5
}) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    startIndex,
    endIndex
  };
}

/**
 * Lazy component with loading state
 */
export function createLazyComponent(
  loader,
  { 
    fallback = <div>Loading...</div>,
    errorFallback = <div>Error loading component</div>,
    delay = 200
  } = {}
) {
  const LazyComponent = React.lazy(() => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(loader());
      }, delay);
    });
  });

  return (props) => (
    <React.Suspense fallback={fallback}>
      <LazyComponent {...props} />
    </React.Suspense>
  );
}

/**
 * Memoized event handler
 */
export function useMemoizedHandler(handler, deps = []) {
  const handlerRef = useRef(handler);

  useEffect(() => {
    handlerRef.current = handler;
  });

  return useCallback((...args) => {
    return handlerRef.current(...args);
  }, deps);
}

/**
 * Stable function reference hook
 */
export function useStableCallback(callback) {
  const callbackRef = useRef(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  });
  
  return useCallback((...args) => {
    return callbackRef.current(...args);
  }, []);
}

/**
 * Performance optimization HOC
 */
export function withPerformanceOptimization(Component, options = {}) {
  const {
    memoize = true,
    trackRenders = false,
    logProps = false
  } = options;

  let OptimizedComponent = Component;

  if (memoize) {
    OptimizedComponent = memo(Component);
  }

  if (trackRenders || logProps) {
    const debugName = Component.displayName || Component.name || 'Component';
    
    return (props) => {
      const renderCount = useRef(0);
      const previousProps = usePrevious(props);

      useEffect(() => {
        renderCount.current += 1;
        
        if (trackRenders) {
          console.log(`${debugName} rendered ${renderCount.current} times`);
        }
        
        if (logProps && previousProps) {
          const changedProps = Object.keys(props).filter(
            key => props[key] !== previousProps[key]
          );
          
          if (changedProps.length > 0) {
            console.log(`${debugName} props changed:`, changedProps);
          }
        }
      });

      return <OptimizedComponent {...props} />;
    };
  }

  return OptimizedComponent;
}

/**
 * Batch state updates
 */
export function useBatchedState(initialState) {
  const [state, setState] = useState(initialState);
  const pendingUpdates = useRef([]);
  const updateTimer = useRef(null);

  const batchedSetState = useCallback((update) => {
    pendingUpdates.current.push(update);
    
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    
    updateTimer.current = setTimeout(() => {
      setState(prevState => {
        let newState = prevState;
        
        pendingUpdates.current.forEach(update => {
          if (typeof update === 'function') {
            newState = { ...newState, ...update(newState) };
          } else {
            newState = { ...newState, ...update };
          }
        });
        
        pendingUpdates.current = [];
        return newState;
      });
    }, 0);
  }, []);

  return [state, batchedSetState];
}

/**
 * Create a performance-optimized context
 */
export function createOptimizedContext(defaultValue) {
  const Context = React.createContext(defaultValue);
  
  const Provider = ({ children, value }) => {
    const memoizedValue = useMemo(() => value, [value]);
    
    return (
      <Context.Provider value={memoizedValue}>
        {children}
      </Context.Provider>
    );
  };
  
  const useContext = () => {
    const context = React.useContext(Context);
    if (context === undefined) {
      throw new Error('useContext must be used within Provider');
    }
    return context;
  };
  
  return { Provider, useContext };
}