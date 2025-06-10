// TODO: i18n - processed
import {
  generateSettingsData,
  generateSettingsOptions,
  generateDataExportOptions } from
'./mockSettingsData';import { useTranslation } from "react-i18next";
export const setupSettingsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };
  // Settings endpoints
  api.get = function (url, ...args) {
    // General settings endpoint
    if (url === '/api/settings' || url === '/api/settings/general') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData
      });
    }
    // Profile settings endpoint
    if (url === '/api/settings/profile') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData.profile
      });
    }
    // Notification settings endpoint
    if (url === '/api/settings/notifications') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData.notifications
      });
    }
    // Privacy settings endpoint
    if (url === '/api/settings/privacy') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData.privacy
      });
    }
    // Security settings endpoint
    if (url === '/api/settings/security') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData.security
      });
    }
    // Appearance settings endpoint
    if (url === '/api/settings/appearance' || url === '/api/settings/theme') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData.appearance
      });
    }
    // Integration settings endpoint
    if (url === '/api/settings/integrations') {
      const userRole = localStorage.getItem('userRole') || 'student';
      const settingsData = generateSettingsData(userRole);
      return Promise.resolve({
        status: 200,
        data: settingsData.integrations
      });
    }
    // Organization settings (admin/tenant_admin only)
    if (url === '/api/settings/organization') {
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'admin' || userRole === 'tenant_admin') {
        const settingsData = generateSettingsData(userRole);
        return Promise.resolve({
          status: 200,
          data: settingsData.organization
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    // Billing settings (admin/tenant_admin only)
    if (url === '/api/settings/billing') {
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'admin' || userRole === 'tenant_admin') {
        const settingsData = generateSettingsData(userRole);
        return Promise.resolve({
          status: 200,
          data: settingsData.billing
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    // Teaching settings (trainer only)
    if (url === '/api/settings/teaching') {
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'trainer') {
        const settingsData = generateSettingsData(userRole);
        return Promise.resolve({
          status: 200,
          data: settingsData.teaching
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    // Learning settings (student only)
    if (url === '/api/settings/learning') {
      const userRole = localStorage.getItem('userRole');
      if (userRole === 'student') {
        const settingsData = generateSettingsData(userRole);
        return Promise.resolve({
          status: 200,
          data: settingsData.learning
        });
      }
      return Promise.resolve({
        status: 403,
        data: { error: 'Access denied' }
      });
    }
    // Settings options endpoint
    if (url === '/api/settings/options') {
      const options = generateSettingsOptions();
      return Promise.resolve({
        status: 200,
        data: options
      });
    }
    // Data export options endpoint
    if (url === '/api/settings/export-options') {
      const exportOptions = generateDataExportOptions();
      return Promise.resolve({
        status: 200,
        data: exportOptions
      });
    }
    // Password requirements endpoint
    if (url === '/api/settings/password-requirements') {
      return Promise.resolve({
        status: 200,
        data: {
          minLength: 8,
          requireUppercase: true,
          requireLowercase: true,
          requireNumbers: true,
          requireSpecialChars: true,
          preventCommonPasswords: true,
          preventReuse: 5
        }
      });
    }
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  // Update settings endpoints
  api.put = function (url, data, ...args) {
    // Update general settings
    if (url === '/api/settings' || url === '/api/settings/general') {
      return Promise.resolve({
        status: 200,
        data: {
          ...data,
          updatedAt: new Date().toISOString(),
          message: 'Settings updated successfully'
        }
      });
    }
    // Update specific setting sections
    const settingsSections = [
    'profile', 'notifications', 'privacy', 'security',
    'appearance', 'integrations', 'organization', 'billing',
    'teaching', 'learning', 'theme'];

    for (const section of settingsSections) {
      if (url === `/api/settings/${section}`) {
        return Promise.resolve({
          status: 200,
          data: {
            ...data,
            updatedAt: new Date().toISOString(),
            message: `${section} settings updated successfully`
          }
        });
      }
    }
    // Update password
    if (url === '/api/settings/password') {
      // Simulate password validation
      if (!data.currentPassword || !data.newPassword) {
        return Promise.resolve({
          status: 400,
          data: { error: 'Current and new password are required' }
        });
      }
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Password updated successfully',
          lastPasswordChange: new Date().toISOString()
        }
      });
    }
    // Update two-factor authentication
    if (url === '/api/settings/two-factor') {
      return Promise.resolve({
        status: 200,
        data: {
          enabled: data.enabled,
          qrCode: data.enabled ? 'data:image/png;base64,iVBORw0KGgoAAAANS...' : null,
          backupCodes: data.enabled ? [
          'ABCD-EFGH-IJKL',
          'MNOP-QRST-UVWX',
          'YZAB-CDEF-GHIJ'] :
          null
        }
      });
    }
    return originalFunctions.put.call(api, url, data, ...args);
  };
  // Settings POST endpoints
  api.post = function (url, data, ...args) {
    // Export data endpoint
    if (url === '/api/settings/export-data') {
      return Promise.resolve({
        status: 200,
        data: {
          downloadUrl: `/api/downloads/export-${Date.now()}.${data.format}`,
          expiresAt: new Date(Date.now() + 3600000).toISOString(),
          message: 'Data export initiated successfully'
        }
      });
    }
    // Import settings endpoint
    if (url === '/api/settings/import') {
      return Promise.resolve({
        status: 200,
        data: {
          imported: true,
          message: 'Settings imported successfully',
          changes: {
            profile: 5,
            notifications: 3,
            privacy: 2
          }
        }
      });
    }
    // Connect integration endpoint
    if (url.startsWith('/api/settings/integrations/') && url.endsWith('/connect')) {
      const integration = url.split('/')[4];
      return Promise.resolve({
        status: 200,
        data: {
          authUrl: `https://auth.${integration}.com/oauth/authorize`,
          state: 'random-state-string',
          message: `Redirecting to ${integration} for authorization`
        }
      });
    }
    // Add API key endpoint
    if (url === '/api/settings/api-keys') {
      return Promise.resolve({
        status: 201,
        data: {
          id: Date.now(),
          name: data.name,
          key: `ta_live_key_${Math.random().toString(36).substring(2, 15)}`,
          permissions: data.permissions,
          createdAt: new Date().toISOString(),
          lastUsed: null
        }
      });
    }
    // Add team member (admin/tenant_admin)
    if (url === '/api/settings/team/invite') {
      return Promise.resolve({
        status: 200,
        data: {
          invited: true,
          email: data.email,
          role: data.role,
          inviteUrl: `https://app.example.com/invite/${Date.now()}`,
          expiresAt: new Date(Date.now() + 7 * 24 * 3600000).toISOString()
        }
      });
    }
    return originalFunctions.post.call(api, url, data, ...args);
  };
  // Settings DELETE endpoints
  api.delete = function (url, ...args) {
    // Delete account endpoint
    if (url === '/api/settings/account') {
      return Promise.resolve({
        status: 200,
        data: {
          message: 'Account deletion request received. You will receive a confirmation email.',
          deletionDate: new Date(Date.now() + 30 * 24 * 3600000).toISOString()
        }
      });
    }
    // Disconnect integration endpoint
    if (url.startsWith('/api/settings/integrations/') && url.endsWith('/disconnect')) {
      const integration = url.split('/')[4];
      return Promise.resolve({
        status: 200,
        data: {
          disconnected: true,
          integration,
          message: `${integration} disconnected successfully`
        }
      });
    }
    // Revoke session endpoint
    if (url.match(/^\/api\/settings\/sessions\/\d+$/)) {
      const sessionId = url.split('/').pop();
      return Promise.resolve({
        status: 200,
        data: {
          revoked: true,
          sessionId,
          message: 'Session revoked successfully'
        }
      });
    }
    // Delete API key endpoint
    if (url.match(/^\/api\/settings\/api-keys\/\d+$/)) {
      const keyId = url.split('/').pop();
      return Promise.resolve({
        status: 200,
        data: {
          deleted: true,
          keyId,
          message: 'API key deleted successfully'
        }
      });
    }
    return originalFunctions.delete.call(api, url, ...args);
  };
};