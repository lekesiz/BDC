// TODO: i18n - processed
/**
 * Report Builder Page
 * 
 * Main page for the advanced report builder interface
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { useToast } from '../../../components/ui/use-toast';
import {
  ArrowLeft,
  Save,
  Eye,
  Download,
  Clock,
  Share,
  Copy,
  Settings,
  Info } from
'lucide-react';

import ReportBuilder from '../components/ReportBuilder';
import RealtimeMonitor from '../components/RealtimeMonitor';
import { validateReportConfig } from '../utils/validationUtils';import { useTranslation } from "react-i18next";

const ReportBuilderPage = () => {const { t } = useTranslation();
  const { reportId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showRealtime, setShowRealtime] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  // Check if we're editing an existing report or creating a new one
  const isEditMode = Boolean(reportId);
  const isReadOnly = location.state?.readonly || false;

  // Load existing report if in edit mode
  useEffect(() => {
    if (isEditMode) {
      loadReport();
    } else {
      // Initialize with template or empty config
      const template = location.state?.template;
      if (template) {
        setReportData(template);
      }
    }
  }, [reportId, isEditMode, location.state]);

  const loadReport = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // This would load from your API
      // const report = await ReportingAPI.getReport(reportId);
      // setReportData(report);

      // For now, simulate loading
      setTimeout(() => {
        setReportData({
          id: reportId,
          name: 'Sample Report',
          description: 'A sample report for demonstration',
          fields: [],
          filters: [],
          grouping: [],
          sorting: []
        });
        setIsLoading(false);
      }, 1000);
    } catch (err) {
      setError(err);
      setIsLoading(false);
      toast({
        title: 'Error',
        description: 'Failed to load report.',
        variant: 'destructive'
      });
    }
  };

  const handleSave = async (savedReport) => {
    setIsDirty(false);
    toast({
      title: 'Success',
      description: `Report "${savedReport.name}" saved successfully.`
    });

    // Navigate to the report if it's a new report
    if (!isEditMode && savedReport.id) {
      navigate(`/reporting/builder/${savedReport.id}`, { replace: true });
    }
  };

  const handlePreview = (previewData) => {
    toast({
      title: 'Preview Generated',
      description: `Preview shows ${previewData.preview_data?.length || 0} sample records.`
    });
  };

  const handleExport = (exportResult) => {
    toast({
      title: 'Export Complete',
      description: `Report exported successfully.`
    });
  };

  const handleBack = () => {
    if (isDirty) {
      if (window.confirm('You have unsaved changes. Are you sure you want to leave?')) {
        navigate('/reporting');
      }
    } else {
      navigate('/reporting');
    }
  };

  const handleDuplicate = () => {
    if (reportData) {
      navigate('/reporting/builder', {
        state: {
          template: {
            ...reportData,
            name: `${reportData.name} (Copy)`,
            id: undefined
          }
        }
      });
    }
  };

  const handleShare = () => {
    // Implement sharing functionality
    toast({
      title: 'Share',
      description: 'Sharing functionality will be implemented here.'
    });
  };

  const handleSchedule = () => {
    if (reportData) {
      navigate('/reporting/schedule', {
        state: { reportConfig: reportData }
      });
    }
  };

  const handleToggleRealtime = () => {
    setShowRealtime(!showRealtime);
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {isEditMode ? 'Loading report...' : 'Initializing report builder...'}
          </p>
        </div>
      </div>);

  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">{t("components.error")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertDescription>
                {error.message || 'Failed to load the report builder.'}
              </AlertDescription>
            </Alert>
            
            <div className="flex space-x-2">
              <Button variant="outline" onClick={handleBack} className="flex-1">
                <ArrowLeft className="h-4 w-4 mr-2" />{t("components.go_back")}

              </Button>
              <Button onClick={loadReport} className="flex-1">{t("components.try_again")}

              </Button>
            </div>
          </CardContent>
        </Card>
      </div>);

  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header Bar */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={handleBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />{t("reporting.back_to_reports")}

            </Button>
            
            <div className="h-6 w-px bg-gray-300" />
            
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {isEditMode ? 'Edit Report' : 'Create Report'}
              </h1>
              <div className="flex items-center space-x-2 mt-1">
                {isEditMode &&
                <Badge variant="outline">
                    ID: {reportId}
                  </Badge>
                }
                {isReadOnly &&
                <Badge variant="secondary">{t("reporting.read_only")}

                </Badge>
                }
                {isDirty &&
                <Badge variant="outline" className="text-orange-600">{t("pages.unsaved_changes")}

                </Badge>
                }
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Action Buttons */}
            {reportData && !isReadOnly &&
            <>
                <Button
                variant="outline"
                size="sm"
                onClick={handleToggleRealtime}>

                  <Clock className="h-4 w-4 mr-2" />
                  {showRealtime ? 'Hide' : 'Show'} Real-time
                </Button>

                {isEditMode &&
              <>
                    <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDuplicate}>

                      <Copy className="h-4 w-4 mr-2" />{t("components.duplicate")}

                </Button>

                    <Button
                  variant="outline"
                  size="sm"
                  onClick={handleShare}>

                      <Share className="h-4 w-4 mr-2" />{t("components.share")}

                </Button>
                  </>
              }

                <Button
                variant="outline"
                size="sm"
                onClick={handleSchedule}>

                  <Clock className="h-4 w-4 mr-2" />{t("components.schedule")}

              </Button>
              </>
            }

            {reportData &&
            <div className="h-6 w-px bg-gray-300" />
            }

            <Button variant="ghost" size="sm">
              <Info className="h-4 w-4 mr-2" />{t("components.help")}

            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Report Builder */}
        <div className={`flex-1 ${showRealtime ? 'border-r' : ''}`}>
          <ReportBuilder
            initialConfig={reportData}
            onSave={handleSave}
            onPreview={handlePreview}
            onExport={handleExport}
            readonly={isReadOnly} />

        </div>

        {/* Real-time Monitor Sidebar */}
        {showRealtime && reportData &&
        <div className="w-96 bg-white border-l overflow-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">{t("reporting.realtime_monitor")}</h3>
                <Button
                variant="ghost"
                size="sm"
                onClick={handleToggleRealtime}>

                  ×
                </Button>
              </div>
            </div>
            
            <div className="p-4">
              <RealtimeMonitor
              subscriptionConfig={{
                type: 'report',
                report_config: reportData
              }}
              autoStart={false} />

            </div>
          </div>
        }
      </div>

      {/* Status Bar */}
      <div className="bg-gray-100 border-t px-6 py-2">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>{t("reporting.advanced_reporting_system")}

            </span>
            {reportData &&
            <>
                <span>•</span>
                <span>
                  {reportData.fields?.length || 0}{t("reporting.fields_selected")}
              </span>
                {reportData.filters?.length > 0 &&
              <>
                    <span>•</span>
                    <span>
                      {reportData.filters.length} filter{reportData.filters.length !== 1 ? 's' : ''} applied
                    </span>
                  </>
              }
              </>
            }
          </div>
          
          <div className="flex items-center space-x-4">
            {reportData &&
            <span>{t("components.last_updated")}
              {new Date().toLocaleTimeString()}
              </span>
            }
          </div>
        </div>
      </div>
    </div>);

};

export default ReportBuilderPage;