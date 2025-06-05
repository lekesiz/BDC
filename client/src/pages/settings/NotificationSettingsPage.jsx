import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, 
  Calendar, 
  FileText, 
  MessageSquare, 
  User, 
  Settings, 
  Mail, 
  Smartphone,
  ArrowLeft,
  Save
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
/**
 * NotificationSettingsPage allows users to configure their notification preferences
 */
const NotificationSettingsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState({
    channels: {
      email: true,
      in_app: true,
      push: false,
    },
    categories: {
      appointments: {
        new_appointment: true,
        appointment_reminder: true,
        appointment_update: true,
        appointment_cancellation: true,
      },
      documents: {
        document_shared: true,
        document_updated: true,
        document_commented: true,
      },
      messages: {
        new_message: true,
        message_reply: true,
      },
      users: {
        new_user: false,
        user_update: false,
      },
      system: {
        system_announcement: true,
        maintenance_alert: true,
      },
    },
    preferences: {
      daily_digest: false,
      quiet_hours: {
        enabled: false,
        start: '22:00',
        end: '08:00',
      },
    },
  });
  // Fetch notification settings
  useEffect(() => {
    const fetchNotificationSettings = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/settings/notifications');
        setSettings(response.data);
      } catch (error) {
        console.error('Error fetching notification settings:', error);
        toast({
          title: 'Error',
          description: 'Failed to load notification settings',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchNotificationSettings();
  }, [toast]);
  // Toggle channel setting
  const toggleChannel = (channel) => {
    setSettings(prev => ({
      ...prev,
      channels: {
        ...prev.channels,
        [channel]: !prev.channels[channel],
      },
    }));
  };
  // Toggle category setting
  const toggleCategorySetting = (category, setting) => {
    setSettings(prev => ({
      ...prev,
      categories: {
        ...prev.categories,
        [category]: {
          ...prev.categories[category],
          [setting]: !prev.categories[category][setting],
        },
      },
    }));
  };
  // Toggle all settings in a category
  const toggleAllInCategory = (category, value) => {
    setSettings(prev => {
      const categorySettings = prev.categories[category];
      const updatedCategorySettings = {};
      // Set all settings in the category to the specified value
      Object.keys(categorySettings).forEach(setting => {
        updatedCategorySettings[setting] = value;
      });
      return {
        ...prev,
        categories: {
          ...prev.categories,
          [category]: updatedCategorySettings,
        },
      };
    });
  };
  // Toggle preference setting
  const togglePreference = (preference) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [preference]: typeof prev.preferences[preference] === 'boolean'
          ? !prev.preferences[preference]
          : {
              ...prev.preferences[preference],
              enabled: !prev.preferences[preference].enabled,
            },
      },
    }));
  };
  // Update quiet hours settings
  const updateQuietHours = (field, value) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        quiet_hours: {
          ...prev.preferences.quiet_hours,
          [field]: value,
        },
      },
    }));
  };
  // Save notification settings
  const saveSettings = async () => {
    try {
      setIsSaving(true);
      await api.put('/api/settings/notifications', settings);
      toast({
        title: 'Success',
        description: 'Notification settings saved successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error saving notification settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save notification settings',
        type: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  };
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <button
          className="mr-4 p-2 rounded-full hover:bg-gray-100"
          onClick={() => navigate('/settings')}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold">Notification Settings</h1>
          <p className="text-gray-500">Configure how and when you receive notifications</p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          {/* Notification Channels */}
          <Card className="p-6 mb-6">
            <h2 className="text-lg font-medium mb-4">Notification Channels</h2>
            <p className="text-gray-500 mb-4">
              Choose how you want to receive notifications
            </p>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                    <Mail className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="font-medium">Email Notifications</div>
                    <div className="text-gray-500 text-sm">
                      Receive notifications via email
                    </div>
                  </div>
                </div>
                <div className="relative inline-block w-12 align-middle select-none">
                  <input
                    type="checkbox"
                    id="toggle-email"
                    className="sr-only"
                    checked={settings.channels.email}
                    onChange={() => toggleChannel('email')}
                  />
                  <label
                    htmlFor="toggle-email"
                    className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                      settings.channels.email ? 'bg-primary' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                        settings.channels.email ? 'translate-x-6' : 'translate-x-0.5'
                      } mt-0.5`}
                    ></span>
                  </label>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                    <Bell className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <div className="font-medium">In-App Notifications</div>
                    <div className="text-gray-500 text-sm">
                      Receive notifications within the application
                    </div>
                  </div>
                </div>
                <div className="relative inline-block w-12 align-middle select-none">
                  <input
                    type="checkbox"
                    id="toggle-in-app"
                    className="sr-only"
                    checked={settings.channels.in_app}
                    onChange={() => toggleChannel('in_app')}
                  />
                  <label
                    htmlFor="toggle-in-app"
                    className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                      settings.channels.in_app ? 'bg-primary' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                        settings.channels.in_app ? 'translate-x-6' : 'translate-x-0.5'
                      } mt-0.5`}
                    ></span>
                  </label>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mr-3">
                    <Smartphone className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <div className="font-medium">Push Notifications</div>
                    <div className="text-gray-500 text-sm">
                      Receive push notifications on your mobile device
                    </div>
                  </div>
                </div>
                <div className="relative inline-block w-12 align-middle select-none">
                  <input
                    type="checkbox"
                    id="toggle-push"
                    className="sr-only"
                    checked={settings.channels.push}
                    onChange={() => toggleChannel('push')}
                  />
                  <label
                    htmlFor="toggle-push"
                    className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                      settings.channels.push ? 'bg-primary' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                        settings.channels.push ? 'translate-x-6' : 'translate-x-0.5'
                      } mt-0.5`}
                    ></span>
                  </label>
                </div>
              </div>
            </div>
          </Card>
          {/* Category Settings */}
          <div className="space-y-6">
            {/* Appointments */}
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                    <Calendar className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 className="text-lg font-medium">Appointment Notifications</h2>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    className="text-sm text-primary hover:underline"
                    onClick={() => toggleAllInCategory('appointments', true)}
                  >
                    Enable All
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    className="text-sm text-gray-500 hover:underline"
                    onClick={() => toggleAllInCategory('appointments', false)}
                  >
                    Disable All
                  </button>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">New Appointment</div>
                    <div className="text-gray-500 text-sm">
                      When a new appointment is scheduled
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-new-appointment"
                      className="sr-only"
                      checked={settings.categories.appointments.new_appointment}
                      onChange={() => toggleCategorySetting('appointments', 'new_appointment')}
                    />
                    <label
                      htmlFor="toggle-new-appointment"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.appointments.new_appointment ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.appointments.new_appointment ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Appointment Reminder</div>
                    <div className="text-gray-500 text-sm">
                      Reminders before scheduled appointments
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-appointment-reminder"
                      className="sr-only"
                      checked={settings.categories.appointments.appointment_reminder}
                      onChange={() => toggleCategorySetting('appointments', 'appointment_reminder')}
                    />
                    <label
                      htmlFor="toggle-appointment-reminder"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.appointments.appointment_reminder ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.appointments.appointment_reminder ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Appointment Update</div>
                    <div className="text-gray-500 text-sm">
                      When an appointment is updated or rescheduled
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-appointment-update"
                      className="sr-only"
                      checked={settings.categories.appointments.appointment_update}
                      onChange={() => toggleCategorySetting('appointments', 'appointment_update')}
                    />
                    <label
                      htmlFor="toggle-appointment-update"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.appointments.appointment_update ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.appointments.appointment_update ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Appointment Cancellation</div>
                    <div className="text-gray-500 text-sm">
                      When an appointment is cancelled
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-appointment-cancellation"
                      className="sr-only"
                      checked={settings.categories.appointments.appointment_cancellation}
                      onChange={() => toggleCategorySetting('appointments', 'appointment_cancellation')}
                    />
                    <label
                      htmlFor="toggle-appointment-cancellation"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.appointments.appointment_cancellation ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.appointments.appointment_cancellation ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
              </div>
            </Card>
            {/* Documents */}
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mr-3">
                    <FileText className="w-5 h-5 text-green-600" />
                  </div>
                  <h2 className="text-lg font-medium">Document Notifications</h2>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    className="text-sm text-primary hover:underline"
                    onClick={() => toggleAllInCategory('documents', true)}
                  >
                    Enable All
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    className="text-sm text-gray-500 hover:underline"
                    onClick={() => toggleAllInCategory('documents', false)}
                  >
                    Disable All
                  </button>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Document Shared</div>
                    <div className="text-gray-500 text-sm">
                      When a document is shared with you
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-document-shared"
                      className="sr-only"
                      checked={settings.categories.documents.document_shared}
                      onChange={() => toggleCategorySetting('documents', 'document_shared')}
                    />
                    <label
                      htmlFor="toggle-document-shared"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.documents.document_shared ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.documents.document_shared ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Document Updated</div>
                    <div className="text-gray-500 text-sm">
                      When a shared document is updated
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-document-updated"
                      className="sr-only"
                      checked={settings.categories.documents.document_updated}
                      onChange={() => toggleCategorySetting('documents', 'document_updated')}
                    />
                    <label
                      htmlFor="toggle-document-updated"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.documents.document_updated ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.documents.document_updated ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Document Commented</div>
                    <div className="text-gray-500 text-sm">
                      When someone comments on a document
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-document-commented"
                      className="sr-only"
                      checked={settings.categories.documents.document_commented}
                      onChange={() => toggleCategorySetting('documents', 'document_commented')}
                    />
                    <label
                      htmlFor="toggle-document-commented"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.documents.document_commented ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.documents.document_commented ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
              </div>
            </Card>
            {/* Messages */}
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                    <MessageSquare className="w-5 h-5 text-purple-600" />
                  </div>
                  <h2 className="text-lg font-medium">Message Notifications</h2>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    className="text-sm text-primary hover:underline"
                    onClick={() => toggleAllInCategory('messages', true)}
                  >
                    Enable All
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    className="text-sm text-gray-500 hover:underline"
                    onClick={() => toggleAllInCategory('messages', false)}
                  >
                    Disable All
                  </button>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">New Message</div>
                    <div className="text-gray-500 text-sm">
                      When you receive a new message
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-new-message"
                      className="sr-only"
                      checked={settings.categories.messages.new_message}
                      onChange={() => toggleCategorySetting('messages', 'new_message')}
                    />
                    <label
                      htmlFor="toggle-new-message"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.messages.new_message ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.messages.new_message ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Message Reply</div>
                    <div className="text-gray-500 text-sm">
                      When someone replies to your message
                    </div>
                  </div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-message-reply"
                      className="sr-only"
                      checked={settings.categories.messages.message_reply}
                      onChange={() => toggleCategorySetting('messages', 'message_reply')}
                    />
                    <label
                      htmlFor="toggle-message-reply"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.categories.messages.message_reply ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.categories.messages.message_reply ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
        {/* Preferences Sidebar */}
        <div>
          <Card className="p-6 mb-6">
            <h2 className="text-lg font-medium mb-4">Additional Preferences</h2>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Daily Digest</div>
                  <div className="text-gray-500 text-sm">
                    Receive a daily summary of all notifications
                  </div>
                </div>
                <div className="relative inline-block w-12 align-middle select-none">
                  <input
                    type="checkbox"
                    id="toggle-daily-digest"
                    className="sr-only"
                    checked={settings.preferences.daily_digest}
                    onChange={() => togglePreference('daily_digest')}
                  />
                  <label
                    htmlFor="toggle-daily-digest"
                    className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                      settings.preferences.daily_digest ? 'bg-primary' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                        settings.preferences.daily_digest ? 'translate-x-6' : 'translate-x-0.5'
                      } mt-0.5`}
                    ></span>
                  </label>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium">Quiet Hours</div>
                  <div className="relative inline-block w-12 align-middle select-none">
                    <input
                      type="checkbox"
                      id="toggle-quiet-hours"
                      className="sr-only"
                      checked={settings.preferences.quiet_hours.enabled}
                      onChange={() => togglePreference('quiet_hours')}
                    />
                    <label
                      htmlFor="toggle-quiet-hours"
                      className={`block overflow-hidden h-6 rounded-full cursor-pointer transition-colors ${
                        settings.preferences.quiet_hours.enabled ? 'bg-primary' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`block w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                          settings.preferences.quiet_hours.enabled ? 'translate-x-6' : 'translate-x-0.5'
                        } mt-0.5`}
                      ></span>
                    </label>
                  </div>
                </div>
                <div className="text-gray-500 text-sm mb-3">
                  Don't send notifications during these hours
                </div>
                {settings.preferences.quiet_hours.enabled && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        From
                      </label>
                      <select
                        value={settings.preferences.quiet_hours.start}
                        onChange={(e) => updateQuietHours('start', e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                      >
                        {Array.from({ length: 24 }).map((_, i) => {
                          const hour = i.toString().padStart(2, '0');
                          return (
                            <option key={hour} value={`${hour}:00`}>
                              {`${hour}:00`}
                            </option>
                          );
                        })}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        To
                      </label>
                      <select
                        value={settings.preferences.quiet_hours.end}
                        onChange={(e) => updateQuietHours('end', e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                      >
                        {Array.from({ length: 24 }).map((_, i) => {
                          const hour = i.toString().padStart(2, '0');
                          return (
                            <option key={hour} value={`${hour}:00`}>
                              {`${hour}:00`}
                            </option>
                          );
                        })}
                      </select>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Card>
          <div className="mt-4">
            <Button
              onClick={saveSettings}
              disabled={isSaving}
              className="w-full flex items-center justify-center"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default NotificationSettingsPage;