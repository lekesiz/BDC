// TODO: i18n - processed
/**
 * React Hook for Distributed Tracing
 * Provides easy integration of tracing into React components
 */
import { useEffect, useRef, useCallback } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import tracingService, {
  traceOperation,
  tracePageLoad,
  traceUserAction,
  traceError,
  getCorrelationId } from
'../services/tracing';
/**
 * Hook for tracing component lifecycle and operations
 */import { useTranslation } from "react-i18next";
export const useTracing = (componentName, options = {}) => {
  const spanRef = useRef(null);
  const location = useLocation();
  const params = useParams();
  const {
    traceMount = true,
    traceUnmount = true,
    traceRenders = false,
    autoTraceErrors = true
  } = options;
  // Trace component mount
  useEffect(() => {
    if (traceMount) {
      spanRef.current = tracingService.createSpan(
        `component.${componentName}.mount`,
        'INTERNAL',
        {
          'component.name': componentName,
          'component.path': location.pathname,
          'component.params': JSON.stringify(params)
        }
      );
    }
    // Cleanup on unmount
    return () => {
      if (traceUnmount && spanRef.current) {
        spanRef.current.setAttributes({
          'component.lifecycle': 'unmount'
        });
        spanRef.current.end();
      }
    };
  }, [componentName, location.pathname, traceMount, traceUnmount]);
  // Trace renders if enabled
  useEffect(() => {
    if (traceRenders) {
      const renderSpan = tracingService.createSpan(
        `component.${componentName}.render`,
        'INTERNAL',
        {
          'component.name': componentName,
          'render.timestamp': Date.now()
        }
      );
      renderSpan.end();
    }
  });
  // Error boundary integration
  useEffect(() => {
    if (autoTraceErrors) {
      const originalConsoleError = console.error;
      console.error = (...args) => {
        const error = args[0];
        if (error instanceof Error) {
          traceError(error, {
            component: componentName,
            location: location.pathname
          });
        }
        originalConsoleError.apply(console, args);
      };
      return () => {
        console.error = originalConsoleError;
      };
    }
  }, [componentName, location.pathname, autoTraceErrors]);
  // Trace operation wrapper
  const trace = useCallback((operationName, operation, attributes = {}) => {
    return traceOperation(
      `${componentName}.${operationName}`,
      operation,
      'INTERNAL',
      {
        'component.name': componentName,
        ...attributes
      }
    );
  }, [componentName]);
  // Trace async operation wrapper
  const traceAsync = useCallback(async (operationName, operation, attributes = {}) => {
    return traceOperation(
      `${componentName}.${operationName}`,
      async (span) => {
        try {
          const result = await operation(span);
          span.setAttributes({
            'operation.result': 'success',
            'operation.async': true
          });
          return result;
        } catch (error) {
          span.setAttributes({
            'operation.result': 'error',
            'operation.async': true,
            'error.message': error.message
          });
          throw error;
        }
      },
      'INTERNAL',
      {
        'component.name': componentName,
        ...attributes
      }
    );
  }, [componentName]);
  // Trace user action
  const traceAction = useCallback((actionName, elementInfo = {}) => {
    return traceUserAction(`${componentName}.${actionName}`, {
      component: componentName,
      ...elementInfo
    });
  }, [componentName]);
  return {
    trace,
    traceAsync,
    traceAction,
    correlationId: getCorrelationId(),
    componentSpan: spanRef.current
  };
};
/**
 * Hook for tracing page loads and navigation
 */
export const usePageTracing = (pageName) => {
  const location = useLocation();
  const params = useParams();
  useEffect(() => {
    tracePageLoad(pageName, {
      path: location.pathname,
      search: location.search,
      hash: location.hash,
      params
    });
  }, [pageName, location.pathname, location.search, location.hash, params]);
  return {
    currentPage: pageName,
    correlationId: getCorrelationId()
  };
};
/**
 * Hook for tracing API calls
 */
export const useApiTracing = () => {
  const traceApiCall = useCallback((method, url, requestData = null, options = {}) => {
    return traceOperation(
      `api.${method.toUpperCase()}`,
      async (span) => {
        try {
          // Add API-specific attributes
          span.setAttributes({
            'http.method': method.toUpperCase(),
            'http.url': url,
            'http.request.size': requestData ? JSON.stringify(requestData).length : 0,
            'api.operation': options.operation || 'unknown',
            'api.version': options.version || 'v1'
          });
          // Make the actual API call
          const response = await fetch(url, {
            method: method.toUpperCase(),
            headers: {
              'Content-Type': 'application/json',
              ...tracingService.injectHeaders(),
              ...options.headers
            },
            body: requestData ? JSON.stringify(requestData) : undefined,
            ...options
          });
          // Add response attributes
          span.setAttributes({
            'http.status_code': response.status,
            'http.response.size': parseInt(response.headers.get('content-length') || '0'),
            'api.response.correlation_id': response.headers.get('x-correlation-id')
          });
          // Parse response
          const responseData = await response.json();
          if (!response.ok) {
            span.setAttributes({
              'error.type': 'http_error',
              'error.message': responseData.message || 'HTTP Error'
            });
            throw new Error(`HTTP ${response.status}: ${responseData.message || 'Unknown error'}`);
          }
          span.setAttributes({
            'api.response.success': true
          });
          return responseData;
        } catch (error) {
          span.setAttributes({
            'api.response.success': false,
            'error.type': error.constructor.name,
            'error.message': error.message
          });
          throw error;
        }
      },
      'CLIENT',
      {
        'operation.type': 'api_call'
      }
    );
  }, []);
  return { traceApiCall };
};
/**
 * Hook for tracing form submissions
 */
export const useFormTracing = (formName) => {
  const traceFormSubmit = useCallback((formData, validationErrors = {}) => {
    return traceOperation(
      `form.${formName}.submit`,
      (span) => {
        span.setAttributes({
          'form.name': formName,
          'form.field_count': Object.keys(formData).length,
          'form.has_errors': Object.keys(validationErrors).length > 0,
          'form.error_count': Object.keys(validationErrors).length
        });
        // Add field information (excluding sensitive data)
        Object.keys(formData).forEach((field) => {
          if (!['password', 'token', 'secret', 'key'].includes(field.toLowerCase())) {
            const value = formData[field];
            span.setAttributes({
              [`form.field.${field}.type`]: typeof value,
              [`form.field.${field}.length`]: value ? value.toString().length : 0,
              [`form.field.${field}.has_value`]: !!value
            });
          }
        });
        // Add validation errors
        if (Object.keys(validationErrors).length > 0) {
          span.setAttributes({
            'form.validation_errors': JSON.stringify(validationErrors)
          });
        }
      },
      'INTERNAL',
      {
        'operation.type': 'form_submit'
      }
    );
  }, [formName]);
  const traceFormValidation = useCallback((fieldName, isValid, errorMessage = null) => {
    return traceOperation(
      `form.${formName}.validate.${fieldName}`,
      (span) => {
        span.setAttributes({
          'form.name': formName,
          'form.field.name': fieldName,
          'form.field.valid': isValid,
          'form.field.error': errorMessage || ''
        });
      },
      'INTERNAL',
      {
        'operation.type': 'form_validation'
      }
    );
  }, [formName]);
  return { traceFormSubmit, traceFormValidation };
};
/**
 * Hook for tracing performance metrics
 */
export const usePerformanceTracing = (componentName) => {
  const performanceObserver = useRef(null);
  useEffect(() => {
    if ('PerformanceObserver' in window) {
      performanceObserver.current = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          traceOperation(
            `performance.${entry.entryType}`,
            (span) => {
              span.setAttributes({
                'performance.name': entry.name,
                'performance.type': entry.entryType,
                'performance.start_time': entry.startTime,
                'performance.duration': entry.duration,
                'component.name': componentName
              });
              // Add specific attributes based on entry type
              if (entry.entryType === 'measure') {
                span.setAttributes({
                  'performance.measure.detail': entry.detail || ''
                });
              } else if (entry.entryType === 'navigation') {
                span.setAttributes({
                  'performance.navigation.type': entry.type,
                  'performance.navigation.redirect_count': entry.redirectCount
                });
              }
            },
            'INTERNAL',
            { 'operation.type': 'performance_metric' }
          );
        });
      });
      performanceObserver.current.observe({
        entryTypes: ['measure', 'navigation', 'paint']
      });
    }
    return () => {
      if (performanceObserver.current) {
        performanceObserver.current.disconnect();
      }
    };
  }, [componentName]);
  const markPerformance = useCallback((markName) => {
    if ('performance' in window && 'mark' in performance) {
      performance.mark(`${componentName}.${markName}`);
    }
  }, [componentName]);
  const measurePerformance = useCallback((measureName, startMark, endMark) => {
    if ('performance' in window && 'measure' in performance) {
      try {
        performance.measure(
          `${componentName}.${measureName}`,
          startMark ? `${componentName}.${startMark}` : undefined,
          endMark ? `${componentName}.${endMark}` : undefined
        );
      } catch (error) {
        console.warn('Performance measurement failed:', error);
      }
    }
  }, [componentName]);
  return { markPerformance, measurePerformance };
};
/**
 * Hook for tracing errors and exceptions
 */
export const useErrorTracing = (componentName) => {
  const traceComponentError = useCallback((error, errorInfo = {}) => {
    traceError(error, {
      component: componentName,
      error_boundary: true,
      ...errorInfo
    });
  }, [componentName]);
  const traceAsyncError = useCallback((error, operation = 'unknown') => {
    traceError(error, {
      component: componentName,
      operation,
      async: true
    });
  }, [componentName]);
  return { traceComponentError, traceAsyncError };
};