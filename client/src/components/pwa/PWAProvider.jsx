import React, { createContext, useContext, useEffect, useState } from 'react';
import { pwaService } from '../../services/pwa.service';
import { InstallPrompt, FloatingInstallButton } from './InstallPrompt';
import { UpdateNotification, UpdateBanner } from './UpdateNotification';
import { OfflineBanner } from './OfflineIndicator';
import { NotificationPermissionPrompt } from './NotificationManager';
/**
 * PWA Context for providing PWA state and methods throughout the app
 */
const PWAContext = createContext({
  isOnline: true,
  canInstall: false,
  isInstalled: false,
  hasUpdate: false,
  isLoading: false,
  error: null,
  install: () => {},
  update: () => {},
  clearError: () => {}
});
export const usePWAContext = () => {
  const context = useContext(PWAContext);
  if (!context) {
    throw new Error('usePWAContext must be used within PWAProvider');
  }
  return context;
};
/**
 * PWA Provider Component
 * Provides PWA functionality and UI components throughout the app
 */
export function PWAProvider({ 
  children, 
  showInstallPrompt = true,
  showUpdateNotifications = true,
  showOfflineIndicators = true,
  showNotificationPrompts = true,
  installPromptDelay = 5000, // 5 seconds
  config = {}
}) {
  const [state, setState] = useState({
    isOnline: navigator.onLine,
    canInstall: false,
    isInstalled: false,
    hasUpdate: false,
    isLoading: false,
    error: null,
    notifications: {
      permission: 'default',
      subscription: null
    }
  });
  const [ui, setUI] = useState({
    showInstallPrompt: false,
    showInstallFloat: false,
    showUpdateBanner: false,
    showNotificationPrompt: false,
    installPromptDismissed: false,
    updateNotificationDismissed: false
  });
  useEffect(() => {
    // Initialize PWA service
    pwaService.init();
    // Setup event listeners
    const handleOnline = () => {
      setState(prev => ({ ...prev, isOnline: true }));
    };
    const handleOffline = () => {
      setState(prev => ({ ...prev, isOnline: false }));
    };
    const handleInstallAvailable = () => {
      setState(prev => ({ ...prev, canInstall: true }));
      if (showInstallPrompt && !ui.installPromptDismissed) {
        // Show install prompt after delay
        setTimeout(() => {
          setUI(prev => ({ ...prev, showInstallPrompt: true }));
        }, installPromptDelay);
        // Show floating button immediately
        setUI(prev => ({ ...prev, showInstallFloat: true }));
      }
    };
    const handleAppInstalled = () => {
      setState(prev => ({ ...prev, canInstall: false, isInstalled: true }));
      setUI(prev => ({ 
        ...prev, 
        showInstallPrompt: false, 
        showInstallFloat: false 
      }));
    };
    const handleUpdateAvailable = () => {
      setState(prev => ({ ...prev, hasUpdate: true }));
      if (showUpdateNotifications && !ui.updateNotificationDismissed) {
        setUI(prev => ({ ...prev, showUpdateBanner: true }));
      }
    };
    const handleError = (error) => {
      setState(prev => ({ ...prev, error: error.message }));
    };
    // Register event listeners
    pwaService.on('online', handleOnline);
    pwaService.on('offline', handleOffline);
    pwaService.on('installAvailable', handleInstallAvailable);
    pwaService.on('appInstalled', handleAppInstalled);
    pwaService.on('updateAvailable', handleUpdateAvailable);
    pwaService.on('error', handleError);
    // Check initial state
    setState(prev => ({
      ...prev,
      canInstall: pwaService.canInstall(),
      isInstalled: pwaService.isInstalled(),
      hasUpdate: pwaService.hasUpdate()
    }));
    // Show notification prompt after delay if enabled
    if (showNotificationPrompts) {
      setTimeout(() => {
        if (Notification.permission === 'default') {
          setUI(prev => ({ ...prev, showNotificationPrompt: true }));
        }
      }, installPromptDelay + 3000); // 3 seconds after install prompt
    }
    return () => {
      pwaService.off('online', handleOnline);
      pwaService.off('offline', handleOffline);
      pwaService.off('installAvailable', handleInstallAvailable);
      pwaService.off('appInstalled', handleAppInstalled);
      pwaService.off('updateAvailable', handleUpdateAvailable);
      pwaService.off('error', handleError);
    };
  }, [showInstallPrompt, showUpdateNotifications, showNotificationPrompts, installPromptDelay, ui.installPromptDismissed, ui.updateNotificationDismissed]);
  const install = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      await pwaService.promptInstall();
    } catch (error) {
      setState(prev => ({ ...prev, error: error.message }));
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };
  const update = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      await pwaService.applyUpdate();
    } catch (error) {
      setState(prev => ({ ...prev, error: error.message }));
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };
  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };
  const handleInstallPromptDismiss = () => {
    setUI(prev => ({ 
      ...prev, 
      showInstallPrompt: false, 
      installPromptDismissed: true 
    }));
    // Remember dismissal for this session
    sessionStorage.setItem('pwa-install-dismissed', 'true');
  };
  const handleUpdateNotificationDismiss = () => {
    setUI(prev => ({ 
      ...prev, 
      showUpdateBanner: false, 
      updateNotificationDismissed: true 
    }));
  };
  const handleNotificationPromptDismiss = () => {
    setUI(prev => ({ ...prev, showNotificationPrompt: false }));
  };
  const contextValue = {
    ...state,
    install,
    update,
    clearError
  };
  return (
    <PWAContext.Provider value={contextValue}>
      {/* Offline banner */}
      {showOfflineIndicators && !state.isOnline && (
        <OfflineBanner className="fixed top-0 left-0 right-0 z-50" />
      )}
      {/* Update banner */}
      {ui.showUpdateBanner && (
        <UpdateBanner 
          onDismiss={handleUpdateNotificationDismiss}
          className="fixed top-0 left-0 right-0 z-50"
        />
      )}
      {/* Main content */}
      <div className={!state.isOnline || ui.showUpdateBanner ? 'mt-12' : ''}>
        {children}
      </div>
      {/* Install prompt */}
      {ui.showInstallPrompt && (
        <div className="fixed top-4 right-4 z-50 max-w-sm">
          <InstallPrompt onDismiss={handleInstallPromptDismiss} />
        </div>
      )}
      {/* Floating install button */}
      {ui.showInstallFloat && !ui.showInstallPrompt && (
        <FloatingInstallButton />
      )}
      {/* Notification permission prompt */}
      {ui.showNotificationPrompt && (
        <div className="fixed bottom-4 left-4 z-50 max-w-sm">
          <NotificationPermissionPrompt onDismiss={handleNotificationPromptDismiss} />
        </div>
      )}
    </PWAContext.Provider>
  );
}
/**
 * PWA Status Component
 * Shows comprehensive PWA status information
 */
export function PWAStatus({ className = '' }) {
  const { isOnline, canInstall, isInstalled, hasUpdate, isLoading } = usePWAContext();
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="text-sm font-medium">PWA Status</div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className={`p-2 rounded ${isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          Connection: {isOnline ? 'Online' : 'Offline'}
        </div>
        <div className={`p-2 rounded ${isInstalled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
          Install: {isInstalled ? 'Installed' : 'Not Installed'}
        </div>
        {canInstall && (
          <div className="p-2 rounded bg-blue-100 text-blue-800">
            Install: Available
          </div>
        )}
        {hasUpdate && (
          <div className="p-2 rounded bg-orange-100 text-orange-800">
            Update: Available
          </div>
        )}
        {isLoading && (
          <div className="p-2 rounded bg-yellow-100 text-yellow-800">
            Status: Loading...
          </div>
        )}
      </div>
    </div>
  );
}
/**
 * PWA Controls Component
 * Manual controls for PWA features
 */
export function PWAControls({ className = '' }) {
  const { canInstall, hasUpdate, isLoading, install, update } = usePWAContext();
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="text-sm font-medium">PWA Controls</div>
      <div className="flex flex-wrap gap-2">
        {canInstall && (
          <button
            onClick={install}
            disabled={isLoading}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Installing...' : 'Install App'}
          </button>
        )}
        {hasUpdate && (
          <button
            onClick={update}
            disabled={isLoading}
            className="px-3 py-1 text-xs bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50"
          >
            {isLoading ? 'Updating...' : 'Update App'}
          </button>
        )}
        <button
          onClick={() => window.location.reload()}
          className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Reload
        </button>
      </div>
    </div>
  );
}
export default PWAProvider;