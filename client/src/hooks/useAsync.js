import { useState, useCallback, useEffect, useRef } from 'react';

/**
 * Custom hook for handling async operations with loading, error, and data states
 * @param {Function} asyncFunction - The async function to execute
 * @param {Array} dependencies - Dependencies for the effect
 * @param {boolean} immediate - Whether to execute immediately on mount
 * @returns {Object} - { execute, data, loading, error, reset }
 */
export const useAsync = (asyncFunction, dependencies = [], immediate = false) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  
  // Track if component is mounted to prevent state updates on unmounted components
  const isMountedRef = useRef(true);
  
  // Track the latest promise to handle race conditions
  const latestPromiseRef = useRef(null);

  const execute = useCallback(
    async (...args) => {
      const thisPromise = Symbol('promise');
      latestPromiseRef.current = thisPromise;
      
      try {
        setLoading(true);
        setError(null);
        
        const result = await asyncFunction(...args);
        
        // Only update state if this is still the latest promise and component is mounted
        if (latestPromiseRef.current === thisPromise && isMountedRef.current) {
          setData(result);
          return result;
        }
      } catch (err) {
        // Only update state if this is still the latest promise and component is mounted
        if (latestPromiseRef.current === thisPromise && isMountedRef.current) {
          setError(err);
          throw err;
        }
      } finally {
        // Only update state if this is still the latest promise and component is mounted
        if (latestPromiseRef.current === thisPromise && isMountedRef.current) {
          setLoading(false);
        }
      }
    },
    [asyncFunction]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    
    if (immediate) {
      execute();
    }
    
    return () => {
      isMountedRef.current = false;
    };
  }, dependencies);

  return {
    execute,
    data,
    loading,
    error,
    reset,
  };
};

/**
 * Hook for handling async operations on demand (not on mount)
 * @param {Function} asyncFunction - The async function to execute
 * @returns {Object} - { execute, data, loading, error, reset }
 */
export const useAsyncCallback = (asyncFunction) => {
  return useAsync(asyncFunction, [], false);
};

/**
 * Hook for handling async operations with debouncing
 * @param {Function} asyncFunction - The async function to execute
 * @param {number} delay - Debounce delay in milliseconds
 * @param {Array} dependencies - Dependencies for the effect
 * @returns {Object} - { execute, data, loading, error, reset }
 */
export const useDebouncedAsync = (asyncFunction, delay = 500, dependencies = []) => {
  const [debouncedFunction, setDebouncedFunction] = useState(null);
  
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedFunction(() => asyncFunction);
    }, delay);
    
    return () => clearTimeout(timeout);
  }, [asyncFunction, delay, ...dependencies]);
  
  return useAsync(debouncedFunction || (() => Promise.resolve()), dependencies);
};

export default useAsync;