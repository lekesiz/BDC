import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import {
  AlertTriangle,
  Bell,
  Send,
  Settings,
  Activity,
  Clock,
  User,
  Filter,
  Download,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertOctagon,
  Info
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
const AlertManagement = () => {
  const [alertStats, setAlertStats] = useState(null);
  const [alertHistory, setAlertHistory] = useState([]);
  const [alertConfig, setAlertConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  // Form states
  const [testAlert, setTestAlert] = useState({
    title: '',
    message: '',
    severity: 'low',
    channels: []
  });
  const [manualAlert, setManualAlert] = useState({
    title: '',
    message: '',
    severity: 'medium',
    event_type: 'manual',
    source: 'admin',
    notes: '',
    metadata: {}
  });
  // Filter states
  const [filters, setFilters] = useState({
    severity: '',
    event_type: '',
    source: '',
    start_date: '',
    end_date: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  });
  useEffect(() => {
    loadData();
  }, []);
  const loadData = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadAlertStats(),
        loadAlertHistory(),
        loadAlertConfig()
      ]);
    } catch (error) {
      console.error('Error loading alert data:', error);
      toast.error('Failed to load alert data');
    } finally {
      setIsLoading(false);
    }
  };
  const loadAlertStats = async () => {
    try {
      const response = await api.get('/api/alerts/stats');
      setAlertStats(response.data.data);
    } catch (error) {
      console.error('Error loading alert stats:', error);
    }
  };
  const loadAlertHistory = async (page = 1, filterParams = {}) => {
    try {
      const params = {
        page,
        per_page: pagination.per_page,
        ...filterParams
      };
      const response = await api.get('/api/alerts/history', { params });
      const data = response.data.data;
      setAlertHistory(data.alerts);
      setPagination(data.pagination);
    } catch (error) {
      console.error('Error loading alert history:', error);
    }
  };
  const loadAlertConfig = async () => {
    try {
      const response = await api.get('/api/alerts/config');
      setAlertConfig(response.data.data);
    } catch (error) {
      console.error('Error loading alert config:', error);
    }
  };
  const sendTestAlert = async () => {
    try {
      if (!testAlert.title || !testAlert.message) {
        toast.error('Please fill in title and message');
        return;
      }
      const response = await api.post('/api/alerts/test', testAlert);
      if (response.data.success) {
        toast.success('Test alert sent successfully!');
        setTestAlert({
          title: '',
          message: '',
          severity: 'low',
          channels: []
        });
        // Reload stats to see the new alert
        await loadAlertStats();
        await loadAlertHistory();
      }
    } catch (error) {
      console.error('Error sending test alert:', error);
      toast.error('Failed to send test alert');
    }
  };
  const sendManualAlert = async () => {
    try {
      if (!manualAlert.title || !manualAlert.message || !manualAlert.event_type) {
        toast.error('Please fill in required fields');
        return;
      }
      const response = await api.post('/api/alerts/send', manualAlert);
      if (response.data.success) {
        toast.success('Manual alert sent successfully!');
        setManualAlert({
          title: '',
          message: '',
          severity: 'medium',
          event_type: 'manual',
          source: 'admin',
          notes: '',
          metadata: {}
        });
        // Reload data
        await loadAlertStats();
        await loadAlertHistory();
      }
    } catch (error) {
      console.error('Error sending manual alert:', error);
      toast.error('Failed to send manual alert');
    }
  };
  const applyFilters = () => {
    const activeFilters = Object.fromEntries(
      Object.entries(filters).filter(([key, value]) => value !== '')
    );
    loadAlertHistory(1, activeFilters);
  };
  const clearFilters = () => {
    setFilters({
      severity: '',
      event_type: '',
      source: '',
      start_date: '',
      end_date: ''
    });
    loadAlertHistory(1, {});
  };
  const exportAlerts = async () => {
    try {
      const params = {
        ...filters,
        format: 'csv',
        all: true
      };
      const response = await api.get('/api/alerts/export', { 
        params,
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `bdc-alerts-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Alert data exported successfully');
    } catch (error) {
      console.error('Error exporting alerts:', error);
      toast.error('Failed to export alert data');
    }
  };
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertOctagon className="h-4 w-4 text-red-500" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'medium':
        return <Bell className="h-4 w-4 text-yellow-500" />;
      case 'low':
        return <Info className="h-4 w-4 text-blue-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-lg">Loading alert management...</span>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Alert Management</h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage system alerts and notifications
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={loadData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={exportAlerts} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="history">Alert History</TabsTrigger>
          <TabsTrigger value="send">Send Alerts</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
        </TabsList>
        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Alert Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Activity className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Last 24 Hours</p>
                    <p className="text-2xl font-bold">{alertStats?.total_alerts_24h || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Last Hour</p>
                    <p className="text-2xl font-bold">{alertStats?.alerts_last_hour || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <CheckCircle className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Active Channels</p>
                    <p className="text-2xl font-bold">{alertStats?.enabled_channels?.length || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <AlertTriangle className="h-8 w-8 text-red-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Critical Alerts</p>
                    <p className="text-2xl font-bold">
                      {alertStats?.severity_breakdown_24h?.critical || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          {/* Severity Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Alert Breakdown (24 Hours)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(alertStats?.severity_breakdown_24h || {}).map(([severity, count]) => (
                  <div key={severity} className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      {getSeverityIcon(severity)}
                    </div>
                    <p className="text-2xl font-bold">{count}</p>
                    <p className="text-sm text-gray-600 capitalize">{severity}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          {/* System Health */}
          <Card>
            <CardHeader>
              <CardTitle>Alert System Health</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Alert Service Status</span>
                  <Badge className="bg-green-100 text-green-800">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Operational
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Enabled Channels</span>
                  <div className="flex space-x-2">
                    {alertStats?.enabled_channels?.map(channel => (
                      <Badge key={channel} variant="outline">
                        {channel}
                      </Badge>
                    ))}
                  </div>
                </div>
                {alertStats?.last_alert && (
                  <div className="flex items-center justify-between">
                    <span>Last Alert</span>
                    <span className="text-sm text-gray-600">
                      {new Date(alertStats.last_alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        {/* Alert History Tab */}
        <TabsContent value="history" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filter Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <Select
                  value={filters.severity}
                  onValueChange={(value) => setFilters(prev => ({ ...prev, severity: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Severities</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  placeholder="Event Type"
                  value={filters.event_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, event_type: e.target.value }))}
                />
                <Input
                  placeholder="Source"
                  value={filters.source}
                  onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                />
                <Input
                  type="datetime-local"
                  placeholder="Start Date"
                  value={filters.start_date}
                  onChange={(e) => setFilters(prev => ({ ...prev, start_date: e.target.value }))}
                />
                <Input
                  type="datetime-local"
                  placeholder="End Date"
                  value={filters.end_date}
                  onChange={(e) => setFilters(prev => ({ ...prev, end_date: e.target.value }))}
                />
              </div>
              <div className="flex space-x-3 mt-4">
                <Button onClick={applyFilters} size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
                <Button onClick={clearFilters} variant="outline" size="sm">
                  Clear Filters
                </Button>
              </div>
            </CardContent>
          </Card>
          {/* Alert List */}
          <Card>
            <CardHeader>
              <CardTitle>Alert History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alertHistory.map((alert) => (
                  <div
                    key={alert.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        {getSeverityIcon(alert.severity)}
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h4 className="font-semibold">{alert.title}</h4>
                            <Badge className={getSeverityColor(alert.severity)}>
                              {alert.severity}
                            </Badge>
                          </div>
                          <p className="text-gray-600 text-sm mb-2">{alert.message}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Source: {alert.source}</span>
                            <span>Type: {alert.event_type}</span>
                            <span>{new Date(alert.timestamp).toLocaleString()}</span>
                            {alert.correlation_id && (
                              <span>ID: {alert.correlation_id}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {alertHistory.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No alerts found matching your criteria</p>
                  </div>
                )}
              </div>
              {/* Pagination */}
              {pagination.pages > 1 && (
                <div className="flex items-center justify-between mt-6">
                  <div className="text-sm text-gray-600">
                    Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
                    {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
                    {pagination.total} alerts
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!pagination.has_prev}
                      onClick={() => loadAlertHistory(pagination.page - 1, filters)}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!pagination.has_next}
                      onClick={() => loadAlertHistory(pagination.page + 1, filters)}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        {/* Send Alerts Tab */}
        <TabsContent value="send" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Test Alert */}
            <Card>
              <CardHeader>
                <CardTitle>Send Test Alert</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Alert Title"
                  value={testAlert.title}
                  onChange={(e) => setTestAlert(prev => ({ ...prev, title: e.target.value }))}
                />
                <Textarea
                  placeholder="Alert Message"
                  value={testAlert.message}
                  onChange={(e) => setTestAlert(prev => ({ ...prev, message: e.target.value }))}
                  rows={3}
                />
                <Select
                  value={testAlert.severity}
                  onValueChange={(value) => setTestAlert(prev => ({ ...prev, severity: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={sendTestAlert} className="w-full">
                  <Send className="h-4 w-4 mr-2" />
                  Send Test Alert
                </Button>
              </CardContent>
            </Card>
            {/* Manual Alert */}
            <Card>
              <CardHeader>
                <CardTitle>Send Manual Alert</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Alert Title *"
                  value={manualAlert.title}
                  onChange={(e) => setManualAlert(prev => ({ ...prev, title: e.target.value }))}
                />
                <Textarea
                  placeholder="Alert Message *"
                  value={manualAlert.message}
                  onChange={(e) => setManualAlert(prev => ({ ...prev, message: e.target.value }))}
                  rows={3}
                />
                <div className="grid grid-cols-2 gap-4">
                  <Select
                    value={manualAlert.severity}
                    onValueChange={(value) => setManualAlert(prev => ({ ...prev, severity: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Severity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Event Type *"
                    value={manualAlert.event_type}
                    onChange={(e) => setManualAlert(prev => ({ ...prev, event_type: e.target.value }))}
                  />
                </div>
                <Input
                  placeholder="Source"
                  value={manualAlert.source}
                  onChange={(e) => setManualAlert(prev => ({ ...prev, source: e.target.value }))}
                />
                <Textarea
                  placeholder="Admin Notes (optional)"
                  value={manualAlert.notes}
                  onChange={(e) => setManualAlert(prev => ({ ...prev, notes: e.target.value }))}
                  rows={2}
                />
                <Button onClick={sendManualAlert} className="w-full">
                  <Send className="h-4 w-4 mr-2" />
                  Send Manual Alert
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        {/* Configuration Tab */}
        <TabsContent value="config" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Alert System Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              {alertConfig ? (
                <div className="space-y-6">
                  {/* Enabled Channels */}
                  <div>
                    <h4 className="font-semibold mb-3">Enabled Channels</h4>
                    <div className="flex flex-wrap gap-2">
                      {alertConfig.enabled_channels.map(channel => (
                        <Badge key={channel} className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          {channel}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  {/* Email Configuration */}
                  <div>
                    <h4 className="font-semibold mb-3">Email Configuration</h4>
                    <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>Server: {alertConfig.email_config.server}</div>
                        <div>Port: {alertConfig.email_config.port}</div>
                        <div>TLS: {alertConfig.email_config.use_tls ? 'Enabled' : 'Disabled'}</div>
                        <div>From: {alertConfig.email_config.from_email}</div>
                      </div>
                      <div>
                        Admin Emails: {alertConfig.email_config.admin_emails.join(', ')}
                      </div>
                    </div>
                  </div>
                  {/* Rate Limits */}
                  <div>
                    <h4 className="font-semibold mb-3">Rate Limits</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(alertConfig.rate_limits).map(([severity, config]) => (
                        <div key={severity} className="bg-gray-50 p-3 rounded-lg">
                          <div className="font-medium capitalize">{severity}</div>
                          <div className="text-sm text-gray-600">
                            {config.max_alerts} per {config.window_minutes}m
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {/* Webhook Status */}
                  <div>
                    <h4 className="font-semibold mb-3">Integration Status</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="flex items-center space-x-2">
                        {alertConfig.slack_config.webhook_configured ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-sm">Slack Webhook</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {alertConfig.webhook_config.primary_configured ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-sm">Primary Webhook</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {alertConfig.webhook_config.teams_configured ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-sm">Teams</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {alertConfig.webhook_config.discord_configured ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="text-sm">Discord</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Settings className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-500">Loading configuration...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
export default AlertManagement;