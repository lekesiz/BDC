// TODO: i18n - processed
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { WifiOff, Wifi, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';

/**
 * OfflineCapable - Component wrapper that provides offline functionality
 * Features offline detection, cached content, and sync queue management
 */import { useTranslation } from "react-i18next";
export const OfflineCapable = ({
  children,
  fallbackComponent,
  offlineMessage = 'You are currently offline',
  showOfflineIndicator = true,
  enableOfflineActions = true,
  syncOnReconnect = true,
  cacheStrategy = 'network-first',
  className,
  ...props
}) => {const { t } = useTranslation();
  const {
    networkStatus,
    hapticFeedback: triggerHaptic,
    isMobile
  } = useMobile();

  const [offlineData, setOfflineData] = useState(null);
  const [syncQueue, setSyncQueue] = useState([]);
  const [lastSyncTime, setLastSyncTime] = useState(null);
  const [syncStatus, setSyncStatus] = useState('idle'); // idle, syncing, success, error
  const syncTimeoutRef = useRef(null);

  // Check if we have cached data
  const hasCachedData = offlineData !== null;
  const isOnline = networkStatus.isOnline;

  // Load cached data from localStorage on mount
  useEffect(() => {
    const loadCachedData = async () => {
      try {
        const cached = localStorage.getItem('offline-cache');
        if (cached) {
          setOfflineData(JSON.parse(cached));
        }
      } catch (error) {
        console.warn('Failed to load cached data:', error);
      }
    };

    loadCachedData();
  }, []);

  // Load sync queue from localStorage
  useEffect(() => {
    const loadSyncQueue = async () => {
      try {
        const queue = localStorage.getItem('sync-queue');
        if (queue) {
          setSyncQueue(JSON.parse(queue));
        }
      } catch (error) {
        console.warn('Failed to load sync queue:', error);
      }
    };

    loadSyncQueue();
  }, []);

  // Save sync queue to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('sync-queue', JSON.stringify(syncQueue));
    } catch (error) {
      console.warn('Failed to save sync queue:', error);
    }
  }, [syncQueue]);

  // Sync when coming back online
  useEffect(() => {
    if (isOnline && syncOnReconnect && syncQueue.length > 0) {
      syncOfflineActions();
    }
  }, [isOnline, syncOnReconnect, syncQueue.length]);

  // Cache data for offline use
  const cacheData = useCallback(async (data, key = 'default') => {
    try {
      const cacheEntry = {
        data,
        timestamp: Date.now(),
        key
      };

      localStorage.setItem(`offline-cache-${key}`, JSON.stringify(cacheEntry));
      setOfflineData(data);
    } catch (error) {
      console.warn('Failed to cache data:', error);
    }
  }, []);

  // Add action to sync queue
  const queueOfflineAction = useCallback((action) => {
    const queueItem = {
      id: Date.now() + Math.random(),
      action,
      timestamp: Date.now(),
      retries: 0
    };

    setSyncQueue((prev) => [...prev, queueItem]);

    if (isMobile) {
      triggerHaptic('light');
    }

    return queueItem.id;
  }, [isMobile, triggerHaptic]);

  // Remove action from sync queue
  const removeFromSyncQueue = useCallback((id) => {
    setSyncQueue((prev) => prev.filter((item) => item.id !== id));
  }, []);

  // Sync offline actions
  const syncOfflineActions = useCallback(async () => {
    if (!isOnline || syncQueue.length === 0) return;

    setSyncStatus('syncing');

    const results = [];
    const failedActions = [];

    for (const queueItem of syncQueue) {
      try {
        // Execute the action
        if (typeof queueItem.action === 'function') {
          await queueItem.action();
        } else if (queueItem.action.type === 'api-call') {
          // Handle API calls
          const response = await fetch(queueItem.action.url, {
            method: queueItem.action.method || 'POST',
            headers: queueItem.action.headers || { 'Content-Type': 'application/json' },
            body: queueItem.action.body ? JSON.stringify(queueItem.action.body) : undefined
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
        }

        results.push({ id: queueItem.id, status: 'success' });
      } catch (error) {
        console.warn('Failed to sync action:', error);

        // Retry logic
        if (queueItem.retries < 3) {
          failedActions.push({
            ...queueItem,
            retries: queueItem.retries + 1
          });
        }

        results.push({ id: queueItem.id, status: 'failed', error });
      }
    }

    // Update sync queue with failed actions
    setSyncQueue(failedActions);
    setLastSyncTime(Date.now());

    // Set sync status
    const hasFailures = results.some((r) => r.status === 'failed');
    setSyncStatus(hasFailures ? 'error' : 'success');

    // Reset status after delay
    clearTimeout(syncTimeoutRef.current);
    syncTimeoutRef.current = setTimeout(() => {
      setSyncStatus('idle');
    }, 3000);

    if (isMobile) {
      triggerHaptic(hasFailures ? 'error' : 'success');
    }

    return results;
  }, [isOnline, syncQueue, isMobile, triggerHaptic]);

  // Manual retry sync
  const retrySyncQueue = useCallback(() => {
    if (isOnline) {
      syncOfflineActions();
    }
  }, [isOnline, syncOfflineActions]);

  // Clear cache
  const clearOfflineCache = useCallback(() => {
    try {
      const keys = Object.keys(localStorage).filter((key) => key.startsWith('offline-cache'));
      keys.forEach((key) => localStorage.removeItem(key));
      setOfflineData(null);
    } catch (error) {
      console.warn('Failed to clear cache:', error);
    }
  }, []);

  // Provide offline context
  const offlineContext = {
    isOnline,
    networkStatus,
    hasCachedData,
    offlineData,
    syncQueue,
    syncStatus,
    lastSyncTime,
    cacheData,
    queueOfflineAction,
    removeFromSyncQueue,
    syncOfflineActions,
    retrySyncQueue,
    clearOfflineCache
  };

  return (
    <div className={cn('relative', className)} {...props}>
      {/* Offline Indicator */}
      {showOfflineIndicator &&
      <OfflineIndicator
        isOnline={isOnline}
        syncQueue={syncQueue}
        syncStatus={syncStatus}
        onRetrySync={retrySyncQueue} />

      }

      {/* Content */}
      {isOnline || hasCachedData ?
      <OfflineProvider value={offlineContext}>
          {children}
        </OfflineProvider> :
      fallbackComponent ?
      fallbackComponent :

      <OfflineFallback message={offlineMessage} />
      }
    </div>);

};

/**
 * OfflineIndicator - Shows connection status and sync queue
 */
const OfflineIndicator = ({
  isOnline,
  syncQueue,
  syncStatus,
  onRetrySync
}) => {const { t } = useTranslation();
  const { isMobile, hapticFeedback: triggerHaptic } = useMobile();
  const [isExpanded, setIsExpanded] = useState(false);

  if (isOnline && syncQueue.length === 0) return null;

  const handleRetry = () => {
    if (isMobile) {
      triggerHaptic('light');
    }
    onRetrySync();
  };

  return (
    <div className={cn(
      'fixed top-4 left-4 right-4 z-50',
      'bg-background border border-border rounded-lg shadow-lg',
      'transition-all duration-300'
    )}>
      <div
        className="flex items-center justify-between p-3 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}>

        <div className="flex items-center gap-2">
          {isOnline ?
          <Wifi className="h-4 w-4 text-green-500" /> :

          <WifiOff className="h-4 w-4 text-red-500" />
          }
          
          <span className="text-sm font-medium">
            {isOnline ? 'Online' : 'Offline'}
          </span>

          {syncQueue.length > 0 &&
          <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
              {syncQueue.length} pending
            </span>
          }
        </div>

        <div className="flex items-center gap-2">
          {syncStatus === 'syncing' &&
          <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
          }
          {syncStatus === 'success' &&
          <CheckCircle className="h-4 w-4 text-green-500" />
          }
          {syncStatus === 'error' &&
          <AlertCircle className="h-4 w-4 text-red-500" />
          }
        </div>
      </div>

      {isExpanded &&
      <div className="border-t p-3 space-y-2">
          {syncQueue.length > 0 &&
        <div>
              <p className="text-sm text-muted-foreground mb-2">
                {syncQueue.length}{t("mobile.actions_will_sync_when_online")}
          </p>
              
              {isOnline &&
          <TouchOptimizedButton
            size="sm"
            onClick={handleRetry}
            disabled={syncStatus === 'syncing'}
            className="w-full">

                  {syncStatus === 'syncing' ? 'Syncing...' : 'Retry Sync'}
                </TouchOptimizedButton>
          }
            </div>
        }
        </div>
      }
    </div>);

};

/**
 * OfflineFallback - Default offline fallback component
 */
const OfflineFallback = ({ message }) =>
<div className="flex flex-col items-center justify-center p-8 text-center">
    <WifiOff className="h-12 w-12 text-muted-foreground mb-4" />
    <h3 className="text-lg font-semibold mb-2">{t("mobile.no_internet_connection")}</h3>
    <p className="text-muted-foreground mb-4">{message}</p>
    <p className="text-sm text-muted-foreground">{t("mobile.please_check_your_connection_and_try_again")}

  </p>
  </div>;


/**
 * OfflineProvider - Context provider for offline functionality
 */
const OfflineContext = React.createContext({});

const OfflineProvider = ({ children, value }) =>
<OfflineContext.Provider value={value}>
    {children}
  </OfflineContext.Provider>;


/**
 * useOffline - Hook to access offline context
 */
export const useOffline = () => {
  const context = React.useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline must be used within an OfflineCapable component');
  }
  return context;
};

/**
 * withOfflineCapability - HOC to add offline capability to components
 */
export const withOfflineCapability = (Component, options = {}) => {
  return function OfflineCapableComponent(props) {
    return (
      <OfflineCapable {...options}>
        <Component {...props} />
      </OfflineCapable>);

  };
};

export default OfflineCapable;