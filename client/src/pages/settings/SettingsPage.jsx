import React, { useState, useEffect } from 'react';
import { Bell, Shield, Globe, Moon, Sun, Monitor, Brain, Lock } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { AnimatedButton, AnimatedCard, AnimatedPage } from '@/components/animations';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Alert } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import api from '@/lib/api';
import AISettingsContent from './AISettingsContent';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
/**
 * Settings page component
 */
const SettingsPage = () => {
  const { user, refreshToken } = useAuth();
  const { addToast } = useToast();
  const { t, i18n } = useTranslation();
  // State management
  const [activeTab, setActiveTab] = useState('notifications');
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState('system');
  const [language, setLanguage] = useState(i18n.language || 'en');
  // Notification settings state
  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: true,
    push_notifications: true,
    sms_notifications: false,
    marketing_emails: false,
    session_reminders: true,
    new_messages: true,
    system_updates: true,
    evaluation_results: true,
  });
  // Privacy settings state
  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: 'all',
    show_online_status: true,
    share_activity: true,
    allow_data_collection: true,
  });
  // Handle notification toggle
  const handleNotificationToggle = (key) => {
    setNotificationSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };
  // Access control based on user roles
  const canAccessPrivacySettings = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'trainer';
  const canAccessAISettings = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'trainer';
  const canAccessIntegrations = user?.role === 'super_admin' || user?.role === 'admin';
  // Handle privacy setting change
  const handlePrivacyChange = (key, value) => {
    setPrivacySettings(prev => ({
      ...prev,
      [key]: value
    }));
  };
  // Fetch notification settings on mount
  useEffect(() => {
    const fetchNotificationSettings = async () => {
      try {
        const response = await api.get('/api/settings/notifications');
        setNotificationSettings(prev => ({
          ...prev,
          ...response.data
        }));
      } catch (err) {
        console.error('Failed to fetch notification settings:', err);
      }
    };
    fetchNotificationSettings();
  }, []);
  // Fetch privacy settings on mount
  useEffect(() => {
    const fetchPrivacySettings = async () => {
      try {
        const response = await api.get('/api/settings/privacy');
        setPrivacySettings(prev => ({
          ...prev,
          ...response.data
        }));
      } catch (err) {
        console.error('Failed to fetch privacy settings:', err);
      }
    };
    fetchPrivacySettings();
  }, []);
  // Handle theme change
  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    // In a real app, this would update the theme in the DOM
    // and possibly store the preference
    document.documentElement.classList.remove('light', 'dark');
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (newTheme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      // For 'system' theme, check system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.add('light');
      }
    }
  };
  // Handle language change
  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    i18n.changeLanguage(newLanguage);
    localStorage.setItem('language', newLanguage);
  };
  // Handle notification settings save
  const handleSaveNotifications = async () => {
    try {
      setIsLoading(true);
      // Call API to save notification settings
      await api.put('/api/settings/notifications', notificationSettings);
      addToast({
        type: 'success',
        title: t('settings.page.messages.settingsSaved'),
        message: t('settings.page.messages.updateSuccess', { type: 'notification' }),
      });
    } catch (err) {
      console.error('Failed to save notification settings:', err);
      addToast({
        type: 'error',
        title: t('common.error'),
        message: err.response?.data?.message || t('settings.page.messages.updateFailed'),
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle privacy settings save
  const handleSavePrivacy = async () => {
    try {
      setIsLoading(true);
      // Call API to save privacy settings
      await api.put('/api/settings/privacy', privacySettings);
      addToast({
        type: 'success',
        title: t('settings.page.messages.settingsSaved'),
        message: t('settings.page.messages.updateSuccess', { type: 'privacy' }),
      });
    } catch (err) {
      console.error('Failed to save privacy settings:', err);
      addToast({
        type: 'error',
        title: t('common.error'),
        message: err.response?.data?.message || t('settings.page.messages.updateFailed'),
      });
    } finally {
      setIsLoading(false);
    }
  };
  // Handle preferences save
  const handleSavePreferences = async () => {
    try {
      setIsLoading(true);
      // Call API to save preferences
      await api.put('/api/users/settings/preferences', {
        theme,
        language,
      });
      addToast({
        type: 'success',
        title: t('settings.page.messages.settingsSaved'),
        message: t('settings.page.messages.updateSuccess', { type: 'preferences' }),
      });
    } catch (err) {
      console.error('Failed to save preferences:', err);
      addToast({
        type: 'error',
        title: t('common.error'),
        message: err.response?.data?.message || t('settings.page.messages.updateFailed'),
      });
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <AnimatedPage className="container mx-auto py-8 px-4">
      <motion.h1 
        className="text-2xl font-bold mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {t('settings.page.title')}
      </motion.h1>
      <AnimatedCard>
        <CardHeader>
          <CardTitle>{t('settings.page.accountSettings')}</CardTitle>
          <CardDescription>
            {t('settings.page.accountSettingsDescription')}
          </CardDescription>
        </CardHeader>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <CardContent className="pb-0">
            <TabsList className="mb-6">
              <TabTrigger value="notifications">
                <Bell className="h-4 w-4 mr-2" />
                {t('settings.page.tabs.notifications')}
              </TabTrigger>
              <TabTrigger value="privacy">
                <Shield className="h-4 w-4 mr-2" />
                {t('settings.page.tabs.privacy')}
              </TabTrigger>
              <TabTrigger value="preferences">
                <Globe className="h-4 w-4 mr-2" />
                {t('settings.page.tabs.preferences')}
              </TabTrigger>
              <TabTrigger value="ai">
                <Brain className="h-4 w-4 mr-2" />
                {t('settings.page.tabs.ai')}
              </TabTrigger>
              <TabTrigger value="integrations">
                <Globe className="h-4 w-4 mr-2" />
                {t('settings.page.tabs.integrations')}
              </TabTrigger>
            </TabsList>
          </CardContent>
          {/* Notifications Tab */}
          <TabContent value="notifications">
            <CardContent>
              <motion.div 
                className="space-y-6"
                variants={staggerContainer}
                initial="initial"
                animate="animate"
              >
                <motion.div 
                  className="space-y-4"
                  variants={staggerItem}
                >
                  <h3 className="text-lg font-medium">{t('settings.page.notifications.email.title')}</h3>
                  <div className="space-y-3">
                  {/* Email Notifications toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.email.title')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.email.description')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.email_notifications}
                        onChange={() => handleNotificationToggle('email_notifications')}
                      />
                    </div>
                  </div>
                  {/* Marketing Emails toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.email.marketing')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.email.marketingDescription')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.marketing_emails}
                        onChange={() => handleNotificationToggle('marketing_emails')}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
              </motion.div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.notifications.push.title')}</h3>
                <div className="space-y-3">
                  {/* Push Notifications toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.push.title')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.push.description')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.push_notifications}
                        onChange={() => handleNotificationToggle('push_notifications')}
                      />
                    </div>
                  </div>
                  {/* New Messages toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.push.newMessages')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.push.newMessagesDescription')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.new_messages}
                        onChange={() => handleNotificationToggle('new_messages')}
                      />
                    </div>
                  </div>
                  {/* Session Reminders toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.push.sessionReminders')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.push.sessionRemindersDescription')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.session_reminders}
                        onChange={() => handleNotificationToggle('session_reminders')}
                      />
                    </div>
                  </div>
                  {/* Evaluation Results toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.push.evaluationResults')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.push.evaluationResultsDescription')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.evaluation_results}
                        onChange={() => handleNotificationToggle('evaluation_results')}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.notifications.sms.title')}</h3>
                <div className="space-y-3">
                  {/* SMS Notifications toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.notifications.sms.title')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.notifications.sms.description')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={notificationSettings.sms_notifications}
                        onChange={() => handleNotificationToggle('sms_notifications')}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="border-t pt-6">
              <Button
                onClick={handleSaveNotifications}
                isLoading={isLoading}
                disabled={isLoading}
                className="ml-auto"
              >
                {t('settings.page.notifications.saveButton')}
              </Button>
            </CardFooter>
          </TabContent>
          {/* Privacy Tab */}
          {canAccessPrivacySettings ? (
            <TabContent value="privacy">
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.privacy.title')}</h3>
                <div className="space-y-3">
                  {/* Profile Visibility */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">{t('settings.page.privacy.profileVisibility.title')}</h4>
                    <p className="text-sm text-muted-foreground">{t('settings.page.privacy.profileVisibility.description')}</p>
                    <div className="flex flex-col space-y-1 mt-2">
                      <div className="flex items-center">
                        <input 
                          type="radio" 
                          id="visibility-all" 
                          name="profile_visibility"
                          className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
                          checked={privacySettings.profile_visibility === 'all'}
                          onChange={() => handlePrivacyChange('profile_visibility', 'all')}
                        />
                        <label htmlFor="visibility-all" className="ml-2 text-sm text-gray-700">
                          {t('settings.page.privacy.profileVisibility.everyone')}
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input 
                          type="radio" 
                          id="visibility-connections" 
                          name="profile_visibility"
                          className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
                          checked={privacySettings.profile_visibility === 'connections'}
                          onChange={() => handlePrivacyChange('profile_visibility', 'connections')}
                        />
                        <label htmlFor="visibility-connections" className="ml-2 text-sm text-gray-700">
                          {t('settings.page.privacy.profileVisibility.connections')}
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input 
                          type="radio" 
                          id="visibility-none" 
                          name="profile_visibility"
                          className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
                          checked={privacySettings.profile_visibility === 'none'}
                          onChange={() => handlePrivacyChange('profile_visibility', 'none')}
                        />
                        <label htmlFor="visibility-none" className="ml-2 text-sm text-gray-700">
                          {t('settings.page.privacy.profileVisibility.private')}
                        </label>
                      </div>
                    </div>
                  </div>
                  {/* Online Status toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.privacy.onlineStatus.title')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.privacy.onlineStatus.description')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={privacySettings.show_online_status}
                        onChange={() => handlePrivacyChange('show_online_status', !privacySettings.show_online_status)}
                      />
                    </div>
                  </div>
                  {/* Activity Sharing toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.privacy.activitySharing.title')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.privacy.activitySharing.description')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={privacySettings.share_activity}
                        onChange={() => handlePrivacyChange('share_activity', !privacySettings.share_activity)}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.privacy.dataCollection.title')}</h3>
                <div className="space-y-3">
                  {/* Data Collection toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{t('settings.page.privacy.dataCollection.allowCollection')}</h4>
                      <p className="text-sm text-muted-foreground">{t('settings.page.privacy.dataCollection.description')}</p>
                    </div>
                    <div className="flex items-center">
                      <input 
                        type="checkbox" 
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                        checked={privacySettings.allow_data_collection}
                        onChange={() => handlePrivacyChange('allow_data_collection', !privacySettings.allow_data_collection)}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <Alert type="info" title={t('settings.page.privacy.dataPrivacyNotice.title')}>
                {t('settings.page.privacy.dataPrivacyNotice.message')}
                View our <a href="/privacy-policy" className="text-primary underline">{t('settings.page.privacy.dataPrivacyNotice.privacyPolicyLink')}</a> for more information.
              </Alert>
            </CardContent>
            <CardFooter className="border-t pt-6">
              <Button
                onClick={handleSavePrivacy}
                isLoading={isLoading}
                disabled={isLoading}
                className="ml-auto"
              >
                {t('settings.page.privacy.saveButton')}
              </Button>
            </CardFooter>
            </TabContent>
          ) : (
            <TabContent value="privacy">
              <CardContent>
                <div className="flex items-center justify-center min-h-[300px]">
                  <div className="text-center">
                    <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('settings.page.accessRestricted.title')}</h3>
                    <p className="text-gray-600 mb-4">
                      {t('settings.page.accessRestricted.privacyMessage')}
                    </p>
                    <p className="text-sm text-gray-500">
                      {t('settings.page.accessRestricted.currentRole')} <Badge variant="secondary">{user?.role}</Badge>
                    </p>
                  </div>
                </div>
              </CardContent>
            </TabContent>
          )}
          {/* Preferences Tab */}
          <TabContent value="preferences">
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.preferences.appearance.title')}</h3>
                <div className="space-y-3">
                  {/* Theme Selection */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">{t('settings.page.preferences.appearance.theme.title')}</h4>
                    <p className="text-sm text-muted-foreground">{t('settings.page.preferences.appearance.theme.description')}</p>
                    <div className="grid grid-cols-3 gap-2 mt-2">
                      <button
                        type="button"
                        className={`flex flex-col items-center justify-center p-3 border rounded-md ${theme === 'light' ? 'border-primary' : 'border-gray-200'}`}
                        onClick={() => handleThemeChange('light')}
                      >
                        <Sun className="h-5 w-5 mb-1" />
                        <span className="text-sm font-medium">{t('settings.page.preferences.appearance.theme.light')}</span>
                      </button>
                      <button
                        type="button"
                        className={`flex flex-col items-center justify-center p-3 border rounded-md ${theme === 'dark' ? 'border-primary' : 'border-gray-200'}`}
                        onClick={() => handleThemeChange('dark')}
                      >
                        <Moon className="h-5 w-5 mb-1" />
                        <span className="text-sm font-medium">{t('settings.page.preferences.appearance.theme.dark')}</span>
                      </button>
                      <button
                        type="button"
                        className={`flex flex-col items-center justify-center p-3 border rounded-md ${theme === 'system' ? 'border-primary' : 'border-gray-200'}`}
                        onClick={() => handleThemeChange('system')}
                      >
                        <Monitor className="h-5 w-5 mb-1" />
                        <span className="text-sm font-medium">{t('settings.page.preferences.appearance.theme.system')}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.preferences.language.title')}</h3>
                <div className="space-y-3">
                  {/* Language Selection */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">{t('settings.page.preferences.language.displayLanguage')}</h4>
                    <p className="text-sm text-muted-foreground">{t('settings.page.preferences.language.description')}</p>
                    <div className="mt-2">
                      <select
                        value={language}
                        onChange={handleLanguageChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="en">English</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                        <option value="tr">Türkçe</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              <Alert type="warning" title={t('settings.page.preferences.themeSupport.title')}>
                {t('settings.page.preferences.themeSupport.message')}
              </Alert>
            </CardContent>
            <CardFooter className="border-t pt-6">
              <AnimatedButton
                onClick={handleSavePreferences}
                isLoading={isLoading}
                disabled={isLoading}
                className="ml-auto"
              >
                {t('settings.page.preferences.saveButton')}
              </AnimatedButton>
            </CardFooter>
          </TabContent>
          {/* AI Tab */}
          {canAccessAISettings ? (
            <TabContent value="ai">
              <AISettingsContent />
            </TabContent>
          ) : (
            <TabContent value="ai">
              <CardContent>
                <div className="flex items-center justify-center min-h-[300px]">
                  <div className="text-center">
                    <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('settings.page.accessRestricted.title')}</h3>
                    <p className="text-gray-600 mb-4">
                      {t('settings.page.accessRestricted.aiMessage')}
                    </p>
                    <p className="text-sm text-gray-500">
                      {t('settings.page.accessRestricted.currentRole')} <Badge variant="secondary">{user?.role}</Badge>
                    </p>
                  </div>
                </div>
              </CardContent>
            </TabContent>
          )}
          {/* Integrations Tab */}
          {canAccessIntegrations ? (
            <TabContent value="integrations">
              <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">{t('settings.page.integrations.title')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('settings.page.integrations.description')}
                </p>
                {/* Wedof Integration */}
                <Card>
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <Globe className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium">{t('settings.page.integrations.wedof.name')}</h4>
                          <p className="text-sm text-muted-foreground">{t('settings.page.integrations.wedof.description')}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open('/integrations/wedof', '_blank')}
                        >
                          {t('settings.page.integrations.wedof.configure')}
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
                {/* Google Workspace */}
                <Card>
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-red-100 rounded-lg">
                          <Globe className="h-5 w-5 text-red-600" />
                        </div>
                        <div>
                          <h4 className="font-medium">{t('settings.page.integrations.google.name')}</h4>
                          <p className="text-sm text-muted-foreground">{t('settings.page.integrations.google.description')}</p>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium text-sm">{t('settings.page.integrations.google.calendar.name')}</p>
                          <p className="text-xs text-muted-foreground">{t('settings.page.integrations.google.calendar.description')}</p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open('/calendar/google-integration', '_blank')}
                        >
                          {t('settings.page.integrations.google.calendar.setup')}
                        </Button>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium text-sm">{t('settings.page.integrations.google.drive.name')}</p>
                          <p className="text-xs text-muted-foreground">{t('settings.page.integrations.google.drive.description')}</p>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              {t('settings.page.integrations.google.drive.clientId')}
                            </label>
                            <Input
                              type="text"
                              placeholder={t('settings.page.integrations.google.drive.clientIdPlaceholder')}
                              className="text-xs"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              {t('settings.page.integrations.google.drive.clientSecret')}
                            </label>
                            <Input
                              type="password"
                              placeholder={t('settings.page.integrations.google.drive.clientSecretPlaceholder')}
                              className="text-xs"
                            />
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium text-sm">{t('settings.page.integrations.google.gmail.name')}</p>
                          <p className="text-xs text-muted-foreground">{t('settings.page.integrations.google.gmail.description')}</p>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              {t('settings.page.integrations.google.gmail.smtpSettings')}
                            </label>
                            <Input
                              type="email"
                              placeholder={t('settings.page.integrations.google.gmail.usernamePlaceholder')}
                              className="text-xs mb-1"
                            />
                            <Input
                              type="password"
                              placeholder={t('settings.page.integrations.google.gmail.passwordPlaceholder')}
                              className="text-xs"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
                {/* Other Integrations */}
                <Card>
                  <div className="p-4">
                    <h4 className="font-medium mb-3">{t('settings.page.integrations.other.title')}</h4>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium text-sm">{t('settings.page.integrations.other.pennylane.name')}</p>
                          <p className="text-xs text-muted-foreground">{t('settings.page.integrations.other.pennylane.description')}</p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open('/integrations/pennylane', '_blank')}
                        >
                          {t('settings.integrations.configure')}
                        </Button>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium text-sm">{t('settings.page.integrations.other.sms.name')}</p>
                          <p className="text-xs text-muted-foreground">{t('settings.page.integrations.other.sms.description')}</p>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              {t('settings.page.integrations.other.sms.provider')}
                            </label>
                            <select className="w-full text-xs border rounded px-2 py-1">
                              <option>{t('settings.page.integrations.other.sms.selectProvider')}</option>
                              <option>{t('settings.page.integrations.other.sms.providers.twilio')}</option>
                              <option>{t('settings.page.integrations.other.sms.providers.messageBird')}</option>
                              <option>{t('settings.page.integrations.other.sms.providers.orangeSms')}</option>
                            </select>
                          </div>
                          <div>
                            <Input
                              type="text"
                              placeholder={t('settings.page.integrations.other.sms.apiKeyPlaceholder')}
                              className="text-xs"
                            />
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <p className="font-medium text-sm">{t('settings.page.integrations.other.webhooks.name')}</p>
                          <p className="text-xs text-muted-foreground">{t('settings.page.integrations.other.webhooks.description')}</p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open('/integrations/webhooks', '_blank')}
                        >
                          {t('settings.page.integrations.other.webhooks.manage')}
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
                {/* Integration Status */}
                <Card>
                  <div className="p-4">
                    <h4 className="font-medium mb-3">{t('settings.page.integrations.health.title')}</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Wedof API</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">{t('settings.page.integrations.health.connected')}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Google Calendar</span>
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">{t('settings.page.integrations.health.partial')}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>AI Services</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">{t('settings.page.integrations.health.active')}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>SMS Service</span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">{t('settings.page.integrations.health.notConfigured')}</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
              <div className="flex justify-end pt-6 border-t">
                <Button onClick={() => {
                  addToast({
                    type: 'success',
                    title: t('settings.page.messages.settingsSaved'),
                    message: t('settings.page.messages.integrationsSaved'),
                  });
                }}>
                  {t('settings.page.integrations.saveButton')}
                </Button>
              </div>
            </CardContent>
            </TabContent>
          ) : (
            <TabContent value="integrations">
              <CardContent>
                <div className="flex items-center justify-center min-h-[300px]">
                  <div className="text-center">
                    <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('settings.page.accessRestricted.title')}</h3>
                    <p className="text-gray-600 mb-4">
                      {t('settings.page.accessRestricted.integrationsMessage')}
                    </p>
                    <p className="text-sm text-gray-500">
                      {t('settings.page.accessRestricted.currentRole')} <Badge variant="secondary">{user?.role}</Badge>
                    </p>
                  </div>
                </div>
              </CardContent>
            </TabContent>
          )}
        </Tabs>
      </AnimatedCard>
    </AnimatedPage>
  );
};
export default SettingsPage;