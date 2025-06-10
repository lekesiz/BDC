// TODO: i18n - processed
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw, 
  Wifi, 
  WifiOff,
  Trash2,
  Pause,
  Play,
  Settings,
  BarChart3,
  Download,
  Upload,
  Sync
} from 'lucide-react';
import { useBackgroundSync, useOnlineStatus } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../ui/use-toast';

/**
 * Advanced Background Sync Manager Component
 * Comprehensive background sync management with retry mechanisms and detailed monitoring
 */import { useTranslation } from "react-i18next";
export function BackgroundSyncManager({ className = '' }) {const { t } = useTranslation();
  const { syncQueue, isSyncing, lastSync, addToSyncQueue, clearSyncQueue } = useBackgroundSync();
  const { isOnline } = useOnlineStatus();
  const { toast } = useToast();
  
  // Enhanced state for advanced features
  const [syncStats, setSyncStats] = useState({});
  const [syncSettings, setSyncSettings] = useState({
    autoSync: true,
    batchSize: 5,
    retryDelay: 5000,
    maxRetries: 3
  });
  const [activeSyncs, setActiveSyncs] = useState(new Set());
  const [syncHistory, setSyncHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Mock enhanced sync queue with more details
  const enhancedSyncQueue = syncQueue.map((item, index) => ({
    ...item,
    id: item.id || `sync_${index}`,
    type: item.tag?.split('-')[0] || 'unknown',
    operation: item.tag?.split('-')[1] || 'update',
    priority: index < 2 ? 'high' : 'normal',
    retryCount: Math.floor(Math.random() * 3),
    maxRetries: syncSettings.maxRetries,
    status: ['pending', 'retrying', 'failed'][Math.floor(Math.random() * 3)] || 'pending',
    estimatedSize: Math.random() * 100 + 10,
    lastError: Math.random() > 0.7 ? 'Network timeout' : null
  }));

  useEffect(() => {
    updateSyncStats();
    loadSyncHistory();
  }, [syncQueue]);

  const updateSyncStats = useCallback(() => {
    const stats = {
      total: enhancedSyncQueue.length,
      pending: enhancedSyncQueue.filter(item => item.status === 'pending').length,
      retrying: enhancedSyncQueue.filter(item => item.status === 'retrying').length,
      failed: enhancedSyncQueue.filter(item => item.status === 'failed').length,
      totalSize: enhancedSyncQueue.reduce((sum, item) => sum + item.estimatedSize, 0)
    };
    setSyncStats(stats);
  }, [enhancedSyncQueue]);

  const loadSyncHistory = useCallback(() => {
    // Mock sync history for demonstration
    const history = [
      {
        id: 'hist_1',
        type: 'evaluation',
        operation: 'create',
        timestamp: Date.now() - 3600000,
        status: 'success',
        duration: 1200
      },
      {
        id: 'hist_2', 
        type: 'beneficiary',
        operation: 'update',
        timestamp: Date.now() - 7200000,
        status: 'failed',
        error: 'Network error'
      }
    ];
    setSyncHistory(history);
  }, []);

  const handleRetrySync = async () => {
    if (enhancedSyncQueue.length > 0) {
      setLoading(true);
      try {
        for (const item of enhancedSyncQueue) {
          await addToSyncQueue(item.tag, item.data);
        }
        toast({
          title: t("components.sync_retry_initiated"),
          description: `${enhancedSyncQueue.length} items queued for retry`
        });
      } catch (error) {
        toast({
          title: t("components.sync_retry_failed"),
          description: error.message,
          variant: 'destructive'
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const retrySpecificItem = async (item) => {
    try {
      await addToSyncQueue(item.tag, item.data);
      toast({
        title: t("components.item_queued_for_retry"),
        description: `${item.type} ${item.operation}`
      });
    } catch (error) {
      toast({
        title: t("components.retry_failed"),
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  const removeSpecificItem = (item) => {
    // In real implementation, this would remove from actual queue
    toast({
      title: t("components.item_removed"),
      description: `${item.type} ${item.operation} removed from queue`
    });
  };

  const exportSyncData = () => {
    const exportData = {
      queue: enhancedSyncQueue,
      history: syncHistory,
      stats: syncStats,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sync-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleTimeString();
  };

  const formatSize = (sizeKB) => {
    if (sizeKB < 1) return `${Math.round(sizeKB * 1000)} B`;
    if (sizeKB < 1024) return `${sizeKB.toFixed(1)} KB`;
    return `${(sizeKB / 1024).toFixed(1)} MB`;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-orange-500" />;
      case 'syncing': return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'retrying': return <RefreshCw className="w-4 h-4 text-orange-500" />;
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'orange';
      case 'syncing': return 'blue';
      case 'retrying': return 'orange';
      case 'failed': return 'red';
      case 'success': return 'green';
      default: return 'gray';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Connection Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">{t("components.background_sync")}</h2>
          <div className="flex items-center gap-2">
            {isOnline ? (
              <Wifi className="w-5 h-5 text-green-500" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-500" />
            )}
            <span className={`text-sm ${isOnline ? 'text-green-600' : 'text-red-600'}`}>
              {isOnline ? t("components.online") : t("components.offline")}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handleRetrySync}
            disabled={!isOnline || loading || enhancedSyncQueue.length === 0}
          >
            <Sync className="w-4 h-4 mr-2" />
            {t("components.sync_now")}
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={exportSyncData}
          >
            <Download className="w-4 h-4 mr-2" />
            {t("components.export")}
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">{syncStats.total || 0}</div>
              <div className="text-sm text-muted-foreground">{t("components.total_items")}</div>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-500" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">{syncStats.pending || 0}</div>
              <div className="text-sm text-muted-foreground">{t("components.pending")}</div>
            </div>
            <Clock className="w-8 h-8 text-orange-500" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">{syncStats.failed || 0}</div>
              <div className="text-sm text-muted-foreground">{t("components.failed")}</div>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold">{formatSize(syncStats.totalSize || 0)}</div>
              <div className="text-sm text-muted-foreground">{t("components.queue_size")}</div>
            </div>
            <Upload className="w-8 h-8 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Offline Alert */}
      {!isOnline && (
        <Alert>
          <WifiOff className="w-4 h-4" />
          <AlertDescription>
            {t("components.offline_sync_message")}
          </AlertDescription>
        </Alert>
      )}

      {/* Enhanced Sync Queue Display */}
      <Tabs defaultValue="queue" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="queue">{t("components.sync_queue")}</TabsTrigger>
          <TabsTrigger value="history">{t("components.sync_history")}</TabsTrigger>
          <TabsTrigger value="settings">{t("components.settings")}</TabsTrigger>
        </TabsList>

        <TabsContent value="queue" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">{t("components.sync_queue")} ({enhancedSyncQueue.length})</h3>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={handleRetrySync}
                disabled={syncStats.failed === 0}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                {t("components.retry_failed")}
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={clearSyncQueue}
                disabled={enhancedSyncQueue.length === 0}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                {t("components.clear_queue")}
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            {enhancedSyncQueue.length === 0 ? (
              <Card className="p-8 text-center">
                <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                <h3 className="text-lg font-semibold mb-2">{t("components.all_synced")}</h3>
                <p className="text-muted-foreground">
                  {t("components.no_pending_sync_items")}
                </p>
              </Card>
            ) : (
              enhancedSyncQueue.map((item) => (
                <Card key={item.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(item.status)}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{item.type}</span>
                          <Badge variant="outline">{item.operation}</Badge>
                          <Badge variant={getStatusColor(item.status)}>
                            {item.status}
                          </Badge>
                          {item.priority === 'high' && (
                            <Badge variant="destructive">{t("components.high_priority")}</Badge>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {formatSize(item.estimatedSize)} • 
                          {formatTime(item.timestamp)} • 
                          {t("components.retries")}: {item.retryCount}/{item.maxRetries}
                          {item.lastError && (
                            <span className="text-red-500 ml-2">
                              {t("components.error")}: {item.lastError}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {item.status === 'failed' && item.retryCount < item.maxRetries && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => retrySpecificItem(item)}
                        >
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeSpecificItem(item)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <h3 className="text-lg font-semibold">{t("components.sync_history")}</h3>
          <div className="space-y-2">
            {syncHistory.map((item) => (
              <Card key={item.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(item.status)}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{item.type}</span>
                        <Badge variant="outline">{item.operation}</Badge>
                        <Badge variant={getStatusColor(item.status)}>
                          {item.status}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {formatTime(item.timestamp)}
                        {item.error && (
                          <span className="text-red-500 ml-2">
                            {t("components.error")}: {item.error}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">{t("components.sync_settings")}</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">{t("components.auto_sync")}</label>
                  <p className="text-sm text-muted-foreground">
                    {t("components.auto_sync_description")}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant={syncSettings.autoSync ? "default" : "outline"}
                  onClick={() => setSyncSettings(prev => ({ 
                    ...prev, 
                    autoSync: !prev.autoSync 
                  }))}
                >
                  {syncSettings.autoSync ? <Pause /> : <Play />}
                </Button>
              </div>

              <div>
                <label className="text-sm font-medium">
                  {t("components.batch_size")}: {syncSettings.batchSize}
                </label>
                <p className="text-sm text-muted-foreground mb-2">
                  {t("components.batch_size_description")}
                </p>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={syncSettings.batchSize}
                  onChange={(e) => setSyncSettings(prev => ({ 
                    ...prev, 
                    batchSize: parseInt(e.target.value) 
                  }))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-sm font-medium">
                  {t("components.max_retries")}: {syncSettings.maxRetries}
                </label>
                <p className="text-sm text-muted-foreground mb-2">
                  {t("components.max_retries_description")}
                </p>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={syncSettings.maxRetries}
                  onChange={(e) => setSyncSettings(prev => ({ 
                    ...prev, 
                    maxRetries: parseInt(e.target.value) 
                  }))}
                  className="w-full"
                />
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
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