/**
 * DashboardBuilder Component
 * 
 * Advanced dashboard builder with drag-and-drop widget management
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
import { 
  Responsive, 
  WidthProvider 
} from 'react-grid-layout';

import WidgetLibrary from './WidgetLibrary';
import DashboardCanvas from './DashboardCanvas';
import DashboardSettings from './DashboardSettings';
import DashboardPreview from './DashboardPreview';

import useDashboard from '../hooks/useDashboard';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

const DashboardBuilder = ({
  initialDashboard = null,
  onSave = null,
  onPreview = null,
  readonly = false
}) => {
  const {
    dashboard,
    widgets,
    isLoading,
    error,
    updateDashboard,
    addWidget,
    updateWidget,
    removeWidget,
    saveDashboard,
    loadWidgetData
  } = useDashboard(initialDashboard);

  const { toast } = useToast();

  const [activeTab, setActiveTab] = useState('design');
  const [dashboardName, setDashboardName] = useState(initialDashboard?.name || '');
  const [dashboardDescription, setDashboardDescription] = useState(initialDashboard?.description || '');
  const [selectedWidget, setSelectedWidget] = useState(null);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [layoutMode, setLayoutMode] = useState('edit'); // edit, preview, fullscreen

  // Grid layout settings
  const [layouts, setLayouts] = useState({});
  const [breakpoints, setBreakpoints] = useState({ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 });
  const [cols, setCols] = useState({ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 });

  // Load layouts from dashboard on mount
  useEffect(() => {
    if (dashboard?.layout?.layouts) {
      setLayouts(dashboard.layout.layouts);
    }
  }, [dashboard]);

  const handleWidgetAdd = useCallback(async (widgetType, position) => {
    try {
      const widgetConfig = {
        type: widgetType,
        config: getDefaultWidgetConfig(widgetType),
        layout: {
          position: position || {
            x: 0,
            y: 0,
            w: getDefaultWidgetSize(widgetType).w,
            h: getDefaultWidgetSize(widgetType).h
          }
        }
      };

      const newWidget = await addWidget(widgetConfig);
      
      // Update layout
      const newLayouts = { ...layouts };
      Object.keys(newLayouts).forEach(breakpoint => {
        if (!newLayouts[breakpoint]) {
          newLayouts[breakpoint] = [];
        }
        newLayouts[breakpoint].push({
          i: newWidget.id,
          x: position?.x || 0,
          y: position?.y || Infinity, // Add to bottom
          w: getDefaultWidgetSize(widgetType).w,
          h: getDefaultWidgetSize(widgetType).h,
          minW: getMinWidgetSize(widgetType).w,
          minH: getMinWidgetSize(widgetType).h
        });
      });
      
      setLayouts(newLayouts);

      toast({
        title: 'Success',
        description: `${widgetType} widget added to dashboard.`
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to add widget.',
        variant: 'destructive'
      });
    }
  }, [addWidget, layouts, toast]);

  const handleWidgetUpdate = useCallback(async (widgetId, updates) => {
    try {
      await updateWidget(widgetId, updates);
      
      if (selectedWidget?.id === widgetId) {
        setSelectedWidget({ ...selectedWidget, ...updates });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update widget.',
        variant: 'destructive'
      });
    }
  }, [updateWidget, selectedWidget, toast]);

  const handleWidgetRemove = useCallback(async (widgetId) => {
    try {
      await removeWidget(widgetId);
      
      // Remove from layouts
      const newLayouts = { ...layouts };
      Object.keys(newLayouts).forEach(breakpoint => {
        newLayouts[breakpoint] = newLayouts[breakpoint].filter(item => item.i !== widgetId);
      });
      setLayouts(newLayouts);

      if (selectedWidget?.id === widgetId) {
        setSelectedWidget(null);
      }

      toast({
        title: 'Success',
        description: 'Widget removed from dashboard.'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to remove widget.',
        variant: 'destructive'
      });
    }
  }, [removeWidget, layouts, selectedWidget, toast]);

  const handleLayoutChange = useCallback((layout, layouts) => {
    setLayouts(layouts);
    
    // Update dashboard layout
    updateDashboard({
      ...dashboard,
      layout: {
        ...dashboard.layout,
        layouts
      }
    });
  }, [dashboard, updateDashboard]);

  const handleSave = async () => {
    try {
      const dashboardData = {
        name: dashboardName,
        description: dashboardDescription,
        layout: {
          ...dashboard.layout,
          layouts
        },
        widgets,
        theme: dashboard.theme || 'light',
        refresh_interval: dashboard.refresh_interval || 300
      };

      const result = await saveDashboard(dashboardData);
      
      if (onSave) {
        onSave(result);
      }

      toast({
        title: 'Success',
        description: 'Dashboard saved successfully.'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to save dashboard.',
        variant: 'destructive'
      });
    }
  };

  const handlePreview = () => {
    setIsPreviewMode(true);
    setActiveTab('preview');
    
    if (onPreview) {
      onPreview({
        ...dashboard,
        name: dashboardName,
        description: dashboardDescription,
        widgets
      });
    }
  };

  const getDefaultWidgetConfig = (widgetType) => {
    const configs = {
      chart: {
        chart_type: 'bar',
        data_source: 'beneficiaries',
        x_axis: 'first_name',
        y_axis: 'id',
        aggregation: 'count'
      },
      metric: {
        metric_type: 'single_value',
        data_source: 'beneficiaries',
        metric_field: 'id',
        aggregation: 'count',
        format: 'number'
      },
      table: {
        data_source: 'beneficiaries',
        columns: ['first_name', 'last_name', 'email'],
        pagination: true,
        page_size: 10
      },
      map: {
        map_type: 'markers',
        data_source: 'beneficiaries',
        location_field: 'address',
        zoom_level: 10
      },
      calendar: {
        data_source: 'appointments',
        date_field: 'start_time',
        title_field: 'title',
        view_type: 'month'
      },
      progress: {
        progress_type: 'linear',
        data_source: 'programs',
        current_field: 'enrolled_count',
        target_field: 'capacity'
      },
      text: {
        content_type: 'markdown',
        content: '# Welcome\n\nThis is a text widget.',
        font_size: 'medium'
      }
    };

    return configs[widgetType] || {};
  };

  const getDefaultWidgetSize = (widgetType) => {
    const sizes = {
      chart: { w: 6, h: 4 },
      metric: { w: 3, h: 2 },
      table: { w: 8, h: 6 },
      map: { w: 6, h: 6 },
      calendar: { w: 8, h: 6 },
      progress: { w: 4, h: 2 },
      text: { w: 4, h: 3 }
    };

    return sizes[widgetType] || { w: 4, h: 3 };
  };

  const getMinWidgetSize = (widgetType) => {
    const minSizes = {
      chart: { w: 3, h: 2 },
      metric: { w: 2, h: 1 },
      table: { w: 4, h: 3 },
      map: { w: 3, h: 3 },
      calendar: { w: 4, h: 3 },
      progress: { w: 2, h: 1 },
      text: { w: 2, h: 2 }
    };

    return minSizes[widgetType] || { w: 2, h: 2 };
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard builder...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Error loading dashboard builder: {error.message}
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
                placeholder="Dashboard Name"
                value={dashboardName}
                onChange={(e) => setDashboardName(e.target.value)}
                className="text-lg font-semibold mb-2"
                disabled={readonly}
              />
              <Input
                placeholder="Dashboard Description (optional)"
                value={dashboardDescription}
                onChange={(e) => setDashboardDescription(e.target.value)}
                className="text-sm text-gray-600"
                disabled={readonly}
              />
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              <Badge variant="outline">
                {widgets.length} Widget{widgets.length !== 1 ? 's' : ''}
              </Badge>
              
              {!readonly && (
                <>
                  <Button
                    variant="outline"
                    onClick={handlePreview}
                  >
                    Preview
                  </Button>
                  
                  <Button
                    onClick={handleSave}
                    disabled={!dashboardName}
                  >
                    Save Dashboard
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Left Sidebar - Widget Library */}
          {!isPreviewMode && (
            <div className="w-80 border-r bg-gray-50 flex flex-col">
              <WidgetLibrary
                onWidgetAdd={handleWidgetAdd}
                readonly={readonly}
              />
            </div>
          )}

          {/* Center - Dashboard Canvas */}
          <div className="flex-1 flex flex-col">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
              {!isPreviewMode && (
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="design">Design</TabsTrigger>
                  <TabsTrigger value="settings">Settings</TabsTrigger>
                  <TabsTrigger value="preview">Preview</TabsTrigger>
                </TabsList>
              )}

              <TabsContent value="design" className="flex-1 p-4">
                <DashboardCanvas
                  widgets={widgets}
                  layouts={layouts}
                  breakpoints={breakpoints}
                  cols={cols}
                  onLayoutChange={handleLayoutChange}
                  onWidgetSelect={setSelectedWidget}
                  onWidgetUpdate={handleWidgetUpdate}
                  onWidgetRemove={handleWidgetRemove}
                  selectedWidget={selectedWidget}
                  readonly={readonly}
                />
              </TabsContent>

              <TabsContent value="settings" className="flex-1 p-4">
                <DashboardSettings
                  dashboard={dashboard}
                  onDashboardUpdate={updateDashboard}
                  breakpoints={breakpoints}
                  cols={cols}
                  onBreakpointsChange={setBreakpoints}
                  onColsChange={setCols}
                  readonly={readonly}
                />
              </TabsContent>

              <TabsContent value="preview" className="flex-1 p-4">
                <DashboardPreview
                  dashboard={{
                    ...dashboard,
                    name: dashboardName,
                    description: dashboardDescription,
                    widgets
                  }}
                  layouts={layouts}
                  breakpoints={breakpoints}
                  cols={cols}
                  onBackToEdit={() => {
                    setIsPreviewMode(false);
                    setActiveTab('design');
                  }}
                />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </DndProvider>
  );
};

export default DashboardBuilder;