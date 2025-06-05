import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer
} from 'recharts';
import {
  Activity,
  AlertTriangle,
  Search,
  Filter,
  Download,
  RefreshCw,
  TrendingUp,
  Shield,
  Clock,
  Eye,
  BarChart3,
  PieChart as PieChartIcon,
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
import { Checkbox } from '@/components/ui/checkbox';
const LogAnalytics = () => {
  const [insights, setInsights] = useState([]);
  const [trends, setTrends] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [analyticsStatus, setAnalyticsStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('insights');
  // Search and filter states
  const [searchParams, setSearchParams] = useState({
    query: '',
    startTime: '',
    endTime: '',
    logLevels: [],
    sources: [],
    maxResults: 1000
  });
  const [insightFilters, setInsightFilters] = useState({
    hours: 24,
    types: [],
    minSeverity: 'low'
  });
  const [trendFilters, setTrendFilters] = useState({
    days: 7,
    granularity: 'hour'
  });
  const severityColors = {
    low: '#3B82F6',
    medium: '#F59E0B', 
    high: '#EF4444',
    critical: '#DC2626'
  };
  const logLevelColors = {
    DEBUG: '#6B7280',
    INFO: '#3B82F6',
    WARNING: '#F59E0B',
    ERROR: '#EF4444',
    CRITICAL: '#DC2626'
  };
  useEffect(() => {
    loadData();
  }, []);
  const loadData = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadInsights(),
        loadTrends(),
        loadAnalyticsStatus()
      ]);
    } catch (error) {
      console.error('Error loading analytics data:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };
  const loadInsights = async () => {
    try {
      const params = new URLSearchParams({
        hours: insightFilters.hours.toString(),
        min_severity: insightFilters.minSeverity
      });
      insightFilters.types.forEach(type => {
        params.append('types', type);
      });
      const response = await api.get(`/api/analytics/logs/insights?${params}`);
      if (response.data.success) {
        setInsights(response.data.data.insights);
      }
    } catch (error) {
      console.error('Error loading insights:', error);
    }
  };
  const loadTrends = async () => {
    try {
      const params = new URLSearchParams({
        days: trendFilters.days.toString(),
        granularity: trendFilters.granularity
      });
      const response = await api.get(`/api/analytics/logs/trends?${params}`);
      if (response.data.success) {
        setTrends(response.data.data.trends);
      }
    } catch (error) {
      console.error('Error loading trends:', error);
    }
  };
  const loadAnalyticsStatus = async () => {
    try {
      const response = await api.get('/api/analytics/status');
      if (response.data.success) {
        setAnalyticsStatus(response.data.data);
      }
    } catch (error) {
      console.error('Error loading analytics status:', error);
    }
  };
  const searchLogs = async () => {
    try {
      const payload = {
        query: searchParams.query,
        start_time: searchParams.startTime,
        end_time: searchParams.endTime,
        log_levels: searchParams.logLevels,
        sources: searchParams.sources,
        max_results: searchParams.maxResults
      };
      const response = await api.post('/api/analytics/logs/search', payload);
      if (response.data.success) {
        setSearchResults(response.data.data.logs);
        toast.success(`Found ${response.data.data.logs.length} log entries`);
      }
    } catch (error) {
      console.error('Error searching logs:', error);
      toast.error('Failed to search logs');
    }
  };
  const runPatternAnalysis = async (analysisType) => {
    try {
      const params = new URLSearchParams({
        type: analysisType,
        hours: '1'
      });
      const response = await api.get(`/api/analytics/logs/patterns?${params}`);
      if (response.data.success) {
        const results = response.data.data.results;
        if (results.length > 0) {
          toast.success(`Found ${results.length} patterns in ${analysisType} analysis`);
          // Refresh insights to include new analysis
          await loadInsights();
        } else {
          toast.info(`No significant patterns found in ${analysisType} analysis`);
        }
      }
    } catch (error) {
      console.error('Error running pattern analysis:', error);
      toast.error('Failed to run pattern analysis');
    }
  };
  const exportLogs = async (format = 'json') => {
    try {
      const payload = {
        start_time: searchParams.startTime,
        end_time: searchParams.endTime,
        format,
        log_levels: searchParams.logLevels,
        sources: searchParams.sources,
        max_results: searchParams.maxResults
      };
      const response = await api.post('/api/analytics/logs/export', payload);
      if (response.data.success) {
        if (format === 'csv') {
          // Download CSV
          const blob = new Blob([response.data.data.csv_content], { type: 'text/csv' });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `bdc-logs-${new Date().toISOString().split('T')[0]}.csv`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else {
          // Download JSON
          const blob = new Blob([JSON.stringify(response.data.data.logs, null, 2)], { type: 'application/json' });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `bdc-logs-${new Date().toISOString().split('T')[0]}.json`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }
        toast.success(`Logs exported as ${format.toUpperCase()}`);
      }
    } catch (error) {
      console.error('Error exporting logs:', error);
      toast.error('Failed to export logs');
    }
  };
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertOctagon className="h-4 w-4 text-red-500" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'medium':
        return <Activity className="h-4 w-4 text-yellow-500" />;
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
  const getAnalysisTypeIcon = (type) => {
    switch (type) {
      case 'error_pattern':
        return <AlertTriangle className="h-4 w-4" />;
      case 'performance_trend':
        return <TrendingUp className="h-4 w-4" />;
      case 'security_incident':
        return <Shield className="h-4 w-4" />;
      case 'usage_pattern':
        return <BarChart3 className="h-4 w-4" />;
      case 'anomaly_detection':
        return <Eye className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-lg">Loading log analytics...</span>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Log Analytics</h1>
          <p className="text-gray-600 mt-1">
            Intelligent log analysis, pattern detection, and insights
          </p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={loadData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
      {/* Analytics Status */}
      {analyticsStatus && (
        <Card>
          <CardHeader>
            <CardTitle>Analytics Service Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${analyticsStatus.enabled ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">Service {analyticsStatus.enabled ? 'Enabled' : 'Disabled'}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${analyticsStatus.elasticsearch_health ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">Elasticsearch</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${analyticsStatus.redis_health ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">Redis</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${analyticsStatus.background_analysis_running ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">Analysis Running</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="search">Log Search</TabsTrigger>
          <TabsTrigger value="patterns">Pattern Analysis</TabsTrigger>
        </TabsList>
        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-6">
          {/* Insight Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Insight Filters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Time Window</label>
                  <Select
                    value={insightFilters.hours.toString()}
                    onValueChange={(value) => setInsightFilters(prev => ({ ...prev, hours: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Last Hour</SelectItem>
                      <SelectItem value="6">Last 6 Hours</SelectItem>
                      <SelectItem value="24">Last 24 Hours</SelectItem>
                      <SelectItem value="72">Last 3 Days</SelectItem>
                      <SelectItem value="168">Last Week</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Minimum Severity</label>
                  <Select
                    value={insightFilters.minSeverity}
                    onValueChange={(value) => setInsightFilters(prev => ({ ...prev, minSeverity: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button onClick={loadInsights} className="w-full">
                    <Filter className="h-4 w-4 mr-2" />
                    Apply Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          {/* Insights List */}
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getAnalysisTypeIcon(insight.analysis_type)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-semibold">{insight.title}</h4>
                          <Badge className={getSeverityColor(insight.severity)}>
                            {getSeverityIcon(insight.severity)}
                            <span className="ml-1">{insight.severity}</span>
                          </Badge>
                          <Badge variant="outline">
                            {insight.analysis_type.replace('_', ' ')}
                          </Badge>
                        </div>
                        <p className="text-gray-600 mb-3">{insight.summary}</p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                          <div>
                            <span className="text-xs text-gray-500">Log Count</span>
                            <div className="font-medium">{insight.log_count}</div>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Confidence</span>
                            <div className="font-medium">{(insight.confidence_score * 100).toFixed(1)}%</div>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Time Period</span>
                            <div className="font-medium text-xs">
                              {new Date(insight.affected_period[0]).toLocaleDateString()}
                            </div>
                          </div>
                          <div>
                            <span className="text-xs text-gray-500">Analysis Time</span>
                            <div className="font-medium text-xs">
                              {new Date(insight.analysis_timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        {insight.recommendations && insight.recommendations.length > 0 && (
                          <div>
                            <span className="text-xs text-gray-500 block mb-1">Recommendations</span>
                            <ul className="text-sm space-y-1">
                              {insight.recommendations.slice(0, 3).map((rec, idx) => (
                                <li key={idx} className="flex items-start space-x-2">
                                  <span className="text-blue-500 mt-1">•</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {insights.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No insights found for the selected criteria</p>
              </div>
            )}
          </div>
        </TabsContent>
        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-6">
          {/* Trend Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Trend Filters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Time Range</label>
                  <Select
                    value={trendFilters.days.toString()}
                    onValueChange={(value) => setTrendFilters(prev => ({ ...prev, days: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Last Day</SelectItem>
                      <SelectItem value="7">Last Week</SelectItem>
                      <SelectItem value="14">Last 2 Weeks</SelectItem>
                      <SelectItem value="30">Last Month</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Granularity</label>
                  <Select
                    value={trendFilters.granularity}
                    onValueChange={(value) => setTrendFilters(prev => ({ ...prev, granularity: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hour">Hourly</SelectItem>
                      <SelectItem value="day">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button onClick={loadTrends} className="w-full">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Update Trends
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          {/* Trend Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Log Volume Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Log Volume Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => {
                        const date = new Date(value);
                        return trendFilters.granularity === 'hour' 
                          ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                          : date.toLocaleDateString();
                      }}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="total" stroke="#3B82F6" name="Total Logs" />
                    <Line type="monotone" dataKey="error" stroke="#EF4444" name="Errors" />
                    <Line type="monotone" dataKey="warning" stroke="#F59E0B" name="Warnings" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            {/* Log Level Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Log Level Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => {
                        const date = new Date(value);
                        return trendFilters.granularity === 'hour' 
                          ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                          : date.toLocaleDateString();
                      }}
                    />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="critical" stackId="a" fill="#DC2626" name="Critical" />
                    <Bar dataKey="error" stackId="a" fill="#EF4444" name="Error" />
                    <Bar dataKey="warning" stackId="a" fill="#F59E0B" name="Warning" />
                    <Bar dataKey="info" stackId="a" fill="#3B82F6" name="Info" />
                    <Bar dataKey="debug" stackId="a" fill="#6B7280" name="Debug" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        {/* Search Tab */}
        <TabsContent value="search" className="space-y-6">
          {/* Search Form */}
          <Card>
            <CardHeader>
              <CardTitle>Log Search</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Search Query</label>
                  <Input
                    placeholder="Search in log messages..."
                    value={searchParams.query}
                    onChange={(e) => setSearchParams(prev => ({ ...prev, query: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Max Results</label>
                  <Select
                    value={searchParams.maxResults.toString()}
                    onValueChange={(value) => setSearchParams(prev => ({ ...prev, maxResults: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="100">100</SelectItem>
                      <SelectItem value="500">500</SelectItem>
                      <SelectItem value="1000">1,000</SelectItem>
                      <SelectItem value="5000">5,000</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Start Time</label>
                  <Input
                    type="datetime-local"
                    value={searchParams.startTime}
                    onChange={(e) => setSearchParams(prev => ({ ...prev, startTime: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">End Time</label>
                  <Input
                    type="datetime-local"
                    value={searchParams.endTime}
                    onChange={(e) => setSearchParams(prev => ({ ...prev, endTime: e.target.value }))}
                  />
                </div>
              </div>
              <div className="flex space-x-3">
                <Button onClick={searchLogs}>
                  <Search className="h-4 w-4 mr-2" />
                  Search Logs
                </Button>
                <Button onClick={() => exportLogs('json')} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export JSON
                </Button>
                <Button onClick={() => exportLogs('csv')} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </CardContent>
          </Card>
          {/* Search Results */}
          <Card>
            <CardHeader>
              <CardTitle>Search Results ({searchResults.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {searchResults.map((log, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-3 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <Badge variant="outline" className={`${logLevelColors[log.level] ? 'border-current' : ''}`}>
                            {log.level}
                          </Badge>
                          <span className="text-sm text-gray-500">{log.source}</span>
                          <span className="text-xs text-gray-400">
                            {new Date(log.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm mb-2">{log.message}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          {log.correlation_id && (
                            <span>Correlation: {log.correlation_id}</span>
                          )}
                          {log.user_id && (
                            <span>User: {log.user_id}</span>
                          )}
                          {log.request_id && (
                            <span>Request: {log.request_id}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {searchResults.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No log entries found matching your search criteria</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        {/* Pattern Analysis Tab */}
        <TabsContent value="patterns" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>On-Demand Pattern Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Button
                  onClick={() => runPatternAnalysis('error_pattern')}
                  variant="outline"
                  className="h-24 flex-col"
                >
                  <AlertTriangle className="h-6 w-6 mb-2" />
                  <span>Error Patterns</span>
                  <span className="text-xs text-gray-500">Analyze recurring errors</span>
                </Button>
                <Button
                  onClick={() => runPatternAnalysis('performance_trend')}
                  variant="outline"
                  className="h-24 flex-col"
                >
                  <TrendingUp className="h-6 w-6 mb-2" />
                  <span>Performance Trends</span>
                  <span className="text-xs text-gray-500">Analyze response times</span>
                </Button>
                <Button
                  onClick={() => runPatternAnalysis('security_incident')}
                  variant="outline"
                  className="h-24 flex-col"
                >
                  <Shield className="h-6 w-6 mb-2" />
                  <span>Security Incidents</span>
                  <span className="text-xs text-gray-500">Detect security threats</span>
                </Button>
                <Button
                  onClick={() => runPatternAnalysis('usage_pattern')}
                  variant="outline"
                  className="h-24 flex-col"
                >
                  <BarChart3 className="h-6 w-6 mb-2" />
                  <span>Usage Patterns</span>
                  <span className="text-xs text-gray-500">Analyze user activity</span>
                </Button>
                <Button
                  onClick={() => runPatternAnalysis('anomaly_detection')}
                  variant="outline"
                  className="h-24 flex-col"
                >
                  <Eye className="h-6 w-6 mb-2" />
                  <span>Anomaly Detection</span>
                  <span className="text-xs text-gray-500">Detect unusual patterns</span>
                </Button>
                <Button
                  onClick={loadInsights}
                  variant="outline"
                  className="h-24 flex-col"
                >
                  <RefreshCw className="h-6 w-6 mb-2" />
                  <span>Refresh All</span>
                  <span className="text-xs text-gray-500">Run all analyses</span>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              Pattern analysis runs automatically every 5 minutes. Use these buttons to run on-demand analysis 
              for the last hour of logs. Results will appear in the Insights tab.
            </AlertDescription>
          </Alert>
        </TabsContent>
      </Tabs>
    </div>
  );
};
export default LogAnalytics;