// TODO: i18n - processed
/**
 * RealtimeMonitor Component
 * 
 * Real-time monitoring and live updates for reports and dashboards
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Switch } from '../../../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Progress } from '../../../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import {
  Activity,
  Wifi,
  WifiOff,
  Play,
  Pause,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  Database,
  Zap,
  Settings,
  Info } from
'lucide-react';

import useRealtime from '../hooks/useRealtime';
import { formatDistanceToNow } from 'date-fns';import { useTranslation } from "react-i18next";

const CONNECTION_STATUS_COLORS = {
  connected: 'bg-green-500',
  connecting: 'bg-yellow-500',
  disconnected: 'bg-red-500',
  error: 'bg-red-600'
};

const CONNECTION_STATUS_LABELS = {
  connected: 'Connected',
  connecting: 'Connecting...',
  disconnected: 'Disconnected',
  error: 'Connection Error'
};

const UPDATE_FREQUENCIES = [
{ value: 1, label: '1 second' },
{ value: 5, label: '5 seconds' },
{ value: 10, label: '10 seconds' },
{ value: 30, label: '30 seconds' },
{ value: 60, label: '1 minute' },
{ value: 300, label: '5 minutes' }];


const RealtimeMonitor = ({
  subscriptionConfig = {},
  onDataUpdate = null,
  onConnectionChange = null,
  autoStart = true,
  className = ''
}) => {const { t } = useTranslation();
  const {
    isConnected,
    connectionStatus,
    subscriptions,
    latestData,
    error,
    statistics,
    subscribe,
    unsubscribe,
    updateSubscription,
    reconnect,
    disconnect
  } = useRealtime();

  const [isMonitoring, setIsMonitoring] = useState(autoStart);
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [updateFrequency, setUpdateFrequency] = useState(5);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [dataHistory, setDataHistory] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    updateCount: 0,
    errorCount: 0,
    avgResponseTime: 0,
    lastUpdateTime: null
  });

  const dataHistoryRef = useRef([]);
  const metricsRef = useRef(performanceMetrics);

  // Update performance metrics when new data arrives
  useEffect(() => {
    if (latestData) {
      const now = Date.now();
      const updateTime = new Date(latestData.timestamp);
      const responseTime = now - updateTime.getTime();

      metricsRef.current = {
        ...metricsRef.current,
        updateCount: metricsRef.current.updateCount + 1,
        avgResponseTime: (metricsRef.current.avgResponseTime + responseTime) / 2,
        lastUpdateTime: now
      };

      setPerformanceMetrics({ ...metricsRef.current });

      // Add to data history (keep last 50 updates)
      const historyItem = {
        id: Date.now(),
        timestamp: latestData.timestamp,
        subscriptionId: latestData.subscription_id,
        type: latestData.type,
        recordCount: latestData.data?.report_data?.data?.length || 0,
        responseTime
      };

      dataHistoryRef.current = [historyItem, ...dataHistoryRef.current.slice(0, 49)];
      setDataHistory([...dataHistoryRef.current]);

      if (onDataUpdate) {
        onDataUpdate(latestData);
      }
    }
  }, [latestData, onDataUpdate]);

  // Update error count
  useEffect(() => {
    if (error) {
      metricsRef.current = {
        ...metricsRef.current,
        errorCount: metricsRef.current.errorCount + 1
      };
      setPerformanceMetrics({ ...metricsRef.current });
    }
  }, [error]);

  // Notify connection changes
  useEffect(() => {
    if (onConnectionChange) {
      onConnectionChange(connectionStatus, isConnected);
    }
  }, [connectionStatus, isConnected, onConnectionChange]);

  const handleStartMonitoring = useCallback(async () => {
    if (!subscriptionConfig.type) {
      return;
    }

    try {
      const result = await subscribe({
        ...subscriptionConfig,
        update_frequency: updateFrequency,
        auto_refresh: true
      });

      if (result.success) {
        setSelectedSubscription(result.subscription_id);
        setIsMonitoring(true);
      }
    } catch (err) {
      console.error('Failed to start monitoring:', err);
    }
  }, [subscribe, subscriptionConfig, updateFrequency]);

  const handleStopMonitoring = useCallback(async () => {
    if (selectedSubscription) {
      try {
        await unsubscribe(selectedSubscription);
        setSelectedSubscription(null);
        setIsMonitoring(false);
      } catch (err) {
        console.error('Failed to stop monitoring:', err);
      }
    }
  }, [unsubscribe, selectedSubscription]);

  const handleUpdateFrequencyChange = useCallback(async (newFrequency) => {
    setUpdateFrequency(newFrequency);

    if (selectedSubscription) {
      try {
        await updateSubscription(selectedSubscription, {
          update_frequency: newFrequency
        });
      } catch (err) {
        console.error('Failed to update frequency:', err);
      }
    }
  }, [updateSubscription, selectedSubscription]);

  const handleReconnect = useCallback(() => {
    reconnect();
  }, [reconnect]);

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="h-4 w-4 text-green-600" />;
      case 'connecting':
        return <RefreshCw className="h-4 w-4 text-yellow-600 animate-spin" />;
      case 'disconnected':
      case 'error':
        return <WifiOff className="h-4 w-4 text-red-600" />;
      default:
        return <WifiOff className="h-4 w-4 text-gray-600" />;
    }
  };

  const renderConnectionStatus = () =>
  <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getConnectionStatusIcon()}
            <span>{t("components.connection_status")}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${CONNECTION_STATUS_COLORS[connectionStatus]}`} />
            <Badge variant={isConnected ? 'default' : 'destructive'}>
              {CONNECTION_STATUS_LABELS[connectionStatus]}
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {!isConnected &&
      <Button onClick={handleReconnect} size="sm" className="w-full">
            <RefreshCw className="h-4 w-4 mr-2" />{t("reporting.reconnect")}

      </Button>
      }

        {error &&
      <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              {error.message || 'Connection error occurred'}
            </AlertDescription>
          </Alert>
      }

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-gray-600">{t("reporting.active_subscriptions")}

        </div>
          <div className="font-medium">
            {subscriptions.length}
          </div>
          
          <div className="text-gray-600">{t("reporting.updates_received")}

        </div>
          <div className="font-medium">
            {performanceMetrics.updateCount}
          </div>
          
          <div className="text-gray-600">
            Errors:
          </div>
          <div className="font-medium text-red-600">
            {performanceMetrics.errorCount}
          </div>
          
          <div className="text-gray-600">{t("reporting.avg_response")}

        </div>
          <div className="font-medium">
            {performanceMetrics.avgResponseTime.toFixed(0)}ms
          </div>
        </div>
      </CardContent>
    </Card>;


  const renderMonitoringControls = () =>
  <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4" />
            <span>{t("reporting.monitoring_controls")}</span>
          </div>
          <Switch
          checked={isMonitoring}
          onCheckedChange={isMonitoring ? handleStopMonitoring : handleStartMonitoring}
          disabled={!isConnected || !subscriptionConfig.type} />

        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-xs font-medium text-gray-700 block mb-2">{t("reporting.update_frequency")}

        </label>
          <Select
          value={updateFrequency.toString()}
          onValueChange={(value) => handleUpdateFrequencyChange(parseInt(value))}
          disabled={!isConnected}>

            <SelectTrigger className="h-8">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {UPDATE_FREQUENCIES.map((freq) =>
            <SelectItem key={freq.value} value={freq.value.toString()}>
                  {freq.label}
                </SelectItem>
            )}
            </SelectContent>
          </Select>
        </div>

        {isMonitoring && selectedSubscription &&
      <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">{t("reporting.subscription_id")}</span>
              <code className="text-xs bg-gray-100 px-1 rounded">
                {selectedSubscription.slice(-8)}
              </code>
            </div>
            
            {performanceMetrics.lastUpdateTime &&
        <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">{t("reporting.last_update")}</span>
                <span className="text-gray-900">
                  {formatDistanceToNow(new Date(performanceMetrics.lastUpdateTime), { addSuffix: true })}
                </span>
              </div>
        }
          </div>
      }

        {!isConnected &&
      <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription className="text-xs">{t("reporting.connect_to_enable_realtime_monitoring")}

        </AlertDescription>
          </Alert>
      }
      </CardContent>
    </Card>;


  const renderDataPreview = () =>
  <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center space-x-2">
          <Database className="h-4 w-4" />
          <span>{t("reporting.latest_data")}</span>
          {latestData &&
        <Badge variant="outline" className="text-xs">
              {latestData.data?.report_data?.data?.length || 0} records
            </Badge>
        }
        </CardTitle>
      </CardHeader>
      <CardContent>
        {latestData ?
      <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-gray-600">Type:</div>
              <div className="font-medium">{latestData.type}</div>
              
              <div className="text-gray-600">Timestamp:</div>
              <div className="font-medium">
                {new Date(latestData.timestamp).toLocaleTimeString()}
              </div>
              
              <div className="text-gray-600">Records:</div>
              <div className="font-medium">
                {latestData.data?.report_data?.data?.length || 0}
              </div>
            </div>

            {latestData.data?.report_data?.data && latestData.data.report_data.data.length > 0 &&
        <div className="mt-3">
                <div className="text-xs font-medium text-gray-700 mb-2">{t("reporting.sample_data")}</div>
                <div className="bg-gray-50 rounded p-2 text-xs font-mono overflow-x-auto">
                  <pre>
                    {JSON.stringify(latestData.data.report_data.data[0], null, 2)}
                  </pre>
                </div>
              </div>
        }
          </div> :

      <div className="text-center text-gray-500 py-4">
            <Database className="h-6 w-6 mx-auto mb-2 text-gray-400" />
            <p className="text-xs">{t("reporting.no_data_received_yet")}</p>
            <p className="text-xs text-gray-400 mt-1">{t("reporting.start_monitoring_to_see_live_updates")}

        </p>
          </div>
      }
      </CardContent>
    </Card>;


  const renderActivityHistory = () =>
  <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center space-x-2">
          <Clock className="h-4 w-4" />
          <span>{t("reporting.activity_history")}</span>
          {dataHistory.length > 0 &&
        <Badge variant="outline" className="text-xs">
              {dataHistory.length} updates
            </Badge>
        }
        </CardTitle>
      </CardHeader>
      <CardContent>
        {dataHistory.length > 0 ?
      <div className="space-y-2 max-h-64 overflow-y-auto">
            {dataHistory.map((item) =>
        <div key={item.id} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="font-medium">{item.type}</span>
                  <span className="text-gray-600">
                    {item.recordCount} records
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-gray-500">
                  <span>{item.responseTime}ms</span>
                  <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
        )}
          </div> :

      <div className="text-center text-gray-500 py-4">
            <Clock className="h-6 w-6 mx-auto mb-2 text-gray-400" />
            <p className="text-xs">{t("reporting.no_activity_history")}</p>
          </div>
      }
      </CardContent>
    </Card>;


  const renderPerformanceMetrics = () =>
  <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center space-x-2">
          <TrendingUp className="h-4 w-4" />
          <span>{t("components.performance")}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {performanceMetrics.updateCount}
              </div>
              <div className="text-xs text-gray-600">{t("components.updates")}</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {performanceMetrics.avgResponseTime.toFixed(0)}ms
              </div>
              <div className="text-xs text-gray-600">{t("components.avg_response")}</div>
            </div>
          </div>

          {performanceMetrics.errorCount > 0 &&
        <div className="text-center">
              <div className="text-lg font-bold text-red-600">
                {performanceMetrics.errorCount}
              </div>
              <div className="text-xs text-gray-600">{t("components.errors")}</div>
            </div>
        }

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>{t("reporting.success_rate")}</span>
              <span className="font-medium">
                {performanceMetrics.updateCount > 0 ?
              ((performanceMetrics.updateCount - performanceMetrics.errorCount) / performanceMetrics.updateCount * 100).toFixed(1) :
              0
              }%
              </span>
            </div>
            
            <Progress
            value={performanceMetrics.updateCount > 0 ?
            (performanceMetrics.updateCount - performanceMetrics.errorCount) / performanceMetrics.updateCount * 100 :
            0
            }
            className="h-2" />

          </div>
        </div>
      </CardContent>
    </Card>;


  return (
    <div className={`space-y-4 ${className}`}>
      {/* Quick Status Bar */}
      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-3">
          {getConnectionStatusIcon()}
          <span className="text-sm font-medium">{t("reporting.realtime_monitor")}

          </span>
          <Badge variant={isMonitoring ? 'default' : 'secondary'}>
            {isMonitoring ? 'Active' : 'Inactive'}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-2">
          {performanceMetrics.updateCount > 0 &&
          <Badge variant="outline" className="text-xs">
              {performanceMetrics.updateCount} updates
            </Badge>
          }
          
          <Button
            size="sm"
            variant={isMonitoring ? 'destructive' : 'default'}
            onClick={isMonitoring ? handleStopMonitoring : handleStartMonitoring}
            disabled={!isConnected || !subscriptionConfig.type}>

            {isMonitoring ?
            <>
                <Pause className="h-3 w-3 mr-1" />{t("reporting.stop")}

            </> :

            <>
                <Play className="h-3 w-3 mr-1" />{t("components.start")}

            </>
            }
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="status" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="status">{t("components.status")}</TabsTrigger>
          <TabsTrigger value="data">{t("components.data")}</TabsTrigger>
          <TabsTrigger value="activity">{t("pages.activity")}</TabsTrigger>
          <TabsTrigger value="performance">{t("components.performance")}</TabsTrigger>
        </TabsList>

        <TabsContent value="status" className="space-y-4">
          {renderConnectionStatus()}
          {renderMonitoringControls()}
        </TabsContent>

        <TabsContent value="data" className="space-y-4">
          {renderDataPreview()}
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          {renderActivityHistory()}
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          {renderPerformanceMetrics()}
        </TabsContent>
      </Tabs>
    </div>);

};

export default RealtimeMonitor;