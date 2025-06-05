import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Alert } from '../../ui/alert';
import { Input } from '../../ui/input';
import {
  Webhook,
  Globe,
  Zap,
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Code,
  Key,
  RefreshCw,
  Play,
  Pause,
  Trash2,
  Copy,
  ExternalLink
} from 'lucide-react';
const WebhooksIntegration = ({ integration, onBack }) => {
  const [webhooks, setWebhooks] = useState([
    {
      id: '1',
      name: 'User Enrollment Webhook',
      url: 'https://api.example.com/webhooks/enrollment',
      events: ['user.enrolled', 'user.updated'],
      status: 'active',
      lastTriggered: '5 minutes ago',
      successRate: 98.5,
      attempts: 1234
    },
    {
      id: '2',
      name: 'Course Completion',
      url: 'https://api.example.com/webhooks/completion',
      events: ['course.completed', 'certificate.issued'],
      status: 'active',
      lastTriggered: '1 hour ago',
      successRate: 99.2,
      attempts: 567
    },
    {
      id: '3',
      name: 'Payment Events',
      url: 'https://api.example.com/webhooks/payment',
      events: ['payment.success', 'payment.failed', 'subscription.updated'],
      status: 'paused',
      lastTriggered: '2 days ago',
      successRate: 95.7,
      attempts: 234
    }
  ]);
  const [availableEvents] = useState([
    { category: 'User Events', events: ['user.enrolled', 'user.updated', 'user.deleted', 'user.activated'] },
    { category: 'Course Events', events: ['course.started', 'course.completed', 'course.dropped'] },
    { category: 'Assignment Events', events: ['assignment.submitted', 'assignment.graded', 'assignment.overdue'] },
    { category: 'Payment Events', events: ['payment.success', 'payment.failed', 'subscription.created', 'subscription.updated'] },
    { category: 'System Events', events: ['system.maintenance', 'system.alert', 'system.update'] }
  ]);
  const [newWebhook, setNewWebhook] = useState({
    name: '',
    url: '',
    events: [],
    secret: '',
    headers: {}
  });
  const [showNewWebhook, setShowNewWebhook] = useState(false);
  const [testResults, setTestResults] = useState({});
  const configFields = [
    {
      name: 'signingSecret',
      label: 'Global Signing Secret',
      type: 'password',
      placeholder: 'Your webhook signing secret',
      required: false,
      description: 'Used to sign all webhook payloads'
    },
    {
      name: 'retryAttempts',
      label: 'Retry Attempts',
      type: 'select',
      options: [
        { value: '3', label: '3 attempts' },
        { value: '5', label: '5 attempts' },
        { value: '10', label: '10 attempts' }
      ],
      required: true
    },
    {
      name: 'timeout',
      label: 'Request Timeout (seconds)',
      type: 'number',
      placeholder: '30',
      required: true
    },
    {
      name: 'enableLogging',
      label: 'Enable detailed logging',
      type: 'checkbox',
      description: 'Log all webhook attempts and responses'
    }
  ];
  const handleTestWebhook = async (webhookId) => {
    setTestResults({ ...testResults, [webhookId]: 'testing' });
    // Simulate test
    setTimeout(() => {
      setTestResults({ ...testResults, [webhookId]: 'success' });
    }, 2000);
  };
  const handleToggleWebhook = (webhookId) => {
    setWebhooks(webhooks.map(webhook => 
      webhook.id === webhookId 
        ? { ...webhook, status: webhook.status === 'active' ? 'paused' : 'active' }
        : webhook
    ));
  };
  const customOverview = (
    <>
      {/* Webhook Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Webhooks</p>
                <p className="text-2xl font-bold">
                  {webhooks.filter(w => w.status === 'active').length}
                </p>
              </div>
              <Webhook className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {webhooks.filter(w => w.status === 'paused').length} paused
            </p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Calls Today</p>
                <p className="text-2xl font-bold">3,456</p>
              </div>
              <Activity className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-xs text-green-600 mt-2">↑ 12% from yesterday</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold">97.8%</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Last 24 hours</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold">245ms</p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">All endpoints</p>
          </div>
        </Card>
      </div>
      {/* Configured Webhooks */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Configured Webhooks</h3>
            <Button 
              variant="primary" 
              size="sm"
              onClick={() => setShowNewWebhook(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Webhook
            </Button>
          </div>
          <div className="space-y-4">
            {webhooks.map((webhook) => (
              <div key={webhook.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium">{webhook.name}</h4>
                    <p className="text-sm text-gray-600 font-mono mt-1">{webhook.url}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={webhook.status === 'active' ? 'success' : 'secondary'}>
                      {webhook.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleWebhook(webhook.id)}
                    >
                      {webhook.status === 'active' ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mb-3">
                  {webhook.events.map((event) => (
                    <Badge key={event} variant="secondary" size="sm">
                      {event}
                    </Badge>
                  ))}
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Last triggered</p>
                    <p className="font-medium">{webhook.lastTriggered}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Success rate</p>
                    <p className="font-medium text-green-600">{webhook.successRate}%</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Total attempts</p>
                    <p className="font-medium">{webhook.attempts.toLocaleString()}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleTestWebhook(webhook.id)}
                      disabled={testResults[webhook.id] === 'testing'}
                    >
                      {testResults[webhook.id] === 'testing' ? (
                        <>
                          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                          Testing...
                        </>
                      ) : (
                        <>
                          <Zap className="w-3 h-3 mr-1" />
                          Test
                        </>
                      )}
                    </Button>
                    {testResults[webhook.id] === 'success' && (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Add New Webhook Form */}
      {showNewWebhook && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Add New Webhook</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Webhook Name
                </label>
                <Input
                  type="text"
                  placeholder="My Custom Webhook"
                  value={newWebhook.name}
                  onChange={(e) => setNewWebhook({ ...newWebhook, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Webhook URL
                </label>
                <Input
                  type="url"
                  placeholder="https://api.example.com/webhook"
                  value={newWebhook.url}
                  onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Events to Subscribe
                </label>
                <div className="space-y-3">
                  {availableEvents.map((category) => (
                    <div key={category.category}>
                      <p className="text-sm font-medium text-gray-600 mb-2">{category.category}</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {category.events.map((event) => (
                          <label key={event} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={newWebhook.events.includes(event)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setNewWebhook({
                                    ...newWebhook,
                                    events: [...newWebhook.events, event]
                                  });
                                } else {
                                  setNewWebhook({
                                    ...newWebhook,
                                    events: newWebhook.events.filter(e => e !== event)
                                  });
                                }
                              }}
                              className="mr-2"
                            />
                            <span className="text-sm">{event}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Secret Key (optional)
                </label>
                <Input
                  type="password"
                  placeholder="Webhook signing secret"
                  value={newWebhook.secret}
                  onChange={(e) => setNewWebhook({ ...newWebhook, secret: e.target.value })}
                />
              </div>
              <div className="flex space-x-2">
                <Button variant="primary">Create Webhook</Button>
                <Button variant="secondary" onClick={() => setShowNewWebhook(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}
      {/* Webhook Payload Example */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Webhook Payload Example</h3>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
            <pre className="text-sm">
{`{
  "id": "evt_1234567890",
  "type": "user.enrolled",
  "created": 1234567890,
  "data": {
    "user_id": "usr_abc123",
    "course_id": "crs_xyz789",
    "enrollment_date": "2024-11-17T10:30:00Z",
    "payment_status": "completed"
  },
  "signature": "sha256=abcdef123456..."
}`}
            </pre>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              All webhooks include a signature header for verification
            </p>
            <Button variant="ghost" size="sm">
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </Button>
          </div>
        </div>
      </Card>
      {/* Recent Webhook Activity */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {[
              { event: 'user.enrolled', endpoint: 'User Enrollment Webhook', status: 'success', time: '2 minutes ago', responseTime: '156ms' },
              { event: 'payment.success', endpoint: 'Payment Events', status: 'success', time: '5 minutes ago', responseTime: '234ms' },
              { event: 'course.completed', endpoint: 'Course Completion', status: 'success', time: '15 minutes ago', responseTime: '189ms' },
              { event: 'assignment.submitted', endpoint: 'User Enrollment Webhook', status: 'failed', time: '30 minutes ago', error: '502 Bad Gateway' },
              { event: 'user.updated', endpoint: 'User Enrollment Webhook', status: 'success', time: '1 hour ago', responseTime: '201ms' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b">
                <div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary" size="sm">{activity.event}</Badge>
                    <span className="text-sm text-gray-600">→ {activity.endpoint}</span>
                  </div>
                  {activity.error && (
                    <p className="text-xs text-red-600 mt-1">{activity.error}</p>
                  )}
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">
                    {activity.responseTime || '-'}
                  </span>
                  <Badge variant={activity.status === 'success' ? 'success' : 'danger'} size="sm">
                    {activity.status}
                  </Badge>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Documentation Link */}
      <Alert variant="info">
        <Code className="w-4 h-4" />
        <div>
          <p className="font-medium">Webhook Documentation</p>
          <p className="text-sm">
            Learn how to implement webhook endpoints and verify signatures in our{' '}
            <a href="#" className="text-blue-600 hover:underline inline-flex items-center">
              developer documentation
              <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </p>
        </div>
      </Alert>
    </>
  );
  return (
    <BaseIntegration
      integration={integration}
      onBack={onBack}
      configFields={configFields}
    >
      {customOverview}
    </BaseIntegration>
  );
};
// Add missing icon import
const Plus = require('lucide-react').Plus;
export default WebhooksIntegration;