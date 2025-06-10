import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  Chip,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Select,
  FormControl,
  InputLabel,
  TextField,
  Slider,
  Switch,
  FormControlLabel,
  Divider,
  useTheme,
  useMediaQuery,
  alpha,
} from '@mui/material';
import {
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  ShowChart as LineChartIcon,
  BubbleChart as BubbleChartIcon,
  DonutLarge as DonutChartIcon,
  Timeline as TimelineIcon,
  TableChart as TableIcon,
  Dashboard as DashboardIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  Settings as SettingsIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterIcon,
  DateRange as DateRangeIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  Image as ImageIcon,
  Code as CodeIcon,
  Palette as PaletteIcon,
  ViewColumn as ViewColumnIcon,
  ViewStream as ViewStreamIcon,
  ViewModule as ViewModuleIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  ReferenceArea,
  Brush,
  ComposedChart,
} from 'recharts';
import { DataGrid } from '@mui/x-data-grid';

// Color palettes
const colorPalettes = {
  default: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'],
  pastel: ['#93c5fd', '#86efac', '#fde047', '#fca5a5', '#c4b5fd', '#fbcfe8', '#67e8f9', '#bef264'],
  dark: ['#1e40af', '#047857', '#d97706', '#dc2626', '#7c3aed', '#db2777', '#0e7490', '#65a30d'],
  monochrome: ['#f3f4f6', '#e5e7eb', '#d1d5db', '#9ca3af', '#6b7280', '#4b5563', '#374151', '#1f2937'],
};

// Mock data generator
const generateMockData = (type, count = 12) => {
  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  switch (type) {
    case 'timeSeries':
      return labels.slice(0, count).map((month, index) => ({
        month,
        value: Math.floor(Math.random() * 1000) + 500,
        previousYear: Math.floor(Math.random() * 1000) + 400,
        target: 1000 + index * 50,
      }));
    
    case 'categories':
      return [
        { category: 'Product A', value: Math.floor(Math.random() * 1000) + 500 },
        { category: 'Product B', value: Math.floor(Math.random() * 1000) + 400 },
        { category: 'Product C', value: Math.floor(Math.random() * 1000) + 600 },
        { category: 'Product D', value: Math.floor(Math.random() * 1000) + 300 },
        { category: 'Product E', value: Math.floor(Math.random() * 1000) + 700 },
      ];
    
    case 'scatter':
      return Array.from({ length: 50 }, () => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
        z: Math.random() * 50 + 10,
      }));
    
    case 'radar':
      return [
        { skill: 'Communication', A: 80, B: 90, fullMark: 100 },
        { skill: 'Technical', A: 85, B: 85, fullMark: 100 },
        { skill: 'Leadership', A: 70, B: 95, fullMark: 100 },
        { skill: 'Teamwork', A: 90, B: 80, fullMark: 100 },
        { skill: 'Problem Solving', A: 85, B: 90, fullMark: 100 },
        { skill: 'Creativity', A: 75, B: 85, fullMark: 100 },
      ];
    
    default:
      return [];
  }
};

// Custom chart components
const ChartWrapper = ({ children, title, subtitle, actions, fullscreen }) => {
  const theme = useTheme();
  
  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: fullscreen ? 'background.paper' : 'transparent',
        p: fullscreen ? 3 : 0,
      }}
    >
      {(title || actions) && (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            {title && (
              <Typography variant="h6" gutterBottom={!subtitle}>
                {title}
              </Typography>
            )}
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          {actions && <Box>{actions}</Box>}
        </Box>
      )}
      <Box sx={{ flex: 1, minHeight: 0 }}>
        {children}
      </Box>
    </Box>
  );
};

const ReportVisualization = ({ data, config = {} }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // State
  const [chartType, setChartType] = useState(config.defaultChart || 'bar');
  const [viewMode, setViewMode] = useState('single');
  const [selectedPalette, setSelectedPalette] = useState('default');
  const [showGrid, setShowGrid] = useState(true);
  const [showLegend, setShowLegend] = useState(true);
  const [showTooltip, setShowTooltip] = useState(true);
  const [showBrush, setShowBrush] = useState(false);
  const [animationEnabled, setAnimationEnabled] = useState(true);
  const [fullscreenChart, setFullscreenChart] = useState(null);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [chartData, setChartData] = useState(data || generateMockData('timeSeries'));
  const [isLoading, setIsLoading] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);
  
  // Chart configurations
  const chartConfigs = {
    bar: {
      title: 'Bar Chart',
      icon: BarChartIcon,
      component: BarChart,
      dataKey: 'value',
      categoryKey: 'month',
    },
    line: {
      title: 'Line Chart',
      icon: LineChartIcon,
      component: LineChart,
      dataKey: 'value',
      categoryKey: 'month',
    },
    pie: {
      title: 'Pie Chart',
      icon: PieChartIcon,
      component: PieChart,
      dataKey: 'value',
      nameKey: 'category',
    },
    area: {
      title: 'Area Chart',
      icon: TimelineIcon,
      component: AreaChart,
      dataKey: 'value',
      categoryKey: 'month',
    },
    scatter: {
      title: 'Scatter Plot',
      icon: BubbleChartIcon,
      component: ScatterChart,
      dataKey: 'y',
      categoryKey: 'x',
    },
    radar: {
      title: 'Radar Chart',
      icon: DonutChartIcon,
      component: RadarChart,
      dataKey: 'A',
      categoryKey: 'skill',
    },
  };
  
  const colors = colorPalettes[selectedPalette];
  
  // Handlers
  const handleRefresh = async () => {
    setIsLoading(true);
    // Simulate data refresh
    setTimeout(() => {
      const newData = generateMockData(
        chartType === 'pie' ? 'categories' : 
        chartType === 'scatter' ? 'scatter' :
        chartType === 'radar' ? 'radar' : 'timeSeries'
      );
      setChartData(newData);
      setIsLoading(false);
    }, 1000);
  };
  
  const handleExport = (format) => {
    // Implement export functionality
    console.log(`Exporting as ${format}`);
    setMenuAnchor(null);
  };
  
  const handleShare = () => {
    // Implement share functionality
    console.log('Sharing visualization');
    setMenuAnchor(null);
  };
  
  const handlePrint = () => {
    window.print();
    setMenuAnchor(null);
  };
  
  const handleFullscreen = (chart) => {
    setFullscreenChart(chart);
  };
  
  const handleZoom = (direction) => {
    setZoomLevel(prev => {
      if (direction === 'in') return Math.min(prev + 10, 200);
      if (direction === 'out') return Math.max(prev - 10, 50);
      return 100;
    });
  };
  
  // Render chart based on type
  const renderChart = (type, isFullscreen = false) => {
    const config = chartConfigs[type];
    const chartHeight = isFullscreen ? 600 : 400;
    
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart data={chartData}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
              <XAxis dataKey={config.categoryKey} stroke={theme.palette.text.secondary} />
              <YAxis stroke={theme.palette.text.secondary} />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <Legend />}
              {showBrush && <Brush dataKey={config.categoryKey} height={30} stroke={theme.palette.primary.main} />}
              <Bar dataKey={config.dataKey} fill={colors[0]} animationDuration={animationEnabled ? 1000 : 0}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Bar>
              {chartData[0]?.previousYear && (
                <Bar dataKey="previousYear" fill={colors[1]} animationDuration={animationEnabled ? 1000 : 0} />
              )}
            </BarChart>
          </ResponsiveContainer>
        );
      
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <LineChart data={chartData}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
              <XAxis dataKey={config.categoryKey} stroke={theme.palette.text.secondary} />
              <YAxis stroke={theme.palette.text.secondary} />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <Legend />}
              {showBrush && <Brush dataKey={config.categoryKey} height={30} stroke={theme.palette.primary.main} />}
              <Line 
                type="monotone" 
                dataKey={config.dataKey} 
                stroke={colors[0]} 
                strokeWidth={2}
                dot={{ r: 4 }}
                animationDuration={animationEnabled ? 1000 : 0}
              />
              {chartData[0]?.previousYear && (
                <Line 
                  type="monotone" 
                  dataKey="previousYear" 
                  stroke={colors[1]} 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  animationDuration={animationEnabled ? 1000 : 0}
                />
              )}
              {chartData[0]?.target && (
                <Line 
                  type="monotone" 
                  dataKey="target" 
                  stroke={colors[2]} 
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  animationDuration={animationEnabled ? 1000 : 0}
                />
              )}
              <ReferenceLine y={800} stroke={theme.palette.error.main} strokeDasharray="3 3" />
            </LineChart>
          </ResponsiveContainer>
        );
      
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                outerRadius={isFullscreen ? 200 : 120}
                fill={colors[0]}
                dataKey={config.dataKey}
                nameKey={config.nameKey}
                animationDuration={animationEnabled ? 1000 : 0}
                label
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              {showTooltip && <RechartsTooltip />}
              {showLegend && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        );
      
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <AreaChart data={chartData}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
              <XAxis dataKey={config.categoryKey} stroke={theme.palette.text.secondary} />
              <YAxis stroke={theme.palette.text.secondary} />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <Legend />}
              {showBrush && <Brush dataKey={config.categoryKey} height={30} stroke={theme.palette.primary.main} />}
              <Area 
                type="monotone" 
                dataKey={config.dataKey} 
                stroke={colors[0]} 
                fill={colors[0]} 
                fillOpacity={0.6}
                animationDuration={animationEnabled ? 1000 : 0}
              />
              {chartData[0]?.previousYear && (
                <Area 
                  type="monotone" 
                  dataKey="previousYear" 
                  stroke={colors[1]} 
                  fill={colors[1]} 
                  fillOpacity={0.4}
                  animationDuration={animationEnabled ? 1000 : 0}
                />
              )}
              <ReferenceArea y1={600} y2={800} stroke={theme.palette.warning.main} strokeOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        );
      
      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <ScatterChart>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
              <XAxis type="number" dataKey="x" name="X" stroke={theme.palette.text.secondary} />
              <YAxis type="number" dataKey="y" name="Y" stroke={theme.palette.text.secondary} />
              {showTooltip && <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />}
              {showLegend && <Legend />}
              <Scatter 
                name="Data Points" 
                data={chartData} 
                fill={colors[0]}
                animationDuration={animationEnabled ? 1000 : 0}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        );
      
      case 'radar':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <RadarChart data={chartData}>
              <PolarGrid stroke={theme.palette.divider} />
              <PolarAngleAxis dataKey={config.categoryKey} stroke={theme.palette.text.secondary} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} stroke={theme.palette.text.secondary} />
              {showTooltip && <RechartsTooltip />}
              {showLegend && <Legend />}
              <Radar 
                name="Series A" 
                dataKey="A" 
                stroke={colors[0]} 
                fill={colors[0]} 
                fillOpacity={0.6}
                animationDuration={animationEnabled ? 1000 : 0}
              />
              <Radar 
                name="Series B" 
                dataKey="B" 
                stroke={colors[1]} 
                fill={colors[1]} 
                fillOpacity={0.6}
                animationDuration={animationEnabled ? 1000 : 0}
              />
            </RadarChart>
          </ResponsiveContainer>
        );
      
      default:
        return null;
    }
  };
  
  // Render table view
  const renderTable = () => {
    const columns = [
      { field: 'id', headerName: 'ID', width: 70 },
      { field: 'month', headerName: 'Month', width: 130 },
      { 
        field: 'value', 
        headerName: 'Value', 
        width: 130,
        type: 'number',
        renderCell: (params) => (
          <Chip 
            label={params.value} 
            size="small" 
            color={params.value > 800 ? 'success' : 'default'}
          />
        ),
      },
      { 
        field: 'previousYear', 
        headerName: 'Previous Year', 
        width: 130,
        type: 'number',
      },
      { 
        field: 'target', 
        headerName: 'Target', 
        width: 130,
        type: 'number',
      },
      {
        field: 'trend',
        headerName: 'Trend',
        width: 130,
        renderCell: (params) => {
          const trend = params.row.value > params.row.previousYear;
          return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {trend ? (
                <TrendingUpIcon color="success" fontSize="small" />
              ) : (
                <TrendingDownIcon color="error" fontSize="small" />
              )}
              <Typography variant="body2">
                {Math.abs(params.row.value - params.row.previousYear).toFixed(0)}
              </Typography>
            </Box>
          );
        },
      },
    ];
    
    const rows = chartData.map((item, index) => ({
      id: index + 1,
      ...item,
    }));
    
    return (
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={10}
        rowsPerPageOptions={[5, 10, 20]}
        checkboxSelection
        disableSelectionOnClick
        sx={{
          border: 'none',
          '& .MuiDataGrid-cell': {
            borderBottom: `1px solid ${theme.palette.divider}`,
          },
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: theme.palette.background.default,
            borderBottom: `2px solid ${theme.palette.divider}`,
          },
        }}
      />
    );
  };
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar */}
      <Paper elevation={0} sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <ToggleButtonGroup
                value={chartType}
                exclusive
                onChange={(e, value) => value && setChartType(value)}
                size="small"
              >
                {Object.entries(chartConfigs).map(([key, config]) => (
                  <ToggleButton key={key} value={key}>
                    <Tooltip title={config.title}>
                      {React.createElement(config.icon, { fontSize: 'small' })}
                    </Tooltip>
                  </ToggleButton>
                ))}
                <ToggleButton value="table">
                  <Tooltip title="Table View">
                    <TableIcon fontSize="small" />
                  </Tooltip>
                </ToggleButton>
              </ToggleButtonGroup>
              
              <Divider orientation="vertical" flexItem />
              
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(e, value) => value && setViewMode(value)}
                size="small"
              >
                <ToggleButton value="single">
                  <ViewStreamIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="split">
                  <ViewColumnIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="grid">
                  <ViewModuleIcon fontSize="small" />
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <IconButton onClick={handleRefresh} disabled={isLoading}>
                <RefreshIcon />
              </IconButton>
              <IconButton onClick={() => handleZoom('out')} disabled={zoomLevel <= 50}>
                <ZoomOutIcon />
              </IconButton>
              <Chip label={`${zoomLevel}%`} size="small" />
              <IconButton onClick={() => handleZoom('in')} disabled={zoomLevel >= 200}>
                <ZoomInIcon />
              </IconButton>
              <IconButton onClick={() => handleZoom('reset')}>
                <RemoveIcon />
              </IconButton>
              <Divider orientation="vertical" flexItem />
              <IconButton onClick={(e) => setMenuAnchor(e.currentTarget)}>
                <MoreVertIcon />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
        
        {/* Advanced Settings */}
        <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Color Palette</InputLabel>
            <Select
              value={selectedPalette}
              onChange={(e) => setSelectedPalette(e.target.value)}
              label="Color Palette"
            >
              {Object.keys(colorPalettes).map((palette) => (
                <MenuItem key={palette} value={palette}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {colorPalettes[palette].slice(0, 4).map((color, index) => (
                      <Box
                        key={index}
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          bgcolor: color,
                        }}
                      />
                    ))}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {palette.charAt(0).toUpperCase() + palette.slice(1)}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControlLabel
            control={<Switch checked={showGrid} onChange={(e) => setShowGrid(e.target.checked)} />}
            label="Grid"
          />
          <FormControlLabel
            control={<Switch checked={showLegend} onChange={(e) => setShowLegend(e.target.checked)} />}
            label="Legend"
          />
          <FormControlLabel
            control={<Switch checked={showTooltip} onChange={(e) => setShowTooltip(e.target.checked)} />}
            label="Tooltip"
          />
          <FormControlLabel
            control={<Switch checked={showBrush} onChange={(e) => setShowBrush(e.target.checked)} />}
            label="Zoom Brush"
          />
          <FormControlLabel
            control={<Switch checked={animationEnabled} onChange={(e) => setAnimationEnabled(e.target.checked)} />}
            label="Animation"
          />
        </Box>
      </Paper>
      
      {/* Chart Area */}
      <Box sx={{ flex: 1, p: 2, overflow: 'auto' }}>
        {viewMode === 'single' && (
          <Paper elevation={0} sx={{ height: '100%', p: 2 }}>
            {chartType === 'table' ? renderTable() : renderChart(chartType)}
          </Paper>
        )}
        
        {viewMode === 'split' && (
          <Grid container spacing={2} sx={{ height: '100%' }}>
            <Grid item xs={12} md={6}>
              <Paper elevation={0} sx={{ height: '100%', p: 2 }}>
                {renderChart('bar')}
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={0} sx={{ height: '100%', p: 2 }}>
                {renderChart('line')}
              </Paper>
            </Grid>
          </Grid>
        )}
        
        {viewMode === 'grid' && (
          <Grid container spacing={2}>
            {Object.keys(chartConfigs).map((type) => (
              <Grid item xs={12} sm={6} md={4} key={type}>
                <Paper elevation={0} sx={{ p: 2, height: 300 }}>
                  <ChartWrapper
                    title={chartConfigs[type].title}
                    actions={
                      <IconButton size="small" onClick={() => handleFullscreen(type)}>
                        <FullscreenIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    {renderChart(type)}
                  </ChartWrapper>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
      
      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
      >
        <MenuItem onClick={() => handleExport('png')}>
          <ImageIcon sx={{ mr: 1 }} /> Export as PNG
        </MenuItem>
        <MenuItem onClick={() => handleExport('svg')}>
          <CodeIcon sx={{ mr: 1 }} /> Export as SVG
        </MenuItem>
        <MenuItem onClick={() => handleExport('pdf')}>
          <DownloadIcon sx={{ mr: 1 }} /> Export as PDF
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleShare}>
          <ShareIcon sx={{ mr: 1 }} /> Share
        </MenuItem>
        <MenuItem onClick={handlePrint}>
          <PrintIcon sx={{ mr: 1 }} /> Print
        </MenuItem>
      </Menu>
      
      {/* Fullscreen Dialog */}
      {fullscreenChart && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'background.paper',
            zIndex: theme.zIndex.modal,
            p: 3,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h5">
              {chartConfigs[fullscreenChart].title}
            </Typography>
            <IconButton onClick={() => setFullscreenChart(null)}>
              <FullscreenExitIcon />
            </IconButton>
          </Box>
          {renderChart(fullscreenChart, true)}
        </Box>
      )}
    </Box>
  );
};

export default ReportVisualization;