import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Alert } from '../../ui/alert';
import {
  CreditCard,
  DollarSign,
  TrendingUp,
  Users,
  ShoppingCart,
  Receipt,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  Shield,
  FileText
} from 'lucide-react';
const StripeIntegration = ({ integration, onBack }) => {
  const [accountInfo, setAccountInfo] = useState({
    accountId: 'acct_1234567890',
    businessName: 'BDC Academy',
    mode: 'live',
    currency: 'EUR',
    payoutsEnabled: true,
    chargesEnabled: true
  });
  const [financialStats, setFinancialStats] = useState({
    revenue: {
      today: 2456.78,
      thisMonth: 45678.90,
      lastMonth: 42345.67
    },
    transactions: {
      today: 23,
      thisMonth: 456,
      pending: 12
    },
    subscriptions: {
      active: 234,
      trial: 45,
      canceled: 12
    }
  });
  const [paymentMethods, setPaymentMethods] = useState({
    card: true,
    sepa: true,
    applePay: true,
    googlePay: true,
    bankTransfer: false,
    ideal: false
  });
  const [products, setProducts] = useState([
    { id: '1', name: 'Python Programming Course', price: 299, currency: 'EUR', sales: 145, status: 'active' },
    { id: '2', name: 'Web Development Bootcamp', price: 499, currency: 'EUR', sales: 89, status: 'active' },
    { id: '3', name: 'Monthly Subscription', price: 49, currency: 'EUR', sales: 234, status: 'active', recurring: true },
    { id: '4', name: 'Annual Subscription', price: 399, currency: 'EUR', sales: 67, status: 'active', recurring: true }
  ]);
  const configFields = [
    {
      name: 'publishableKey',
      label: 'Publishable Key',
      type: 'text',
      placeholder: 'pk_live_...',
      required: true,
      description: 'Your Stripe publishable key'
    },
    {
      name: 'secretKey',
      label: 'Secret Key',
      type: 'password',
      placeholder: 'sk_live_...',
      required: true,
      description: 'Keep this secure - never expose in client code'
    },
    {
      name: 'webhookSecret',
      label: 'Webhook Signing Secret',
      type: 'password',
      placeholder: 'whsec_...',
      required: false,
      description: 'For webhook endpoint verification'
    },
    {
      name: 'statementDescriptor',
      label: 'Statement Descriptor',
      type: 'text',
      placeholder: 'BDC ACADEMY',
      required: false,
      description: 'What appears on customer statements'
    },
    {
      name: 'automaticTax',
      label: 'Enable automatic tax calculation',
      type: 'checkbox',
      description: 'Let Stripe calculate taxes automatically'
    }
  ];
  const webhookEvents = [
    'payment_intent.succeeded',
    'payment_intent.failed',
    'charge.succeeded',
    'charge.failed',
    'customer.subscription.created',
    'customer.subscription.updated',
    'customer.subscription.deleted',
    'invoice.paid',
    'invoice.payment_failed'
  ];
  const apiEndpoints = [
    {
      method: 'POST',
      path: '/api/integrations/stripe/create-payment-intent',
      description: 'Create a payment intent'
    },
    {
      method: 'POST',
      path: '/api/integrations/stripe/create-subscription',
      description: 'Create a new subscription'
    },
    {
      method: 'GET',
      path: '/api/integrations/stripe/customers',
      description: 'List all customers'
    },
    {
      method: 'POST',
      path: '/api/integrations/stripe/refund',
      description: 'Process a refund'
    }
  ];
  const recentTransactions = [
    { id: '1', customer: 'John Doe', amount: 299, currency: 'EUR', status: 'succeeded', time: '5 minutes ago', description: 'Python Programming Course' },
    { id: '2', customer: 'Jane Smith', amount: 49, currency: 'EUR', status: 'succeeded', time: '30 minutes ago', description: 'Monthly Subscription' },
    { id: '3', customer: 'Mike Johnson', amount: 499, currency: 'EUR', status: 'processing', time: '1 hour ago', description: 'Web Development Bootcamp' },
    { id: '4', customer: 'Sarah Wilson', amount: 399, currency: 'EUR', status: 'failed', time: '2 hours ago', description: 'Annual Subscription', error: 'Card declined' }
  ];
  const customOverview = (
    <>
      {/* Account Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <CreditCard className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">{accountInfo.businessName}</h3>
                <p className="text-sm text-gray-500">
                  {accountInfo.accountId} · {accountInfo.mode === 'live' ? 'Live Mode' : 'Test Mode'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {accountInfo.chargesEnabled ? (
                <Badge variant="success">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Charges Enabled
                </Badge>
              ) : (
                <Badge variant="danger">
                  <AlertCircle className="w-3 h-3 mr-1" />
                  Charges Disabled
                </Badge>
              )}
              {accountInfo.payoutsEnabled && (
                <Badge variant="success">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Payouts Enabled
                </Badge>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Today's Revenue</p>
                <TrendingUp className="w-4 h-4 text-green-500" />
              </div>
              <p className="text-2xl font-bold">€{financialStats.revenue.today.toLocaleString()}</p>
              <p className="text-sm text-gray-500">{financialStats.transactions.today} transactions</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">This Month</p>
                <DollarSign className="w-4 h-4 text-purple-500" />
              </div>
              <p className="text-2xl font-bold">€{financialStats.revenue.thisMonth.toLocaleString()}</p>
              <p className="text-sm text-green-600">
                +{((financialStats.revenue.thisMonth - financialStats.revenue.lastMonth) / financialStats.revenue.lastMonth * 100).toFixed(1)}% vs last month
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Active Subscriptions</p>
                <Users className="w-4 h-4 text-blue-500" />
              </div>
              <p className="text-2xl font-bold">{financialStats.subscriptions.active}</p>
              <p className="text-sm text-gray-500">{financialStats.subscriptions.trial} in trial</p>
            </div>
          </div>
        </div>
      </Card>
      {/* Payment Methods */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Accepted Payment Methods</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(paymentMethods).map(([method, enabled]) => (
              <div key={method} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <CreditCard className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="font-medium capitalize">
                    {method.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={() => setPaymentMethods({
                      ...paymentMethods,
                      [method]: !enabled
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Products & Prices */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Products & Prices</h3>
            <Button variant="primary" size="sm">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Add Product
            </Button>
          </div>
          <div className="space-y-3">
            {products.map((product) => (
              <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">{product.name}</p>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-sm text-gray-600">
                      €{product.price} {product.currency}
                    </span>
                    {product.recurring && (
                      <Badge variant="secondary" size="sm">Recurring</Badge>
                    )}
                    <span className="text-sm text-gray-500">
                      {product.sales} sales
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={product.status === 'active' ? 'success' : 'secondary'}>
                    {product.status}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    Edit
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Recent Transactions */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Transactions</h3>
            <Button variant="ghost" size="sm">
              <BarChart3 className="w-4 h-4 mr-2" />
              View All
            </Button>
          </div>
          <div className="space-y-3">
            {recentTransactions.map((transaction) => (
              <div key={transaction.id} className="flex items-start justify-between py-3 border-b">
                <div>
                  <div className="flex items-center space-x-2">
                    <p className="font-medium">{transaction.customer}</p>
                    <Badge variant={
                      transaction.status === 'succeeded' ? 'success' :
                      transaction.status === 'processing' ? 'warning' : 'danger'
                    } size="sm">
                      {transaction.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{transaction.description}</p>
                  {transaction.error && (
                    <p className="text-xs text-red-600 mt-1">{transaction.error}</p>
                  )}
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    €{transaction.amount} {transaction.currency}
                  </p>
                  <p className="text-xs text-gray-500">{transaction.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Quick Actions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <CreditCard className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Create Payment Link</p>
                <p className="text-sm text-gray-500">Generate a payment link</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Receipt className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Send Invoice</p>
                <p className="text-sm text-gray-500">Create and send an invoice</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <FileText className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Export Reports</p>
                <p className="text-sm text-gray-500">Download financial reports</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Shield className="w-5 h-5 text-orange-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Fraud Protection</p>
                <p className="text-sm text-gray-500">Configure Radar settings</p>
              </div>
            </button>
          </div>
        </div>
      </Card>
      {/* Compliance Alert */}
      <Alert variant="info">
        <Shield className="w-4 h-4" />
        <div>
          <p className="font-medium">PCI Compliance</p>
          <p className="text-sm">
            Stripe handles all payment processing securely. Your integration is PCI compliant by default.
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
      webhookEvents={webhookEvents}
      apiEndpoints={apiEndpoints}
    >
      {customOverview}
    </BaseIntegration>
  );
};
export default StripeIntegration;