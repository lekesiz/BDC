import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Calendar, 
  Link, 
  Settings, 
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Users,
  Clock,
  Video,
  Plus,
  Trash2,
  Edit,
  ExternalLink
} from 'lucide-react';
const GoogleCalendarIntegrationV2Page = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);
  const [calendars, setCalendars] = useState([]);
  const [syncSettings, setSyncSettings] = useState({
    autoSync: true,
    syncInterval: 15,
    syncDirection: 'bidirectional',
    defaultCalendar: '',
    eventTypes: ['appointments', 'meetings', 'training']
  });
  useEffect(() => {
    // Mock data
    const mockCalendars = [
      { id: '1', name: 'Primary Calendar', color: '#4285F4', selected: true },
      { id: '2', name: 'BDC Training Sessions', color: '#34A853', selected: true },
      { id: '3', name: 'Team Meetings', color: '#FBBC04', selected: false },
      { id: '4', name: 'Personal', color: '#EA4335', selected: false }
    ];
    setCalendars(mockCalendars);
    setIsConnected(true);
  }, []);
  const upcomingEvents = [
    { 
      id: 1, 
      title: 'Trainer Meeting with Sarah',
      date: '2024-11-18',
      time: '10:00 AM',
      attendees: 3,
      location: 'Google Meet',
      calendar: 'BDC Training Sessions'
    },
    { 
      id: 2, 
      title: 'Beneficiary Progress Review',
      date: '2024-11-18',
      time: '2:00 PM',
      attendees: 5,
      location: 'Conference Room A',
      calendar: 'Primary Calendar'
    },
    { 
      id: 3, 
      title: 'Python Programming Session',
      date: '2024-11-19',
      time: '9:00 AM',
      attendees: 12,
      location: 'Online',
      calendar: 'BDC Training Sessions'
    }
  ];
  const syncHistory = [
    { id: 1, date: '2024-11-17 3:45 PM', events: 45, status: 'success', direction: 'import' },
    { id: 2, date: '2024-11-17 2:30 PM', events: 23, status: 'success', direction: 'export' },
    { id: 3, date: '2024-11-17 1:15 PM', events: 0, status: 'failed', direction: 'import', error: 'API rate limit' },
    { id: 4, date: '2024-11-17 12:00 PM', events: 67, status: 'success', direction: 'bidirectional' }
  ];
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Calendar },
    { id: 'calendars', label: 'Calendars', icon: Calendar },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'sync', label: 'Sync History', icon: RefreshCw },
    { id: 'events', label: 'Upcoming Events', icon: Clock }
  ];
  const handleConnect = () => {
    setLoading(true);
    // Mock OAuth flow
    setTimeout(() => {
      setIsConnected(true);
      setLoading(false);
    }, 2000);
  };
  const handleDisconnect = () => {
    setIsConnected(false);
  };
  const handleSync = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 3000);
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Google Calendar Integration</h1>
        {isConnected ? (
          <div className="flex space-x-2">
            <Button variant="secondary" onClick={handleSync}>
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Sync Now
            </Button>
            <Button variant="danger" onClick={handleDisconnect}>
              <XCircle className="w-4 h-4 mr-2" />
              Disconnect
            </Button>
          </div>
        ) : (
          <Button variant="primary" onClick={handleConnect}>
            <Link className="w-4 h-4 mr-2" />
            Connect Google Calendar
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
                      {isConnected ? 'Connected to Google Calendar' : 'Not connected'}
                    </p>
                  </div>
                </div>
                {isConnected && (
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Last synced</p>
                    <p className="text-sm font-medium">5 minutes ago</p>
                  </div>
                )}
              </div>
              {isConnected && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Events</p>
                    <p className="text-2xl font-bold text-gray-900">342</p>
                    <p className="text-xs text-gray-500 mt-1">Synced today: 23</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Active Calendars</p>
                    <p className="text-2xl font-bold text-gray-900">2/4</p>
                    <p className="text-xs text-gray-500 mt-1">Selected for sync</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Sync Status</p>
                    <p className="text-2xl font-bold text-green-600">Active</p>
                    <p className="text-xs text-gray-500 mt-1">Every 15 minutes</p>
                  </div>
                </div>
              )}
            </div>
          </Card>
          {!isConnected && (
            <Card>
              <div className="p-8 text-center">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Connect Your Google Calendar</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  Sync your Google Calendar to automatically import and export events, 
                  manage appointments, and keep everything in one place.
                </p>
                <Button variant="primary" size="lg" onClick={handleConnect}>
                  <Link className="w-5 h-5 mr-2" />
                  Connect Google Calendar
                </Button>
                <p className="text-sm text-gray-500 mt-4">
                  We'll request permission to read and write calendar events
                </p>
              </div>
            </Card>
          )}
          {isConnected && (
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
          )}
        </div>
      )}
      {activeTab === 'calendars' && isConnected && (
        <div className="space-y-6">
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
                        <p className="text-sm text-gray-500">Calendar ID: {calendar.id}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={calendar.selected}
                          onChange={() => {}}
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
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Calendar Mapping</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Appointments</p>
                    <p className="text-sm text-gray-500">BDC appointment events</p>
                  </div>
                  <select className="form-select rounded-md border-gray-300">
                    <option>BDC Training Sessions</option>
                    <option>Primary Calendar</option>
                    <option>Team Meetings</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Training Sessions</p>
                    <p className="text-sm text-gray-500">Program training events</p>
                  </div>
                  <select className="form-select rounded-md border-gray-300">
                    <option>BDC Training Sessions</option>
                    <option>Primary Calendar</option>
                    <option>Team Meetings</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Team Meetings</p>
                    <p className="text-sm text-gray-500">Internal team events</p>
                  </div>
                  <select className="form-select rounded-md border-gray-300">
                    <option>Team Meetings</option>
                    <option>Primary Calendar</option>
                    <option>BDC Training Sessions</option>
                  </select>
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
              <h3 className="text-lg font-semibold mb-4">Sync Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={syncSettings.autoSync}
                      onChange={(e) => setSyncSettings({...syncSettings, autoSync: e.target.checked})}
                      className="mr-2"
                    />
                    <span className="font-medium">Enable automatic sync</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically sync events between BDC and Google Calendar
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
                    <option value="5">Every 5 minutes</option>
                    <option value="15">Every 15 minutes</option>
                    <option value="30">Every 30 minutes</option>
                    <option value="60">Every hour</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sync Direction
                  </label>
                  <select 
                    value={syncSettings.syncDirection}
                    onChange={(e) => setSyncSettings({...syncSettings, syncDirection: e.target.value})}
                    className="form-select rounded-md border-gray-300 w-full"
                  >
                    <option value="bidirectional">Bidirectional</option>
                    <option value="bdc-to-google">BDC to Google only</option>
                    <option value="google-to-bdc">Google to BDC only</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Types to Sync
                  </label>
                  <div className="space-y-2">
                    {['appointments', 'meetings', 'training', 'reminders'].map((type) => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={syncSettings.eventTypes.includes(type)}
                          onChange={() => {}}
                          className="mr-2"
                        />
                        <span className="capitalize">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="pt-4">
                  <Button variant="primary">Save Settings</Button>
                </div>
              </div>
            </div>
          </Card>
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Event Defaults</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Event Duration
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>30 minutes</option>
                    <option>45 minutes</option>
                    <option>1 hour</option>
                    <option>90 minutes</option>
                    <option>2 hours</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Reminder
                  </label>
                  <select className="form-select rounded-md border-gray-300 w-full">
                    <option>10 minutes before</option>
                    <option>15 minutes before</option>
                    <option>30 minutes before</option>
                    <option>1 hour before</option>
                    <option>1 day before</option>
                  </select>
                </div>
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="font-medium">Auto-create Google Meet links</span>
                  </label>
                  <p className="text-sm text-gray-500 ml-6">
                    Automatically add video call links to online events
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'sync' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sync History</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date & Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Direction
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Events
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
                          <span className="flex items-center">
                            {sync.direction === 'import' && '← Import'}
                            {sync.direction === 'export' && '→ Export'}
                            {sync.direction === 'bidirectional' && '↔ Both'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {sync.events}
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
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Sync Statistics</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Total Syncs Today</p>
                  <p className="text-2xl font-bold text-gray-900">48</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Events Synced</p>
                  <p className="text-2xl font-bold text-gray-900">892</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-green-600">98.2%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Avg Sync Time</p>
                  <p className="text-2xl font-bold text-gray-900">1.2s</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
      {activeTab === 'events' && isConnected && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Upcoming Events</h3>
              <div className="space-y-3">
                {upcomingEvents.map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-start">
                      <div className="w-1 h-full bg-blue-500 rounded-full mr-4" />
                      <div>
                        <h4 className="font-medium">{event.title}</h4>
                        <p className="text-sm text-gray-500">
                          {event.date} at {event.time}
                        </p>
                        <div className="flex items-center mt-2 space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Users className="w-3 h-3 mr-1" />
                            {event.attendees} attendees
                          </span>
                          <span className="flex items-center">
                            <MapPin className="w-3 h-3 mr-1" />
                            {event.location}
                          </span>
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {event.calendar}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-center">
                <Button variant="secondary">View All Events</Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
export default GoogleCalendarIntegrationV2Page;