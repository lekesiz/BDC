import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { 
  Users, 
  Link, 
  Settings, 
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Download,
  Upload,
  FileText,
  Euro,
  Calendar,
  TrendingUp,
  Activity,
  Database,
  Shield,
  Briefcase
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const WedofIntegrationPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [syncStatus, setSyncStatus] = useState({
    lastSync: '2024-11-17 15:30',
    totalRecords: 1234,
    syncedToday: 45,
    failedRecords: 2
  });

  const syncHistory = [
    { id: 1, date: '2024-11-17 15:30', type: 'Beneficiaries', records: 23, status: 'success' },
    { id: 2, date: '2024-11-17 14:00', type: 'Programs', records: 5, status: 'success' },
    { id: 3, date: '2024-11-17 12:30', type: 'Financials', records: 87, status: 'failed', error: 'Invalid data format' },
    { id: 4, date: '2024-11-17 11:00', type: 'Activities', records: 34, status: 'success' }
  ];

  const dataMapping = [
    { bdc: 'beneficiary_id', wedof: 'person_id', status: 'mapped' },
    { bdc: 'first_name', wedof: 'prenom', status: 'mapped' },
    { bdc: 'last_name', wedof: 'nom', status: 'mapped' },
    { bdc: 'email', wedof: 'email', status: 'mapped' },
    { bdc: 'phone', wedof: 'telephone', status: 'mapped' },
    { bdc: 'program_name', wedof: 'formation', status: 'mapped' },
    { bdc: 'trainer_name', wedof: 'formateur', status: 'pending' },
    { bdc: 'completion_date', wedof: 'date_fin', status: 'error' }
  ];

  const financialSummary = {
    totalAllocated: 250000,
    totalSpent: 187500,
    pendingPayments: 12500,
    remainingBudget: 62500
  };

  const activityMetrics = [
    { month: 'Jan', beneficiaries: 120, programs: 8, spending: 22000 },
    { month: 'Feb', beneficiaries: 135, programs: 9, spending: 24500 },
    { month: 'Mar', beneficiaries: 150, programs: 10, spending: 28000 },
    { month: 'Apr', beneficiaries: 142, programs: 9, spending: 26800 },
    { month: 'May', beneficiaries: 165, programs: 11, spending: 31000 },
    { month: 'Jun', beneficiaries: 178, programs: 12, spending: 33500 }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Briefcase },
    { id: 'configuration', label: 'Configuration', icon: Settings },
    { id: 'data-mapping', label: 'Data Mapping', icon: Database },
    { id: 'sync', label: 'Sync', icon: RefreshCw },
    { id: 'financial', label: 'Financial', icon: Euro },
    { id: 'reports', label: 'Reports', icon: FileText }
  ];

  const handleConnect = () => {
    if (apiKey) {
      setLoading(true);
      setTimeout(() => {
        setIsConnected(true);
        setLoading(false);
      }, 2000);
    }
  };

  const handleSync = (type) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 3000);
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Wedof Integration</h1>
        {isConnected ? (
          <div className="flex space-x-2">
            <Button variant="secondary" onClick={() => handleSync('all')}>
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Sync All
            </Button>
            <Button variant="danger" onClick={() => setIsConnected(false)}>
              <XCircle className="w-4 h-4 mr-2" />
              Disconnect
            </Button>
          </div>
        ) : (
          <Button variant="primary" onClick={handleConnect} disabled={!apiKey}>
            <Link className="w-4 h-4 mr-2" />
            Connect to Wedof
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
                      {isConnected ? 'Connected to Wedof' : 'Not connected'}
                    </p>
                  </div>
                </div>
                {isConnected && (
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Last synced</p>
                    <p className="text-sm font-medium">{syncStatus.lastSync}</p>
                  </div>
                )}
              </div>

              {!isConnected && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">
                    Connect your Wedof account to sync beneficiary data, financial records, and program information.
                  </p>
                  <div className="space-y-3">
                    <Input
                      type="password"
                      placeholder="Enter your Wedof API key"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                    />
                    <p className="text-xs text-gray-500">
                      You can find your API key in Wedof Settings → API Access
                    </p>
                  </div>
                </div>
              )}

              {isConnected && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Records</p>
                    <p className="text-2xl font-bold text-gray-900">{syncStatus.totalRecords}</p>
                    <p className="text-xs text-gray-500 mt-1">All synced data</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Synced Today</p>
                    <p className="text-2xl font-bold text-green-600">{syncStatus.syncedToday}</p>
                    <p className="text-xs text-gray-500 mt-1">New records</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Failed Records</p>
                    <p className="text-2xl font-bold text-red-600">{syncStatus.failedRecords}</p>
                    <p className="text-xs text-gray-500 mt-1">Need attention</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Sync Status</p>
                    <p className="text-2xl font-bold text-blue-600">Active</p>
                    <p className="text-xs text-gray-500 mt-1">Auto-sync enabled</p>
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
                    <h3 className="text-lg font-semibold mb-4">Activity Overview</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={activityMetrics}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="month" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="beneficiaries" stroke="#3B82F6" name="Beneficiaries" />
                          <Line type="monotone" dataKey="programs" stroke="#10B981" name="Programs" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Financial Overview</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={[
                              { name: 'Spent', value: financialSummary.totalSpent },
                              { name: 'Pending', value: financialSummary.pendingPayments },
                              { name: 'Remaining', value: financialSummary.remainingBudget }
                            ]}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ value }) => `€${value.toLocaleString()}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {[0, 1, 2].map((index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index]} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </Card>
              </div>

              <Card>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Recent Sync History</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date & Time
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Data Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Records
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Details
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {syncHistory.map((sync) => (
                          <tr key={sync.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {sync.date}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {sync.type}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {sync.records}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                ${sync.status === 'success' ? 'bg-green-100 text-green-800' : 
                                  'bg-red-100 text-red-800'}`}>
                                {sync.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {sync.error || 'Completed successfully'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'configuration' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key
                  </label>
                  <div className="flex space-x-2">
                    <Input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="flex-1"
                    />
                    <Button variant="secondary">Update</Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Endpoint
                  </label>
                  <Input
                    type="text"
                    defaultValue="https://api.wedof.fr/v2/"
                    readOnly
                    className="bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organization ID
                  </label>
                  <Input
                    type="text"
                    placeholder="Your Wedof organization ID"
                  />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sync Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable automatic sync</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically sync data every hour
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sync Frequency
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>Every 15 minutes</option>
                    <option>Every 30 minutes</option>
                    <option>Every hour</option>
                    <option>Every 6 hours</option>
                    <option>Daily</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data to Sync
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Beneficiaries</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Programs</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Financial Data</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Activities</span>
                    </label>
                  </div>
                </div>

                <div className="pt-4">
                  <Button variant="primary">Save Settings</Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'data-mapping' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Field Mapping</h3>
              <p className="text-sm text-gray-600 mb-4">
                Map BDC fields to corresponding Wedof fields for proper data synchronization.
              </p>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        BDC Field
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Wedof Field
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {dataMapping.map((mapping, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {mapping.bdc}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <select className="form-select rounded-md border-gray-300 text-sm">
                            <option value={mapping.wedof}>{mapping.wedof}</option>
                            <option value="">-- Select field --</option>
                            <option value="autre_champ">autre_champ</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${mapping.status === 'mapped' ? 'bg-green-100 text-green-800' : 
                              mapping.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'}`}>
                            {mapping.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <Button variant="ghost" size="sm">Edit</Button>
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
              <h3 className="text-lg font-semibold mb-4">Custom Field Rules</h3>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Date Format Conversion</h4>
                    <Button variant="ghost" size="sm">Edit</Button>
                  </div>
                  <p className="text-sm text-gray-600">
                    Convert BDC date format (YYYY-MM-DD) to Wedof format (DD/MM/YYYY)
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Name Capitalization</h4>
                    <Button variant="ghost" size="sm">Edit</Button>
                  </div>
                  <p className="text-sm text-gray-600">
                    Automatically capitalize first and last names during sync
                  </p>
                </div>
                <Button variant="primary">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Custom Rule
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'sync' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Manual Sync</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('beneficiaries')}
                >
                  <Users className="w-5 h-5 text-blue-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Sync Beneficiaries</p>
                    <p className="text-sm text-gray-500">Import/export beneficiary data</p>
                  </div>
                </button>
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('programs')}
                >
                  <Briefcase className="w-5 h-5 text-green-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Sync Programs</p>
                    <p className="text-sm text-gray-500">Sync training program data</p>
                  </div>
                </button>
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('financial')}
                >
                  <Euro className="w-5 h-5 text-yellow-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Sync Financial</p>
                    <p className="text-sm text-gray-500">Import financial records</p>
                  </div>
                </button>
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('activities')}
                >
                  <Activity className="w-5 h-5 text-purple-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Sync Activities</p>
                    <p className="text-sm text-gray-500">Sync activity records</p>
                  </div>
                </button>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sync Progress</h3>
              {loading && (
                <div className="space-y-4">
                  <div className="flex items-center">
                    <RefreshCw className="w-5 h-5 mr-3 animate-spin text-blue-600" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">Syncing Beneficiaries...</span>
                        <span className="text-sm text-gray-500">45%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {!loading && (
                <p className="text-sm text-gray-600">No sync in progress</p>
              )}
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'financial' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Financial Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Total Allocated</p>
                  <p className="text-2xl font-bold text-gray-900">€{financialSummary.totalAllocated.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Total Spent</p>
                  <p className="text-2xl font-bold text-green-600">€{financialSummary.totalSpent.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-yellow-600">€{financialSummary.pendingPayments.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Remaining</p>
                  <p className="text-2xl font-bold text-blue-600">€{financialSummary.remainingBudget.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Spending Trend</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={activityMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="spending" fill="#3B82F6" name="Monthly Spending (€)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'reports' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Export Reports</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Beneficiary Report</h4>
                    <FileText className="w-5 h-5 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Export all beneficiary data with program enrollments
                  </p>
                  <Button variant="secondary" size="sm" className="w-full">
                    <Download className="w-4 h-4 mr-2" />
                    Export CSV
                  </Button>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Financial Report</h4>
                    <Euro className="w-5 h-5 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Generate detailed financial report for all programs
                  </p>
                  <Button variant="secondary" size="sm" className="w-full">
                    <Download className="w-4 h-4 mr-2" />
                    Export PDF
                  </Button>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Activity Log</h4>
                    <Activity className="w-5 h-5 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Export detailed activity logs and sync history
                  </p>
                  <Button variant="secondary" size="sm" className="w-full">
                    <Download className="w-4 h-4 mr-2" />
                    Export JSON
                  </Button>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Custom Report</h4>
                    <Settings className="w-5 h-5 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    Create custom report with selected data fields
                  </p>
                  <Button variant="primary" size="sm" className="w-full">
                    Create Report
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

export default WedofIntegrationPage;