import React, { useState, useCallback } from 'react';
import { 
  X, 
  Upload, 
  Download, 
  Users, 
  Trash2, 
  Edit3, 
  UserPlus,
  AlertCircle,
  CheckCircle,
  FileText
} from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Alert } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import api from '@/lib/api';
import { useToast } from '@/components/ui/toast';

const BulkOperationsModal = ({ 
  isOpen, 
  onClose, 
  entityType, 
  selectedIds = [],
  onSuccess 
}) => {
  const [activeTab, setActiveTab] = useState('update');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [updateFields, setUpdateFields] = useState({});
  const [assignTrainerId, setAssignTrainerId] = useState('');
  const [trainers, setTrainers] = useState([]);
  const { addToast } = useToast();

  // Fetch trainers for assignment
  React.useEffect(() => {
    if (isOpen && entityType === 'beneficiaries') {
      fetchTrainers();
    }
  }, [isOpen, entityType]);

  const fetchTrainers = async () => {
    try {
      const response = await api.get('/api/users', {
        params: { role: 'trainer', status: 'active' }
      });
      setTrainers(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch trainers:', error);
    }
  };

  const handleBulkOperation = async (operation) => {
    setIsProcessing(true);
    setProgress(0);
    setResults(null);

    try {
      // Validate operation first
      const validationResponse = await api.post('/api/v2/bulk/validate', {
        operation,
        entity_type: entityType,
        ids: selectedIds,
        fields_to_update: operation === 'update' ? updateFields : 
                          operation === 'assign' ? { trainer_id: assignTrainerId } : undefined
      });

      if (!validationResponse.data.valid) {
        addToast({
          type: 'error',
          title: 'Validation Failed',
          message: validationResponse.data.errors.join(', ')
        });
        setIsProcessing(false);
        return;
      }

      // Show warnings if any
      if (validationResponse.data.warnings.length > 0) {
        const confirmed = window.confirm(
          `Warning: ${validationResponse.data.warnings.join('\n')}\n\nDo you want to continue?`
        );
        if (!confirmed) {
          setIsProcessing(false);
          return;
        }
      }

      // Execute operation
      const response = await api.post('/api/v2/bulk/operations', {
        operation,
        entity_type: entityType,
        ids: selectedIds,
        fields_to_update: operation === 'update' ? updateFields : 
                          operation === 'assign' ? { trainer_id: assignTrainerId } : undefined
      });

      setResults(response.data);
      setProgress(100);

      if (response.data.successful > 0) {
        addToast({
          type: 'success',
          title: 'Bulk Operation Completed',
          message: `Successfully processed ${response.data.successful} of ${response.data.total} items`
        });
        
        if (onSuccess) {
          onSuccess();
        }
      }

      if (response.data.failed > 0) {
        addToast({
          type: 'warning',
          title: 'Some Operations Failed',
          message: `${response.data.failed} items could not be processed`
        });
      }

    } catch (error) {
      console.error('Bulk operation failed:', error);
      addToast({
        type: 'error',
        title: 'Operation Failed',
        message: error.response?.data?.error || 'An unexpected error occurred'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsProcessing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post(`/api/v2/bulk/import/${entityType}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResults(response.data);
      addToast({
        type: 'success',
        title: 'Import Completed',
        message: `Imported ${response.data.successful} of ${response.data.total} items`
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Import Failed',
        message: error.response?.data?.error || 'Failed to import file'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await api.get(`/api/v2/bulk/templates/${entityType}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${entityType}_import_template.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Download Failed',
        message: 'Failed to download template'
      });
    }
  };

  const exportSelected = async () => {
    try {
      const response = await api.post('/api/v2/bulk/operations', {
        operation: 'export',
        entity_type: entityType,
        ids: selectedIds,
        format: 'csv'
      });

      // Create download link
      const blob = new Blob([response.data.export_data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', response.data.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      addToast({
        type: 'success',
        title: 'Export Completed',
        message: `Exported ${selectedIds.length} items`
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Export Failed',
        message: error.response?.data?.error || 'Failed to export data'
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Bulk Operations - {selectedIds.length} items selected</DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-5 w-full">
            <TabTrigger value="update">
              <Edit3 className="h-4 w-4 mr-2" />
              Update
            </TabTrigger>
            <TabTrigger value="assign">
              <UserPlus className="h-4 w-4 mr-2" />
              Assign
            </TabTrigger>
            <TabTrigger value="delete">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </TabTrigger>
            <TabTrigger value="import">
              <Upload className="h-4 w-4 mr-2" />
              Import
            </TabTrigger>
            <TabTrigger value="export">
              <Download className="h-4 w-4 mr-2" />
              Export
            </TabTrigger>
          </TabsList>

          {/* Update Tab */}
          <TabContent value="update" className="space-y-4">
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Update Fields</h3>
              
              {entityType === 'beneficiaries' && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Status</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={updateFields.status || ''}
                      onChange={(e) => setUpdateFields({...updateFields, status: e.target.value})}
                    >
                      <option value="">-- No change --</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="pending">Pending</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">City</label>
                    <input
                      type="text"
                      className="w-full p-2 border rounded-md"
                      value={updateFields.city || ''}
                      onChange={(e) => setUpdateFields({...updateFields, city: e.target.value})}
                      placeholder="Leave empty for no change"
                    />
                  </div>
                </>
              )}

              <Button
                onClick={() => handleBulkOperation('update')}
                disabled={isProcessing || Object.keys(updateFields).length === 0}
                className="w-full"
              >
                Update {selectedIds.length} Items
              </Button>
            </div>
          </TabContent>

          {/* Assign Tab */}
          <TabContent value="assign" className="space-y-4">
            {entityType === 'beneficiaries' && (
              <div className="space-y-4">
                <h3 className="text-sm font-medium">Assign Trainer</h3>
                
                <select
                  className="w-full p-2 border rounded-md"
                  value={assignTrainerId}
                  onChange={(e) => setAssignTrainerId(e.target.value)}
                >
                  <option value="">Select a trainer</option>
                  {trainers.map(trainer => (
                    <option key={trainer.id} value={trainer.id}>
                      {trainer.first_name} {trainer.last_name} - {trainer.email}
                    </option>
                  ))}
                </select>

                <Button
                  onClick={() => handleBulkOperation('assign')}
                  disabled={isProcessing || !assignTrainerId}
                  className="w-full"
                >
                  Assign to {selectedIds.length} Beneficiaries
                </Button>
              </div>
            )}
          </TabContent>

          {/* Delete Tab */}
          <TabContent value="delete" className="space-y-4">
            <Alert type="warning" title="Warning">
              This action cannot be undone. Are you sure you want to delete {selectedIds.length} items?
            </Alert>

            <Button
              variant="destructive"
              onClick={() => handleBulkOperation('delete')}
              disabled={isProcessing}
              className="w-full"
            >
              Delete {selectedIds.length} Items
            </Button>
          </TabContent>

          {/* Import Tab */}
          <TabContent value="import" className="space-y-4">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Import from CSV</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadTemplate}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Download Template
                </Button>
              </div>

              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="bulk-import-file"
                />
                <label htmlFor="bulk-import-file" className="cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-sm text-gray-600">
                    Click to upload CSV file or drag and drop
                  </p>
                </label>
              </div>
            </div>
          </TabContent>

          {/* Export Tab */}
          <TabContent value="export" className="space-y-4">
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Export Selected Items</h3>
              
              <p className="text-sm text-gray-600">
                Export {selectedIds.length} selected items to CSV format.
              </p>

              <Button
                onClick={exportSelected}
                disabled={isProcessing}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                Export to CSV
              </Button>
            </div>
          </TabContent>
        </Tabs>

        {/* Progress and Results */}
        {isProcessing && (
          <div className="mt-6 space-y-2">
            <p className="text-sm font-medium">Processing...</p>
            <Progress value={progress} />
          </div>
        )}

        {results && (
          <div className="mt-6 space-y-4">
            <h3 className="text-sm font-medium">Results</h3>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold">{results.total}</p>
                <p className="text-sm text-gray-600">Total</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{results.successful}</p>
                <p className="text-sm text-gray-600">Successful</p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{results.failed}</p>
                <p className="text-sm text-gray-600">Failed</p>
              </div>
            </div>

            {results.errors && results.errors.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Errors:</h4>
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {results.errors.map((error, idx) => (
                    <div key={idx} className="text-sm text-red-600 flex items-start">
                      <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0 mt-0.5" />
                      <span>
                        {error.id ? `ID ${error.id}: ` : ''}
                        {error.row ? `Row ${error.row}: ` : ''}
                        {error.error}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default BulkOperationsModal;