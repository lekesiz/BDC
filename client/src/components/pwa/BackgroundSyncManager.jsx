// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, AlertCircle, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { useBackgroundSync, useOnlineStatus } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

/**
 * Background Sync Manager Component
 * Manages offline actions and background synchronization
 */import { useTranslation } from "react-i18next";
export function BackgroundSyncManager({ className = '' }) {const { t } = useTranslation();
  const { syncQueue, isSyncing, lastSync, addToSyncQueue, clearSyncQueue } = useBackgroundSync();
  const { isOnline } = useOnlineStatus();
  const [syncProgress, setSyncProgress] = useState(0);

  useEffect(() => {
    if (isSyncing && syncQueue.length > 0) {
      // Simulate progress for visual feedback
      const interval = setInterval(() => {
        setSyncProgress((prev) => {
          const increment = 100 / syncQueue.length;
          return Math.min(prev + increment, 100);
        });
      }, 500);

      return () => clearInterval(interval);
    } else {
      setSyncProgress(0);
    }
  }, [isSyncing, syncQueue.length]);

  const handleRetrySync = async () => {
    if (syncQueue.length > 0) {
      for (const item of syncQueue) {
        await addToSyncQueue(item.tag, item.data);
      }
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleTimeString();
  };

  const getSyncStatusIcon = () => {
    if (!isOnline) return <WifiOff className="h-4 w-4 text-red-500" />;
    if (isSyncing) return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
    if (syncQueue.length > 0) return <Clock className="h-4 w-4 text-yellow-500" />;
    return <CheckCircle className="h-4 w-4 text-green-500" />;
  };

  const getSyncStatusText = () => {
    if (!isOnline) return 'Offline - Sync paused';
    if (isSyncing) return 'Syncing...';
    if (syncQueue.length > 0) return `${syncQueue.length} items pending`;
    return 'All synced';
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getSyncStatusIcon()}
            <CardTitle className="text-lg">{t("components.background_sync")}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {isOnline ?
            <Badge variant="success" className="bg-green-100 text-green-800">
                <Wifi className="h-3 w-3 mr-1" />{t("components.online")}

            </Badge> :

            <Badge variant="destructive" className="bg-red-100 text-red-800">
                <WifiOff className="h-3 w-3 mr-1" />{t("components.offline")}

            </Badge>
            }
          </div>
        </div>
        <CardDescription>
          {getSyncStatusText()}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Sync Progress */}
        {isSyncing &&
        <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{t("components.syncing_progress")}</span>
              <span>{Math.round(syncProgress)}%</span>
            </div>
            <Progress value={syncProgress} className="h-2" />
          </div>
        }

        {/* Sync Queue */}
        {syncQueue.length > 0 &&
        <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm">{t("components.pending_items")}</h4>
              <Badge variant="outline">{syncQueue.length}</Badge>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {syncQueue.map((item, index) =>
            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="flex items-center gap-2">
                    <Clock className="h-3 w-3 text-gray-500" />
                    <span className="text-xs font-medium capitalize">{item.tag.replace('-', ' ')}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {formatTime(item.timestamp)}
                  </span>
                </div>
            )}
            </div>
          </div>
        }

        {/* Last Sync Info */}
        <div className="text-xs text-gray-500">{t("components.last_sync")}
          {formatTime(lastSync)}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          {syncQueue.length > 0 && isOnline && !isSyncing &&
          <Button
            onClick={handleRetrySync}
            size="sm"
            variant="outline"
            className="flex-1">

              <RefreshCw className="h-3 w-3 mr-1" />{t("components.retry_sync")}

          </Button>
          }
          
          {syncQueue.length > 0 &&
          <Button
            onClick={clearSyncQueue}
            size="sm"
            variant="outline"
            className="flex-1">{t("components.clear_queue")}


          </Button>
          }
        </div>

        {/* Sync Status Messages */}
        {!isOnline &&
        <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
            <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            <span className="text-sm text-yellow-700 dark:text-yellow-300">{t("components.your_changes_will_sync_automatically_when_youre_ba")}

          </span>
          </div>
        }

        {syncQueue.length === 0 && isOnline &&
        <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded">
            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
            <span className="text-sm text-green-700 dark:text-green-300">{t("components.all_your_data_is_synchronized_and_up_to_date")}

          </span>
          </div>
        }
      </CardContent>
    </Card>);

}

/**
 * Simple Sync Status Indicator
 * Minimal component showing sync status
 */
export function SyncStatusIndicator({ className = '' }) {const { t } = useTranslation();
  const { syncQueue, isSyncing } = useBackgroundSync();
  const { isOnline } = useOnlineStatus();

  if (!isOnline && syncQueue.length === 0) return null;

  return (
    <div className={`flex items-center gap-2 text-sm ${className}`}>
      {isSyncing ?
      <>
          <RefreshCw className="h-3 w-3 animate-spin text-blue-500" />
          <span className="text-blue-600 dark:text-blue-400">Syncing...</span>
        </> :
      syncQueue.length > 0 ?
      <>
          <Clock className="h-3 w-3 text-yellow-500" />
          <span className="text-yellow-600 dark:text-yellow-400">
            {syncQueue.length} pending
          </span>
        </> :

      <>
          <CheckCircle className="h-3 w-3 text-green-500" />
          <span className="text-green-600 dark:text-green-400">{t("components.synced")}</span>
        </>
      }
    </div>);

}

/**
 * Sync Queue Item Component
 * Individual queue item with retry functionality
 */
export function SyncQueueItem({ item, onRetry, onRemove, className = '' }) {const { t } = useTranslation();
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    try {
      await onRetry(item);
    } finally {
      setIsRetrying(false);
    }
  };

  return (
    <div className={`flex items-center justify-between p-3 bg-white dark:bg-gray-800 border rounded ${className}`}>
      <div className="flex items-center gap-3">
        <div className="p-1 bg-yellow-100 dark:bg-yellow-900/30 rounded">
          <Clock className="h-3 w-3 text-yellow-600 dark:text-yellow-400" />
        </div>
        <div>
          <div className="font-medium text-sm capitalize">
            {item.tag.replace('-', ' ')}
          </div>
          <div className="text-xs text-gray-500">
            {new Date(item.timestamp).toLocaleString()}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          onClick={handleRetry}
          disabled={isRetrying}
          size="sm"
          variant="outline">

          {isRetrying ?
          <RefreshCw className="h-3 w-3 animate-spin" /> :

          'Retry'
          }
        </Button>
        <Button
          onClick={() => onRemove(item)}
          size="sm"
          variant="ghost"
          className="text-red-600 hover:text-red-700">{t("components.remove")}


        </Button>
      </div>
    </div>);

}

export default BackgroundSyncManager;