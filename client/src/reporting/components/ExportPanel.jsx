/**
 * ExportPanel Component
 * 
 * Comprehensive export functionality for reports with multiple formats and options
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Checkbox } from '../../../components/ui/checkbox';
import { Textarea } from '../../../components/ui/textarea';
import { Badge } from '../../../components/ui/badge';
import { Progress } from '../../../components/ui/progress';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { 
  Download, 
  FileText, 
  FileSpreadsheet, 
  File, 
  Presentation,
  Image,
  Code,
  Settings,
  CheckCircle,
  AlertCircle,
  Calendar,
  Mail,
  Webhook
} from 'lucide-react';

const EXPORT_FORMATS = {
  pdf: {
    name: 'PDF Document',
    description: 'Portable Document Format with professional layout',
    icon: FileText,
    category: 'document',
    options: ['page_size', 'orientation', 'margins', 'charts', 'styling']
  },
  excel: {
    name: 'Excel Workbook',
    description: 'Microsoft Excel with multiple sheets and charts',
    icon: FileSpreadsheet,
    category: 'spreadsheet',
    options: ['sheets', 'charts', 'formatting', 'pivot_tables']
  },
  csv: {
    name: 'CSV File',
    description: 'Comma-separated values for data analysis',
    icon: File,
    category: 'data',
    options: ['delimiter', 'encoding', 'headers']
  },
  powerpoint: {
    name: 'PowerPoint Presentation',
    description: 'Microsoft PowerPoint with charts and data',
    icon: Presentation,
    category: 'presentation',
    options: ['template', 'charts', 'tables', 'styling']
  },
  word: {
    name: 'Word Document',
    description: 'Microsoft Word with formatted tables',
    icon: FileText,
    category: 'document',
    options: ['template', 'styling', 'charts', 'tables']
  },
  json: {
    name: 'JSON Data',
    description: 'JavaScript Object Notation for APIs',
    icon: Code,
    category: 'data',
    options: ['formatting', 'metadata']
  },
  xml: {
    name: 'XML Data',
    description: 'Extensible Markup Language format',
    icon: Code,
    category: 'data',
    options: ['formatting', 'schema', 'metadata']
  },
  png: {
    name: 'PNG Image',
    description: 'Portable Network Graphics image',
    icon: Image,
    category: 'image',
    options: ['resolution', 'quality', 'transparency']
  }
};

const ExportPanel = ({
  reportConfig,
  reportName = '',
  onExport,
  disabled = false,
  className = ''
}) => {
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [exportOptions, setExportOptions] = useState({});
  const [deliveryMethod, setDeliveryMethod] = useState('download');
  const [exportProgress, setExportProgress] = useState(null);
  const [exportHistory, setExportHistory] = useState([]);
  const [isExporting, setIsExporting] = useState(false);

  const selectedFormatInfo = EXPORT_FORMATS[selectedFormat];

  const handleExport = async () => {
    if (!onExport || disabled) return;

    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const result = await onExport(selectedFormat, {
        ...exportOptions,
        delivery_method: deliveryMethod,
        file_name: exportOptions.file_name || `${reportName || 'report'}.${getFileExtension(selectedFormat)}`
      });

      clearInterval(progressInterval);
      setExportProgress(100);

      // Add to history
      const historyItem = {
        id: Date.now(),
        format: selectedFormat,
        name: exportOptions.file_name || `${reportName || 'report'}.${getFileExtension(selectedFormat)}`,
        timestamp: new Date().toISOString(),
        size: result.file_size || 0,
        status: 'completed'
      };
      setExportHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10

      setTimeout(() => {
        setExportProgress(null);
        setIsExporting(false);
      }, 1000);

    } catch (error) {
      setExportProgress(null);
      setIsExporting(false);
      
      const historyItem = {
        id: Date.now(),
        format: selectedFormat,
        name: exportOptions.file_name || `${reportName || 'report'}.${getFileExtension(selectedFormat)}`,
        timestamp: new Date().toISOString(),
        status: 'failed',
        error: error.message
      };
      setExportHistory(prev => [historyItem, ...prev.slice(0, 9)]);
    }
  };

  const updateExportOption = (key, value) => {
    setExportOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const getFileExtension = (format) => {
    const extensions = {
      pdf: 'pdf',
      excel: 'xlsx',
      csv: 'csv',
      powerpoint: 'pptx',
      word: 'docx',
      json: 'json',
      xml: 'xml',
      png: 'png'
    };
    return extensions[format] || format;
  };

  const renderFormatOptions = () => {
    if (!selectedFormatInfo) return null;

    switch (selectedFormat) {
      case 'pdf':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="page_size">Page Size</Label>
                <Select value={exportOptions.page_size || 'A4'} onValueChange={(value) => updateExportOption('page_size', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="A4">A4</SelectItem>
                    <SelectItem value="Letter">Letter</SelectItem>
                    <SelectItem value="Legal">Legal</SelectItem>
                    <SelectItem value="A3">A3</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="orientation">Orientation</Label>
                <Select value={exportOptions.orientation || 'portrait'} onValueChange={(value) => updateExportOption('orientation', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="portrait">Portrait</SelectItem>
                    <SelectItem value="landscape">Landscape</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="margins">Margins (inches)</Label>
              <Input
                placeholder="0.75"
                value={exportOptions.margins || ''}
                onChange={(e) => updateExportOption('margins', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="include_charts"
                  checked={exportOptions.include_charts !== false}
                  onCheckedChange={(checked) => updateExportOption('include_charts', checked)}
                />
                <Label htmlFor="include_charts">Include charts</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="include_metadata"
                  checked={exportOptions.include_metadata !== false}
                  onCheckedChange={(checked) => updateExportOption('include_metadata', checked)}
                />
                <Label htmlFor="include_metadata">Include metadata</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="alternate_row_colors"
                  checked={exportOptions.alternate_row_colors !== false}
                  onCheckedChange={(checked) => updateExportOption('alternate_row_colors', checked)}
                />
                <Label htmlFor="alternate_row_colors">Alternate row colors</Label>
              </div>
            </div>
          </div>
        );

      case 'excel':
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="include_summary"
                  checked={exportOptions.include_summary !== false}
                  onCheckedChange={(checked) => updateExportOption('include_summary', checked)}
                />
                <Label htmlFor="include_summary">Include summary sheet</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="include_charts_excel"
                  checked={exportOptions.include_charts !== false}
                  onCheckedChange={(checked) => updateExportOption('include_charts', checked)}
                />
                <Label htmlFor="include_charts_excel">Include charts sheet</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="auto_fit_columns"
                  checked={exportOptions.auto_fit_columns !== false}
                  onCheckedChange={(checked) => updateExportOption('auto_fit_columns', checked)}
                />
                <Label htmlFor="auto_fit_columns">Auto-fit column widths</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="zebra_striping"
                  checked={exportOptions.zebra_striping !== false}
                  onCheckedChange={(checked) => updateExportOption('zebra_striping', checked)}
                />
                <Label htmlFor="zebra_striping">Zebra striping</Label>
              </div>
            </div>
          </div>
        );

      case 'csv':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="delimiter">Delimiter</Label>
                <Select value={exportOptions.delimiter || ','} onValueChange={(value) => updateExportOption('delimiter', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value=",">Comma (,)</SelectItem>
                    <SelectItem value=";">Semicolon (;)</SelectItem>
                    <SelectItem value="\t">Tab</SelectItem>
                    <SelectItem value="|">Pipe (|)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="encoding">Encoding</Label>
                <Select value={exportOptions.encoding || 'utf-8'} onValueChange={(value) => updateExportOption('encoding', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="utf-8">UTF-8</SelectItem>
                    <SelectItem value="utf-16">UTF-16</SelectItem>
                    <SelectItem value="latin-1">Latin-1</SelectItem>
                    <SelectItem value="ascii">ASCII</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox 
                id="include_headers"
                checked={exportOptions.include_headers !== false}
                onCheckedChange={(checked) => updateExportOption('include_headers', checked)}
              />
              <Label htmlFor="include_headers">Include column headers</Label>
            </div>
          </div>
        );

      case 'json':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="indent">Indentation</Label>
              <Select value={exportOptions.indent?.toString() || '2'} onValueChange={(value) => updateExportOption('indent', parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">None</SelectItem>
                  <SelectItem value="2">2 spaces</SelectItem>
                  <SelectItem value="4">4 spaces</SelectItem>
                  <SelectItem value="8">1 tab</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="include_metadata_json"
                  checked={exportOptions.include_metadata !== false}
                  onCheckedChange={(checked) => updateExportOption('include_metadata', checked)}
                />
                <Label htmlFor="include_metadata_json">Include metadata</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="ensure_ascii"
                  checked={exportOptions.ensure_ascii === true}
                  onCheckedChange={(checked) => updateExportOption('ensure_ascii', checked)}
                />
                <Label htmlFor="ensure_ascii">Ensure ASCII encoding</Label>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-sm text-gray-500">
            No additional options available for this format.
          </div>
        );
    }
  };

  const renderDeliveryOptions = () => {
    switch (deliveryMethod) {
      case 'email':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="email_recipients">Recipients (comma-separated)</Label>
              <Input
                id="email_recipients"
                placeholder="user@example.com, another@example.com"
                value={exportOptions.email_recipients || ''}
                onChange={(e) => updateExportOption('email_recipients', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="email_subject">Subject</Label>
              <Input
                id="email_subject"
                placeholder="Report Export"
                value={exportOptions.email_subject || ''}
                onChange={(e) => updateExportOption('email_subject', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="email_body">Message</Label>
              <Textarea
                id="email_body"
                placeholder="Please find the attached report..."
                value={exportOptions.email_body || ''}
                onChange={(e) => updateExportOption('email_body', e.target.value)}
                rows={3}
              />
            </div>
          </div>
        );

      case 'schedule':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="schedule_frequency">Frequency</Label>
              <Select value={exportOptions.schedule_frequency || 'daily'} onValueChange={(value) => updateExportOption('schedule_frequency', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="schedule_time">Time</Label>
              <Input
                id="schedule_time"
                type="time"
                value={exportOptions.schedule_time || '09:00'}
                onChange={(e) => updateExportOption('schedule_time', e.target.value)}
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Export Progress */}
      {exportProgress !== null && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  Exporting {selectedFormatInfo?.name}...
                </span>
                <span className="text-sm text-gray-500">
                  {exportProgress}%
                </span>
              </div>
              <Progress value={exportProgress} className="w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="format" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="format">Format & Options</TabsTrigger>
          <TabsTrigger value="delivery">Delivery</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="format" className="space-y-4">
          {/* Format Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Export Format</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(EXPORT_FORMATS).map(([format, info]) => {
                  const IconComponent = info.icon;
                  return (
                    <div
                      key={format}
                      className={`
                        p-3 border rounded-lg cursor-pointer transition-all
                        ${selectedFormat === format 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                      onClick={() => setSelectedFormat(format)}
                    >
                      <div className="flex items-start space-x-3">
                        <IconComponent className="h-5 w-5 mt-1 text-gray-600" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">
                            {info.name}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {info.description}
                          </p>
                          <Badge variant="outline" className="mt-2 text-xs">
                            {info.category}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* File Name */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">File Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="file_name">File Name</Label>
                <Input
                  id="file_name"
                  placeholder={`${reportName || 'report'}.${getFileExtension(selectedFormat)}`}
                  value={exportOptions.file_name || ''}
                  onChange={(e) => updateExportOption('file_name', e.target.value)}
                />
              </div>

              {/* Format-specific Options */}
              {selectedFormatInfo && (
                <div>
                  <Label className="text-sm font-medium">Format Options</Label>
                  <div className="mt-2">
                    {renderFormatOptions()}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="delivery" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Delivery Method</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-3">
                <div
                  className={`
                    p-3 border rounded-lg cursor-pointer transition-all flex items-center space-x-3
                    ${deliveryMethod === 'download' 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                  onClick={() => setDeliveryMethod('download')}
                >
                  <Download className="h-5 w-5 text-gray-600" />
                  <div>
                    <p className="text-sm font-medium">Download</p>
                    <p className="text-xs text-gray-500">Download file immediately</p>
                  </div>
                </div>

                <div
                  className={`
                    p-3 border rounded-lg cursor-pointer transition-all flex items-center space-x-3
                    ${deliveryMethod === 'email' 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                  onClick={() => setDeliveryMethod('email')}
                >
                  <Mail className="h-5 w-5 text-gray-600" />
                  <div>
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-xs text-gray-500">Send via email attachment</p>
                  </div>
                </div>

                <div
                  className={`
                    p-3 border rounded-lg cursor-pointer transition-all flex items-center space-x-3
                    ${deliveryMethod === 'schedule' 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                  onClick={() => setDeliveryMethod('schedule')}
                >
                  <Calendar className="h-5 w-5 text-gray-600" />
                  <div>
                    <p className="text-sm font-medium">Schedule</p>
                    <p className="text-xs text-gray-500">Set up recurring exports</p>
                  </div>
                </div>
              </div>

              {/* Delivery-specific Options */}
              <div className="mt-4">
                {renderDeliveryOptions()}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Export History</CardTitle>
            </CardHeader>
            <CardContent>
              {exportHistory.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Download className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm">No exports yet</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Your export history will appear here
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {exportHistory.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {item.status === 'completed' ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        )}
                        <div>
                          <p className="text-sm font-medium">{item.name}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(item.timestamp).toLocaleString()}
                            {item.size && ` • ${formatFileSize(item.size)}`}
                          </p>
                          {item.error && (
                            <p className="text-xs text-red-600 mt-1">{item.error}</p>
                          )}
                        </div>
                      </div>
                      <Badge variant={item.status === 'completed' ? 'default' : 'destructive'}>
                        {item.format.toUpperCase()}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Export Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleExport}
          disabled={disabled || isExporting || !selectedFormat}
          size="lg"
          className="min-w-32"
        >
          {isExporting ? (
            <>
              <Settings className="h-4 w-4 mr-2 animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <Download className="h-4 w-4 mr-2" />
              Export {selectedFormatInfo?.name}
            </>
          )}
        </Button>
      </div>

      {disabled && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Please fix any validation errors before exporting the report.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

// Helper function to format file size
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export default ExportPanel;