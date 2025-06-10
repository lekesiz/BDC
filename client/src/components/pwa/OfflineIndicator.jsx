// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, CloudOff, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { useOnlineStatus, useBackgroundSync } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
/**
 * Offline Status Indicator
 * Shows current connection status and sync information
 */import { useTranslation } from "react-i18next";
export function OfflineIndicator({ className = '' }) {const { t } = useTranslation();
  const { isOnline, connectionInfo } = useOnlineStatus();
  const { syncQueue, isSyncing, lastSync } = useBackgroundSync();
  const [showDetails, setShowDetails] = useState(false);
  const pendingCount = syncQueue.length;
  const hasSlowConnection = connectionInfo?.effectiveType === 'slow-2g' ||
  connectionInfo?.effectiveType === '2g';
  if (isOnline && !pendingCount && !hasSlowConnection) {
    return null;
  }
  const getStatusColor = () => {
    if (!isOnline) return 'bg-red-500';
    if (pendingCount > 0) return 'bg-orange-500';
    if (hasSlowConnection) return 'bg-yellow-500';
    return 'bg-green-500';
  };
  const getStatusText = () => {
    if (!isOnline) return 'Offline';
    if (isSyncing) return 'Syncing...';
    if (pendingCount > 0) return `${pendingCount} pending`;
    if (hasSlowConnection) return 'Slow connection';
    return 'Online';
  };
  const getStatusIcon = () => {
    if (!isOnline) return <WifiOff className="h-4 w-4" />;
    if (isSyncing) return <RefreshCw className="h-4 w-4 animate-spin" />;
    if (pendingCount > 0) return <CloudOff className="h-4 w-4" />;
    return <Wifi className="h-4 w-4" />;
  };
  return (
    <>
      {/* Status indicator */}
      <div className={`flex items-center gap-2 ${className}`}>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowDetails(!showDetails)}
          className="h-8 px-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200">

          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-xs">{getStatusText()}</span>
            <div className={`h-2 w-2 rounded-full ${getStatusColor()}`} />
          </div>
        </Button>
      </div>
      {/* Detailed status panel */}
      {showDetails &&
      <Card className="absolute top-full right-0 mt-2 w-80 z-50 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              {getStatusIcon()}{t("components.connection_status")}

          </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Connection info */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Status:</span>
                <Badge variant={isOnline ? 'default' : 'destructive'}>
                  {isOnline ? 'Online' : 'Offline'}
                </Badge>
              </div>
              {connectionInfo &&
            <>
                  <div className="flex items-center justify-between text-sm">
                    <span>{t("components.connection")}</span>
                    <span className="text-gray-600 dark:text-gray-400">
                      {connectionInfo.effectiveType || 'Unknown'}
                    </span>
                  </div>
                  {connectionInfo.downlink &&
              <div className="flex items-center justify-between text-sm">
                      <span>Speed:</span>
                      <span className="text-gray-600 dark:text-gray-400">
                        {connectionInfo.downlink}{t("components.mbps")}
                </span>
                    </div>
              }
                </>
            }
            </div>
            {/* Sync status */}
            {(pendingCount > 0 || isSyncing || lastSync) &&
          <div className="border-t pt-3 space-y-2">
                <h4 className="text-sm font-medium">{t("components.sync_status")}</h4>
                {isSyncing &&
            <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
                    <RefreshCw className="h-3 w-3 animate-spin" />
                    <span>{t("components.syncing_data")}</span>
                  </div>
            }
                {pendingCount > 0 &&
            <div className="flex items-center gap-2 text-sm text-orange-600 dark:text-orange-400">
                    <CloudOff className="h-3 w-3" />
                    <span>{pendingCount}{t("components.items_waiting_to_sync")}</span>
                  </div>
            }
                {lastSync &&
            <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                    <CheckCircle className="h-3 w-3" />
                    <span>{t("components.last_sync")}{lastSync.toLocaleTimeString()}</span>
                  </div>
            }
              </div>
          }
            {/* Actions */}
            <div className="border-t pt-3">
              <Button
              onClick={() => window.location.reload()}
              variant="outline"
              size="sm"
              className="w-full">

                <RefreshCw className="mr-2 h-3 w-3" />{t("components.retry_connection")}

            </Button>
            </div>
          </CardContent>
        </Card>
      }
    </>);

}
/**
 * Offline Banner
 * Full-width banner shown when offline
 */
export function OfflineBanner({ className = '' }) {const { t } = useTranslation();
  const { isOnline } = useOnlineStatus();
  const { syncQueue } = useBackgroundSync();
  const [dismissed, setDismissed] = useState(false);
  useEffect(() => {
    if (isOnline) {
      setDismissed(false);
    }
  }, [isOnline]);
  if (isOnline || dismissed) {
    return null;
  }
  const pendingCount = syncQueue.length;
  return (
    <Alert className={`border-orange-200 bg-orange-50 dark:bg-orange-950 dark:border-orange-800 ${className}`}>
      <WifiOff className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="font-medium">{t("components.youre_offline")}</span>
          {pendingCount > 0 &&
          <span className="text-sm text-orange-700 dark:text-orange-300">
              {pendingCount}{t("components.changes_will_sync_when_youre_back_online")}
          </span>
          }
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setDismissed(true)}
          className="text-orange-600 hover:text-orange-800 dark:text-orange-400">{t("components.dismiss")}


        </Button>
      </AlertDescription>
    </Alert>);

}
/**
 * Connection Quality Indicator
 * Shows connection quality and speed
 */
export function ConnectionQualityIndicator({ className = '' }) {const { t } = useTranslation();
  const { isOnline, connectionInfo } = useOnlineStatus();
  if (!isOnline || !connectionInfo) {
    return null;
  }
  const getQualityColor = () => {
    if (!connectionInfo.effectiveType) return 'text-gray-400';
    switch (connectionInfo.effectiveType) {
      case '4g':
        return 'text-green-500';
      case '3g':
        return 'text-yellow-500';
      case '2g':
      case 'slow-2g':
        return 'text-red-500';
      default:
        return 'text-gray-400';
    }
  };
  const getQualityBars = () => {
    if (!connectionInfo.effectiveType) return 1;
    switch (connectionInfo.effectiveType) {
      case '4g':
        return 4;
      case '3g':
        return 3;
      case '2g':
        return 2;
      case 'slow-2g':
        return 1;
      default:
        return 1;
    }
  };
  const bars = getQualityBars();
  const qualityColor = getQualityColor();
  return (
    <div className={`flex items-center gap-1 ${className}`} title={`Connection: ${connectionInfo.effectiveType}`}>
      {[1, 2, 3, 4].map((bar) =>
      <div
        key={bar}
        className={`w-1 h-3 rounded-sm ${
        bar <= bars ? qualityColor.replace('text-', 'bg-') : 'bg-gray-300 dark:bg-gray-600'}`
        } />

      )}
    </div>);

}
/**
 * Sync Queue Status
 * Shows pending sync operations
 */
export function SyncQueueStatus({ className = '' }) {const { t } = useTranslation();
  const { syncQueue, isSyncing } = useBackgroundSync();
  if (syncQueue.length === 0 && !isSyncing) {
    return null;
  }
  return (
    <div className={`flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 ${className}`}>
      {isSyncing ?
      <>
          <RefreshCw className="h-3 w-3 animate-spin text-blue-500" />
          <span>Syncing...</span>
        </> :

      <>
          <CloudOff className="h-3 w-3 text-orange-500" />
          <span>{syncQueue.length} pending</span>
        </>
      }
    </div>);

}
export default OfflineIndicator;