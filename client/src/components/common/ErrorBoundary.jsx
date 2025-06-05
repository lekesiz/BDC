import React, { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
/**
 * Enhanced Error Boundary component that catches JavaScript errors in child components
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }
  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    // Update state with error details
    this.setState({
      error,
      errorInfo,
      errorCount: this.state.errorCount + 1
    });
    // Report to error tracking service (e.g., Sentry)
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }
  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };
  render() {
    const { hasError, error, errorInfo, errorCount } = this.state;
    const { 
      children, 
      fallback, 
      showDetails = process.env.NODE_ENV === 'development',
      resetButtonText = "Try Again",
      errorTitle = "Something went wrong",
      errorMessage = "An unexpected error occurred. Please try refreshing the page."
    } = this.props;
    if (hasError) {
      // Custom fallback component
      if (fallback) {
        return fallback(error, errorInfo, this.handleReset);
      }
      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="mt-4 text-xl font-semibold text-gray-900 text-center">
                {errorTitle}
              </h2>
              <p className="mt-2 text-sm text-gray-600 text-center">
                {errorMessage}
              </p>
              {errorCount > 1 && (
                <p className="mt-2 text-xs text-gray-500 text-center">
                  This error has occurred {errorCount} times
                </p>
              )}
              {showDetails && error && (
                <details className="mt-4">
                  <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                    Error Details
                  </summary>
                  <div className="mt-2 p-3 bg-gray-50 rounded text-xs text-gray-700 font-mono overflow-auto">
                    <p className="font-semibold">{error.toString()}</p>
                    {errorInfo && (
                      <pre className="mt-2 whitespace-pre-wrap">
                        {errorInfo.componentStack}
                      </pre>
                    )}
                  </div>
                </details>
              )}
              <div className="mt-6 flex gap-3">
                <Button
                  onClick={this.handleReset}
                  className="flex-1"
                  variant="primary"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {resetButtonText}
                </Button>
                <Button
                  onClick={() => window.location.href = '/'}
                  className="flex-1"
                  variant="outline"
                >
                  Go to Home
                </Button>
              </div>
            </div>
          </div>
        </div>
      );
    }
    return children;
  }
}
/**
 * HOC to wrap any component with error boundary
 */
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  return (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );
};
/**
 * Hook for error handling in functional components
 */
export const useErrorHandler = () => {
  const [error, setError] = React.useState(null);
  const resetError = () => setError(null);
  const captureError = React.useCallback((error) => {
    setError(error);
    console.error('Error captured:', error);
  }, []);
  // Throw error to be caught by nearest error boundary
  if (error) {
    throw error;
  }
  return { captureError, resetError };
};
/**
 * Generic error display component
 */
export const ErrorDisplay = ({ 
  error, 
  onRetry, 
  title = "Error", 
  showDetails = process.env.NODE_ENV === 'development' 
}) => {
  return (
    <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{error?.message || "An unexpected error occurred"}</p>
          </div>
          {showDetails && error?.stack && (
            <details className="mt-2">
              <summary className="cursor-pointer text-xs text-red-600">
                Show error details
              </summary>
              <pre className="mt-1 text-xs text-red-600 overflow-auto p-2 bg-red-100 rounded">
                {error.stack}
              </pre>
            </details>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
export default ErrorBoundary;