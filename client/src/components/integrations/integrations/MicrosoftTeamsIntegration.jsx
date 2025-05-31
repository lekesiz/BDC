import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import {
  Users,
  MessageSquare,
  Video,
  Calendar,
  Bell,
  Hash,
  UserPlus,
  Settings,
  Activity
} from 'lucide-react';

const MicrosoftTeamsIntegration = ({ integration, onBack }) => {
  const [teams, setTeams] = useState([
    { id: '1', name: 'BDC Training Team', members: 45, channels: 8, active: true },
    { id: '2', name: 'Program Coordinators', members: 12, channels: 4, active: true },
    { id: '3', name: 'Beneficiary Support', members: 23, channels: 6, active: false }
  ]);

  const [channels, setChannels] = useState([
    { id: '1', name: 'general', team: 'BDC Training Team', notifications: true },
    { id: '2', name: 'announcements', team: 'BDC Training Team', notifications: true },
    { id: '3', name: 'python-programming', team: 'BDC Training Team', notifications: false },
    { id: '4', name: 'web-development', team: 'BDC Training Team', notifications: false }
  ]);

  const configFields = [
    {
      name: 'tenantId',
      label: 'Tenant ID',
      type: 'text',
      placeholder: 'Your Microsoft 365 Tenant ID',
      required: true,
      description: 'Found in Azure Active Directory'
    },
    {
      name: 'clientId',
      label: 'Application (Client) ID',
      type: 'text',
      placeholder: 'Your App Registration Client ID',
      required: true
    },
    {
      name: 'clientSecret',
      label: 'Client Secret',
      type: 'password',
      placeholder: 'Your App Registration Secret',
      required: true,
      description: 'Created in Certificates & secrets'
    },
    {
      name: 'defaultTeam',
      label: 'Default Team',
      type: 'select',
      options: teams.map(team => ({ value: team.id, label: team.name })),
      required: true
    },
    {
      name: 'notificationTypes',
      label: 'Notification Settings',
      type: 'checkbox',
      description: 'Send notifications to Teams channels'
    },
    {
      name: 'autoCreateMeetings',
      label: 'Auto-create Teams meetings',
      type: 'checkbox',
      description: 'Automatically create Teams meetings for appointments'
    }
  ];

  const oauthConfig = {
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    clientId: process.env.REACT_APP_TEAMS_CLIENT_ID,
    redirectUri: `${window.location.origin}/integrations/microsoft-teams/callback`,
    scopes: [
      'User.Read',
      'Team.ReadBasic.All',
      'Channel.ReadWrite.All',
      'Chat.ReadWrite',
      'OnlineMeetings.ReadWrite'
    ]
  };

  const webhookEvents = [
    'teams.message.created',
    'teams.meeting.created',
    'teams.meeting.updated',
    'teams.member.added',
    'teams.member.removed',
    'teams.channel.created'
  ];

  const apiEndpoints = [
    {
      method: 'GET',
      path: '/api/integrations/teams/teams',
      description: 'List all accessible teams'
    },
    {
      method: 'GET',
      path: '/api/integrations/teams/channels',
      description: 'List channels in a team'
    },
    {
      method: 'POST',
      path: '/api/integrations/teams/messages',
      description: 'Send a message to a channel'
    },
    {
      method: 'POST',
      path: '/api/integrations/teams/meetings',
      description: 'Create a Teams meeting'
    }
  ];

  const customOverview = (
    <>
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Teams</p>
                <p className="text-2xl font-bold">3</p>
              </div>
              <Users className="w-8 h-8 text-purple-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">80 total members</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Messages Sent</p>
                <p className="text-2xl font-bold">156</p>
              </div>
              <MessageSquare className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Today: 23</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Meetings Created</p>
                <p className="text-2xl font-bold">48</p>
              </div>
              <Video className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">This week: 12</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Channels</p>
                <p className="text-2xl font-bold">18</p>
              </div>
              <Hash className="w-8 h-8 text-orange-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">With notifications: 6</p>
          </div>
        </Card>
      </div>

      {/* Teams Overview */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Connected Teams</h3>
          <div className="space-y-3">
            {teams.map((team) => (
              <div key={team.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${
                    team.active ? 'bg-purple-100' : 'bg-gray-100'
                  }`}>
                    <Users className={`w-5 h-5 ${team.active ? 'text-purple-600' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <p className="font-medium">{team.name}</p>
                    <p className="text-sm text-gray-500">
                      {team.members} members · {team.channels} channels
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={team.active ? 'success' : 'secondary'}>
                    {team.active ? 'Active' : 'Inactive'}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Channel Configuration */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Channel Notifications</h3>
          <div className="space-y-3">
            {channels.map((channel) => (
              <div key={channel.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <Hash className="w-4 h-4 text-gray-400 mr-3" />
                  <div>
                    <p className="font-medium">{channel.name}</p>
                    <p className="text-sm text-gray-500">{channel.team}</p>
                  </div>
                </div>
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
              <MessageSquare className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Send Announcement</p>
                <p className="text-sm text-gray-500">Post to selected channels</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Video className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Schedule Meeting</p>
                <p className="text-sm text-gray-500">Create a Teams video call</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <UserPlus className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Invite Members</p>
                <p className="text-sm text-gray-500">Add users to teams</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Bell className="w-5 h-5 text-orange-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Configure Alerts</p>
                <p className="text-sm text-gray-500">Set up notification rules</p>
              </div>
            </button>
          </div>
        </div>
      </Card>

      {/* Recent Activity */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {[
              { time: '10 minutes ago', action: 'Meeting created: Python Programming Session', team: 'BDC Training Team', status: 'success' },
              { time: '1 hour ago', action: 'Announcement posted in #general', team: 'Program Coordinators', status: 'success' },
              { time: '2 hours ago', action: 'Failed to send message - permissions error', team: 'Beneficiary Support', status: 'error' },
              { time: '3 hours ago', action: '5 new members added', team: 'BDC Training Team', status: 'info' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <Activity className="w-4 h-4 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.team} · {activity.time}</p>
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

export default MicrosoftTeamsIntegration;