import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../../lib/api';
import { toast } from 'react-hot-toast';
import {
  BellIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  GlobeAltIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { Switch } from '@headlessui/react';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function PushNotificationSettings() {
  const { t } = useTranslation();
  const [settings, setSettings] = useState(null);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [settingsRes, devicesRes] = await Promise.all([
        api.get('/api/push-notifications/settings'),
        api.get('/api/push-notifications/devices')
      ]);

      setSettings(settingsRes.data.settings);
      setDevices(devicesRes.data.devices);
    } catch (error) {
      toast.error(t('pushNotifications.error.fetchFailed'));
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (newSettings) => {
    setUpdating(true);
    try {
      await api.put('/api/push-notifications/settings', newSettings);
      setSettings(newSettings);
      toast.success(t('pushNotifications.success.settingsUpdated'));
    } catch (error) {
      toast.error(t('pushNotifications.error.updateFailed'));
    } finally {
      setUpdating(false);
    }
  };

  const unregisterDevice = async (deviceToken) => {
    try {
      await api.post('/api/push-notifications/unregister', { device_token: deviceToken });
      setDevices(devices.filter(d => d.device_token !== deviceToken));
      toast.success(t('pushNotifications.success.deviceUnregistered'));
    } catch (error) {
      toast.error(t('pushNotifications.error.unregisterFailed'));
    }
  };

  const sendTestNotification = async () => {
    try {
      await api.post('/api/push-notifications/test');
      toast.success(t('pushNotifications.success.testSent'));
    } catch (error) {
      toast.error(t('pushNotifications.error.testFailed'));
    }
  };

  const getDeviceIcon = (deviceType) => {
    switch (deviceType) {
      case 'ios':
      case 'android':
        return DevicePhoneMobileIcon;
      case 'web':
        return GlobeAltIcon;
      default:
        return ComputerDesktopIcon;
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  if (!settings) {
    return <div>{t('pushNotifications.error.settingsNotFound')}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Main Settings */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">
            {t('pushNotifications.settings.title')}
          </h3>
          <button
            onClick={sendTestNotification}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <BellIcon className="h-4 w-4 mr-2" />
            {t('pushNotifications.actions.sendTest')}
          </button>
        </div>

        {/* Master Toggle */}
        <div className="flex items-center justify-between py-4 border-b border-gray-200">
          <div>
            <h4 className="font-medium text-gray-900">
              {t('pushNotifications.settings.enableNotifications')}
            </h4>
            <p className="text-sm text-gray-500">
              {t('pushNotifications.settings.enableNotificationsDesc')}
            </p>
          </div>
          <Switch
            checked={settings.enabled}
            onChange={(enabled) => updateSettings({ ...settings, enabled })}
            disabled={updating}
            className={classNames(
              settings.enabled ? 'bg-indigo-600' : 'bg-gray-200',
              'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2'
            )}
          >
            <span
              className={classNames(
                settings.enabled ? 'translate-x-5' : 'translate-x-0',
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
              )}
            />
          </Switch>
        </div>

        {/* Notification Types */}
        <div className="space-y-4 mt-6">
          <h4 className="font-medium text-gray-900">
            {t('pushNotifications.settings.notificationTypes')}
          </h4>
          {Object.entries(settings.types).map(([type, enabled]) => (
            <div key={type} className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-gray-700">
                  {t(`pushNotifications.types.${type}`)}
                </span>
              </div>
              <Switch
                checked={enabled}
                onChange={(value) => updateSettings({
                  ...settings,
                  types: { ...settings.types, [type]: value }
                })}
                disabled={updating || !settings.enabled}
                className={classNames(
                  enabled ? 'bg-indigo-600' : 'bg-gray-200',
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2'
                )}
              >
                <span
                  className={classNames(
                    enabled ? 'translate-x-5' : 'translate-x-0',
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                  )}
                />
              </Switch>
            </div>
          ))}
        </div>

        {/* Quiet Hours */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">
                {t('pushNotifications.settings.quietHours')}
              </h4>
              <p className="text-sm text-gray-500">
                {t('pushNotifications.settings.quietHoursDesc')}
              </p>
            </div>
            <Switch
              checked={settings.quiet_hours.enabled}
              onChange={(enabled) => updateSettings({
                ...settings,
                quiet_hours: { ...settings.quiet_hours, enabled }
              })}
              disabled={updating || !settings.enabled}
              className={classNames(
                settings.quiet_hours.enabled ? 'bg-indigo-600' : 'bg-gray-200',
                'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2'
              )}
            >
              <span
                className={classNames(
                  settings.quiet_hours.enabled ? 'translate-x-5' : 'translate-x-0',
                  'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                )}
              />
            </Switch>
          </div>

          {settings.quiet_hours.enabled && (
            <div className="mt-4 flex items-center space-x-4">
              <ClockIcon className="h-5 w-5 text-gray-400" />
              <div className="flex items-center space-x-2">
                <input
                  type="time"
                  value={settings.quiet_hours.start}
                  onChange={(e) => updateSettings({
                    ...settings,
                    quiet_hours: { ...settings.quiet_hours, start: e.target.value }
                  })}
                  className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                <span className="text-gray-500">{t('pushNotifications.settings.to')}</span>
                <input
                  type="time"
                  value={settings.quiet_hours.end}
                  onChange={(e) => updateSettings({
                    ...settings,
                    quiet_hours: { ...settings.quiet_hours, end: e.target.value }
                  })}
                  className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Registered Devices */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {t('pushNotifications.devices.title')} ({devices.length})
        </h3>

        {devices.length === 0 ? (
          <p className="text-gray-500 text-sm">
            {t('pushNotifications.devices.noDevices')}
          </p>
        ) : (
          <div className="space-y-3">
            {devices.map((device) => {
              const Icon = getDeviceIcon(device.device_type);
              return (
                <div
                  key={device.id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {device.device_name || t(`pushNotifications.devices.types.${device.device_type}`)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {device.device_model && `${device.device_model} • `}
                        {device.device_os && `${device.device_os} • `}
                        {t('pushNotifications.devices.provider')}: {device.provider}
                      </p>
                      <p className="text-xs text-gray-400">
                        {t('pushNotifications.devices.lastUsed')}: {
                          device.last_used_at 
                            ? new Date(device.last_used_at).toLocaleDateString()
                            : t('pushNotifications.devices.never')
                        }
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {device.is_active ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircleIcon className="h-5 w-5 text-red-500" />
                    )}
                    <button
                      onClick={() => unregisterDevice(device.device_token)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}