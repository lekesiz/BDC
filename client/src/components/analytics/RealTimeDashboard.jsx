// Real-Time Analytics Dashboard
// Live data streaming with beneficiary progress tracking and system monitoring

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  Users,
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Zap,
  Globe,
  Server,
  Cpu,
  HardDrive,
  Wifi,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  Settings,
  RefreshCw,
  Bell,
  BellOff
} from 'lucide-react';
import { useAnalytics } from '@/contexts/AnalyticsContext';
import { useSocket } from '@/contexts/SocketContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BaseChart, 
  TimeSeriesChart, 
  MetricCard, 
  ChartGrid 
} from './charts/ChartLibrary';
import { format } from 'date-fns';

const RealTimeDashboard = () => {
  const { 
    realtimeMetrics, 
    liveUpdates, 
    systemHealth, 
    activeUsers, 
    activeSessions,
    subscribe,
    refreshAll,
    isLoading
  } = useAnalytics();
  
  const { connected } = useSocket();
  
  // Dashboard state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showNotifications, setShowNotifications] = useState(true);
  const [selectedMetrics, setSelectedMetrics] = useState(new Set(['users', 'sessions', 'performance', 'health']));
  const [timeRange, setTimeRange] = useState('24h');
  
  // Real-time data subscriptions
  useEffect(() => {
    const unsubscribers = [
      subscribe('beneficiary_progress', handleBeneficiaryUpdate),
      subscribe('trainer_activity', handleTrainerUpdate),
      subscribe('system_metrics', handleSystemUpdate),
      subscribe('performance_metrics', handlePerformanceUpdate)
    ];
    
    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      refreshAll();
    }, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, [autoRefresh, refreshAll]);

  // Event handlers for real-time updates
  const handleBeneficiaryUpdate = (data) => {
    if (showNotifications) {
      // Handle beneficiary progress notifications
    }
  };

  const handleTrainerUpdate = (data) => {
    if (showNotifications) {
      // Handle trainer activity notifications
    }
  };

  const handleSystemUpdate = (data) => {
    if (showNotifications && data.alert) {
      // Handle system alerts
    }
  };

  const handlePerformanceUpdate = (data) => {
    if (showNotifications && data.degradation) {
      // Handle performance degradation alerts
    }
  };

  // Toggle metric visibility
  const toggleMetric = (metric) => {
    setSelectedMetrics(prev => {
      const newSet = new Set(prev);
      if (newSet.has(metric)) {
        newSet.delete(metric);
      } else {
        newSet.add(metric);
      }
      return newSet;
    });
  };

  // Metric cards data
  const metricCards = useMemo(() => [
    {
      id: 'users',
      title: 'Active Users',
      value: activeUsers || 0,
      change: realtimeMetrics.userGrowth || 0,
      changeType: (realtimeMetrics.userGrowth || 0) >= 0 ? 'positive' : 'negative',
      icon: Users,
      color: 'blue'
    },
    {
      id: 'sessions',
      title: 'Live Sessions',
      value: activeSessions || 0,
      change: realtimeMetrics.sessionGrowth || 0,
      changeType: (realtimeMetrics.sessionGrowth || 0) >= 0 ? 'positive' : 'negative',
      icon: Activity,
      color: 'green'
    },
    {
      id: 'performance',
      title: 'System Performance',
      value: `${systemHealth.performance || 95}%`,
      change: systemHealth.performanceChange || 0,
      changeType: (systemHealth.performanceChange || 0) >= 0 ? 'positive' : 'negative',
      icon: Zap,
      color: systemHealth.performance > 90 ? 'green' : systemHealth.performance > 70 ? 'yellow' : 'red'
    },
    {
      id: 'uptime',
      title: 'System Uptime',
      value: `${systemHealth.uptime || 99.9}%`,
      change: systemHealth.uptimeChange || 0,
      changeType: 'positive',
      icon: Server,
      color: 'purple'
    }
  ], [activeUsers, activeSessions, realtimeMetrics, systemHealth]);

  // Time series data for charts
  const timeSeriesData = useMemo(() => {
    const labels = Array.from({ length: 24 }, (_, i) => 
      format(new Date(Date.now() - (23 - i) * 60 * 60 * 1000), 'HH:mm')
    );
    
    return {
      labels,
      datasets: [
        {
          label: 'Active Users',
          data: realtimeMetrics.userTimeSeries || Array(24).fill(0).map(() => Math.floor(Math.random() * 100) + 50),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        },
        {
          label: 'Active Sessions',
          data: realtimeMetrics.sessionTimeSeries || Array(24).fill(0).map(() => Math.floor(Math.random() * 50) + 20),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4
        }
      ]
    };
  }, [realtimeMetrics]);

  // System health indicators
  const systemHealthIndicators = [
    {
      name: 'CPU Usage',
      value: systemHealth.cpu || 45,
      threshold: 80,
      icon: Cpu,
      color: (systemHealth.cpu || 45) > 80 ? 'red' : (systemHealth.cpu || 45) > 60 ? 'yellow' : 'green'
    },
    {
      name: 'Memory Usage',
      value: systemHealth.memory || 60,
      threshold: 85,
      icon: HardDrive,
      color: (systemHealth.memory || 60) > 85 ? 'red' : (systemHealth.memory || 60) > 70 ? 'yellow' : 'green'
    },
    {
      name: 'Network',
      value: systemHealth.network || 95,
      threshold: 90,
      icon: Wifi,
      color: (systemHealth.network || 95) < 90 ? 'red' : 'green'
    },
    {
      name: 'Database',
      value: systemHealth.database || 88,
      threshold: 85,
      icon: Server,
      color: (systemHealth.database || 88) < 85 ? 'red' : 'green'
    }
  ];

  // Live updates component
  const LiveUpdates = () => (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center">
          <Activity className="w-4 h-4 mr-2" />
          Live Updates
        </h3>
        <Badge variant={connected ? 'default' : 'destructive'}>
          {connected ? 'Connected' : 'Disconnected'}
        </Badge>
      </div>
      
      <div className="space-y-2 max-h-64 overflow-y-auto">
        <AnimatePresence>
          {liveUpdates.slice(0, 10).map((update) => (
            <motion.div
              key={update.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
            >
              <div className="flex-1">
                <p className="text-sm font-medium">{update.message}</p>
                <p className="text-xs text-gray-500">
                  {format(update.timestamp, 'HH:mm:ss')}
                </p>
              </div>
              <Badge variant="outline" className="text-xs">
                {update.type}
              </Badge>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {liveUpdates.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No recent updates</p>
          </div>
        )}
      </div>
    </Card>
  );

  // System health component
  const SystemHealthPanel = () => (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center">
          <Server className="w-4 h-4 mr-2" />
          System Health
        </h3>
        <div className="flex items-center space-x-2">
          {systemHealth.status === 'healthy' && (
            <CheckCircle className="w-4 h-4 text-green-500" />
          )}
          {systemHealth.status === 'warning' && (
            <AlertTriangle className="w-4 h-4 text-yellow-500" />
          )}
          {systemHealth.status === 'critical' && (
            <XCircle className="w-4 h-4 text-red-500" />
          )}
          <Badge variant={
            systemHealth.status === 'healthy' ? 'default' :
            systemHealth.status === 'warning' ? 'secondary' : 'destructive'
          }>
            {systemHealth.status || 'healthy'}
          </Badge>
        </div>
      </div>
      
      <div className="space-y-4">
        {systemHealthIndicators.map((indicator) => (
          <div key={indicator.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <indicator.icon className="w-4 h-4 mr-2" />
                <span className="text-sm font-medium">{indicator.name}</span>
              </div>
              <span className={`text-sm font-bold ${
                indicator.color === 'red' ? 'text-red-600' :
                indicator.color === 'yellow' ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {indicator.value}%
              </span>
            </div>
            <Progress 
              value={indicator.value} 
              className={`h-2 ${
                indicator.color === 'red' ? 'bg-red-100' :
                indicator.color === 'yellow' ? 'bg-yellow-100' : 'bg-green-100'
              }`}
            />
          </div>
        ))}
      </div>
    </Card>
  );

  return (
    <div className={`space-y-6 ${isFullscreen ? 'fixed inset-0 z-50 bg-white p-6 overflow-auto' : ''}`}>
      {/* Dashboard Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Real-Time Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Live analytics and system monitoring • Last updated: {format(new Date(), 'HH:mm:ss')}
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Switch
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
              id="auto-refresh"
            />
            <label htmlFor="auto-refresh" className="text-sm font-medium">
              Auto Refresh
            </label>
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              checked={showNotifications}
              onCheckedChange={setShowNotifications}
              id="notifications"
            />
            {showNotifications ? (
              <Bell className="w-4 h-4" />
            ) : (
              <BellOff className="w-4 h-4" />
            )}
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={refreshAll}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Connection Status Banner */}
      {!connected && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
        >
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mr-3" />
            <div>
              <p className="font-medium text-yellow-800">Real-time connection lost</p>
              <p className="text-sm text-yellow-700">
                Some data may not be up to date. Trying to reconnect...
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((metric) => (
          selectedMetrics.has(metric.id) && (
            <MetricCard
              key={metric.id}
              title={metric.title}
              value={metric.value}
              change={metric.change}
              changeType={metric.changeType}
              icon={metric.icon}
              color={metric.color}
              loading={isLoading}
            />
          )
        ))}
      </div>

      {/* Main Charts and Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Time Series Chart */}
        <div className="lg:col-span-2">
          <TimeSeriesChart
            data={timeSeriesData}
            title="User Activity Over Time"
            description="Real-time user and session activity for the last 24 hours"
            height={400}
          />
        </div>
        
        {/* Live Updates Panel */}
        <div>
          <LiveUpdates />
        </div>
      </div>

      {/* System Health and Additional Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemHealthPanel />
        
        {/* Additional Metrics Panel */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center">
              <TrendingUp className="w-4 h-4 mr-2" />
              Performance Metrics
            </h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Response Time</span>
              <span className="text-sm font-bold text-blue-600">
                {realtimeMetrics.responseTime || '120'}ms
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Throughput</span>
              <span className="text-sm font-bold text-green-600">
                {realtimeMetrics.throughput || '1,250'} req/min
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Error Rate</span>
              <span className="text-sm font-bold text-red-600">
                {realtimeMetrics.errorRate || '0.1'}%
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Data Transfer</span>
              <span className="text-sm font-bold text-purple-600">
                {realtimeMetrics.dataTransfer || '45.2'} MB/s
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Metric Selection Controls */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold flex items-center">
            <Settings className="w-4 h-4 mr-2" />
            Dashboard Configuration
          </h3>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {metricCards.map((metric) => (
            <Button
              key={metric.id}
              variant={selectedMetrics.has(metric.id) ? 'default' : 'outline'}
              size="sm"
              onClick={() => toggleMetric(metric.id)}
              className="flex items-center"
            >
              {selectedMetrics.has(metric.id) ? (
                <Eye className="w-3 h-3 mr-1" />
              ) : (
                <EyeOff className="w-3 h-3 mr-1" />
              )}
              {metric.title}
            </Button>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default RealTimeDashboard;