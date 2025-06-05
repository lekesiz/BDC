import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import {
  MessageSquare,
  Hash,
  Bell,
  Users,
  AtSign,
  Zap,
  Settings,
  Send,
  AlertCircle
} from 'lucide-react';
const SlackIntegration = ({ integration, onBack }) => {
  const [workspace, setWorkspace] = useState({
    name: 'BDC Academy',
    id: 'T0123456789',
    members: 156,
    channels: 24
  });
  const [channels, setChannels] = useState([
    { id: 'C001', name: 'general', type: 'public', notifications: true, members: 156 },
    { id: 'C002', name: 'announcements', type: 'public', notifications: true, members: 145 },
    { id: 'C003', name: 'training-updates', type: 'public', notifications: true, members: 89 },
    { id: 'C004', name: 'beneficiary-support', type: 'private', notifications: false, members: 23 },
    { id: 'C005', name: 'dev-team', type: 'private', notifications: false, members: 12 }
  ]);
  const [notificationSettings, setNotificationSettings] = useState({
    newEnrollment: true,
    assignmentSubmission: true,
    gradePosted: true,
    appointmentReminder: true,
    programUpdate: true,
    systemAlerts: false
  });
  const configFields = [
    {
      name: 'botToken',
      label: 'Bot User OAuth Token',
      type: 'password',
      placeholder: 'xoxb-your-token',
      required: true,
      description: 'Found in your Slack app settings under OAuth & Permissions'
    },
    {
      name: 'signingSecret',
      label: 'Signing Secret',
      type: 'password',
      placeholder: 'Your signing secret',
      required: true,
      description: 'Used to verify requests from Slack'
    },
    {
      name: 'defaultChannel',
      label: 'Default Channel',
      type: 'select',
      options: channels.map(ch => ({ value: ch.id, label: `#${ch.name}` })),
      required: true
    },
    {
      name: 'mentionUsers',
      label: 'Mention users in notifications',
      type: 'checkbox',
      description: 'Use @mentions for urgent notifications'
    },
    {
      name: 'threadMessages',
      label: 'Use threaded messages',
      type: 'checkbox',
      description: 'Group related messages in threads'
    }
  ];
  const oauthConfig = {
    authUrl: 'https://slack.com/oauth/v2/authorize',
    tokenUrl: 'https://slack.com/api/oauth.v2.access',
    clientId: process.env.REACT_APP_SLACK_CLIENT_ID,
    redirectUri: `${window.location.origin}/integrations/slack/callback`,
    scopes: [
      'channels:read',
      'channels:write',
      'chat:write',
      'users:read',
      'files:write',
      'im:write'
    ]
  };
  const webhookEvents = [
    'message.channels',
    'message.im',
    'app_mention',
    'channel_created',
    'member_joined_channel',
    'reaction_added'
  ];
  const apiEndpoints = [
    {
      method: 'GET',
      path: '/api/integrations/slack/channels',
      description: 'List all channels in workspace'
    },
    {
      method: 'POST',
      path: '/api/integrations/slack/messages',
      description: 'Send a message to a channel'
    },
    {
      method: 'POST',
      path: '/api/integrations/slack/files',
      description: 'Upload a file to Slack'
    },
    {
      method: 'GET',
      path: '/api/integrations/slack/users',
      description: 'List workspace members'
    }
  ];
  const customOverview = (
    <>
      {/* Workspace Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <MessageSquare className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">{workspace.name}</h3>
                <p className="text-sm text-gray-500">Workspace ID: {workspace.id}</p>
              </div>
            </div>
            <Badge variant="success">Connected</Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">{workspace.members}</p>
              <p className="text-sm text-gray-600">Members</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">{workspace.channels}</p>
              <p className="text-sm text-gray-600">Channels</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">892</p>
              <p className="text-sm text-gray-600">Messages Sent</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold">145</p>
              <p className="text-sm text-gray-600">Files Shared</p>
            </div>
          </div>
        </div>
      </Card>
      {/* Channel Management */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Channel Configuration</h3>
          <div className="space-y-3">
            {channels.map((channel) => (
              <div key={channel.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <div className="mr-3">
                    {channel.type === 'public' ? (
                      <Hash className="w-4 h-4 text-gray-400" />
                    ) : (
                      <Lock className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium">{channel.name}</p>
                    <p className="text-sm text-gray-500">
                      {channel.members} members · {channel.type}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={channel.notifications}
                      onChange={() => {
                        setChannels(channels.map(c => 
                          c.id === channel.id ? { ...c, notifications: !c.notifications } : c
                        ));
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">Send notifications</span>
                  </label>
                  <Button variant="ghost" size="sm">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Notification Settings */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Notification Types</h3>
          <div className="space-y-4">
            {Object.entries(notificationSettings).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <div className="flex items-center">
                  <Bell className="w-4 h-4 text-gray-400 mr-3" />
                  <div>
                    <p className="font-medium capitalize">
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </p>
                    <p className="text-sm text-gray-500">
                      {key === 'newEnrollment' && 'Notify when new beneficiaries enroll'}
                      {key === 'assignmentSubmission' && 'Alert on assignment submissions'}
                      {key === 'gradePosted' && 'Notify when grades are posted'}
                      {key === 'appointmentReminder' && 'Send appointment reminders'}
                      {key === 'programUpdate' && 'Program changes and updates'}
                      {key === 'systemAlerts' && 'System maintenance and alerts'}
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={() => {
                      setNotificationSettings({
                        ...notificationSettings,
                        [key]: !value
                      });
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
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
              <Send className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Send Message</p>
                <p className="text-sm text-gray-500">Post to any channel</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <AtSign className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Direct Message</p>
                <p className="text-sm text-gray-500">Message a specific user</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Zap className="w-5 h-5 text-yellow-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Test Integration</p>
                <p className="text-sm text-gray-500">Send a test notification</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Users className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Sync Users</p>
                <p className="text-sm text-gray-500">Update user mappings</p>
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
              { channel: '#announcements', message: 'New Python course starting next week!', time: '5 minutes ago', status: 'sent' },
              { channel: '#training-updates', message: 'Assignment deadline reminder sent', time: '30 minutes ago', status: 'sent' },
              { channel: '@john.doe', message: 'Your grade has been posted', time: '1 hour ago', status: 'sent' },
              { channel: '#general', message: 'Failed to send - rate limit exceeded', time: '2 hours ago', status: 'failed' }
            ].map((msg, index) => (
              <div key={index} className="flex items-start justify-between py-3 border-b">
                <div className="flex items-start">
                  <MessageSquare className="w-4 h-4 text-gray-400 mt-1 mr-3" />
                  <div>
                    <p className="text-sm font-medium">{msg.channel}</p>
                    <p className="text-sm text-gray-600">{msg.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{msg.time}</p>
                  </div>
                </div>
                <Badge variant={msg.status === 'sent' ? 'success' : 'danger'}>
                  {msg.status}
                </Badge>
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
      oauthConfig={oauthConfig}
      webhookEvents={webhookEvents}
      apiEndpoints={apiEndpoints}
    >
      {customOverview}
    </BaseIntegration>
  );
};
// Add missing Lock icon import
import { Lock } from 'lucide-react';
export default SlackIntegration;