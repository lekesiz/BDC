import React, { useState, useEffect } from 'react';
import { Bell, Shield, Globe, Moon, Sun, Monitor, Brain } from 'lucide-react';

import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/toast';
import { AnimatedButton, AnimatedCard, AnimatedPage } from '@/components/animations';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Alert } from '@/components/ui/alert';
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
  
  // State management
  const [activeTab, setActiveTab] = useState('notifications');
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState('system');
  const [language, setLanguage] = useState('en');
  
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
    // In a real app, this would update the language throughout the app
  };
  
  // Handle notification settings save
  const handleSaveNotifications = async () => {
    try {
      setIsLoading(true);
      
      // Call API to save notification settings
      await api.put('/api/settings/notifications', notificationSettings);
      
      addToast({
        type: 'success',
        title: 'Settings updated',
        message: 'Your notification settings have been saved.',
      });
    } catch (err) {
      console.error('Failed to save notification settings:', err);
      
      addToast({
        type: 'error',
        title: 'Update failed',
        message: err.response?.data?.message || 'Failed to update settings. Please try again.',
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
        title: 'Settings updated',
        message: 'Your privacy settings have been saved.',
      });
    } catch (err) {
      console.error('Failed to save privacy settings:', err);
      
      addToast({
        type: 'error',
        title: 'Update failed',
        message: err.response?.data?.message || 'Failed to update settings. Please try again.',
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
        title: 'Settings updated',
        message: 'Your preferences have been saved.',
      });
    } catch (err) {
      console.error('Failed to save preferences:', err);
      
      addToast({
        type: 'error',
        title: 'Update failed',
        message: err.response?.data?.message || 'Failed to update settings. Please try again.',
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
        Settings
      </motion.h1>
      
      <AnimatedCard>
        <CardHeader>
          <CardTitle>Account Settings</CardTitle>
          <CardDescription>
            Manage your account preferences and settings
          </CardDescription>
        </CardHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <CardContent className="pb-0">
            <TabsList className="mb-6">
              <TabTrigger value="notifications">
                <Bell className="h-4 w-4 mr-2" />
                Notifications
              </TabTrigger>
              <TabTrigger value="privacy">
                <Shield className="h-4 w-4 mr-2" />
                Privacy
              </TabTrigger>
              <TabTrigger value="preferences">
                <Globe className="h-4 w-4 mr-2" />
                Preferences
              </TabTrigger>
              <TabTrigger value="ai">
                <Brain className="h-4 w-4 mr-2" />
                AI
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
                  <h3 className="text-lg font-medium">Email Notifications</h3>
                  
                  <div className="space-y-3">
                  {/* Email Notifications toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">Email Notifications</h4>
                      <p className="text-sm text-muted-foreground">Receive email notifications for important updates</p>
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
                      <h4 className="text-sm font-medium">Marketing Emails</h4>
                      <p className="text-sm text-muted-foreground">Receive emails about new features and offers</p>
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
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Push Notifications</h3>
                
                <div className="space-y-3">
                  {/* Push Notifications toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">Push Notifications</h4>
                      <p className="text-sm text-muted-foreground">Receive push notifications in your browser</p>
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
                      <h4 className="text-sm font-medium">New Messages</h4>
                      <p className="text-sm text-muted-foreground">Get notified when you receive new messages</p>
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
                      <h4 className="text-sm font-medium">Session Reminders</h4>
                      <p className="text-sm text-muted-foreground">Get reminders for upcoming sessions</p>
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
                      <h4 className="text-sm font-medium">Evaluation Results</h4>
                      <p className="text-sm text-muted-foreground">Get notified when your evaluation results are ready</p>
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
                <h3 className="text-lg font-medium">SMS Notifications</h3>
                
                <div className="space-y-3">
                  {/* SMS Notifications toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">SMS Notifications</h4>
                      <p className="text-sm text-muted-foreground">Receive text message notifications (carrier charges may apply)</p>
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
                Save Notification Settings
              </Button>
            </CardFooter>
          </TabContent>
          
          {/* Privacy Tab */}
          <TabContent value="privacy">
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Privacy Settings</h3>
                
                <div className="space-y-3">
                  {/* Profile Visibility */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Profile Visibility</h4>
                    <p className="text-sm text-muted-foreground">Control who can see your profile information</p>
                    
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
                          Everyone
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
                          Only connections
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
                          Private
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  {/* Online Status toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">Show Online Status</h4>
                      <p className="text-sm text-muted-foreground">Allow others to see when you're online</p>
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
                      <h4 className="text-sm font-medium">Share Activity</h4>
                      <p className="text-sm text-muted-foreground">Share your learning progress and achievements</p>
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
                <h3 className="text-lg font-medium">Data Collection</h3>
                
                <div className="space-y-3">
                  {/* Data Collection toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium">Allow Data Collection</h4>
                      <p className="text-sm text-muted-foreground">Help us improve our platform by sharing usage data</p>
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
              
              <Alert type="info" title="Data Privacy">
                Your data is always protected and never shared with third parties without your consent.
                View our <a href="/privacy-policy" className="text-primary underline">Privacy Policy</a> for more information.
              </Alert>
            </CardContent>
            
            <CardFooter className="border-t pt-6">
              <Button
                onClick={handleSavePrivacy}
                isLoading={isLoading}
                disabled={isLoading}
                className="ml-auto"
              >
                Save Privacy Settings
              </Button>
            </CardFooter>
          </TabContent>
          
          {/* Preferences Tab */}
          <TabContent value="preferences">
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Appearance</h3>
                
                <div className="space-y-3">
                  {/* Theme Selection */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Theme</h4>
                    <p className="text-sm text-muted-foreground">Choose your preferred theme</p>
                    
                    <div className="grid grid-cols-3 gap-2 mt-2">
                      <button
                        type="button"
                        className={`flex flex-col items-center justify-center p-3 border rounded-md ${theme === 'light' ? 'border-primary' : 'border-gray-200'}`}
                        onClick={() => handleThemeChange('light')}
                      >
                        <Sun className="h-5 w-5 mb-1" />
                        <span className="text-sm font-medium">Light</span>
                      </button>
                      
                      <button
                        type="button"
                        className={`flex flex-col items-center justify-center p-3 border rounded-md ${theme === 'dark' ? 'border-primary' : 'border-gray-200'}`}
                        onClick={() => handleThemeChange('dark')}
                      >
                        <Moon className="h-5 w-5 mb-1" />
                        <span className="text-sm font-medium">Dark</span>
                      </button>
                      
                      <button
                        type="button"
                        className={`flex flex-col items-center justify-center p-3 border rounded-md ${theme === 'system' ? 'border-primary' : 'border-gray-200'}`}
                        onClick={() => handleThemeChange('system')}
                      >
                        <Monitor className="h-5 w-5 mb-1" />
                        <span className="text-sm font-medium">System</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Language</h3>
                
                <div className="space-y-3">
                  {/* Language Selection */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Display Language</h4>
                    <p className="text-sm text-muted-foreground">Choose your preferred language for the interface</p>
                    
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
              
              <Alert type="warning" title="Theme Support">
                Theme settings are currently in beta and may not apply to all parts of the application.
              </Alert>
            </CardContent>
            
            <CardFooter className="border-t pt-6">
              <AnimatedButton
                onClick={handleSavePreferences}
                isLoading={isLoading}
                disabled={isLoading}
                className="ml-auto"
              >
                Save Preferences
              </AnimatedButton>
            </CardFooter>
          </TabContent>
          
          {/* AI Tab */}
          <TabContent value="ai">
            <AISettingsContent />
          </TabContent>
        </Tabs>
      </AnimatedCard>
    </AnimatedPage>
  );
};

export default SettingsPage;