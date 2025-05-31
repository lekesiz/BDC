/**
 * Clean, consolidated App component
 * Eliminates 900+ lines and 170+ imports
 * Uses centralized route configuration
 */

import React from 'react';
import { useAuth } from './hooks/useAuth';
import { ToastProvider } from './components/ui/toast';
import { SocketProvider } from './contexts/SocketContext';
import { ThemeProvider } from './contexts/ThemeContext';
import GlobalErrorHandler from './components/common/GlobalErrorHandler';
import ErrorBoundary from './components/common/ErrorBoundary';
import NotificationProviderV2 from './providers/NotificationProviderV2';
import SimpleRouteRenderer from './components/routing/SimpleRouteRenderer';
import LoadingSpinner from './components/ui/LoadingSpinner';

/**
 * Main App component with centralized providers and routing
 */
function App() {
  const { isLoading } = useAuth();

  // Show app-level loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading application..." />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <GlobalErrorHandler />
          <NotificationProviderV2>
            <SocketProvider>
              <SimpleRouteRenderer />
            </SocketProvider>
          </NotificationProviderV2>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;