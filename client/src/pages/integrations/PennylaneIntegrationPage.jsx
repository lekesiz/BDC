import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { 
  Calculator, 
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
  TrendingUp,
  Activity,
  Receipt,
  CreditCard,
  DollarSign,
  PieChart,
  BarChart3,
  Building
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PennylaneIntegrationPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  const [apiCredentials, setApiCredentials] = useState({
    apiKey: '',
    companyId: ''
  });

  const accountingMetrics = {
    totalRevenue: 450000,
    totalExpenses: 320000,
    netProfit: 130000,
    taxLiability: 45000,
    cashFlow: 85000,
    unpaidInvoices: 23,
    overduePayments: 5,
    bankBalance: 125000
  };

  const monthlyData = [
    { month: 'Jan', revenue: 65000, expenses: 45000, profit: 20000 },
    { month: 'Feb', revenue: 72000, expenses: 48000, profit: 24000 },
    { month: 'Mar', revenue: 68000, expenses: 52000, profit: 16000 },
    { month: 'Apr', revenue: 75000, expenses: 50000, profit: 25000 },
    { month: 'May', revenue: 82000, expenses: 55000, profit: 27000 },
    { month: 'Jun', revenue: 88000, expenses: 60000, profit: 28000 }
  ];

  const expenseCategories = [
    { category: 'Salaries', amount: 180000, percentage: 56 },
    { category: 'Training Materials', amount: 45000, percentage: 14 },
    { category: 'Facilities', amount: 35000, percentage: 11 },
    { category: 'Technology', amount: 28000, percentage: 9 },
    { category: 'Marketing', amount: 20000, percentage: 6 },
    { category: 'Other', amount: 12000, percentage: 4 }
  ];

  const recentTransactions = [
    { id: 1, date: '2024-11-17', description: 'Program Fee - Python Training', amount: 2500, type: 'income' },
    { id: 2, date: '2024-11-17', description: 'Instructor Payment - John Doe', amount: -1200, type: 'expense' },
    { id: 3, date: '2024-11-16', description: 'Office Rent', amount: -3500, type: 'expense' },
    { id: 4, date: '2024-11-16', description: 'Grant from Foundation', amount: 25000, type: 'income' },
    { id: 5, date: '2024-11-15', description: 'Software Licenses', amount: -450, type: 'expense' }
  ];

  const syncSettings = {
    autoSync: true,
    syncInterval: '1h',
    syncCategories: ['invoices', 'expenses', 'bank', 'tax'],
    reconciliation: true
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Calculator },
    { id: 'accounting', label: 'Accounting', icon: Building },
    { id: 'invoices', label: 'Invoices', icon: Receipt },
    { id: 'expenses', label: 'Expenses', icon: CreditCard },
    { id: 'sync', label: 'Sync', icon: RefreshCw },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const handleConnect = () => {
    if (apiCredentials.apiKey && apiCredentials.companyId) {
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

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Pennylane Integration</h1>
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
          <Button variant="primary" onClick={handleConnect} disabled={!apiCredentials.apiKey || !apiCredentials.companyId}>
            <Link className="w-4 h-4 mr-2" />
            Connect to Pennylane
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
                      {isConnected ? 'Connected to Pennylane' : 'Not connected'}
                    </p>
                  </div>
                </div>
                {isConnected && (
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Last synced</p>
                    <p className="text-sm font-medium">10 minutes ago</p>
                  </div>
                )}
              </div>

              {!isConnected && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">
                    Connect your Pennylane account to sync accounting data, invoices, and expenses.
                  </p>
                  <div className="space-y-3">
                    <Input
                      type="password"
                      placeholder="Enter your Pennylane API key"
                      value={apiCredentials.apiKey}
                      onChange={(e) => setApiCredentials({...apiCredentials, apiKey: e.target.value})}
                    />
                    <Input
                      type="text"
                      placeholder="Enter your Company ID"
                      value={apiCredentials.companyId}
                      onChange={(e) => setApiCredentials({...apiCredentials, companyId: e.target.value})}
                    />
                    <p className="text-xs text-gray-500">
                      You can find these in Pennylane Settings → API Access
                    </p>
                  </div>
                </div>
              )}

              {isConnected && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Revenue YTD</p>
                    <p className="text-2xl font-bold text-gray-900">€{accountingMetrics.totalRevenue.toLocaleString()}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Expenses YTD</p>
                    <p className="text-2xl font-bold text-red-600">€{accountingMetrics.totalExpenses.toLocaleString()}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Net Profit</p>
                    <p className="text-2xl font-bold text-green-600">€{accountingMetrics.netProfit.toLocaleString()}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Bank Balance</p>
                    <p className="text-2xl font-bold text-blue-600">€{accountingMetrics.bankBalance.toLocaleString()}</p>
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
                    <h3 className="text-lg font-semibold mb-4">Revenue vs Expenses</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={monthlyData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="month" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="revenue" stroke="#3B82F6" name="Revenue" />
                          <Line type="monotone" dataKey="expenses" stroke="#EF4444" name="Expenses" />
                          <Line type="monotone" dataKey="profit" stroke="#10B981" name="Profit" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Expense Categories</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <RechartsPieChart>
                          <Pie
                            data={expenseCategories}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ category, percentage }) => `${category} (${percentage}%)`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="amount"
                          >
                            {expenseCategories.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </RechartsPieChart>
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
                      <Receipt className="w-5 h-5 text-blue-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Create Invoice</p>
                        <p className="text-sm text-gray-500">Generate a new invoice in Pennylane</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <CreditCard className="w-5 h-5 text-green-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Record Expense</p>
                        <p className="text-sm text-gray-500">Add a new expense transaction</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <BarChart3 className="w-5 h-5 text-purple-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Financial Report</p>
                        <p className="text-sm text-gray-500">Generate comprehensive report</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Building className="w-5 h-5 text-gray-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Bank Reconciliation</p>
                        <p className="text-sm text-gray-500">Reconcile bank transactions</p>
                      </div>
                    </button>
                  </div>
                </div>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'accounting' && isConnected && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Cash Flow</p>
                    <p className="text-2xl font-bold text-gray-900">€{accountingMetrics.cashFlow.toLocaleString()}</p>
                    <p className="text-xs text-green-600 mt-1">+12% from last month</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Tax Liability</p>
                    <p className="text-2xl font-bold text-gray-900">€{accountingMetrics.taxLiability.toLocaleString()}</p>
                    <p className="text-xs text-gray-600 mt-1">Q4 2024</p>
                  </div>
                  <Euro className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Profit Margin</p>
                    <p className="text-2xl font-bold text-gray-900">28.9%</p>
                    <p className="text-xs text-green-600 mt-1">+2.3% improvement</p>
                  </div>
                  <PieChart className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {recentTransactions.map((transaction) => (
                      <tr key={transaction.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {transaction.date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {transaction.description}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${transaction.type === 'income' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {transaction.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <span className={transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}>
                            €{Math.abs(transaction.amount).toLocaleString()}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Reconciled
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
              <h3 className="text-lg font-semibold mb-4">Chart of Accounts</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <Building className="w-5 h-5 mr-3 text-blue-600" />
                    <div>
                      <p className="font-medium">Assets</p>
                      <p className="text-sm text-gray-500">Bank accounts, receivables, inventory</p>
                    </div>
                  </div>
                  <span className="text-lg font-semibold">€358,000</span>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <CreditCard className="w-5 h-5 mr-3 text-red-600" />
                    <div>
                      <p className="font-medium">Liabilities</p>
                      <p className="text-sm text-gray-500">Loans, payables, taxes due</p>
                    </div>
                  </div>
                  <span className="text-lg font-semibold">€145,000</span>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <DollarSign className="w-5 h-5 mr-3 text-green-600" />
                    <div>
                      <p className="font-medium">Equity</p>
                      <p className="text-sm text-gray-500">Capital, reserves, retained earnings</p>
                    </div>
                  </div>
                  <span className="text-lg font-semibold">€213,000</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'invoices' && isConnected && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Unpaid Invoices</p>
                    <p className="text-2xl font-bold text-gray-900">{accountingMetrics.unpaidInvoices}</p>
                    <p className="text-xs text-gray-600 mt-1">€45,000 pending</p>
                  </div>
                  <Receipt className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Overdue</p>
                    <p className="text-2xl font-bold text-red-600">{accountingMetrics.overduePayments}</p>
                    <p className="text-xs text-gray-600 mt-1">€12,000 overdue</p>
                  </div>
                  <AlertCircle className="w-8 h-8 text-red-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Paid This Month</p>
                    <p className="text-2xl font-bold text-green-600">32</p>
                    <p className="text-xs text-gray-600 mt-1">€78,000 collected</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Invoices</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  New Invoice
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice #</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Client</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">INV-2024-089</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Tech Academy</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-15</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">€3,500</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                          Pending
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <Button variant="ghost" size="sm">View</Button>
                      </td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">INV-2024-088</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">City Foundation</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-10</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">€15,000</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Paid
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <Button variant="ghost" size="sm">View</Button>
                      </td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">INV-2024-087</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">DataCorp Inc.</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-05</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">€5,200</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          Overdue
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <Button variant="ghost" size="sm">View</Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'expenses' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Expense Overview</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={expenseCategories}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="amount" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Expenses</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Expense
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Receipt</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-17</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Office Supplies Ltd</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Office</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">€450</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <FileText className="w-4 h-4 text-green-500" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <Button variant="ghost" size="sm">View</Button>
                      </td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-16</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Training Materials Co.</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Education</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">€1,200</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <FileText className="w-4 h-4 text-green-500" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <Button variant="ghost" size="sm">View</Button>
                      </td>
                    </tr>
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2024-11-15</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">CloudTech Services</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Technology</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">€2,500</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <AlertCircle className="w-4 h-4 text-yellow-500" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <Button variant="ghost" size="sm">Upload</Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'sync' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sync Control</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('invoices')}
                >
                  <Receipt className="w-5 h-5 text-blue-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Sync Invoices</p>
                    <p className="text-sm text-gray-500">Import/export invoice data</p>
                  </div>
                </button>
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('expenses')}
                >
                  <CreditCard className="w-5 h-5 text-red-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Sync Expenses</p>
                    <p className="text-sm text-gray-500">Sync expense transactions</p>
                  </div>
                </button>
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('bank')}
                >
                  <Building className="w-5 h-5 text-green-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Bank Transactions</p>
                    <p className="text-sm text-gray-500">Sync bank account data</p>
                  </div>
                </button>
                <button 
                  className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => handleSync('tax')}
                >
                  <Euro className="w-5 h-5 text-yellow-600 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Tax Data</p>
                    <p className="text-sm text-gray-500">Sync tax-related information</p>
                  </div>
                </button>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sync History</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                    <div>
                      <p className="font-medium">Bank Transactions</p>
                      <p className="text-sm text-gray-500">2024-11-17 10:30 AM - 145 transactions synced</p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">5 min ago</span>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                    <div>
                      <p className="font-medium">Invoices</p>
                      <p className="text-sm text-gray-500">2024-11-17 10:00 AM - 23 invoices updated</p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">35 min ago</span>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <XCircle className="w-5 h-5 text-red-500 mr-3" />
                    <div>
                      <p className="font-medium">Expenses</p>
                      <p className="text-sm text-gray-500">2024-11-17 09:30 AM - Failed: API rate limit</p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">1 hour ago</span>
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
              <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key
                  </label>
                  <div className="flex space-x-2">
                    <Input
                      type="password"
                      value={apiCredentials.apiKey}
                      onChange={(e) => setApiCredentials({...apiCredentials, apiKey: e.target.value})}
                      className="flex-1"
                    />
                    <Button variant="secondary">Update</Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company ID
                  </label>
                  <Input
                    type="text"
                    value={apiCredentials.companyId}
                    onChange={(e) => setApiCredentials({...apiCredentials, companyId: e.target.value})}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Endpoint
                  </label>
                  <Input
                    type="text"
                    defaultValue="https://api.pennylane.com/v1/"
                    readOnly
                    className="bg-gray-50"
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
                    <input 
                      type="checkbox" 
                      className="mr-2" 
                      checked={syncSettings.autoSync}
                      onChange={(e) => setSyncSettings({...syncSettings, autoSync: e.target.checked})}
                    />
                    <span className="font-medium">Enable automatic sync</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically sync data at regular intervals
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sync Interval
                  </label>
                  <select 
                    value={syncSettings.syncInterval}
                    onChange={(e) => setSyncSettings({...syncSettings, syncInterval: e.target.value})}
                    className="form-select rounded-md border-gray-300 w-full"
                  >
                    <option value="30m">Every 30 minutes</option>
                    <option value="1h">Every hour</option>
                    <option value="6h">Every 6 hours</option>
                    <option value="1d">Daily</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data Categories
                  </label>
                  <div className="space-y-2">
                    {['invoices', 'expenses', 'bank', 'tax'].map((category) => (
                      <label key={category} className="flex items-center">
                        <input
                          type="checkbox"
                          className="mr-2"
                          checked={syncSettings.syncCategories.includes(category)}
                          onChange={() => {}}
                        />
                        <span className="capitalize">{category}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="flex items-center">
                    <input 
                      type="checkbox" 
                      className="mr-2" 
                      checked={syncSettings.reconciliation}
                      onChange={(e) => setSyncSettings({...syncSettings, reconciliation: e.target.checked})}
                    />
                    <span className="font-medium">Auto-reconciliation</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically reconcile bank transactions
                  </p>
                </div>

                <div className="pt-4">
                  <Button variant="primary">Save Settings</Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PennylaneIntegrationPage;