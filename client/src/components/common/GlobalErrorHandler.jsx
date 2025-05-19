import React, { useEffect } from 'react';
import { X, AlertTriangle, CheckCircle, Info, AlertCircle } from 'lucide-react';
import { useToast } from '@/components/ui/toast';

/**
 * Global error handler that listens for unhandled errors and displays them
 */
const GlobalErrorHandler = () => {
  const { addToast } = useToast();

  useEffect(() => {
    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      
      let message = 'An unexpected error occurred';
      if (event.reason instanceof Error) {
        message = event.reason.message;
      } else if (typeof event.reason === 'string') {
        message = event.reason;
      }
      
      addToast({
        type: 'error',
        title: 'Error',
        message,
        duration: 5000
      });
      
      // Prevent the default error handling
      event.preventDefault();
    };

    // Handle global errors
    const handleError = (event) => {
      console.error('Global error:', event.error);
      
      addToast({
        type: 'error',
        title: 'Application Error',
        message: event.error?.message || 'An unexpected error occurred',
        duration: 5000
      });
      
      // Prevent the default error handling
      event.preventDefault();
    };

    // Add event listeners
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    // Cleanup
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, [addToast]);

  return null; // This component doesn't render anything
};

/**
 * Hook to handle errors in a consistent way
 */
export const useErrorHandler = () => {
  const { addToast } = useToast();

  const handleError = (error, options = {}) => {
    const {
      title = 'Error',
      showToast = true,
      logError = true,
      rethrow = false
    } = options;

    // Log error if enabled
    if (logError) {
      console.error(`[${title}]:`, error);
    }

    // Extract error message
    let message = 'An unexpected error occurred';
    if (error instanceof Error) {
      message = error.message;
    } else if (error?.response?.data?.message) {
      message = error.response.data.message;
    } else if (error?.response?.data?.error) {
      message = error.response.data.error;
    } else if (typeof error === 'string') {
      message = error;
    }

    // Show toast if enabled
    if (showToast) {
      addToast({
        type: 'error',
        title,
        message,
        duration: 5000
      });
    }

    // Rethrow if requested
    if (rethrow) {
      throw error;
    }

    return { error, message };
  };

  return { handleError };
};

/**
 * Network error interceptor to handle common API errors
 */
export const setupNetworkErrorInterceptor = (api, toast) => {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      // Don't handle cancelled requests
      if (error.code === 'ERR_CANCELED') {
        return Promise.reject(error);
      }

      // Network error
      if (!error.response) {
        toast.addToast({
          type: 'error',
          title: 'Network Error',
          message: 'Unable to connect to the server. Please check your internet connection.',
          duration: 5000
        });
        return Promise.reject(error);
      }

      // Handle specific status codes
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          // Bad request - show error message from server
          toast.addToast({
            type: 'error',
            title: 'Invalid Request',
            message: data?.message || 'The request was invalid',
            duration: 5000
          });
          break;
          
        case 401:
          // Unauthorized - handled by auth interceptor
          break;
          
        case 403:
          toast.addToast({
            type: 'error',
            title: 'Access Denied',
            message: data?.message || 'You do not have permission to perform this action',
            duration: 5000
          });
          break;
          
        case 404:
          toast.addToast({
            type: 'error',
            title: 'Not Found',
            message: data?.message || 'The requested resource was not found',
            duration: 5000
          });
          break;
          
        case 422:
          // Validation error
          let validationMessage = 'Please check your input and try again';
          if (data?.errors) {
            const errorMessages = Object.values(data.errors).flat();
            validationMessage = errorMessages.join(', ');
          } else if (data?.message) {
            validationMessage = data.message;
          }
          
          toast.addToast({
            type: 'error',
            title: 'Validation Error',
            message: validationMessage,
            duration: 5000
          });
          break;
          
        case 429:
          toast.addToast({
            type: 'error',
            title: 'Too Many Requests',
            message: 'Please slow down and try again later',
            duration: 5000
          });
          break;
          
        case 500:
        case 502:
        case 503:
        case 504:
          toast.addToast({
            type: 'error',
            title: 'Server Error',
            message: 'Something went wrong on our end. Please try again later.',
            duration: 5000
          });
          break;
          
        default:
          if (status >= 400) {
            toast.addToast({
              type: 'error',
              title: 'Error',
              message: data?.message || `An error occurred (${status})`,
              duration: 5000
            });
          }
      }
      
      return Promise.reject(error);
    }
  );
};

/**
 * Enhanced error message component for better UX
 */
export const ErrorMessage = ({ 
  error, 
  title = 'Error', 
  showDetails = false,
  onRetry,
  className = ''
}) => {
  if (!error) return null;

  let message = 'An unexpected error occurred';
  let details = null;

  if (error instanceof Error) {
    message = error.message;
    details = error.stack;
  } else if (error?.response?.data?.message) {
    message = error.response.data.message;
    details = error.response.data.errors ? JSON.stringify(error.response.data.errors, null, 2) : null;
  } else if (typeof error === 'string') {
    message = error;
  }

  return (
    <div className={`rounded-md bg-red-50 p-4 ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <AlertCircle className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{message}</p>
          </div>
          
          {showDetails && details && (
            <details className="mt-3">
              <summary className="text-sm text-red-600 cursor-pointer hover:text-red-800">
                Show details
              </summary>
              <pre className="mt-2 text-xs text-red-600 overflow-auto p-2 bg-red-100 rounded">
                {details}
              </pre>
            </details>
          )}
          
          {onRetry && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onRetry}
                className="text-sm font-medium text-red-600 hover:text-red-500"
              >
                Try again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GlobalErrorHandler;