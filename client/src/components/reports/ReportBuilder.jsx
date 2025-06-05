import React, { useState, useCallback, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { 
  Save, 
  Download, 
  Eye, 
  Plus, 
  Settings,
  FileText,
  BarChart3,
  Table,
  Type,
  Image,
  Filter,
  Calendar,
  Layout,
  Moon,
  Sun,
  ChevronRight,
  X,
  GripVertical,
  Trash2,
  Copy,
  Edit2
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { ScrollArea } from '../ui/scroll-area';
import { toast } from '../ui/use-toast';
import { Separator } from '../ui/separator';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import WidgetLibrary from './WidgetLibrary';
import ReportSection from './ReportSection';
import ReportPreview from './ReportPreview';
import ReportWidget from './ReportWidget';
import { reportTemplates } from './reportTemplates';
import { exportToPDF, exportToExcel, exportToCSV } from './exportUtils';
const ReportBuilder = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('design');
  const [reportName, setReportName] = useState('Untitled Report');
  const [reportDescription, setReportDescription] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [sections, setSections] = useState([]);
  const [selectedDataSources, setSelectedDataSources] = useState([]);
  const [dateRange, setDateRange] = useState({ start: null, end: null });
  const [filters, setFilters] = useState({});
  const [layoutMode, setLayoutMode] = useState('single'); // single, two-column, grid
  const [showWidgetLibrary, setShowWidgetLibrary] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [autoSave, setAutoSave] = useState(true);
  const [selectedSection, setSelectedSection] = useState(null);
  const [selectedWidget, setSelectedWidget] = useState(null);
  // Available data sources
  const dataSources = [
    { id: 'beneficiaries', name: 'Beneficiaries', icon: '👥' },
    { id: 'evaluations', name: 'Evaluations', icon: '📊' },
    { id: 'programs', name: 'Programs', icon: '📚' },
    { id: 'trainers', name: 'Trainers', icon: '👨‍🏫' },
    { id: 'analytics', name: 'Analytics', icon: '📈' },
    { id: 'performance', name: 'Performance', icon: '🎯' }
  ];
  // Auto-save functionality
  useEffect(() => {
    if (autoSave && sections.length > 0) {
      const saveTimer = setTimeout(() => {
        handleSave(true);
      }, 30000); // Auto-save every 30 seconds
      return () => clearTimeout(saveTimer);
    }
  }, [sections, autoSave]);
  // Load template
  const loadTemplate = (templateId) => {
    const template = reportTemplates.find(t => t.id === templateId);
    if (template) {
      setReportName(template.name);
      setReportDescription(template.description);
      setSections(template.sections);
      setSelectedDataSources(template.dataSources);
      setLayoutMode(template.layout || 'single');
      setSelectedTemplate(templateId);
      toast({
        title: "Template Loaded",
        description: `${template.name} template has been loaded successfully.`,
      });
    }
  };
  // Handle drag and drop
  const handleDragEnd = (result) => {
    if (!result.destination) return;
    const { source, destination, type } = result;
    // If dragging from widget library to report
    if (type === 'WIDGET' && source.droppableId === 'widget-library' && destination.droppableId.startsWith('section-')) {
      const sectionId = destination.droppableId.replace('section-', '');
      const widgetType = result.draggableId;
      addWidgetToSection(sectionId, widgetType, destination.index);
      return;
    }
    // If reordering sections
    if (type === 'SECTION') {
      const newSections = Array.from(sections);
      const [reorderedSection] = newSections.splice(source.index, 1);
      newSections.splice(destination.index, 0, reorderedSection);
      setSections(newSections);
      return;
    }
    // If reordering widgets within a section
    if (type === 'WIDGET' && source.droppableId === destination.droppableId) {
      const sectionId = source.droppableId.replace('section-', '');
      const section = sections.find(s => s.id === sectionId);
      if (section) {
        const newWidgets = Array.from(section.widgets);
        const [reorderedWidget] = newWidgets.splice(source.index, 1);
        newWidgets.splice(destination.index, 0, reorderedWidget);
        updateSection(sectionId, { widgets: newWidgets });
      }
      return;
    }
    // If moving widget between sections
    if (type === 'WIDGET' && source.droppableId !== destination.droppableId) {
      const sourceSectionId = source.droppableId.replace('section-', '');
      const destSectionId = destination.droppableId.replace('section-', '');
      const sourceSection = sections.find(s => s.id === sourceSectionId);
      const destSection = sections.find(s => s.id === destSectionId);
      if (sourceSection && destSection) {
        const sourceWidgets = Array.from(sourceSection.widgets);
        const [movedWidget] = sourceWidgets.splice(source.index, 1);
        const destWidgets = Array.from(destSection.widgets);
        destWidgets.splice(destination.index, 0, movedWidget);
        const newSections = sections.map(section => {
          if (section.id === sourceSectionId) {
            return { ...section, widgets: sourceWidgets };
          }
          if (section.id === destSectionId) {
            return { ...section, widgets: destWidgets };
          }
          return section;
        });
        setSections(newSections);
      }
    }
  };
  // Add new section
  const addSection = () => {
    const newSection = {
      id: `section-${Date.now()}`,
      title: 'New Section',
      layout: layoutMode,
      widgets: []
    };
    setSections([...sections, newSection]);
    setSelectedSection(newSection.id);
  };
  // Update section
  const updateSection = (sectionId, updates) => {
    setSections(sections.map(section => 
      section.id === sectionId ? { ...section, ...updates } : section
    ));
  };
  // Delete section
  const deleteSection = (sectionId) => {
    setSections(sections.filter(section => section.id !== sectionId));
    if (selectedSection === sectionId) {
      setSelectedSection(null);
    }
  };
  // Duplicate section
  const duplicateSection = (sectionId) => {
    const section = sections.find(s => s.id === sectionId);
    if (section) {
      const newSection = {
        ...section,
        id: `section-${Date.now()}`,
        title: `${section.title} (Copy)`,
        widgets: section.widgets.map(widget => ({
          ...widget,
          id: `widget-${Date.now()}-${Math.random()}`
        }))
      };
      const sectionIndex = sections.findIndex(s => s.id === sectionId);
      const newSections = [...sections];
      newSections.splice(sectionIndex + 1, 0, newSection);
      setSections(newSections);
    }
  };
  // Add widget to section
  const addWidgetToSection = (sectionId, widgetType, index) => {
    const newWidget = {
      id: `widget-${Date.now()}`,
      type: widgetType,
      config: getDefaultWidgetConfig(widgetType),
      dataSource: selectedDataSources[0] || null
    };
    const section = sections.find(s => s.id === sectionId);
    if (section) {
      const newWidgets = [...section.widgets];
      newWidgets.splice(index !== undefined ? index : newWidgets.length, 0, newWidget);
      updateSection(sectionId, { widgets: newWidgets });
    }
  };
  // Get default widget configuration
  const getDefaultWidgetConfig = (widgetType) => {
    const configs = {
      chart: {
        chartType: 'bar',
        title: 'Chart Title',
        xAxis: 'category',
        yAxis: 'value',
        colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
        showLegend: true,
        showGrid: true
      },
      table: {
        title: 'Table Title',
        columns: [],
        pageSize: 10,
        sortable: true,
        filterable: true,
        exportable: true
      },
      kpi: {
        title: 'KPI Title',
        value: 0,
        unit: '',
        trend: 'up',
        trendValue: 0,
        icon: 'TrendingUp',
        color: '#3b82f6'
      },
      text: {
        content: '<p>Enter your text here...</p>',
        fontSize: 'base',
        alignment: 'left'
      },
      image: {
        src: '',
        alt: '',
        width: '100%',
        height: 'auto',
        alignment: 'center'
      }
    };
    return configs[widgetType] || {};
  };
  // Update widget
  const updateWidget = (sectionId, widgetId, updates) => {
    setSections(sections.map(section => {
      if (section.id === sectionId) {
        return {
          ...section,
          widgets: section.widgets.map(widget =>
            widget.id === widgetId ? { ...widget, ...updates } : widget
          )
        };
      }
      return section;
    }));
  };
  // Delete widget
  const deleteWidget = (sectionId, widgetId) => {
    setSections(sections.map(section => {
      if (section.id === sectionId) {
        return {
          ...section,
          widgets: section.widgets.filter(widget => widget.id !== widgetId)
        };
      }
      return section;
    }));
  };
  // Save report
  const handleSave = async (isAutoSave = false) => {
    const reportData = {
      name: reportName,
      description: reportDescription,
      template: selectedTemplate,
      sections,
      dataSources: selectedDataSources,
      filters,
      dateRange,
      layoutMode,
      updatedAt: new Date().toISOString()
    };
    try {
      // Save to localStorage for now
      localStorage.setItem('currentReport', JSON.stringify(reportData));
      if (!isAutoSave) {
        toast({
          title: "Report Saved",
          description: "Your report has been saved successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Save Failed",
        description: "Failed to save report. Please try again.",
        variant: "destructive"
      });
    }
  };
  // Save as template
  const handleSaveAsTemplate = () => {
    const templateData = {
      id: `template-${Date.now()}`,
      name: `${reportName} Template`,
      description: `Template based on ${reportName}`,
      sections: sections.map(section => ({
        ...section,
        widgets: section.widgets.map(widget => ({
          ...widget,
          // Clear actual data, keep only configuration
          data: null
        }))
      })),
      dataSources: selectedDataSources,
      layout: layoutMode,
      createdAt: new Date().toISOString()
    };
    try {
      const existingTemplates = JSON.parse(localStorage.getItem('customTemplates') || '[]');
      existingTemplates.push(templateData);
      localStorage.setItem('customTemplates', JSON.stringify(existingTemplates));
      toast({
        title: "Template Saved",
        description: "Your report has been saved as a template.",
      });
    } catch (error) {
      toast({
        title: "Save Failed",
        description: "Failed to save template. Please try again.",
        variant: "destructive"
      });
    }
  };
  // Export report
  const handleExport = async (format) => {
    const reportData = {
      name: reportName,
      description: reportDescription,
      sections,
      dateRange,
      generatedAt: new Date().toISOString()
    };
    try {
      switch (format) {
        case 'pdf':
          await exportToPDF(reportData);
          break;
        case 'excel':
          await exportToExcel(reportData);
          break;
        case 'csv':
          await exportToCSV(reportData);
          break;
        default:
          throw new Error('Unsupported format');
      }
      toast({
        title: "Export Successful",
        description: `Report exported as ${format.toUpperCase()} successfully.`,
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: `Failed to export report as ${format.toUpperCase()}.`,
        variant: "destructive"
      });
    }
  };
  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      <DragDropContext onDragEnd={handleDragEnd}>
        {/* Header */}
        <div className="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Report Builder
                </h1>
                <Input
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                  className="w-64"
                  placeholder="Report Name"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPreview(!showPreview)}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Preview
                </Button>
                <div className="flex items-center space-x-2 border-l pl-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleSave()}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    Save
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleSaveAsTemplate}
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Save as Template
                  </Button>
                </div>
                <div className="flex items-center space-x-2 border-l pl-2">
                  <Button
                    size="sm"
                    onClick={() => handleExport('pdf')}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
                <div className="flex items-center space-x-2 border-l pl-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDarkMode(!darkMode)}
                  >
                    {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
            </div>
          </div>
          {/* Tabs */}
          <div className="px-4">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full max-w-md grid-cols-3">
                <TabsTrigger value="design">Design</TabsTrigger>
                <TabsTrigger value="data">Data</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>
        {/* Main Content */}
        <div className="flex h-[calc(100vh-8rem)]">
          {/* Sidebar */}
          {activeTab === 'design' && showWidgetLibrary && (
            <div className="w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
              <WidgetLibrary darkMode={darkMode} />
            </div>
          )}
          {/* Content Area */}
          <div className="flex-1 overflow-auto">
            <Tabs value={activeTab} className="h-full">
              {/* Design Tab */}
              <TabsContent value="design" className="h-full p-6">
                {sections.length === 0 ? (
                  <div className="h-full flex items-center justify-center">
                    <Card className="max-w-md">
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <Layout className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                          <h3 className="text-lg font-semibold mb-2">Start Building Your Report</h3>
                          <p className="text-gray-500 mb-6">
                            Choose a template or add sections to begin creating your custom report.
                          </p>
                          <div className="space-y-3">
                            <Select onValueChange={loadTemplate}>
                              <SelectTrigger>
                                <SelectValue placeholder="Choose a template" />
                              </SelectTrigger>
                              <SelectContent>
                                {reportTemplates.map(template => (
                                  <SelectItem key={template.id} value={template.id}>
                                    <div>
                                      <div className="font-medium">{template.name}</div>
                                      <div className="text-sm text-gray-500">{template.description}</div>
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <Button onClick={addSection} className="w-full">
                              <Plus className="w-4 h-4 mr-2" />
                              Add Section
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Droppable droppableId="sections" type="SECTION">
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                          className="space-y-4"
                        >
                          {sections.map((section, index) => (
                            <Draggable
                              key={section.id}
                              draggableId={section.id}
                              index={index}
                            >
                              {(provided, snapshot) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                >
                                  <ReportSection
                                    section={section}
                                    darkMode={darkMode}
                                    isSelected={selectedSection === section.id}
                                    onSelect={() => setSelectedSection(section.id)}
                                    onUpdate={(updates) => updateSection(section.id, updates)}
                                    onDelete={() => deleteSection(section.id)}
                                    onDuplicate={() => duplicateSection(section.id)}
                                    onUpdateWidget={(widgetId, updates) => 
                                      updateWidget(section.id, widgetId, updates)
                                    }
                                    onDeleteWidget={(widgetId) => 
                                      deleteWidget(section.id, widgetId)
                                    }
                                    dragHandleProps={provided.dragHandleProps}
                                    isDragging={snapshot.isDragging}
                                  />
                                </div>
                              )}
                            </Draggable>
                          ))}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                    <div className="flex justify-center pt-4">
                      <Button onClick={addSection} variant="outline">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Section
                      </Button>
                    </div>
                  </div>
                )}
              </TabsContent>
              {/* Data Tab */}
              <TabsContent value="data" className="h-full p-6">
                <div className="max-w-4xl mx-auto space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Data Sources</CardTitle>
                      <CardDescription>
                        Select the data sources you want to include in your report
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        {dataSources.map(source => (
                          <label
                            key={source.id}
                            className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            <input
                              type="checkbox"
                              checked={selectedDataSources.includes(source.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedDataSources([...selectedDataSources, source.id]);
                                } else {
                                  setSelectedDataSources(
                                    selectedDataSources.filter(id => id !== source.id)
                                  );
                                }
                              }}
                              className="rounded"
                            />
                            <span className="text-2xl">{source.icon}</span>
                            <span className="font-medium">{source.name}</span>
                          </label>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle>Date Range</CardTitle>
                      <CardDescription>
                        Set the date range for your report data
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Start Date</Label>
                          <Input
                            type="date"
                            value={dateRange.start || ''}
                            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                          />
                        </div>
                        <div>
                          <Label>End Date</Label>
                          <Input
                            type="date"
                            value={dateRange.end || ''}
                            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle>Filters</CardTitle>
                      <CardDescription>
                        Apply filters to refine your report data
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button variant="outline" className="w-full">
                        <Filter className="w-4 h-4 mr-2" />
                        Add Filter
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              {/* Settings Tab */}
              <TabsContent value="settings" className="h-full p-6">
                <div className="max-w-4xl mx-auto space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Report Settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label>Report Description</Label>
                        <textarea
                          value={reportDescription}
                          onChange={(e) => setReportDescription(e.target.value)}
                          className="w-full p-2 border rounded-md"
                          rows={3}
                          placeholder="Describe the purpose of this report..."
                        />
                      </div>
                      <div>
                        <Label>Layout Mode</Label>
                        <Select value={layoutMode} onValueChange={setLayoutMode}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="single">Single Column</SelectItem>
                            <SelectItem value="two-column">Two Columns</SelectItem>
                            <SelectItem value="grid">Grid Layout</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex items-center justify-between">
                        <Label>Auto-save</Label>
                        <Switch
                          checked={autoSave}
                          onCheckedChange={setAutoSave}
                        />
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle>Export Settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Button
                          variant="outline"
                          className="w-full justify-between"
                          onClick={() => handleExport('pdf')}
                        >
                          <span>Export as PDF</span>
                          <Badge>Recommended</Badge>
                        </Button>
                        <Button
                          variant="outline"
                          className="w-full"
                          onClick={() => handleExport('excel')}
                        >
                          Export as Excel
                        </Button>
                        <Button
                          variant="outline"
                          className="w-full"
                          onClick={() => handleExport('csv')}
                        >
                          Export as CSV
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
          {/* Preview Panel */}
          {showPreview && (
            <div className="w-96 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
              <div className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Preview</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowPreview(false)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div className="p-4">
                <ReportPreview
                  reportName={reportName}
                  reportDescription={reportDescription}
                  sections={sections}
                  darkMode={darkMode}
                />
              </div>
            </div>
          )}
        </div>
      </DragDropContext>
    </div>
  );
};
export default ReportBuilder;