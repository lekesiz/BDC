import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { 
  MessageSquare, 
  Link, 
  Settings, 
  CheckCircle,
  XCircle,
  AlertCircle,
  Send,
  Phone,
  Users,
  Calendar,
  Clock,
  DollarSign,
  Globe,
  BarChart,
  Zap,
  Shield,
  Smartphone,
  MessageCircle
} from 'lucide-react';
import { LineChart, Line, BarChart as RechartsBarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SMSIntegrationPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  const [smsConfig, setSmsConfig] = useState({
    provider: 'twilio',
    accountSid: '',
    authToken: '',
    phoneNumber: ''
  });

  const smsStats = {
    totalSent: 45678,
    delivered: 44234,
    failed: 567,
    queued: 123,
    deliveryRate: 96.8,
    avgCostPerSMS: 0.045,
    totalCost: 2055.51,
    activeNumbers: 3
  };

  const smsActivity = [
    { day: 'Mon', sent: 6543, delivered: 6321, failed: 45 },
    { day: 'Tue', sent: 6234, delivered: 6089, failed: 38 },
    { day: 'Wed', sent: 7123, delivered: 6945, failed: 52 },
    { day: 'Thu', sent: 6892, delivered: 6678, failed: 47 },
    { day: 'Fri', sent: 6456, delivered: 6234, failed: 41 },
    { day: 'Sat', sent: 5234, delivered: 5089, failed: 35 },
    { day: 'Sun', sent: 5789, delivered: 5623, failed: 39 }
  ];

  const messageTypes = [
    { type: 'Appointment Reminders', count: 12345, percentage: 35 },
    { type: 'Course Notifications', count: 8967, percentage: 25 },
    { type: 'Login OTP', count: 7234, percentage: 20 },
    { type: 'Payment Alerts', count: 5432, percentage: 15 },
    { type: 'General Updates', count: 1789, percentage: 5 }
  ];

  const phoneNumbers = [
    { id: 1, number: '+1 (555) 123-4567', country: 'US', type: 'Toll-free', status: 'active' },
    { id: 2, number: '+44 20 7123 4567', country: 'UK', type: 'Local', status: 'active' },
    { id: 3, number: '+33 1 23 45 67 89', country: 'FR', type: 'Local', status: 'active' }
  ];

  const automations = [
    { id: 1, name: 'Appointment Reminder', trigger: '24 hours before', status: 'active', sent: 3456 },
    { id: 2, name: 'Payment Due', trigger: '3 days before due', status: 'active', sent: 1234 },
    { id: 3, name: 'Course Start', trigger: '1 hour before', status: 'active', sent: 2345 },
    { id: 4, name: 'Birthday Wishes', trigger: 'On birthday', status: 'paused', sent: 567 }
  ];

  const campaigns = [
    { id: 1, name: 'New Course Launch', date: '2024-11-15', recipients: 1234, status: 'completed' },
    { id: 2, name: 'Holiday Greetings', date: '2024-11-10', recipients: 2456, status: 'completed' },
    { id: 3, name: 'System Maintenance', date: '2024-11-20', recipients: 3567, status: 'scheduled' },
    { id: 4, name: 'Early Bird Offer', date: '2024-11-08', recipients: 1876, status: 'draft' }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: MessageSquare },
    { id: 'messages', label: 'Messages', icon: MessageCircle },
    { id: 'campaigns', label: 'Campaigns', icon: Send },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'numbers', label: 'Phone Numbers', icon: Phone },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const smsProviders = [
    { value: 'twilio', label: 'Twilio', icon: MessageSquare },
    { value: 'nexmo', label: 'Nexmo/Vonage', icon: MessageSquare },
    { value: 'sns', label: 'Amazon SNS', icon: MessageSquare },
    { value: 'messagebird', label: 'MessageBird', icon: MessageSquare }
  ];

  const handleConnect = () => {
    if (smsConfig.accountSid && smsConfig.authToken) {
      setLoading(true);
      setTimeout(() => {
        setIsConnected(true);
        setLoading(false);
      }, 2000);
    }
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">SMS Service Integration</h1>
        {isConnected ? (
          <div className="flex space-x-2">
            <Button variant="primary">
              <Send className="w-4 h-4 mr-2" />
              Send SMS
            </Button>
            <Button variant="danger" onClick={() => setIsConnected(false)}>
              <XCircle className="w-4 h-4 mr-2" />
              Disconnect
            </Button>
          </div>
        ) : (
          <Button variant="primary" onClick={handleConnect} disabled={!smsConfig.accountSid || !smsConfig.authToken}>
            <Link className="w-4 h-4 mr-2" />
            Connect SMS Service
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
                      {isConnected ? `Connected to ${smsConfig.provider}` : 'Not connected'}
                    </p>
                  </div>
                </div>
                {isConnected && (
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Account Balance</p>
                    <p className="text-sm font-medium">$524.89</p>
                  </div>
                )}
              </div>

              {!isConnected && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">
                    Connect your SMS service to send notifications, reminders, and alerts to beneficiaries.
                  </p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        SMS Provider
                      </label>
                      <select 
                        value={smsConfig.provider}
                        onChange={(e) => setSmsConfig({...smsConfig, provider: e.target.value})}
                        className="form-select rounded-md border-gray-300 w-full"
                      >
                        {smsProviders.map((provider) => (
                          <option key={provider.value} value={provider.value}>
                            {provider.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    {smsConfig.provider === 'twilio' && (
                      <>
                        <Input
                          type="text"
                          placeholder="Account SID"
                          value={smsConfig.accountSid}
                          onChange={(e) => setSmsConfig({...smsConfig, accountSid: e.target.value})}
                        />
                        <Input
                          type="password"
                          placeholder="Auth Token"
                          value={smsConfig.authToken}
                          onChange={(e) => setSmsConfig({...smsConfig, authToken: e.target.value})}
                        />
                        <Input
                          type="tel"
                          placeholder="Phone Number"
                          value={smsConfig.phoneNumber}
                          onChange={(e) => setSmsConfig({...smsConfig, phoneNumber: e.target.value})}
                        />
                      </>
                    )}
                  </div>
                </div>
              )}

              {isConnected && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">SMS Sent</p>
                    <p className="text-2xl font-bold text-gray-900">{smsStats.totalSent.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Delivery Rate</p>
                    <p className="text-2xl font-bold text-green-600">{smsStats.deliveryRate}%</p>
                    <p className="text-xs text-gray-500 mt-1">Industry avg: 95%</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Cost</p>
                    <p className="text-2xl font-bold text-blue-600">${smsStats.totalCost}</p>
                    <p className="text-xs text-gray-500 mt-1">This month</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Avg Cost/SMS</p>
                    <p className="text-2xl font-bold text-gray-900">${smsStats.avgCostPerSMS}</p>
                    <p className="text-xs text-gray-500 mt-1">USD per message</p>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {isConnected && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">SMS Activity (Last 7 Days)</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={smsActivity}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="day" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="sent" stroke="#3B82F6" name="Sent" />
                          <Line type="monotone" dataKey="delivered" stroke="#10B981" name="Delivered" />
                          <Line type="monotone" dataKey="failed" stroke="#EF4444" name="Failed" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Message Categories</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={messageTypes}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ type, percentage }) => `${type} (${percentage}%)`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="count"
                          >
                            {messageTypes.map((entry, index) => (
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
                  <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Send className="w-5 h-5 text-blue-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Send Bulk SMS</p>
                        <p className="text-sm text-gray-500">Send messages to multiple recipients</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <MessageCircle className="w-5 h-5 text-green-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Create Template</p>
                        <p className="text-sm text-gray-500">Design reusable message templates</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Zap className="w-5 h-5 text-purple-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Setup Automation</p>
                        <p className="text-sm text-gray-500">Create automated SMS workflows</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Users className="w-5 h-5 text-orange-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Contact Lists</p>
                        <p className="text-sm text-gray-500">Manage recipient groups</p>
                      </div>
                    </button>
                  </div>
                </div>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'messages' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Messages</h3>
                <Button variant="primary" size="sm">
                  <Send className="w-4 h-4 mr-2" />
                  Send New
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date & Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipient</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-17 15:30</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">+1 555-123-4567</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <p className="truncate max-w-xs">Reminder: Your appointment is tomorrow at 10:00 AM</p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Delivered
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$0.045</td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-17 14:15</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">+44 20-7123-4567</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <p className="truncate max-w-xs">Your login OTP is: 234567. Valid for 10 minutes.</p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Delivered
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$0.065</td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-17 13:45</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">+33 1-2345-6789</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <p className="truncate max-w-xs">New course available: Advanced Python Programming</p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          Failed
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$0.055</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Message Templates</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2">Appointment Reminder</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Hi {'{name}'}, this is a reminder about your appointment on {'{date}'} at {'{time}'}. Reply YES to confirm.
                  </p>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">Edit</Button>
                    <Button variant="outline" size="sm">Use</Button>
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2">Payment Reminder</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Dear {'{name}'}, your payment of {'{amount}'} is due on {'{date}'}. Please ensure timely payment.
                  </p>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">Edit</Button>
                    <Button variant="outline" size="sm">Use</Button>
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2">Course Start</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Hi {'{name}'}, your {'{course}'} starts tomorrow at {'{time}'}. See you there!
                  </p>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">Edit</Button>
                    <Button variant="outline" size="sm">Use</Button>
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2">OTP Message</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Your verification code is: {'{otp}'}. This code will expire in 10 minutes.
                  </p>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">Edit</Button>
                    <Button variant="outline" size="sm">Use</Button>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'campaigns' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">SMS Campaigns</h3>
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
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Delivery Rate</th>
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
                          {campaign.recipients}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${campaign.status === 'completed' ? 'bg-green-100 text-green-800' :
                              campaign.status === 'scheduled' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'}`}>
                            {campaign.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {campaign.status === 'completed' ? '97.2%' : '-'}
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
                <h3 className="text-lg font-semibold">SMS Automations</h3>
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
        </div>
      )}

      {activeTab === 'numbers' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Phone Numbers</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Number
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Monthly Cost</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {phoneNumbers.map((number) => (
                      <tr key={number.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          <div className="flex items-center">
                            <Phone className="w-4 h-4 mr-2 text-gray-400" />
                            {number.number}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Globe className="w-4 h-4 mr-2 text-gray-400" />
                            <span className="text-sm text-gray-900">{number.country}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {number.type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {number.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${number.type === 'Toll-free' ? '15.00' : '5.00'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2">
                          <Button variant="ghost" size="sm">Configure</Button>
                          <Button variant="ghost" size="sm">Remove</Button>
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
              <h3 className="text-lg font-semibold mb-4">Number Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Sender Number
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>+1 (555) 123-4567 (US)</option>
                    <option>+44 20 7123 4567 (UK)</option>
                    <option>+33 1 23 45 67 89 (FR)</option>
                  </select>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Use intelligent number routing</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically select the best number based on recipient location
                  </p>
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
              <h3 className="text-lg font-semibold mb-4">SMS Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMS Provider
                  </label>
                  <select 
                    value={smsConfig.provider}
                    onChange={(e) => setSmsConfig({...smsConfig, provider: e.target.value})}
                    className="form-select rounded-md border-gray-300 w-full"
                  >
                    {smsProviders.map((provider) => (
                      <option key={provider.value} value={provider.value}>
                        {provider.label}
                      </option>
                    ))}
                  </select>
                </div>

                {smsConfig.provider === 'twilio' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Account SID
                      </label>
                      <div className="flex space-x-2">
                        <Input
                          type="text"
                          value={smsConfig.accountSid}
                          onChange={(e) => setSmsConfig({...smsConfig, accountSid: e.target.value})}
                          className="flex-1"
                        />
                        <Button variant="secondary">Update</Button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Auth Token
                      </label>
                      <Input
                        type="password"
                        value={smsConfig.authToken}
                        onChange={(e) => setSmsConfig({...smsConfig, authToken: e.target.value})}
                      />
                    </div>
                  </>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Country Code
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option value="+1">+1 (US/Canada)</option>
                    <option value="+44">+44 (UK)</option>
                    <option value="+33">+33 (France)</option>
                    <option value="+49">+49 (Germany)</option>
                  </select>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">SMS Preferences</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable delivery reports</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Receive confirmation when messages are delivered
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Unicode support</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Support for special characters and emojis
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="font-medium">Concatenate long messages</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically split and join messages over 160 characters
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message Retry Attempts
                  </label>
                  <Input type="number" defaultValue="3" min="1" max="5" />
                </div>

                <div className="pt-4">
                  <Button variant="primary">Save Settings</Button>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Compliance & Opt-out</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-start">
                    <Shield className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900">TCPA Compliance</h4>
                      <p className="text-sm text-blue-800 mt-1">
                        Ensure all SMS communications comply with TCPA regulations. Obtain proper consent before sending messages.
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Auto-process opt-out keywords</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically handle STOP, UNSUBSCRIBE, and other opt-out keywords
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Opt-out Response Message
                  </label>
                  <Input
                    type="text"
                    defaultValue="You have been unsubscribed. Reply START to resubscribe."
                  />
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SMSIntegrationPage;