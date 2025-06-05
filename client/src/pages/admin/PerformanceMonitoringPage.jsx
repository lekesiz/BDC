import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Activity, 
  Zap, 
  Server, 
  Monitor,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Clock,
  BarChart3,
  Database,
  HardDrive,
  Cpu,
  MemoryStick,
  Globe,
  AlertCircle
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
const PerformanceMonitoringPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [metrics, setMetrics] = useState({
    responseTime: 124,
    uptime: 99.98,
    errorRate: 0.12,
    throughput: 3450,
    cpuUsage: 45,
    memoryUsage: 67,
    diskUsage: 72,
    networkIO: 85
  });
  const performanceData = [
    { time: '00:00', responseTime: 120, requests: 2500, errors: 3 },
    { time: '04:00', responseTime: 110, requests: 1800, errors: 1 },
    { time: '08:00', responseTime: 145, requests: 3800, errors: 5 },
    { time: '12:00', responseTime: 185, requests: 4500, errors: 8 },
    { time: '16:00', responseTime: 165, requests: 4200, errors: 6 },
    { time: '20:00', responseTime: 135, requests: 3000, errors: 4 },
    { time: '24:00', responseTime: 125, requests: 2200, errors: 2 }
  ];
  const endpointPerformance = [
    { endpoint: '/api/users', avgTime: 85, calls: 12500, errorRate: 0.08 },
    { endpoint: '/api/beneficiaries', avgTime: 125, calls: 8900, errorRate: 0.15 },
    { endpoint: '/api/documents', avgTime: 245, calls: 5600, errorRate: 0.25 },
    { endpoint: '/api/reports', avgTime: 520, calls: 3200, errorRate: 0.32 },
    { endpoint: '/api/analytics', avgTime: 380, calls: 2800, errorRate: 0.18 }
  ];
  const systemResources = [
    { resource: 'CPU', usage: 45, threshold: 80 },
    { resource: 'Memory', usage: 67, threshold: 85 },
    { resource: 'Disk I/O', usage: 72, threshold: 90 },
    { resource: 'Network', usage: 38, threshold: 75 }
  ];
  const alerts = [
    { id: 1, type: 'warning', message: 'High memory usage detected (>80%)', time: '10 minutes ago' },
    { id: 2, type: 'error', message: 'API endpoint /api/reports response time >500ms', time: '1 hour ago' },
    { id: 3, type: 'info', message: 'Scheduled maintenance window approaching', time: '2 hours ago' },
    { id: 4, type: 'success', message: 'Performance optimization deployed successfully', time: '3 hours ago' }
  ];
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Monitor },
    { id: 'metrics', label: 'Metrics', icon: BarChart3 },
    { id: 'endpoints', label: 'Endpoints', icon: Globe },
    { id: 'resources', label: 'Resources', icon: Server },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'apm', label: 'APM Setup', icon: Activity }
  ];
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Performance Monitoring</h1>
        <div className="flex space-x-2">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="1h">Last 1 Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <Button variant="primary">
            <Activity className="w-4 h-4 mr-2" />
            Configure Alerts
          </Button>
        </div>
      </div>
      <div className="bg-white border-b">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Avg Response Time</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics.responseTime}ms</p>
                    <p className="text-xs text-green-600 flex items-center mt-1">
                      <TrendingDown className="w-3 h-3 mr-1" />
                      12% improvement
                    </p>
                  </div>
                  <Clock className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Uptime</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics.uptime}%</p>
                    <p className="text-xs text-gray-600 mt-1">Last 30 days</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Error Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics.errorRate}%</p>
                    <p className="text-xs text-red-600 flex items-center mt-1">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      0.05% increase
                    </p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Throughput</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics.throughput}/s</p>
                    <p className="text-xs text-gray-600 mt-1">Requests per second</p>
                  </div>
                  <Zap className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Response Time Trend</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="responseTime" stroke="#3B82F6" name="Response Time (ms)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Request Volume</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area type="monotone" dataKey="requests" stroke="#10B981" fill="#10B981" fillOpacity={0.6} name="Requests" />
                      <Area type="monotone" dataKey="errors" stroke="#EF4444" fill="#EF4444" fillOpacity={0.6} name="Errors" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
          </div>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">System Health</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="relative inline-flex">
                    <div className="w-24 h-24">
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          className="text-gray-200"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          strokeDasharray={`${2 * Math.PI * 36}`}
                          strokeDashoffset={`${2 * Math.PI * 36 * (1 - metrics.cpuUsage / 100)}`}
                          className="text-blue-500"
                        />
                      </svg>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-semibold">{metrics.cpuUsage}%</span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-600">CPU Usage</p>
                </div>
                <div className="text-center">
                  <div className="relative inline-flex">
                    <div className="w-24 h-24">
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          className="text-gray-200"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          strokeDasharray={`${2 * Math.PI * 36}`}
                          strokeDashoffset={`${2 * Math.PI * 36 * (1 - metrics.memoryUsage / 100)}`}
                          className="text-green-500"
                        />
                      </svg>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-semibold">{metrics.memoryUsage}%</span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-600">Memory Usage</p>
                </div>
                <div className="text-center">
                  <div className="relative inline-flex">
                    <div className="w-24 h-24">
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          className="text-gray-200"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          strokeDasharray={`${2 * Math.PI * 36}`}
                          strokeDashoffset={`${2 * Math.PI * 36 * (1 - metrics.diskUsage / 100)}`}
                          className="text-yellow-500"
                        />
                      </svg>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-semibold">{metrics.diskUsage}%</span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-600">Disk Usage</p>
                </div>
                <div className="text-center">
                  <div className="relative inline-flex">
                    <div className="w-24 h-24">
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          className="text-gray-200"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="36"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="none"
                          strokeDasharray={`${2 * Math.PI * 36}`}
                          strokeDashoffset={`${2 * Math.PI * 36 * (1 - metrics.networkIO / 100)}`}
                          className="text-purple-500"
                        />
                      </svg>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-semibold">{metrics.networkIO}%</span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-600">Network I/O</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'metrics' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Key Performance Indicators</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Apdex Score</h4>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900">0.94</span>
                    <span className="ml-2 text-sm text-gray-500">/ 1.0</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-green-600">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    <span>+0.02 from last week</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">First Contentful Paint</h4>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900">1.2</span>
                    <span className="ml-2 text-sm text-gray-500">seconds</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-green-600">
                    <TrendingDown className="w-4 h-4 mr-1" />
                    <span>-0.3s improvement</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Time to Interactive</h4>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900">2.8</span>
                    <span className="ml-2 text-sm text-gray-500">seconds</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-yellow-600">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    <span>No change</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Core Web Vitals - LCP</h4>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900">2.1</span>
                    <span className="ml-2 text-sm text-gray-500">seconds</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-green-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span>Good</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Core Web Vitals - FID</h4>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900">68</span>
                    <span className="ml-2 text-sm text-gray-500">ms</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-green-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span>Good</span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Core Web Vitals - CLS</h4>
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900">0.05</span>
                    <span className="ml-2 text-sm text-gray-500">score</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-green-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span>Good</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Application Metrics</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">24h Avg</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">7d Avg</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trend</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Database Queries/min</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2,845</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2,654</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2,501</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <TrendingUp className="w-4 h-4 text-red-500" />
                      </td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Cache Hit Rate</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">92%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">89%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">87%</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      </td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Active Sessions</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">1,234</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">1,156</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">1,089</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'endpoints' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Endpoint Performance</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Endpoint</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Response Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Calls/Hour</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Error Rate</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {endpointPerformance.map((endpoint) => (
                      <tr key={endpoint.endpoint}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{endpoint.endpoint}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.avgTime}ms</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.calls.toLocaleString()}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.errorRate}%</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${endpoint.avgTime < 200 ? 'bg-green-100 text-green-800' : 
                              endpoint.avgTime < 500 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'}`}>
                            {endpoint.avgTime < 200 ? 'Healthy' : endpoint.avgTime < 500 ? 'Slow' : 'Critical'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Response Time Distribution</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={endpointPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="endpoint" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="avgTime" fill="#3B82F6" name="Avg Response Time (ms)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'resources' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Resource Utilization</h3>
              <div className="space-y-4">
                {systemResources.map((resource) => (
                  <div key={resource.resource}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">{resource.resource}</span>
                      <span className="text-sm text-gray-500">{resource.usage}%</span>
                    </div>
                    <div className="relative">
                      <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                        <div
                          style={{ width: `${resource.usage}%` }}
                          className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center
                            ${resource.usage > resource.threshold ? 'bg-red-500' : 
                              resource.usage > resource.threshold * 0.8 ? 'bg-yellow-500' : 'bg-green-500'}`}
                        />
                      </div>
                      <div
                        style={{ left: `${resource.threshold}%` }}
                        className="absolute top-0 bottom-0 w-0.5 bg-red-600"
                      >
                        <span className="absolute -top-5 left-1/2 transform -translate-x-1/2 text-xs text-red-600">
                          {resource.threshold}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Database Performance</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Active Connections</span>
                    <span className="text-sm font-medium">45/100</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Query Queue</span>
                    <span className="text-sm font-medium">12</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Replication Lag</span>
                    <span className="text-sm font-medium">125ms</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Lock Waits/sec</span>
                    <span className="text-sm font-medium">0.8</span>
                  </div>
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Cache Performance</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Memory Used</span>
                    <span className="text-sm font-medium">3.2GB/4GB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Hit Rate</span>
                    <span className="text-sm font-medium text-green-600">92%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Evictions/hour</span>
                    <span className="text-sm font-medium">245</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Connections</span>
                    <span className="text-sm font-medium">128</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}
      {activeTab === 'alerts' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Alerts</h3>
                <Button variant="secondary" size="sm">
                  Configure Rules
                </Button>
              </div>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div key={alert.id} className={`p-4 rounded-lg flex items-start space-x-3
                    ${alert.type === 'error' ? 'bg-red-50 border border-red-200' :
                      alert.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                      alert.type === 'success' ? 'bg-green-50 border border-green-200' :
                      'bg-blue-50 border border-blue-200'}`}>
                    {alert.type === 'error' && <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />}
                    {alert.type === 'warning' && <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0" />}
                    {alert.type === 'success' && <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />}
                    {alert.type === 'info' && <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0" />}
                    <div className="flex-1">
                      <p className={`font-medium
                        ${alert.type === 'error' ? 'text-red-800' :
                          alert.type === 'warning' ? 'text-yellow-800' :
                          alert.type === 'success' ? 'text-green-800' :
                          'text-blue-800'}`}>
                        {alert.message}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">{alert.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Alert Rules</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">High Response Time</p>
                    <p className="text-sm text-gray-500">Alert when response time &gt; 500ms for 5 minutes</p>
                  </div>
                  <Button variant="ghost" size="sm">Edit</Button>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Error Rate Threshold</p>
                    <p className="text-sm text-gray-500">Alert when error rate &gt; 1% for 10 minutes</p>
                  </div>
                  <Button variant="ghost" size="sm">Edit</Button>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Resource Usage</p>
                    <p className="text-sm text-gray-500">Alert when CPU/Memory &gt; 85% for 15 minutes</p>
                  </div>
                  <Button variant="ghost" size="sm">Edit</Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'apm' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">New Relic Setup</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`# Install New Relic Python Agent
pip install newrelic
# newrelic.ini configuration
[newrelic]
license_key = YOUR_LICENSE_KEY
app_name = BDC Application
monitor_mode = true
log_level = info
ssl = true
# Flask Integration
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
@newrelic.agent.wsgi_application()
def application(environ, start_response):
    return app(environ, start_response)`}</code>
              </pre>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Datadog Setup</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`# Install Datadog Agent
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=YOUR_API_KEY \
DD_SITE="datadoghq.com" bash -c "$(curl -L \
https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
# Python Application Integration
from ddtrace import patch_all
patch_all()
# Environment Variables
export DD_ENV=production
export DD_SERVICE=bdc-api
export DD_VERSION=1.0.0
# Custom Metrics
from datadog import statsd
statsd.increment('api.request.count')
statsd.histogram('api.response.time', response_time)`}</code>
              </pre>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Budget</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Page Load Time Budget
                  </label>
                  <Input type="number" defaultValue="3000" placeholder="milliseconds" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time to Interactive Budget
                  </label>
                  <Input type="number" defaultValue="5000" placeholder="milliseconds" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    JavaScript Bundle Size Limit
                  </label>
                  <Input type="number" defaultValue="500" placeholder="KB" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Image Size Limit
                  </label>
                  <Input type="number" defaultValue="200" placeholder="KB per image" />
                </div>
                <Button variant="primary">Save Performance Budget</Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
export default PerformanceMonitoringPage;