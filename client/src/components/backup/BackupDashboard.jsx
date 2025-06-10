import React, { useState, useEffect, useCallback } from 'react';
import { 
  Database, 
  Download, 
  Upload, 
  Clock, 
  Calendar,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Settings,
  Play,
  Pause,
  Trash2,
  Shield,
  HardDrive,
  Archive,
  History,
  Save
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ResponsiveContainer, ResponsiveGrid, ResponsiveCard } from '@/components/responsive/ResponsiveContainer';
import { cn } from '@/lib/utils';
import api from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

const BackupDashboard = () => {
  const [backupHistory, setBackupHistory] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [recoveryPoints, setRecoveryPoints] = useState([]);
  const [backupStatus, setBackupStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingBackup, setIsCreatingBackup] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState(null);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  const fetchBackupData = useCallback(async () => {
    try {
      const [historyRes, schedulesRes, recoveryRes, statusRes] = await Promise.all([
        api.get('/api/v2/backup/history'),
        api.get('/api/v2/backup/schedules'),
        api.get('/api/v2/backup/recovery-points'),
        api.get('/api/v2/backup/status')
      ]);

      setBackupHistory(historyRes.data.backups || []);
      setSchedules(schedulesRes.data.schedules || []);
      setRecoveryPoints(recoveryRes.data.recovery_points || []);
      setBackupStatus(statusRes.data.status);
    } catch (error) {
      console.error('Failed to fetch backup data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBackupData();
  }, [fetchBackupData]);

  const createBackup = async (backupType = 'full') => {
    setIsCreatingBackup(true);
    try {
      const response = await api.post('/api/v2/backup/create', {
        backup_type: backupType,
        description: `Manual ${backupType} backup`,
        include_files: true,
        notify: true
      });

      if (response.data.success) {
        await fetchBackupData();
        // Show success notification
      }
    } catch (error) {
      console.error('Failed to create backup:', error);
      // Show error notification
    } finally {
      setIsCreatingBackup(false);
    }
  };

  const restoreBackup = async (backupId, restorePoint) => {
    try {
      const response = await api.post('/api/v2/backup/restore', {
        backup_id: backupId,
        restore_point: restorePoint,
        restore_database: true,
        restore_files: true
      });

      if (response.data.success) {
        setShowRestoreModal(false);
        // Show success notification
      }
    } catch (error) {
      console.error('Failed to restore backup:', error);
      // Show error notification
    }
  };

  const downloadBackup = async (backupId) => {
    try {
      const response = await api.get(`/api/v2/backup/download/${backupId}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${backupId}.tar.gz`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download backup:', error);
    }
  };

  const toggleSchedule = async (scheduleName, enabled) => {
    try {
      await api.put(`/api/v2/backup/schedules/${scheduleName}`, { enabled });
      await fetchBackupData();
    } catch (error) {
      console.error('Failed to update schedule:', error);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <ResponsiveContainer>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <RefreshCw className="h-6 w-6 animate-spin" />
            <span>Loading backup data...</span>
          </div>
        </div>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Backup & Recovery</h1>
            <p className="text-sm text-gray-500">
              Manage backups, restore points, and recovery operations
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowScheduleModal(true)}
            >
              <Calendar className="h-4 w-4 mr-2" />
              Manage Schedules
            </Button>
            
            <Button
              variant="primary"
              onClick={() => createBackup('full')}
              disabled={isCreatingBackup}
            >
              {isCreatingBackup ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Creating Backup...
                </>
              ) : (
                <>
                  <Database className="h-4 w-4 mr-2" />
                  Create Backup
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Status Overview */}
        <ResponsiveGrid cols={{ default: 1, sm: 2, lg: 4 }}>
          {/* Total Backups */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Backups</p>
                  <p className="text-2xl font-bold">{backupStatus?.total_backups || 0}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {backupStatus?.successful_backups || 0} successful
                  </p>
                </div>
                <Database className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Storage Used */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Storage Used</p>
                  <p className="text-2xl font-bold">
                    {backupStatus?.total_size_mb ? `${backupStatus.total_size_mb} MB` : '0 MB'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {backupStatus?.storage_type || 'local'}
                  </p>
                </div>
                <HardDrive className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Last Backup */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Last Backup</p>
                  <p className="text-lg font-bold">
                    {backupStatus?.last_backup ? 
                      formatDistanceToNow(new Date(backupStatus.last_backup.timestamp), { addSuffix: true }) :
                      'Never'
                    }
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {backupStatus?.last_backup?.status || 'N/A'}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </ResponsiveCard>

          {/* Next Scheduled */}
          <ResponsiveCard>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Next Scheduled</p>
                  <p className="text-lg font-bold">
                    {backupStatus?.next_scheduled_backup ? 
                      formatDistanceToNow(new Date(backupStatus.next_scheduled_backup), { addSuffix: true }) :
                      'Not scheduled'
                    }
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {backupStatus?.scheduler_running ? 'Scheduler active' : 'Scheduler inactive'}
                  </p>
                </div>
                <Calendar className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </ResponsiveCard>
        </ResponsiveGrid>

        {/* Backup Schedules */}
        <ResponsiveCard>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Backup Schedules</span>
              </div>
              <Badge variant="outline">{schedules.length} schedules</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {schedules.map((schedule) => (
                <div
                  key={schedule.name}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className={cn(
                      'w-2 h-2 rounded-full',
                      schedule.enabled ? 'bg-green-500' : 'bg-gray-300'
                    )} />
                    <div>
                      <p className="font-medium">{schedule.name}</p>
                      <p className="text-sm text-gray-600">
                        {schedule.backup_type} backup • {schedule.frequency} at {schedule.time}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {schedule.last_run && (
                      <span className="text-xs text-gray-500">
                        Last: {formatDistanceToNow(new Date(schedule.last_run), { addSuffix: true })}
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSchedule(schedule.name, !schedule.enabled)}
                    >
                      {schedule.enabled ? (
                        <Pause className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              ))}
              
              {schedules.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No backup schedules configured
                </div>
              )}
            </div>
          </CardContent>
        </ResponsiveCard>

        {/* Backup History */}
        <ResponsiveCard>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <History className="h-5 w-5" />
              <span>Backup History</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Backup ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {backupHistory.map((backup) => (
                    <tr key={backup.backup_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Archive className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm font-medium text-gray-900">
                            {backup.backup_id}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant="outline">{backup.type}</Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {backup.size_mb} MB
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDistanceToNow(new Date(backup.timestamp), { addSuffix: true })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge
                          variant={backup.status === 'completed' ? 'success' : 
                                  backup.status === 'failed' ? 'destructive' : 'warning'}
                        >
                          {backup.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => {
                              setSelectedBackup(backup);
                              setShowRestoreModal(true);
                            }}
                            className="text-blue-600 hover:text-blue-900"
                            disabled={backup.status !== 'completed'}
                          >
                            <Upload className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => downloadBackup(backup.backup_id)}
                            className="text-green-600 hover:text-green-900"
                            disabled={backup.status !== 'completed'}
                          >
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {backupHistory.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No backups found
                </div>
              )}
            </div>
          </CardContent>
        </ResponsiveCard>

        {/* Recovery Points */}
        <ResponsiveCard>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5" />
              <span>Recovery Points</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recoveryPoints.map((point) => (
                <div
                  key={point.backup_id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div>
                    <p className="font-medium">{point.backup_id}</p>
                    <p className="text-sm text-gray-600">
                      {point.type} backup • {point.size_mb} MB
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Recovery range: {new Date(point.can_restore_to.start).toLocaleDateString()} - 
                      {new Date(point.can_restore_to.end).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedBackup(point);
                      setShowRestoreModal(true);
                    }}
                  >
                    Restore
                  </Button>
                </div>
              ))}
              
              {recoveryPoints.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No recovery points available
                </div>
              )}
            </div>
          </CardContent>
        </ResponsiveCard>
      </div>

      {/* Restore Modal */}
      {showRestoreModal && selectedBackup && (
        <RestoreModal
          backup={selectedBackup}
          onClose={() => setShowRestoreModal(false)}
          onRestore={restoreBackup}
        />
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
        <ScheduleModal
          schedules={schedules}
          onClose={() => setShowScheduleModal(false)}
          onRefresh={fetchBackupData}
        />
      )}
    </ResponsiveContainer>
  );
};

// Restore Modal Component
const RestoreModal = ({ backup, onClose, onRestore }) => {
  const [restorePoint, setRestorePoint] = useState('');
  const [isRestoring, setIsRestoring] = useState(false);

  const handleRestore = async () => {
    setIsRestoring(true);
    try {
      await onRestore(backup.backup_id, restorePoint || null);
    } finally {
      setIsRestoring(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Restore Backup</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Backup ID
              </label>
              <p className="text-sm text-gray-900">{backup.backup_id}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Restore Point (Optional)
              </label>
              <input
                type="datetime-local"
                value={restorePoint}
                onChange={(e) => setRestorePoint(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Leave empty for latest"
              />
              <p className="text-xs text-gray-500 mt-1">
                Specify a point in time to restore to, or leave empty to restore the full backup
              </p>
            </div>
            
            <div className="bg-yellow-50 p-3 rounded-lg">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">Warning</p>
                  <p className="text-xs text-yellow-700 mt-1">
                    This will restore the database and files to the selected backup state. 
                    Current data will be overwritten. This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end space-x-2 mt-6">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleRestore}
              disabled={isRestoring}
            >
              {isRestoring ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Restoring...
                </>
              ) : (
                'Restore Backup'
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Schedule Modal Component
const ScheduleModal = ({ schedules, onClose, onRefresh }) => {
  const [name, setName] = useState('');
  const [backupType, setBackupType] = useState('full');
  const [frequency, setFrequency] = useState('daily');
  const [time, setTime] = useState('02:00');
  const [retentionDays, setRetentionDays] = useState(7);
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = async () => {
    setIsCreating(true);
    try {
      await api.post('/api/v2/backup/schedules', {
        name,
        backup_type: backupType,
        frequency,
        time,
        retention_days: retentionDays
      });
      
      await onRefresh();
      onClose();
    } catch (error) {
      console.error('Failed to create schedule:', error);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Manage Backup Schedules</h3>
          
          {/* Create New Schedule */}
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <h4 className="font-medium mb-3">Create New Schedule</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Schedule Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., daily_backup"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Backup Type
                </label>
                <select
                  value={backupType}
                  onChange={(e) => setBackupType(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="full">Full</option>
                  <option value="incremental">Incremental</option>
                  <option value="differential">Differential</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Frequency
                </label>
                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time
                </label>
                <input
                  type="time"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Retention Days
                </label>
                <input
                  type="number"
                  value={retentionDays}
                  onChange={(e) => setRetentionDays(parseInt(e.target.value))}
                  min="1"
                  max="365"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-end">
                <Button
                  onClick={handleCreate}
                  disabled={isCreating || !name}
                  className="w-full"
                >
                  {isCreating ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Create Schedule
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
          
          {/* Existing Schedules */}
          <div>
            <h4 className="font-medium mb-3">Existing Schedules</h4>
            <div className="space-y-2">
              {schedules.map((schedule) => (
                <div
                  key={schedule.name}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{schedule.name}</p>
                    <p className="text-sm text-gray-600">
                      {schedule.backup_type} • {schedule.frequency} • {schedule.retention_days} days retention
                    </p>
                  </div>
                  
                  <button
                    onClick={async () => {
                      try {
                        await api.delete(`/api/v2/backup/schedules/${schedule.name}`);
                        await onRefresh();
                      } catch (error) {
                        console.error('Failed to delete schedule:', error);
                      }
                    }}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex justify-end mt-6">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BackupDashboard;