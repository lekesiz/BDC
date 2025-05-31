import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Alert } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Tabs } from '../ui/tabs';
import { 
  Settings, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  RefreshCw,
  Plus,
  Search,
  Filter,
  Link,
  Shield,
  Activity,
  Grid,
  List
} from 'lucide-react';

// Import integration components
import GoogleCalendarIntegration from './integrations/GoogleCalendarIntegration';
import MicrosoftTeamsIntegration from './integrations/MicrosoftTeamsIntegration';
import SlackIntegration from './integrations/SlackIntegration';
import ZoomIntegration from './integrations/ZoomIntegration';
import GoogleDriveIntegration from './integrations/GoogleDriveIntegration';
import DropboxIntegration from './integrations/DropboxIntegration';
import MailchimpIntegration from './integrations/MailchimpIntegration';
import TwilioIntegration from './integrations/TwilioIntegration';
import StripeIntegration from './integrations/StripeIntegration';
import WebhooksIntegration from './integrations/WebhooksIntegration';

// Import mock data
import { generateIntegrationsData, generateIntegrationActivity, generateIntegrationStats } from './mockIntegrationsData';

const IntegrationManager = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [integrations, setIntegrations] = useState([]);
  const [activity, setActivity] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedIntegration, setSelectedIntegration] = useState(null);

  useEffect(() => {
    // Load mock data
    const data = generateIntegrationsData();
    setIntegrations(data.available);
    setActivity(generateIntegrationActivity());
    setStats(generateIntegrationStats());
  }, []);

  const categories = [
    { id: 'all', name: 'All Integrations', count: integrations.length },
    { id: 'productivity', name: 'Productivity', count: integrations.filter(i => i.category === 'productivity').length },
    { id: 'communication', name: 'Communication', count: integrations.filter(i => i.category === 'communication').length },
    { id: 'payment', name: 'Payment', count: integrations.filter(i => i.category === 'payment').length },
    { id: 'storage', name: 'Storage', count: integrations.filter(i => i.category === 'storage').length },
    { id: 'marketing', name: 'Marketing', count: integrations.filter(i => i.category === 'marketing').length },
    { id: 'automation', name: 'Automation', count: integrations.filter(i => i.category === 'automation').length }
  ];

  const filteredIntegrations = integrations.filter(integration => {
    const matchesSearch = integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         integration.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || integration.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getIntegrationComponent = (integrationId) => {
    const components = {
      'google-calendar': GoogleCalendarIntegration,
      'microsoft-teams': MicrosoftTeamsIntegration,
      'slack': SlackIntegration,
      'zoom': ZoomIntegration,
      'google-drive': GoogleDriveIntegration,
      'dropbox': DropboxIntegration,
      'mailchimp': MailchimpIntegration,
      'twilio': TwilioIntegration,
      'stripe': StripeIntegration,
      'webhooks': WebhooksIntegration
    };
    return components[integrationId];
  };

  const handleIntegrationClick = (integration) => {
    setSelectedIntegration(integration);
  };

  const handleBackToList = () => {
    setSelectedIntegration(null);
  };

  if (selectedIntegration) {
    const IntegrationComponent = getIntegrationComponent(selectedIntegration.id);
    if (IntegrationComponent) {
      return (
        <IntegrationComponent 
          integration={selectedIntegration}
          onBack={handleBackToList}
        />
      );
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
          <p className="text-gray-600 mt-1">Connect your favorite tools and services</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="secondary">
            <Shield className="w-4 h-4 mr-2" />
            API Keys
          </Button>
          <Button variant="primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Integration
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="p-4">
              <p className="text-sm text-gray-600">Total Integrations</p>
              <p className="text-2xl font-bold">{stats.overview.totalIntegrations}</p>
              <p className="text-xs text-gray-500 mt-1">
                {stats.overview.activeIntegrations} active
              </p>
            </div>
          </Card>
          <Card>
            <div className="p-4">
              <p className="text-sm text-gray-600">API Calls Today</p>
              <p className="text-2xl font-bold">{stats.overview.totalApiCalls.toLocaleString()}</p>
              <p className="text-xs text-green-600 mt-1">↑ 12% from yesterday</p>
            </div>
          </Card>
          <Card>
            <div className="p-4">
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold">{stats.overview.successRate}%</p>
              <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
            </div>
          </Card>
          <Card>
            <div className="p-4">
              <p className="text-sm text-gray-600">Active Webhooks</p>
              <p className="text-2xl font-bold">3</p>
              <p className="text-xs text-gray-500 mt-1">2 triggered today</p>
            </div>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Search integrations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="form-select rounded-md border-gray-300"
              >
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name} ({category.count})
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Integrations Grid/List */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredIntegrations.map((integration) => (
                <Card 
                  key={integration.id} 
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => handleIntegrationClick(integration)}
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center">
                        <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
                          <img 
                            src={integration.icon} 
                            alt={integration.name}
                            className="w-8 h-8"
                          />
                        </div>
                        <div>
                          <h3 className="font-semibold">{integration.name}</h3>
                          <p className="text-sm text-gray-500">{integration.category}</p>
                        </div>
                      </div>
                      {integration.status === 'connected' ? (
                        <Badge variant="success">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <XCircle className="w-3 h-3 mr-1" />
                          Not Connected
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-4">{integration.description}</p>
                    <div className="flex items-center justify-between">
                      <Button 
                        variant={integration.status === 'connected' ? 'secondary' : 'primary'}
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Handle connection
                        }}
                      >
                        {integration.status === 'connected' ? 'Manage' : 'Connect'}
                      </Button>
                      {integration.status === 'connected' && integration.connectionDetails && (
                        <p className="text-xs text-gray-500">
                          Last sync: {new Date(integration.connectionDetails.lastSync).toLocaleTimeString()}
                        </p>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredIntegrations.map((integration) => (
                <div 
                  key={integration.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => handleIntegrationClick(integration)}
                >
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
                      <img 
                        src={integration.icon} 
                        alt={integration.name}
                        className="w-6 h-6"
                      />
                    </div>
                    <div>
                      <h3 className="font-medium">{integration.name}</h3>
                      <p className="text-sm text-gray-500">{integration.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {integration.status === 'connected' && integration.connectionDetails && (
                      <p className="text-sm text-gray-500">
                        Last sync: {new Date(integration.connectionDetails.lastSync).toLocaleTimeString()}
                      </p>
                    )}
                    {integration.status === 'connected' ? (
                      <Badge variant="success">Connected</Badge>
                    ) : (
                      <Badge variant="secondary">Not Connected</Badge>
                    )}
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle settings
                      }}
                    >
                      <Settings className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Recent Activity */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Activity</h3>
            <Button variant="ghost" size="sm">
              <Activity className="w-4 h-4 mr-2" />
              View All
            </Button>
          </div>
          <div className="space-y-3">
            {activity.slice(0, 5).map((item) => (
              <div key={item.id} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-3 ${
                    item.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="font-medium text-sm">{item.integration}</p>
                    <p className="text-sm text-gray-500">{item.action} - {item.details}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-500">
                  {new Date(item.timestamp).toLocaleTimeString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default IntegrationManager;