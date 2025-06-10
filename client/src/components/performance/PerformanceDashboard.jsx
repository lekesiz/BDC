import React, { useState, useEffect, useCallback } from 'react';
import { 
  Zap, 
  Database, 
  Server, 
  Activity,
  Clock,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  HardDrive,
  Wifi,
  RefreshCw,
  Download,
  Settings,
  BarChart3
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
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer as RechartsResponsiveContainer
} from 'recharts';

const PerformanceDashboard = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [cacheStats, setCacheStats] = useState(null);
  const [compressionStats, setCompressionStats] = useState(null);
  const [queryMetrics, setQueryMetrics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');

  const fetchPerformanceData = useCallback(async () => {
    try {
      const [perfResponse, cacheResponse, compressionResponse, queryResponse] = await Promise.all([
        api.get('/api/v2/performance/metrics'),
        api.get('/api/v2/performance/cache-stats'),
        api.get('/api/v2/performance/compression-stats'),
        api.get('/api/v2/performance/query-metrics')
      ]);

      setPerformanceData(perfResponse.data);
      setCacheStats(cacheResponse.data);
      setCompressionStats(compressionResponse.data);
      setQueryMetrics(queryResponse.data.metrics || []);
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPerformanceData();
  }, [fetchPerformanceData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchPerformanceData, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, [autoRefresh, fetchPerformanceData]);

  const getPerformanceScore = () => {
    if (!performanceData) return 0;
    
    const { query_performance, cache_performance, system_performance } = performanceData;
    
    // Calculate composite score
    let score = 100;
    
    // Deduct for slow queries
    if (query_performance?.slow_queries > 0) {
      score -= Math.min(20, query_performance.slow_queries * 2);
    }
    
    // Deduct for low cache hit rate
    if (cache_performance?.hit_rate < 60) {
      score -= Math.min(20, (60 - cache_performance.hit_rate) * 0.5);
    }
    
    // Deduct for high resource usage
    if (system_performance?.cpu_percent > 70) {
      score -= Math.min(15, (system_performance.cpu_percent - 70) * 0.5);
    }
    if (system_performance?.memory_percent > 80) {
      score -= Math.min(15, (system_performance.memory_percent - 80) * 0.5);
    }
    
    return Math.max(0, Math.round(score));
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const exportPerformanceReport = async () => {
    try {
      const response = await api.get('/api/v2/performance/export', {
        params: { format: 'pdf' }
      });
      
      // Handle file download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `performance-report-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export performance report:', error);
    }
  };

  if (isLoading) {
    return (
      <ResponsiveContainer>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <RefreshCw className="h-6 w-6 animate-spin" />
            <span>Loading performance data...</span>
          </div>
        </div>
      </ResponsiveContainer>
    );
  }

  const performanceScore = getPerformanceScore();

  return (
    <ResponsiveContainer>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Performance Dashboard</h1>
            <p className="text-sm text-gray-500">
              System performance monitoring and optimization
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
            
            <Button
              variant="outline"
              size="sm"
              onClick={exportPerformanceReport}
            >
              <Download className="h-4 w-4 mr-2" />
              Export Report
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
              onClick={fetchPerformanceData}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Performance Score */}
        <ResponsiveCard>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className={cn(
                    'text-4xl font-bold',
                    getScoreColor(performanceScore)
                  )}>
                    {performanceScore}
                  </div>
                  <div className="text-sm text-gray-500">Performance Score</div>
                </div>
                
                <div className="h-16 w-px bg-gray-200" />
                
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Cache Hit Rate: {cacheStats?.hit_rate || 0}%</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Activity className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">
                      Avg Response Time: {performanceData?.query_performance?.avg_query_time?.toFixed(1) || 0}ms
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm">
                      Compression Savings: {compressionStats?.mb_saved || 0}MB
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <PerformanceSparkline data={queryMetrics} />
              </div>
            </div>
          </CardContent>
        </ResponsiveCard>

        {/* Key Metrics */}
        <ResponsiveGrid cols={{ default: 1, sm: 2, lg: 4 }}>
          {/* Query Performance */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Database className="h-5 w-5 text-blue-500" />
                  <h3 className="font-medium">Query Performance</h3>
                </div>
                {performanceData?.query_performance?.slow_queries > 0 && (
                  <Badge variant="warning">
                    {performanceData.query_performance.slow_queries} slow
                  </Badge>
                )}
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Queries</span>
                  <span className="text-sm font-medium">
                    {performanceData?.query_performance?.total_queries || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Optimized</span>
                  <span className="text-sm font-medium">
                    {performanceData?.query_performance?.optimized_queries || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Avg Time</span>
                  <span className="text-sm font-medium">
                    {performanceData?.query_performance?.avg_query_time?.toFixed(1) || 0}ms
                  </span>
                </div>
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Cache Performance */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Server className="h-5 w-5 text-green-500" />
                  <h3 className="font-medium">Cache Performance</h3>
                </div>
                <Badge variant={cacheStats?.hit_rate > 70 ? 'success' : 'warning'}>
                  {cacheStats?.hit_rate || 0}%
                </Badge>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Hits</span>
                  <span className="text-sm font-medium">
                    {cacheStats?.performance?.hit_count || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Misses</span>
                  <span className="text-sm font-medium">
                    {cacheStats?.performance?.miss_count || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Memory Used</span>
                  <span className="text-sm font-medium">
                    {cacheStats?.memory_cache?.size_mb || 0}MB
                  </span>
                </div>
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Compression Stats */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-purple-500" />
                  <h3 className="font-medium">Compression</h3>
                </div>
                <Badge variant="info">
                  {compressionStats?.enabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Saved</span>
                  <span className="text-sm font-medium">
                    {compressionStats?.mb_saved || 0}MB
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Compressed</span>
                  <span className="text-sm font-medium">
                    {compressionStats?.total_compressed || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Algorithms</span>
                  <span className="text-sm font-medium">
                    {compressionStats?.algorithms?.join(', ') || 'None'}
                  </span>
                </div>
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* System Resources */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5 text-orange-500" />
                  <h3 className="font-medium">System Resources</h3>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">CPU Usage</span>
                  <span className={cn(
                    'text-sm font-medium',
                    performanceData?.system_performance?.cpu_percent > 70 ? 'text-red-600' : ''
                  )}>
                    {performanceData?.system_performance?.cpu_percent?.toFixed(1) || 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Memory Usage</span>
                  <span className={cn(
                    'text-sm font-medium',
                    performanceData?.system_performance?.memory_percent > 80 ? 'text-red-600' : ''
                  )}>
                    {performanceData?.system_performance?.memory_percent?.toFixed(1) || 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Connections</span>
                  <span className="text-sm font-medium">
                    {performanceData?.system_performance?.active_connections || 0}
                  </span>
                </div>
              </div>
            </CardContent>
          </ResponsiveCard>
        </ResponsiveGrid>

        {/* Performance Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Query Performance Chart */}
          <ResponsiveCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Query Performance Trends</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <RechartsResponsiveContainer width="100%" height={250}>
                <AreaChart data={queryMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value, name) => [
                      name === 'execution_time' ? `${value.toFixed(2)}ms` : value,
                      name
                    ]}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="execution_time" 
                    stroke="#3b82f6" 
                    fill="#3b82f6" 
                    fillOpacity={0.3}
                    name="Execution Time"
                  />
                </AreaChart>
              </RechartsResponsiveContainer>
            </CardContent>
          </ResponsiveCard>

          {/* Cache Hit Rate Chart */}
          <ResponsiveCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Server className="h-5 w-5" />
                <span>Cache Performance</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <RechartsResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Cache Hits', value: cacheStats?.performance?.hit_count || 0 },
                      { name: 'Cache Misses', value: cacheStats?.performance?.miss_count || 0 }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill="#10b981" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </RechartsResponsiveContainer>
            </CardContent>
          </ResponsiveCard>
        </div>

        {/* Recommendations */}
        {performanceData?.recommendations && performanceData.recommendations.length > 0 && (
          <ResponsiveCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <span>Performance Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {performanceData.recommendations.map((recommendation, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg"
                  >
                    <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" />
                    <p className="text-sm text-yellow-800">{recommendation}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </ResponsiveCard>
        )}
      </div>
    </ResponsiveContainer>
  );
};

// Performance Sparkline Component
const PerformanceSparkline = ({ data }) => {
  const recentData = data.slice(-20); // Last 20 data points
  
  return (
    <div className="w-32 h-12">
      <RechartsResponsiveContainer width="100%" height="100%">
        <LineChart data={recentData}>
          <Line
            type="monotone"
            dataKey="execution_time"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </RechartsResponsiveContainer>
    </div>
  );
};

export default PerformanceDashboard;