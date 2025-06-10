// System Health Monitoring Dashboard
// Real-time system monitoring with alert notifications and performance tracking

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Server,
  Database,
  Cpu,
  HardDrive,
  Wifi,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Zap,
  Globe,
  Monitor,
  Clock,
  TrendingUp,
  TrendingDown,
  Bell,
  BellOff,
  Settings,
  RefreshCw,
  Download,
  Eye,
  EyeOff,
  ChevronRight,
  Calendar,
  Target,
  Gauge
} from 'lucide-react';
import { useAnalytics } from '@/contexts/AnalyticsContext';
import { useSocket } from '@/contexts/SocketContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  BaseChart, 
  TimeSeriesChart, 
  MetricCard 
} from './charts/ChartLibrary';
import { format, subHours, subMinutes } from 'date-fns';

const SystemHealthMonitoring = () => {
  const { 
    systemHealth, 
    realtimeMetrics, 
    subscribe, 
    refreshAll,
    isLoading 
  } = useAnalytics();
  
  const { connected } = useSocket();

  // State management
  const [alerts, setAlerts] = useState([]);
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [visibleMetrics, setVisibleMetrics] = useState(new Set(['cpu', 'memory', 'network', 'database']));
  const [systemMetrics, setSystemMetrics] = useState({});
  const [performanceHistory, setPerformanceHistory] = useState({});

  // Alert types configuration
  const alertThresholds = {
    cpu: { warning: 70, critical: 85 },
    memory: { warning: 75, critical: 90 },
    network: { warning: 10, critical: 5 }, // For network, lower is worse
    database: { warning: 200, critical: 500 }, // Response time in ms
    uptime: { warning: 99.5, critical: 99.0 }
  };

  // Subscribe to system health updates
  useEffect(() => {
    const unsubscribers = [
      subscribe('system_health', handleSystemHealthUpdate),
      subscribe('performance_alert', handlePerformanceAlert),
      subscribe('system_metric_update', handleMetricUpdate)
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
    }, 15000); // Refresh every 15 seconds for system health

    return () => clearInterval(interval);
  }, [autoRefresh, refreshAll]);

  // Handle system health updates
  const handleSystemHealthUpdate = (data) => {
    setSystemMetrics(prev => ({ ...prev, ...data.metrics }));
    
    // Check for threshold violations
    checkThresholds(data.metrics);
  };

  // Handle performance alerts
  const handlePerformanceAlert = (alert) => {
    if (alertsEnabled) {
      addAlert(alert);
    }
  };

  // Handle metric updates
  const handleMetricUpdate = (data) => {
    setPerformanceHistory(prev => ({
      ...prev,
      [data.metric]: {
        ...prev[data.metric],
        data: [...(prev[data.metric]?.data || []), data.value].slice(-50), // Keep last 50 points
        timestamp: [...(prev[data.metric]?.timestamp || []), new Date()].slice(-50)
      }
    }));
  };

  // Check alert thresholds
  const checkThresholds = (metrics) => {
    Object.entries(metrics).forEach(([metric, value]) => {
      const threshold = alertThresholds[metric];
      if (!threshold) return;

      let alertLevel = null;
      let message = '';

      if (metric === 'network') {
        // For network, lower values are worse
        if (value <= threshold.critical) {
          alertLevel = 'critical';
          message = `Network performance critical: ${value}% availability`;
        } else if (value <= threshold.warning) {
          alertLevel = 'warning';
          message = `Network performance warning: ${value}% availability`;
        }
      } else if (metric === 'database') {
        // For database response time, higher is worse
        if (value >= threshold.critical) {
          alertLevel = 'critical';
          message = `Database response time critical: ${value}ms`;
        } else if (value >= threshold.warning) {
          alertLevel = 'warning';
          message = `Database response time warning: ${value}ms`;
        }
      } else {
        // For CPU, memory, etc., higher is worse
        if (value >= threshold.critical) {
          alertLevel = 'critical';
          message = `${metric.toUpperCase()} usage critical: ${value}%`;
        } else if (value >= threshold.warning) {
          alertLevel = 'warning';
          message = `${metric.toUpperCase()} usage warning: ${value}%`;
        }
      }

      if (alertLevel) {
        addAlert({
          id: Date.now(),
          level: alertLevel,
          metric,
          message,
          value,
          timestamp: new Date()
        });
      }
    });
  };

  // Add alert
  const addAlert = (alert) => {
    setAlerts(prev => [alert, ...prev.slice(0, 49)]); // Keep last 50 alerts
  };

  // Clear alerts
  const clearAlerts = () => {
    setAlerts([]);
  };

  // Toggle metric visibility
  const toggleMetric = (metric) => {
    setVisibleMetrics(prev => {
      const newSet = new Set(prev);
      if (newSet.has(metric)) {
        newSet.delete(metric);
      } else {
        newSet.add(metric);
      }
      return newSet;
    });
  };

  // System status calculation
  const systemStatus = useMemo(() => {
    const metrics = { ...systemHealth, ...systemMetrics };
    
    const criticalIssues = Object.entries(metrics).filter(([key, value]) => {
      const threshold = alertThresholds[key];
      if (!threshold) return false;
      
      if (key === 'network') return value <= threshold.critical;
      if (key === 'database') return value >= threshold.critical;
      return value >= threshold.critical;
    }).length;

    const warningIssues = Object.entries(metrics).filter(([key, value]) => {
      const threshold = alertThresholds[key];
      if (!threshold) return false;
      
      if (key === 'network') return value <= threshold.warning && value > threshold.critical;
      if (key === 'database') return value >= threshold.warning && value < threshold.critical;
      return value >= threshold.warning && value < threshold.critical;
    }).length;

    if (criticalIssues > 0) return { status: 'critical', color: 'red', icon: XCircle };
    if (warningIssues > 0) return { status: 'warning', color: 'yellow', icon: AlertTriangle };
    return { status: 'healthy', color: 'green', icon: CheckCircle };
  }, [systemHealth, systemMetrics]);

  // Metric cards data
  const metricCards = useMemo(() => {
    const metrics = { ...systemHealth, ...systemMetrics };
    
    return [
      {
        id: 'cpu',
        title: 'CPU Usage',
        value: `${metrics.cpu || 0}%`,
        threshold: alertThresholds.cpu,
        current: metrics.cpu || 0,
        icon: Cpu,
        color: (metrics.cpu || 0) > 85 ? 'red' : (metrics.cpu || 0) > 70 ? 'yellow' : 'green'
      },
      {
        id: 'memory',
        title: 'Memory Usage',
        value: `${metrics.memory || 0}%`,
        threshold: alertThresholds.memory,
        current: metrics.memory || 0,
        icon: HardDrive,
        color: (metrics.memory || 0) > 90 ? 'red' : (metrics.memory || 0) > 75 ? 'yellow' : 'green'
      },
      {
        id: 'network',
        title: 'Network Health',
        value: `${metrics.network || 100}%`,
        threshold: alertThresholds.network,
        current: metrics.network || 100,
        icon: Wifi,
        color: (metrics.network || 100) < 5 ? 'red' : (metrics.network || 100) < 10 ? 'yellow' : 'green'
      },
      {
        id: 'database',
        title: 'Database Response',
        value: `${metrics.database || 50}ms`,
        threshold: alertThresholds.database,
        current: metrics.database || 50,
        icon: Database,
        color: (metrics.database || 50) > 500 ? 'red' : (metrics.database || 50) > 200 ? 'yellow' : 'green'
      }
    ];
  }, [systemHealth, systemMetrics]);

  // Performance trend data
  const performanceTrendData = useMemo(() => {
    const now = new Date();
    const timePoints = Array.from({ length: 20 }, (_, i) => 
      format(subMinutes(now, (19 - i) * 3), 'HH:mm')
    );

    return {
      labels: timePoints,
      datasets: [
        {
          label: 'CPU Usage',
          data: performanceHistory.cpu?.data?.slice(-20) || Array(20).fill(0).map(() => Math.random() * 80 + 10),
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4
        },
        {
          label: 'Memory Usage',
          data: performanceHistory.memory?.data?.slice(-20) || Array(20).fill(0).map(() => Math.random() * 70 + 20),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        },
        {
          label: 'Network Health',
          data: performanceHistory.network?.data?.slice(-20) || Array(20).fill(0).map(() => Math.random() * 20 + 80),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4
        }
      ]
    };
  }, [performanceHistory]);

  // Alert component
  const AlertItem = ({ alert, onDismiss }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={`p-4 rounded-lg border-l-4 ${
        alert.level === 'critical' 
          ? 'bg-red-50 border-red-500' 
          : 'bg-yellow-50 border-yellow-500'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          {alert.level === 'critical' ? (
            <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" />
          )}
          <div>
            <p className={`font-medium ${
              alert.level === 'critical' ? 'text-red-800' : 'text-yellow-800'
            }`}>
              {alert.message}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {format(alert.timestamp, 'MMM dd, HH:mm:ss')}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDismiss(alert.id)}
          className="text-gray-400 hover:text-gray-600"
        >
          ✕
        </Button>
      </div>
    </motion.div>
  );

  // Service status component
  const ServiceStatus = ({ name, status, icon: Icon, description }) => (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-full ${
          status === 'healthy' ? 'bg-green-100' :
          status === 'warning' ? 'bg-yellow-100' : 'bg-red-100'
        }`}>
          <Icon className={`w-4 h-4 ${
            status === 'healthy' ? 'text-green-600' :
            status === 'warning' ? 'text-yellow-600' : 'text-red-600'
          }`} />
        </div>
        <div>
          <p className="font-medium">{name}</p>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
      </div>
      <Badge variant={
        status === 'healthy' ? 'default' :
        status === 'warning' ? 'secondary' : 'destructive'
      }>
        {status}
      </Badge>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Health Monitoring</h1>
          <p className="text-gray-600 mt-1">
            Real-time system performance and health monitoring
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
              checked={alertsEnabled}
              onCheckedChange={setAlertsEnabled}
              id="alerts"
            />
            {alertsEnabled ? (
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
        </div>
      </div>

      {/* System Status Banner */}
      <Card className={`p-4 border-l-4 ${
        systemStatus.status === 'healthy' ? 'border-green-500 bg-green-50' :
        systemStatus.status === 'warning' ? 'border-yellow-500 bg-yellow-50' :
        'border-red-500 bg-red-50'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <systemStatus.icon className={`w-6 h-6 ${
              systemStatus.status === 'healthy' ? 'text-green-600' :
              systemStatus.status === 'warning' ? 'text-yellow-600' :
              'text-red-600'
            }`} />
            <div>
              <h2 className={`font-semibold ${
                systemStatus.status === 'healthy' ? 'text-green-800' :
                systemStatus.status === 'warning' ? 'text-yellow-800' :
                'text-red-800'
              }`}>
                System Status: {systemStatus.status.charAt(0).toUpperCase() + systemStatus.status.slice(1)}
              </h2>
              <p className="text-sm text-gray-600">
                Last updated: {format(new Date(), 'HH:mm:ss')} • Connection: {connected ? 'Connected' : 'Disconnected'}
              </p>
            </div>
          </div>
          
          {alerts.length > 0 && (
            <Badge variant="destructive">
              {alerts.length} active alert{alerts.length !== 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      </Card>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((metric) => (
          visibleMetrics.has(metric.id) && (
            <Card key={metric.id} className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <metric.icon className="w-5 h-5 text-gray-600" />
                  <h3 className="font-medium">{metric.title}</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleMetric(metric.id)}
                >
                  <EyeOff className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold">{metric.value}</span>
                  <Badge variant={
                    metric.color === 'green' ? 'default' :
                    metric.color === 'yellow' ? 'secondary' : 'destructive'
                  }>
                    {metric.color === 'green' ? 'Normal' :
                     metric.color === 'yellow' ? 'Warning' : 'Critical'}
                  </Badge>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Current</span>
                    <span>{metric.current}{metric.id === 'database' ? 'ms' : '%'}</span>
                  </div>
                  <Progress 
                    value={metric.id === 'database' ? 
                      Math.min((metric.current / 1000) * 100, 100) : 
                      metric.current
                    } 
                    className={`h-2 ${
                      metric.color === 'red' ? 'bg-red-100' :
                      metric.color === 'yellow' ? 'bg-yellow-100' : 'bg-green-100'
                    }`}
                  />
                </div>
              </div>
            </Card>
          )
        ))}
      </div>

      {/* Tabs for detailed views */}
      <Tabs defaultValue="performance" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="alerts">Alerts ({alerts.length})</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-6">
          <TimeSeriesChart
            data={performanceTrendData}
            title="System Performance Trends"
            description="Real-time performance metrics over the last hour"
            height={400}
          />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="p-4">
              <h3 className="font-semibold mb-4">CPU Load Distribution</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">1 min avg</span>
                  <span className="font-medium">{systemMetrics.cpuLoad1min || '1.2'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">5 min avg</span>
                  <span className="font-medium">{systemMetrics.cpuLoad5min || '1.5'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">15 min avg</span>
                  <span className="font-medium">{systemMetrics.cpuLoad15min || '1.8'}</span>
                </div>
              </div>
            </Card>
            
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Memory Breakdown</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">Used</span>
                  <span className="font-medium">{systemMetrics.memoryUsed || '4.2'} GB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Free</span>
                  <span className="font-medium">{systemMetrics.memoryFree || '3.8'} GB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Cache</span>
                  <span className="font-medium">{systemMetrics.memoryCache || '2.1'} GB</span>
                </div>
              </div>
            </Card>
            
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Network Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">Rx</span>
                  <span className="font-medium">{systemMetrics.networkRx || '125'} MB/s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Tx</span>
                  <span className="font-medium">{systemMetrics.networkTx || '89'} MB/s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Latency</span>
                  <span className="font-medium">{systemMetrics.networkLatency || '12'} ms</span>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ServiceStatus
              name="Web Server"
              status={systemHealth.webServer || 'healthy'}
              icon={Globe}
              description="Application web server status"
            />
            <ServiceStatus
              name="Database"
              status={systemHealth.database > 200 ? 'warning' : 'healthy'}
              icon={Database}
              description="Primary database connection"
            />
            <ServiceStatus
              name="Cache Server"
              status={systemHealth.cache || 'healthy'}
              icon={Zap}
              description="Redis cache server"
            />
            <ServiceStatus
              name="File Storage"
              status={systemHealth.storage || 'healthy'}
              icon={HardDrive}
              description="File system and storage"
            />
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Active Alerts</h3>
            {alerts.length > 0 && (
              <Button variant="outline" size="sm" onClick={clearAlerts}>
                Clear All
              </Button>
            )}
          </div>
          
          <div className="space-y-3">
            <AnimatePresence>
              {alerts.map((alert) => (
                <AlertItem
                  key={alert.id}
                  alert={alert}
                  onDismiss={(id) => setAlerts(prev => prev.filter(a => a.id !== id))}
                />
              ))}
            </AnimatePresence>
            
            {alerts.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No active alerts</p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Visible Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {metricCards.map((metric) => (
                <div key={metric.id} className="flex items-center space-x-2">
                  <Switch
                    checked={visibleMetrics.has(metric.id)}
                    onCheckedChange={() => toggleMetric(metric.id)}
                    id={`metric-${metric.id}`}
                  />
                  <label htmlFor={`metric-${metric.id}`} className="text-sm font-medium">
                    {metric.title}
                  </label>
                </div>
              ))}
            </div>
          </Card>
          
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Alert Thresholds</h3>
            <div className="space-y-4">
              {Object.entries(alertThresholds).map(([metric, thresholds]) => (
                <div key={metric} className="grid grid-cols-3 gap-4 items-center">
                  <label className="text-sm font-medium capitalize">{metric}</label>
                  <div>
                    <label className="text-xs text-gray-500">Warning</label>
                    <Input
                      type="number"
                      value={thresholds.warning}
                      onChange={(e) => {
                        const newThresholds = { ...alertThresholds };
                        newThresholds[metric].warning = Number(e.target.value);
                        // Update thresholds
                      }}
                      className="text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Critical</label>
                    <Input
                      type="number"
                      value={thresholds.critical}
                      onChange={(e) => {
                        const newThresholds = { ...alertThresholds };
                        newThresholds[metric].critical = Number(e.target.value);
                        // Update thresholds
                      }}
                      className="text-sm"
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SystemHealthMonitoring;