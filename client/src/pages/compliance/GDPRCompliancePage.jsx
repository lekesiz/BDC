import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Modal } from '../../components/ui/modal';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import {
  Loader2,
  Shield,
  Download,
  Trash2,
  AlertTriangle,
  CheckCircle,
  FileText,
  Lock,
  User,
  Settings,
  Eye,
  EyeOff,
  Copy,
  ClipboardCheck
} from 'lucide-react';
const GDPRCompliancePage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [personalData, setPersonalData] = useState(null);
  const [dataDeletionRequests, setDataDeletionRequests] = useState([]);
  const [consentHistory, setConsentHistory] = useState([]);
  const [privacySettings, setPrivacySettings] = useState({
    data_collection: true,
    analytics_tracking: true,
    marketing_emails: false,
    third_party_sharing: false
  });
  const [showDataExport, setShowDataExport] = useState(false);
  const [showDataDeletion, setShowDataDeletion] = useState(false);
  const [showAccessLog, setShowAccessLog] = useState(false);
  const [accessLog, setAccessLog] = useState([]);
  const [deletionReason, setDeletionReason] = useState('');
  useEffect(() => {
    fetchPersonalData();
    fetchDataDeletionRequests();
    fetchConsentHistory();
    fetchPrivacySettings();
  }, []);
  const fetchPersonalData = async () => {
    try {
      const res = await fetch('/api/gdpr/personal-data', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch personal data');
      const data = await res.json();
      setPersonalData(data);
    } catch (error) {
      console.error('Error fetching personal data:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch personal data',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const fetchDataDeletionRequests = async () => {
    try {
      const res = await fetch('/api/gdpr/deletion-requests', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch deletion requests');
      const data = await res.json();
      setDataDeletionRequests(data);
    } catch (error) {
      console.error('Error fetching deletion requests:', error);
    }
  };
  const fetchConsentHistory = async () => {
    try {
      const res = await fetch('/api/gdpr/consent-history', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch consent history');
      const data = await res.json();
      setConsentHistory(data);
    } catch (error) {
      console.error('Error fetching consent history:', error);
    }
  };
  const fetchPrivacySettings = async () => {
    try {
      const res = await fetch('/api/gdpr/privacy-settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch privacy settings');
      const data = await res.json();
      setPrivacySettings(data);
    } catch (error) {
      console.error('Error fetching privacy settings:', error);
    }
  };
  const fetchAccessLog = async () => {
    try {
      const res = await fetch('/api/gdpr/access-log', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch access log');
      const data = await res.json();
      setAccessLog(data);
    } catch (error) {
      console.error('Error fetching access log:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch access log',
        variant: 'destructive'
      });
    }
  };
  const handleDataExport = async (format) => {
    try {
      const res = await fetch(`/api/gdpr/export-data?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to export data');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `personal_data_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast({
        title: 'Success',
        description: 'Personal data exported successfully'
      });
      setShowDataExport(false);
    } catch (error) {
      console.error('Error exporting data:', error);
      toast({
        title: 'Error',
        description: 'Failed to export personal data',
        variant: 'destructive'
      });
    }
  };
  const handleDataDeletion = async () => {
    if (!deletionReason.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a reason for data deletion',
        variant: 'destructive'
      });
      return;
    }
    try {
      const res = await fetch('/api/gdpr/request-deletion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ reason: deletionReason })
      });
      if (!res.ok) throw new Error('Failed to request data deletion');
      toast({
        title: 'Success',
        description: 'Data deletion request submitted successfully'
      });
      setShowDataDeletion(false);
      setDeletionReason('');
      fetchDataDeletionRequests();
    } catch (error) {
      console.error('Error requesting data deletion:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit deletion request',
        variant: 'destructive'
      });
    }
  };
  const handlePrivacySettingsUpdate = async (setting, value) => {
    const updatedSettings = { ...privacySettings, [setting]: value };
    setPrivacySettings(updatedSettings);
    try {
      const res = await fetch('/api/gdpr/privacy-settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(updatedSettings)
      });
      if (!res.ok) throw new Error('Failed to update privacy settings');
      toast({
        title: 'Success',
        description: 'Privacy settings updated successfully'
      });
    } catch (error) {
      console.error('Error updating privacy settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to update privacy settings',
        variant: 'destructive'
      });
    }
  };
  const handleAnonymizeData = async () => {
    if (!confirm('Are you sure you want to anonymize your data? This action cannot be undone.')) {
      return;
    }
    try {
      const res = await fetch('/api/gdpr/anonymize', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to anonymize data');
      toast({
        title: 'Success',
        description: 'Data anonymized successfully'
      });
      fetchPersonalData();
    } catch (error) {
      console.error('Error anonymizing data:', error);
      toast({
        title: 'Error',
        description: 'Failed to anonymize data',
        variant: 'destructive'
      });
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
        <div className="flex items-center gap-3">
          <Shield className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">GDPR Compliance</h1>
        </div>
      </div>
      {/* GDPR Rights Overview */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Your GDPR Rights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Eye className="h-5 w-5 text-blue-600" />
              <h3 className="font-medium">Right to Access</h3>
            </div>
            <p className="text-sm text-gray-600">View all personal data we hold about you</p>
          </div>
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Download className="h-5 w-5 text-green-600" />
              <h3 className="font-medium">Right to Portability</h3>
            </div>
            <p className="text-sm text-gray-600">Export your data in standard formats</p>
          </div>
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Trash2 className="h-5 w-5 text-red-600" />
              <h3 className="font-medium">Right to Erasure</h3>
            </div>
            <p className="text-sm text-gray-600">Request deletion of your personal data</p>
          </div>
          <div className="border rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <Settings className="h-5 w-5 text-purple-600" />
              <h3 className="font-medium">Right to Control</h3>
            </div>
            <p className="text-sm text-gray-600">Manage how your data is processed</p>
          </div>
        </div>
      </Card>
      {/* Personal Data Overview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Personal Data Overview</h2>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDataExport(true)}
            >
              <Download className="h-4 w-4 mr-2" />
              Export Data
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAccessLog(true)}
            >
              <Eye className="h-4 w-4 mr-2" />
              Access Log
            </Button>
          </div>
        </div>
        {personalData && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-700">Name</p>
                <p className="text-gray-900">{personalData.name}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Email</p>
                <p className="text-gray-900">{personalData.email}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Account Created</p>
                <p className="text-gray-900">{new Date(personalData.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Last Updated</p>
                <p className="text-gray-900">{new Date(personalData.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Data Categories Collected</p>
              <div className="flex flex-wrap gap-2">
                {personalData.data_categories.map((category) => (
                  <Badge key={category} variant="secondary">
                    {category}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}
      </Card>
      {/* Privacy Settings */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Privacy Settings</h2>
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Data Collection</p>
              <p className="text-sm text-gray-600">Allow collection of usage data for service improvement</p>
            </div>
            <input
              type="checkbox"
              checked={privacySettings.data_collection}
              onChange={(e) => handlePrivacySettingsUpdate('data_collection', e.target.checked)}
              className="rounded text-primary h-5 w-5"
            />
          </label>
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Analytics Tracking</p>
              <p className="text-sm text-gray-600">Enable analytics to help us understand usage patterns</p>
            </div>
            <input
              type="checkbox"
              checked={privacySettings.analytics_tracking}
              onChange={(e) => handlePrivacySettingsUpdate('analytics_tracking', e.target.checked)}
              className="rounded text-primary h-5 w-5"
            />
          </label>
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Marketing Emails</p>
              <p className="text-sm text-gray-600">Receive emails about new features and updates</p>
            </div>
            <input
              type="checkbox"
              checked={privacySettings.marketing_emails}
              onChange={(e) => handlePrivacySettingsUpdate('marketing_emails', e.target.checked)}
              className="rounded text-primary h-5 w-5"
            />
          </label>
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Third-party Sharing</p>
              <p className="text-sm text-gray-600">Share anonymized data with research partners</p>
            </div>
            <input
              type="checkbox"
              checked={privacySettings.third_party_sharing}
              onChange={(e) => handlePrivacySettingsUpdate('third_party_sharing', e.target.checked)}
              className="rounded text-primary h-5 w-5"
            />
          </label>
        </div>
      </Card>
      {/* Data Management Actions */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Data Management</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <h3 className="font-medium">Anonymize Personal Data</h3>
              <p className="text-sm text-gray-600">Replace identifiable information with anonymous identifiers</p>
            </div>
            <Button
              variant="outline"
              onClick={handleAnonymizeData}
            >
              <EyeOff className="h-4 w-4 mr-2" />
              Anonymize
            </Button>
          </div>
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <h3 className="font-medium">Request Data Deletion</h3>
              <p className="text-sm text-gray-600">Submit a request to permanently delete your data</p>
            </div>
            <Button
              variant="destructive"
              onClick={() => setShowDataDeletion(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Request Deletion
            </Button>
          </div>
        </div>
      </Card>
      {/* Consent History */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Consent History</h2>
        {consentHistory.length === 0 ? (
          <p className="text-gray-500">No consent history available</p>
        ) : (
          <div className="space-y-3">
            {consentHistory.map((consent) => (
              <div key={consent.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">{consent.type}</p>
                  <p className="text-sm text-gray-600">
                    {consent.granted ? 'Granted' : 'Revoked'} on {new Date(consent.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <Badge variant={consent.granted ? 'success' : 'secondary'}>
                  {consent.granted ? 'Active' : 'Revoked'}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
      {/* Deletion Requests */}
      {dataDeletionRequests.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Data Deletion Requests</h2>
          <div className="space-y-3">
            {dataDeletionRequests.map((request) => (
              <div key={request.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">Request #{request.id}</p>
                  <p className="text-sm text-gray-600">
                    Submitted on {new Date(request.created_at).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">Reason: {request.reason}</p>
                </div>
                <Badge
                  variant={
                    request.status === 'completed' ? 'success' :
                    request.status === 'pending' ? 'warning' :
                    'secondary'
                  }
                >
                  {request.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
      {/* Export Data Modal */}
      <Modal
        isOpen={showDataExport}
        onClose={() => setShowDataExport(false)}
        title="Export Personal Data"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Select the format in which you'd like to export your personal data:
          </p>
          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => handleDataExport('json')}
            >
              <FileText className="h-4 w-4 mr-2" />
              JSON Format (Machine Readable)
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => handleDataExport('csv')}
            >
              <FileText className="h-4 w-4 mr-2" />
              CSV Format (Spreadsheet)
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => handleDataExport('pdf')}
            >
              <FileText className="h-4 w-4 mr-2" />
              PDF Format (Human Readable)
            </Button>
          </div>
        </div>
      </Modal>
      {/* Delete Data Modal */}
      <Modal
        isOpen={showDataDeletion}
        onClose={() => setShowDataDeletion(false)}
        title="Request Data Deletion"
      >
        <div className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <div>
                <h3 className="font-medium text-red-900">Warning</h3>
                <p className="text-sm text-red-700 mt-1">
                  Deleting your data is permanent and cannot be undone. All your personal information,
                  progress, and associated data will be permanently removed from our systems.
                </p>
              </div>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reason for deletion
            </label>
            <Textarea
              value={deletionReason}
              onChange={(e) => setDeletionReason(e.target.value)}
              rows={3}
              placeholder="Please tell us why you want to delete your data..."
            />
          </div>
          <div className="flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowDataDeletion(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDataDeletion}
            >
              Submit Deletion Request
            </Button>
          </div>
        </div>
      </Modal>
      {/* Access Log Modal */}
      <Modal
        isOpen={showAccessLog}
        onClose={() => setShowAccessLog(false)}
        title="Data Access Log"
      >
        <div className="space-y-4">
          {!accessLog.length ? (
            <Button
              onClick={() => {
                fetchAccessLog();
              }}
            >
              Load Access Log
            </Button>
          ) : (
            <div className="max-h-96 overflow-y-auto">
              <div className="space-y-3">
                {accessLog.map((entry) => (
                  <div key={entry.id} className="border rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium">{entry.action}</p>
                      <Badge variant="secondary">{entry.type}</Badge>
                    </div>
                    <p className="text-sm text-gray-600">
                      {new Date(entry.timestamp).toLocaleString()}
                    </p>
                    {entry.details && (
                      <p className="text-sm text-gray-600 mt-1">{entry.details}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};
export default GDPRCompliancePage;