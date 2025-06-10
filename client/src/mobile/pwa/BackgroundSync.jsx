// TODO: i18n - processed
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { RefreshCw, Upload, Download, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';

/**
 * BackgroundSync - Component for managing background synchronization
 * Features automatic sync, manual triggers, and progress tracking
 */import { useTranslation } from "react-i18next";
export const BackgroundSync = ({
  children,
  syncInterval = 30000, // 30 seconds
  autoSync = true,
  syncOnVisibilityChange = true,
  syncOnNetworkChange = true,
  maxRetries = 3,
  retryDelay = 5000,
  showSyncStatus = true,
  onSyncStart,
  onSyncComplete,
  onSyncError,
  syncProvider,
  className,
  ...props
}) => {const { t } = useTranslation();
  const {
    networkStatus,
    hapticFeedback: triggerHaptic,
    isMobile
  } = useMobile();

  const [syncState, setSyncState] = useState({
    isActive: false,
    lastSyncTime: null,
    pendingUploads: 0,
    pendingDownloads: 0,
    failedSyncs: 0,
    status: 'idle' // idle, syncing, success, error, paused
  });

  const [syncQueue, setSyncQueue] = useState([]);
  const syncIntervalRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const syncInProgressRef = useRef(false);

  // Initialize sync provider
  useEffect(() => {
    if (syncProvider && typeof syncProvider.initialize === 'function') {
      syncProvider.initialize();
    }
  }, [syncProvider]);

  // Set up automatic sync interval
  useEffect(() => {
    if (!autoSync || !networkStatus.isOnline) return;

    const startAutoSync = () => {
      syncIntervalRef.current = setInterval(() => {
        if (!syncInProgressRef.current && networkStatus.isOnline) {
          performSync();
        }
      }, syncInterval);
    };

    startAutoSync();

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [autoSync, syncInterval, networkStatus.isOnline]);

  // Sync on network status change
  useEffect(() => {
    if (syncOnNetworkChange && networkStatus.isOnline && syncQueue.length > 0) {
      performSync();
    }
  }, [networkStatus.isOnline, syncOnNetworkChange, syncQueue.length]);

  // Sync on visibility change
  useEffect(() => {
    if (!syncOnVisibilityChange) return;

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && networkStatus.isOnline) {
        performSync();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [syncOnVisibilityChange, networkStatus.isOnline]);

  // Add item to sync queue
  const addToSyncQueue = useCallback((item) => {
    const queueItem = {
      id: Date.now() + Math.random(),
      type: item.type || 'data',
      data: item.data,
      operation: item.operation || 'upload', // upload, download, bidirectional
      priority: item.priority || 'normal', // high, normal, low
      retries: 0,
      timestamp: Date.now(),
      ...item
    };

    setSyncQueue((prev) => {
      const newQueue = [...prev, queueItem];
      // Sort by priority and timestamp
      return newQueue.sort((a, b) => {
        const priorityOrder = { high: 3, normal: 2, low: 1 };
        if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        }
        return a.timestamp - b.timestamp;
      });
    });

    // Update pending counts
    setSyncState((prev) => ({
      ...prev,
      pendingUploads: prev.pendingUploads + (item.operation === 'upload' ? 1 : 0),
      pendingDownloads: prev.pendingDownloads + (item.operation === 'download' ? 1 : 0)
    }));

    return queueItem.id;
  }, []);

  // Remove item from sync queue
  const removeFromSyncQueue = useCallback((id) => {
    setSyncQueue((prev) => {
      const item = prev.find((item) => item.id === id);
      if (item) {
        setSyncState((current) => ({
          ...current,
          pendingUploads: current.pendingUploads - (item.operation === 'upload' ? 1 : 0),
          pendingDownloads: current.pendingDownloads - (item.operation === 'download' ? 1 : 0)
        }));
      }
      return prev.filter((item) => item.id !== id);
    });
  }, []);

  // Perform sync operation
  const performSync = useCallback(async (forceSync = false) => {
    if (syncInProgressRef.current && !forceSync) return;
    if (!networkStatus.isOnline && !forceSync) return;
    if (syncQueue.length === 0 && !forceSync) return;

    syncInProgressRef.current = true;
    setSyncState((prev) => ({ ...prev, isActive: true, status: 'syncing' }));
    onSyncStart?.();

    try {
      let processedItems = 0;
      let failedItems = 0;
      const failedQueue = [];

      // Process sync queue
      for (const item of syncQueue) {
        try {
          if (syncProvider && typeof syncProvider.syncItem === 'function') {
            await syncProvider.syncItem(item);
          } else {
            // Default sync logic
            await defaultSyncItem(item);
          }

          removeFromSyncQueue(item.id);
          processedItems++;
        } catch (error) {
          console.warn('Sync item failed:', error);
          failedItems++;

          // Retry logic
          if (item.retries < maxRetries) {
            failedQueue.push({
              ...item,
              retries: item.retries + 1
            });
          } else {
            removeFromSyncQueue(item.id);
          }
        }
      }

      // Update queue with failed items for retry
      if (failedQueue.length > 0) {
        setSyncQueue((prev) => [...prev.filter((item) => !failedQueue.find((f) => f.id === item.id)), ...failedQueue]);

        // Schedule retry
        retryTimeoutRef.current = setTimeout(() => {
          performSync(true);
        }, retryDelay);
      }

      // Update sync state
      setSyncState((prev) => ({
        ...prev,
        isActive: false,
        lastSyncTime: Date.now(),
        failedSyncs: failedItems,
        status: failedItems > 0 ? 'error' : 'success'
      }));

      onSyncComplete?.({ processed: processedItems, failed: failedItems });

      if (isMobile) {
        triggerHaptic(failedItems > 0 ? 'error' : 'success');
      }

    } catch (error) {
      console.error('Sync failed:', error);

      setSyncState((prev) => ({
        ...prev,
        isActive: false,
        status: 'error',
        failedSyncs: prev.failedSyncs + 1
      }));

      onSyncError?.(error);

      if (isMobile) {
        triggerHaptic('error');
      }
    } finally {
      syncInProgressRef.current = false;
    }
  }, [
  networkStatus.isOnline,
  syncQueue,
  syncProvider,
  maxRetries,
  retryDelay,
  onSyncStart,
  onSyncComplete,
  onSyncError,
  isMobile,
  triggerHaptic,
  removeFromSyncQueue]
  );

  // Default sync item implementation
  const defaultSyncItem = async (item) => {
    if (!item.endpoint) {
      throw new Error('No endpoint specified for sync item');
    }

    const response = await fetch(item.endpoint, {
      method: item.method || (item.operation === 'upload' ? 'POST' : 'GET'),
      headers: {
        'Content-Type': 'application/json',
        ...item.headers
      },
      body: item.operation === 'upload' ? JSON.stringify(item.data) : undefined
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  };

  // Manual sync trigger
  const triggerSync = useCallback(() => {
    performSync(true);
  }, [performSync]);

  // Pause/resume sync
  const pauseSync = useCallback(() => {
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
      syncIntervalRef.current = null;
    }
    setSyncState((prev) => ({ ...prev, status: 'paused' }));
  }, []);

  const resumeSync = useCallback(() => {
    if (autoSync && !syncIntervalRef.current) {
      syncIntervalRef.current = setInterval(() => {
        if (!syncInProgressRef.current && networkStatus.isOnline) {
          performSync();
        }
      }, syncInterval);
    }
    setSyncState((prev) => ({ ...prev, status: 'idle' }));
  }, [autoSync, syncInterval, networkStatus.isOnline, performSync]);

  // Clear sync queue
  const clearSyncQueue = useCallback(() => {
    setSyncQueue([]);
    setSyncState((prev) => ({
      ...prev,
      pendingUploads: 0,
      pendingDownloads: 0
    }));
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  // Provide sync context
  const syncContext = {
    syncState,
    syncQueue,
    addToSyncQueue,
    removeFromSyncQueue,
    triggerSync,
    pauseSync,
    resumeSync,
    clearSyncQueue,
    isOnline: networkStatus.isOnline
  };

  return (
    <BackgroundSyncProvider value={syncContext}>
      <div className={cn('relative', className)} {...props}>
        {/* Sync Status Indicator */}
        {showSyncStatus &&
        <SyncStatusIndicator syncState={syncState} onTriggerSync={triggerSync} />
        }

        {children}
      </div>
    </BackgroundSyncProvider>);

};

/**
 * SyncStatusIndicator - Shows current sync status
 */
const SyncStatusIndicator = ({ syncState, onTriggerSync }) => {const { t } = useTranslation();
  const { isMobile } = useMobile();
  const [isExpanded, setIsExpanded] = useState(false);

  if (syncState.status === 'idle' && syncState.pendingUploads === 0 && syncState.pendingDownloads === 0) {
    return null;
  }

  const getStatusIcon = () => {
    switch (syncState.status) {
      case 'syncing':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'paused':
        return <Clock className="h-4 w-4 text-orange-500" />;
      default:
        return <RefreshCw className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="fixed bottom-20 right-4 z-40">
      <div className="bg-background border border-border rounded-lg shadow-lg">
        <div
          className="flex items-center gap-2 p-2 cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}>

          {getStatusIcon()}
          
          <div className="text-xs">
            {syncState.pendingUploads > 0 &&
            <div className="flex items-center gap-1">
                <Upload className="h-3 w-3" />
                <span>{syncState.pendingUploads}</span>
              </div>
            }
            {syncState.pendingDownloads > 0 &&
            <div className="flex items-center gap-1">
                <Download className="h-3 w-3" />
                <span>{syncState.pendingDownloads}</span>
              </div>
            }
          </div>
        </div>

        {isExpanded &&
        <div className="border-t p-2 min-w-[200px]">
            <div className="space-y-2 text-xs">
              <div>Status: {syncState.status}</div>
              {syncState.lastSyncTime &&
            <div>{t("components.last_sync")}
              {new Date(syncState.lastSyncTime).toLocaleTimeString()}
                </div>
            }
              {syncState.failedSyncs > 0 &&
            <div className="text-red-500">{t("mobile.failed_syncs")}
              {syncState.failedSyncs}
                </div>
            }
            </div>
            
            <TouchOptimizedButton
            size="sm"
            variant="outline"
            onClick={onTriggerSync}
            disabled={syncState.isActive}
            className="w-full mt-2">

              {syncState.isActive ? 'Syncing...' : 'Sync Now'}
            </TouchOptimizedButton>
          </div>
        }
      </div>
    </div>);

};

/**
 * BackgroundSyncProvider - Context provider for sync functionality
 */
const BackgroundSyncContext = React.createContext({});

const BackgroundSyncProvider = ({ children, value }) =>
<BackgroundSyncContext.Provider value={value}>
    {children}
  </BackgroundSyncContext.Provider>;


/**
 * useBackgroundSync - Hook to access sync context
 */
export const useBackgroundSync = () => {
  const context = React.useContext(BackgroundSyncContext);
  if (!context) {
    throw new Error('useBackgroundSync must be used within a BackgroundSync component');
  }
  return context;
};

/**
 * withBackgroundSync - HOC to add sync capability to components
 */
export const withBackgroundSync = (Component, syncOptions = {}) => {
  return function BackgroundSyncComponent(props) {
    return (
      <BackgroundSync {...syncOptions}>
        <Component {...props} />
      </BackgroundSync>);

  };
};

export default BackgroundSync;