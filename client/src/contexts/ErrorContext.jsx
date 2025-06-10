// TODO: i18n - processed
import React, { createContext, useContext, useState, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, AlertTriangle, XCircle, CheckCircle, Info } from 'lucide-react';
import { createErrorBoundaryHandler } from '@/utils/errorHandling';
/**
 * Global error context for centralized error handling
 */import { useTranslation } from "react-i18next";
const ErrorContext = createContext();
export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within ErrorProvider');
  }
  return context;
};
/**
 * Error notification component
 */
const ErrorNotification = ({ error, onClose }) => {const { t } = useTranslation();
  const icons = {
    error: XCircle,
    warning: AlertTriangle,
    success: CheckCircle,
    info: Info
  };
  const colors = {
    error: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200'
  };
  const Icon = icons[error.type] || AlertTriangle;
  const colorClass = colors[error.type] || colors.error;
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`flex items-start p-4 mb-4 border rounded-lg ${colorClass}`}>

      <Icon className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        {error.title &&
        <h4 className="font-medium mb-1">{error.title}</h4>
        }
        <p className="text-sm">{error.message}</p>
        {error.details &&
        <details className="mt-2">
            <summary className="cursor-pointer text-sm opacity-80">{t("components.show_details")}

          </summary>
            <pre className="mt-2 text-xs overflow-auto p-2 bg-black bg-opacity-5 rounded">
              {JSON.stringify(error.details, null, 2)}
            </pre>
          </details>
        }
      </div>
      <button
        onClick={() => onClose(error.id)}
        className="ml-3 flex-shrink-0 hover:opacity-70 transition-opacity">

        <X className="w-5 h-5" />
      </button>
    </motion.div>);

};
/**
 * Error provider component
 */
export const ErrorProvider = ({ children, options = {} }) => {const { t } = useTranslation();
  const [errors, setErrors] = useState([]);
  const [errorQueue, setErrorQueue] = useState([]);
  const {
    maxErrors = 3,
    errorDuration = 5000,
    position = 'top-right',
    enableErrorBoundary = true
  } = options;
  // Add error to the list
  const addError = useCallback((error) => {
    const newError = {
      id: Date.now() + Math.random(),
      timestamp: new Date(),
      ...error
    };
    setErrors((prev) => {
      const updated = [...prev, newError];
      // Keep only the latest maxErrors
      if (updated.length > maxErrors) {
        setErrorQueue((queue) => [...queue, ...updated.slice(0, updated.length - maxErrors)]);
        return updated.slice(-maxErrors);
      }
      return updated;
    });
    // Auto-remove after duration
    if (errorDuration > 0 && error.type !== 'error') {
      setTimeout(() => {
        removeError(newError.id);
      }, errorDuration);
    }
    return newError;
  }, [maxErrors, errorDuration]);
  // Remove error
  const removeError = useCallback((id) => {
    setErrors((prev) => prev.filter((error) => error.id !== id));
    // Check if there are queued errors
    setErrorQueue((queue) => {
      if (queue.length > 0) {
        const [next, ...rest] = queue;
        setErrors((prev) => [...prev, next]);
        return rest;
      }
      return queue;
    });
  }, []);
  // Clear all errors
  const clearErrors = useCallback(() => {
    setErrors([]);
    setErrorQueue([]);
  }, []);
  // Show error notification
  const showError = useCallback((message, options = {}) => {
    return addError({
      type: 'error',
      message,
      ...options
    });
  }, [addError]);
  // Show warning notification
  const showWarning = useCallback((message, options = {}) => {
    return addError({
      type: 'warning',
      message,
      ...options
    });
  }, [addError]);
  // Show success notification
  const showSuccess = useCallback((message, options = {}) => {
    return addError({
      type: 'success',
      message,
      ...options
    });
  }, [addError]);
  // Show info notification
  const showInfo = useCallback((message, options = {}) => {
    return addError({
      type: 'info',
      message,
      ...options
    });
  }, [addError]);
  // Error boundary handler
  const errorBoundaryHandler = React.useMemo(() => {
    if (!enableErrorBoundary) return null;
    return createErrorBoundaryHandler({
      onError: (error, details) => {
        showError('An unexpected error occurred', {
          title: 'Application Error',
          details: {
            error: error.toString(),
            ...details
          }
        });
      }
    });
  }, [enableErrorBoundary, showError]);
  // Position classes
  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  };
  const value = {
    errors,
    errorQueue,
    addError,
    removeError,
    clearErrors,
    showError,
    showWarning,
    showSuccess,
    showInfo,
    errorBoundaryHandler
  };
  return (
    <ErrorContext.Provider value={value}>
      {children}
      {/* Error notifications container */}
      <div className={`fixed z-50 ${positionClasses[position] || positionClasses['top-right']}`}>
        <AnimatePresence>
          {errors.map((error) =>
          <ErrorNotification
            key={error.id}
            error={error}
            onClose={removeError} />

          )}
        </AnimatePresence>
      </div>
    </ErrorContext.Provider>);

};
/**
 * Hook for handling async errors
 */
export const useAsyncError = () => {
  const { showError } = useError();
  return useCallback((error) => {
    // This will be caught by the nearest error boundary
    throw error;
  }, []);
};
/**
 * Error boundary component that integrates with ErrorContext
 */
export const ContextErrorBoundary = ({ children }) => {const { t } = useTranslation();
  const { errorBoundaryHandler } = useError();
  return (
    <ErrorBoundary
      onError={errorBoundaryHandler}
      fallback={(error, errorInfo, reset) =>
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">{t("components.something_went_wrong")}

          </h1>
            <p className="text-gray-600 mb-6">
              An unexpected error occurred. Please try refreshing the page.
            </p>
            <div className="flex gap-3">
              <button
              onClick={reset}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">{t("components.try_again")}


            </button>
              <button
              onClick={() => window.location.href = '/'}
              className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">{t("components.go_home")}


            </button>
            </div>
            {process.env.NODE_ENV === 'development' &&
          <details className="mt-6">
                <summary className="cursor-pointer text-sm text-gray-500">{t("components.error_details")}

            </summary>
                <pre className="mt-2 text-xs bg-gray-100 p-3 rounded overflow-auto">
                  {error.toString()}
                </pre>
              </details>
          }
          </div>
        </div>
      }>

      {children}
    </ErrorBoundary>);

};