// Customizable Dashboard with Drag-and-Drop Layout
// Advanced dashboard builder with widget management and layout persistence

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Settings,
  Save,
  RotateCcw,
  Layout,
  Grid,
  Eye,
  EyeOff,
  Copy,
  Trash2,
  Edit,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2,
  MoreHorizontal,
  Filter,
  Download,
  Users,
  BarChart3,
  PieChart,
  Activity,
  Target,
  Clock,
  TrendingUp,
  Calendar,
  Award,
  BookOpen,
  MessageSquare
} from 'lucide-react';
import { useAnalytics } from '@/contexts/AnalyticsContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BaseChart, 
  TimeSeriesChart, 
  ComparisonChart,
  DistributionChart,
  PerformanceRadar,
  MetricCard,
  ChartGrid
} from './charts/ChartLibrary';
import RealTimeDashboard from './RealTimeDashboard';
import TrainerPerformanceDashboard from './TrainerPerformanceDashboard';
import SystemHealthMonitoring from './SystemHealthMonitoring';

// Widget types and configurations
const WIDGET_TYPES = {
  metric_card: {
    name: 'Metric Card',
    icon: Target,
    description: 'Display key performance indicators',
    defaultSize: { w: 1, h: 1 },
    configurable: ['title', 'metric', 'format', 'color']
  },
  line_chart: {
    name: 'Line Chart',
    icon: TrendingUp,
    description: 'Time series data visualization',
    defaultSize: { w: 2, h: 2 },
    configurable: ['title', 'dataSource', 'timeRange', 'metrics']
  },
  bar_chart: {
    name: 'Bar Chart',
    icon: BarChart3,
    description: 'Comparison and categorical data',
    defaultSize: { w: 2, h: 2 },
    configurable: ['title', 'dataSource', 'groupBy', 'metrics']
  },
  pie_chart: {
    name: 'Pie Chart',
    icon: PieChart,
    description: 'Distribution and percentage data',
    defaultSize: { w: 2, h: 2 },
    configurable: ['title', 'dataSource', 'category', 'showPercentage']
  },
  table: {
    name: 'Data Table',
    icon: Grid,
    description: 'Tabular data display',
    defaultSize: { w: 3, h: 2 },
    configurable: ['title', 'dataSource', 'columns', 'pagination']
  },
  real_time: {
    name: 'Real-time Monitor',
    icon: Activity,
    description: 'Live data streaming widget',
    defaultSize: { w: 2, h: 2 },
    configurable: ['title', 'metrics', 'refreshInterval']
  }
};

// Default dashboard layouts
const DEFAULT_LAYOUTS = {
  overview: {
    name: 'Overview Dashboard',
    description: 'General analytics overview',
    widgets: [
      { id: 'total_users', type: 'metric_card', position: { x: 0, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'active_sessions', type: 'metric_card', position: { x: 1, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'completion_rate', type: 'metric_card', position: { x: 2, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'system_health', type: 'metric_card', position: { x: 3, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'user_trends', type: 'line_chart', position: { x: 0, y: 1 }, size: { w: 2, h: 2 } },
      { id: 'program_distribution', type: 'pie_chart', position: { x: 2, y: 1 }, size: { w: 2, h: 2 } }
    ]
  },
  performance: {
    name: 'Performance Dashboard',
    description: 'System and user performance metrics',
    widgets: [
      { id: 'cpu_usage', type: 'metric_card', position: { x: 0, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'memory_usage', type: 'metric_card', position: { x: 1, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'response_time', type: 'metric_card', position: { x: 2, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'performance_trends', type: 'line_chart', position: { x: 0, y: 1 }, size: { w: 3, h: 2 } }
    ]
  },
  training: {
    name: 'Training Dashboard',
    description: 'Training programs and beneficiary progress',
    widgets: [
      { id: 'active_programs', type: 'metric_card', position: { x: 0, y: 0 }, size: { w: 1, h: 1 } },
      { id: 'beneficiary_progress', type: 'bar_chart', position: { x: 1, y: 0 }, size: { w: 2, h: 2 } },
      { id: 'trainer_performance', type: 'table', position: { x: 0, y: 2 }, size: { w: 3, h: 2 } }
    ]
  }
};

const CustomizableDashboard = () => {
  const { requestAnalyticsData, isLoading } = useAnalytics();

  // Dashboard state
  const [currentLayout, setCurrentLayout] = useState('overview');
  const [customLayouts, setCustomLayouts] = useState({});
  const [widgets, setWidgets] = useState(DEFAULT_LAYOUTS.overview.widgets);
  const [editMode, setEditMode] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState(null);
  const [dashboardData, setDashboardData] = useState({});
  const [gridSize, setGridSize] = useState({ cols: 4, rows: 6 });
  const [showGrid, setShowGrid] = useState(false);

  // Widget configuration state
  const [widgetConfigs, setWidgetConfigs] = useState({});
  const [showWidgetLibrary, setShowWidgetLibrary] = useState(false);
  const [savedLayouts, setSavedLayouts] = useState({});

  // Load saved layouts and configurations
  useEffect(() => {
    const saved = localStorage.getItem('bdc_dashboard_layouts');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSavedLayouts(parsed.layouts || {});
        setWidgetConfigs(parsed.configs || {});
      } catch (error) {
        console.error('Error loading saved layouts:', error);
      }
    }
  }, []);

  // Fetch dashboard data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await requestAnalyticsData('dashboard');
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();
  }, [requestAnalyticsData]);

  // Handle drag end
  const handleDragEnd = useCallback((result) => {
    if (!result.destination || !editMode) return;

    const { source, destination, draggableId } = result;
    
    if (source.droppableId === 'widget-library' && destination.droppableId === 'dashboard') {
      // Adding new widget from library
      const widgetType = draggableId;
      const newWidget = {
        id: `${widgetType}_${Date.now()}`,
        type: widgetType,
        position: { 
          x: destination.index % gridSize.cols, 
          y: Math.floor(destination.index / gridSize.cols) 
        },
        size: WIDGET_TYPES[widgetType].defaultSize
      };
      
      setWidgets(prev => [...prev, newWidget]);
    } else if (source.droppableId === 'dashboard' && destination.droppableId === 'dashboard') {
      // Reordering existing widgets
      const newWidgets = Array.from(widgets);
      const [reorderedWidget] = newWidgets.splice(source.index, 1);
      
      // Update position based on destination
      reorderedWidget.position = {
        x: destination.index % gridSize.cols,
        y: Math.floor(destination.index / gridSize.cols)
      };
      
      newWidgets.splice(destination.index, 0, reorderedWidget);
      setWidgets(newWidgets);
    }
  }, [editMode, widgets, gridSize]);

  // Save layout
  const saveLayout = useCallback((name, description) => {
    const layoutData = {
      name,
      description,
      widgets: widgets,
      configs: widgetConfigs,
      created: new Date().toISOString(),
      gridSize
    };

    const updatedLayouts = {
      ...savedLayouts,
      [name.toLowerCase().replace(/\s+/g, '_')]: layoutData
    };

    setSavedLayouts(updatedLayouts);
    
    // Save to localStorage
    localStorage.setItem('bdc_dashboard_layouts', JSON.stringify({
      layouts: updatedLayouts,
      configs: widgetConfigs
    }));
  }, [widgets, widgetConfigs, savedLayouts, gridSize]);

  // Load layout
  const loadLayout = useCallback((layoutKey) => {
    if (DEFAULT_LAYOUTS[layoutKey]) {
      setWidgets(DEFAULT_LAYOUTS[layoutKey].widgets);
      setCurrentLayout(layoutKey);
    } else if (savedLayouts[layoutKey]) {
      const layout = savedLayouts[layoutKey];
      setWidgets(layout.widgets);
      setWidgetConfigs(layout.configs || {});
      setGridSize(layout.gridSize || { cols: 4, rows: 6 });
      setCurrentLayout(layoutKey);
    }
  }, [savedLayouts]);

  // Remove widget
  const removeWidget = useCallback((widgetId) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId));
    setSelectedWidget(null);
  }, []);

  // Duplicate widget
  const duplicateWidget = useCallback((widget) => {
    const newWidget = {
      ...widget,
      id: `${widget.type}_${Date.now()}`,
      position: { x: widget.position.x + 1, y: widget.position.y }
    };
    setWidgets(prev => [...prev, newWidget]);
  }, []);

  // Render widget content
  const renderWidgetContent = useCallback((widget) => {
    const config = widgetConfigs[widget.id] || {};
    
    switch (widget.type) {
      case 'metric_card':
        return (
          <MetricCard
            title={config.title || 'Metric'}
            value={dashboardData[config.metric] || '0'}
            change={config.showChange ? 5.2 : undefined}
            icon={Users}
            color={config.color || 'blue'}
          />
        );
        
      case 'line_chart':
        return (
          <TimeSeriesChart
            data={{
              labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
              datasets: [{
                label: config.title || 'Data',
                data: [65, 59, 80, 81, 56, 55],
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
              }]
            }}
            title={config.title || 'Time Series'}
            height={widget.size.h * 150}
          />
        );
        
      case 'bar_chart':
        return (
          <ComparisonChart
            data={{
              labels: ['Program A', 'Program B', 'Program C', 'Program D'],
              datasets: [{
                label: config.title || 'Data',
                data: [12, 19, 3, 5],
                backgroundColor: 'rgba(59, 130, 246, 0.8)'
              }]
            }}
            title={config.title || 'Comparison'}
            height={widget.size.h * 150}
          />
        );
        
      case 'pie_chart':
        return (
          <DistributionChart
            data={{
              labels: ['Active', 'Completed', 'On Hold', 'Cancelled'],
              datasets: [{
                data: [45, 30, 15, 10],
                backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
              }]
            }}
            title={config.title || 'Distribution'}
            height={widget.size.h * 150}
          />
        );
        
      case 'table':
        return (
          <Card className="p-4 h-full">
            <h3 className="font-semibold mb-4">{config.title || 'Data Table'}</h3>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Name</th>
                    <th className="text-left p-2">Value</th>
                    <th className="text-left p-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[1, 2, 3, 4, 5].map(i => (
                    <tr key={i} className="border-b">
                      <td className="p-2">Item {i}</td>
                      <td className="p-2">{Math.floor(Math.random() * 100)}</td>
                      <td className="p-2">
                        <Badge variant="default">Active</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        );
        
      case 'real_time':
        return (
          <Card className="p-4 h-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">{config.title || 'Real-time Monitor'}</h3>
              <Activity className="w-4 h-4 text-green-500 animate-pulse" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Active Users</span>
                <span className="font-medium text-blue-600">
                  {Math.floor(Math.random() * 100) + 50}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Live Sessions</span>
                <span className="font-medium text-green-600">
                  {Math.floor(Math.random() * 50) + 20}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">System Load</span>
                <span className="font-medium text-yellow-600">
                  {(Math.random() * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </Card>
        );
        
      default:
        return (
          <Card className="p-4 h-full flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Grid className="w-6 h-6" />
              </div>
              <p className="text-sm">Unknown Widget Type</p>
            </div>
          </Card>
        );
    }
  }, [widgetConfigs, dashboardData]);

  // Widget wrapper component
  const WidgetWrapper = ({ widget, index }) => (
    <div
      className={`relative h-full ${editMode ? 'ring-2 ring-blue-200 ring-opacity-50' : ''}`}
      style={{
        gridColumn: `span ${widget.size.w}`,
        gridRow: `span ${widget.size.h}`
      }}
    >
      {renderWidgetContent(widget)}
      
      {editMode && (
        <div className="absolute top-2 right-2 flex space-x-1">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setSelectedWidget(widget)}
            className="h-6 w-6 p-0"
          >
            <Settings className="w-3 h-3" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => duplicateWidget(widget)}
            className="h-6 w-6 p-0"
          >
            <Copy className="w-3 h-3" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => removeWidget(widget.id)}
            className="h-6 w-6 p-0"
          >
            <Trash2 className="w-3 h-3" />
          </Button>
        </div>
      )}
    </div>
  );

  // Widget library component
  const WidgetLibrary = () => (
    <Card className="p-4">
      <h3 className="font-semibold mb-4">Widget Library</h3>
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(WIDGET_TYPES).map(([type, config]) => (
          <Draggable key={type} draggableId={type} index={0}>
            {(provided, snapshot) => (
              <div
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
                className={`p-3 border rounded-lg cursor-move transition-all ${
                  snapshot.isDragging ? 'shadow-lg bg-blue-50' : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <config.icon className="w-4 h-4" />
                  <div>
                    <p className="text-sm font-medium">{config.name}</p>
                    <p className="text-xs text-gray-500">{config.description}</p>
                  </div>
                </div>
              </div>
            )}
          </Draggable>
        ))}
      </div>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Customizable analytics and reporting dashboard</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Switch
              checked={editMode}
              onCheckedChange={setEditMode}
              id="edit-mode"
            />
            <label htmlFor="edit-mode" className="text-sm font-medium">
              Edit Mode
            </label>
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              checked={showGrid}
              onCheckedChange={setShowGrid}
              id="show-grid"
            />
            <label htmlFor="show-grid" className="text-sm font-medium">
              Show Grid
            </label>
          </div>
          
          <Button
            variant="outline"
            onClick={() => setShowWidgetLibrary(!showWidgetLibrary)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Widgets
          </Button>
          
          <Button variant="outline">
            <Save className="w-4 h-4 mr-2" />
            Save Layout
          </Button>
        </div>
      </div>

      {/* Layout Selection */}
      <div className="flex items-center space-x-2">
        <label className="text-sm font-medium">Layout:</label>
        <select
          value={currentLayout}
          onChange={(e) => loadLayout(e.target.value)}
          className="px-3 py-1 border rounded-md text-sm"
        >
          <option value="overview">Overview Dashboard</option>
          <option value="performance">Performance Dashboard</option>
          <option value="training">Training Dashboard</option>
          {Object.keys(savedLayouts).map(key => (
            <option key={key} value={key}>{savedLayouts[key].name}</option>
          ))}
        </select>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Widget Library Sidebar */}
          <AnimatePresence>
            {(showWidgetLibrary && editMode) && (
              <motion.div
                initial={{ opacity: 0, x: -100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                className="lg:col-span-1"
              >
                <Droppable droppableId="widget-library">
                  {(provided) => (
                    <div ref={provided.innerRef} {...provided.droppableProps}>
                      <WidgetLibrary />
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Main Dashboard Grid */}
          <div className={showWidgetLibrary && editMode ? 'lg:col-span-4' : 'lg:col-span-5'}>
            <Droppable droppableId="dashboard">
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`grid gap-4 min-h-96 p-4 rounded-lg transition-colors ${
                    showGrid ? 'bg-gray-50' : ''
                  } ${
                    snapshot.isDraggingOver ? 'bg-blue-50' : ''
                  }`}
                  style={{
                    gridTemplateColumns: `repeat(${gridSize.cols}, 1fr)`,
                    gridTemplateRows: `repeat(${gridSize.rows}, minmax(150px, 1fr))`
                  }}
                >
                  {widgets.map((widget, index) => (
                    <Draggable
                      key={widget.id}
                      draggableId={widget.id}
                      index={index}
                      isDragDisabled={!editMode}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className={`transition-transform ${
                            snapshot.isDragging ? 'scale-105 shadow-lg' : ''
                          }`}
                        >
                          <WidgetWrapper widget={widget} index={index} />
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                  
                  {/* Empty state */}
                  {widgets.length === 0 && (
                    <div className="col-span-full flex items-center justify-center py-12">
                      <div className="text-center text-gray-500">
                        <Layout className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No widgets added yet</p>
                        <p className="text-sm">
                          {editMode ? 'Drag widgets from the library to get started' : 'Enable edit mode to customize this dashboard'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </Droppable>
          </div>
        </div>
      </DragDropContext>

      {/* Widget Configuration Modal */}
      <AnimatePresence>
        {selectedWidget && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedWidget(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg p-6 w-96 max-h-96 overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Configure Widget</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedWidget(null)}
                >
                  ✕
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Title</label>
                  <Input
                    value={widgetConfigs[selectedWidget.id]?.title || ''}
                    onChange={(e) => setWidgetConfigs(prev => ({
                      ...prev,
                      [selectedWidget.id]: {
                        ...prev[selectedWidget.id],
                        title: e.target.value
                      }
                    }))}
                    placeholder="Widget title"
                  />
                </div>
                
                {WIDGET_TYPES[selectedWidget.type]?.configurable.includes('metric') && (
                  <div>
                    <label className="text-sm font-medium mb-2 block">Metric</label>
                    <select
                      value={widgetConfigs[selectedWidget.id]?.metric || ''}
                      onChange={(e) => setWidgetConfigs(prev => ({
                        ...prev,
                        [selectedWidget.id]: {
                          ...prev[selectedWidget.id],
                          metric: e.target.value
                        }
                      }))}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">Select metric</option>
                      <option value="totalUsers">Total Users</option>
                      <option value="activeSessions">Active Sessions</option>
                      <option value="completionRate">Completion Rate</option>
                    </select>
                  </div>
                )}
                
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setSelectedWidget(null)}
                  >
                    Cancel
                  </Button>
                  <Button onClick={() => setSelectedWidget(null)}>
                    Save
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CustomizableDashboard;