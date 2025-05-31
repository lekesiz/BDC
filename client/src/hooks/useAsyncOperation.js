import { useState, useCallback, useEffect } from 'react';
import { toast } from '@/components/ui/use-toast';

/**
 * Custom hook for handling async operations with loading states, error handling, and retry logic
 * @param {Object} options Configuration options
 * @param {boolean} options.showErrorToast Whether to show error toast notifications
 * @param {boolean} options.showSuccessToast Whether to show success toast notifications
 * @param {number} options.retryCount Number of retry attempts for failed operations
 * @param {number} options.retryDelay Delay between retry attempts in ms
 * @param {function} options.onSuccess Callback for successful operations
 * @param {function} options.onError Callback for failed operations
 * @returns {Object} Hook state and methods
 */
export const useAsyncOperation = (options = {}) => {
  const {
    showErrorToast = true,
    showSuccessToast = false,
    retryCount = 0,
    retryDelay = 1000,
    onSuccess,
    onError
  } = options;

  const [state, setState] = useState({
    loading: false,
    error: null,
    data: null,
    attempt: 0
  });

  const execute = useCallback(async (asyncFunction, {
    successMessage,
    errorMessage,
    silent = false
  } = {}) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    const attemptExecution = async (attemptNumber = 0) => {
      try {
        const result = await asyncFunction();
        
        setState(prev => ({ 
          ...prev, 
          loading: false, 
          data: result, 
          error: null,
          attempt: 0
        }));

        if (onSuccess) {
          onSuccess(result);
        }

        if (showSuccessToast && !silent && successMessage) {
          toast.success(successMessage);
        }

        return result;
      } catch (error) {
        console.error('Async operation error:', error);

        if (attemptNumber < retryCount) {
          setState(prev => ({ ...prev, attempt: attemptNumber + 1 }));
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          return attemptExecution(attemptNumber + 1);
        }

        setState(prev => ({ 
          ...prev, 
          loading: false, 
          error,
          attempt: 0
        }));

        if (onError) {
          onError(error);
        }

        if (showErrorToast && !silent) {
          const message = errorMessage || error.response?.data?.message || error.message || 'An error occurred';
          toast.error(message);
        }

        throw error;
      }
    };

    return attemptExecution();
  }, [retryCount, retryDelay, onSuccess, onError, showErrorToast, showSuccessToast]);

  const reset = useCallback(() => {
    setState({
      loading: false,
      error: null,
      data: null,
      attempt: 0
    });
  }, []);

  const retry = useCallback(async () => {
    if (state.error && state.lastAsyncFunction) {
      return execute(state.lastAsyncFunction);
    }
  }, [state.error, state.lastAsyncFunction, execute]);

  return {
    ...state,
    execute,
    reset,
    retry,
    isRetrying: state.attempt > 0
  };
};

/**
 * Hook for API calls with standard error handling
 */
export const useApiCall = (apiFunction, options = {}) => {
  const {
    immediate = false,
    dependencies = [],
    ...asyncOptions
  } = options;

  const { execute, ...state } = useAsyncOperation(asyncOptions);

  const call = useCallback(async (...args) => {
    return execute(() => apiFunction(...args));
  }, [execute, apiFunction]);

  useEffect(() => {
    if (immediate) {
      call();
    }
  }, dependencies);

  return {
    ...state,
    call,
    refetch: call
  };
};

/**
 * Hook for form submissions with loading states
 */
export const useFormSubmit = (onSubmit, options = {}) => {
  const { execute, ...state } = useAsyncOperation({
    showSuccessToast: true,
    ...options
  });

  const handleSubmit = useCallback(async (formData) => {
    return execute(() => onSubmit(formData), {
      successMessage: options.successMessage || 'Form submitted successfully',
      errorMessage: options.errorMessage || 'Failed to submit form'
    });
  }, [execute, onSubmit, options.successMessage, options.errorMessage]);

  return {
    ...state,
    handleSubmit,
    isSubmitting: state.loading
  };
};

/**
 * Hook for data fetching with caching
 */
export const useCachedData = (key, fetchFunction, options = {}) => {
  const {
    ttl = 5 * 60 * 1000, // 5 minutes default TTL
    staleWhileRevalidate = true,
    ...asyncOptions
  } = options;

  const [cache, setCache] = useState(() => {
    const cached = localStorage.getItem(`cache_${key}`);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      if (Date.now() - timestamp < ttl) {
        return { data, isStale: false };
      }
      return { data, isStale: true };
    }
    return null;
  });

  const { execute, ...state } = useAsyncOperation(asyncOptions);

  const fetch = useCallback(async (force = false) => {
    if (!force && cache && (!cache.isStale || staleWhileRevalidate)) {
      return cache.data;
    }

    const result = await execute(fetchFunction);
    
    const cacheData = {
      data: result,
      timestamp: Date.now()
    };
    
    localStorage.setItem(`cache_${key}`, JSON.stringify(cacheData));
    setCache({ data: result, isStale: false });
    
    return result;
  }, [key, fetchFunction, cache, staleWhileRevalidate, execute, ttl]);

  const invalidate = useCallback(() => {
    localStorage.removeItem(`cache_${key}`);
    setCache(null);
  }, [key]);

  return {
    ...state,
    data: cache?.data || state.data,
    isStale: cache?.isStale || false,
    fetch,
    invalidate,
    refetch: () => fetch(true)
  };
};