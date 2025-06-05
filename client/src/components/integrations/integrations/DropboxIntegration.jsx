import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Progress } from '../../ui/progress';
import {
  Cloud,
  Folder,
  File,
  Upload,
  Download,
  Link2,
  FolderSync,
  History,
  Shield,
  HardDrive,
  Users,
  RefreshCw
} from 'lucide-react';
const DropboxIntegration = ({ integration, onBack }) => {
  const [accountInfo, setAccountInfo] = useState({
    email: 'admin@bdcacademy.com',
    accountType: 'Business',
    storageUsed: 234.5,
    storageTotal: 1000,
    teamMembers: 45
  });
  const [syncedFolders, setSyncedFolders] = useState([
    { id: '1', name: 'Training Resources', path: '/Training Resources', status: 'synced', size: '45.2 GB', files: 1234 },
    { id: '2', name: 'Student Submissions', path: '/Student Submissions', status: 'syncing', size: '23.8 GB', files: 567 },
    { id: '3', name: 'Administrative Docs', path: '/Administrative Docs', status: 'synced', size: '12.4 GB', files: 234 },
    { id: '4', name: 'Course Materials', path: '/Course Materials', status: 'error', size: '67.9 GB', files: 2345 }
  ]);
  const [backupSettings, setBackupSettings] = useState({
    autoBackup: true,
    backupFrequency: 'daily',
    versioning: true,
    maxVersions: 10,
    includeDeleted: false,
    compression: true
  });
  const configFields = [
    {
      name: 'accessToken',
      label: 'Access Token',
      type: 'password',
      placeholder: 'Your Dropbox access token',
      required: true,
      description: 'Generate from Dropbox App Console'
    },
    {
      name: 'appKey',
      label: 'App Key',
      type: 'text',
      placeholder: 'Your Dropbox app key',
      required: true
    },
    {
      name: 'appSecret',
      label: 'App Secret',
      type: 'password',
      placeholder: 'Your Dropbox app secret',
      required: true
    },
    {
      name: 'rootPath',
      label: 'Root Sync Path',
      type: 'text',
      placeholder: '/BDC Academy',
      required: false,
      description: 'Base folder for all synced content'
    },
    {
      name: 'teamFolder',
      label: 'Use Team Folders',
      type: 'checkbox',
      description: 'Enable Dropbox Business team folders'
    }
  ];
  const oauthConfig = {
    authUrl: 'https://www.dropbox.com/oauth2/authorize',
    tokenUrl: 'https://api.dropboxapi.com/oauth2/token',
    clientId: process.env.REACT_APP_DROPBOX_APP_KEY,
    redirectUri: `${window.location.origin}/integrations/dropbox/callback`,
    scopes: []
  };
  const webhookEvents = [
    'file.added',
    'file.modified',
    'file.deleted',
    'folder.created',
    'share.created',
    'member.added'
  ];
  const apiEndpoints = [
    {
      method: 'GET',
      path: '/api/integrations/dropbox/files/list',
      description: 'List files in a folder'
    },
    {
      method: 'POST',
      path: '/api/integrations/dropbox/files/upload',
      description: 'Upload a file'
    },
    {
      method: 'POST',
      path: '/api/integrations/dropbox/folders/create',
      description: 'Create a new folder'
    },
    {
      method: 'POST',
      path: '/api/integrations/dropbox/sharing/create',
      description: 'Create a shared link'
    }
  ];
  const storagePercentage = (accountInfo.storageUsed / accountInfo.storageTotal) * 100;
  const customOverview = (
    <>
      {/* Account Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <Cloud className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Dropbox {accountInfo.accountType}</h3>
                <p className="text-sm text-gray-500">{accountInfo.email}</p>
              </div>
            </div>
            <Badge variant="success">Active</Badge>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Storage Used</span>
                <span className="text-gray-600">
                  {accountInfo.storageUsed} GB / {accountInfo.storageTotal} GB
                </span>
              </div>
              <Progress value={storagePercentage} className="h-3" />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <HardDrive className="w-6 h-6 mx-auto mb-2 text-gray-600" />
                <p className="text-2xl font-bold">{storagePercentage.toFixed(1)}%</p>
                <p className="text-sm text-gray-600">Used</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <Users className="w-6 h-6 mx-auto mb-2 text-gray-600" />
                <p className="text-2xl font-bold">{accountInfo.teamMembers}</p>
                <p className="text-sm text-gray-600">Team Members</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <FolderSync className="w-6 h-6 mx-auto mb-2 text-gray-600" />
                <p className="text-2xl font-bold">4</p>
                <p className="text-sm text-gray-600">Synced Folders</p>
              </div>
            </div>
          </div>
        </div>
      </Card>
      {/* Synced Folders */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Synced Folders</h3>
            <Button variant="primary" size="sm">
              <FolderSync className="w-4 h-4 mr-2" />
              Add Folder
            </Button>
          </div>
          <div className="space-y-3">
            {syncedFolders.map((folder) => (
              <div key={folder.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  <Folder className="w-5 h-5 text-blue-500 mr-3" />
                  <div>
                    <p className="font-medium">{folder.name}</p>
                    <p className="text-sm text-gray-500">
                      {folder.path} · {folder.files} files · {folder.size}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={
                    folder.status === 'synced' ? 'success' :
                    folder.status === 'syncing' ? 'warning' : 'danger'
                  }>
                    {folder.status === 'syncing' && (
                      <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                    )}
                    {folder.status}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    Manage
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Backup Settings */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Backup Configuration</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Automatic Backup</p>
                <p className="text-sm text-gray-500">Backup files automatically</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={backupSettings.autoBackup}
                  onChange={() => setBackupSettings({
                    ...backupSettings,
                    autoBackup: !backupSettings.autoBackup
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Backup Frequency
              </label>
              <select
                value={backupSettings.backupFrequency}
                onChange={(e) => setBackupSettings({
                  ...backupSettings,
                  backupFrequency: e.target.value
                })}
                className="form-select rounded-md border-gray-300 w-full"
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Version Control</p>
                <p className="text-sm text-gray-500">Keep file version history</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={backupSettings.versioning}
                  onChange={() => setBackupSettings({
                    ...backupSettings,
                    versioning: !backupSettings.versioning
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Compression</p>
                <p className="text-sm text-gray-500">Compress files before backup</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={backupSettings.compression}
                  onChange={() => setBackupSettings({
                    ...backupSettings,
                    compression: !backupSettings.compression
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>
      </Card>
      {/* Quick Actions */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Upload className="w-5 h-5 text-blue-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Upload Files</p>
                <p className="text-sm text-gray-500">Add files to Dropbox</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Link2 className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Create Share Link</p>
                <p className="text-sm text-gray-500">Share files with link</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <History className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Version History</p>
                <p className="text-sm text-gray-500">View file versions</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Shield className="w-5 h-5 text-orange-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Security Settings</p>
                <p className="text-sm text-gray-500">Manage permissions</p>
              </div>
            </button>
          </div>
        </div>
      </Card>
      {/* Recent Activity */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {[
              { action: 'Backup completed', details: 'Training Resources folder', time: '5 minutes ago', status: 'success' },
              { action: 'File uploaded', details: 'Assessment_Template_2024.docx', time: '30 minutes ago', status: 'success' },
              { action: 'Sync error', details: 'Course Materials - Permission denied', time: '1 hour ago', status: 'error' },
              { action: 'Folder shared', details: 'Student Submissions with 5 users', time: '2 hours ago', status: 'info' },
              { action: 'Version restored', details: 'Budget_Report_Q4.xlsx (v3)', time: '3 hours ago', status: 'success' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-3 ${
                    activity.status === 'success' ? 'bg-green-500' :
                    activity.status === 'error' ? 'bg-red-500' : 'bg-blue-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.details}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">{activity.time}</span>
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
export default DropboxIntegration;