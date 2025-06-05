import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Save, 
  Download, 
  Upload, 
  Calendar, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Archive,
  RefreshCw,
  Settings,
  FolderOpen,
  Database,
  Cloud,
  HardDrive,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';
const backupTypes = [
  { id: 'full', name: 'Full Backup', description: 'Complete system backup including all data' },
  { id: 'incremental', name: 'Incremental Backup', description: 'Only changed data since last backup' },
  { id: 'differential', name: 'Differential Backup', description: 'All changes since last full backup' },
  { id: 'selective', name: 'Selective Backup', description: 'Backup specific modules or data types' }
];
const storageLocations = [
  { id: 'local', name: 'Local Storage', icon: HardDrive, available: true },
  { id: 'cloud', name: 'Cloud Storage', icon: Cloud, available: true },
  { id: 'network', name: 'Network Drive', icon: Database, available: false },
  { id: 'external', name: 'External Drive', icon: Archive, available: false }
];
const DataBackupPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [backups, setBackups] = useState([]);
  const [backupSettings, setBackupSettings] = useState({
    autoBackup: true,
    frequency: 'daily',
    retention: 30,
    compression: true,
    encryption: true,
    storageLocation: 'cloud',
    includeLogs: true,
    includeMedia: true,
    notifyOnCompletion: true,
    notifyOnFailure: true
  });
  const [selectedModules, setSelectedModules] = useState({
    users: true,
    beneficiaries: true,
    programs: true,
    tests: true,
    documents: true,
    messages: false,
    analytics: false,
    settings: true
  });
  const [backupProgress, setBackupProgress] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  useEffect(() => {
    fetchBackups();
    fetchBackupSettings();
  }, []);
  const fetchBackups = async () => {
    try {
      const response = await fetch('/api/admin/backups', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setBackups(data.backups || []);
      }
    } catch (error) {
      console.error('Error fetching backups:', error);
    }
  };
  const fetchBackupSettings = async () => {
    try {
      const response = await fetch('/api/admin/backup-settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setBackupSettings(data.settings);
      }
    } catch (error) {
      console.error('Error fetching backup settings:', error);
    }
  };
  const createBackup = async (type = 'manual') => {
    setLoading(true);
    setBackupProgress(0);
    try {
      const response = await fetch('/api/admin/backups/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          type,
          modules: selectedModules,
          settings: backupSettings
        })
      });
      if (response.ok) {
        // Simulate progress
        const progressInterval = setInterval(() => {
          setBackupProgress(prev => {
            if (prev >= 100) {
              clearInterval(progressInterval);
              showToast('Backup completed successfully', 'success');
              fetchBackups();
              setBackupProgress(null);
              return 100;
            }
            return prev + 10;
          });
        }, 500);
      } else {
        showToast('Failed to create backup', 'error');
        setBackupProgress(null);
      }
    } catch (error) {
      showToast('Error creating backup', 'error');
      setBackupProgress(null);
    } finally {
      setLoading(false);
    }
  };
  const restoreBackup = async (backupId) => {
    if (!confirm('Are you sure you want to restore this backup? This will overwrite current data.')) {
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`/api/admin/backups/${backupId}/restore`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        showToast('Restore initiated successfully', 'success');
        // In a real app, would show restore progress
      } else {
        showToast('Failed to restore backup', 'error');
      }
    } catch (error) {
      showToast('Error restoring backup', 'error');
    } finally {
      setLoading(false);
    }
  };
  const downloadBackup = async (backupId) => {
    try {
      const response = await fetch(`/api/admin/backups/${backupId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backup-${backupId}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      showToast('Error downloading backup', 'error');
    }
  };
  const updateSettings = async (newSettings) => {
    try {
      const response = await fetch('/api/admin/backup-settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newSettings)
      });
      if (response.ok) {
        setBackupSettings(newSettings);
        showToast('Settings updated successfully', 'success');
      }
    } catch (error) {
      showToast('Error updating settings', 'error');
    }
  };
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <h3 className="font-medium mb-2">Create Backup</h3>
          <p className="text-sm text-gray-600 mb-4">Run a manual backup now</p>
          <Button 
            onClick={() => createBackup('manual')}
            disabled={loading}
            className="w-full"
          >
            <Save className="w-4 h-4 mr-2" />
            Backup Now
          </Button>
        </Card>
        <Card>
          <h3 className="font-medium mb-2">Last Backup</h3>
          <p className="text-sm text-gray-600 mb-2">
            {backups[0] ? new Date(backups[0].created_at).toLocaleString() : 'No backups yet'}
          </p>
          <p className="text-sm">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
              ${backups[0]?.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
              {backups[0]?.status || 'No backup'}
            </span>
          </p>
        </Card>
        <Card>
          <h3 className="font-medium mb-2">Auto-Backup</h3>
          <p className="text-sm text-gray-600 mb-4">
            {backupSettings.autoBackup ? 'Enabled' : 'Disabled'}
          </p>
          <Button
            variant={backupSettings.autoBackup ? 'secondary' : 'primary'}
            onClick={() => updateSettings({ ...backupSettings, autoBackup: !backupSettings.autoBackup })}
            className="w-full"
          >
            {backupSettings.autoBackup ? 'Disable' : 'Enable'} Auto-Backup
          </Button>
        </Card>
      </div>
      {/* Backup Progress */}
      {backupProgress !== null && (
        <Card>
          <h3 className="font-medium mb-4">Backup Progress</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Creating backup...</span>
              <span>{backupProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${backupProgress}%` }}
              />
            </div>
          </div>
        </Card>
      )}
      {/* Recent Backups */}
      <Card>
        <h3 className="font-medium mb-4">Recent Backups</h3>
        {backups.length === 0 ? (
          <p className="text-gray-600">No backups found</p>
        ) : (
          <div className="space-y-3">
            {backups.slice(0, 5).map(backup => (
              <div key={backup.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  {backup.status === 'completed' ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                  )}
                  <div>
                    <p className="font-medium">{backup.type} Backup</p>
                    <p className="text-sm text-gray-600">
                      {new Date(backup.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{backup.size}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => downloadBackup(backup.id)}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => restoreBackup(backup.id)}
                  >
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
  const renderSettings = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="font-medium mb-4">Backup Configuration</h3>
        <div className="space-y-4">
          {/* Auto-backup */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Automatic Backups</p>
              <p className="text-sm text-gray-600">Enable scheduled backups</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={backupSettings.autoBackup}
                onChange={(e) => updateSettings({ ...backupSettings, autoBackup: e.target.checked })}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Frequency */}
          <div>
            <label className="block text-sm font-medium mb-1">Backup Frequency</label>
            <select
              className="w-full p-2 border rounded-lg"
              value={backupSettings.frequency}
              onChange={(e) => updateSettings({ ...backupSettings, frequency: e.target.value })}
              disabled={!backupSettings.autoBackup}
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          {/* Retention */}
          <div>
            <label className="block text-sm font-medium mb-1">Retention Period (days)</label>
            <input
              type="number"
              className="w-full p-2 border rounded-lg"
              value={backupSettings.retention}
              onChange={(e) => updateSettings({ ...backupSettings, retention: parseInt(e.target.value) })}
              min="1"
              max="365"
            />
          </div>
          {/* Compression */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Compression</p>
              <p className="text-sm text-gray-600">Reduce backup size</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={backupSettings.compression}
                onChange={(e) => updateSettings({ ...backupSettings, compression: e.target.checked })}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Encryption */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Encryption</p>
              <p className="text-sm text-gray-600">Secure backups with encryption</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={backupSettings.encryption}
                onChange={(e) => updateSettings({ ...backupSettings, encryption: e.target.checked })}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
        </div>
      </Card>
      {/* Storage Location */}
      <Card>
        <h3 className="font-medium mb-4">Storage Location</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {storageLocations.map(location => (
            <div
              key={location.id}
              className={`p-4 border rounded-lg cursor-pointer transition-all ${
                backupSettings.storageLocation === location.id
                  ? 'border-primary bg-primary/5'
                  : 'border-gray-200 hover:border-gray-300'
              } ${!location.available ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => location.available && updateSettings({ ...backupSettings, storageLocation: location.id })}
            >
              <div className="flex items-center space-x-3">
                <location.icon className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium">{location.name}</p>
                  {!location.available && (
                    <p className="text-xs text-gray-500">Not available</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
      {/* Modules Selection */}
      <Card>
        <h3 className="font-medium mb-4">Modules to Backup</h3>
        <div className="space-y-3">
          {Object.entries(selectedModules).map(([module, included]) => (
            <div key={module} className="flex items-center justify-between">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="mr-3"
                  checked={included}
                  onChange={(e) => setSelectedModules({
                    ...selectedModules,
                    [module]: e.target.checked
                  })}
                />
                <span className="capitalize">{module}</span>
              </label>
            </div>
          ))}
        </div>
      </Card>
      {/* Notifications */}
      <Card>
        <h3 className="font-medium mb-4">Notification Settings</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="mr-3"
                checked={backupSettings.notifyOnCompletion}
                onChange={(e) => updateSettings({
                  ...backupSettings,
                  notifyOnCompletion: e.target.checked
                })}
              />
              <span>Notify on backup completion</span>
            </label>
          </div>
          <div className="flex items-center justify-between">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="mr-3"
                checked={backupSettings.notifyOnFailure}
                onChange={(e) => updateSettings({
                  ...backupSettings,
                  notifyOnFailure: e.target.checked
                })}
              />
              <span>Notify on backup failure</span>
            </label>
          </div>
        </div>
      </Card>
    </div>
  );
  // Spinner component definition
  const Spinner = () => (
    <div className="flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  );
  const renderHistory = () => (
    <Card>
      <h3 className="font-medium mb-4">Backup History</h3>
      {backups.length === 0 ? (
        <p className="text-gray-600">No backups found</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {backups.map(backup => (
                <tr key={backup.id}>
                  <td className="px-4 py-3 text-sm">
                    {new Date(backup.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm capitalize">{backup.type}</td>
                  <td className="px-4 py-3 text-sm">{backup.size}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                      ${backup.status === 'completed' ? 'bg-green-100 text-green-800' : 
                        backup.status === 'failed' ? 'bg-red-100 text-red-800' : 
                        'bg-yellow-100 text-yellow-800'}`}>
                      {backup.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">{backup.duration || 'N/A'}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => downloadBackup(backup.id)}
                        disabled={backup.status !== 'completed'}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => restoreBackup(backup.id)}
                        disabled={backup.status !== 'completed'}
                      >
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Data Backup System</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary"
        >
          Back to Settings
        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'settings', 'history'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>
      {/* Tab Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'settings' && renderSettings()}
          {activeTab === 'history' && renderHistory()}
        </>
      )}
    </div>
  );
};
export default DataBackupPage;