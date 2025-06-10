// TODO: i18n - processed
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw } from 'lucide-react';import { useTranslation } from "react-i18next";
class ErrorBoundaryWithLogging extends React.Component {
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
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    // Log error details to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    // Store error details in localStorage for debugging
    const errorLog = {
      timestamp: new Date().toISOString(),
      message: error.toString(),
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      url: window.location.href,
      userAgent: navigator.userAgent
    };
    // Get existing errors from localStorage
    const existingErrors = JSON.parse(localStorage.getItem('bdc_error_log') || '[]');
    existingErrors.push(errorLog);
    // Keep only last 10 errors
    if (existingErrors.length > 10) {
      existingErrors.shift();
    }
    localStorage.setItem('bdc_error_log', JSON.stringify(existingErrors));
    // Update state
    this.setState((prevState) => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));
  }
  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
    // Optionally reload the page
    if (this.state.errorCount > 2) {
      window.location.reload();
    }
  };
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <Card className="max-w-2xl w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertCircle className="h-6 w-6" />
                Something went wrong
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">
                An error occurred while rendering this component. The error has been logged for debugging.
              </p>
              {process.env.NODE_ENV === 'development' &&
              <div className="space-y-2">
                  <details className="bg-gray-100 p-4 rounded-md">
                    <summary className="cursor-pointer font-medium text-sm">
                      Error Details (Development Only)
                    </summary>
                    <div className="mt-2 space-y-2">
                      <div>
                        <p className="text-xs font-mono text-red-600">
                          {this.state.error && this.state.error.toString()}
                        </p>
                      </div>
                      {this.state.errorInfo &&
                    <div>
                          <p className="text-xs text-gray-500 font-medium mb-1">Component Stack:</p>
                          <pre className="text-xs font-mono text-gray-600 overflow-auto max-h-40">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </div>
                    }
                    </div>
                  </details>
                  <div className="text-xs text-gray-500">
                    Error #{this.state.errorCount} • Check console for full details
                  </div>
                </div>
              }
              <div className="flex gap-2">
                <Button
                  onClick={this.handleReset}
                  variant="primary"
                  className="flex items-center gap-2">

                  <RefreshCw className="h-4 w-4" />
                  Try Again
                </Button>
                <Button
                  onClick={() => window.history.back()}
                  variant="outline">

                  Go Back
                </Button>
                <Button
                  onClick={() => window.location.href = '/'}
                  variant="outline">

                  Go to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>);

    }
    return this.props.children;
  }
}
export default ErrorBoundaryWithLogging;