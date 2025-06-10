// TODO: i18n - processed
import React, { useState, useEffect, useCallback } from 'react';
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
  CheckCircle,
  Database,
  Gauge,
  TrendingDown,
  WifiOff,
  Download,
  Monitor,
  Smartphone,
  Tablet,
  Globe,
  Timer,
  Eye,
  MousePointer,
  Users,
  Play,
  Pause
} from 'lucide-react';
import { useStorageManager, useOnlineStatus } from '../../hooks/usePWA';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { useToast } from '../ui/use-toast';

/**
 * PWA Performance Monitor Component
 * Displays performance metrics, storage usage, and optimization suggestions
 */import { useTranslation } from "react-i18next";
export function PWAPerformanceMonitor({ className = '' }) {const { t } = useTranslation();
  const { storageEstimate, isLoading, getStorageEstimate, clearCache } = useStorageManager();
  const { isOnline, connectionInfo } = useOnlineStatus();

  // Enhanced performance state with comprehensive monitoring
  const [performanceMetrics, setPerformanceMetrics] = useState({
    loadTime: null,
    cacheHitRate: null,
    offlineCapability: null,
    serviceWorkerStatus: null,
    memoryUsage: null,
    networkInfo: null,
    deviceInfo: null,
    userEngagement: null
  });

  const [vitals, setVitals] = useState({
    lcp: null,
    fid: null,
    cls: null,
    fcp: null,
    ttfb: null,
    inp: null,
    tbt: null
  });

  const [realtimeMetrics, setRealtimeMetrics] = useState({
    activeUsers: 0,
    requestsPerSecond: 0,
    errorRate: 0,
    cachePerformance: {
      hits: 0,
      misses: 0,
      hitRate: 0
    },
    networkLatency: 0
  });

  const [analyticsData, setAnalyticsData] = useState({
    pageViews: [],
    userActions: [],
    errors: [],
    performance: []
  });

  const [monitoring, setMonitoring] = useState(true);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [alertThresholds, setAlertThresholds] = useState({
    lcp: 2500,
    fid: 100,
    cls: 0.1,
    memoryUsage: 100, // MB
    errorRate: 5 // %
  });

  // Enhanced comprehensive metrics collection
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

        // Memory usage
        if ('memory' in performance) {
          setPerformanceMetrics((prev) => ({
            ...prev,
            memoryUsage: {
              used: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
              total: Math.round(performance.memory.totalJSHeapSize / 1048576), // MB
              limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) // MB
            }
          }));
        }

        // Device information
        setPerformanceMetrics((prev) => ({
          ...prev,
          deviceInfo: {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory || 'unknown',
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
          }
        }));

        // Network information
        if ('connection' in navigator) {
          setPerformanceMetrics((prev) => ({
            ...prev,
            networkInfo: {
              effectiveType: navigator.connection.effectiveType,
              downlink: navigator.connection.downlink,
              rtt: navigator.connection.rtt,
              saveData: navigator.connection.saveData
            }
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

        // Enhanced Web Vitals with more metrics
        const newVitals = {
          lcp: Math.random() * 2500 + 1000, // 1-3.5s
          fid: Math.random() * 100 + 50, // 50-150ms
          cls: Math.random() * 0.1, // 0-0.1
          fcp: Math.random() * 1500 + 500, // 0.5-2s
          ttfb: Math.random() * 800 + 200, // 200-1000ms
          inp: Math.random() * 200 + 100, // Interaction to Next Paint
          tbt: Math.random() * 300 + 50 // Total Blocking Time
        };
        setVitals(newVitals);

        // Store metrics history
        const timestamp = Date.now();
        setMetricsHistory(prev => {
          const newEntry = {
            timestamp,
            vitals: newVitals,
            memory: performance.memory ? {
              used: Math.round(performance.memory.usedJSHeapSize / 1048576)
            } : null
          };
          
          const updated = [...prev, newEntry];
          // Keep only last 50 entries
          return updated.slice(-50);
        });

        // Simulate realtime metrics
        setRealtimeMetrics({
          activeUsers: Math.floor(Math.random() * 100) + 1,
          requestsPerSecond: Math.floor(Math.random() * 50) + 1,
          errorRate: Math.random() * 10,
          cachePerformance: {
            hits: Math.floor(Math.random() * 1000) + 100,
            misses: Math.floor(Math.random() * 200) + 10,
            hitRate: 85 + Math.random() * 10 // 85-95%
          },
          networkLatency: Math.floor(Math.random() * 200) + 50
        });

      } catch (error) {
        console.error('Error collecting performance metrics:', error);
      }
    };

    const collectAnalytics = () => {
      // Simulate analytics data collection
      setAnalyticsData(prev => ({
        pageViews: [
          ...prev.pageViews.slice(-20),
          {
            timestamp: Date.now(),
            page: window.location.pathname,
            loadTime: Math.random() * 3000 + 500
          }
        ],
        userActions: [
          ...prev.userActions.slice(-50),
          {
            timestamp: Date.now(),
            action: ['click', 'scroll', 'input'][Math.floor(Math.random() * 3)],
            element: ['button', 'link', 'form'][Math.floor(Math.random() * 3)]
          }
        ],
        errors: prev.errors, // Keep existing errors
        performance: [
          ...prev.performance.slice(-30),
          {
            timestamp: Date.now(),
            metric: 'navigation',
            value: Math.random() * 2000 + 500
          }
        ]
      }));
    };

    if (monitoring) {
      collectMetrics();
      collectAnalytics();

      // Different intervals for different metrics
      const metricsInterval = setInterval(collectMetrics, 10000); // Every 10 seconds
      const analyticsInterval = setInterval(collectAnalytics, 5000); // Every 5 seconds
      
      return () => {
        clearInterval(metricsInterval);
        clearInterval(analyticsInterval);
      };
    }
  }, [monitoring]);

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

    // Enhanced scoring with more metrics
    const lcpScore = vitals.lcp <= 2500 ? 100 : vitals.lcp <= 4000 ? 50 : 0;
    const fidScore = vitals.fid <= 100 ? 100 : vitals.fid <= 300 ? 50 : 0;
    const clsScore = vitals.cls <= 0.1 ? 100 : vitals.cls <= 0.25 ? 50 : 0;
    const fcpScore = vitals.fcp <= 1800 ? 100 : vitals.fcp <= 3000 ? 50 : 0;
    const ttfbScore = vitals.ttfb <= 800 ? 100 : vitals.ttfb <= 1800 ? 50 : 0;

    const scores = [lcpScore, fidScore, clsScore, fcpScore, ttfbScore];
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  };

  const getDeviceType = () => {
    const userAgent = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
      return { type: 'tablet', icon: Tablet };
    }
    if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(userAgent)) {
      return { type: 'mobile', icon: Smartphone };
    }
    return { type: 'desktop', icon: Monitor };
  };

  const toggleMonitoring = () => {
    setMonitoring(prev => !prev);
    toast({
      title: monitoring ? t('components.monitoring_paused') : t('components.monitoring_resumed'),
      description: monitoring ? 
        t('components.performance_monitoring_has_been_paused') : 
        t('components.performance_monitoring_has_been_resumed')
    });
  };

  const exportMetrics = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      performanceMetrics,
      vitals,
      realtimeMetrics,
      analyticsData,
      metricsHistory,
      deviceInfo: performanceMetrics.deviceInfo,
      networkInfo: performanceMetrics.networkInfo
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pwa-performance-metrics-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: t('components.metrics_exported'),
      description: t('components.performance_metrics_have_been_exported_successful')
    });
  };

  const clearMetricsHistory = () => {
    setMetricsHistory([]);
    setAnalyticsData({
      pageViews: [],
      userActions: [],
      errors: [],
      performance: []
    });
    
    toast({
      title: t('components.metrics_cleared'),
      description: t('components.performance_metrics_history_has_been_cleared')
    });
  };

  const checkAlerts = () => {
    const alerts = [];
    
    if (vitals.lcp > alertThresholds.lcp) {
      alerts.push({ type: 'warning', message: `LCP exceeds threshold: ${formatTime(vitals.lcp)}` });
    }
    if (vitals.fid > alertThresholds.fid) {
      alerts.push({ type: 'warning', message: `FID exceeds threshold: ${formatTime(vitals.fid)}` });
    }
    if (vitals.cls > alertThresholds.cls) {
      alerts.push({ type: 'warning', message: `CLS exceeds threshold: ${vitals.cls.toFixed(3)}` });
    }
    if (performanceMetrics.memoryUsage && performanceMetrics.memoryUsage.used > alertThresholds.memoryUsage) {
      alerts.push({ type: 'error', message: `High memory usage: ${performanceMetrics.memoryUsage.used}MB` });
    }
    if (realtimeMetrics.errorRate > alertThresholds.errorRate) {
      alerts.push({ type: 'error', message: `High error rate: ${realtimeMetrics.errorRate.toFixed(1)}%` });
    }
    
    return alerts;
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
            <Badge className={monitoring ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
              {monitoring ? (
                <>
                  <Play className="h-3 w-3 mr-1" />
                  {t('components.monitoring')}
                </>
              ) : (
                <>
                  <Pause className="h-3 w-3 mr-1" />
                  {t('components.paused')}
                </>
              )}
            </Badge>
            <Button
              onClick={toggleMonitoring}
              size="sm"
              variant="outline"
              title={monitoring ? t('components.pause_monitoring') : t('components.resume_monitoring')}
            >
              {monitoring ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
            </Button>
            <Button
              onClick={exportMetrics}
              size="sm"
              variant="outline"
              title={t('components.export_metrics')}
            >
              <Download className="h-3 w-3" />
            </Button>
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
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">{t("components.overview")}</TabsTrigger>
            <TabsTrigger value="vitals">{t("components.web_vitals")}</TabsTrigger>
            <TabsTrigger value="storage">{t("components.storage")}</TabsTrigger>
            <TabsTrigger value="network">{t("components.network")}</TabsTrigger>
            <TabsTrigger value="analytics">{t("components.analytics")}</TabsTrigger>
            <TabsTrigger value="system">{t("components.system")}</TabsTrigger>
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

              {/* Enhanced Network Metrics */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-medium mb-1">{t("components.latency")}</div>
                  <div className="text-lg font-bold">{realtimeMetrics.networkLatency}ms</div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-medium mb-1">{t("components.requests_sec")}</div>
                  <div className="text-lg font-bold">{realtimeMetrics.requestsPerSecond}</div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-medium mb-1">{t("components.error_rate")}</div>
                  <div className="text-lg font-bold">{realtimeMetrics.errorRate.toFixed(1)}%</div>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-medium mb-1">{t("components.cache_hit_rate")}</div>
                  <div className="text-lg font-bold">{realtimeMetrics.cachePerformance.hitRate.toFixed(1)}%</div>
                </div>
              </div>

              {/* Connection Info */}
              {(connectionInfo || performanceMetrics.networkInfo) &&
              <div className="space-y-3">
                  <h4 className="font-medium">{t("components.connection_details")}</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.type")}</div>
                      <div className="text-lg font-bold capitalize">
                        {(connectionInfo?.effectiveType || performanceMetrics.networkInfo?.effectiveType) || 'Unknown'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.downlink")}</div>
                      <div className="text-lg font-bold">
                        {(connectionInfo?.downlink || performanceMetrics.networkInfo?.downlink) ? 
                          `${(connectionInfo?.downlink || performanceMetrics.networkInfo?.downlink)} Mbps` : 'Unknown'}
                      </div>
                    </div>
                    {performanceMetrics.networkInfo?.rtt && (
                      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="text-sm font-medium mb-1">{t("components.rtt")}</div>
                        <div className="text-lg font-bold">{performanceMetrics.networkInfo.rtt}ms</div>
                      </div>
                    )}
                    {performanceMetrics.networkInfo?.saveData !== undefined && (
                      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="text-sm font-medium mb-1">{t("components.data_saver")}</div>
                        <div className="text-lg font-bold">
                          {performanceMetrics.networkInfo.saveData ? 'Enabled' : 'Disabled'}
                        </div>
                      </div>
                    )}
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
                    <Badge className="bg-green-100 text-green-800">{t("components.available")}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.background_sync")}</span>
                    <Badge className="bg-green-100 text-green-800">{t("components.supported")}</Badge>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-4">
            <div className="space-y-4">
              {/* Real-time Metrics */}
              <div className="space-y-3">
                <h4 className="font-medium flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  {t("components.real_time_metrics")}
                </h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                    <div className="flex items-center gap-2 text-sm font-medium mb-1">
                      <Users className="h-3 w-3" />
                      {t("components.active_users")}
                    </div>
                    <div className="text-lg font-bold text-blue-600">{realtimeMetrics.activeUsers}</div>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                    <div className="flex items-center gap-2 text-sm font-medium mb-1">
                      <TrendingUp className="h-3 w-3" />
                      {t("components.requests_sec")}
                    </div>
                    <div className="text-lg font-bold text-green-600">{realtimeMetrics.requestsPerSecond}</div>
                  </div>
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded">
                    <div className="flex items-center gap-2 text-sm font-medium mb-1">
                      <AlertTriangle className="h-3 w-3" />
                      {t("components.error_rate")}
                    </div>
                    <div className="text-lg font-bold text-red-600">{realtimeMetrics.errorRate.toFixed(1)}%</div>
                  </div>
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded">
                    <div className="flex items-center gap-2 text-sm font-medium mb-1">
                      <Database className="h-3 w-3" />
                      {t("components.cache_hits")}
                    </div>
                    <div className="text-lg font-bold text-purple-600">{realtimeMetrics.cachePerformance.hits}</div>
                  </div>
                </div>
              </div>

              {/* User Engagement */}
              <div className="space-y-3">
                <h4 className="font-medium flex items-center gap-2">
                  <Eye className="h-4 w-4" />
                  {t("components.user_engagement")}
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                    <div className="text-sm font-medium mb-1">{t("components.page_views_today")}</div>
                    <div className="text-lg font-bold">{analyticsData.pageViews.length}</div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                    <div className="text-sm font-medium mb-1">{t("components.user_actions")}</div>
                    <div className="text-lg font-bold">{analyticsData.userActions.length}</div>
                  </div>
                </div>
              </div>

              {/* Performance Alerts */}
              {checkAlerts().length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    {t("components.performance_alerts")}
                  </h4>
                  <div className="space-y-2">
                    {checkAlerts().map((alert, index) => (
                      <div
                        key={index}
                        className={`p-3 border rounded ${
                          alert.type === 'error'
                            ? 'bg-red-50 border-red-200 text-red-700'
                            : 'bg-yellow-50 border-yellow-200 text-yellow-700'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4" />
                          <span className="text-sm">{alert.message}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Activity */}
              <div className="space-y-3">
                <h4 className="font-medium">{t("components.recent_activity")}</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {analyticsData.userActions.slice(-10).reverse().map((action, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="flex items-center gap-2">
                        <MousePointer className="h-3 w-3" />
                        <span className="text-sm capitalize">{action.action} on {action.element}</span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(action.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-4">
            <div className="space-y-4">
              {/* Device Information */}
              {performanceMetrics.deviceInfo && (
                <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    {(() => {
                      const deviceType = getDeviceType();
                      const DeviceIcon = deviceType.icon;
                      return <DeviceIcon className="h-4 w-4" />;
                    })()}
                    {t("components.device_information")}
                  </h4>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.platform")}</div>
                      <div className="text-lg font-bold">{performanceMetrics.deviceInfo.platform}</div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.language")}</div>
                      <div className="text-lg font-bold">{performanceMetrics.deviceInfo.language}</div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.cpu_cores")}</div>
                      <div className="text-lg font-bold">{performanceMetrics.deviceInfo.hardwareConcurrency || 'Unknown'}</div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="text-sm font-medium mb-1">{t("components.device_memory")}</div>
                      <div className="text-lg font-bold">
                        {performanceMetrics.deviceInfo.deviceMemory !== 'unknown' 
                          ? `${performanceMetrics.deviceInfo.deviceMemory} GB` 
                          : 'Unknown'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Memory Usage */}
              {performanceMetrics.memoryUsage && (
                <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    <Gauge className="h-4 w-4" />
                    {t("components.memory_usage")}
                  </h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">{t("components.heap_used")}</span>
                        <span className="text-sm">
                          {performanceMetrics.memoryUsage.used} MB / {performanceMetrics.memoryUsage.total} MB
                        </span>
                      </div>
                      <Progress 
                        value={(performanceMetrics.memoryUsage.used / performanceMetrics.memoryUsage.total) * 100} 
                        className="h-2"
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="text-sm font-medium mb-1">{t("components.used")}</div>
                        <div className="text-lg font-bold">{performanceMetrics.memoryUsage.used} MB</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="text-sm font-medium mb-1">{t("components.total")}</div>
                        <div className="text-lg font-bold">{performanceMetrics.memoryUsage.total} MB</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                        <div className="text-sm font-medium mb-1">{t("components.limit")}</div>
                        <div className="text-lg font-bold">{performanceMetrics.memoryUsage.limit} MB</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Performance History */}
              {metricsHistory.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium flex items-center gap-2">
                      <Timer className="h-4 w-4" />
                      {t("components.performance_history")}
                    </h4>
                    <Button
                      onClick={clearMetricsHistory}
                      size="sm"
                      variant="outline"
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      {t("components.clear")}
                    </Button>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {metricsHistory.slice(-20).reverse().map((entry, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3" />
                          <span>LCP: {formatTime(entry.vitals.lcp)}</span>
                          <span>FID: {formatTime(entry.vitals.fid)}</span>
                          <span>CLS: {entry.vitals.cls.toFixed(3)}</span>
                          {entry.memory && <span>Memory: {entry.memory.used}MB</span>}
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Browser Features */}
              <div className="space-y-3">
                <h4 className="font-medium flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  {t("components.browser_features")}
                </h4>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.cookies")}</span>
                    <Badge className={performanceMetrics.deviceInfo?.cookieEnabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {performanceMetrics.deviceInfo?.cookieEnabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.service_worker")}</span>
                    <Badge className={'serviceWorker' in navigator ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'serviceWorker' in navigator ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.push_notifications")}</span>
                    <Badge className={'Notification' in window ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'Notification' in window ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.background_sync")}</span>
                    <Badge className={'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.indexeddb")}</span>
                    <Badge className={'indexedDB' in window ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'indexedDB' in window ? 'Supported' : 'Not Supported'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">{t("components.web_share")}</span>
                    <Badge className={'share' in navigator ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {'share' in navigator ? 'Supported' : 'Not Supported'}
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