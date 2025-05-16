import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Switch } from '../../components/ui/switch';
import { Badge } from '../../components/ui/badge';
import {
  Loader2,
  Mail,
  Clock,
  Settings,
  Save,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const EmailRemindersPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [reminderSettings, setReminderSettings] = useState({
    enabled: false,
    appointment_reminders: true,
    session_reminders: true,
    test_reminders: true,
    custom_time_enabled: false,
    default_reminder_times: [24, 2], // hours before
    email_template_id: 'default',
    include_calendar_attachment: true
  });
  
  const [emailTemplates, setEmailTemplates] = useState([]);
  const [testEmail, setTestEmail] = useState('');
  const [sendingTest, setSendingTest] = useState(false);

  useEffect(() => {
    fetchReminderSettings();
    fetchEmailTemplates();
  }, []);

  const fetchReminderSettings = async () => {
    try {
      const res = await fetch('/api/settings/email-reminders', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch reminder settings');

      const data = await res.json();
      setReminderSettings(data);
    } catch (error) {
      console.error('Error fetching reminder settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch reminder settings',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchEmailTemplates = async () => {
    try {
      const res = await fetch('/api/email-templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch email templates');

      const data = await res.json();
      setEmailTemplates(data);
    } catch (error) {
      console.error('Error fetching email templates:', error);
    }
  };

  const handleSettingChange = (field, value) => {
    setReminderSettings({
      ...reminderSettings,
      [field]: value
    });
  };

  const handleReminderTimeChange = (index, value) => {
    const newTimes = [...reminderSettings.default_reminder_times];
    newTimes[index] = parseInt(value);
    setReminderSettings({
      ...reminderSettings,
      default_reminder_times: newTimes.filter(t => t > 0).sort((a, b) => b - a)
    });
  };

  const addReminderTime = () => {
    setReminderSettings({
      ...reminderSettings,
      default_reminder_times: [...reminderSettings.default_reminder_times, 1]
    });
  };

  const removeReminderTime = (index) => {
    const newTimes = reminderSettings.default_reminder_times.filter((_, i) => i !== index);
    setReminderSettings({
      ...reminderSettings,
      default_reminder_times: newTimes
    });
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/settings/email-reminders', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(reminderSettings)
      });

      if (!res.ok) throw new Error('Failed to save settings');

      toast({
        title: 'Success',
        description: 'Email reminder settings saved successfully'
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save email reminder settings',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const sendTestReminder = async () => {
    if (!testEmail) {
      toast({
        title: 'Error',
        description: 'Please enter an email address',
        variant: 'destructive'
      });
      return;
    }

    setSendingTest(true);
    try {
      const res = await fetch('/api/settings/email-reminders/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ email: testEmail })
      });

      if (!res.ok) throw new Error('Failed to send test email');

      toast({
        title: 'Success',
        description: 'Test reminder email sent successfully'
      });
      setTestEmail('');
    } catch (error) {
      console.error('Error sending test email:', error);
      toast({
        title: 'Error',
        description: 'Failed to send test email',
        variant: 'destructive'
      });
    } finally {
      setSendingTest(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Email Reminders</h1>
      </div>

      {/* Main Settings */}
      <Card className="p-6">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="h-6 w-6 text-primary" />
              <div>
                <h2 className="text-lg font-semibold">Email Reminder Settings</h2>
                <p className="text-sm text-gray-600">
                  Configure automatic email reminders for appointments and sessions
                </p>
              </div>
            </div>
            <Switch
              checked={reminderSettings.enabled}
              onCheckedChange={(checked) => handleSettingChange('enabled', checked)}
            />
          </div>

          {reminderSettings.enabled && (
            <>
              <div className="border-t pt-6 space-y-4">
                <h3 className="font-medium text-gray-900">Event Types</h3>
                
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Appointment Reminders</p>
                    <p className="text-sm text-gray-600">
                      Send reminders for training appointments
                    </p>
                  </div>
                  <Switch
                    checked={reminderSettings.appointment_reminders}
                    onCheckedChange={(checked) => handleSettingChange('appointment_reminders', checked)}
                  />
                </label>

                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Session Reminders</p>
                    <p className="text-sm text-gray-600">
                      Send reminders for program sessions
                    </p>
                  </div>
                  <Switch
                    checked={reminderSettings.session_reminders}
                    onCheckedChange={(checked) => handleSettingChange('session_reminders', checked)}
                  />
                </label>

                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Test Reminders</p>
                    <p className="text-sm text-gray-600">
                      Send reminders for upcoming tests and assessments
                    </p>
                  </div>
                  <Switch
                    checked={reminderSettings.test_reminders}
                    onCheckedChange={(checked) => handleSettingChange('test_reminders', checked)}
                  />
                </label>
              </div>

              <div className="border-t pt-6 space-y-4">
                <h3 className="font-medium text-gray-900">Reminder Times</h3>
                <p className="text-sm text-gray-600">
                  Set when to send reminder emails before each event
                </p>
                
                <div className="space-y-3">
                  {reminderSettings.default_reminder_times.map((time, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <Input
                        type="number"
                        value={time}
                        onChange={(e) => handleReminderTimeChange(index, e.target.value)}
                        min="1"
                        className="w-24"
                      />
                      <span className="text-sm text-gray-600">hours before</span>
                      {reminderSettings.default_reminder_times.length > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeReminderTime(index)}
                        >
                          Remove
                        </Button>
                      )}
                    </div>
                  ))}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={addReminderTime}
                  >
                    Add Reminder Time
                  </Button>
                </div>
              </div>

              <div className="border-t pt-6 space-y-4">
                <h3 className="font-medium text-gray-900">Email Template</h3>
                
                <Select
                  value={reminderSettings.email_template_id}
                  onChange={(e) => handleSettingChange('email_template_id', e.target.value)}
                >
                  <option value="default">Default Template</option>
                  {emailTemplates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </Select>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={reminderSettings.include_calendar_attachment}
                    onChange={(e) => handleSettingChange('include_calendar_attachment', e.target.checked)}
                    className="rounded text-primary"
                  />
                  <div>
                    <p className="font-medium">Include Calendar Attachment</p>
                    <p className="text-sm text-gray-600">
                      Attach .ics file for easy calendar import
                    </p>
                  </div>
                </label>
              </div>
            </>
          )}

          <div className="flex justify-end pt-4">
            <Button 
              onClick={handleSaveSettings}
              disabled={saving}
            >
              {saving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>

      {/* Test Email */}
      <Card className="p-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Send Test Reminder</h3>
          <p className="text-sm text-gray-600">
            Send a test reminder email to verify your settings
          </p>
          
          <div className="flex gap-3">
            <Input
              type="email"
              placeholder="Enter email address"
              value={testEmail}
              onChange={(e) => setTestEmail(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={sendTestReminder}
              disabled={sendingTest || !reminderSettings.enabled}
            >
              {sendingTest ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Send Test
                </>
              )}
            </Button>
          </div>
          
          {!reminderSettings.enabled && (
            <div className="flex items-center gap-2 text-amber-600">
              <AlertCircle className="h-4 w-4" />
              <p className="text-sm">Enable email reminders to send a test</p>
            </div>
          )}
        </div>
      </Card>

      {/* Email Service Status */}
      <Card className="p-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Email Service Status</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Service Provider</span>
              <Badge variant="secondary">SendGrid</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status</span>
              <Badge variant="success">
                <CheckCircle className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Daily Limit</span>
              <span className="text-sm font-medium">1,000 / 10,000</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Today's Sent</span>
              <span className="text-sm font-medium">127</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Info Box */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-gray-900 mb-1">How Email Reminders Work</h3>
            <p className="text-sm text-gray-700">
              When enabled, the system will automatically send email reminders to participants before their scheduled appointments, 
              sessions, or tests. You can customize the timing and content of these reminders.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default EmailRemindersPage;