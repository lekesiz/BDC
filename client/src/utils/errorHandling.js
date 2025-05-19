import { toast } from '@/components/ui/use-toast';

/**
 * Centralized error handling utilities
 */

// Error types
export const ErrorTypes = {
  NETWORK: 'NETWORK_ERROR',
  AUTHENTICATION: 'AUTHENTICATION_ERROR',
  AUTHORIZATION: 'AUTHORIZATION_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  SERVER: 'SERVER_ERROR',
  TIMEOUT: 'TIMEOUT_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
};

// Default error messages
export const DefaultErrorMessages = {
  [ErrorTypes.NETWORK]: 'Unable to connect to the server. Please check your connection.',
  [ErrorTypes.AUTHENTICATION]: 'Please log in to continue.',
  [ErrorTypes.AUTHORIZATION]: 'You do not have permission to perform this action.',
  [ErrorTypes.VALIDATION]: 'Please check your input and try again.',
  [ErrorTypes.NOT_FOUND]: 'The requested resource was not found.',
  [ErrorTypes.SERVER]: 'A server error occurred. Please try again later.',
  [ErrorTypes.TIMEOUT]: 'The request timed out. Please try again.',
  [ErrorTypes.UNKNOWN]: 'An unexpected error occurred.'
};

/**
 * Get error type from error object
 */
export const getErrorType = (error) => {
  if (!error) return ErrorTypes.UNKNOWN;
  
  // Network errors
  if (error.code === 'ERR_NETWORK' || error.message === 'Network Error' || !navigator.onLine) {
    return ErrorTypes.NETWORK;
  }
  
  // Timeout errors
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    return ErrorTypes.TIMEOUT;
  }
  
  // HTTP status based errors
  if (error.response) {
    const status = error.response.status;
    
    if (status === 401) return ErrorTypes.AUTHENTICATION;
    if (status === 403) return ErrorTypes.AUTHORIZATION;
    if (status === 404) return ErrorTypes.NOT_FOUND;
    if (status === 422 || status === 400) return ErrorTypes.VALIDATION;
    if (status >= 500) return ErrorTypes.SERVER;
  }
  
  return ErrorTypes.UNKNOWN;
};

/**
 * Get user-friendly error message
 */
export const getErrorMessage = (error, customMessages = {}) => {
  const errorType = getErrorType(error);
  
  // Check for custom message
  if (customMessages[errorType]) {
    return customMessages[errorType];
  }
  
  // Check for API response message
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  
  // Check for API response errors (validation)
  if (error?.response?.data?.errors) {
    const errors = error.response.data.errors;
    if (Array.isArray(errors)) {
      return errors.join(', ');
    }
    if (typeof errors === 'object') {
      return Object.values(errors).flat().join(', ');
    }
  }
  
  // Use default message
  return DefaultErrorMessages[errorType] || error.message || DefaultErrorMessages[ErrorTypes.UNKNOWN];
};

/**
 * Log error for debugging/monitoring
 */
export const logError = (error, context = {}) => {
  const errorInfo = {
    message: error.message,
    stack: error.stack,
    type: getErrorType(error),
    context,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent
  };
  
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error logged:', errorInfo);
  }
  
  // Send to error tracking service (e.g., Sentry)
  if (window.Sentry) {
    window.Sentry.captureException(error, {
      extra: errorInfo
    });
  }
  
  return errorInfo;
};

/**
 * Handle error with toast notification
 */
export const handleError = (error, options = {}) => {
  const {
    showToast = true,
    toastOptions = {},
    customMessages = {},
    context = {},
    onError
  } = options;
  
  // Log the error
  const errorInfo = logError(error, context);
  
  // Get user-friendly message
  const message = getErrorMessage(error, customMessages);
  
  // Show toast notification
  if (showToast) {
    toast.error(message, {
      duration: 4000,
      ...toastOptions
    });
  }
  
  // Call custom error handler
  if (onError) {
    onError(error, errorInfo);
  }
  
  return { error, message, errorInfo };
};

/**
 * Create error handler for API calls
 */
export const createApiErrorHandler = (defaultOptions = {}) => {
  return (error, specificOptions = {}) => {
    const options = { ...defaultOptions, ...specificOptions };
    return handleError(error, options);
  };
};

/**
 * Retry failed request with exponential backoff
 */
export const retryWithBackoff = async (
  fn,
  {
    maxAttempts = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    shouldRetry = (error) => {
      const errorType = getErrorType(error);
      return [ErrorTypes.NETWORK, ErrorTypes.TIMEOUT, ErrorTypes.SERVER].includes(errorType);
    },
    onRetry = (attempt, delay) => {
      console.log(`Retrying... Attempt ${attempt} after ${delay}ms`);
    }
  } = {}
) => {
  let attempt = 0;
  let delay = initialDelay;
  
  while (attempt < maxAttempts) {
    try {
      return await fn();
    } catch (error) {
      attempt++;
      
      if (attempt >= maxAttempts || !shouldRetry(error)) {
        throw error;
      }
      
      onRetry(attempt, delay);
      await new Promise(resolve => setTimeout(resolve, delay));
      
      delay = Math.min(delay * backoffFactor, maxDelay);
    }
  }
};

/**
 * Create error boundary error handler
 */
export const createErrorBoundaryHandler = (options = {}) => {
  return (error, errorInfo) => {
    const errorDetails = {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
      ...options.context
    };
    
    logError(error, errorDetails);
    
    if (options.onError) {
      options.onError(error, errorDetails);
    }
  };
};

/**
 * Format validation errors
 */
export const formatValidationErrors = (errors) => {
  if (!errors) return {};
  
  if (Array.isArray(errors)) {
    return errors.reduce((acc, error) => {
      const field = error.field || 'general';
      if (!acc[field]) acc[field] = [];
      acc[field].push(error.message);
      return acc;
    }, {});
  }
  
  if (typeof errors === 'object') {
    return Object.entries(errors).reduce((acc, [field, messages]) => {
      acc[field] = Array.isArray(messages) ? messages : [messages];
      return acc;
    }, {});
  }
  
  return { general: [errors] };
};