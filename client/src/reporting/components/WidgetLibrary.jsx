// TODO: i18n - processed
/**
 * WidgetLibrary Component
 * 
 * Displays available widgets that can be dragged into the dashboard
 */

import React, { useState } from 'react';
import { useDrag } from 'react-dnd';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Input } from '../../../components/ui/input';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../../../components/ui/accordion';
import {
  Search,
  BarChart3,
  Gauge,
  Table,
  Map,
  Calendar,
  Progress,
  Type,
  Plus,
  Info } from
'lucide-react';import { useTranslation } from "react-i18next";

const WIDGET_TYPES = {
  chart: {
    name: 'Chart Widget',
    description: 'Display data in various chart formats (bar, line, pie, etc.)',
    icon: BarChart3,
    category: 'visualization',
    color: 'blue',
    features: ['Multiple chart types', 'Grouping', 'Aggregation', 'Interactive']
  },
  metric: {
    name: 'Metric Widget',
    description: 'Show key performance indicators and metrics',
    icon: Gauge,
    category: 'visualization',
    color: 'green',
    features: ['KPI display', 'Comparison', 'Goal tracking', 'Trends']
  },
  table: {
    name: 'Data Table',
    description: 'Display data in tabular format with sorting and filtering',
    icon: Table,
    category: 'data',
    color: 'purple',
    features: ['Sorting', 'Filtering', 'Pagination', 'Export']
  },
  map: {
    name: 'Geographic Map',
    description: 'Show data on interactive maps with various overlays',
    icon: Map,
    category: 'visualization',
    color: 'orange',
    features: ['Interactive maps', 'Markers', 'Heatmaps', 'Clustering']
  },
  calendar: {
    name: 'Calendar View',
    description: 'Display scheduled events and appointments',
    icon: Calendar,
    category: 'data',
    color: 'indigo',
    features: ['Multiple views', 'Event management', 'Date filtering', 'Color coding']
  },
  progress: {
    name: 'Progress Tracker',
    description: 'Track progress towards goals with visual indicators',
    icon: Progress,
    category: 'visualization',
    color: 'teal',
    features: ['Goal tracking', 'Progress bars', 'Percentage display', 'Multiple styles']
  },
  text: {
    name: 'Text Widget',
    description: 'Display custom text, markdown, or HTML content',
    icon: Type,
    category: 'content',
    color: 'gray',
    features: ['Markdown support', 'HTML rendering', 'Custom styling', 'Rich text']
  }
};

const WIDGET_CATEGORIES = {
  visualization: {
    name: 'Visualization',
    description: 'Charts, graphs, and visual data representations',
    icon: BarChart3
  },
  data: {
    name: 'Data Display',
    description: 'Tables, lists, and structured data views',
    icon: Table
  },
  content: {
    name: 'Content',
    description: 'Text, media, and informational widgets',
    icon: Type
  }
};

const DraggableWidget = ({ widgetType, widget }) => {const { t } = useTranslation();
  const [{ isDragging }, drag] = useDrag({
    type: 'widget',
    item: { widgetType, widget },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  const IconComponent = widget.icon;
  const colorClasses = {
    blue: 'border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700',
    green: 'border-green-200 bg-green-50 hover:bg-green-100 text-green-700',
    purple: 'border-purple-200 bg-purple-50 hover:bg-purple-100 text-purple-700',
    orange: 'border-orange-200 bg-orange-50 hover:bg-orange-100 text-orange-700',
    indigo: 'border-indigo-200 bg-indigo-50 hover:bg-indigo-100 text-indigo-700',
    teal: 'border-teal-200 bg-teal-50 hover:bg-teal-100 text-teal-700',
    gray: 'border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-700'
  };

  return (
    <div
      ref={drag}
      className={`
        p-4 border-2 rounded-lg cursor-move transition-all
        ${colorClasses[widget.color]}
        ${isDragging ? 'opacity-50 shadow-lg scale-105' : 'hover:shadow-md'}
      `}>

      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          <IconComponent className="h-6 w-6" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm mb-1">
            {widget.name}
          </h4>
          <p className="text-xs opacity-80 line-clamp-2">
            {widget.description}
          </p>
          <div className="mt-2 flex flex-wrap gap-1">
            {widget.features.slice(0, 2).map((feature, index) =>
            <Badge
              key={index}
              variant="secondary"
              className="text-xs px-1 py-0">

                {feature}
              </Badge>
            )}
            {widget.features.length > 2 &&
            <Badge variant="outline" className="text-xs px-1 py-0">
                +{widget.features.length - 2}
              </Badge>
            }
          </div>
        </div>
      </div>
    </div>);

};

const WidgetPreview = ({ widgetType, widget, onAdd }) => {const { t } = useTranslation();
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center space-x-2">
          <widget.icon className="h-5 w-5 text-gray-600" />
          <CardTitle className="text-sm">{widget.name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-xs text-gray-600">
          {widget.description}
        </p>
        
        <div className="space-y-2">
          <h5 className="text-xs font-medium text-gray-700">Features:</h5>
          <div className="flex flex-wrap gap-1">
            {widget.features.map((feature, index) =>
            <Badge
              key={index}
              variant="outline"
              className="text-xs">

                {feature}
              </Badge>
            )}
          </div>
        </div>

        <Button
          size="sm"
          onClick={() => onAdd(widgetType)}
          className="w-full">

          <Plus className="h-3 w-3 mr-1" />
          Add Widget
        </Button>
      </CardContent>
    </Card>);

};

const WidgetLibrary = ({ onWidgetAdd, readonly = false }) => {const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('drag'); // drag, preview
  const [expandedCategories, setExpandedCategories] = useState(['visualization']);

  // Filter widgets based on search term
  const filteredWidgets = React.useMemo(() => {
    if (!searchTerm) return WIDGET_TYPES;

    const filtered = {};
    Object.entries(WIDGET_TYPES).forEach(([key, widget]) => {
      const searchLower = searchTerm.toLowerCase();
      if (
      widget.name.toLowerCase().includes(searchLower) ||
      widget.description.toLowerCase().includes(searchLower) ||
      widget.features.some((f) => f.toLowerCase().includes(searchLower)) ||
      widget.category.toLowerCase().includes(searchLower))
      {
        filtered[key] = widget;
      }
    });

    return filtered;
  }, [searchTerm]);

  // Group widgets by category
  const widgetsByCategory = React.useMemo(() => {
    const grouped = {};

    Object.entries(filteredWidgets).forEach(([key, widget]) => {
      const category = widget.category;
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push({ key, ...widget });
    });

    return grouped;
  }, [filteredWidgets]);

  const handleWidgetAdd = (widgetType) => {
    if (onWidgetAdd) {
      onWidgetAdd(widgetType);
    }
  };

  if (readonly) {
    return (
      <div className="p-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Widget Library</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500">
              This dashboard is in read-only mode. Widgets cannot be added or modified.
            </p>
          </CardContent>
        </Card>
      </div>);

  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">
            Widget Library
          </h3>
          <div className="flex space-x-1">
            <Button
              variant={viewMode === 'drag' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('drag')}>{t("reporting.drag")}


            </Button>
            <Button
              variant={viewMode === 'preview' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('preview')}>{t("components.preview")}


            </Button>
          </div>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search widgets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10" />

        </div>

        {/* Stats */}
        <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
          <span>{Object.keys(filteredWidgets).length} widgets available</span>
          {searchTerm &&
          <span>
              in {Object.keys(widgetsByCategory).length} categor{Object.keys(widgetsByCategory).length !== 1 ? 'ies' : 'y'}
            </span>
          }
        </div>
      </div>

      {/* Widget List */}
      <div className="flex-1 overflow-auto">
        {Object.keys(widgetsByCategory).length === 0 ?
        <div className="p-4 text-center text-gray-500">
            {searchTerm ? 'No widgets match your search.' : 'No widgets available.'}
          </div> :

        <div className="p-4">
            {viewMode === 'drag' ?
          <Accordion
            type="multiple"
            value={expandedCategories}
            onValueChange={setExpandedCategories}
            className="w-full">

                {Object.entries(widgetsByCategory).map(([category, widgets]) => {
              const categoryInfo = WIDGET_CATEGORIES[category];
              return (
                <AccordionItem key={category} value={category} className="border-0">
                      <AccordionTrigger className="py-3 hover:bg-gray-50 rounded-lg px-2">
                        <div className="flex items-center space-x-2">
                          <categoryInfo.icon className="h-4 w-4 text-blue-600" />
                          <span className="font-medium">{categoryInfo.name}</span>
                          <Badge variant="secondary" className="ml-auto">
                            {widgets.length}
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-2 pb-2">
                        <p className="text-xs text-gray-600 mb-3">
                          {categoryInfo.description}
                        </p>
                        <div className="space-y-3">
                          {widgets.map((widget) =>
                      <DraggableWidget
                        key={widget.key}
                        widgetType={widget.key}
                        widget={widget} />

                      )}
                        </div>
                      </AccordionContent>
                    </AccordionItem>);

            })}
              </Accordion> :

          <div className="grid grid-cols-1 gap-4">
                {Object.entries(widgetsByCategory).map(([category, widgets]) => {
              const categoryInfo = WIDGET_CATEGORIES[category];
              return (
                <div key={category} className="space-y-3">
                      <div className="flex items-center space-x-2">
                        <categoryInfo.icon className="h-4 w-4 text-blue-600" />
                        <h4 className="font-medium text-sm">{categoryInfo.name}</h4>
                        <Badge variant="secondary" className="text-xs">
                          {widgets.length}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-1 gap-3">
                        {widgets.map((widget) =>
                    <WidgetPreview
                      key={widget.key}
                      widgetType={widget.key}
                      widget={widget}
                      onAdd={handleWidgetAdd} />

                    )}
                      </div>
                    </div>);

            })}
              </div>
          }
          </div>
        }
      </div>

      {/* Footer */}
      {viewMode === 'drag' &&
      <div className="p-4 border-t bg-gray-50">
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Drag widgets to the dashboard canvas</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Drop to add and position widgets</span>
            </div>
            <div className="flex items-center space-x-2">
              <Info className="h-3 w-3 text-gray-400" />
              <span>Widgets can be resized and repositioned</span>
            </div>
          </div>
        </div>
      }
    </div>);

};

export default WidgetLibrary;