import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Search, 
  Filter, 
  Download, 
  Calendar, 
  User,
  Activity,
  Shield,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  Eye,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';
const eventTypes = [
  { value: 'all', label: 'All Events' },
  { value: 'auth', label: 'Authentication' },
  { value: 'user', label: 'User Management' },
  { value: 'data', label: 'Data Access' },
  { value: 'admin', label: 'Admin Actions' },
  { value: 'system', label: 'System Events' },
  { value: 'security', label: 'Security Events' }
];
const severityLevels = [
  { value: 'all', label: 'All Levels', color: 'gray' },
  { value: 'info', label: 'Info', color: 'blue' },
  { value: 'warning', label: 'Warning', color: 'yellow' },
  { value: 'error', label: 'Error', color: 'red' },
  { value: 'critical', label: 'Critical', color: 'purple' }
];
const AuditLogsPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    eventType: 'all',
    severity: 'all',
    userId: '',
    dateFrom: '',
    dateTo: '',
    page: 1,
    limit: 20
  });
  const [stats, setStats] = useState({
    total: 0,
    byType: {},
    bySeverity: {},
    recentActivity: []
  });
  const [selectedLog, setSelectedLog] = useState(null);
  const [exportFormat, setExportFormat] = useState('csv');
  const [autoRefresh, setAutoRefresh] = useState(false);
  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [filters]);
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);
  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== 'all') {
          params.append(key, value);
        }
      });
      const response = await fetch(`/api/admin/audit-logs?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchStats = async () => {
    try {
      const response = await fetch('/api/admin/audit-logs/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };
  const exportLogs = async () => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== 'all') {
          params.append(key, value);
        }
      });
      params.append('format', exportFormat);
      const response = await fetch(`/api/admin/audit-logs/export?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit-logs-${new Date().toISOString()}.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showToast('Logs exported successfully', 'success');
      }
    } catch (error) {
      showToast('Error exporting logs', 'error');
    }
  };
  // Spinner component definition
  const Spinner = () => (
    <div className="flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  );
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'info':
        return <CheckCircle className="w-4 h-4 text-blue-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'critical':
        return <Shield className="w-4 h-4 text-purple-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };
  const getEventTypeIcon = (type) => {
    switch (type) {
      case 'auth':
        return <Shield className="w-4 h-4" />;
      case 'user':
        return <User className="w-4 h-4" />;
      case 'data':
        return <Database className="w-4 h-4" />;
      case 'admin':
        return <Activity className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };
  const renderFilters = () => (
    <Card className="mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium mb-1">Search</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              className="w-full pl-10 pr-3 py-2 border rounded-lg"
              placeholder="Search logs..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
        </div>
        {/* Event Type */}
        <div>
          <label className="block text-sm font-medium mb-1">Event Type</label>
          <select
            className="w-full p-2 border rounded-lg"
            value={filters.eventType}
            onChange={(e) => setFilters({ ...filters, eventType: e.target.value })}
          >
            {eventTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>
        {/* Severity */}
        <div>
          <label className="block text-sm font-medium mb-1">Severity</label>
          <select
            className="w-full p-2 border rounded-lg"
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
          >
            {severityLevels.map(level => (
              <option key={level.value} value={level.value}>{level.label}</option>
            ))}
          </select>
        </div>
        {/* User ID */}
        <div>
          <label className="block text-sm font-medium mb-1">User ID</label>
          <input
            type="text"
            className="w-full p-2 border rounded-lg"
            placeholder="Filter by user ID"
            value={filters.userId}
            onChange={(e) => setFilters({ ...filters, userId: e.target.value })}
          />
        </div>
        {/* Date From */}
        <div>
          <label className="block text-sm font-medium mb-1">From Date</label>
          <input
            type="datetime-local"
            className="w-full p-2 border rounded-lg"
            value={filters.dateFrom}
            onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
          />
        </div>
        {/* Date To */}
        <div>
          <label className="block text-sm font-medium mb-1">To Date</label>
          <input
            type="datetime-local"
            className="w-full p-2 border rounded-lg"
            value={filters.dateTo}
            onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
          />
        </div>
        {/* Export Format */}
        <div>
          <label className="block text-sm font-medium mb-1">Export Format</label>
          <select
            className="w-full p-2 border rounded-lg"
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
        {/* Actions */}
        <div className="flex items-end space-x-2">
          <Button onClick={fetchLogs} disabled={loading}>
            <Search className="w-4 h-4 mr-2" />
            Search
          </Button>
          <Button variant="secondary" onClick={exportLogs}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
    </Card>
  );
  const renderStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <Card>
        <h3 className="font-medium mb-2">Total Events</h3>
        <p className="text-2xl font-bold">{stats.total.toLocaleString()}</p>
        <p className="text-sm text-gray-600">Last 30 days</p>
      </Card>
      <Card>
        <h3 className="font-medium mb-2">Security Events</h3>
        <p className="text-2xl font-bold text-red-600">
          {stats.bySeverity?.critical || 0}
        </p>
        <p className="text-sm text-gray-600">Critical severity</p>
      </Card>
      <Card>
        <h3 className="font-medium mb-2">Most Active</h3>
        <p className="text-2xl font-bold">{Object.keys(stats.byType)[0] || 'N/A'}</p>
        <p className="text-sm text-gray-600">Event type</p>
      </Card>
      <Card>
        <h3 className="font-medium mb-2">Auto-Refresh</h3>
        <label className="relative inline-flex items-center cursor-pointer mt-2">
          <input
            type="checkbox"
            className="sr-only peer"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
        </label>
        <p className="text-sm text-gray-600 mt-1">Every 30 seconds</p>
      </Card>
    </div>
  );
  const renderLogs = () => (
    <Card>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {logs.map(log => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span>{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">
                  <div className="flex items-center space-x-2">
                    {getEventTypeIcon(log.type)}
                    <span className="font-medium">{log.event}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">
                  <div className="flex items-center space-x-2">
                    <User className="w-3 h-3 text-gray-400" />
                    <span>{log.user_id || 'System'}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">{log.ip_address || 'N/A'}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-1">
                    {getSeverityIcon(log.severity)}
                    <span className={`text-xs font-medium
                      ${log.severity === 'info' ? 'text-blue-600' :
                        log.severity === 'warning' ? 'text-yellow-600' :
                        log.severity === 'error' ? 'text-red-600' :
                        log.severity === 'critical' ? 'text-purple-600' :
                        'text-gray-600'}`}>
                      {log.severity}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setSelectedLog(log)}
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Pagination */}
      <div className="flex justify-between items-center mt-4">
        <p className="text-sm text-gray-600">
          Showing {logs.length} of {stats.total} logs
        </p>
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
            disabled={filters.page === 1}
          >
            Previous
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
            disabled={logs.length < filters.limit}
          >
            Next
          </Button>
        </div>
      </div>
    </Card>
  );
  const renderLogDetail = () => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <h3 className="font-semibold text-lg">Log Details</h3>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setSelectedLog(null)}
          >
            <XCircle className="w-4 h-4" />
          </Button>
        </div>
        {selectedLog && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Timestamp</p>
                <p className="text-sm">{new Date(selectedLog.timestamp).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Event Type</p>
                <p className="text-sm">{selectedLog.type}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">User ID</p>
                <p className="text-sm">{selectedLog.user_id || 'System'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">IP Address</p>
                <p className="text-sm">{selectedLog.ip_address || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">User Agent</p>
                <p className="text-sm">{selectedLog.user_agent || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Severity</p>
                <p className="text-sm">{selectedLog.severity}</p>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Event</p>
              <p className="text-sm">{selectedLog.event}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Description</p>
              <p className="text-sm">{selectedLog.description}</p>
            </div>
            {selectedLog.metadata && (
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Metadata</p>
                <pre className="text-sm bg-gray-50 p-3 rounded overflow-x-auto">
                  {JSON.stringify(selectedLog.metadata, null, 2)}
                </pre>
              </div>
            )}
            {selectedLog.error && (
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Error Details</p>
                <pre className="text-sm bg-red-50 p-3 rounded overflow-x-auto text-red-700">
                  {JSON.stringify(selectedLog.error, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Audit Logs</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary"
        >
          Back to Settings
        </Button>
      </div>
      {renderStats()}
      {renderFilters()}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        renderLogs()
      )}
      {selectedLog && renderLogDetail()}
    </div>
  );
};
export default AuditLogsPage;