import React, { useState } from 'react';
import { Draggable, Droppable } from '@hello-pangea/dnd';
import {
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  Table2,
  Type,
  Image,
  Square,
  Circle,
  Triangle,
  Activity,
  Users,
  DollarSign,
  Target,
  Award,
  BookOpen,
  Calendar,
  Clock,
  Hash,
  Percent,
  Filter,
  Search
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';

const WidgetLibrary = ({ darkMode }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');

  const widgetCategories = {
    charts: {
      name: 'Charts',
      icon: BarChart3,
      widgets: [
        { id: 'bar-chart', name: 'Bar Chart', icon: BarChart3, type: 'chart', config: { chartType: 'bar' } },
        { id: 'line-chart', name: 'Line Chart', icon: LineChart, type: 'chart', config: { chartType: 'line' } },
        { id: 'pie-chart', name: 'Pie Chart', icon: PieChart, type: 'chart', config: { chartType: 'pie' } },
        { id: 'donut-chart', name: 'Donut Chart', icon: Circle, type: 'chart', config: { chartType: 'donut' } },
        { id: 'area-chart', name: 'Area Chart', icon: Activity, type: 'chart', config: { chartType: 'area' } },
        { id: 'radar-chart', name: 'Radar Chart', icon: Triangle, type: 'chart', config: { chartType: 'radar' } },
      ]
    },
    kpis: {
      name: 'KPIs',
      icon: TrendingUp,
      widgets: [
        { id: 'kpi-trend', name: 'KPI with Trend', icon: TrendingUp, type: 'kpi', config: { showTrend: true } },
        { id: 'kpi-users', name: 'Users KPI', icon: Users, type: 'kpi', config: { icon: 'users' } },
        { id: 'kpi-revenue', name: 'Revenue KPI', icon: DollarSign, type: 'kpi', config: { icon: 'dollar' } },
        { id: 'kpi-target', name: 'Target KPI', icon: Target, type: 'kpi', config: { icon: 'target' } },
        { id: 'kpi-achievement', name: 'Achievement KPI', icon: Award, type: 'kpi', config: { icon: 'award' } },
        { id: 'kpi-progress', name: 'Progress KPI', icon: Percent, type: 'kpi', config: { showProgress: true } },
      ]
    },
    tables: {
      name: 'Tables',
      icon: Table2,
      widgets: [
        { id: 'basic-table', name: 'Basic Table', icon: Table2, type: 'table', config: { variant: 'basic' } },
        { id: 'sortable-table', name: 'Sortable Table', icon: Table2, type: 'table', config: { sortable: true } },
        { id: 'filterable-table', name: 'Filterable Table', icon: Filter, type: 'table', config: { filterable: true } },
        { id: 'paginated-table', name: 'Paginated Table', icon: Hash, type: 'table', config: { paginated: true } },
        { id: 'pivot-table', name: 'Pivot Table', icon: Table2, type: 'table', config: { variant: 'pivot' } },
      ]
    },
    content: {
      name: 'Content',
      icon: Type,
      widgets: [
        { id: 'text-block', name: 'Text Block', icon: Type, type: 'text', config: {} },
        { id: 'rich-text', name: 'Rich Text', icon: Type, type: 'text', config: { richText: true } },
        { id: 'image', name: 'Image', icon: Image, type: 'image', config: {} },
        { id: 'logo', name: 'Logo', icon: Square, type: 'image', config: { isLogo: true } },
        { id: 'divider', name: 'Divider', icon: Square, type: 'divider', config: {} },
      ]
    },
    advanced: {
      name: 'Advanced',
      icon: Activity,
      widgets: [
        { id: 'timeline', name: 'Timeline', icon: Clock, type: 'timeline', config: {} },
        { id: 'calendar-view', name: 'Calendar View', icon: Calendar, type: 'calendar', config: {} },
        { id: 'progress-bars', name: 'Progress Bars', icon: Activity, type: 'progress', config: {} },
        { id: 'skill-matrix', name: 'Skill Matrix', icon: BookOpen, type: 'matrix', config: {} },
      ]
    }
  };

  const allWidgets = Object.values(widgetCategories).flatMap(cat => cat.widgets);
  
  const filteredWidgets = activeCategory === 'all' 
    ? allWidgets.filter(widget => 
        widget.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : widgetCategories[activeCategory]?.widgets.filter(widget =>
        widget.name.toLowerCase().includes(searchTerm.toLowerCase())
      ) || [];

  const renderWidget = (widget, index) => (
    <Draggable
      key={widget.id}
      draggableId={widget.id}
      index={index}
      isDragDisabled={false}
    >
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`
            p-3 rounded-lg border cursor-move transition-all
            ${snapshot.isDragging 
              ? 'shadow-lg scale-105 bg-blue-50 dark:bg-blue-900 border-blue-300 dark:border-blue-700' 
              : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }
          `}
        >
          <div className="flex items-center space-x-3">
            <div className={`
              p-2 rounded-md
              ${snapshot.isDragging 
                ? 'bg-blue-100 dark:bg-blue-800' 
                : 'bg-gray-100 dark:bg-gray-700'
              }
            `}>
              <widget.icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                {widget.name}
              </h4>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Drag to add
              </p>
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-3">Widget Library</h3>
        
        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search widgets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Category Tabs */}
        <Tabs value={activeCategory} onValueChange={setActiveCategory}>
          <TabsList className="grid grid-cols-3 gap-1">
            <TabsTrigger value="all" className="text-xs">All</TabsTrigger>
            <TabsTrigger value="charts" className="text-xs">Charts</TabsTrigger>
            <TabsTrigger value="kpis" className="text-xs">KPIs</TabsTrigger>
          </TabsList>
          <TabsList className="grid grid-cols-3 gap-1 mt-1">
            <TabsTrigger value="tables" className="text-xs">Tables</TabsTrigger>
            <TabsTrigger value="content" className="text-xs">Content</TabsTrigger>
            <TabsTrigger value="advanced" className="text-xs">Advanced</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <ScrollArea className="flex-1 p-4">
        <Droppable 
          droppableId="widget-library" 
          type="WIDGET"
          isDropDisabled={true}
        >
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="space-y-2"
            >
              {filteredWidgets.length > 0 ? (
                filteredWidgets.map((widget, index) => renderWidget(widget, index))
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400">
                    No widgets found matching "{searchTerm}"
                  </p>
                </div>
              )}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </ScrollArea>

      {/* Widget Tips */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
        <h4 className="text-sm font-medium mb-2">Tips:</h4>
        <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
          <li>• Drag widgets to add them to your report</li>
          <li>• Drop widgets between sections to reorder</li>
          <li>• Click on a widget to configure it</li>
          <li>• Use filters to find specific widget types</li>
        </ul>
      </div>
    </div>
  );
};

export default WidgetLibrary;