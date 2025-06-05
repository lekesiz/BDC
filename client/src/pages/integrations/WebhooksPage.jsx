import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Webhook, 
  Link, 
  Settings, 
  CheckCircle,
  XCircle,
  AlertCircle,
  Send,
  Shield,
  Activity,
  Code,
  Clock,
  RefreshCw,
  Eye,
  Copy,
  Trash2,
  Edit,
  Plus,
  Filter
} from 'lucide-react';
import { LineChart, Line, BarChart as RechartsBarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
const WebhooksPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [webhooks, setWebhooks] = useState([]);
  const [webhookStats, setWebhookStats] = useState({
    totalWebhooks: 12,
    activeWebhooks: 9,
    totalCalls: 45678,
    successRate: 98.5,
    avgResponseTime: 145,
    failedCalls: 234,
    pendingRetries: 12
  });
  useEffect(() => {
    const mockWebhooks = [
      { 
        id: 1, 
        name: 'User Registration', 
        url: 'https://api.example.com/user-created',
        events: ['user.created', 'user.verified'],
        status: 'active',
        lastTriggered: '2024-11-17 15:30',
        successRate: 99.5
      },
      { 
        id: 2, 
        name: 'Payment Processor', 
        url: 'https://payments.example.com/webhook',
        events: ['payment.completed', 'payment.failed'],
        status: 'active',
        lastTriggered: '2024-11-17 15:28',
        successRate: 98.2
      },
      { 
        id: 3, 
        name: 'CRM Sync', 
        url: 'https://crm.example.com/sync',
        events: ['beneficiary.updated', 'program.created'],
        status: 'active',
        lastTriggered: '2024-11-17 15:25',
        successRate: 97.8
      },
      { 
        id: 4, 
        name: 'Analytics Service', 
        url: 'https://analytics.example.com/events',
        events: ['test.completed', 'course.finished'],
        status: 'inactive',
        lastTriggered: '2024-11-17 10:15',
        successRate: 94.5
      }
    ];
    setWebhooks(mockWebhooks);
  }, []);
  const webhookActivity = [
    { hour: '00:00', calls: 234, success: 232, failed: 2 },
    { hour: '04:00', calls: 189, success: 187, failed: 2 },
    { hour: '08:00', calls: 456, success: 450, failed: 6 },
    { hour: '12:00', calls: 678, success: 665, failed: 13 },
    { hour: '16:00', calls: 589, success: 578, failed: 11 },
    { hour: '20:00', calls: 345, success: 340, failed: 5 }
  ];
  const eventTypes = [
    { event: 'user.created', count: 12345, percentage: 27 },
    { event: 'payment.completed', count: 8967, percentage: 20 },
    { event: 'test.completed', count: 7234, percentage: 16 },
    { event: 'beneficiary.updated', count: 6789, percentage: 15 },
    { event: 'course.finished', count: 5432, percentage: 12 },
    { event: 'other', count: 4567, percentage: 10 }
  ];
  const recentLogs = [
    { 
      id: 1, 
      timestamp: '2024-11-17 15:30:45', 
      event: 'user.created',
      webhook: 'User Registration',
      status: 'success',
      responseCode: 200,
      duration: 123
    },
    { 
      id: 2, 
      timestamp: '2024-11-17 15:29:12', 
      event: 'payment.completed',
      webhook: 'Payment Processor',
      status: 'success',
      responseCode: 200,
      duration: 156
    },
    { 
      id: 3, 
      timestamp: '2024-11-17 15:28:33', 
      event: 'beneficiary.updated',
      webhook: 'CRM Sync',
      status: 'failed',
      responseCode: 500,
      duration: 2456
    },
    { 
      id: 4, 
      timestamp: '2024-11-17 15:27:55', 
      event: 'test.completed',
      webhook: 'Analytics Service',
      status: 'success',
      responseCode: 201,
      duration: 89
    }
  ];
  const availableEvents = [
    { category: 'User Events', events: ['user.created', 'user.updated', 'user.deleted', 'user.verified'] },
    { category: 'Payment Events', events: ['payment.completed', 'payment.failed', 'payment.refunded'] },
    { category: 'Course Events', events: ['course.enrolled', 'course.started', 'course.finished'] },
    { category: 'Test Events', events: ['test.created', 'test.started', 'test.completed', 'test.graded'] },
    { category: 'Beneficiary Events', events: ['beneficiary.created', 'beneficiary.updated', 'beneficiary.assigned'] }
  ];
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'webhooks', label: 'Webhooks', icon: Webhook },
    { id: 'logs', label: 'Logs', icon: Code },
    { id: 'events', label: 'Events', icon: Send },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">API Webhooks</h1>
        <Button variant="primary">
          <Plus className="w-4 h-4 mr-2" />
          Create Webhook
        </Button>
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
                    <p className="text-sm text-gray-600">Active Webhooks</p>
                    <p className="text-2xl font-bold text-gray-900">{webhookStats.activeWebhooks}/{webhookStats.totalWebhooks}</p>
                    <p className="text-xs text-gray-500 mt-1">Configured endpoints</p>
                  </div>
                  <Webhook className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Calls</p>
                    <p className="text-2xl font-bold text-gray-900">{webhookStats.totalCalls.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
                  </div>
                  <Send className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold text-green-600">{webhookStats.successRate}%</p>
                    <p className="text-xs text-gray-500 mt-1">Last 7 days</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Avg Response</p>
                    <p className="text-2xl font-bold text-gray-900">{webhookStats.avgResponseTime}ms</p>
                    <p className="text-xs text-gray-500 mt-1">Response time</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Webhook Activity</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={webhookActivity}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="hour" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="calls" stroke="#3B82F6" name="Total Calls" />
                      <Line type="monotone" dataKey="success" stroke="#10B981" name="Successful" />
                      <Line type="monotone" dataKey="failed" stroke="#EF4444" name="Failed" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Event Distribution</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={eventTypes}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ event, percentage }) => `${event} (${percentage}%)`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {eventTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
          </div>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">System Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                    <div>
                      <p className="font-medium text-green-900">API Status</p>
                      <p className="text-sm text-green-700">All systems operational</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-yellow-50 rounded-lg">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-yellow-600 mr-3" />
                    <div>
                      <p className="font-medium text-yellow-900">Pending Retries</p>
                      <p className="text-sm text-yellow-700">{webhookStats.pendingRetries} webhooks queued</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center">
                    <Activity className="w-5 h-5 text-blue-600 mr-3" />
                    <div>
                      <p className="font-medium text-blue-900">Rate Limiting</p>
                      <p className="text-sm text-blue-700">1000 requests/minute</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'webhooks' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Configured Webhooks</h3>
                <div className="flex space-x-2">
                  <Button variant="secondary" size="sm">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="primary" size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Webhook
                  </Button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">URL</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Events</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Triggered</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {webhooks.map((webhook) => (
                      <tr key={webhook.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {webhook.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="max-w-xs truncate">
                            {webhook.url}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {webhook.events.length} events
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${webhook.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                            {webhook.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center">
                            <span>{webhook.successRate}%</span>
                            <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: `${webhook.successRate}%` }}></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {webhook.lastTriggered}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
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
              <h3 className="text-lg font-semibold mb-4">Webhook Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Webhook Name
                  </label>
                  <Input type="text" placeholder="Enter webhook name" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Endpoint URL
                  </label>
                  <Input type="url" placeholder="https://api.example.com/webhook" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea 
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    rows="3"
                    placeholder="Describe what this webhook does..."
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Headers
                  </label>
                  <div className="space-y-2">
                    <div className="flex space-x-2">
                      <Input type="text" placeholder="Header name" className="flex-1" />
                      <Input type="text" placeholder="Header value" className="flex-1" />
                      <Button variant="secondary" size="sm">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Secret Key
                  </label>
                  <div className="flex space-x-2">
                    <Input type="password" placeholder="Webhook secret for signature verification" className="flex-1" />
                    <Button variant="secondary" size="sm">
                      Generate
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'logs' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Webhook Logs</h3>
                <div className="flex space-x-2">
                  <Button variant="secondary" size="sm">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="secondary" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Webhook</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Response</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {recentLogs.map((log) => (
                      <tr key={log.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {log.timestamp}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.event}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {log.webhook}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${log.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {log.responseCode}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {log.duration}ms
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <Button variant="ghost" size="sm">View Details</Button>
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
              <h3 className="text-lg font-semibold mb-4">Log Details</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Request Headers</h4>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
{`{
  "Content-Type": "application/json",
  "X-Webhook-Signature": "sha256=...",
  "X-Event-Type": "user.created",
  "X-Request-ID": "abc123..."
}`}
                  </pre>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Request Body</h4>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
{`{
  "event": "user.created",
  "data": {
    "user_id": "usr_123",
    "email": "john.doe@example.com",
    "created_at": "2024-11-17T15:30:45Z"
  }
}`}
                  </pre>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Response</h4>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
{`{
  "status": "success",
  "message": "Webhook processed successfully"
}`}
                  </pre>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'events' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Available Events</h3>
              <div className="space-y-6">
                {availableEvents.map((category) => (
                  <div key={category.category}>
                    <h4 className="font-medium text-gray-900 mb-3">{category.category}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {category.events.map((event) => (
                        <div key={event} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium">{event}</p>
                            <p className="text-sm text-gray-500">Triggered when {event.replace('.', ' is ')}</p>
                          </div>
                          <label className="flex items-center">
                            <input type="checkbox" className="mr-2" />
                            <span className="text-sm">Subscribe</span>
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Event Testing</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Event
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>user.created</option>
                    <option>payment.completed</option>
                    <option>test.completed</option>
                    <option>course.finished</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Payload
                  </label>
                  <textarea 
                    className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                    rows="10"
                    defaultValue={`{
  "event": "user.created",
  "data": {
    "user_id": "test_123",
    "email": "test@example.com",
    "created_at": "2024-11-17T15:30:45Z"
  }
}`}
                  />
                </div>
                <Button variant="primary">
                  <Send className="w-4 h-4 mr-2" />
                  Send Test Event
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'security' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable signature verification</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Verify webhook signatures to ensure requests are from authorized sources
                  </p>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">SSL/TLS only</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Only send webhooks to HTTPS endpoints
                  </p>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">IP whitelisting</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Restrict webhook delivery to specific IP addresses
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Request timeout (seconds)
                  </label>
                  <Input type="number" defaultValue="30" min="5" max="60" />
                </div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">API Keys</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Production API Key</p>
                    <p className="text-sm text-gray-500">Created on 2024-10-15</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <code className="px-2 py-1 bg-gray-100 rounded text-sm">sk_live_...4a7f</code>
                    <Button variant="ghost" size="sm">
                      <Copy className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Test API Key</p>
                    <p className="text-sm text-gray-500">Created on 2024-10-15</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <code className="px-2 py-1 bg-gray-100 rounded text-sm">sk_test_...9b2c</code>
                    <Button variant="ghost" size="sm">
                      <Copy className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                <Button variant="primary">
                  <Plus className="w-4 h-4 mr-2" />
                  Generate New API Key
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'settings' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Webhook Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Retry attempts
                  </label>
                  <Input type="number" defaultValue="3" min="0" max="5" />
                  <p className="text-xs text-gray-500 mt-1">
                    Number of times to retry failed webhook deliveries
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Retry delay (seconds)
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>30</option>
                    <option>60</option>
                    <option>300</option>
                    <option>600</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Time to wait between retry attempts
                  </p>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable exponential backoff</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Increase delay between retries exponentially
                  </p>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="font-medium">Disable failed endpoints</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically disable webhooks after repeated failures
                  </p>
                </div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Rate Limiting</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Requests per minute
                    </label>
                    <Input type="number" defaultValue="1000" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Burst limit
                    </label>
                    <Input type="number" defaultValue="100" />
                  </div>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable rate limiting per endpoint</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Apply different rate limits to different webhook endpoints
                  </p>
                </div>
                <div className="pt-4">
                  <Button variant="primary">Save Settings</Button>
                </div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Event Filtering</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="font-medium">Enable event filtering</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Filter events based on custom conditions before sending webhooks
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter Rules
                  </label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <select className="form-select rounded-md border-gray-300">
                        <option>user.role</option>
                        <option>payment.amount</option>
                        <option>test.score</option>
                      </select>
                      <select className="form-select rounded-md border-gray-300">
                        <option>equals</option>
                        <option>greater than</option>
                        <option>less than</option>
                        <option>contains</option>
                      </select>
                      <Input type="text" placeholder="Value" />
                      <Button variant="ghost" size="sm">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm" className="mt-2">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Filter Rule
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
export default WebhooksPage;