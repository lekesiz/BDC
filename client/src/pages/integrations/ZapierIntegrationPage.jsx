import React, { useState } from 'react';
import { FaPlug, FaBolt, FaSync, FaChartBar, FaKey, FaExchangeAlt, FaRocket, FaCode, FaCheckCircle, FaClock } from 'react-icons/fa';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';

const ZapierIntegrationPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  
  const tabs = [
    { id: 'overview', name: 'Overview', icon: <FaBolt /> },
    { id: 'connect', name: 'Connection', icon: <FaPlug /> },
    { id: 'zaps', name: 'Zaps', icon: <FaExchangeAlt /> },
    { id: 'triggers', name: 'Triggers', icon: <FaRocket /> },
    { id: 'actions', name: 'Actions', icon: <FaCode /> },
    { id: 'history', name: 'History', icon: <FaClock /> },
    { id: 'analytics', name: 'Analytics', icon: <FaChartBar /> },
  ];

  // Zapier connection state
  const [zapierAuth, setZapierAuth] = useState({
    apiKey: '',
    accountEmail: '',
    webhookUrl: ''
  });

  // Active Zaps
  const [activeZaps, setActiveZaps] = useState([
    {
      id: 1,
      name: 'New Beneficiary → CRM',
      trigger: 'New beneficiary created',
      action: 'Create contact in CRM',
      status: 'active',
      lastRun: '2024-12-21T14:30:00',
      runCount: 156,
      app: 'Salesforce'
    },
    {
      id: 2,
      name: 'Donation Processed → Email',
      trigger: 'Donation processed successfully',
      action: 'Send thank you email',
      status: 'active',
      lastRun: '2024-12-21T15:45:00',
      runCount: 89,
      app: 'Gmail'
    },
    {
      id: 3,
      name: 'Event Created → Calendar',
      trigger: 'New event created',
      action: 'Create Google Calendar event',
      status: 'active',
      lastRun: '2024-12-21T12:00:00',
      runCount: 45,
      app: 'Google Calendar'
    }
  ]);

  // Available triggers
  const availableTriggers = [
    { event: 'beneficiary.created', name: 'New Beneficiary', description: 'Triggered when a new beneficiary is created' },
    { event: 'donation.received', name: 'Donation Received', description: 'Triggered when a donation is received' },
    { event: 'donation.processed', name: 'Donation Processed', description: 'Triggered when a donation is processed successfully' },
    { event: 'subscription.created', name: 'New Subscription', description: 'Triggered when a subscription is created' },
    { event: 'subscription.cancelled', name: 'Subscription Cancelled', description: 'Triggered when a subscription is cancelled' },
    { event: 'event.created', name: 'Event Created', description: 'Triggered when an event is created' },
    { event: 'volunteer.registered', name: 'Volunteer Registered', description: 'Triggered when a volunteer registers' },
    { event: 'member.created', name: 'New Member', description: 'Triggered when a new member is added' },
    { event: 'email.sent', name: 'Email Sent', description: 'Triggered when an email is sent' },
    { event: 'sms.sent', name: 'SMS Sent', description: 'Triggered when an SMS is sent' }
  ];

  // Available actions
  const availableActions = [
    { action: 'create_beneficiary', name: 'Create Beneficiary', description: 'Create a new beneficiary' },
    { action: 'update_beneficiary', name: 'Update Beneficiary', description: 'Update beneficiary information' },
    { action: 'create_donation', name: 'Create Donation', description: 'Record a new donation' },
    { action: 'create_event', name: 'Create Event', description: 'Create a new event' },
    { action: 'send_email', name: 'Send Email', description: 'Send an email to a contact' },
    { action: 'send_sms', name: 'Send SMS', description: 'Send an SMS to a contact' },
    { action: 'add_note', name: 'Add Note', description: 'Add a note to a record' },
    { action: 'create_task', name: 'Create Task', description: 'Create a new task' },
    { action: 'update_contact', name: 'Update Contact', description: 'Update contact information' },
    { action: 'create_subscription', name: 'Create Subscription', description: 'Create a new subscription' }
  ];

  // Zap history
  const [zapHistory] = useState([
    {
      id: 1,
      zapName: 'New Beneficiary → CRM',
      status: 'success',
      timestamp: '2024-12-21T15:30:00',
      duration: '1.2s',
      data: { beneficiaryId: '12345', crmContactId: 'SF-67890' }
    },
    {
      id: 2,
      zapName: 'Donation Processed → Email',
      status: 'success',
      timestamp: '2024-12-21T15:25:00',
      duration: '0.8s',
      data: { donationId: '54321', emailId: 'EM-13579' }
    },
    {
      id: 3,
      zapName: 'Event Created → Calendar',
      status: 'failed',
      timestamp: '2024-12-21T15:20:00',
      duration: '3.4s',
      error: 'Google Calendar authentication expired'
    }
  ]);

  // Analytics data
  const analytics = {
    totalZaps: 12,
    activeZaps: 9,
    totalRuns: 3456,
    successRate: 94.5,
    avgDuration: 1.8,
    mostUsedTrigger: 'New Beneficiary',
    mostUsedAction: 'Create contact in CRM',
    topApps: ['Salesforce', 'Gmail', 'Google Calendar', 'Slack', 'Mailchimp']
  };

  const renderOverview = () => (
    <div>
      <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
        <h3 className="text-lg font-semibold mb-4">Zapier Integration Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Status</div>
            <div className="text-xl font-semibold text-green-600">
              {isConnected ? 'Connected' : 'Not Connected'}
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Active Zaps</div>
            <div className="text-xl font-semibold">{analytics.activeZaps}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Total Runs</div>
            <div className="text-xl font-semibold">{analytics.totalRuns}</div>
          </div>
        </div>
        <div className="prose max-w-none text-gray-600">
          <p>Zapier integration allows you to connect your CRM to over 5000 applications.</p>
          <ul className="mt-2">
            <li>Automate your processes with Zaps</li>
            <li>Sync data between applications</li>
            <li>Trigger actions based on events</li>
            <li>Easy integration without coding</li>
          </ul>
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Usage Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">{analytics.totalZaps}</div>
            <div className="text-sm text-gray-600">Total Zaps</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{analytics.successRate}%</div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{analytics.avgDuration}s</div>
            <div className="text-sm text-gray-600">Avg Duration</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{analytics.activeZaps}</div>
            <div className="text-sm text-gray-600">Active Zaps</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderConnect = () => (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Connect to Zapier</h3>
      
      {!isConnected ? (
        <div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h4 className="font-medium text-blue-900 mb-2">Connection Instructions</h4>
            <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
              <li>Log in to your Zapier account</li>
              <li>Create a new Zap and search for "BDC CRM"</li>
              <li>Copy your API key from your Zapier account settings</li>
              <li>Paste the API key below to establish connection</li>
            </ol>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Zapier API Key</label>
              <Input
                type="password"
                value={zapierAuth.apiKey}
                onChange={(e) => setZapierAuth({...zapierAuth, apiKey: e.target.value})}
                placeholder="Enter your Zapier API key"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Account Email</label>
              <Input
                type="email"
                value={zapierAuth.accountEmail}
                onChange={(e) => setZapierAuth({...zapierAuth, accountEmail: e.target.value})}
                placeholder="email@example.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Webhook URL</label>
              <Input
                type="text"
                value={zapierAuth.webhookUrl}
                onChange={(e) => setZapierAuth({...zapierAuth, webhookUrl: e.target.value})}
                placeholder="https://hooks.zapier.com/..."
              />
            </div>

            <Button
              onClick={() => setIsConnected(true)}
              className="bg-primary text-white"
            >
              Connect to Zapier
            </Button>
          </div>
        </div>
      ) : (
        <div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <FaCheckCircle className="text-green-600 mr-2" />
              <div>
                <p className="font-medium text-green-900">Connection Established</p>
                <p className="text-sm text-green-800">Account: {zapierAuth.accountEmail || 'admin@example.com'}</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-2">Connection Details</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <p>API Key: •••••••••••••</p>
                <p>Webhook URL: {zapierAuth.webhookUrl || 'https://hooks.zapier.com/...'}</p>
                <p>Last Connected: {new Date().toLocaleDateString()}</p>
              </div>
            </div>

            <Button
              onClick={() => setIsConnected(false)}
              variant="destructive"
            >
              Disconnect
            </Button>
          </div>
        </div>
      )}
    </div>
  );

  const renderZaps = () => (
    <div>
      <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">My Zaps</h3>
          <Button className="bg-primary text-white">
            Create Zap
          </Button>
        </div>

        <div className="space-y-4">
          {activeZaps.map(zap => (
            <div key={zap.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="font-medium">{zap.name}</h4>
                  <div className="text-sm text-gray-600 mt-1">
                    <span className="inline-flex items-center">
                      <FaBolt className="mr-1" /> {zap.trigger}
                    </span>
                    <span className="mx-2">→</span>
                    <span className="inline-flex items-center">
                      <FaRocket className="mr-1" /> {zap.action}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Last run: {new Date(zap.lastRun).toLocaleString()} • 
                    {zap.runCount} runs • 
                    App: {zap.app}
                  </div>
                </div>
                <div className="ml-4">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    zap.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {zap.status === 'active' ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="outline">Edit</Button>
                <Button size="sm" variant="outline">History</Button>
                <Button size="sm" variant="outline">
                  {zap.status === 'active' ? 'Deactivate' : 'Activate'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Popular Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4 hover:border-primary cursor-pointer">
            <h4 className="font-medium">Salesforce → Email</h4>
            <p className="text-sm text-gray-600 mt-1">
              Send a welcome email when a new contact is created in Salesforce
            </p>
          </div>
          <div className="border rounded-lg p-4 hover:border-primary cursor-pointer">
            <h4 className="font-medium">Donation → Slack</h4>
            <p className="text-sm text-gray-600 mt-1">
              Notify your team on Slack when a large donation is received
            </p>
          </div>
          <div className="border rounded-lg p-4 hover:border-primary cursor-pointer">
            <h4 className="font-medium">Event → Google Calendar</h4>
            <p className="text-sm text-gray-600 mt-1">
              Automatically create Google Calendar events
            </p>
          </div>
          <div className="border rounded-lg p-4 hover:border-primary cursor-pointer">
            <h4 className="font-medium">New Member → Mailchimp</h4>
            <p className="text-sm text-gray-600 mt-1">
              Add new members to your Mailchimp list
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTriggers = () => (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Available Triggers</h3>
      <p className="text-gray-600 mb-6">
        Triggers allow you to start your Zaps based on events in your CRM.
      </p>

      <div className="space-y-4">
        {availableTriggers.map((trigger, index) => (
          <div key={index} className="border rounded-lg p-4 hover:border-primary">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-medium">{trigger.name}</h4>
                <p className="text-sm text-gray-600 mt-1">{trigger.description}</p>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-2 inline-block">
                  {trigger.event}
                </code>
              </div>
              <Button size="sm" variant="outline">
                Use
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderActions = () => (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Available Actions</h3>
      <p className="text-gray-600 mb-6">
        Actions allow your Zaps to perform operations in your CRM.
      </p>

      <div className="space-y-4">
        {availableActions.map((action, index) => (
          <div key={index} className="border rounded-lg p-4 hover:border-primary">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-medium">{action.name}</h4>
                <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-2 inline-block">
                  {action.action}
                </code>
              </div>
              <Button size="sm" variant="outline">
                Use
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderHistory = () => (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Execution History</h3>
      
      <div className="space-y-3">
        {zapHistory.map(entry => (
          <div key={entry.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium">{entry.zapName}</h4>
                <p className="text-sm text-gray-600 mt-1">
                  {new Date(entry.timestamp).toLocaleString()} • Duration: {entry.duration}
                </p>
                {entry.data && (
                  <pre className="text-xs bg-gray-50 p-2 rounded mt-2">
                    {JSON.stringify(entry.data, null, 2)}
                  </pre>
                )}
                {entry.error && (
                  <div className="text-sm text-red-600 mt-2">
                    Error: {entry.error}
                  </div>
                )}
              </div>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                entry.status === 'success' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {entry.status === 'success' ? 'Success' : 'Failed'}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex justify-center">
        <Button variant="outline">
          Load More
        </Button>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Performance Analytics</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">{analytics.totalRuns}</div>
            <div className="text-sm text-gray-600">Total Runs</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{analytics.successRate}%</div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{analytics.avgDuration}s</div>
            <div className="text-sm text-gray-600">Avg Duration</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{analytics.activeZaps}</div>
            <div className="text-sm text-gray-600">Active Zaps</div>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="font-medium mb-3">Usage by Trigger</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm">New Beneficiary</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                  <div className="bg-primary h-2 rounded-full" style={{width: '75%'}}></div>
                </div>
                <span className="text-sm text-gray-600">1,234</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Donation Received</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                  <div className="bg-primary h-2 rounded-full" style={{width: '60%'}}></div>
                </div>
                <span className="text-sm text-gray-600">987</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Event Created</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                  <div className="bg-primary h-2 rounded-full" style={{width: '40%'}}></div>
                </div>
                <span className="text-sm text-gray-600">654</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Most Used Apps</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {analytics.topApps.map((app, index) => (
            <div key={index} className="text-center p-4 border rounded-lg">
              <div className="text-lg font-medium">{app}</div>
              <div className="text-sm text-gray-600 mt-1">
                {Math.floor(Math.random() * 500 + 100)} connections
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Zapier Integration</h1>
        <div className="flex items-center gap-4">
          <span className={`px-3 py-1 rounded-full text-sm ${
            isConnected 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {isConnected ? 'Connected' : 'Not Connected'}
          </span>
          <Button variant="outline">
            Documentation
          </Button>
        </div>
      </div>

      <div className="flex space-x-1 mb-6 border-b">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.icon}
            <span>{tab.name}</span>
          </button>
        ))}
      </div>

      <div>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'connect' && renderConnect()}
        {activeTab === 'zaps' && renderZaps()}
        {activeTab === 'triggers' && renderTriggers()}
        {activeTab === 'actions' && renderActions()}
        {activeTab === 'history' && renderHistory()}
        {activeTab === 'analytics' && renderAnalytics()}
      </div>
    </div>
  );
};

export default ZapierIntegrationPage;