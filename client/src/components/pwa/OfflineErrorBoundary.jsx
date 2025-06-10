// TODO: i18n - processed
import React, { Component } from 'react';
import { AlertTriangle, RefreshCw, WifiOff, Home, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';

/**
 * Offline-aware Error Boundary Component
 * Handles errors with different strategies based on online/offline status
 */import { useTranslation } from "react-i18next";
class OfflineErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      isOnline: navigator.onLine,
      retryCount: 0,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log error to service for online analysis
    this.logError(error, errorInfo);
  }

  componentDidMount() {
    // Listen for online/offline changes
    window.addEventListener('online', this.handleOnlineChange);
    window.addEventListener('offline', this.handleOfflineChange);
  }

  componentWillUnmount() {
    window.removeEventListener('online', this.handleOnlineChange);
    window.removeEventListener('offline', this.handleOfflineChange);
  }

  handleOnlineChange = () => {
    this.setState({ isOnline: true });

    // Auto-retry if we were offline
    if (this.state.hasError && this.state.retryCount < 3) {
      setTimeout(() => {
        this.handleRetry();
      }, 1000);
    }
  };

  handleOfflineChange = () => {
    this.setState({ isOnline: false });
  };

  logError = async (error, errorInfo) => {
    try {
      const errorData = {
        id: this.state.errorId,
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        isOnline: navigator.onLine
      };

      if (navigator.onLine) {
        // Send to error reporting service
        await fetch('/api/errors', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(errorData)
        });
      } else {
        // Store offline for later sync
        await this.storeOfflineError(errorData);
      }
    } catch (logError) {
      console.error('Failed to log error:', logError);
    }
  };

  storeOfflineError = async (errorData) => {
    try {
      // Store in IndexedDB for later sync
      const request = indexedDB.open('BDC_ErrorStore', 1);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('errors')) {
          db.createObjectStore('errors', { keyPath: 'id' });
        }
      };

      request.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction(['errors'], 'readwrite');
        const store = transaction.objectStore('errors');
        store.add(errorData);
      };
    } catch (error) {
      console.error('Failed to store offline error:', error);
    }
  };

  handleRetry = () => {
    this.setState((prevState) => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleGoBack = () => {
    window.history.back();
  };

  handleReload = () => {
    window.location.reload();
  };

  getErrorCategory = (error) => {
    if (!error) return 'unknown';

    const message = error.message.toLowerCase();

    if (message.includes('network') || message.includes('fetch')) {
      return 'network';
    }
    if (message.includes('chunk') || message.includes('loading')) {
      return 'loading';
    }
    if (message.includes('permission') || message.includes('denied')) {
      return 'permission';
    }
    if (message.includes('quota') || message.includes('storage')) {
      return 'storage';
    }

    return 'application';
  };

  getErrorSolution = (category, isOnline) => {
    const solutions = {
      network: {
        title: isOnline ? 'Network Error' : 'You\'re Offline',
        description: isOnline ?
        'There was a problem connecting to our servers. This might be a temporary issue.' :
        'Some features may not work while you\'re offline. We\'ll sync your data when you\'re back online.',
        actions: isOnline ?
        ['retry', 'reload'] :
        ['retry', 'offline']
      },
      loading: {
        title: 'Loading Error',
        description: 'Failed to load some application resources. This might be due to a poor connection or server issue.',
        actions: ['retry', 'reload', 'home']
      },
      permission: {
        title: 'Permission Error',
        description: 'The application doesn\'t have the necessary permissions to complete this action.',
        actions: ['reload', 'home']
      },
      storage: {
        title: 'Storage Error',
        description: 'There\'s not enough storage space available. Try clearing some cached data.',
        actions: ['clear', 'reload']
      },
      application: {
        title: 'Application Error',
        description: 'Something went wrong in the application. This is likely a temporary issue.',
        actions: ['retry', 'reload', 'home']
      },
      unknown: {
        title: 'Unexpected Error',
        description: 'An unexpected error occurred. Please try again.',
        actions: ['retry', 'reload', 'home']
      }
    };

    return solutions[category] || solutions.unknown;
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const errorCategory = this.getErrorCategory(this.state.error);
    const solution = this.getErrorSolution(errorCategory, this.state.isOnline);
    const canRetry = this.state.retryCount < 3;

    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-900">
        <Card className="w-full max-w-lg">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-full w-fit">
              {!this.state.isOnline ?
              <WifiOff className="h-8 w-8 text-red-600 dark:text-red-400" /> :

              <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-400" />
              }
            </div>
            <CardTitle className="text-xl">{solution.title}</CardTitle>
            <CardDescription className="text-base">
              {solution.description}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Offline Alert */}
            {!this.state.isOnline &&
            <Alert>
                <WifiOff className="h-4 w-4" />
                <AlertDescription>
                  You're currently offline. Some features may not work properly until you reconnect.
                </AlertDescription>
              </Alert>
            }

            {/* Action Buttons */}
            <div className="flex flex-col gap-2">
              {solution.actions.includes('retry') && canRetry &&
              <Button
                onClick={this.handleRetry}
                className="w-full">

                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again {this.state.retryCount > 0 && `(${this.state.retryCount}/3)`}
                </Button>
              }

              {solution.actions.includes('reload') &&
              <Button
                onClick={this.handleReload}
                variant="outline"
                className="w-full">

                  <RefreshCw className="mr-2 h-4 w-4" />
                  Reload Page
                </Button>
              }

              {solution.actions.includes('home') &&
              <Button
                onClick={this.handleGoHome}
                variant="outline"
                className="w-full">

                  <Home className="mr-2 h-4 w-4" />
                  Go to Home
                </Button>
              }

              <Button
                onClick={this.handleGoBack}
                variant="ghost"
                className="w-full">

                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back
              </Button>
            </div>

            {/* Error Details (Development) */}
            {process.env.NODE_ENV === 'development' && this.state.error &&
            <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-600 dark:text-gray-400">
                  Error Details (Development)
                </summary>
                <div className="mt-2 p-3 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono">
                  <div className="text-red-600 dark:text-red-400 mb-2">
                    {this.state.error.message}
                  </div>
                  <div className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {this.state.error.stack}
                  </div>
                </div>
              </details>
            }

            {/* Error ID for Support */}
            <div className="text-center">
              <p className="text-xs text-gray-500">
                Error ID: {this.state.errorId}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Share this ID with support if the problem persists.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>);

  }
}

/**
 * Functional wrapper for easier use in React functional components
 */
export function OfflineErrorBoundaryWrapper({ children, fallback, onError }) {const { t } = useTranslation();
  return (
    <OfflineErrorBoundary fallback={fallback} onError={onError}>
      {children}
    </OfflineErrorBoundary>);

}

/**
 * Higher-order component for adding offline error boundary
 */
export function withOfflineErrorBoundary(WrappedComponent, errorBoundaryProps = {}) {
  const WithOfflineErrorBoundaryComponent = (props) => {const { t } = useTranslation();
    return (
      <OfflineErrorBoundary {...errorBoundaryProps}>
        <WrappedComponent {...props} />
      </OfflineErrorBoundary>);

  };

  WithOfflineErrorBoundaryComponent.displayName =
  `withOfflineErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

  return WithOfflineErrorBoundaryComponent;
}

export default OfflineErrorBoundary;