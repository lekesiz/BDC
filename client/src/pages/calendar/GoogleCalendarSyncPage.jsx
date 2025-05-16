import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Link, 
  CheckCircle, 
  AlertTriangle, 
  Loader, 
  RefreshCw, 
  Settings, 
  Trash, 
  Lock, 
  Info 
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * GoogleCalendarSyncPage provides controls for Google Calendar synchronization
 */
const GoogleCalendarSyncPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isRefreshingEvents, setIsRefreshingEvents] = useState(false);
  const [activeTab, setActiveTab] = useState('connection');
  const [syncSettings, setSyncSettings] = useState({
    is_connected: false,
    last_synced: null,
    calendars: [],
    selected_calendars: [],
    sync_options: {
      two_way_sync: true,
      sync_past_events: false,
      days_to_sync_in_past: 30,
      days_to_sync_in_future: 90,
      avoid_conflicts: true,
      auto_sync_frequency: 'hourly', // 'manual', 'hourly', 'daily'
    },
    conflict_resolution: {
      strategy: 'prompt', // 'bdc_overrides', 'google_overrides', 'prompt'
      auto_resolve_simple_conflicts: true,
    },
    sync_status: {
      total_events_synced: 0,
      last_sync_errors: [],
      last_sync_success: true,
    }
  });

  // Fetch sync settings
  useEffect(() => {
    const fetchSyncSettings = async () => {
      try {
        setIsLoading(true);
        // In a real app, this would make an API call
        const response = await api.get('/api/calendar/google-sync');
        
        if (response.data) {
          setSyncSettings(response.data);
        }
      } catch (error) {
        console.error('Error fetching Google Calendar sync settings:', error);
        toast({
          title: 'Error',
          description: 'Failed to load Google Calendar sync settings',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSyncSettings();
  }, [toast]);

  // Connect to Google Calendar
  const handleConnectGoogleCalendar = async () => {
    try {
      setIsConnecting(true);
      
      // In a real app, this would initiate the OAuth flow
      // For now, simulate a successful connection
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock successful connection with sample calendars
      setSyncSettings(prev => ({
        ...prev,
        is_connected: true,
        last_synced: new Date().toISOString(),
        calendars: [
          { id: 'primary', name: 'Primary Calendar', color: '#039BE5' },
          { id: 'work', name: 'Work Calendar', color: '#33B679' },
          { id: 'personal', name: 'Personal Calendar', color: '#8E24AA' },
        ],
        selected_calendars: ['primary'],
      }));
      
      toast({
        title: 'Success',
        description: 'Connected to Google Calendar successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error connecting to Google Calendar:', error);
      toast({
        title: 'Error',
        description: 'Failed to connect to Google Calendar',
        type: 'error',
      });
    } finally {
      setIsConnecting(false);
    }
  };

  // Disconnect from Google Calendar
  const handleDisconnectGoogleCalendar = async () => {
    try {
      setIsConnecting(true);
      
      // In a real app, this would revoke access
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSyncSettings(prev => ({
        ...prev,
        is_connected: false,
        calendars: [],
        selected_calendars: [],
      }));
      
      toast({
        title: 'Success',
        description: 'Disconnected from Google Calendar',
        type: 'success',
      });
    } catch (error) {
      console.error('Error disconnecting from Google Calendar:', error);
      toast({
        title: 'Error',
        description: 'Failed to disconnect from Google Calendar',
        type: 'error',
      });
    } finally {
      setIsConnecting(false);
    }
  };

  // Toggle calendar selection
  const handleCalendarToggle = (calendarId) => {
    setSyncSettings(prev => {
      const isSelected = prev.selected_calendars.includes(calendarId);
      
      return {
        ...prev,
        selected_calendars: isSelected
          ? prev.selected_calendars.filter(id => id !== calendarId)
          : [...prev.selected_calendars, calendarId],
      };
    });
  };

  // Handle sync option changes
  const handleSyncOptionChange = (option, value) => {
    setSyncSettings(prev => ({
      ...prev,
      sync_options: {
        ...prev.sync_options,
        [option]: value,
      },
    }));
  };

  // Handle conflict resolution changes
  const handleConflictResolutionChange = (option, value) => {
    setSyncSettings(prev => ({
      ...prev,
      conflict_resolution: {
        ...prev.conflict_resolution,
        [option]: value,
      },
    }));
  };

  // Save sync settings
  const handleSaveSettings = async () => {
    try {
      setIsSaving(true);
      
      // In a real app, this would make an API call
      await api.put('/api/calendar/google-sync', syncSettings);
      
      toast({
        title: 'Success',
        description: 'Google Calendar sync settings saved successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error saving Google Calendar sync settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save Google Calendar sync settings',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Manually trigger sync
  const handleManualSync = async () => {
    try {
      setIsRefreshingEvents(true);
      
      // In a real app, this would trigger a sync
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update last synced time
      setSyncSettings(prev => ({
        ...prev,
        last_synced: new Date().toISOString(),
        sync_status: {
          ...prev.sync_status,
          total_events_synced: prev.sync_status.total_events_synced + 5,
          last_sync_errors: [],
          last_sync_success: true,
        }
      }));
      
      toast({
        title: 'Success',
        description: 'Calendar events synced successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error syncing calendar events:', error);
      toast({
        title: 'Error',
        description: 'Failed to sync calendar events',
        type: 'error',
      });
      
      // Update sync status with error
      setSyncSettings(prev => ({
        ...prev,
        sync_status: {
          ...prev.sync_status,
          last_sync_errors: ['Network error while syncing events'],
          last_sync_success: false,
        }
      }));
    } finally {
      setIsRefreshingEvents(false);
    }
  };

  // Navigate to availability settings
  const handleNavigateToAvailability = () => {
    navigate('/calendar/availability');
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Google Calendar Synchronization</h1>
        
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={handleNavigateToAvailability}
            className="flex items-center"
          >
            <Settings className="w-4 h-4 mr-2" />
            Availability Settings
          </Button>
          
          <Button
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="flex items-center"
          >
            {isSaving ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4 mr-2" />
                Save Settings
              </>
            )}
          </Button>
        </div>
      </div>
      
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList>
          <Tabs.TabTrigger value="connection">
            <Link className="w-4 h-4 mr-2" />
            Connection
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="calendars" disabled={!syncSettings.is_connected}>
            <Calendar className="w-4 h-4 mr-2" />
            Calendars
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="sync-options" disabled={!syncSettings.is_connected}>
            <Settings className="w-4 h-4 mr-2" />
            Sync Options
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="conflicts" disabled={!syncSettings.is_connected}>
            <AlertTriangle className="w-4 h-4 mr-2" />
            Conflict Resolution
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        
        {/* Connection Tab */}
        <Tabs.TabContent value="connection">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Google Calendar Connection</h2>
              
              {syncSettings.is_connected ? (
                <div className="space-y-6">
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <h3 className="text-sm font-medium text-green-800">Connected to Google Calendar</h3>
                    </div>
                    <p className="mt-2 text-sm text-green-700">
                      Your BDC account is connected to Google Calendar. You can manage which calendars to sync and sync settings.
                    </p>
                    <div className="mt-2 text-sm text-green-700">
                      {syncSettings.last_synced && (
                        <div className="flex items-center mt-1">
                          <RefreshCw className="h-4 w-4 mr-1" />
                          <span>
                            Last synced: {new Date(syncSettings.last_synced).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <Button
                      variant="outline" 
                      onClick={handleManualSync}
                      disabled={isRefreshingEvents}
                      className="w-full flex items-center justify-center"
                    >
                      {isRefreshingEvents ? (
                        <>
                          <Loader className="w-4 h-4 mr-2 animate-spin" />
                          Syncing...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Sync Now
                        </>
                      )}
                    </Button>
                    
                    <Button
                      variant="destructive" 
                      onClick={handleDisconnectGoogleCalendar}
                      disabled={isConnecting}
                      className="w-full flex items-center justify-center"
                    >
                      {isConnecting ? (
                        <>
                          <Loader className="w-4 h-4 mr-2 animate-spin" />
                          Disconnecting...
                        </>
                      ) : (
                        <>
                          <Trash className="w-4 h-4 mr-2" />
                          Disconnect from Google Calendar
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="flex">
                      <Info className="h-5 w-5 text-blue-500 mr-2" />
                      <h3 className="text-sm font-medium text-blue-800">Connect to Google Calendar</h3>
                    </div>
                    <p className="mt-2 text-sm text-blue-700">
                      Connecting to Google Calendar allows you to sync your BDC appointments with your Google Calendar, and vice versa.
                    </p>
                  </div>
                  
                  <Button
                    onClick={handleConnectGoogleCalendar}
                    disabled={isConnecting}
                    className="w-full flex items-center justify-center"
                  >
                    {isConnecting ? (
                      <>
                        <Loader className="w-4 h-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Calendar className="w-4 h-4 mr-2" />
                        Connect to Google Calendar
                      </>
                    )}
                  </Button>
                </div>
              )}
            </Card>
            
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Benefits of Google Calendar Sync</h2>
              
              <ul className="space-y-4">
                <li className="flex">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">
                    <span className="font-medium">Avoid Double Bookings:</span> Automatically block times in BDC when you have Google Calendar events.
                  </span>
                </li>
                <li className="flex">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">
                    <span className="font-medium">See All Appointments:</span> View BDC appointments directly in your Google Calendar.
                  </span>
                </li>
                <li className="flex">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">
                    <span className="font-medium">Two-Way Sync:</span> Changes made in either system are reflected in both.
                  </span>
                </li>
                <li className="flex">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">
                    <span className="font-medium">Auto-Sync:</span> Set automatic sync frequency based on your needs.
                  </span>
                </li>
                <li className="flex">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">
                    <span className="font-medium">Conflict Handling:</span> Define how to handle conflicting appointments.
                  </span>
                </li>
              </ul>
              
              <div className="mt-6 flex items-center bg-gray-50 p-4 rounded-lg">
                <Lock className="w-5 h-5 text-gray-500 mr-2 flex-shrink-0" />
                <p className="text-sm text-gray-600">
                  BDC only requests calendar access necessary for syncing appointments. We never read the content of your events or share your calendar data with third parties.
                </p>
              </div>
            </Card>
          </div>
          
          {syncSettings.is_connected && syncSettings.sync_status.last_sync_errors.length > 0 && (
            <Card className="p-6 mt-6 border-orange-300">
              <h2 className="text-lg font-medium mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 text-orange-500 mr-2" />
                Sync Issues
              </h2>
              
              <ul className="space-y-2 text-sm">
                {syncSettings.sync_status.last_sync_errors.map((error, index) => (
                  <li key={index} className="flex items-start">
                    <div className="h-5 w-5 text-orange-500 mr-2">•</div>
                    <span>{error}</span>
                  </li>
                ))}
              </ul>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualSync}
                className="mt-4 flex items-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry Sync
              </Button>
            </Card>
          )}
        </Tabs.TabContent>
        
        {/* Calendars Tab */}
        <Tabs.TabContent value="calendars">
          {syncSettings.is_connected && (
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Select Calendars to Sync</h2>
              <p className="text-gray-600 mb-4">
                Choose which Google Calendars you want to sync with BDC. Appointments from selected calendars will be considered when checking your availability.
              </p>
              
              <div className="space-y-4 mt-6">
                {syncSettings.calendars.map(calendar => (
                  <div 
                    key={calendar.id} 
                    className={`p-4 rounded-lg border ${
                      syncSettings.selected_calendars.includes(calendar.id)
                        ? 'border-primary bg-primary-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div 
                          className="w-4 h-4 rounded-full mr-3" 
                          style={{ backgroundColor: calendar.color }}
                        ></div>
                        <span className="font-medium">{calendar.name}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <button
                          type="button"
                          className={`relative inline-flex h-6 w-11 items-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                            syncSettings.selected_calendars.includes(calendar.id)
                              ? 'bg-primary'
                              : 'bg-gray-200'
                          }`}
                          onClick={() => handleCalendarToggle(calendar.id)}
                        >
                          <span
                            className={`${
                              syncSettings.selected_calendars.includes(calendar.id)
                                ? 'translate-x-6'
                                : 'translate-x-1'
                            } inline-block h-4 w-4 transform rounded-full bg-white transition`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {syncSettings.calendars.length === 0 && (
                <div className="bg-gray-50 p-6 rounded-lg text-center">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <h3 className="text-lg font-medium text-gray-900 mb-1">No Calendars Found</h3>
                  <p className="text-gray-500 mb-4">
                    We couldn't find any calendars in your Google account.
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleConnectGoogleCalendar}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh Calendars
                  </Button>
                </div>
              )}
            </Card>
          )}
        </Tabs.TabContent>
        
        {/* Sync Options Tab */}
        <Tabs.TabContent value="sync-options">
          {syncSettings.is_connected && (
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Sync Options</h2>
              <p className="text-gray-600 mb-6">
                Customize how your calendars sync between BDC and Google Calendar.
              </p>
              
              <div className="space-y-6">
                <div className="flex items-start justify-between">
                  <div>
                    <label htmlFor="two_way_sync" className="block text-sm font-medium text-gray-700 mb-1">
                      Two-Way Sync
                    </label>
                    <p className="text-xs text-gray-500">
                      When enabled, changes made in either BDC or Google Calendar will sync to the other.
                      When disabled, only Google Calendar events will sync to BDC.
                    </p>
                  </div>
                  <div className="ml-4">
                    <button
                      id="two_way_sync"
                      type="button"
                      className={`relative inline-flex h-6 w-11 items-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                        syncSettings.sync_options.two_way_sync
                          ? 'bg-primary'
                          : 'bg-gray-200'
                      }`}
                      onClick={() => handleSyncOptionChange('two_way_sync', !syncSettings.sync_options.two_way_sync)}
                    >
                      <span
                        className={`${
                          syncSettings.sync_options.two_way_sync
                            ? 'translate-x-6'
                            : 'translate-x-1'
                        } inline-block h-4 w-4 transform rounded-full bg-white transition`}
                      />
                    </button>
                  </div>
                </div>
                
                <div className="flex items-start justify-between">
                  <div>
                    <label htmlFor="avoid_conflicts" className="block text-sm font-medium text-gray-700 mb-1">
                      Avoid Double Bookings
                    </label>
                    <p className="text-xs text-gray-500">
                      When enabled, BDC will check for conflicts with Google Calendar events before allowing appointments.
                    </p>
                  </div>
                  <div className="ml-4">
                    <button
                      id="avoid_conflicts"
                      type="button"
                      className={`relative inline-flex h-6 w-11 items-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                        syncSettings.sync_options.avoid_conflicts
                          ? 'bg-primary'
                          : 'bg-gray-200'
                      }`}
                      onClick={() => handleSyncOptionChange('avoid_conflicts', !syncSettings.sync_options.avoid_conflicts)}
                    >
                      <span
                        className={`${
                          syncSettings.sync_options.avoid_conflicts
                            ? 'translate-x-6'
                            : 'translate-x-1'
                        } inline-block h-4 w-4 transform rounded-full bg-white transition`}
                      />
                    </button>
                  </div>
                </div>
                
                <div className="flex items-start justify-between">
                  <div>
                    <label htmlFor="sync_past_events" className="block text-sm font-medium text-gray-700 mb-1">
                      Sync Past Events
                    </label>
                    <p className="text-xs text-gray-500">
                      When enabled, past events will also be synced between calendars.
                    </p>
                  </div>
                  <div className="ml-4">
                    <button
                      id="sync_past_events"
                      type="button"
                      className={`relative inline-flex h-6 w-11 items-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                        syncSettings.sync_options.sync_past_events
                          ? 'bg-primary'
                          : 'bg-gray-200'
                      }`}
                      onClick={() => handleSyncOptionChange('sync_past_events', !syncSettings.sync_options.sync_past_events)}
                    >
                      <span
                        className={`${
                          syncSettings.sync_options.sync_past_events
                            ? 'translate-x-6'
                            : 'translate-x-1'
                        } inline-block h-4 w-4 transform rounded-full bg-white transition`}
                      />
                    </button>
                  </div>
                </div>
                
                {syncSettings.sync_options.sync_past_events && (
                  <div>
                    <label htmlFor="days_to_sync_in_past" className="block text-sm font-medium text-gray-700 mb-1">
                      Days to Sync in Past
                    </label>
                    <select
                      id="days_to_sync_in_past"
                      value={syncSettings.sync_options.days_to_sync_in_past}
                      onChange={(e) => handleSyncOptionChange('days_to_sync_in_past', parseInt(e.target.value))}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      <option value={7}>7 days</option>
                      <option value={14}>14 days</option>
                      <option value={30}>30 days</option>
                      <option value={60}>60 days</option>
                      <option value={90}>90 days</option>
                    </select>
                  </div>
                )}
                
                <div>
                  <label htmlFor="days_to_sync_in_future" className="block text-sm font-medium text-gray-700 mb-1">
                    Days to Sync in Future
                  </label>
                  <select
                    id="days_to_sync_in_future"
                    value={syncSettings.sync_options.days_to_sync_in_future}
                    onChange={(e) => handleSyncOptionChange('days_to_sync_in_future', parseInt(e.target.value))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value={30}>30 days</option>
                    <option value={60}>60 days</option>
                    <option value={90}>90 days</option>
                    <option value={180}>180 days</option>
                    <option value={365}>365 days</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="auto_sync_frequency" className="block text-sm font-medium text-gray-700 mb-1">
                    Auto-Sync Frequency
                  </label>
                  <select
                    id="auto_sync_frequency"
                    value={syncSettings.sync_options.auto_sync_frequency}
                    onChange={(e) => handleSyncOptionChange('auto_sync_frequency', e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value="manual">Manual only</option>
                    <option value="hourly">Every hour</option>
                    <option value="daily">Once a day</option>
                  </select>
                </div>
              </div>
            </Card>
          )}
        </Tabs.TabContent>
        
        {/* Conflict Resolution Tab */}
        <Tabs.TabContent value="conflicts">
          {syncSettings.is_connected && (
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Conflict Resolution</h2>
              <p className="text-gray-600 mb-6">
                Configure how to handle conflicting appointments between BDC and Google Calendar.
              </p>
              
              <div className="space-y-6">
                <div>
                  <label htmlFor="conflict_strategy" className="block text-sm font-medium text-gray-700 mb-1">
                    Conflict Resolution Strategy
                  </label>
                  <select
                    id="conflict_strategy"
                    value={syncSettings.conflict_resolution.strategy}
                    onChange={(e) => handleConflictResolutionChange('strategy', e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                  >
                    <option value="prompt">Prompt me to resolve conflicts</option>
                    <option value="bdc_overrides">BDC appointments take priority</option>
                    <option value="google_overrides">Google Calendar events take priority</option>
                  </select>
                </div>
                
                <div className="flex items-start justify-between">
                  <div>
                    <label htmlFor="auto_resolve_simple_conflicts" className="block text-sm font-medium text-gray-700 mb-1">
                      Auto-Resolve Simple Conflicts
                    </label>
                    <p className="text-xs text-gray-500">
                      When enabled, simple conflicts (like identical events with different titles) will be automatically resolved using your strategy.
                    </p>
                  </div>
                  <div className="ml-4">
                    <button
                      id="auto_resolve_simple_conflicts"
                      type="button"
                      className={`relative inline-flex h-6 w-11 items-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                        syncSettings.conflict_resolution.auto_resolve_simple_conflicts
                          ? 'bg-primary'
                          : 'bg-gray-200'
                      }`}
                      onClick={() => handleConflictResolutionChange('auto_resolve_simple_conflicts', !syncSettings.conflict_resolution.auto_resolve_simple_conflicts)}
                    >
                      <span
                        className={`${
                          syncSettings.conflict_resolution.auto_resolve_simple_conflicts
                            ? 'translate-x-6'
                            : 'translate-x-1'
                        } inline-block h-4 w-4 transform rounded-full bg-white transition`}
                      />
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 bg-blue-50 p-4 rounded-lg">
                <div className="flex">
                  <Info className="h-5 w-5 text-blue-500 mr-2" />
                  <h3 className="text-sm font-medium text-blue-800">What is a conflict?</h3>
                </div>
                <p className="mt-2 text-sm text-blue-700">
                  A conflict occurs when appointments in BDC overlap with events in Google Calendar, or when an event is updated in both systems with different information.
                </p>
              </div>
              
              <div className="mt-6">
                <h3 className="text-md font-medium mb-2">Example conflict scenarios:</h3>
                <ul className="space-y-2 text-sm text-gray-700 list-disc pl-6">
                  <li>You have a Google Calendar event at 10:00-11:00 AM, and someone tries to book a BDC appointment at the same time</li>
                  <li>You modify an appointment's time in BDC, but someone also modifies the same event's time in Google Calendar</li>
                  <li>You delete an event in Google Calendar that still exists in BDC</li>
                </ul>
              </div>
            </Card>
          )}
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};

export default GoogleCalendarSyncPage;