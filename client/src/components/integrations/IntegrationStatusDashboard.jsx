import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert } from '../ui/alert';
import {
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  BarChart3,
  PieChart,
  Calendar,
  Clock,
  Zap
} from 'lucide-react';

const IntegrationStatusDashboard = () => {
  const [stats, setStats] = useState({
    totalIntegrations: 11,
    connectedIntegrations: 7,
    totalApiCalls: 156789,
    successRate: 98.2,
    averageResponseTime: 245,
    dataTransferred: '2.3 TB'
  });

  const [integrationHealth, setIntegrationHealth] = useState([
    { name: 'Google Calendar', status: 'healthy', uptime: 99.9, lastCheck: '2 min ago', issues: 0 },
    { name: 'Slack', status: 'healthy', uptime: 99.5, lastCheck: '5 min ago', issues: 0 },
    { name: 'Stripe', status: 'healthy', uptime: 100, lastCheck: '1 min ago', issues: 0 },
    { name: 'Zoom', status: 'warning', uptime: 97.2, lastCheck: '3 min ago', issues: 2 },
    { name: 'Google Drive', status: 'healthy', uptime: 99.8, lastCheck: '4 min ago', issues: 0 },
    { name: 'Twilio', status: 'error', uptime: 95.5, lastCheck: '1 min ago', issues: 5 },
    { name: 'Mailchimp', status: 'healthy', uptime: 99.7, lastCheck: '6 min ago', issues: 0 }
  ]);

  const [activityTimeline, setActivityTimeline] = useState([
    { time: '09:00', calls: 234, errors: 2 },
    { time: '10:00', calls: 456, errors: 5 },
    { time: '11:00', calls: 678, errors: 3 },
    { time: '12:00', calls: 543, errors: 1 },
    { time: '13:00', calls: 789, errors: 4 },
    { time: '14:00', calls: 901, errors: 2 },
    { time: '15:00', calls: 765, errors: 3 },
    { time: '16:00', calls: 654, errors: 2 }
  ]);

  const [topEndpoints, setTopEndpoints] = useState([
    { endpoint: 'Google Calendar Sync', calls: 12456, avgTime: 156, trend: 'up' },
    { endpoint: 'Slack Notifications', calls: 9876, avgTime: 89, trend: 'up' },
    { endpoint: 'Stripe Payments', calls: 5432, avgTime: 234, trend: 'stable' },
    { endpoint: 'Twilio SMS', calls: 8765, avgTime: 178, trend: 'down' },
    { endpoint: 'Zoom Meetings', calls: 3456, avgTime: 345, trend: 'up' }
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-5 h-5" />;
      case 'warning': return <AlertCircle className="w-5 h-5" />;
      case 'error': return <XCircle className="w-5 h-5" />;
      default: return <AlertCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold">{stats.connectedIntegrations}/{stats.totalIntegrations}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-500" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">API Calls</p>
                <p className="text-2xl font-bold">{(stats.totalApiCalls / 1000).toFixed(1)}k</p>
              </div>
              <Zap className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold">{stats.successRate}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response</p>
                <p className="text-2xl font-bold">{stats.averageResponseTime}ms</p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Data Transfer</p>
                <p className="text-2xl font-bold">{stats.dataTransferred}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-indigo-500" />
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Health Score</p>
                <p className="text-2xl font-bold">98.5</p>
              </div>
              <PieChart className="w-8 h-8 text-pink-500" />
            </div>
          </div>
        </Card>
      </div>

      {/* System Health Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Integration Health Status</h3>
            <button className="text-sm text-blue-600 hover:text-blue-800 flex items-center">
              <RefreshCw className="w-4 h-4 mr-1" />
              Refresh
            </button>
          </div>
          
          <div className="space-y-3">
            {integrationHealth.map((integration) => (
              <div key={integration.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={getStatusColor(integration.status)}>
                    {getStatusIcon(integration.status)}
                  </div>
                  <div>
                    <p className="font-medium">{integration.name}</p>
                    <p className="text-sm text-gray-500">Last check: {integration.lastCheck}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Uptime</p>
                    <p className="font-medium">{integration.uptime}%</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Issues</p>
                    <p className="font-medium">{integration.issues}</p>
                  </div>
                  <Badge variant={
                    integration.status === 'healthy' ? 'success' :
                    integration.status === 'warning' ? 'warning' : 'danger'
                  }>
                    {integration.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Activity Timeline */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">API Activity Timeline</h3>
          <div className="h-64 flex items-end justify-between space-x-2">
            {activityTimeline.map((hour) => {
              const maxCalls = Math.max(...activityTimeline.map(h => h.calls));
              const heightPercentage = (hour.calls / maxCalls) * 100;
              const errorPercentage = (hour.errors / hour.calls) * 100;
              
              return (
                <div key={hour.time} className="flex-1 flex flex-col items-center">
                  <div className="w-full bg-gray-200 rounded-t relative" style={{ height: `${heightPercentage}%` }}>
                    <div 
                      className="absolute bottom-0 w-full bg-red-500 rounded-t"
                      style={{ height: `${errorPercentage}%` }}
                    />
                    <div 
                      className="absolute bottom-0 w-full bg-blue-500 rounded-t"
                      style={{ height: `${100 - errorPercentage}%`, opacity: 0.8 }}
                    />
                  </div>
                  <p className="text-xs text-gray-600 mt-2">{hour.time}</p>
                </div>
              );
            })}
          </div>
          <div className="flex items-center justify-center space-x-6 mt-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded mr-2" />
              <span className="text-sm text-gray-600">Successful Calls</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded mr-2" />
              <span className="text-sm text-gray-600">Failed Calls</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Top Endpoints */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Top Integration Endpoints</h3>
          <div className="space-y-3">
            {topEndpoints.map((endpoint) => (
              <div key={endpoint.endpoint} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-medium">{endpoint.endpoint}</p>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-600">{endpoint.calls.toLocaleString()} calls</span>
                      <span className="text-sm text-gray-600">{endpoint.avgTime}ms avg</span>
                      {endpoint.trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500" />}
                      {endpoint.trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500" />}
                    </div>
                  </div>
                  <Progress value={(endpoint.calls / 12456) * 100} className="h-2" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Alerts */}
      <div className="space-y-3">
        <Alert variant="warning">
          <AlertCircle className="w-4 h-4" />
          <div>
            <p className="font-medium">Zoom Integration - High Response Time</p>
            <p className="text-sm">Average response time has increased to 345ms. Consider optimizing API calls.</p>
          </div>
        </Alert>
        
        <Alert variant="danger">
          <XCircle className="w-4 h-4" />
          <div>
            <p className="font-medium">Twilio Integration - Connection Issues</p>
            <p className="text-sm">5 failed requests in the last hour. Please check your API credentials.</p>
          </div>
        </Alert>
      </div>
    </div>
  );
};

export default IntegrationStatusDashboard;