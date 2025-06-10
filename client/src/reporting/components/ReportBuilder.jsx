/**
 * ReportBuilder Component
 * 
 * Main drag-and-drop report builder interface
 */

import React, { useState, useEffect, useCallback } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Badge } from '../../../components/ui/badge';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { useToast } from '../../../components/ui/use-toast';

import FieldPalette from './dragdrop/FieldPalette';
import ReportCanvas from './ReportCanvas';
import FilterBuilder from './FilterBuilder';
import PreviewPanel from './PreviewPanel';
import ExportPanel from './ExportPanel';

import useReportBuilder from '../hooks/useReportBuilder';
import { validateReportConfig } from '../utils/validationUtils';

const ReportBuilder = ({
  initialConfig = null,
  onSave = null,
  onPreview = null,
  onExport = null,
  readonly = false
}) => {
  const {
    reportConfig,
    availableFields,
    isLoading,
    error,
    updateReportConfig,
    saveReport,
    previewReport,
    exportReport,
    loadAvailableFields
  } = useReportBuilder(initialConfig);

  const { toast } = useToast();

  const [activeTab, setActiveTab] = useState('design');
  const [reportName, setReportName] = useState(initialConfig?.name || '');
  const [reportDescription, setReportDescription] = useState(initialConfig?.description || '');
  const [validationErrors, setValidationErrors] = useState([]);
  const [previewData, setPreviewData] = useState(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // Load available fields on mount
  useEffect(() => {
    loadAvailableFields();
  }, [loadAvailableFields]);

  // Validate report configuration whenever it changes
  useEffect(() => {
    if (reportConfig) {
      const validation = validateReportConfig(reportConfig);
      setValidationErrors(validation.errors || []);
    }
  }, [reportConfig]);

  const handleFieldDrop = useCallback((field, position) => {
    const newFields = [...(reportConfig.fields || [])];
    
    // Check if field already exists
    const existingIndex = newFields.findIndex(f => f.field === field.field && f.source === field.source);
    
    if (existingIndex >= 0) {
      // Move existing field
      const [movedField] = newFields.splice(existingIndex, 1);
      newFields.splice(position, 0, movedField);
    } else {
      // Add new field
      const newField = {
        ...field,
        id: `${field.source}_${field.field}_${Date.now()}`,
        alias: field.alias || field.name || field.field
      };
      newFields.splice(position, 0, newField);
    }
    
    updateReportConfig({
      ...reportConfig,
      fields: newFields
    });
  }, [reportConfig, updateReportConfig]);

  const handleFieldRemove = useCallback((fieldId) => {
    const newFields = (reportConfig.fields || []).filter(f => f.id !== fieldId);
    updateReportConfig({
      ...reportConfig,
      fields: newFields
    });
  }, [reportConfig, updateReportConfig]);

  const handleFieldUpdate = useCallback((fieldId, updates) => {
    const newFields = (reportConfig.fields || []).map(f =>
      f.id === fieldId ? { ...f, ...updates } : f
    );
    updateReportConfig({
      ...reportConfig,
      fields: newFields
    });
  }, [reportConfig, updateReportConfig]);

  const handleFilterUpdate = useCallback((filters) => {
    updateReportConfig({
      ...reportConfig,
      filters
    });
  }, [reportConfig, updateReportConfig]);

  const handleGroupingUpdate = useCallback((grouping) => {
    updateReportConfig({
      ...reportConfig,
      grouping
    });
  }, [reportConfig, updateReportConfig]);

  const handleSortingUpdate = useCallback((sorting) => {
    updateReportConfig({
      ...reportConfig,
      sorting
    });
  }, [reportConfig, updateReportConfig]);

  const handleSave = async () => {
    if (validationErrors.length > 0) {
      toast({
        title: 'Validation Error',
        description: 'Please fix the validation errors before saving.',
        variant: 'destructive'
      });
      return;
    }

    try {
      const reportData = {
        name: reportName,
        description: reportDescription,
        ...reportConfig
      };

      const result = await saveReport(reportData);
      
      if (onSave) {
        onSave(result);
      }

      toast({
        title: 'Success',
        description: 'Report saved successfully.'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to save report.',
        variant: 'destructive'
      });
    }
  };

  const handlePreview = async () => {
    if (validationErrors.length > 0) {
      toast({
        title: 'Validation Error',
        description: 'Please fix the validation errors before previewing.',
        variant: 'destructive'
      });
      return;
    }

    setIsPreviewLoading(true);
    try {
      const result = await previewReport({
        ...reportConfig,
        name: reportName,
        description: reportDescription
      });

      setPreviewData(result);
      setActiveTab('preview');

      if (onPreview) {
        onPreview(result);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to generate preview.',
        variant: 'destructive'
      });
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const handleExport = async (format, options) => {
    try {
      const result = await exportReport({
        ...reportConfig,
        name: reportName,
        description: reportDescription
      }, format, options);

      if (onExport) {
        onExport(result);
      }

      toast({
        title: 'Success',
        description: `Report exported as ${format.toUpperCase()}.`
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to export report.',
        variant: 'destructive'
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading report builder...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Error loading report builder: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="border-b bg-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 max-w-2xl">
              <Input
                placeholder="Report Name"
                value={reportName}
                onChange={(e) => setReportName(e.target.value)}
                className="text-lg font-semibold mb-2"
                disabled={readonly}
              />
              <Input
                placeholder="Report Description (optional)"
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                className="text-sm text-gray-600"
                disabled={readonly}
              />
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              {validationErrors.length > 0 && (
                <Badge variant="destructive">
                  {validationErrors.length} Error{validationErrors.length > 1 ? 's' : ''}
                </Badge>
              )}
              
              {!readonly && (
                <>
                  <Button
                    variant="outline"
                    onClick={handlePreview}
                    disabled={isPreviewLoading || validationErrors.length > 0}
                  >
                    {isPreviewLoading ? 'Previewing...' : 'Preview'}
                  </Button>
                  
                  <Button
                    onClick={handleSave}
                    disabled={!reportName || validationErrors.length > 0}
                  >
                    Save Report
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Validation Errors */}
          {validationErrors.length > 0 && (
            <div className="mt-4">
              <Alert variant="destructive">
                <AlertDescription>
                  <ul className="list-disc list-inside space-y-1">
                    {validationErrors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Left Sidebar - Field Palette */}
          <div className="w-80 border-r bg-gray-50 flex flex-col">
            <FieldPalette
              availableFields={availableFields}
              onFieldDrag={handleFieldDrop}
              readonly={readonly}
            />
          </div>

          {/* Center - Report Builder */}
          <div className="flex-1 flex flex-col">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="design">Design</TabsTrigger>
                <TabsTrigger value="filters">Filters</TabsTrigger>
                <TabsTrigger value="preview">Preview</TabsTrigger>
                <TabsTrigger value="export">Export</TabsTrigger>
              </TabsList>

              <TabsContent value="design" className="flex-1 p-4">
                <ReportCanvas
                  fields={reportConfig.fields || []}
                  onFieldDrop={handleFieldDrop}
                  onFieldRemove={handleFieldRemove}
                  onFieldUpdate={handleFieldUpdate}
                  onGroupingUpdate={handleGroupingUpdate}
                  onSortingUpdate={handleSortingUpdate}
                  readonly={readonly}
                />
              </TabsContent>

              <TabsContent value="filters" className="flex-1 p-4">
                <FilterBuilder
                  filters={reportConfig.filters || []}
                  availableFields={availableFields}
                  onFiltersUpdate={handleFilterUpdate}
                  readonly={readonly}
                />
              </TabsContent>

              <TabsContent value="preview" className="flex-1 p-4">
                <PreviewPanel
                  previewData={previewData}
                  isLoading={isPreviewLoading}
                  onRefresh={handlePreview}
                />
              </TabsContent>

              <TabsContent value="export" className="flex-1 p-4">
                <ExportPanel
                  reportConfig={reportConfig}
                  reportName={reportName}
                  onExport={handleExport}
                  disabled={validationErrors.length > 0}
                />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </DndProvider>
  );
};

export default ReportBuilder;