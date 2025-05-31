import React, { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import {
  GripVertical,
  Settings,
  Trash2,
  TrendingUp,
  TrendingDown,
  Minus,
  Edit2,
  Check,
  X,
  Download,
  Maximize2
} from 'lucide-react';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Switch } from '../ui/switch';
import { Textarea } from '../ui/textarea';

// Sample data for widgets
const generateSampleData = (type) => {
  const chartData = [
    { name: 'Jan', value: 4000, value2: 2400 },
    { name: 'Feb', value: 3000, value2: 2210 },
    { name: 'Mar', value: 5000, value2: 2290 },
    { name: 'Apr', value: 4500, value2: 2000 },
    { name: 'May', value: 6000, value2: 2181 },
    { name: 'Jun', value: 5500, value2: 2500 },
  ];

  const pieData = [
    { name: 'Group A', value: 400, color: '#3b82f6' },
    { name: 'Group B', value: 300, color: '#10b981' },
    { name: 'Group C', value: 300, color: '#f59e0b' },
    { name: 'Group D', value: 200, color: '#ef4444' },
  ];

  const radarData = [
    { subject: 'Math', A: 120, B: 110, fullMark: 150 },
    { subject: 'Chinese', A: 98, B: 130, fullMark: 150 },
    { subject: 'English', A: 86, B: 130, fullMark: 150 },
    { subject: 'Geography', A: 99, B: 100, fullMark: 150 },
    { subject: 'Physics', A: 85, B: 90, fullMark: 150 },
    { subject: 'History', A: 65, B: 85, fullMark: 150 },
  ];

  const tableData = [
    { id: 1, name: 'John Doe', role: 'Student', progress: 75, status: 'Active' },
    { id: 2, name: 'Jane Smith', role: 'Student', progress: 92, status: 'Active' },
    { id: 3, name: 'Bob Johnson', role: 'Student', progress: 68, status: 'Active' },
    { id: 4, name: 'Alice Brown', role: 'Student', progress: 45, status: 'Inactive' },
    { id: 5, name: 'Charlie Wilson', role: 'Student', progress: 88, status: 'Active' },
  ];

  switch (type) {
    case 'pie':
    case 'donut':
      return pieData;
    case 'radar':
      return radarData;
    case 'table':
      return tableData;
    default:
      return chartData;
  }
};

const ReportWidget = ({
  widget,
  darkMode,
  onUpdate,
  onDelete,
  dragHandleProps,
  isDragging
}) => {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [localConfig, setLocalConfig] = useState(widget.config);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Generate sample data based on widget type
  const sampleData = useMemo(() => {
    if (widget.type === 'chart') {
      return generateSampleData(widget.config.chartType);
    } else if (widget.type === 'table') {
      return generateSampleData('table');
    }
    return null;
  }, [widget.type, widget.config.chartType]);

  const handleConfigSave = () => {
    onUpdate({ config: localConfig });
    setIsConfigOpen(false);
  };

  const handleConfigCancel = () => {
    setLocalConfig(widget.config);
    setIsConfigOpen(false);
  };

  const renderChart = () => {
    const { chartType, colors, showLegend, showGrid } = widget.config;
    const chartColors = colors || ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sampleData}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              {showLegend && <Legend />}
              <Bar dataKey="value" fill={chartColors[0]} />
              <Bar dataKey="value2" fill={chartColors[1]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sampleData}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              {showLegend && <Legend />}
              <Line type="monotone" dataKey="value" stroke={chartColors[0]} />
              <Line type="monotone" dataKey="value2" stroke={chartColors[1]} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={sampleData}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              {showLegend && <Legend />}
              <Area type="monotone" dataKey="value" stroke={chartColors[0]} fill={chartColors[0]} fillOpacity={0.6} />
              <Area type="monotone" dataKey="value2" stroke={chartColors[1]} fill={chartColors[1]} fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sampleData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label
              >
                {sampleData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              {showLegend && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        );

      case 'donut':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sampleData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label
              >
                {sampleData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              {showLegend && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        );

      case 'radar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={sampleData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" />
              <PolarRadiusAxis />
              <Radar name="Series A" dataKey="A" stroke={chartColors[0]} fill={chartColors[0]} fillOpacity={0.6} />
              <Radar name="Series B" dataKey="B" stroke={chartColors[1]} fill={chartColors[1]} fillOpacity={0.6} />
              {showLegend && <Legend />}
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  const renderKPI = () => {
    const { title, value, unit, trend, trendValue, color, showProgress } = widget.config;
    const trendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
    const TrendIcon = trendIcon;
    const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600';

    return (
      <div className="p-6">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
          {title || 'KPI Title'}
        </h3>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-bold" style={{ color: color || '#3b82f6' }}>
            {value || 0}
          </span>
          {unit && <span className="text-lg text-gray-500">{unit}</span>}
        </div>
        {trendValue !== undefined && (
          <div className={`flex items-center mt-2 ${trendColor}`}>
            <TrendIcon className="w-4 h-4 mr-1" />
            <span className="text-sm font-medium">{trendValue}%</span>
            <span className="text-sm text-gray-500 ml-1">vs last period</span>
          </div>
        )}
        {showProgress && (
          <div className="mt-4">
            <Progress value={value || 0} className="h-2" />
          </div>
        )}
      </div>
    );
  };

  const renderTable = () => {
    const { title, pageSize, sortable, filterable } = widget.config;

    return (
      <div className="p-4">
        {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b dark:border-gray-700">
                <th className="text-left p-2">Name</th>
                <th className="text-left p-2">Role</th>
                <th className="text-left p-2">Progress</th>
                <th className="text-left p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {sampleData?.slice(0, pageSize || 5).map((row) => (
                <tr key={row.id} className="border-b dark:border-gray-700">
                  <td className="p-2">{row.name}</td>
                  <td className="p-2">{row.role}</td>
                  <td className="p-2">
                    <div className="flex items-center space-x-2">
                      <Progress value={row.progress} className="w-20 h-2" />
                      <span className="text-xs">{row.progress}%</span>
                    </div>
                  </td>
                  <td className="p-2">
                    <Badge variant={row.status === 'Active' ? 'default' : 'secondary'}>
                      {row.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderText = () => {
    const { content, fontSize, alignment } = widget.config;
    const alignmentClass = alignment === 'center' ? 'text-center' : alignment === 'right' ? 'text-right' : 'text-left';
    const sizeClass = fontSize === 'small' ? 'text-sm' : fontSize === 'large' ? 'text-lg' : 'text-base';

    return (
      <div className={`p-4 ${alignmentClass} ${sizeClass}`}>
        <div dangerouslySetInnerHTML={{ __html: content || '<p>Enter text here...</p>' }} />
      </div>
    );
  };

  const renderImage = () => {
    const { src, alt, width, height, alignment } = widget.config;
    const alignmentClass = alignment === 'center' ? 'mx-auto' : alignment === 'right' ? 'ml-auto' : '';

    return (
      <div className="p-4">
        {src ? (
          <img
            src={src}
            alt={alt || 'Image'}
            style={{ width: width || '100%', height: height || 'auto' }}
            className={`rounded-lg ${alignmentClass}`}
          />
        ) : (
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
            <p className="text-gray-500">No image selected</p>
          </div>
        )}
      </div>
    );
  };

  const renderWidget = () => {
    switch (widget.type) {
      case 'chart':
        return renderChart();
      case 'kpi':
        return renderKPI();
      case 'table':
        return renderTable();
      case 'text':
        return renderText();
      case 'image':
        return renderImage();
      default:
        return (
          <div className="p-8 text-center text-gray-500">
            <p>Widget type not supported: {widget.type}</p>
          </div>
        );
    }
  };

  const renderConfigDialog = () => {
    switch (widget.type) {
      case 'chart':
        return (
          <Tabs defaultValue="general" className="w-full">
            <TabsList>
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
              <TabsTrigger value="data">Data</TabsTrigger>
            </TabsList>
            <TabsContent value="general" className="space-y-4">
              <div>
                <Label>Chart Title</Label>
                <Input
                  value={localConfig.title || ''}
                  onChange={(e) => setLocalConfig({ ...localConfig, title: e.target.value })}
                  placeholder="Enter chart title"
                />
              </div>
              <div>
                <Label>Chart Type</Label>
                <Select
                  value={localConfig.chartType}
                  onValueChange={(value) => setLocalConfig({ ...localConfig, chartType: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bar">Bar Chart</SelectItem>
                    <SelectItem value="line">Line Chart</SelectItem>
                    <SelectItem value="area">Area Chart</SelectItem>
                    <SelectItem value="pie">Pie Chart</SelectItem>
                    <SelectItem value="donut">Donut Chart</SelectItem>
                    <SelectItem value="radar">Radar Chart</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
            <TabsContent value="appearance" className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Show Legend</Label>
                <Switch
                  checked={localConfig.showLegend}
                  onCheckedChange={(checked) => setLocalConfig({ ...localConfig, showLegend: checked })}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>Show Grid</Label>
                <Switch
                  checked={localConfig.showGrid}
                  onCheckedChange={(checked) => setLocalConfig({ ...localConfig, showGrid: checked })}
                />
              </div>
            </TabsContent>
            <TabsContent value="data" className="space-y-4">
              <div>
                <Label>Data Source</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select data source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beneficiaries">Beneficiaries</SelectItem>
                    <SelectItem value="programs">Programs</SelectItem>
                    <SelectItem value="evaluations">Evaluations</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>
        );

      case 'kpi':
        return (
          <div className="space-y-4">
            <div>
              <Label>KPI Title</Label>
              <Input
                value={localConfig.title || ''}
                onChange={(e) => setLocalConfig({ ...localConfig, title: e.target.value })}
                placeholder="Enter KPI title"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Value</Label>
                <Input
                  type="number"
                  value={localConfig.value || 0}
                  onChange={(e) => setLocalConfig({ ...localConfig, value: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <Label>Unit</Label>
                <Input
                  value={localConfig.unit || ''}
                  onChange={(e) => setLocalConfig({ ...localConfig, unit: e.target.value })}
                  placeholder="%, $, etc."
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Trend</Label>
                <Select
                  value={localConfig.trend || 'neutral'}
                  onValueChange={(value) => setLocalConfig({ ...localConfig, trend: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="up">Up</SelectItem>
                    <SelectItem value="down">Down</SelectItem>
                    <SelectItem value="neutral">Neutral</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Trend Value (%)</Label>
                <Input
                  type="number"
                  value={localConfig.trendValue || 0}
                  onChange={(e) => setLocalConfig({ ...localConfig, trendValue: parseFloat(e.target.value) })}
                />
              </div>
            </div>
            <div>
              <Label>Color</Label>
              <Input
                type="color"
                value={localConfig.color || '#3b82f6'}
                onChange={(e) => setLocalConfig({ ...localConfig, color: e.target.value })}
                className="h-10"
              />
            </div>
            <div className="flex items-center justify-between">
              <Label>Show Progress Bar</Label>
              <Switch
                checked={localConfig.showProgress || false}
                onCheckedChange={(checked) => setLocalConfig({ ...localConfig, showProgress: checked })}
              />
            </div>
          </div>
        );

      case 'text':
        return (
          <div className="space-y-4">
            <div>
              <Label>Content</Label>
              <Textarea
                value={localConfig.content || ''}
                onChange={(e) => setLocalConfig({ ...localConfig, content: e.target.value })}
                placeholder="Enter your text content..."
                rows={6}
              />
            </div>
            <div>
              <Label>Font Size</Label>
              <Select
                value={localConfig.fontSize || 'base'}
                onValueChange={(value) => setLocalConfig({ ...localConfig, fontSize: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="small">Small</SelectItem>
                  <SelectItem value="base">Normal</SelectItem>
                  <SelectItem value="large">Large</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Alignment</Label>
              <Select
                value={localConfig.alignment || 'left'}
                onValueChange={(value) => setLocalConfig({ ...localConfig, alignment: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="left">Left</SelectItem>
                  <SelectItem value="center">Center</SelectItem>
                  <SelectItem value="right">Right</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );

      default:
        return <p>Configuration not available for this widget type.</p>;
    }
  };

  return (
    <>
      <Card
        className={`
          transition-all duration-200
          ${isDragging ? 'shadow-lg scale-105 opacity-90' : ''}
          ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'}
        `}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div
                {...dragHandleProps}
                className="cursor-move p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <GripVertical className="w-4 h-4 text-gray-400" />
              </div>
              {widget.config.title && (
                <h4 className="font-semibold text-sm">{widget.config.title}</h4>
              )}
            </div>
            <div className="flex items-center space-x-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsFullscreen(true)}
              >
                <Maximize2 className="w-4 h-4" />
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button size="sm" variant="ghost">
                    <Settings className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setIsConfigOpen(true)}>
                    <Edit2 className="w-4 h-4 mr-2" />
                    Configure
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Download className="w-4 h-4 mr-2" />
                    Export Data
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    onClick={onDelete}
                    className="text-red-600 dark:text-red-400"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-2">
          {renderWidget()}
        </CardContent>
      </Card>

      {/* Configuration Dialog */}
      <Dialog open={isConfigOpen} onOpenChange={setIsConfigOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Configure Widget</DialogTitle>
            <DialogDescription>
              Customize the appearance and behavior of this widget.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {renderConfigDialog()}
          </div>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={handleConfigCancel}>
              Cancel
            </Button>
            <Button onClick={handleConfigSave}>
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Fullscreen Dialog */}
      <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
        <DialogContent className="max-w-6xl h-[90vh]">
          <DialogHeader>
            <DialogTitle>{widget.config.title || 'Widget'}</DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-auto py-4">
            {renderWidget()}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ReportWidget;