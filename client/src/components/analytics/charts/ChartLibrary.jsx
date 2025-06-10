// Advanced Charts Library
// Comprehensive visualization components with drill-down capabilities

import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
} from 'chart.js';
import { Line, Bar, Pie, Doughnut, Radar, PolarArea } from 'react-chartjs-2';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  ZoomIn,
  Download,
  Maximize2,
  Filter,
  RefreshCw,
  Info,
  ChevronDown,
  Calendar,
  BarChart3,
  PieChart,
  Activity,
  Target
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { format, subDays, parseISO } from 'date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
);

// Base Chart Component with advanced features
export const BaseChart = ({
  type = 'line',
  data,
  options = {},
  title,
  description,
  showControls = true,
  showFilters = true,
  onDrillDown,
  onExport,
  onRefresh,
  loading = false,
  error = null,
  height = 400,
  className = ''
}) => {
  const chartRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [activeDataPoint, setActiveDataPoint] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);

  // Chart components mapping
  const ChartComponents = {
    line: Line,
    bar: Bar,
    pie: Pie,
    doughnut: Doughnut,
    radar: Radar,
    polarArea: PolarArea
  };

  const ChartComponent = ChartComponents[type] || Line;

  // Default chart options with animations and interactions
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          afterTitle: () => '',
          beforeBody: () => '',
          afterBody: (context) => {
            if (onDrillDown) {
              return ['', '🔍 Click to drill down'];
            }
            return '';
          }
        }
      }
    },
    scales: type === 'pie' || type === 'doughnut' ? {} : {
      x: {
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          font: {
            size: 11
          }
        }
      },
      y: {
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          font: {
            size: 11
          }
        }
      }
    },
    onClick: (event, elements) => {
      if (elements.length > 0 && onDrillDown) {
        const element = elements[0];
        const dataIndex = element.index;
        const datasetIndex = element.datasetIndex;
        onDrillDown({
          dataIndex,
          datasetIndex,
          data: data.datasets[datasetIndex].data[dataIndex],
          label: data.labels[dataIndex]
        });
      }
    },
    onHover: (event, elements) => {
      if (elements.length > 0) {
        const element = elements[0];
        setActiveDataPoint({
          dataIndex: element.index,
          datasetIndex: element.datasetIndex,
          value: data.datasets[element.datasetIndex].data[element.index],
          label: data.labels[element.index]
        });
        setShowTooltip(true);
      } else {
        setShowTooltip(false);
        setActiveDataPoint(null);
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart'
    }
  };

  const mergedOptions = useMemo(() => ({
    ...defaultOptions,
    ...options
  }), [options]);

  // Export chart as image
  const exportChart = async (format = 'png') => {
    if (chartRef.current) {
      const canvas = chartRef.current.canvas;
      const url = canvas.toDataURL(`image/${format}`);
      const link = document.createElement('a');
      link.download = `chart_${Date.now()}.${format}`;
      link.href = url;
      link.click();
    }
    
    if (onExport) {
      onExport(format);
    }
  };

  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (loading) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="flex flex-col items-center space-y-4">
            <RefreshCW className="w-8 h-8 animate-spin text-primary" />
            <p className="text-sm text-gray-500">Loading chart data...</p>
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <Info className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Failed to load chart</p>
              <p className="text-sm text-gray-500 mt-1">{error}</p>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}
      >
        <Card className={`${isFullscreen ? 'h-full' : ''} ${className}`}>
          {/* Chart Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex-1">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              )}
              {description && (
                <p className="text-sm text-gray-500 mt-1">{description}</p>
              )}
            </div>
            
            {showControls && (
              <div className="flex items-center space-x-2">
                {showFilters && (
                  <div className="relative">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFilterOpen(!filterOpen)}
                    >
                      <Filter className="w-4 h-4" />
                    </Button>
                    
                    {filterOpen && (
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border p-2">
                        <div className="space-y-2">
                          <Button variant="outline" size="sm" className="w-full justify-start">
                            <Calendar className="w-4 h-4 mr-2" />
                            Date Range
                          </Button>
                          <Button variant="outline" size="sm" className="w-full justify-start">
                            <Target className="w-4 h-4 mr-2" />
                            Metrics
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {onRefresh && (
                  <Button variant="outline" size="sm" onClick={onRefresh}>
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                )}
                
                <Button variant="outline" size="sm" onClick={() => exportChart('png')}>
                  <Download className="w-4 h-4" />
                </Button>
                
                <Button variant="outline" size="sm" onClick={toggleFullscreen}>
                  <Maximize2 className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>

          {/* Chart Content */}
          <div className="p-4">
            <div style={{ height: isFullscreen ? 'calc(100vh - 120px)' : height }}>
              <ChartComponent
                ref={chartRef}
                data={data}
                options={mergedOptions}
              />
            </div>
          </div>

          {/* Active Data Point Info */}
          {showTooltip && activeDataPoint && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute bottom-4 right-4 bg-black text-white p-3 rounded-lg shadow-lg"
            >
              <div className="text-sm">
                <div className="font-medium">{activeDataPoint.label}</div>
                <div className="text-gray-300">Value: {activeDataPoint.value}</div>
                {onDrillDown && (
                  <div className="text-xs text-blue-300 mt-1">Click to explore</div>
                )}
              </div>
            </motion.div>
          )}
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};

// Specialized Chart Components

// Time Series Chart
export const TimeSeriesChart = ({ data, title, onDrillDown, ...props }) => {
  const [timeRange, setTimeRange] = useState('7d');
  
  const processedData = useMemo(() => {
    if (!data || !data.datasets) return data;
    
    return {
      ...data,
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        borderColor: dataset.borderColor || '#3B82F6',
        backgroundColor: dataset.backgroundColor || 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      }))
    };
  }, [data]);

  return (
    <BaseChart
      type="line"
      data={processedData}
      title={title}
      onDrillDown={onDrillDown}
      {...props}
    />
  );
};

// Comparison Chart
export const ComparisonChart = ({ data, title, showPercentage = false, ...props }) => {
  const processedData = useMemo(() => {
    if (!data || !data.datasets) return data;
    
    return {
      ...data,
      datasets: data.datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || [
          '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'
        ][index % 5],
        borderWidth: 1,
        borderColor: '#ffffff'
      }))
    };
  }, [data]);

  return (
    <BaseChart
      type="bar"
      data={processedData}
      title={title}
      options={{
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = context.parsed.y;
                const percentage = showPercentage 
                  ? ` (${((value / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%)`
                  : '';
                return `${context.dataset.label}: ${value}${percentage}`;
              }
            }
          }
        }
      }}
      {...props}
    />
  );
};

// Distribution Chart
export const DistributionChart = ({ data, title, showLegend = true, ...props }) => {
  const processedData = useMemo(() => {
    if (!data || !data.datasets) return data;
    
    return {
      ...data,
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || [
          '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
          '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
        ],
        borderWidth: 2,
        borderColor: '#ffffff'
      }))
    };
  }, [data]);

  return (
    <BaseChart
      type="doughnut"
      data={processedData}
      title={title}
      options={{
        plugins: {
          legend: {
            display: showLegend,
            position: 'right'
          }
        },
        cutout: '60%'
      }}
      {...props}
    />
  );
};

// Performance Radar Chart
export const PerformanceRadar = ({ data, title, ...props }) => {
  const processedData = useMemo(() => {
    if (!data || !data.datasets) return data;
    
    return {
      ...data,
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || 'rgba(59, 130, 246, 0.2)',
        borderColor: dataset.borderColor || '#3B82F6',
        borderWidth: 2,
        pointBackgroundColor: '#3B82F6',
        pointBorderColor: '#ffffff',
        pointHoverBackgroundColor: '#ffffff',
        pointHoverBorderColor: '#3B82F6'
      }))
    };
  }, [data]);

  return (
    <BaseChart
      type="radar"
      data={processedData}
      title={title}
      options={{
        scales: {
          r: {
            angleLines: {
              display: true
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        }
      }}
      {...props}
    />
  );
};

// Metric Card Component
export const MetricCard = ({
  title,
  value,
  change,
  changeType = 'positive',
  icon: Icon,
  color = 'blue',
  onClick,
  loading = false
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card 
        className={`p-6 cursor-pointer transition-all hover:shadow-lg ${onClick ? 'hover:border-primary' : ''}`}
        onClick={onClick}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            
            {loading ? (
              <div className="flex items-center mt-2">
                <div className="animate-pulse bg-gray-200 h-8 w-24 rounded"></div>
              </div>
            ) : (
              <>
                <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
                
                {change !== undefined && (
                  <div className={`flex items-center mt-2 text-sm ${
                    changeType === 'positive' ? 'text-green-600' : 
                    changeType === 'negative' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {changeType === 'positive' ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    <span>{Math.abs(change)}% from last period</span>
                  </div>
                )}
              </>
            )}
          </div>
          
          {Icon && (
            <div className={`p-3 rounded-full border ${colorClasses[color]}`}>
              <Icon className="w-6 h-6" />
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
};

// Chart Grid Component
export const ChartGrid = ({ charts, columns = 2, gap = 6 }) => {
  return (
    <div className={`grid grid-cols-1 lg:grid-cols-${columns} gap-${gap}`}>
      {charts.map((chart, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          {chart}
        </motion.div>
      ))}
    </div>
  );
};