// TODO: i18n - processed
/**
 * ChartRenderer Component
 * 
 * Advanced chart rendering with multiple chart types and interactive features
 */

import React, { useEffect, useRef, useState, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  ScatterController,
  BubbleController } from
'chart.js';
import {
  Bar,
  Line,
  Pie,
  Doughnut,
  Scatter,
  Bubble,
  PolarArea,
  Radar } from
'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '../../../../components/ui/card';
import { Alert, AlertDescription } from '../../../../components/ui/alert';
import { Skeleton } from '../../../../components/ui/skeleton';
import { Badge } from '../../../../components/ui/badge';
import { Button } from '../../../../components/ui/button';
import {
  Download,
  Maximize2,
  RefreshCw,
  Settings,
  TrendingUp,
  TrendingDown,
  Minus } from
'lucide-react';

// Register Chart.js components
import { useTranslation } from "react-i18next";ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  ScatterController,
  BubbleController
);

const COLOR_PALETTES = {
  default: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'],
  blue_scale: ['#0066cc', '#0080ff', '#3399ff', '#66b3ff', '#99ccff', '#cce6ff'],
  green_scale: ['#006600', '#009900', '#00cc00', '#33ff33', '#66ff66', '#99ff99'],
  warm: ['#ff6b6b', '#ffa500', '#ffd700', '#ff69b4', '#ff1493', '#dc143c'],
  cool: ['#00ced1', '#20b2aa', '#4682b4', '#6495ed', '#87ceeb', '#b0e0e6'],
  professional: ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#bdc3c7', '#ecf0f1']
};

const ChartRenderer = ({
  data = [],
  config = {},
  title = '',
  loading = false,
  error = null,
  onRefresh = null,
  onExport = null,
  onFullscreen = null,
  onConfigChange = null,
  interactive = true,
  height = 300,
  className = ''
}) => {const { t } = useTranslation();
  const chartRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chartError, setChartError] = useState(null);

  const chartType = config.chart_type || 'bar';
  const colorPalette = config.color_palette || 'default';

  // Process data for Chart.js format
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }

    try {
      const processedData = processDataForChart(data, config);
      return processedData;
    } catch (err) {
      setChartError(`Data processing error: ${err.message}`);
      return {
        labels: [],
        datasets: []
      };
    }
  }, [data, config]);

  // Chart options
  const chartOptions = useMemo(() => {
    return getChartOptions(config, chartType, {
      onRefresh,
      onExport,
      interactive
    });
  }, [config, chartType, onRefresh, onExport, interactive]);

  // Get chart component based on type
  const getChartComponent = () => {
    const components = {
      bar: Bar,
      line: Line,
      pie: Pie,
      doughnut: Doughnut,
      scatter: Scatter,
      bubble: Bubble,
      polarArea: PolarArea,
      radar: Radar
    };

    return components[chartType] || Bar;
  };

  const ChartComponent = getChartComponent();

  const handleExport = async (format = 'png') => {
    if (!chartRef.current) return;

    try {
      const canvas = chartRef.current.canvas;
      const url = canvas.toDataURL(`image/${format}`);

      // Create download link
      const link = document.createElement('a');
      link.download = `chart.${format}`;
      link.href = url;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      if (onExport) {
        onExport({ format, url });
      }
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    if (onFullscreen) {
      onFullscreen(!isFullscreen);
    }
  };

  const calculateTrend = () => {
    if (!data || data.length < 2 || chartType === 'pie' || chartType === 'doughnut') {
      return null;
    }

    // Simple trend calculation for line/bar charts
    const values = data.map((item) => {
      const yField = config.y_axis;
      return parseFloat(item[yField]) || 0;
    });

    if (values.length < 2) return null;

    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const change = lastValue - firstValue;
    const percentChange = firstValue !== 0 ? change / firstValue * 100 : 0;

    return {
      change,
      percentChange,
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral'
    };
  };

  const trend = calculateTrend();

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-8 w-8 rounded" />
          </div>
        </CardHeader>
        <CardContent>
          <Skeleton className="w-full" style={{ height: height }} />
        </CardContent>
      </Card>);

  }

  if (error || chartError) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            {title || 'Chart'}
            {onRefresh &&
            <Button variant="outline" size="sm" onClick={onRefresh}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            }
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              {error || chartError}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>);

  }

  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-sm">{title || 'Chart'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className="flex items-center justify-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg"
            style={{ height }}>

            <div className="text-center">
              <p className="text-sm">{t("components.no_data_available")}</p>
              <p className="text-xs text-gray-400 mt-1">{t("reporting.configure_data_source_to_display_chart")}

              </p>
            </div>
          </div>
        </CardContent>
      </Card>);

  }

  return (
    <Card className={`${className} ${isFullscreen ? 'fixed inset-4 z-50' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CardTitle className="text-sm">{title || 'Chart'}</CardTitle>
            {trend &&
            <div className="flex items-center space-x-1">
                {trend.direction === 'up' &&
              <TrendingUp className="h-4 w-4 text-green-600" />
              }
                {trend.direction === 'down' &&
              <TrendingDown className="h-4 w-4 text-red-600" />
              }
                {trend.direction === 'neutral' &&
              <Minus className="h-4 w-4 text-gray-600" />
              }
                <Badge
                variant={trend.direction === 'up' ? 'default' : trend.direction === 'down' ? 'destructive' : 'secondary'}
                className="text-xs">

                  {trend.percentChange > 0 ? '+' : ''}{trend.percentChange.toFixed(1)}%
                </Badge>
              </div>
            }
          </div>

          <div className="flex items-center space-x-1">
            {data.length > 0 &&
            <Badge variant="outline" className="text-xs">
                {data.length} records
              </Badge>
            }

            {interactive &&
            <>
                {onRefresh &&
              <Button variant="ghost" size="sm" onClick={onRefresh}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
              }

                <Button variant="ghost" size="sm" onClick={() => handleExport('png')}>
                  <Download className="h-4 w-4" />
                </Button>

                <Button variant="ghost" size="sm" onClick={handleFullscreen}>
                  <Maximize2 className="h-4 w-4" />
                </Button>

                {onConfigChange &&
              <Button variant="ghost" size="sm" onClick={onConfigChange}>
                    <Settings className="h-4 w-4" />
                  </Button>
              }
              </>
            }
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div style={{ height: isFullscreen ? 'calc(100vh - 200px)' : height }}>
          <ChartComponent
            ref={chartRef}
            data={chartData}
            options={chartOptions} />

        </div>
      </CardContent>
    </Card>);

};

// Helper function to process data for Chart.js
function processDataForChart(data, config) {
  const chartType = config.chart_type || 'bar';
  const xField = config.x_axis;
  const yField = config.y_axis;
  const groupField = config.group_by;
  const colorPalette = COLOR_PALETTES[config.color_palette] || COLOR_PALETTES.default;

  if (!xField || !yField) {
    throw new Error('Both x_axis and y_axis are required');
  }

  // Extract labels (x-axis values)
  const labels = [...new Set(data.map((item) => item[xField]))].sort();

  if (groupField) {
    // Grouped data
    const groups = [...new Set(data.map((item) => item[groupField]))];
    const datasets = groups.map((group, index) => {
      const groupData = data.filter((item) => item[groupField] === group);
      const dataPoints = labels.map((label) => {
        const item = groupData.find((d) => d[xField] === label);
        return item ? parseFloat(item[yField]) || 0 : 0;
      });

      const color = colorPalette[index % colorPalette.length];

      return {
        label: group,
        data: dataPoints,
        backgroundColor: chartType === 'line' ? `${color}20` : color,
        borderColor: color,
        borderWidth: chartType === 'line' ? 2 : 1,
        fill: chartType === 'area',
        tension: chartType === 'line' ? 0.4 : undefined
      };
    });

    return { labels, datasets };
  } else {
    // Single dataset
    const dataPoints = labels.map((label) => {
      const item = data.find((d) => d[xField] === label);
      return item ? parseFloat(item[yField]) || 0 : 0;
    });

    const color = colorPalette[0];

    const dataset = {
      label: yField,
      data: dataPoints,
      backgroundColor: chartType === 'pie' || chartType === 'doughnut' ?
      colorPalette.slice(0, labels.length) :
      chartType === 'line' ? `${color}20` : color,
      borderColor: chartType === 'pie' || chartType === 'doughnut' ?
      colorPalette.slice(0, labels.length) :
      color,
      borderWidth: chartType === 'line' ? 2 : 1,
      fill: chartType === 'area',
      tension: chartType === 'line' ? 0.4 : undefined
    };

    return { labels, datasets: [dataset] };
  }
}

// Helper function to generate chart options
function getChartOptions(config, chartType, callbacks = {}) {
  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: config.show_legend !== false,
        position: config.legend_position || 'top'
      },
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false
      }
    }
  };

  // Chart-specific options
  if (chartType === 'line' || chartType === 'bar') {
    baseOptions.scales = {
      x: {
        display: true,
        title: {
          display: !!config.x_label,
          text: config.x_label || ''
        },
        grid: {
          display: config.show_grid !== false
        }
      },
      y: {
        display: true,
        title: {
          display: !!config.y_label,
          text: config.y_label || ''
        },
        grid: {
          display: config.show_grid !== false
        },
        beginAtZero: config.start_from_zero !== false
      }
    };

    // Stacked configuration
    if (config.stacked) {
      baseOptions.scales.x.stacked = true;
      baseOptions.scales.y.stacked = true;
    }
  }

  // Pie/Doughnut specific options
  if (chartType === 'pie' || chartType === 'doughnut') {
    baseOptions.plugins.tooltip = {
      callbacks: {
        label: function (context) {
          const label = context.label || '';
          const value = context.parsed;
          const total = context.dataset.data.reduce((a, b) => a + b, 0);
          const percentage = (value / total * 100).toFixed(1);
          return `${label}: ${value} (${percentage}%)`;
        }
      }
    };
  }

  // Animation options
  if (config.animated !== false) {
    baseOptions.animation = {
      duration: config.animation_duration || 1000,
      easing: config.animation_easing || 'easeInOutQuart'
    };
  }

  // Interaction options
  if (callbacks.interactive !== false) {
    baseOptions.interaction = {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    };
  }

  return baseOptions;
}

export default ChartRenderer;