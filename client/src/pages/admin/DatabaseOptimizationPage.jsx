import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  Activity, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  BarChart,
  RefreshCw,
  Settings,
  Download,
  Search,
  Filter,
  Play,
  Pause,
  ChevronDown,
  ChevronRight,
  Plus
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/toast';
const queryCategories = [
  { id: 'slow', label: 'Slow Queries', color: 'red' },
  { id: 'frequent', label: 'Frequent Queries', color: 'yellow' },
  { id: 'complex', label: 'Complex Queries', color: 'orange' },
  { id: 'optimized', label: 'Optimized', color: 'green' }
];
const DatabaseOptimizationPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [queries, setQueries] = useState([]);
  const [metrics, setMetrics] = useState({
    avgQueryTime: 0,
    totalQueries: 0,
    slowQueries: 0,
    cacheHitRate: 0,
    dbSize: '0 MB',
    indexUsage: 0,
    connectionPool: {
      active: 0,
      idle: 0,
      total: 0
    }
  });
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [optimizationSuggestions, setOptimizationSuggestions] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [indexAnalysis, setIndexAnalysis] = useState([]);
  const [queryHistory, setQueryHistory] = useState([]);
  useEffect(() => {
    fetchMetrics();
    fetchSlowQueries();
    fetchIndexAnalysis();
  }, []);
  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(() => {
        fetchMetrics();
        fetchQueryHistory();
      }, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [isMonitoring]);
  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/admin/database/metrics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };
  const fetchSlowQueries = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/database/slow-queries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQueries(data.queries || []);
      }
    } catch (error) {
      console.error('Error fetching queries:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchIndexAnalysis = async () => {
    try {
      const response = await fetch('/api/admin/database/index-analysis', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setIndexAnalysis(data.indexes || []);
      }
    } catch (error) {
      console.error('Error fetching index analysis:', error);
    }
  };
  const fetchQueryHistory = async () => {
    try {
      const response = await fetch('/api/admin/database/query-history', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQueryHistory(data.history || []);
      }
    } catch (error) {
      console.error('Error fetching query history:', error);
    }
  };
  const analyzeQuery = async (queryId) => {
    try {
      const response = await fetch(`/api/admin/database/analyze-query/${queryId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setOptimizationSuggestions(data.suggestions);
        setSelectedQuery(data.query);
        showToast('Query analysis completed', 'success');
      }
    } catch (error) {
      showToast('Error analyzing query', 'error');
    }
  };
  const optimizeQuery = async (queryId, optimization) => {
    try {
      const response = await fetch(`/api/admin/database/optimize-query/${queryId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ optimization })
      });
      if (response.ok) {
        showToast('Query optimized successfully', 'success');
        fetchSlowQueries();
      }
    } catch (error) {
      showToast('Error optimizing query', 'error');
    }
  };
  const createIndex = async (table, columns) => {
    try {
      const response = await fetch('/api/admin/database/create-index', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ table, columns })
      });
      if (response.ok) {
        showToast('Index created successfully', 'success');
        fetchIndexAnalysis();
      }
    } catch (error) {
      showToast('Error creating index', 'error');
    }
  };
  const exportReport = async (format = 'pdf') => {
    try {
      const response = await fetch(`/api/admin/database/export-report?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `database-optimization-report.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      showToast('Error exporting report', 'error');
    }
  };
  const getDurationColor = (duration) => {
    if (duration > 1000) return 'text-red-600';
    if (duration > 500) return 'text-yellow-600';
    return 'text-green-600';
  };
  const formatDuration = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Query Time</p>
              <p className={`text-2xl font-bold ${getDurationColor(metrics.avgQueryTime)}`}>
                {formatDuration(metrics.avgQueryTime)}
              </p>
            </div>
            <Clock className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Slow Queries</p>
              <p className="text-2xl font-bold text-red-600">{metrics.slowQueries}</p>
              <p className="text-xs text-gray-500">Last 24h</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Cache Hit Rate</p>
              <p className="text-2xl font-bold text-green-600">
                {(metrics.cacheHitRate * 100).toFixed(1)}%
              </p>
            </div>
            <Zap className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Index Usage</p>
              <p className="text-2xl font-bold">
                {(metrics.indexUsage * 100).toFixed(1)}%
              </p>
            </div>
            <Database className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
      </div>
      {/* Connection Pool Status */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Connection Pool Status</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{metrics.connectionPool.active}</p>
            <p className="text-sm text-gray-600">Active</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-yellow-600">{metrics.connectionPool.idle}</p>
            <p className="text-sm text-gray-600">Idle</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">{metrics.connectionPool.total}</p>
            <p className="text-sm text-gray-600">Total</p>
          </div>
        </div>
      </Card>
      {/* Real-time Monitoring */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">Real-time Monitoring</h3>
          <Button
            onClick={() => setIsMonitoring(!isMonitoring)}
            variant={isMonitoring ? 'secondary' : 'primary'}
            size="sm"
          >
            {isMonitoring ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Stop Monitoring
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Monitoring
              </>
            )}
          </Button>
        </div>
        {isMonitoring && queryHistory.length > 0 && (
          <div className="space-y-2">
            {queryHistory.slice(0, 5).map((query, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm truncate flex-1">{query.query}</span>
                <span className={`text-sm font-medium ${getDurationColor(query.duration)}`}>
                  {formatDuration(query.duration)}
                </span>
              </div>
            ))}
          </div>
        )}
        {isMonitoring && queryHistory.length === 0 && (
          <p className="text-gray-600 text-center py-4">Monitoring active queries...</p>
        )}
      </Card>
      {/* Top Slow Queries */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">Top Slow Queries</h3>
          <Button
            onClick={() => setActiveTab('queries')}
            variant="secondary"
            size="sm"
          >
            View All
          </Button>
        </div>
        <div className="space-y-3">
          {queries.slice(0, 5).map(query => (
            <div key={query.id} className="border rounded-lg p-3">
              <div className="flex justify-between items-start mb-2">
                <code className="text-sm bg-gray-50 p-2 rounded flex-1 mr-4">
                  {query.query.substring(0, 100)}...
                </code>
                <span className={`font-medium ${getDurationColor(query.avgDuration)}`}>
                  {formatDuration(query.avgDuration)}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm text-gray-600">
                <span>Executed {query.count} times</span>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => analyzeQuery(query.id)}
                >
                  Analyze
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
  const renderQueries = () => (
    <div className="space-y-6">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">Query Analysis</h3>
          <div className="flex space-x-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => exportReport('csv')}
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => exportReport('pdf')}
            >
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </Button>
          </div>
        </div>
        {/* Filters */}
        <div className="flex space-x-4 mb-4">
          {queryCategories.map(category => (
            <label key={category.id} className="flex items-center cursor-pointer">
              <input type="checkbox" className="mr-2" defaultChecked />
              <span className={`text-sm font-medium text-${category.color}-600`}>
                {category.label}
              </span>
            </label>
          ))}
        </div>
        {/* Query List */}
        <div className="space-y-4">
          {queries.map(query => (
            <div key={query.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <code className="text-sm bg-gray-50 p-3 rounded block overflow-x-auto">
                    {query.query}
                  </code>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Avg Duration</p>
                  <p className={`font-medium ${getDurationColor(query.avgDuration)}`}>
                    {formatDuration(query.avgDuration)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Executions</p>
                  <p className="font-medium">{query.count}</p>
                </div>
                <div>
                  <p className="text-gray-600">Total Time</p>
                  <p className="font-medium">{formatDuration(query.totalDuration)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Last Run</p>
                  <p className="font-medium">
                    {new Date(query.lastExecution).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <div className="flex justify-between items-center mt-3">
                <div className="flex space-x-2">
                  {query.tags?.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => analyzeQuery(query.id)}
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Analyze
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => optimizeQuery(query.id, 'auto')}
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    Optimize
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
      {/* Query Analysis Results */}
      {selectedQuery && (
        <Card>
          <h3 className="font-semibold text-lg mb-4">Analysis Results</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Execution Plan</h4>
              <pre className="bg-gray-50 p-3 rounded text-sm overflow-x-auto">
                {selectedQuery.executionPlan}
              </pre>
            </div>
            <div>
              <h4 className="font-medium mb-2">Optimization Suggestions</h4>
              {optimizationSuggestions.length === 0 ? (
                <p className="text-gray-600">No optimization suggestions available</p>
              ) : (
                <div className="space-y-3">
                  {optimizationSuggestions.map((suggestion, index) => (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex items-start space-x-2 mb-2">
                        {suggestion.priority === 'high' ? (
                          <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                        ) : (
                          <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <p className="font-medium">{suggestion.title}</p>
                          <p className="text-sm text-gray-600">{suggestion.description}</p>
                        </div>
                      </div>
                      {suggestion.action && (
                        <Button
                          size="sm"
                          onClick={() => optimizeQuery(selectedQuery.id, suggestion.action)}
                        >
                          Apply Fix
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
  const renderIndexes = () => (
    <div className="space-y-6">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">Index Analysis</h3>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Create Index
          </Button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Table</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Index Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Columns</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {indexAnalysis.map(index => (
                <tr key={index.id}>
                  <td className="px-4 py-3 text-sm">{index.table}</td>
                  <td className="px-4 py-3 text-sm font-mono">{index.name}</td>
                  <td className="px-4 py-3 text-sm">{index.columns.join(', ')}</td>
                  <td className="px-4 py-3 text-sm">{index.size}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{ width: `${index.usage * 100}%` }}
                        />
                      </div>
                      <span className="text-sm">{(index.usage * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {index.status === 'optimal' ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Optimal
                      </span>
                    ) : index.status === 'unused' ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        Unused
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Needs Optimization
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <Button size="sm" variant="ghost">
                      <Settings className="w-4 h-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      {/* Missing Indexes */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Recommended Indexes</h3>
        <div className="space-y-3">
          {[
            { table: 'users', columns: ['email'], impact: 'high', queries: 245 },
            { table: 'sessions', columns: ['user_id', 'created_at'], impact: 'medium', queries: 156 },
            { table: 'documents', columns: ['category_id', 'status'], impact: 'low', queries: 89 }
          ].map((recommendation, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">
                    Create index on {recommendation.table}({recommendation.columns.join(', ')})
                  </p>
                  <p className="text-sm text-gray-600">
                    Would improve {recommendation.queries} queries
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium
                    ${recommendation.impact === 'high' ? 'bg-red-100 text-red-800' :
                      recommendation.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'}`}>
                    {recommendation.impact} impact
                  </span>
                  <Button
                    size="sm"
                    onClick={() => createIndex(recommendation.table, recommendation.columns)}
                  >
                    Create
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
  const renderPerformance = () => (
    <div className="space-y-6">
      {/* Performance Trends */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Performance Trends</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
          <p className="text-gray-600">Performance chart would go here</p>
        </div>
      </Card>
      {/* Table Analysis */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Table Analysis</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Table</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rows</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Row Length</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fragmentation</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {[
                { name: 'users', rows: 15420, size: '12.4 MB', avgRow: '823 B', fragmentation: 5 },
                { name: 'sessions', rows: 234567, size: '156.7 MB', avgRow: '701 B', fragmentation: 12 },
                { name: 'documents', rows: 4521, size: '45.2 MB', avgRow: '10.5 KB', fragmentation: 8 },
                { name: 'messages', rows: 89234, size: '67.8 MB', avgRow: '798 B', fragmentation: 15 }
              ].map(table => (
                <tr key={table.name}>
                  <td className="px-4 py-3 text-sm font-medium">{table.name}</td>
                  <td className="px-4 py-3 text-sm">{table.rows.toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm">{table.size}</td>
                  <td className="px-4 py-3 text-sm">{table.avgRow}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            table.fragmentation > 10 ? 'bg-red-500' :
                            table.fragmentation > 5 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${table.fragmentation}%` }}
                        />
                      </div>
                      <span className="text-sm">{table.fragmentation}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Button
                      size="sm"
                      variant="secondary"
                      disabled={table.fragmentation < 10}
                    >
                      Optimize
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      {/* Optimization Recommendations */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Optimization Recommendations</h3>
        <div className="space-y-3">
          {[
            {
              title: 'Enable Query Cache',
              description: 'Query cache is currently disabled. Enabling it could improve performance by 15-20%',
              impact: 'high',
              effort: 'low'
            },
            {
              title: 'Increase Buffer Pool Size',
              description: 'Current buffer pool is 128MB. Increasing to 512MB would better utilize available memory',
              impact: 'high',
              effort: 'medium'
            },
            {
              title: 'Optimize Slow Log Settings',
              description: 'Adjust slow query log threshold from 10s to 1s to catch more problematic queries',
              impact: 'medium',
              effort: 'low'
            },
            {
              title: 'Implement Table Partitioning',
              description: 'Large tables like sessions could benefit from date-based partitioning',
              impact: 'high',
              effort: 'high'
            }
          ].map((recommendation, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="font-medium mb-1">{recommendation.title}</h4>
                  <p className="text-sm text-gray-600">{recommendation.description}</p>
                  <div className="flex space-x-4 mt-2">
                    <span className="text-xs">
                      Impact: <span className={`font-medium
                        ${recommendation.impact === 'high' ? 'text-red-600' :
                          recommendation.impact === 'medium' ? 'text-yellow-600' :
                          'text-green-600'}`}>
                        {recommendation.impact}
                      </span>
                    </span>
                    <span className="text-xs">
                      Effort: <span className={`font-medium
                        ${recommendation.effort === 'high' ? 'text-red-600' :
                          recommendation.effort === 'medium' ? 'text-yellow-600' :
                          'text-green-600'}`}>
                        {recommendation.effort}
                      </span>
                    </span>
                  </div>
                </div>
                <Button size="sm">
                  Implement
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Database Optimization</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary"
        >
          Back to Settings
        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'queries', 'indexes', 'performance'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>
      {/* Tab Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'queries' && renderQueries()}
          {activeTab === 'indexes' && renderIndexes()}
          {activeTab === 'performance' && renderPerformance()}
        </>
      )}
    </div>
  );
};
export default DatabaseOptimizationPage;