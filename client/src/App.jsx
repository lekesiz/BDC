/**
 * Clean, consolidated App component
 * Eliminates 900+ lines and 170+ imports
 * Uses centralized route configuration
 * Includes i18n (internationalization) support
 */
import React, { Suspense, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import { ToastProvider } from './components/ui/toast';
import { SocketProvider } from './contexts/SocketContext';
import { ThemeProvider } from './contexts/ThemeContext';
import GlobalErrorHandler from './components/common/GlobalErrorHandler';
import ErrorBoundary from './components/common/ErrorBoundary';
import NotificationProviderV2 from './providers/NotificationProviderV2';
import SimpleRouteRenderer from './components/routing/SimpleRouteRenderer';
import LoadingSpinner from './components/ui/LoadingSpinner';
import { useTranslation } from 'react-i18next';
import { LanguageProvider, RTLProvider } from './i18n';

/**
 * Inner App component that uses auth context
 */
function AppContent() {
  const { t, i18n } = useTranslation();
  const { isLoading } = useAuth();
  
  // Handle language direction changes
  useEffect(() => {
    const currentLang = i18n.language;
    const isRTL = ['ar', 'he', 'fa'].includes(currentLang);
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLang;
  }, [i18n.language]);
  
  // Show app-level loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text={t('common.loading_application', 'Loading application...')} />
      </div>
    );
  }
  
  return (
    <RTLProvider>
      <SimpleRouteRenderer />
    </RTLProvider>
  );

}
/**
 * Main App component with centralized providers and routing
 * Includes i18n provider wrapping for full internationalization support
 */
function App() {
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <ThemeProvider>
          <ToastProvider>
            <GlobalErrorHandler />
            <NotificationProviderV2>
              <SocketProvider>
                <Suspense fallback={
                  <div className="flex items-center justify-center min-h-screen">
                    <LoadingSpinner size="lg" text="Loading..." />
                  </div>
                }>
                  <AppContent />
                </Suspense>
              </SocketProvider>
            </NotificationProviderV2>
          </ToastProvider>
        </ThemeProvider>
      </LanguageProvider>
    </ErrorBoundary>
  );
}

// Export App with displayName for better debugging
App.displayName = 'BDC_App';

export default App;