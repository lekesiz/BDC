import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import {
  Calendar,
  Users,
  Clock,
  Video,
  Plus,
  Settings,
  CheckCircle,
  XCircle
} from 'lucide-react';

const GoogleCalendarIntegration = ({ integration, onBack }) => {
  const [calendars, setCalendars] = useState([
    { id: '1', name: 'Primary Calendar', color: '#4285F4', selected: true, events: 45 },
    { id: '2', name: 'BDC Training Sessions', color: '#34A853', selected: true, events: 23 },
    { id: '3', name: 'Team Meetings', color: '#FBBC04', selected: false, events: 12 },
    { id: '4', name: 'Personal', color: '#EA4335', selected: false, events: 8 }
  ]);

  const configFields = [
    {
      name: 'clientId',
      label: 'Client ID',
      type: 'text',
      placeholder: 'Your Google OAuth Client ID',
      required: true,
      description: 'Get this from Google Cloud Console'
    },
    {
      name: 'clientSecret',
      label: 'Client Secret',
      type: 'password',
      placeholder: 'Your Google OAuth Client Secret',
      required: true,
      description: 'Keep this secure'
    },
    {
      name: 'syncInterval',
      label: 'Sync Interval',
      type: 'select',
      options: [
        { value: '5', label: 'Every 5 minutes' },
        { value: '15', label: 'Every 15 minutes' },
        { value: '30', label: 'Every 30 minutes' },
        { value: '60', label: 'Every hour' }
      ],
      required: true
    },
    {
      name: 'syncDirection',
      label: 'Sync Direction',
      type: 'select',
      options: [
        { value: 'bidirectional', label: 'Bidirectional' },
        { value: 'bdc-to-google', label: 'BDC to Google only' },
        { value: 'google-to-bdc', label: 'Google to BDC only' }
      ],
      required: true
    },
    {
      name: 'autoCreateMeetLinks',
      label: 'Auto-create Google Meet links',
      type: 'checkbox',
      description: 'Automatically add video call links to online events'
    }
  ];

  const oauthConfig = {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID,
    redirectUri: `${window.location.origin}/integrations/google-calendar/callback`,
    scopes: [
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.events',
      'https://www.googleapis.com/auth/userinfo.email'
    ]
  };

  const webhookEvents = [
    'calendar.event.created',
    'calendar.event.updated',
    'calendar.event.deleted',
    'calendar.event.reminder',
    'calendar.sync.completed'
  ];

  const apiEndpoints = [
    {
      method: 'GET',
      path: '/api/integrations/google-calendar/calendars',
      description: 'List all available calendars'
    },
    {
      method: 'GET',
      path: '/api/integrations/google-calendar/events',
      description: 'Retrieve calendar events'
    },
    {
      method: 'POST',
      path: '/api/integrations/google-calendar/events',
      description: 'Create a new calendar event'
    },
    {
      method: 'POST',
      path: '/api/integrations/google-calendar/sync',
      description: 'Trigger manual synchronization'
    }
  ];

  const customOverview = (
    <>
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Events</p>
                <p className="text-2xl font-bold">342</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Synced today: 23</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Calendars</p>
                <p className="text-2xl font-bold">2/4</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Selected for sync</p>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Next Sync</p>
                <p className="text-2xl font-bold">12m</p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Every 15 minutes</p>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Plus className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Create Event</p>
                <p className="text-sm text-gray-500">Add a new event to Google Calendar</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Users className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Import Appointments</p>
                <p className="text-sm text-gray-500">Import from BDC to Google Calendar</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Video className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Setup Meet Links</p>
                <p className="text-sm text-gray-500">Auto-generate video calls for events</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Settings className="w-5 h-5 text-gray-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Configure Sync</p>
                <p className="text-sm text-gray-500">Adjust sync settings and preferences</p>
              </div>
            </button>
          </div>
        </div>
      </Card>

      {/* Calendar Selection */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Available Calendars</h3>
          <div className="space-y-3">
            {calendars.map((calendar) => (
              <div key={calendar.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center">
                  <div 
                    className="w-4 h-4 rounded-full mr-3" 
                    style={{ backgroundColor: calendar.color }}
                  />
                  <div>
                    <p className="font-medium">{calendar.name}</p>
                    <p className="text-sm text-gray-500">{calendar.events} events</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={calendar.selected}
                      onChange={() => {
                        setCalendars(calendars.map(c => 
                          c.id === calendar.id ? { ...c, selected: !c.selected } : c
                        ));
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">Sync enabled</span>
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

      {/* Recent Sync Activity */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Sync Activity</h3>
          <div className="space-y-3">
            {[
              { time: '5 minutes ago', action: 'Imported 12 events from Google Calendar', status: 'success' },
              { time: '20 minutes ago', action: 'Exported 8 appointments to Google Calendar', status: 'success' },
              { time: '35 minutes ago', action: 'Sync failed - API rate limit', status: 'error' },
              { time: '50 minutes ago', action: 'Calendar permissions updated', status: 'info' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-3 ${
                    activity.status === 'success' ? 'bg-green-500' :
                    activity.status === 'error' ? 'bg-red-500' : 'bg-blue-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
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

export default GoogleCalendarIntegration;