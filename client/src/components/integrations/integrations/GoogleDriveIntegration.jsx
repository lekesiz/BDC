import React, { useState } from 'react';
import BaseIntegration from '../BaseIntegration';
import { Card } from '../../ui/card';
import { Button } from '../../ui/button';
import { Badge } from '../../ui/badge';
import { Progress } from '../../ui/progress';
import {
  HardDrive,
  Folder,
  File,
  Upload,
  Download,
  Share2,
  FolderPlus,
  FileText,
  Image,
  Video,
  Archive,
  Shield,
  RefreshCw
} from 'lucide-react';
const GoogleDriveIntegration = ({ integration, onBack }) => {
  const [storageInfo, setStorageInfo] = useState({
    used: 45.2,
    total: 100,
    percentage: 45.2
  });
  const [folders, setFolders] = useState([
    { id: '1', name: 'Training Materials', files: 234, size: '12.5 GB', shared: true, lastModified: '2024-11-15' },
    { id: '2', name: 'Beneficiary Documents', files: 567, size: '8.3 GB', shared: true, lastModified: '2024-11-17' },
    { id: '3', name: 'Assessment Results', files: 123, size: '3.2 GB', shared: false, lastModified: '2024-11-16' },
    { id: '4', name: 'Course Videos', files: 45, size: '15.8 GB', shared: true, lastModified: '2024-11-14' },
    { id: '5', name: 'Administrative', files: 89, size: '2.1 GB', shared: false, lastModified: '2024-11-17' }
  ]);
  const [syncSettings, setSyncSettings] = useState({
    autoSync: true,
    syncInterval: 30,
    syncDirection: 'bidirectional',
    fileTypes: ['documents', 'spreadsheets', 'presentations', 'pdfs', 'images', 'videos'],
    maxFileSize: 100,
    preserveFolderStructure: true
  });
  const configFields = [
    {
      name: 'clientId',
      label: 'Client ID',
      type: 'text',
      placeholder: 'Your Google OAuth Client ID',
      required: true,
      description: 'Get this from Google Cloud Console'
    },
    {
      name: 'clientSecret',
      label: 'Client Secret',
      type: 'password',
      placeholder: 'Your Google OAuth Client Secret',
      required: true
    },
    {
      name: 'rootFolder',
      label: 'Root Folder',
      type: 'text',
      placeholder: 'BDC Academy Files',
      required: false,
      description: 'Main folder for all synced files'
    },
    {
      name: 'syncInterval',
      label: 'Sync Interval',
      type: 'select',
      options: [
        { value: '15', label: 'Every 15 minutes' },
        { value: '30', label: 'Every 30 minutes' },
        { value: '60', label: 'Every hour' },
        { value: '360', label: 'Every 6 hours' },
        { value: '1440', label: 'Daily' }
      ],
      required: true
    },
    {
      name: 'autoBackup',
      label: 'Enable automatic backup',
      type: 'checkbox',
      description: 'Automatically backup important documents'
    }
  ];
  const oauthConfig = {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID,
    redirectUri: `${window.location.origin}/integrations/google-drive/callback`,
    scopes: [
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/drive.file',
      'https://www.googleapis.com/auth/drive.readonly'
    ]
  };
  const webhookEvents = [
    'file.created',
    'file.updated',
    'file.deleted',
    'folder.created',
    'permission.changed',
    'storage.limit.warning'
  ];
  const apiEndpoints = [
    {
      method: 'GET',
      path: '/api/integrations/drive/files',
      description: 'List files and folders'
    },
    {
      method: 'POST',
      path: '/api/integrations/drive/upload',
      description: 'Upload a file to Drive'
    },
    {
      method: 'GET',
      path: '/api/integrations/drive/download/:id',
      description: 'Download a file'
    },
    {
      method: 'POST',
      path: '/api/integrations/drive/share',
      description: 'Share files or folders'
    }
  ];
  const fileTypeStats = [
    { type: 'Documents', icon: FileText, count: 456, size: '5.2 GB', color: 'text-blue-600' },
    { type: 'Spreadsheets', icon: FileText, count: 234, size: '2.8 GB', color: 'text-green-600' },
    { type: 'Images', icon: Image, count: 789, size: '12.4 GB', color: 'text-purple-600' },
    { type: 'Videos', icon: Video, count: 67, size: '18.3 GB', color: 'text-red-600' },
    { type: 'Archives', icon: Archive, count: 45, size: '6.5 GB', color: 'text-orange-600' }
  ];
  const customOverview = (
    <>
      {/* Storage Overview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <HardDrive className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Storage Usage</h3>
                <p className="text-sm text-gray-500">Google Drive Storage</p>
              </div>
            </div>
            <Button variant="secondary" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Sync Now
            </Button>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Used: {storageInfo.used} GB</span>
                <span className="text-gray-600">Total: {storageInfo.total} GB</span>
              </div>
              <Progress value={storageInfo.percentage} className="h-3" />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {fileTypeStats.map((stat) => {
                const Icon = stat.icon;
                return (
                  <div key={stat.type} className="text-center">
                    <Icon className={`w-8 h-8 mx-auto mb-2 ${stat.color}`} />
                    <p className="text-sm font-medium">{stat.count}</p>
                    <p className="text-xs text-gray-500">{stat.size}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </Card>
      {/* Folders */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Synced Folders</h3>
            <Button variant="primary" size="sm">
              <FolderPlus className="w-4 h-4 mr-2" />
              Create Folder
            </Button>
          </div>
          <div className="space-y-3">
            {folders.map((folder) => (
              <div key={folder.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center">
                  <Folder className="w-5 h-5 text-blue-500 mr-3" />
                  <div>
                    <p className="font-medium">{folder.name}</p>
                    <p className="text-sm text-gray-500">
                      {folder.files} files · {folder.size} · Modified {folder.lastModified}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {folder.shared && (
                    <Badge variant="secondary">
                      <Share2 className="w-3 h-3 mr-1" />
                      Shared
                    </Badge>
                  )}
                  <Button variant="ghost" size="sm">
                    Open
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      {/* Sync Settings */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Sync Configuration</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Automatic Sync</p>
                <p className="text-sm text-gray-500">Keep files synchronized automatically</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={syncSettings.autoSync}
                  onChange={() => setSyncSettings({
                    ...syncSettings,
                    autoSync: !syncSettings.autoSync
                  })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                File Types to Sync
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {['documents', 'spreadsheets', 'presentations', 'pdfs', 'images', 'videos'].map((type) => (
                  <label key={type} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={syncSettings.fileTypes.includes(type)}
                      onChange={() => {
                        const newTypes = syncSettings.fileTypes.includes(type)
                          ? syncSettings.fileTypes.filter(t => t !== type)
                          : [...syncSettings.fileTypes, type];
                        setSyncSettings({ ...syncSettings, fileTypes: newTypes });
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum File Size (MB)
              </label>
              <input
                type="number"
                value={syncSettings.maxFileSize}
                onChange={(e) => setSyncSettings({
                  ...syncSettings,
                  maxFileSize: parseInt(e.target.value)
                })}
                className="form-input rounded-md border-gray-300 w-full"
              />
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
                <p className="text-sm text-gray-500">Add files to Google Drive</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-5 h-5 text-green-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Bulk Download</p>
                <p className="text-sm text-gray-500">Download multiple files</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Share2 className="w-5 h-5 text-purple-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Share Settings</p>
                <p className="text-sm text-gray-500">Manage permissions</p>
              </div>
            </button>
            <button className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
              <Shield className="w-5 h-5 text-orange-600 mr-3" />
              <div className="text-left">
                <p className="font-medium">Security Scan</p>
                <p className="text-sm text-gray-500">Check file security</p>
              </div>
            </button>
          </div>
        </div>
      </Card>
      {/* Recent Activity */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent File Activity</h3>
          <div className="space-y-3">
            {[
              { action: 'Uploaded', file: 'Python_Course_Module_5.pdf', user: 'John Doe', time: '10 minutes ago', type: 'upload' },
              { action: 'Modified', file: 'Training_Schedule_2024.xlsx', user: 'Jane Smith', time: '1 hour ago', type: 'edit' },
              { action: 'Shared', file: 'Assessment_Results_Q4', user: 'Admin', time: '2 hours ago', type: 'share' },
              { action: 'Downloaded', file: 'Certificate_Template.docx', user: 'Mike Johnson', time: '3 hours ago', type: 'download' },
              { action: 'Deleted', file: 'Old_Training_Video.mp4', user: 'System', time: '5 hours ago', type: 'delete' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b">
                <div className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                    activity.type === 'upload' ? 'bg-blue-100' :
                    activity.type === 'edit' ? 'bg-green-100' :
                    activity.type === 'share' ? 'bg-purple-100' :
                    activity.type === 'download' ? 'bg-orange-100' :
                    'bg-red-100'
                  }`}>
                    {activity.type === 'upload' && <Upload className="w-4 h-4 text-blue-600" />}
                    {activity.type === 'edit' && <File className="w-4 h-4 text-green-600" />}
                    {activity.type === 'share' && <Share2 className="w-4 h-4 text-purple-600" />}
                    {activity.type === 'download' && <Download className="w-4 h-4 text-orange-600" />}
                    {activity.type === 'delete' && <File className="w-4 h-4 text-red-600" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      {activity.action} {activity.file}
                    </p>
                    <p className="text-xs text-gray-500">by {activity.user}</p>
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
export default GoogleDriveIntegration;