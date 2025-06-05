import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Server,
  Database,
  Cpu,
  MemoryStick,
  HardDrive,
  Users,
  FileText,
  BookOpen,
  UserCheck,
  TrendingUp,
  BarChart3,
  RefreshCw,
  ExternalLink,
  Shield,
  Clock,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
const SystemMonitoring = () => {
  const [metrics, setMetrics] = useState({});
  const [serviceStatus, setServiceStatus] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  useEffect(() => {
    loadMonitoringData();
    const interval = setInterval(loadMonitoringData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);
  const loadMonitoringData = async () => {
    try {
      await Promise.all([
        loadSystemMetrics(),
        loadServiceStatus(),
        loadAlerts()
      ]);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading monitoring data:', error);
      toast.error('Failed to load monitoring data');
    } finally {
      setIsLoading(false);
    }
  };
  const loadSystemMetrics = async () => {
    try {
      // Simulate fetching metrics from Prometheus/custom endpoint
      const mockMetrics = {
        system: {
          cpu: Math.floor(Math.random() * 50) + 20,
          memory: Math.floor(Math.random() * 40) + 30,
          disk: Math.floor(Math.random() * 30) + 40
        },
        application: {
          users: 1247,
          beneficiaries: 892,
          programs: 45,
          evaluations: 3421,
          documents: 7834,
          activeSessions: 23,
          responseTime: Math.floor(Math.random() * 500) + 200,
          errorRate: (Math.random() * 2).toFixed(2)
        },
        database: {
          connections: 12,
          maxConnections: 100,
          queryTime: Math.floor(Math.random() * 100) + 50
        },
        cache: {
          hitRate: (85 + Math.random() * 10).toFixed(1),
          memoryUsage: Math.floor(Math.random() * 30) + 40
        }
      };
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  };
  const loadServiceStatus = async () => {
    try {
      // Simulate service health checks
      const services = {
        backend: { status: 'healthy', uptime: '5d 12h', version: '1.0.0' },
        frontend: { status: 'healthy', uptime: '5d 12h', version: '1.0.0' },
        database: { status: 'healthy', uptime: '10d 3h', version: '14.9' },
        redis: { status: 'healthy', uptime: '8d 7h', version: '7.0' },
        prometheus: { status: 'healthy', uptime: '2d 15h', version: '2.47' },
        grafana: { status: 'healthy', uptime: '2d 15h', version: '10.1' },
        alertmanager: { status: 'healthy', uptime: '2d 15h', version: '0.26' }
      };
      setServiceStatus(services);
    } catch (error) {
      console.error('Error loading service status:', error);
    }
  };
  const loadAlerts = async () => {
    try {
      // Simulate active alerts
      const mockAlerts = [
        {
          id: 1,
          name: 'High Memory Usage',
          severity: 'warning',
          status: 'firing',
          since: '5m ago',
          description: 'Memory usage is above 85% threshold'
        },
        {
          id: 2,
          name: 'Database Slow Queries',
          severity: 'medium',
          status: 'firing',
          since: '12m ago',
          description: 'Average query time above 1 second'
        }
      ];
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'error':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'warning':
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };
  const openMonitoringTool = (tool) => {
    const urls = {
      prometheus: 'http://localhost:9090',
      grafana: 'http://localhost:3000',
      alertmanager: 'http://localhost:9093'
    };
    if (urls[tool]) {
      window.open(urls[tool], '_blank');
    }
  };
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-lg">Loading monitoring data...</span>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">System Monitoring</h1>
          <p className="text-gray-600 mt-1">
            Real-time system health and performance metrics
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdated?.toLocaleTimeString()}
          </div>
          <Button onClick={loadMonitoringData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
      {/* Active Alerts */}
      {alerts.length > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {alerts.length} active alert{alerts.length > 1 ? 's' : ''} require attention
          </AlertDescription>
        </Alert>
      )}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
        </TabsList>
        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* System Health Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system?.cpu}%</div>
                <Progress value={metrics.system?.cpu} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {metrics.system?.cpu < 50 ? 'Normal' : metrics.system?.cpu < 80 ? 'High' : 'Critical'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                <MemoryStick className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system?.memory}%</div>
                <Progress value={metrics.system?.memory} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {metrics.system?.memory < 50 ? 'Normal' : metrics.system?.memory < 80 ? 'High' : 'Critical'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system?.disk}%</div>
                <Progress value={metrics.system?.disk} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {metrics.system?.disk < 50 ? 'Normal' : metrics.system?.disk < 80 ? 'High' : 'Critical'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Response Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.responseTime}ms</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {metrics.application?.responseTime < 300 ? 'Excellent' : 
                   metrics.application?.responseTime < 1000 ? 'Good' : 'Slow'}
                </p>
              </CardContent>
            </Card>
          </div>
          {/* Application Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.users?.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Registered users</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Beneficiaries</CardTitle>
                <UserCheck className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.beneficiaries?.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Active beneficiaries</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Programs</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.programs}</div>
                <p className="text-xs text-muted-foreground">Training programs</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Evaluations</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.evaluations?.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Completed evaluations</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Documents</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.documents?.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Stored documents</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.application?.activeSessions}</div>
                <p className="text-xs text-muted-foreground">Current sessions</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        {/* Services Tab */}
        <TabsContent value="services" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(serviceStatus).map(([service, info]) => (
              <Card key={service}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium capitalize">{service}</CardTitle>
                  {info.status === 'healthy' ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <Badge className={info.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {info.status}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        Uptime: {info.uptime}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Version: {info.version}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        {/* Metrics Tab */}
        <TabsContent value="metrics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Database Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Active Connections</span>
                  <span className="text-sm">{metrics.database?.connections}/{metrics.database?.maxConnections}</span>
                </div>
                <Progress value={(metrics.database?.connections / metrics.database?.maxConnections) * 100} />
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Avg Query Time</span>
                  <span className="text-sm">{metrics.database?.queryTime}ms</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Cache Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Hit Rate</span>
                  <span className="text-sm">{metrics.cache?.hitRate}%</span>
                </div>
                <Progress value={parseFloat(metrics.cache?.hitRate)} />
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Memory Usage</span>
                  <span className="text-sm">{metrics.cache?.memoryUsage}%</span>
                </div>
                <Progress value={metrics.cache?.memoryUsage} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Active Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                  <p>No active alerts</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h4 className="font-semibold">{alert.name}</h4>
                            <Badge className={getSeverityColor(alert.severity)}>
                              {alert.severity}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{alert.description}</p>
                          <p className="text-xs text-gray-500">Since: {alert.since}</p>
                        </div>
                        <Button variant="outline" size="sm">
                          Acknowledge
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        {/* Tools Tab */}
        <TabsContent value="tools" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Prometheus</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Metrics collection and monitoring
                </p>
                <Button 
                  onClick={() => openMonitoringTool('prometheus')}
                  className="w-full"
                  variant="outline"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Prometheus
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Grafana</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Visualization and dashboards
                </p>
                <Button 
                  onClick={() => openMonitoringTool('grafana')}
                  className="w-full"
                  variant="outline"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Grafana
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>AlertManager</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Alert management and routing
                </p>
                <Button 
                  onClick={() => openMonitoringTool('alertmanager')}
                  className="w-full"
                  variant="outline"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open AlertManager
                </Button>
              </CardContent>
            </Card>
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button onClick={loadMonitoringData} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh All Data
                </Button>
                <Button variant="outline">
                  <Zap className="h-4 w-4 mr-2" />
                  Run Health Check
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
export default SystemMonitoring;