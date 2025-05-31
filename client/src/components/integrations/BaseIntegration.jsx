import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Alert } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Tabs } from '../ui/tabs';
import {
  ArrowLeft,
  Settings,
  Activity,
  Shield,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Link,
  Unlink,
  TestTube,
  Save,
  Clock,
  Database,
  Key,
  Eye,
  EyeOff
} from 'lucide-react';

const BaseIntegration = ({ 
  integration, 
  onBack, 
  children, 
  configFields = [],
  oauthConfig = null,
  webhookEvents = [],
  apiEndpoints = [],
  customTabs = []
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [config, setConfig] = useState({});
  const [showSecrets, setShowSecrets] = useState({});
  const [connectionStatus, setConnectionStatus] = useState(integration.status);
  const [lastSync, setLastSync] = useState(null);
  const [activityLog, setActivityLog] = useState([]);
  const [rateLimits, setRateLimits] = useState({
    limit: 1000,
    remaining: 850,
    resetsAt: new Date(Date.now() + 3600000).toISOString()
  });

  useEffect(() => {
    // Load saved configuration
    loadConfiguration();
    loadActivityLog();
  }, [integration.id]);

  const loadConfiguration = () => {
    // Mock loading saved config
    const savedConfig = localStorage.getItem(`integration_${integration.id}_config`);
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }
  };

  const loadActivityLog = () => {
    // Mock activity log
    setActivityLog([
      { id: 1, action: 'Connection established', timestamp: new Date(Date.now() - 3600000), status: 'success' },
      { id: 2, action: 'Data sync completed', timestamp: new Date(Date.now() - 7200000), status: 'success' },
      { id: 3, action: 'Configuration updated', timestamp: new Date(Date.now() - 86400000), status: 'info' }
    ]);
  };

  const handleConnect = async () => {
    setLoading(true);
    try {
      if (oauthConfig) {
        // Initiate OAuth flow
        const authUrl = buildOAuthUrl();
        window.location.href = authUrl;
      } else {
        // API key based connection
        await testConnection();
        setConnectionStatus('connected');
        setLastSync(new Date().toISOString());
      }
    } catch (error) {
      console.error('Connection failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    try {
      // Clear stored credentials
      localStorage.removeItem(`integration_${integration.id}_config`);
      setConfig({});
      setConnectionStatus('disconnected');
      setLastSync(null);
    } catch (error) {
      console.error('Disconnect failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setTestingConnection(true);
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000));
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    } finally {
      setTestingConnection(false);
    }
  };

  const saveConfiguration = () => {
    localStorage.setItem(`integration_${integration.id}_config`, JSON.stringify(config));
    // Add to activity log
    setActivityLog(prev => [{
      id: Date.now(),
      action: 'Configuration saved',
      timestamp: new Date(),
      status: 'success'
    }, ...prev]);
  };

  const buildOAuthUrl = () => {
    if (!oauthConfig) return '';
    
    const params = new URLSearchParams({
      client_id: oauthConfig.clientId,
      redirect_uri: oauthConfig.redirectUri,
      response_type: 'code',
      scope: oauthConfig.scopes.join(' '),
      state: generateState()
    });

    return `${oauthConfig.authUrl}?${params.toString()}`;
  };

  const generateState = () => {
    return Math.random().toString(36).substring(2, 15);
  };

  const handleSync = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      setLastSync(new Date().toISOString());
      setActivityLog(prev => [{
        id: Date.now(),
        action: 'Manual sync completed',
        timestamp: new Date(),
        status: 'success'
      }, ...prev]);
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const defaultTabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'configuration', label: 'Configuration', icon: Settings },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'activity', label: 'Activity Log', icon: Clock },
    { id: 'api', label: 'API & Webhooks', icon: Database },
    ...customTabs
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Button variant="ghost" onClick={onBack} className="mr-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{integration.name}</h1>
            <p className="text-gray-600">{integration.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {connectionStatus === 'connected' && (
            <>
              <Button variant="secondary" onClick={handleSync} disabled={loading}>
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Sync Now
              </Button>
              <Button variant="danger" onClick={handleDisconnect}>
                <Unlink className="w-4 h-4 mr-2" />
                Disconnect
              </Button>
            </>
          )}
          {connectionStatus !== 'connected' && (
            <Button variant="primary" onClick={handleConnect} disabled={loading}>
              <Link className="w-4 h-4 mr-2" />
              Connect
            </Button>
          )}
        </div>
      </div>

      {/* Connection Status */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                connectionStatus === 'connected' ? 'bg-green-100' : 'bg-gray-100'
              }`}>
                {connectionStatus === 'connected' ? (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                ) : (
                  <XCircle className="w-6 h-6 text-gray-400" />
                )}
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold">Connection Status</h3>
                <p className={`text-sm ${connectionStatus === 'connected' ? 'text-green-600' : 'text-gray-500'}`}>
                  {connectionStatus === 'connected' ? 'Connected' : 'Not connected'}
                </p>
              </div>
            </div>
            {connectionStatus === 'connected' && lastSync && (
              <div className="text-right">
                <p className="text-sm text-gray-500">Last synced</p>
                <p className="text-sm font-medium">
                  {new Date(lastSync).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <div className="bg-white border-b">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {defaultTabs.map((tab) => {
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

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {children}
        </div>
      )}

      {activeTab === 'configuration' && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Configuration</h3>
            <div className="space-y-4">
              {configFields.map((field) => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {field.type === 'password' || field.type === 'secret' ? (
                    <div className="relative">
                      <Input
                        type={showSecrets[field.name] ? 'text' : 'password'}
                        value={config[field.name] || ''}
                        onChange={(e) => setConfig({ ...config, [field.name]: e.target.value })}
                        placeholder={field.placeholder}
                        required={field.required}
                      />
                      <button
                        type="button"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2"
                        onClick={() => setShowSecrets({ ...showSecrets, [field.name]: !showSecrets[field.name] })}
                      >
                        {showSecrets[field.name] ? (
                          <EyeOff className="w-4 h-4 text-gray-400" />
                        ) : (
                          <Eye className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                  ) : field.type === 'select' ? (
                    <select
                      value={config[field.name] || ''}
                      onChange={(e) => setConfig({ ...config, [field.name]: e.target.value })}
                      className="form-select rounded-md border-gray-300 w-full"
                      required={field.required}
                    >
                      <option value="">Select {field.label}</option>
                      {field.options.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : field.type === 'checkbox' ? (
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config[field.name] || false}
                        onChange={(e) => setConfig({ ...config, [field.name]: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm">{field.description}</span>
                    </label>
                  ) : (
                    <Input
                      type={field.type}
                      value={config[field.name] || ''}
                      onChange={(e) => setConfig({ ...config, [field.name]: e.target.value })}
                      placeholder={field.placeholder}
                      required={field.required}
                    />
                  )}
                  {field.description && field.type !== 'checkbox' && (
                    <p className="text-sm text-gray-500 mt-1">{field.description}</p>
                  )}
                </div>
              ))}
              <div className="pt-4 flex space-x-2">
                <Button variant="primary" onClick={saveConfiguration}>
                  <Save className="w-4 h-4 mr-2" />
                  Save Configuration
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={testConnection}
                  disabled={testingConnection}
                >
                  <TestTube className="w-4 h-4 mr-2" />
                  {testingConnection ? 'Testing...' : 'Test Connection'}
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'security' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">API Credentials</h3>
              <div className="space-y-4">
                <Alert variant="warning">
                  <AlertCircle className="w-4 h-4" />
                  <p>Keep your API credentials secure and never share them publicly.</p>
                </Alert>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key
                  </label>
                  <div className="flex space-x-2">
                    <Input
                      type={showSecrets.apiKey ? 'text' : 'password'}
                      value={config.apiKey || ''}
                      readOnly
                      className="flex-1"
                    />
                    <Button
                      variant="ghost"
                      onClick={() => setShowSecrets({ ...showSecrets, apiKey: !showSecrets.apiKey })}
                    >
                      {showSecrets.apiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
                {oauthConfig && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      OAuth Scopes
                    </label>
                    <div className="space-y-2">
                      {oauthConfig.scopes.map(scope => (
                        <div key={scope} className="flex items-center">
                          <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                          <span className="text-sm">{scope}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Rate Limits</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">API Calls Remaining</span>
                  <span className="font-medium">{rateLimits.remaining} / {rateLimits.limit}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${(rateLimits.remaining / rateLimits.limit) * 100}%` }}
                  />
                </div>
                <p className="text-sm text-gray-500">
                  Resets at {new Date(rateLimits.resetsAt).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'activity' && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Activity Log</h3>
            <div className="space-y-3">
              {activityLog.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between py-3 border-b">
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-3 ${
                      activity.status === 'success' ? 'bg-green-500' :
                      activity.status === 'error' ? 'bg-red-500' : 'bg-blue-500'
                    }`} />
                    <div>
                      <p className="font-medium text-sm">{activity.action}</p>
                      <p className="text-xs text-gray-500">
                        {activity.timestamp.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Badge variant={
                    activity.status === 'success' ? 'success' :
                    activity.status === 'error' ? 'danger' : 'info'
                  }>
                    {activity.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'api' && (
        <div className="space-y-6">
          {webhookEvents.length > 0 && (
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Webhook Events</h3>
                <div className="space-y-2">
                  {webhookEvents.map((event) => (
                    <div key={event} className="flex items-center justify-between py-2">
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-3" />
                        <span className="text-sm font-medium">{event}</span>
                      </div>
                      <Badge variant="secondary">POST</Badge>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Webhook URL
                  </label>
                  <Input
                    type="url"
                    placeholder="https://your-app.com/webhooks/integration-name"
                    value={config.webhookUrl || ''}
                    onChange={(e) => setConfig({ ...config, webhookUrl: e.target.value })}
                  />
                </div>
              </div>
            </Card>
          )}

          {apiEndpoints.length > 0 && (
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">API Endpoints</h3>
                <div className="space-y-3">
                  {apiEndpoints.map((endpoint) => (
                    <div key={endpoint.path} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <Badge variant={
                              endpoint.method === 'GET' ? 'info' :
                              endpoint.method === 'POST' ? 'success' :
                              endpoint.method === 'PUT' ? 'warning' :
                              'danger'
                            }>
                              {endpoint.method}
                            </Badge>
                            <span className="font-mono text-sm">{endpoint.path}</span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">{endpoint.description}</p>
                        </div>
                        <Button variant="ghost" size="sm">
                          <TestTube className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default BaseIntegration;