import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { 
  CreditCard, 
  Link, 
  Settings, 
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign,
  Euro,
  ShoppingCart,
  Users,
  TrendingUp,
  Shield,
  Lock,
  BarChart,
  RefreshCw,
  FileText,
  Calendar,
  Globe
} from 'lucide-react';
import { LineChart, Line, BarChart as RechartsBarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PaymentIntegrationPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  const [paymentConfig, setPaymentConfig] = useState({
    provider: 'stripe',
    apiKey: '',
    secretKey: '',
    webhookSecret: ''
  });

  const paymentStats = {
    totalRevenue: 125450,
    monthlyRevenue: 12560,
    totalTransactions: 3456,
    successRate: 98.5,
    avgTransaction: 36.25,
    pendingPayouts: 4520,
    refunds: 234,
    disputes: 3
  };

  const revenueData = [
    { month: 'Jan', revenue: 18500, transactions: 456 },
    { month: 'Feb', revenue: 19800, transactions: 489 },
    { month: 'Mar', revenue: 21200, transactions: 523 },
    { month: 'Apr', revenue: 20500, transactions: 512 },
    { month: 'May', revenue: 22800, transactions: 567 },
    { month: 'Jun', revenue: 24600, transactions: 589 }
  ];

  const paymentMethods = [
    { method: 'Credit Card', count: 2345, percentage: 68 },
    { method: 'Debit Card', count: 678, percentage: 20 },
    { method: 'Bank Transfer', count: 234, percentage: 7 },
    { method: 'Digital Wallet', count: 156, percentage: 4 },
    { method: 'Other', count: 43, percentage: 1 }
  ];

  const recentTransactions = [
    { id: 'TXN-001', date: '2024-11-17 15:30', amount: 89.99, status: 'completed', method: 'Visa ****1234' },
    { id: 'TXN-002', date: '2024-11-17 14:45', amount: 129.00, status: 'completed', method: 'Mastercard ****5678' },
    { id: 'TXN-003', date: '2024-11-17 13:20', amount: 45.50, status: 'pending', method: 'Bank Transfer' },
    { id: 'TXN-004', date: '2024-11-17 12:15', amount: 200.00, status: 'failed', method: 'Visa ****9012' },
    { id: 'TXN-005', date: '2024-11-17 11:30', amount: 75.25, status: 'refunded', method: 'PayPal' }
  ];

  const subscriptions = [
    { id: 1, plan: 'Basic Training', price: 49.99, frequency: 'monthly', active: 234 },
    { id: 2, plan: 'Pro Development', price: 99.99, frequency: 'monthly', active: 156 },
    { id: 3, plan: 'Enterprise', price: 299.99, frequency: 'monthly', active: 45 },
    { id: 4, plan: 'Annual Basic', price: 499.99, frequency: 'yearly', active: 89 }
  ];

  const paymentProviders = [
    { value: 'stripe', label: 'Stripe', icon: CreditCard },
    { value: 'paypal', label: 'PayPal', icon: CreditCard },
    { value: 'square', label: 'Square', icon: CreditCard },
    { value: 'razorpay', label: 'Razorpay', icon: CreditCard }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: DollarSign },
    { id: 'transactions', label: 'Transactions', icon: FileText },
    { id: 'subscriptions', label: 'Subscriptions', icon: RefreshCw },
    { id: 'methods', label: 'Payment Methods', icon: CreditCard },
    { id: 'analytics', label: 'Analytics', icon: BarChart },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const handleConnect = () => {
    if (paymentConfig.apiKey && paymentConfig.secretKey) {
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
        <h1 className="text-3xl font-bold text-gray-900">Payment Gateway Integration</h1>
        {isConnected ? (
          <div className="flex space-x-2">
            <Button variant="primary">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Create Payment
            </Button>
            <Button variant="danger" onClick={() => setIsConnected(false)}>
              <XCircle className="w-4 h-4 mr-2" />
              Disconnect
            </Button>
          </div>
        ) : (
          <Button variant="primary" onClick={handleConnect} disabled={!paymentConfig.apiKey || !paymentConfig.secretKey}>
            <Link className="w-4 h-4 mr-2" />
            Connect Payment Gateway
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
                      {isConnected ? `Connected to ${paymentConfig.provider}` : 'Not connected'}
                    </p>
                  </div>
                </div>
                {isConnected && (
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Available Balance</p>
                    <p className="text-sm font-medium">$12,345.67</p>
                  </div>
                )}
              </div>

              {!isConnected && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-3">
                    Connect your payment gateway to accept payments, manage subscriptions, and track revenue.
                  </p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Payment Provider
                      </label>
                      <select 
                        value={paymentConfig.provider}
                        onChange={(e) => setPaymentConfig({...paymentConfig, provider: e.target.value})}
                        className="form-select rounded-md border-gray-300 w-full"
                      >
                        {paymentProviders.map((provider) => (
                          <option key={provider.value} value={provider.value}>
                            {provider.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <Input
                      type="text"
                      placeholder="API Key"
                      value={paymentConfig.apiKey}
                      onChange={(e) => setPaymentConfig({...paymentConfig, apiKey: e.target.value})}
                    />
                    <Input
                      type="password"
                      placeholder="Secret Key"
                      value={paymentConfig.secretKey}
                      onChange={(e) => setPaymentConfig({...paymentConfig, secretKey: e.target.value})}
                    />
                    {paymentConfig.provider === 'stripe' && (
                      <Input
                        type="text"
                        placeholder="Webhook Secret (optional)"
                        value={paymentConfig.webhookSecret}
                        onChange={(e) => setPaymentConfig({...paymentConfig, webhookSecret: e.target.value})}
                      />
                    )}
                  </div>
                </div>
              )}

              {isConnected && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Revenue</p>
                    <p className="text-2xl font-bold text-gray-900">${paymentStats.totalRevenue.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 mt-1">All time</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">This Month</p>
                    <p className="text-2xl font-bold text-green-600">${paymentStats.monthlyRevenue.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 mt-1">+12% from last month</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold text-blue-600">{paymentStats.successRate}%</p>
                    <p className="text-xs text-gray-500 mt-1">Industry avg: 95%</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Avg Transaction</p>
                    <p className="text-2xl font-bold text-gray-900">${paymentStats.avgTransaction}</p>
                    <p className="text-xs text-gray-500 mt-1">Per payment</p>
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
                    <h3 className="text-lg font-semibold mb-4">Revenue Trend</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={revenueData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="month" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="revenue" stroke="#3B82F6" name="Revenue ($)" />
                          <Line type="monotone" dataKey="transactions" stroke="#10B981" name="Transactions" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Payment Methods</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={paymentMethods}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ method, percentage }) => `${method} (${percentage}%)`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="count"
                          >
                            {paymentMethods.map((entry, index) => (
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
                      <DollarSign className="w-5 h-5 text-blue-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Create Invoice</p>
                        <p className="text-sm text-gray-500">Generate a new payment invoice</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <RefreshCw className="w-5 h-5 text-green-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Setup Subscription</p>
                        <p className="text-sm text-gray-500">Create recurring payment plan</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <FileText className="w-5 h-5 text-purple-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Export Reports</p>
                        <p className="text-sm text-gray-500">Download payment reports</p>
                      </div>
                    </button>
                    <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <Shield className="w-5 h-5 text-orange-600 mr-3" />
                      <div className="text-left">
                        <p className="font-medium">Dispute Center</p>
                        <p className="text-sm text-gray-500">Manage payment disputes</p>
                      </div>
                    </button>
                  </div>
                </div>
              </Card>
            </>
          )}
        </div>
      )}

      {activeTab === 'transactions' && isConnected && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Transactions</p>
                    <p className="text-2xl font-bold text-gray-900">{paymentStats.totalTransactions}</p>
                  </div>
                  <FileText className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Pending</p>
                    <p className="text-2xl font-bold text-yellow-600">${paymentStats.pendingPayouts}</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Refunds</p>
                    <p className="text-2xl font-bold text-red-600">{paymentStats.refunds}</p>
                  </div>
                  <RefreshCw className="w-8 h-8 text-red-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Disputes</p>
                    <p className="text-2xl font-bold text-orange-600">{paymentStats.disputes}</p>
                  </div>
                  <AlertCircle className="w-8 h-8 text-orange-500" />
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Recent Transactions</h3>
                <Button variant="secondary" size="sm">
                  Export CSV
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Transaction ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date & Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {recentTransactions.map((transaction) => (
                      <tr key={transaction.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {transaction.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {transaction.date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          ${transaction.amount}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {transaction.method}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${transaction.status === 'completed' ? 'bg-green-100 text-green-800' :
                              transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              transaction.status === 'failed' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'}`}>
                            {transaction.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2">
                          <Button variant="ghost" size="sm">View</Button>
                          {transaction.status === 'completed' && (
                            <Button variant="ghost" size="sm">Refund</Button>
                          )}
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

      {activeTab === 'subscriptions' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Subscription Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Active Subscriptions</p>
                  <p className="text-2xl font-bold text-gray-900">524</p>
                  <p className="text-xs text-green-600 mt-1">+8% from last month</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Monthly Recurring</p>
                  <p className="text-2xl font-bold text-green-600">$45,678</p>
                  <p className="text-xs text-gray-500 mt-1">MRR</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Churn Rate</p>
                  <p className="text-2xl font-bold text-red-600">3.2%</p>
                  <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Subscription Plans</h3>
                <Button variant="primary" size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Plan
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Billing Cycle</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active Subscribers</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {subscriptions.map((subscription) => (
                      <tr key={subscription.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {subscription.plan}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${subscription.price}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {subscription.frequency}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {subscription.active}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                          ${(subscription.price * subscription.active).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 space-x-2">
                          <Button variant="ghost" size="sm">Edit</Button>
                          <Button variant="ghost" size="sm">View</Button>
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

      {activeTab === 'methods' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Accepted Payment Methods</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <CreditCard className="w-5 h-5 text-blue-600 mr-3" />
                      <h4 className="font-medium">Credit/Debit Cards</h4>
                    </div>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span className="text-sm">Enabled</span>
                    </label>
                  </div>
                  <p className="text-sm text-gray-600">Accept Visa, Mastercard, Amex, Discover</p>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <DollarSign className="w-5 h-5 text-green-600 mr-3" />
                      <h4 className="font-medium">Bank Transfers</h4>
                    </div>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span className="text-sm">Enabled</span>
                    </label>
                  </div>
                  <p className="text-sm text-gray-600">ACH transfers and wire transfers</p>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <Globe className="w-5 h-5 text-purple-600 mr-3" />
                      <h4 className="font-medium">Digital Wallets</h4>
                    </div>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span className="text-sm">Enabled</span>
                    </label>
                  </div>
                  <p className="text-sm text-gray-600">PayPal, Apple Pay, Google Pay</p>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <Euro className="w-5 h-5 text-orange-600 mr-3" />
                      <h4 className="font-medium">International</h4>
                    </div>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span className="text-sm">Enabled</span>
                    </label>
                  </div>
                  <p className="text-sm text-gray-600">SEPA, iDEAL, Bancontact</p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Currency Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Currency
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="GBP">GBP - British Pound</option>
                    <option value="CAD">CAD - Canadian Dollar</option>
                  </select>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="font-medium">Enable multi-currency</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Accept payments in multiple currencies
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Automatic currency conversion</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Convert foreign currencies to your primary currency
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'analytics' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Revenue Analytics</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsBarChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="revenue" fill="#3B82F6" name="Revenue ($)" />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Payment Success Rates</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Credit Cards</span>
                      <span className="text-sm text-gray-500">98.5%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: '98.5%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Bank Transfers</span>
                      <span className="text-sm text-gray-500">95.2%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: '95.2%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Digital Wallets</span>
                      <span className="text-sm text-gray-500">99.1%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: '99.1%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Top Revenue Sources</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Pro Development Plan</p>
                      <p className="text-sm text-gray-500">156 subscribers</p>
                    </div>
                    <p className="font-medium text-green-600">$15,594/mo</p>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Basic Training Plan</p>
                      <p className="text-sm text-gray-500">234 subscribers</p>
                    </div>
                    <p className="font-medium text-green-600">$11,698/mo</p>
                  </div>
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">Enterprise Plan</p>
                      <p className="text-sm text-gray-500">45 subscribers</p>
                    </div>
                    <p className="font-medium text-green-600">$13,500/mo</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'settings' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Payment Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Payment Provider
                  </label>
                  <select 
                    value={paymentConfig.provider}
                    onChange={(e) => setPaymentConfig({...paymentConfig, provider: e.target.value})}
                    className="form-select rounded-md border-gray-300 w-full"
                  >
                    {paymentProviders.map((provider) => (
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
                      type="text"
                      value={paymentConfig.apiKey}
                      onChange={(e) => setPaymentConfig({...paymentConfig, apiKey: e.target.value})}
                      className="flex-1"
                    />
                    <Button variant="secondary">Update</Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Secret Key
                  </label>
                  <Input
                    type="password"
                    value={paymentConfig.secretKey}
                    onChange={(e) => setPaymentConfig({...paymentConfig, secretKey: e.target.value})}
                  />
                </div>

                {paymentConfig.provider === 'stripe' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Webhook Endpoint
                    </label>
                    <div className="flex space-x-2">
                      <Input
                        type="text"
                        value="https://yourdomain.com/webhooks/stripe"
                        readOnly
                        className="flex-1 bg-gray-50"
                      />
                      <Button variant="secondary" size="sm">Copy</Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Enable 3D Secure</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Require additional authentication for card payments
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">PCI compliance mode</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Ensure all payment data is handled securely
                  </p>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Fraud detection</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Enable automatic fraud detection and prevention
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Risk threshold
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>Low (Block high-risk payments)</option>
                    <option>Medium (Balanced)</option>
                    <option>High (Allow most payments)</option>
                  </select>
                </div>

                <div className="pt-4">
                  <Button variant="primary">Save Settings</Button>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Webhook Configuration</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-start">
                    <Lock className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900">Secure Webhooks</h4>
                      <p className="text-sm text-blue-800 mt-1">
                        All webhook endpoints are secured with signature verification to ensure data integrity.
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Webhook Events
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Payment succeeded</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Payment failed</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Subscription created</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span>Subscription cancelled</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span>Dispute created</span>
                    </label>
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

export default PaymentIntegrationPage;