// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Switch } from '../../components/ui/switch';
import { Input } from '../../components/ui/input';
import {
  Loader2,
  Calendar,
  CheckCircle,
  XCircle,
  Settings,
  RefreshCw,
  Link,
  Unlink,
  AlertTriangle } from
'lucide-react';import { useTranslation } from "react-i18next";
const GoogleCalendarIntegrationPage = () => {const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [integration, setIntegration] = useState(null);
  const [syncSettings, setSyncSettings] = useState({
    sync_enabled: false,
    sync_appointments: true,
    sync_sessions: true,
    sync_deadlines: true,
    calendar_id: '',
    webhook_url: ''
  });
  useEffect(() => {
    fetchIntegrationStatus();
  }, []);
  const fetchIntegrationStatus = async () => {
    try {
      const res = await fetch('/api/integrations/google-calendar', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch integration status');
      const data = await res.json();
      setIntegration(data);
      if (data.connected) {
        setSyncSettings(data.settings || syncSettings);
      }
    } catch (error) {
      console.error('Error fetching integration status:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch integration status',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleConnect = async () => {
    try {
      const res = await fetch('/api/integrations/google-calendar/auth-url', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to get auth URL');
      const { auth_url } = await res.json();
      // Redirect to Google OAuth
      window.location.href = auth_url;
    } catch (error) {
      console.error('Error connecting to Google:', error);
      toast({
        title: 'Error',
        description: 'Failed to connect to Google Calendar',
        variant: 'destructive'
      });
    }
  };
  const handleDisconnect = async () => {
    if (!confirm(t("pages.are_you_sure_you_want_to_disconnect_google_calenda"))) {
      return;
    }
    try {
      const res = await fetch('/api/integrations/google-calendar/disconnect', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to disconnect');
      toast({
        title: 'Success',
        description: 'Google Calendar disconnected successfully'
      });
      setIntegration({ connected: false });
      setSyncSettings({
        sync_enabled: false,
        sync_appointments: true,
        sync_sessions: true,
        sync_deadlines: true,
        calendar_id: '',
        webhook_url: ''
      });
    } catch (error) {
      console.error('Error disconnecting:', error);
      toast({
        title: 'Error',
        description: 'Failed to disconnect Google Calendar',
        variant: 'destructive'
      });
    }
  };
  const handleSync = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/integrations/google-calendar/sync', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to sync');
      const { synced_events, errors } = await res.json();
      toast({
        title: 'Sync Complete',
        description: `Synced ${synced_events} events${errors > 0 ? `, ${errors} errors` : ''}`
      });
      fetchIntegrationStatus();
    } catch (error) {
      console.error('Error syncing:', error);
      toast({
        title: 'Error',
        description: 'Failed to sync with Google Calendar',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };
  const handleSettingsChange = (field, value) => {
    setSyncSettings({
      ...syncSettings,
      [field]: value
    });
  };
  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/integrations/google-calendar/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(syncSettings)
      });
      if (!res.ok) throw new Error('Failed to save settings');
      toast({
        title: 'Success',
        description: 'Settings saved successfully'
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save settings',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>);

  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{t("pages.google_calendar_integration")}</h1>
      </div>
      {/* Connection Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Calendar className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="text-lg font-semibold">{t("components.connection_status")}</h2>
              <p className="text-sm text-gray-600">
                {integration?.connected ? 'Connected to Google Calendar' : 'Not connected'}
              </p>
            </div>
          </div>
          {integration?.connected ?
          <div className="flex items-center gap-3">
              <Badge variant="success">
                <CheckCircle className="h-4 w-4 mr-1" />{t("components.connected")}

            </Badge>
              <Button variant="outline" onClick={handleDisconnect}>
                <Unlink className="h-4 w-4 mr-2" />{t("components.disconnect")}

            </Button>
            </div> :

          <Button onClick={handleConnect}>
              <Link className="h-4 w-4 mr-2" />{t("pages.connect_google_calendar")}

          </Button>
          }
        </div>
        {integration?.connected && integration.account_email &&
        <div className="mt-4 p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">{t("pages.connected_as")}
            <span className="font-medium">{integration.account_email}</span>
            </p>
            <p className="text-sm text-gray-600">{t("pages.last_synced")}
            {integration.last_sync ? new Date(integration.last_sync).toLocaleString() : 'Never'}
            </p>
          </div>
        }
      </Card>
      {/* Sync Settings */}
      {integration?.connected &&
      <>
          <Card className="p-6">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">{t("pages.sync_settings")}</h2>
                <Button
                variant="outline"
                size="sm"
                onClick={handleSync}
                disabled={!syncSettings.sync_enabled || saving}>

                  <RefreshCw className={`h-4 w-4 mr-2 ${saving ? 'animate-spin' : ''}`} />{t("components.sync_now")}

              </Button>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{t("pages.enable_sync")}</p>
                    <p className="text-sm text-gray-600">{t("pages.automatically_sync_events_with_google_calendar")}

                  </p>
                  </div>
                  <Switch
                  checked={syncSettings.sync_enabled}
                  onCheckedChange={(checked) => handleSettingsChange('sync_enabled', checked)} />

                </div>
                <div className="border-t pt-4 space-y-3">
                  <h3 className="font-medium text-gray-900">{t("pages.event_types_to_sync")}</h3>
                  <label className="flex items-center gap-3">
                    <input
                    type="checkbox"
                    checked={syncSettings.sync_appointments}
                    onChange={(e) => handleSettingsChange('sync_appointments', e.target.checked)}
                    className="rounded text-primary" />

                    <div>
                      <p className="font-medium">{t("components.appointments")}</p>
                      <p className="text-sm text-gray-600">{t("pages.sync_training_appointments")}</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                    type="checkbox"
                    checked={syncSettings.sync_sessions}
                    onChange={(e) => handleSettingsChange('sync_sessions', e.target.checked)}
                    className="rounded text-primary" />

                    <div>
                      <p className="font-medium">{t("pages.program_sessions")}</p>
                      <p className="text-sm text-gray-600">{t("pages.sync_program_schedule_sessions")}</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                    type="checkbox"
                    checked={syncSettings.sync_deadlines}
                    onChange={(e) => handleSettingsChange('sync_deadlines', e.target.checked)}
                    className="rounded text-primary" />

                    <div>
                      <p className="font-medium">{t("pages.assignment_deadlines")}</p>
                      <p className="text-sm text-gray-600">{t("pages.sync_test_and_assignment_deadlines")}</p>
                    </div>
                  </label>
                </div>
                <div className="border-t pt-4">
                  <label className="block">
                    <p className="font-medium mb-1">{t("pages.calendar_id_optional")}</p>
                    <p className="text-sm text-gray-600 mb-2">{t("pages.leave_empty_to_use_primary_calendar")}

                  </p>
                    <Input
                    type="text"
                    value={syncSettings.calendar_id}
                    onChange={(e) => handleSettingsChange('calendar_id', e.target.value)}
                    placeholder="calendar-id@group.calendar.google.com" />

                  </label>
                </div>
              </div>
              <div className="flex justify-end">
                <Button
                onClick={handleSaveSettings}
                disabled={saving}>

                  {saving ?
                <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </> :

                <>
                      <Settings className="h-4 w-4 mr-2" />{t("pages.save_settings")}

                </>
                }
                </Button>
              </div>
            </div>
          </Card>
          {/* Sync History */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">{t("components.recent_sync_activity")}</h2>
            {integration.sync_history && integration.sync_history.length > 0 ?
          <div className="space-y-3">
                {integration.sync_history.map((entry, index) =>
            <div key={index} className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <p className="text-sm font-medium">{entry.timestamp}</p>
                      <p className="text-sm text-gray-600">
                        {entry.events_synced}{t("pages.events_synced")}
                  {entry.errors > 0 && ` • ${entry.errors} errors`}
                      </p>
                    </div>
                    <Badge variant={entry.errors > 0 ? "destructive" : "success"}>
                      {entry.errors > 0 ? 'With Errors' : 'Success'}
                    </Badge>
                  </div>
            )}
              </div> :

          <p className="text-sm text-gray-500">{t("pages.no_sync_history_available")}</p>
          }
          </Card>
        </>
      }
      {/* Help Section */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="flex gap-3">
          <AlertTriangle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-gray-900 mb-1">{t("pages.how_it_works")}</h3>
            <p className="text-sm text-gray-700">
              When connected, your appointments and program sessions will automatically sync with your Google Calendar. 
              You can control which types of events sync and manually trigger syncs when needed.
            </p>
          </div>
        </div>
      </Card>
    </div>);

};
export default GoogleCalendarIntegrationPage;