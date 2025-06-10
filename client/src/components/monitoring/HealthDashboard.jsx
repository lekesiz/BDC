import React, { useState, useEffect, useCallback } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Activity, 
  Server, 
  Database, 
  Wifi, 
  HardDrive,
  Cpu,
  MemoryStick,
  Clock,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Settings,
  Bell,
  BellOff,
  Download,
  Filter
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ResponsiveContainer, ResponsiveGrid, ResponsiveCard } from '@/components/responsive/ResponsiveContainer';
import { cn } from '@/lib/utils';
import api from '@/lib/api';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer as RechartsResponsiveContainer
} from 'recharts';

const HealthDashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [services, setServices] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
  const [selectedTimeframe, setSelectedTimeframe] = useState(24);
  const [alertsEnabled, setAlertsEnabled] = useState(true);

  const fetchHealthData = useCallback(async () => {
    try {
      const [healthResponse, metricsResponse, alertsResponse, servicesResponse] = await Promise.all([
        api.get('/api/v2/health/detailed'),
        api.get(`/api/v2/health/metrics?hours=${selectedTimeframe}`),
        api.get('/api/v2/health/alerts'),
        api.get('/api/v2/health/services')
      ]);

      setHealthData(healthResponse.data);
      setMetrics(metricsResponse.data);
      setAlerts(alertsResponse.data.active_alerts || []);
      setServices(servicesResponse.data.services || {});
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedTimeframe]);

  useEffect(() => {
    fetchHealthData();
  }, [fetchHealthData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchHealthData, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchHealthData]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'critical':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatUptime = (uptime) => {
    if (!uptime) return 'Unknown';
    return uptime;
  };

  const exportHealthReport = async () => {
    try {
      const response = await api.get('/api/v2/health/detailed');
      const data = response.data;
      
      const report = {
        timestamp: new Date().toISOString(),
        overall_status: data.status,
        system_metrics: data.system,
        services: data.services,
        alerts: data.alerts,
        performance: data.performance
      };

      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `health-report-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export health report:', error);
    }
  };

  if (isLoading) {
    return (
      <ResponsiveContainer>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <RefreshCw className="h-6 w-6 animate-spin" />
            <span>Loading health data...</span>
          </div>
        </div>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">System Health Dashboard</h1>
            <p className="text-sm text-gray-500">
              Real-time monitoring and health status
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAlertsEnabled(!alertsEnabled)}
              className={cn(alertsEnabled ? 'text-green-600' : 'text-gray-400')}
            >
              {alertsEnabled ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
              Alerts
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={exportHealthReport}
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={cn(autoRefresh ? 'text-green-600' : 'text-gray-400')}
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', autoRefresh && 'animate-spin')} />
              Auto Refresh
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={fetchHealthData}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Overall Status */}
        <ResponsiveCard>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={cn('h-3 w-3 rounded-full', getStatusColor(healthData?.status))} />
                <div>
                  <h3 className="text-lg font-medium">
                    System Status: {healthData?.status?.toUpperCase() || 'UNKNOWN'}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Last updated: {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleString() : 'Unknown'}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-2xl font-bold">
                  {healthData?.response_time_ms?.toFixed(1) || 0}ms
                </div>
                <div className="text-sm text-gray-500">Response Time</div>
              </div>
            </div>
          </div>
        </ResponsiveCard>

        {/* Alerts */}
        {alerts.length > 0 && alertsEnabled && (
          <ResponsiveCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <span>Active Alerts ({alerts.length})</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alerts.map((alert, index) => (
                  <div
                    key={index}
                    className={cn(
                      'p-3 rounded-lg border-l-4',
                      alert.severity === 'critical' ? 'border-red-500 bg-red-50' : 'border-yellow-500 bg-yellow-50'
                    )}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{alert.message}</p>
                        <p className="text-sm text-gray-600">
                          Threshold: {alert.threshold} | Current: {alert.current_value}
                        </p>
                      </div>
                      <Badge variant={alert.severity === 'critical' ? 'destructive' : 'warning'}>
                        {alert.severity}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </ResponsiveCard>
        )}

        {/* System Metrics */}
        <ResponsiveGrid cols={{ default: 1, sm: 2, lg: 4 }}>
          {/* CPU Usage */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Cpu className="h-8 w-8 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">CPU Usage</p>
                    <p className="text-2xl font-bold">
                      {healthData?.system?.cpu?.percent?.toFixed(1) || 0}%
                    </p>
                  </div>
                </div>
                {getStatusIcon(healthData?.system?.cpu?.status)}
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Memory Usage */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <MemoryStick className="h-8 w-8 text-purple-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Memory Usage</p>
                    <p className="text-2xl font-bold">
                      {healthData?.system?.memory?.percent?.toFixed(1) || 0}%
                    </p>
                  </div>
                </div>
                {getStatusIcon(healthData?.system?.memory?.status)}
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Disk Usage */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <HardDrive className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Disk Usage</p>
                    <p className="text-2xl font-bold">
                      {healthData?.services?.disk?.usage_percent?.toFixed(1) || 0}%
                    </p>
                  </div>
                </div>
                {getStatusIcon(healthData?.services?.disk?.status)}
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Uptime */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Clock className="h-8 w-8 text-orange-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Uptime</p>
                    <p className="text-lg font-bold">
                      {formatUptime(healthData?.uptime)}
                    </p>
                  </div>
                </div>
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              </div>
            </CardContent>
          </ResponsiveCard>
        </ResponsiveGrid>

        {/* Services Status */}
        <ResponsiveCard>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>Services Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(services).map(([serviceName, service]) => (
                <div
                  key={serviceName}
                  className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {serviceName === 'database' ? (
                        <Database className="h-5 w-5 text-blue-500" />
                      ) : serviceName === 'redis' ? (
                        <Wifi className="h-5 w-5 text-red-500" />
                      ) : (
                        <Server className="h-5 w-5 text-gray-500" />
                      )}
                      <span className="font-medium">{service.name || serviceName}</span>
                    </div>
                    {getStatusIcon(service.status)}
                  </div>
                  
                  {service.response_time && (
                    <p className="text-sm text-gray-600">
                      Response: {service.response_time.toFixed(1)}ms
                    </p>
                  )}
                  
                  {service.error_message && (
                    <p className="text-sm text-red-600 mt-1">
                      Error: {service.error_message}
                    </p>
                  )}
                  
                  <p className="text-xs text-gray-500 mt-1">
                    Last check: {service.last_check ? new Date(service.last_check).toLocaleTimeString() : 'Unknown'}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </ResponsiveCard>

        {/* Performance Metrics Charts */}
        {metrics?.history && metrics.history.length > 0 && (
          <ResponsiveCard>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Performance Trends</span>
                </div>
                <select
                  value={selectedTimeframe}
                  onChange={(e) => setSelectedTimeframe(Number(e.target.value))}
                  className="text-sm border rounded px-2 py-1"
                >
                  <option value={1}>Last Hour</option>
                  <option value={24}>Last 24 Hours</option>
                  <option value={168}>Last Week</option>
                  <option value={720}>Last Month</option>
                </select>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* CPU and Memory Chart */}
                <div>
                  <h4 className="text-sm font-medium mb-3">System Resources</h4>
                  <RechartsResponsiveContainer width="100%" height={200}>
                    <LineChart data={metrics.history}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                      />
                      <YAxis domain={[0, 100]} />
                      <Tooltip 
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value, name) => [`${value.toFixed(1)}%`, name]}
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="cpu_percent" 
                        stroke="#3b82f6" 
                        name="CPU %" 
                        strokeWidth={2}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="memory_percent" 
                        stroke="#8b5cf6" 
                        name="Memory %" 
                        strokeWidth={2}
                      />
                    </LineChart>
                  </RechartsResponsiveContainer>
                </div>

                {/* Response Time Chart */}
                <div>
                  <h4 className="text-sm font-medium mb-3">Response Time</h4>
                  <RechartsResponsiveContainer width="100%" height={200}>
                    <AreaChart data={metrics.history}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value, name) => [`${value.toFixed(1)}ms`, name]}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="response_time_ms" 
                        stroke="#10b981" 
                        fill="#10b981" 
                        fillOpacity={0.3}
                        name="Response Time"
                      />
                    </AreaChart>
                  </RechartsResponsiveContainer>
                </div>
              </div>
            </CardContent>
          </ResponsiveCard>
        )}

        {/* Environment Info */}
        <ResponsiveCard>
          <CardHeader>
            <CardTitle>Environment Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Hostname</p>
                <p className="font-mono">{healthData?.environment?.hostname || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">OS</p>
                <p className="font-mono">{healthData?.environment?.os || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Python Version</p>
                <p className="font-mono">{healthData?.environment?.python_version || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Environment</p>
                <p className="font-mono">{healthData?.environment?.environment || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">App Version</p>
                <p className="font-mono">{healthData?.version || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Timezone</p>
                <p className="font-mono">{healthData?.environment?.timezone || 'Unknown'}</p>
              </div>
            </div>
          </CardContent>
        </ResponsiveCard>
      </div>
    </ResponsiveContainer>
  );
};

export default HealthDashboard;