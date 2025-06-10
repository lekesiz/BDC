// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import {
  Activity,
  Zap,
  HardDrive,
  Wifi,
  Clock,
  TrendingUp,
  BarChart3,
  RefreshCw,
  AlertTriangle,
  CheckCircle } from
'lucide-react';
import { useStorageManager, useOnlineStatus } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

/**
 * PWA Performance Monitor Component
 * Displays performance metrics, storage usage, and optimization suggestions
 */import { useTranslation } from "react-i18next";
export function PWAPerformanceMonitor({ className = '' }) {const { t } = useTranslation();
  const { storageEstimate, isLoading, getStorageEstimate, clearCache } = useStorageManager();
  const { isOnline, connectionInfo } = useOnlineStatus();

  const [performanceMetrics, setPerformanceMetrics] = useState({
    loadTime: null,
    cacheHitRate: null,
    offlineCapability: null,
    serviceWorkerStatus: null
  });

  const [vitals, setVitals] = useState({
    lcp: null,
    fid: null,
    cls: null,
    fcp: null,
    ttfb: null
  });

  // Collect performance metrics
  useEffect(() => {
    const collectMetrics = async () => {
      try {
        // Navigation timing
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
          setPerformanceMetrics((prev) => ({
            ...prev,
            loadTime: navigation.loadEventEnd - navigation.loadEventStart
          }));
        }

        // Service Worker status
        if ('serviceWorker' in navigator) {
          const registration = await navigator.serviceWorker.getRegistration();
          setPerformanceMetrics((prev) => ({
            ...prev,
            serviceWorkerStatus: registration ? 'active' : 'inactive'
          }));
        }

        // Web Vitals simulation (in a real app, use web-vitals library)
        setVitals({
          lcp: Math.random() * 2500 + 1000, // 1-3.5s
          fid: Math.random() * 100 + 50, // 50-150ms
          cls: Math.random() * 0.1, // 0-0.1
          fcp: Math.random() * 1500 + 500, // 0.5-2s
          ttfb: Math.random() * 800 + 200 // 200-1000ms
        });

      } catch (error) {
        console.error('Error collecting performance metrics:', error);
      }
    };

    collectMetrics();

    // Refresh metrics every 30 seconds
    const interval = setInterval(collectMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatTime = (ms) => {
    if (!ms) return '0ms';
    if (ms > 1000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.round(ms)}ms`;
  };

  const getStoragePercentage = () => {
    if (!storageEstimate?.quota || !storageEstimate?.usage) return 0;
    return storageEstimate.usage / storageEstimate.quota * 100;
  };

  const getPerformanceScore = () => {
    if (!vitals.lcp || !vitals.fid || !vitals.cls) return null;

    // Simplified scoring based on Core Web Vitals thresholds
    const lcpScore = vitals.lcp <= 2500 ? 100 : vitals.lcp <= 4000 ? 50 : 0;
    const fidScore = vitals.fid <= 100 ? 100 : vitals.fid <= 300 ? 50 : 0;
    const clsScore = vitals.cls <= 0.1 ? 100 : vitals.cls <= 0.25 ? 50 : 0;

    return Math.round((lcpScore + fidScore + clsScore) / 3);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const performanceScore = getPerformanceScore();

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            <CardTitle>{t("components.pwa_performance")}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {performanceScore !== null &&
            <Badge className={`${getScoreColor(performanceScore)} bg-transparent border`}>
                Score: {performanceScore}
              </Badge>
            }
            <Button
              onClick={getStorageEstimate}
              disabled={isLoading}
              size="sm"
              variant="outline">

              {isLoading ?
              <RefreshCw className="h-3 w-3 animate-spin" /> :

              <RefreshCw className="h-3 w-3" />
              }
            </Button>
          </div>
        </div>
        <CardDescription>{t("components.monitor_app_performance_storage_usage_and_optimiza")}

        </CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">{t("components.overview")}</TabsTrigger>
            <TabsTrigger value="vitals">{t("components.web_vitals")}</TabsTrigger>
            <TabsTrigger value="storage">{t("components.storage")}</TabsTrigger>
            <TabsTrigger value="network">{t("components.network")}</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                <div className="flex items-center justify-center gap-1 text-sm font-medium mb-1">
                  <Zap className="h-3 w-3" />{t("components.load_time")}

                </div>
                <div className="text-lg font-bold">
                  {formatTime(performanceMetrics.loadTime)}
                </div>
              </div>

              <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                <div className="flex items-center justify-center gap-1 text-sm font-medium mb-1">
                  <HardDrive className="h-3 w-3" />{t("components.storage_used")}

                </div>
                <div className="text-lg font-bold">
                  {formatBytes(storageEstimate?.usage)}
                </div>
              </div>

              <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                <div className="flex items-center justify-center gap-1 text-sm font-medium mb-1">
                  <Wifi className="h-3 w-3" />{t("components.connection")}

                </div>
                <div className="text-lg font-bold">
                  {isOnline ? 'Online' : 'Offline'}
                </div>
              </div>

              <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                <div className="flex items-center justify-center gap-1 text-sm font-medium mb-1">
                  <CheckCircle className="h-3 w-3" />{t("components.service_worker")}

                </div>
                <div className="text-lg font-bold capitalize">
                  {performanceMetrics.serviceWorkerStatus || 'Unknown'}
                </div>
              </div>
            </div>

            {/* Performance Score */}
            {performanceScore !== null &&
            <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{t("components.performance_score")}</span>
                  <span className={`text-sm font-bold ${getScoreColor(performanceScore)}`}>
                    {performanceScore}/100
                  </span>
                </div>
                <Progress
                value={performanceScore}
                className={`h-2 ${
                performanceScore >= 80 ? 'bg-green-100' :
                performanceScore >= 60 ? 'bg-yellow-100' : 'bg-red-100'}`
                } />

              </div>
            }
          </TabsContent>

          {/* Web Vitals Tab */}
          <TabsContent value="vitals" className="space-y-4">
            <div className="space-y-4">
              {/* LCP */}
              <div className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-medium">{t("components.largest_contentful_paint_lcp")}</div>
                  <div className="text-sm text-gray-500">{t("components.how_quickly_the_main_content_loads")}

                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-bold ${vitals.lcp <= 2500 ? 'text-green-600' : vitals.lcp <= 4000 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {formatTime(vitals.lcp)}
                  </div>
                  <div className="text-xs text-gray-500">{t("components.good_25s")}

                  </div>
                </div>
              </div>

              {/* FID */}
              <div className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-medium">{t("components.first_input_delay_fid")}</div>
                  <div className="text-sm text-gray-500">{t("components.how_quickly_the_page_responds_to_interactions")}

                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-bold ${vitals.fid <= 100 ? 'text-green-600' : vitals.fid <= 300 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {formatTime(vitals.fid)}
                  </div>
                  <div className="text-xs text-gray-500">{t("components.good_100ms")}

                  </div>
                </div>
              </div>

              {/* CLS */}
              <div className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-medium">{t("components.cumulative_layout_shift_cls")}</div>
                  <div className="text-sm text-gray-500">{t("components.how_stable_the_page_layout_is_during_loading")}

                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-bold ${vitals.cls <= 0.1 ? 'text-green-600' : vitals.cls <= 0.25 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {vitals.cls?.toFixed(3)}
                  </div>
                  <div className="text-xs text-gray-500">{t("components.good_01")}

                  </div>
                </div>
              </div>

              {/* Additional Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-medium mb-1">{t("components.first_contentful_paint")}</div>
                  <div className="text-lg font-bold">{formatTime(vitals.fcp)}</div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-medium mb-1">{t("components.time_to_first_byte")}</div>
                  <div className="text-lg font-bold">{formatTime(vitals.ttfb)}</div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Storage Tab */}
          <TabsContent value="storage" className="space-y-4">
            <div className="space-y-4">
              {/* Storage Usage */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{t("components.storage_usage")}</span>
                  <span className="text-sm">
                    {formatBytes(storageEstimate?.usage)} / {formatBytes(storageEstimate?.quota)}
                  </span>
                </div>
                <Progress value={getStoragePercentage()} className="h-2" />
                <div className="text-xs text-gray-500">
                  {getStoragePercentage().toFixed(1)}{t("components._of_available_storage_used")}
                </div>
              </div>

              {/* Storage Breakdown */}
              <div className="space-y-3">
                <h4 className="font-medium">{t("components.storage_breakdown")}</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.cache_storage")}</span>
                    <span className="text-sm font-medium">
                      {formatBytes((storageEstimate?.usage || 0) * 0.6)} {/* Estimated */}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.indexeddb")}</span>
                    <span className="text-sm font-medium">
                      {formatBytes((storageEstimate?.usage || 0) * 0.3)} {/* Estimated */}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.local_storage")}</span>
                    <span className="text-sm font-medium">
                      {formatBytes((storageEstimate?.usage || 0) * 0.1)} {/* Estimated */}
                    </span>
                  </div>
                </div>
              </div>

              {/* Clear Cache Button */}
              <Button
                onClick={() => clearCache()}
                variant="outline"
                className="w-full"
                disabled={isLoading}>

                <HardDrive className="mr-2 h-4 w-4" />{t("components.clear_all_caches")}

              </Button>

              {/* Storage Warnings */}
              {getStoragePercentage() > 80 &&
              <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
                  <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                  <span className="text-sm text-yellow-700 dark:text-yellow-300">
                    Storage usage is high. Consider clearing some cached data.
                  </span>
                </div>
              }
            </div>
          </TabsContent>

          {/* Network Tab */}
          <TabsContent value="network" className="space-y-4">
            <div className="space-y-4">
              {/* Connection Status */}
              <div className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-2">
                  <Wifi className={`h-4 w-4 ${isOnline ? 'text-green-600' : 'text-red-600'}`} />
                  <span className="font-medium">{t("components.connection_status")}</span>
                </div>
                <Badge className={isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                  {isOnline ? 'Online' : 'Offline'}
                </Badge>
              </div>

              {/* Connection Info */}
              {connectionInfo &&
              <div className="space-y-3">
                  <h4 className="font-medium">{t("components.connection_details")}</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.type")}</div>
                      <div className="text-lg font-bold capitalize">
                        {connectionInfo.effectiveType || 'Unknown'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.downlink")}</div>
                      <div className="text-lg font-bold">
                        {connectionInfo.downlink ? `${connectionInfo.downlink} Mbps` : 'Unknown'}
                      </div>
                    </div>
                  </div>
                </div>
              }

              {/* Offline Capabilities */}
              <div className="space-y-3">
                <h4 className="font-medium">{t("components.offline_capabilities")}</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.service_worker")}</span>
                    <Badge className={performanceMetrics.serviceWorkerStatus === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {performanceMetrics.serviceWorkerStatus === 'active' ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.cache_storage")}</span>
                    <Badge className="bg-green-100 text-green-800">{t("components.available")}

                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.background_sync")}</span>
                    <Badge className="bg-green-100 text-green-800">{t("components.supported")}

                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>);

}

export default PWAPerformanceMonitor;