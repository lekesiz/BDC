import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Mail, 
  Link, 
  Settings, 
  CheckCircle,
  XCircle,
  AlertCircle,
  Send,
  Inbox,
  FileText,
  Users,
  Calendar,
  Clock,
  RefreshCw,
  Shield,
  Zap,
  BarChart,
  Filter,
  Tag
} from 'lucide-react';
import { LineChart, Line, BarChart as RechartsBarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const EmailIntegrationPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  const [emailConfig, setEmailConfig] = useState({
    provider: 'gmail',
    apiKey: '',
    clientId: '',
    clientSecret: ''
  });

  const emailStats = {
    totalSent: 15342,
    delivered: 14989,
    opened: 11234,
    clicked: 3456,
    bounced: 234,
    unsubscribed: 119,
    avgOpenRate: 73.2,
    avgClickRate: 22.5
  };

  const emailActivity = [
    { day: 'Mon', sent: 2345, opened: 1876, clicked: 423 },
    { day: 'Tue', sent: 2156, opened: 1654, clicked: 367 },
    { day: 'Wed', sent: 2489, opened: 1923, clicked: 478 },
    { day: 'Thu', sent: 2678, opened: 2076, clicked: 512 },
    { day: 'Fri', sent: 2234, opened: 1678, clicked: 389 },
    { day: 'Sat', sent: 1567, opened: 1234, clicked: 267 },
    { day: 'Sun', sent: 1873, opened: 1456, clicked: 324 }
  ];

  const emailTemplates = [
    { id: 1, name: 'Welcome Email', type: 'Onboarding', used: 456, openRate: 82 },
    { id: 2, name: 'Course Reminder', type: 'Notification', used: 1234, openRate: 76 },
    { id: 3, name: 'Progress Report', type: 'Report', used: 789, openRate: 68 },
    { id: 4, name: 'Certificate Ready', type: 'Achievement', used: 345, openRate: 91 },
    { id: 5, name: 'Monthly Newsletter', type: 'Newsletter', used: 567, openRate: 64 }
  ];

  const campaigns = [
    { id: 1, name: 'New Python Course Launch', date: '2024-11-15', recipients: 2456, status: 'sent' },
    { id: 2, name: 'Q4 Training Schedule', date: '2024-11-10', recipients: 3234, status: 'sent' },
    { id: 3, name: 'Early Bird Registration', date: '2024-11-08', recipients: 1876, status: 'scheduled' },
    { id: 4, name: 'Success Stories Newsletter', date: '2024-11-05', recipients: 4567, status: 'draft' }
  ];

  const automations = [
    { id: 1, name: 'Welcome Series', trigger: 'User Registration', status: 'active', sent: 1234 },
    { id: 2, name: 'Course Completion', trigger: 'Course Finished', status: 'active', sent: 567 },
    { id: 3, name: 'Re-engagement', trigger: '30 Days Inactive', status: 'paused', sent: 234 },
    { id: 4, name: 'Birthday Wishes', trigger: 'Birthday', status: 'active', sent: 89 }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Mail },
    { id: 'templates', label: 'Templates', icon: FileText },
    { id: 'campaigns', label: 'Campaigns', icon: Send },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'analytics', label: 'Analytics', icon: BarChart },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const emailProviders = [
    { value: 'gmail', label: 'Gmail', icon: Mail },
    { value: 'sendgrid', label: 'SendGrid', icon: Send },
    { value: 'mailgun', label: 'Mailgun', icon: Mail },
    { value: 'ses', label: 'Amazon SES', icon: Mail }
  ];

  const handleConnect = () => {
    if (emailConfig.apiKey) {
      setLoading(true);
      setTimeout(() => {
        setIsConnected(true);
        setLoading(false);
      }, 2000);
    }
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Email Service Integration</h1>
        {isConnected ? (
          <div className="flex space-x-2">
            <Button variant="secondary">
              <RefreshCw className="w-4 h-4 mr-2" />
              Sync Now
            </Button>
            <Button variant="danger" onClick={() => setIsConnected(false)}>
              <XCircle className="w-4 h-4 mr-2" />
              Disconnect
            </Button>
          </div>
        ) : (
          <Button variant="primary" onClick={handleConnect} disabled={!emailConfig.apiKey}>
            <Link className="w-4 h-4 mr-2" />
            Connect Email Service
          </Button>
        )}
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
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    isConnected ? 'bg-green-100' : 'bg-gray-100'
                  }`}>
                    {isConnected ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <XCircle className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold">Connection Status</h3>
                    <p className={`text-sm ${isConnected ? 'text-green-600' : 'text-gray-500'}`}>
                      {isConnected ? `Connected to ${emailConfig.provider}` : 'Not connected'}
                    </p>
                  </div>
                </div>
                {isConnected && (
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Last synced</p>
                    <p className="text-sm font-medium">5 minutes ago</p>
                  </div>
                )}
              </div>

              {!isConnected && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">
                    Connect your email service to send automated emails, track performance, and manage campaigns.
                  </p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email Provider
                      </label>
                      <select 
                        value={emailConfig.provider}
                        onChange={(e) => setEmailConfig({...emailConfig, provider: e.target.value})}
                        className="form-select rounded-md border-gray-300 w-full"
                      >
                        {emailProviders.map((provider) => (
                          <option key={provider.value} value={provider.value}>
                            {provider.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <Input
                      type="password"
                      placeholder="Enter API key"
                      value={emailConfig.apiKey}
                      onChange={(e) => setEmailConfig({...emailConfig, apiKey: e.target.value})}
                    />
                    {emailConfig.provider === 'gmail' && (
                      <>
                        <Input
                          type="text"
                          placeholder="Client ID"
                          value={emailConfig.clientId}
                          onChange={(e) => setEmailConfig({...emailConfig, clientId: e.target.value})}
                        />
                        <Input
                          type="password"
                          placeholder="Client Secret"
                          value={emailConfig.clientSecret}
                          onChange={(e) => setEmailConfig({...emailConfig, clientSecret: e.target.value})}
                        />
                      </>
                    )}
                  </div>
                </div>
              )}

              {isConnected && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Emails Sent</p>
                    <p className="text-2xl font-bold text-gray-900">{emailStats.totalSent.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Open Rate</p>
                    <p className="text-2xl font-bold text-green-600">{emailStats.avgOpenRate}%</p>
                    <p className="text-xs text-gray-500 mt-1">Industry avg: 65%</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Click Rate</p>
                    <p className="text-2xl font-bold text-blue-600">{emailStats.avgClickRate}%</p>
                    <p className="text-xs text-gray-500 mt-1">Industry avg: 18%</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Bounce Rate</p>
                    <p className="text-2xl font-bold text-red-600">{((emailStats.bounced / emailStats.totalSent) * 100).toFixed(1)}%</p>
                    <p className="text-xs text-gray-500 mt-1">Target: &lt; 2%</p>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {isConnected && (
            <>
              <Card>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Email Activity (Last 7 Days)</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={emailActivity}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="sent" stroke="#3B82F6" name="Sent" />
                        <Line type="monotone" dataKey="opened" stroke="#10B981" name="Opened" />
                        <Line type="monotone" dataKey="clicked" stroke="#F59E0B" name="Clicked" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </Card>

              <Card>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Send className="w-5 h-5 text-blue-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Send Campaign</p>
                        <p className="text-sm text-gray-500">Create and send a new email campaign</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <FileText className="w-5 h-5 text-green-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Create Template</p>
                        <p className="text-sm text-gray-500">Design a new email template</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Zap className="w-5 h-5 text-purple-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Setup Automation</p>
                        <p className="text-sm text-gray-500">Create automated email workflows</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Users className="w-5 h-5 text-orange-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Manage Lists</p>
                        <p className="text-sm text-gray-500">Organize subscriber lists</p>
                      </div>
                    </button>
                  </div>
                </div>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'templates' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Email Templates</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Template
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Template Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Times Used</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Open Rate</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Modified</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {emailTemplates.map((template) => (
                      <tr key={template.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {template.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                            {template.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {template.used}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center">
                            <span>{template.openRate}%</span>
                            <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                              <div className="bg-green-500 h-2 rounded-full" style={{ width: `${template.openRate}%` }}></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          2 days ago
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2">
                          <Button variant="ghost" size="sm">Edit</Button>
                          <Button variant="ghost" size="sm">Duplicate</Button>
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
              <h3 className="text-lg font-semibold mb-4">Template Categories</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <Inbox className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <p className="font-medium">Onboarding</p>
                  <p className="text-sm text-gray-500">5 templates</p>
                </div>
                <div className="text-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <Send className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <p className="font-medium">Notifications</p>
                  <p className="text-sm text-gray-500">8 templates</p>
                </div>
                <div className="text-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <FileText className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                  <p className="font-medium">Reports</p>
                  <p className="text-sm text-gray-500">3 templates</p>
                </div>
                <div className="text-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <Calendar className="w-8 h-8 text-orange-500 mx-auto mb-2" />
                  <p className="font-medium">Events</p>
                  <p className="text-sm text-gray-500">4 templates</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'campaigns' && isConnected && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Campaigns</p>
                    <p className="text-2xl font-bold text-gray-900">12</p>
                  </div>
                  <Send className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Scheduled</p>
                    <p className="text-2xl font-bold text-gray-900">5</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Drafts</p>
                    <p className="text-2xl font-bold text-gray-900">8</p>
                  </div>
                  <FileText className="w-8 h-8 text-gray-500" />
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Campaigns</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  New Campaign
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Campaign Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipients</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {campaigns.map((campaign) => (
                      <tr key={campaign.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {campaign.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {campaign.date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {campaign.recipients.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${campaign.status === 'sent' ? 'bg-green-100 text-green-800' :
                              campaign.status === 'scheduled' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'}`}>
                            {campaign.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {campaign.status === 'sent' ? (
                            <div>
                              <p>Open: 76%</p>
                              <p>Click: 23%</p>
                            </div>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2">
                          <Button variant="ghost" size="sm">View</Button>
                          <Button variant="ghost" size="sm">Edit</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'automation' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Email Automations</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Automation
                </Button>
              </div>
              <div className="space-y-4">
                {automations.map((automation) => (
                  <div key={automation.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 ${
                          automation.status === 'active' ? 'bg-green-100' : 'bg-gray-100'
                        }`}>
                          <Zap className={`w-5 h-5 ${
                            automation.status === 'active' ? 'text-green-600' : 'text-gray-400'
                          }`} />
                        </div>
                        <div>
                          <h4 className="font-medium">{automation.name}</h4>
                          <p className="text-sm text-gray-500">Trigger: {automation.trigger}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="text-sm font-medium">{automation.sent} sent</p>
                          <p className="text-xs text-gray-500">Last 30 days</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button 
                            variant={automation.status === 'active' ? 'secondary' : 'primary'}
                            size="sm"
                          >
                            {automation.status === 'active' ? 'Pause' : 'Activate'}
                          </Button>
                          <Button variant="ghost" size="sm">Edit</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Automation Templates</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-medium mb-2">Welcome Series</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Send a series of onboarding emails to new users
                  </p>
                  <Button variant="outline" size="sm" className="w-full">Use Template</Button>
                </div>
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-medium mb-2">Abandoned Course</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Re-engage students who haven't completed their course
                  </p>
                  <Button variant="outline" size="sm" className="w-full">Use Template</Button>
                </div>
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-medium mb-2">Feedback Request</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Automatically request feedback after course completion
                  </p>
                  <Button variant="outline" size="sm" className="w-full">Use Template</Button>
                </div>
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-medium mb-2">Birthday Messages</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Send personalized birthday wishes to students
                  </p>
                  <Button variant="outline" size="sm" className="w-full">Use Template</Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'analytics' && isConnected && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Email Performance</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsBarChart data={emailActivity}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="sent" fill="#3B82F6" name="Sent" />
                      <Bar dataKey="opened" fill="#10B981" name="Opened" />
                      <Bar dataKey="clicked" fill="#F59E0B" name="Clicked" />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Engagement Breakdown</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Opened', value: emailStats.opened },
                          { name: 'Clicked', value: emailStats.clicked },
                          { name: 'No Action', value: emailStats.delivered - emailStats.opened }
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {[0, 1, 2].map((index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index]} />
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
              <h3 className="text-lg font-semibold mb-4">Top Performing Content</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Python Course Launch Announcement</p>
                    <p className="text-sm text-gray-500">Sent: Nov 15 • Recipients: 2,456</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">Open: 84%</p>
                    <p className="text-sm text-gray-500">Click: 31%</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Success Story: John's Journey</p>
                    <p className="text-sm text-gray-500">Sent: Nov 10 • Recipients: 3,234</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">Open: 78%</p>
                    <p className="text-sm text-gray-500">Click: 28%</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Early Bird Registration Open</p>
                    <p className="text-sm text-gray-500">Sent: Nov 8 • Recipients: 1,876</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">Open: 72%</p>
                    <p className="text-sm text-gray-500">Click: 26%</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'settings' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Email Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Provider
                  </label>
                  <select 
                    value={emailConfig.provider}
                    onChange={(e) => setEmailConfig({...emailConfig, provider: e.target.value})}
                    className="form-select rounded-md border-gray-300 w-full"
                  >
                    {emailProviders.map((provider) => (
                      <option key={provider.value} value={provider.value}>
                        {provider.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key
                  </label>
                  <div className="flex space-x-2">
                    <Input
                      type="password"
                      value={emailConfig.apiKey}
                      onChange={(e) => setEmailConfig({...emailConfig, apiKey: e.target.value})}
                      className="flex-1"
                    />
                    <Button variant="secondary">Update</Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Email
                  </label>
                  <Input
                    type="email"
                    placeholder="noreply@yourdomain.com"
                    defaultValue="noreply@bdc.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Name
                  </label>
                  <Input
                    type="text"
                    placeholder="Your Organization Name"
                    defaultValue="BDC Training Center"
                  />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Email Preferences</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Track email opens</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Monitor when recipients open your emails
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Track link clicks</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Monitor which links recipients click
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable unsubscribe link</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Include unsubscribe link in all emails (required by law)
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="font-medium">Send test emails</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Send a test copy before launching campaigns
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
              <h3 className="text-lg font-semibold mb-4">Compliance</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-start">
                    <Shield className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900">GDPR Compliance</h4>
                      <p className="text-sm text-blue-800 mt-1">
                        Ensure all email communications comply with GDPR regulations. Include proper consent mechanisms and data handling procedures.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-green-900">CAN-SPAM Act</h4>
                      <p className="text-sm text-green-800 mt-1">
                        All emails include required sender information, subject lines are accurate, and unsubscribe options are clearly visible.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EmailIntegrationPage;