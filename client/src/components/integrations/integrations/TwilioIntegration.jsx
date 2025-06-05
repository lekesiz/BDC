import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Alert } from '../../ui/alert';
import {
  MessageSquare,
  Phone,
  Send,
  Users,
  Clock,
  AlertCircle,
  TrendingUp,
  DollarSign,
  Globe,
  Shield,
  Zap,
  BarChart3
} from 'lucide-react';
const TwilioIntegration = ({ integration, onBack }) => {
  const [accountInfo, setAccountInfo] = useState({
    accountSid: 'AC1234567890abcdef',
    phoneNumbers: ['+33123456789', '+33987654321'],
    balance: 245.67,
    messagesThisMonth: 12456,
    callsThisMonth: 234
  });
  const [messagingSettings, setMessagingSettings] = useState({
    enableSMS: true,
    enableWhatsApp: true,
    enableVoice: false,
    defaultSender: '+33123456789',
    quietHoursEnabled: true,
    quietHoursStart: '22:00',
    quietHoursEnd: '08:00',
    urgentBypassQuietHours: true
  });
  const [messageTemplates, setMessageTemplates] = useState([
    { id: '1', name: 'Appointment Reminder', type: 'sms', usage: 1234, lastUsed: '2 hours ago' },
    { id: '2', name: 'Assignment Due', type: 'sms', usage: 567, lastUsed: '1 day ago' },
    { id: '3', name: 'Welcome Message', type: 'whatsapp', usage: 234, lastUsed: '3 days ago' },
    { id: '4', name: 'Course Completion', type: 'sms', usage: 456, lastUsed: '1 week ago' }
  ]);
  const [notificationTypes, setNotificationTypes] = useState({
    appointmentReminders: true,
    assignmentDeadlines: true,
    gradeNotifications: true,
    programUpdates: false,
    emergencyAlerts: true,
    marketingMessages: false
  });
  const configFields = [
    {
      name: 'accountSid',
      label: 'Account SID',
      type: 'text',
      placeholder: 'Your Twilio Account SID',
      required: true,
      description: 'Found in your Twilio Console'
    },
    {
      name: 'authToken',
      label: 'Auth Token',
      type: 'password',
      placeholder: 'Your Twilio Auth Token',
      required: true,
      description: 'Keep this secure'
    },
    {
      name: 'phoneNumber',
      label: 'Default Phone Number',
      type: 'text',
      placeholder: '+33123456789',
      required: true,
      description: 'Your Twilio phone number'
    },
    {
      name: 'messagingServiceSid',
      label: 'Messaging Service SID',
      type: 'text',
      placeholder: 'MG1234567890abcdef (optional)',
      required: false,
      description: 'For advanced messaging features'
    },
    {
      name: 'enableStatusCallbacks',
      label: 'Enable delivery status callbacks',
      type: 'checkbox',
      description: 'Track message delivery status'
    }
  ];
  const webhookEvents = [
    'message.sent',
    'message.delivered',
    'message.failed',
    'message.received',
    'call.initiated',
    'call.completed'
  ];
  const apiEndpoints = [
    {
      method: 'POST',
      path: '/api/integrations/twilio/messages/send',
      description: 'Send an SMS or WhatsApp message'
    },
    {
      method: 'GET',
      path: '/api/integrations/twilio/messages',
      description: 'List sent messages'
    },
    {
      method: 'POST',
      path: '/api/integrations/twilio/messages/bulk',
      description: 'Send bulk messages'
    },
    {
      method: 'GET',
      path: '/api/integrations/twilio/phone-numbers',
      description: 'List available phone numbers'
    }
  ];
  const customOverview = (
    <>
      {/* Account Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4">
                <MessageSquare className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Twilio Account</h3>
                <p className="text-sm text-gray-500">SID: {accountInfo.accountSid}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Balance</p>
              <p className="text-xl font-bold">€{accountInfo.balance}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <MessageSquare className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">{accountInfo.messagesThisMonth.toLocaleString()}</p>
              <p className="text-sm text-gray-600">Messages</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <Phone className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">{accountInfo.callsThisMonth}</p>
              <p className="text-sm text-gray-600">Calls</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <TrendingUp className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">98.5%</p>
              <p className="text-sm text-gray-600">Delivery Rate</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <DollarSign className="w-5 h-5 mx-auto mb-2 text-gray-600" />
              <p className="text-2xl font-bold">€0.045</p>
              <p className="text-sm text-gray-600">Avg Cost</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <p className="text-sm text-gray-600">Phone Numbers:</p>
            {accountInfo.phoneNumbers.map((number) => (
              <Badge key={number} variant="secondary">
                <Phone className="w-3 h-3 mr-1" />
                {number}
              </Badge>
            ))}
          </div>
        </div>
      </Card>
      {/* Messaging Settings */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Messaging Configuration</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <MessageSquare className="w-5 h-5 text-blue-500 mr-2" />
                  <span className="font-medium">SMS</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={messagingSettings.enableSMS}
                    onChange={() => setMessagingSettings({
                      ...messagingSettings,
                      enableSMS: !messagingSettings.enableSMS
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                </label>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <MessageSquare className="w-5 h-5 text-green-500 mr-2" />
                  <span className="font-medium">WhatsApp</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={messagingSettings.enableWhatsApp}
                    onChange={() => setMessagingSettings({
                      ...messagingSettings,
                      enableWhatsApp: !messagingSettings.enableWhatsApp
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                </label>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <Phone className="w-5 h-5 text-purple-500 mr-2" />
                  <span className="font-medium">Voice</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={messagingSettings.enableVoice}
                    onChange={() => setMessagingSettings({
                      ...messagingSettings,
                      enableVoice: !messagingSettings.enableVoice
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                </label>
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-medium">Quiet Hours</p>
                  <p className="text-sm text-gray-500">Prevent non-urgent messages during these hours</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={messagingSettings.quietHoursEnabled}
                    onChange={() => setMessagingSettings({
                      ...messagingSettings,
                      quietHoursEnabled: !messagingSettings.quietHoursEnabled
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                </label>
              </div>
              {messagingSettings.quietHoursEnabled && (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 text-gray-400 mr-2" />
                    <input
                      type="time"
                      value={messagingSettings.quietHoursStart}
                      onChange={(e) => setMessagingSettings({
                        ...messagingSettings,
                        quietHoursStart: e.target.value
                      })}
                      className="form-input rounded-md border-gray-300"
                    />
                  </div>
                  <span className="text-gray-500">to</span>
                  <input
                    type="time"
                    value={messagingSettings.quietHoursEnd}
                    onChange={(e) => setMessagingSettings({
                      ...messagingSettings,
                      quietHoursEnd: e.target.value
                    })}
                    className="form-input rounded-md border-gray-300"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>
      {/* Notification Types */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Notification Types</h3>
          <div className="space-y-3">
            {Object.entries(notificationTypes).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between py-2">
                <div>
                  <p className="font-medium capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </p>
                  <p className="text-sm text-gray-500">
                    {key === 'appointmentReminders' && 'Send reminders for upcoming appointments'}
                    {key === 'assignmentDeadlines' && 'Notify about assignment due dates'}
                    {key === 'gradeNotifications' && 'Alert when grades are posted'}
                    {key === 'programUpdates' && 'Updates about program changes'}
                    {key === 'emergencyAlerts' && 'Critical system notifications'}
                    {key === 'marketingMessages' && 'Promotional messages and offers'}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={() => setNotificationTypes({
                      ...notificationTypes,
                      [key]: !value
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                </label>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Message Templates */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Message Templates</h3>
            <Button variant="primary" size="sm">
              Create Template
            </Button>
          </div>
          <div className="space-y-3">
            {messageTemplates.map((template) => (
              <div key={template.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <MessageSquare className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <p className="font-medium">{template.name}</p>
                    <p className="text-sm text-gray-500">
                      {template.type.toUpperCase()} · Used {template.usage} times · {template.lastUsed}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    Edit
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Send className="w-4 h-4" />
                  </Button>
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
              <Send className="w-5 h-5 text-red-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Send Message</p>
                <p className="text-sm text-gray-500">Send SMS or WhatsApp</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Users className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Bulk Messaging</p>
                <p className="text-sm text-gray-500">Message multiple recipients</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Zap className="w-5 h-5 text-yellow-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Test Message</p>
                <p className="text-sm text-gray-500">Send a test notification</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <BarChart3 className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Usage Report</p>
                <p className="text-sm text-gray-500">View detailed analytics</p>
              </div>
            </button>
          </div>
        </div>
      </Card>
      {/* Recent Messages */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Messages</h3>
          <div className="space-y-3">
            {[
              { to: '+33612345678', message: 'Reminder: Python class tomorrow at 10 AM', status: 'delivered', time: '5 minutes ago', type: 'sms' },
              { to: '+33698765432', message: 'Your assignment has been graded', status: 'delivered', time: '30 minutes ago', type: 'whatsapp' },
              { to: '+33745678901', message: 'Welcome to BDC Academy!', status: 'sent', time: '1 hour ago', type: 'sms' },
              { to: '+33632145698', message: 'Payment reminder', status: 'failed', time: '2 hours ago', type: 'sms', error: 'Invalid number' }
            ].map((msg, index) => (
              <div key={index} className="flex items-start justify-between py-3 border-b">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <p className="text-sm font-medium">{msg.to}</p>
                    <Badge variant="secondary" size="sm">
                      {msg.type}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{msg.message}</p>
                  {msg.error && (
                    <p className="text-xs text-red-600 mt-1">{msg.error}</p>
                  )}
                </div>
                <div className="text-right">
                  <Badge variant={
                    msg.status === 'delivered' ? 'success' :
                    msg.status === 'sent' ? 'warning' : 'danger'
                  } size="sm">
                    {msg.status}
                  </Badge>
                  <p className="text-xs text-gray-500 mt-1">{msg.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
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
export default TwilioIntegration;