import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  IconButton,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  CircularProgress,
  LinearProgress,
  Tooltip,
  Menu,
  Divider,
  Alert,
  Snackbar,
  Fab,
  Badge,
  Switch,
  FormControlLabel,
  Checkbox,
  InputAdornment,
  Pagination,
  Skeleton,
  useTheme,
  useMediaQuery,
  alpha,
  Autocomplete,
  ToggleButton,
  ToggleButtonGroup,
  Card,
  CardContent,
  CardActions,
  CardHeader,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Collapse,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Drawer,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Schedule as ScheduleIcon,
  History as HistoryIcon,
  Preview as PreviewIcon,
  DragIndicator as DragIndicatorIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  CloudUpload as CloudUploadIcon,
  CloudDownload as CloudDownloadIcon,
  Refresh as RefreshIcon,
  Send as SendIcon,
  Email as EmailIcon,
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Code as JsonIcon,
  Image as ImageIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ViewList as ViewListIcon,
  ViewModule as ViewModuleIcon,
  CalendarToday as CalendarIcon,
  AccessTime as TimeIcon,
  Group as GroupIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
  ContentCopy as ContentCopyIcon,
  Share as ShareIcon,
  Archive as ArchiveIcon,
  Unarchive as UnarchiveIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  NotificationsActive as NotificationsIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Dashboard as DashboardIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  ShowChart as LineChartIcon,
  BubbleChart as BubbleChartIcon,
  DonutLarge as DonutChartIcon,
  Timeline as TimelineIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  CloudQueue as CloudIcon,
  Sync as SyncIcon,
  SyncDisabled as SyncDisabledIcon,
  CheckBox as CheckBoxIcon,
  CheckBoxOutlineBlank as CheckBoxBlankIcon,
  IndeterminateCheckBox as IndeterminateCheckBoxIcon,
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { format, parseISO, isAfter, isBefore, addDays, addWeeks, addMonths } from 'date-fns';
import { useHotkeys } from 'react-hotkeys-hook';

// Mock WebSocket connection for real-time updates
const useWebSocket = (url) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Mock WebSocket implementation
    const mockSocket = {
      send: (data) => console.log('WebSocket send:', data),
      close: () => setIsConnected(false),
    };
    setSocket(mockSocket);
    setIsConnected(true);

    return () => {
      mockSocket.close();
    };
  }, [url]);

  return { socket, isConnected };
};

// Custom hooks for report management
const useReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setReports(mockReports);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  return { reports, loading, error, refetch: fetchReports, setReports };
};

// Mock data
const mockReports = [
  {
    id: '1',
    name: 'Monthly Sales Report',
    description: 'Comprehensive sales analysis for the month',
    type: 'sales',
    format: 'pdf',
    schedule: 'monthly',
    lastRun: new Date().toISOString(),
    nextRun: addMonths(new Date(), 1).toISOString(),
    status: 'completed',
    starred: true,
    tags: ['sales', 'monthly', 'revenue'],
    createdBy: 'John Doe',
    createdAt: new Date().toISOString(),
    recipients: ['john@example.com', 'jane@example.com'],
  },
  {
    id: '2',
    name: 'Customer Analytics Dashboard',
    description: 'Real-time customer behavior and engagement metrics',
    type: 'analytics',
    format: 'excel',
    schedule: 'weekly',
    lastRun: addDays(new Date(), -2).toISOString(),
    nextRun: addWeeks(new Date(), 1).toISOString(),
    status: 'running',
    starred: false,
    tags: ['customers', 'analytics', 'weekly'],
    createdBy: 'Jane Smith',
    createdAt: addDays(new Date(), -30).toISOString(),
    recipients: ['analytics@example.com'],
  },
  {
    id: '3',
    name: 'Inventory Status Report',
    description: 'Current inventory levels and reorder recommendations',
    type: 'inventory',
    format: 'json',
    schedule: 'daily',
    lastRun: addDays(new Date(), -1).toISOString(),
    nextRun: addDays(new Date(), 1).toISOString(),
    status: 'failed',
    starred: false,
    tags: ['inventory', 'daily', 'operations'],
    createdBy: 'Mike Johnson',
    createdAt: addDays(new Date(), -60).toISOString(),
    recipients: ['operations@example.com'],
  },
];

const reportFormats = [
  { value: 'pdf', label: 'PDF', icon: PdfIcon },
  { value: 'excel', label: 'Excel', icon: ExcelIcon },
  { value: 'json', label: 'JSON', icon: JsonIcon },
  { value: 'png', label: 'Image', icon: ImageIcon },
];

const scheduleOptions = [
  { value: 'once', label: 'One Time' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'yearly', label: 'Yearly' },
];

const reportTypes = [
  { value: 'sales', label: 'Sales Report', color: '#4CAF50' },
  { value: 'analytics', label: 'Analytics Dashboard', color: '#2196F3' },
  { value: 'inventory', label: 'Inventory Report', color: '#FF9800' },
  { value: 'financial', label: 'Financial Statement', color: '#9C27B0' },
  { value: 'custom', label: 'Custom Report', color: '#607D8B' },
];

const chartTypes = [
  { value: 'bar', label: 'Bar Chart', icon: BarChartIcon },
  { value: 'line', label: 'Line Chart', icon: LineChartIcon },
  { value: 'pie', label: 'Pie Chart', icon: PieChartIcon },
  { value: 'donut', label: 'Donut Chart', icon: DonutChartIcon },
  { value: 'bubble', label: 'Bubble Chart', icon: BubbleChartIcon },
  { value: 'timeline', label: 'Timeline', icon: TimelineIcon },
];

const ReportsDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  // State management
  const [selectedTab, setSelectedTab] = useState(0);
  const [viewMode, setViewMode] = useState('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchor, setFilterAnchor] = useState(null);
  const [selectedReports, setSelectedReports] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [filterTags, setFilterTags] = useState([]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterFormat, setFilterFormat] = useState('all');
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [builderDialogOpen, setBuilderDialogOpen] = useState(false);
  const [deliveryDialogOpen, setDeliveryDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [bulkGenerateDialogOpen, setBulkGenerateDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  
  // Selected report for actions
  const [selectedReport, setSelectedReport] = useState(null);
  
  // Form states
  const [reportForm, setReportForm] = useState({
    name: '',
    description: '',
    type: 'sales',
    format: 'pdf',
    schedule: 'once',
    tags: [],
    recipients: [],
    includeCharts: true,
    autoSend: false,
  });
  
  // Progress tracking
  const [generationProgress, setGenerationProgress] = useState({});
  
  // Notifications
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info',
  });
  
  // WebSocket connection
  const { socket, isConnected } = useWebSocket('ws://localhost:3001/reports');
  
  // Data fetching
  const { reports, loading, error, refetch, setReports } = useReports();
  
  // Keyboard shortcuts
  useHotkeys('ctrl+n', () => setCreateDialogOpen(true), []);
  useHotkeys('ctrl+f', () => document.getElementById('search-input')?.focus(), []);
  useHotkeys('ctrl+r', () => refetch(), []);
  useHotkeys('ctrl+g', () => setViewMode(viewMode === 'grid' ? 'list' : 'grid'), [viewMode]);
  useHotkeys('esc', () => {
    setCreateDialogOpen(false);
    setEditDialogOpen(false);
    setPreviewDialogOpen(false);
    setScheduleDialogOpen(false);
    setHistoryDialogOpen(false);
    setBuilderDialogOpen(false);
    setDeliveryDialogOpen(false);
    setDeleteDialogOpen(false);
    setBulkGenerateDialogOpen(false);
    setImportDialogOpen(false);
    setExportDialogOpen(false);
  }, []);
  
  // Filter and sort reports
  const filteredReports = useMemo(() => {
    let filtered = [...reports];
    
    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(report =>
        report.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }
    
    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(report => report.status === filterStatus);
    }
    
    // Format filter
    if (filterFormat !== 'all') {
      filtered = filtered.filter(report => report.format === filterFormat);
    }
    
    // Tag filter
    if (filterTags.length > 0) {
      filtered = filtered.filter(report =>
        filterTags.every(tag => report.tags.includes(tag))
      );
    }
    
    // Sorting
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'lastRun' || sortBy === 'nextRun' || sortBy === 'createdAt') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return filtered;
  }, [reports, searchQuery, filterStatus, filterFormat, filterTags, sortBy, sortOrder]);
  
  // Pagination
  const paginatedReports = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredReports.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredReports, currentPage, itemsPerPage]);
  
  const totalPages = Math.ceil(filteredReports.length / itemsPerPage);
  
  // Handlers
  const handleCreateReport = () => {
    setReportForm({
      name: '',
      description: '',
      type: 'sales',
      format: 'pdf',
      schedule: 'once',
      tags: [],
      recipients: [],
      includeCharts: true,
      autoSend: false,
    });
    setCreateDialogOpen(true);
  };
  
  const handleEditReport = (report) => {
    setSelectedReport(report);
    setReportForm({
      name: report.name,
      description: report.description,
      type: report.type,
      format: report.format,
      schedule: report.schedule,
      tags: report.tags,
      recipients: report.recipients,
      includeCharts: true,
      autoSend: false,
    });
    setEditDialogOpen(true);
  };
  
  const handleDeleteReport = (report) => {
    setSelectedReport(report);
    setDeleteDialogOpen(true);
  };
  
  const handlePreviewReport = (report) => {
    setSelectedReport(report);
    setPreviewDialogOpen(true);
  };
  
  const handleScheduleReport = (report) => {
    setSelectedReport(report);
    setScheduleDialogOpen(true);
  };
  
  const handleViewHistory = (report) => {
    setSelectedReport(report);
    setHistoryDialogOpen(true);
  };
  
  const handleToggleStar = (report) => {
    const updatedReports = reports.map(r =>
      r.id === report.id ? { ...r, starred: !r.starred } : r
    );
    setReports(updatedReports);
    showSnackbar(
      report.starred ? 'Report removed from favorites' : 'Report added to favorites',
      'success'
    );
  };
  
  const handleGenerateReport = async (report) => {
    setGenerationProgress({
      ...generationProgress,
      [report.id]: { status: 'running', progress: 0 },
    });
    
    // Simulate report generation with progress
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 200));
      setGenerationProgress(prev => ({
        ...prev,
        [report.id]: { status: 'running', progress: i },
      }));
    }
    
    setGenerationProgress(prev => ({
      ...prev,
      [report.id]: { status: 'completed', progress: 100 },
    }));
    
    showSnackbar(`Report "${report.name}" generated successfully`, 'success');
    
    // Clear progress after 3 seconds
    setTimeout(() => {
      setGenerationProgress(prev => {
        const { [report.id]: _, ...rest } = prev;
        return rest;
      });
    }, 3000);
  };
  
  const handleBulkGenerate = () => {
    if (selectedReports.length === 0) {
      showSnackbar('Please select reports to generate', 'warning');
      return;
    }
    setBulkGenerateDialogOpen(true);
  };
  
  const handleSelectAll = () => {
    if (selectedReports.length === paginatedReports.length) {
      setSelectedReports([]);
    } else {
      setSelectedReports(paginatedReports.map(r => r.id));
    }
  };
  
  const handleSelectReport = (reportId) => {
    if (selectedReports.includes(reportId)) {
      setSelectedReports(selectedReports.filter(id => id !== reportId));
    } else {
      setSelectedReports([...selectedReports, reportId]);
    }
  };
  
  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };
  
  const handleDragEnd = (result) => {
    if (!result.destination) return;
    
    const items = Array.from(reports);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    setReports(items);
    showSnackbar('Report order updated', 'success');
  };
  
  // Report Card Component
  const ReportCard = ({ report, index }) => {
    const [menuAnchor, setMenuAnchor] = useState(null);
    const progress = generationProgress[report.id];
    
    const getStatusColor = (status) => {
      switch (status) {
        case 'completed':
          return 'success';
        case 'running':
          return 'info';
        case 'failed':
          return 'error';
        case 'scheduled':
          return 'warning';
        default:
          return 'default';
      }
    };
    
    const getFormatIcon = (format) => {
      const formatConfig = reportFormats.find(f => f.value === format);
      return formatConfig ? formatConfig.icon : DescriptionIcon;
    };
    
    return (
      <Draggable draggableId={report.id} index={index} isDragDisabled={viewMode === 'list'}>
        {(provided, snapshot) => (
          <Card
            ref={provided.innerRef}
            {...provided.draggableProps}
            elevation={snapshot.isDragging ? 8 : 1}
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              transition: 'all 0.3s',
              transform: snapshot.isDragging ? 'scale(1.05)' : 'scale(1)',
              opacity: snapshot.isDragging ? 0.9 : 1,
              position: 'relative',
              overflow: 'visible',
              '&:hover': {
                boxShadow: theme.shadows[4],
                transform: 'translateY(-2px)',
              },
            }}
          >
            {viewMode === 'grid' && (
              <Box
                {...provided.dragHandleProps}
                sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  cursor: 'grab',
                  color: 'text.secondary',
                  opacity: 0.5,
                  '&:hover': { opacity: 1 },
                }}
              >
                <DragIndicatorIcon />
              </Box>
            )}
            
            <CardHeader
              avatar={
                <Avatar sx={{ bgcolor: reportTypes.find(t => t.value === report.type)?.color }}>
                  {React.createElement(getFormatIcon(report.format))}
                </Avatar>
              }
              action={
                <Box>
                  <Checkbox
                    checked={selectedReports.includes(report.id)}
                    onChange={() => handleSelectReport(report.id)}
                    sx={{ p: 0.5 }}
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => setMenuAnchor(e.currentTarget)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleToggleStar(report)}
                    color={report.starred ? 'warning' : 'default'}
                  >
                    {report.starred ? <StarIcon /> : <StarBorderIcon />}
                  </IconButton>
                </Box>
              }
              title={
                <Typography variant="h6" noWrap>
                  {report.name}
                </Typography>
              }
              subheader={
                <Box>
                  <Chip
                    label={report.status}
                    size="small"
                    color={getStatusColor(report.status)}
                    sx={{ mr: 1 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {report.schedule}
                  </Typography>
                </Box>
              }
              sx={{ pb: 0 }}
            />
            
            <CardContent sx={{ flexGrow: 1, py: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {report.description}
              </Typography>
              
              <Box sx={{ mt: 1 }}>
                {report.tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                    onClick={() => setFilterTags([...filterTags, tag])}
                  />
                ))}
              </Box>
              
              {progress && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={progress.progress}
                    color={progress.status === 'completed' ? 'success' : 'primary'}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                    {progress.status === 'running' ? `Generating... ${progress.progress}%` : 'Completed'}
                  </Typography>
                </Box>
              )}
            </CardContent>
            
            <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Last run: {format(parseISO(report.lastRun), 'MMM dd, HH:mm')}
                </Typography>
              </Box>
              <Box>
                <Tooltip title="Preview">
                  <IconButton
                    size="small"
                    onClick={() => handlePreviewReport(report)}
                  >
                    <PreviewIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Generate Now">
                  <IconButton
                    size="small"
                    onClick={() => handleGenerateReport(report)}
                    disabled={progress?.status === 'running'}
                  >
                    {progress?.status === 'running' ? <CircularProgress size={20} /> : <PlayIcon />}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Download">
                  <IconButton
                    size="small"
                    disabled={report.status !== 'completed'}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </CardActions>
            
            <Menu
              anchorEl={menuAnchor}
              open={Boolean(menuAnchor)}
              onClose={() => setMenuAnchor(null)}
            >
              <MenuItem onClick={() => {
                handleEditReport(report);
                setMenuAnchor(null);
              }}>
                <EditIcon sx={{ mr: 1 }} /> Edit
              </MenuItem>
              <MenuItem onClick={() => {
                handleScheduleReport(report);
                setMenuAnchor(null);
              }}>
                <ScheduleIcon sx={{ mr: 1 }} /> Schedule
              </MenuItem>
              <MenuItem onClick={() => {
                handleViewHistory(report);
                setMenuAnchor(null);
              }}>
                <HistoryIcon sx={{ mr: 1 }} /> History
              </MenuItem>
              <MenuItem onClick={() => {
                setSelectedReport(report);
                setDeliveryDialogOpen(true);
                setMenuAnchor(null);
              }}>
                <SendIcon sx={{ mr: 1 }} /> Delivery Settings
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => {
                // Clone report
                const clonedReport = {
                  ...report,
                  id: Date.now().toString(),
                  name: `${report.name} (Copy)`,
                  createdAt: new Date().toISOString(),
                };
                setReports([...reports, clonedReport]);
                showSnackbar('Report cloned successfully', 'success');
                setMenuAnchor(null);
              }}>
                <ContentCopyIcon sx={{ mr: 1 }} /> Clone
              </MenuItem>
              <MenuItem onClick={() => {
                // Archive report
                showSnackbar('Report archived', 'success');
                setMenuAnchor(null);
              }}>
                <ArchiveIcon sx={{ mr: 1 }} /> Archive
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => {
                handleDeleteReport(report);
                setMenuAnchor(null);
              }} sx={{ color: 'error.main' }}>
                <DeleteIcon sx={{ mr: 1 }} /> Delete
              </MenuItem>
            </Menu>
          </Card>
        )}
      </Draggable>
    );
  };
  
  // Report List Item Component
  const ReportListItem = ({ report, index }) => {
    const [expanded, setExpanded] = useState(false);
    const progress = generationProgress[report.id];
    
    return (
      <Draggable draggableId={report.id} index={index}>
        {(provided, snapshot) => (
          <Paper
            ref={provided.innerRef}
            {...provided.draggableProps}
            elevation={snapshot.isDragging ? 8 : 1}
            sx={{
              mb: 1,
              transition: 'all 0.3s',
              transform: snapshot.isDragging ? 'scale(1.02)' : 'scale(1)',
              opacity: snapshot.isDragging ? 0.9 : 1,
            }}
          >
            <ListItem
              secondaryAction={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <IconButton
                    size="small"
                    onClick={() => handleToggleStar(report)}
                    color={report.starred ? 'warning' : 'default'}
                  >
                    {report.starred ? <StarIcon /> : <StarBorderIcon />}
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handlePreviewReport(report)}
                  >
                    <PreviewIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleGenerateReport(report)}
                    disabled={progress?.status === 'running'}
                  >
                    {progress?.status === 'running' ? <CircularProgress size={20} /> : <PlayIcon />}
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => setExpanded(!expanded)}
                  >
                    {expanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                  </IconButton>
                </Box>
              }
            >
              <Box {...provided.dragHandleProps} sx={{ mr: 2, cursor: 'grab' }}>
                <DragIndicatorIcon />
              </Box>
              <Checkbox
                checked={selectedReports.includes(report.id)}
                onChange={() => handleSelectReport(report.id)}
                sx={{ mr: 1 }}
              />
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: reportTypes.find(t => t.value === report.type)?.color }}>
                  {React.createElement(reportFormats.find(f => f.value === report.format)?.icon || DescriptionIcon)}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">{report.name}</Typography>
                    <Chip
                      label={report.status}
                      size="small"
                      color={
                        report.status === 'completed' ? 'success' :
                        report.status === 'running' ? 'info' :
                        report.status === 'failed' ? 'error' :
                        'default'
                      }
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {report.description}
                    </Typography>
                    {progress && (
                      <Box sx={{ mt: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={progress.progress}
                          color={progress.status === 'completed' ? 'success' : 'primary'}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    )}
                  </Box>
                }
              />
            </ListItem>
            <Collapse in={expanded}>
              <Box sx={{ px: 3, pb: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Type</Typography>
                    <Typography variant="body2">
                      {reportTypes.find(t => t.value === report.type)?.label}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Schedule</Typography>
                    <Typography variant="body2">{report.schedule}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Last Run</Typography>
                    <Typography variant="body2">
                      {format(parseISO(report.lastRun), 'MMM dd, yyyy HH:mm')}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="caption" color="text.secondary">Next Run</Typography>
                    <Typography variant="body2">
                      {format(parseISO(report.nextRun), 'MMM dd, yyyy HH:mm')}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {report.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" />
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleEditReport(report)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        startIcon={<ScheduleIcon />}
                        onClick={() => handleScheduleReport(report)}
                      >
                        Schedule
                      </Button>
                      <Button
                        size="small"
                        startIcon={<HistoryIcon />}
                        onClick={() => handleViewHistory(report)}
                      >
                        History
                      </Button>
                      <Button
                        size="small"
                        startIcon={<DeleteIcon />}
                        color="error"
                        onClick={() => handleDeleteReport(report)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            </Collapse>
          </Paper>
        )}
      </Draggable>
    );
  };
  
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                  <DescriptionIcon fontSize="large" />
                </Avatar>
                <Box>
                  <Typography variant="h4" gutterBottom>
                    Reports Dashboard
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Create, manage, and schedule comprehensive reports
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateReport}
                  size={isMobile ? 'small' : 'medium'}
                >
                  New Report
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CloudUploadIcon />}
                  onClick={() => setImportDialogOpen(true)}
                  size={isMobile ? 'small' : 'medium'}
                >
                  Import
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CloudDownloadIcon />}
                  onClick={() => setExportDialogOpen(true)}
                  size={isMobile ? 'small' : 'medium'}
                  disabled={selectedReports.length === 0}
                >
                  Export ({selectedReports.length})
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
        
        {/* Connection Status */}
        {!isConnected && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Real-time updates are currently unavailable. Data will be refreshed manually.
            </Typography>
          </Alert>
        )}
        
        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={selectedTab}
            onChange={(e, v) => setSelectedTab(v)}
            variant={isMobile ? 'scrollable' : 'standard'}
            scrollButtons={isMobile ? 'auto' : false}
          >
            <Tab label="All Reports" icon={<DescriptionIcon />} iconPosition="start" />
            <Tab label="Templates" icon={<DashboardIcon />} iconPosition="start" />
            <Tab label="Scheduled" icon={<ScheduleIcon />} iconPosition="start" />
            <Tab label="History" icon={<HistoryIcon />} iconPosition="start" />
            <Tab label="Report Builder" icon={<SettingsIcon />} iconPosition="start" />
          </Tabs>
        </Paper>
        
        {/* Toolbar */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                id="search-input"
                fullWidth
                variant="outlined"
                placeholder="Search reports..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: searchQuery && (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        onClick={() => setSearchQuery('')}
                      >
                        <CloseIcon />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                size="small"
              />
            </Grid>
            <Grid item xs={6} md={2}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={selectedReports.length === paginatedReports.length && paginatedReports.length > 0}
                    indeterminate={selectedReports.length > 0 && selectedReports.length < paginatedReports.length}
                    onChange={handleSelectAll}
                  />
                }
                label={`Select All (${selectedReports.length})`}
              />
            </Grid>
            <Grid item xs={6} md={6}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <ToggleButtonGroup
                  value={viewMode}
                  exclusive
                  onChange={(e, v) => v && setViewMode(v)}
                  size="small"
                >
                  <ToggleButton value="grid">
                    <ViewModuleIcon />
                  </ToggleButton>
                  <ToggleButton value="list">
                    <ViewListIcon />
                  </ToggleButton>
                </ToggleButtonGroup>
                <Button
                  startIcon={<FilterListIcon />}
                  onClick={(e) => setFilterAnchor(e.currentTarget)}
                  variant={filterTags.length > 0 || filterStatus !== 'all' || filterFormat !== 'all' ? 'contained' : 'outlined'}
                  size="small"
                >
                  Filters
                  {(filterTags.length > 0 || filterStatus !== 'all' || filterFormat !== 'all') && (
                    <Chip
                      label={filterTags.length + (filterStatus !== 'all' ? 1 : 0) + (filterFormat !== 'all' ? 1 : 0)}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Button>
                <Button
                  startIcon={<SyncIcon />}
                  onClick={refetch}
                  disabled={loading}
                  size="small"
                >
                  Refresh
                </Button>
                {selectedReports.length > 0 && (
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<PlayIcon />}
                    onClick={handleBulkGenerate}
                    size="small"
                  >
                    Generate ({selectedReports.length})
                  </Button>
                )}
              </Box>
            </Grid>
          </Grid>
        </Paper>
        
        {/* Filter Menu */}
        <Menu
          anchorEl={filterAnchor}
          open={Boolean(filterAnchor)}
          onClose={() => setFilterAnchor(null)}
          PaperProps={{ sx: { width: 300 } }}
        >
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Filter by Status
            </Typography>
            <TextField
              select
              fullWidth
              size="small"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="running">Running</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
              <MenuItem value="scheduled">Scheduled</MenuItem>
            </TextField>
            
            <Typography variant="subtitle2" gutterBottom>
              Filter by Format
            </Typography>
            <TextField
              select
              fullWidth
              size="small"
              value={filterFormat}
              onChange={(e) => setFilterFormat(e.target.value)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="all">All Formats</MenuItem>
              {reportFormats.map((format) => (
                <MenuItem key={format.value} value={format.value}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {React.createElement(format.icon, { fontSize: 'small' })}
                    {format.label}
                  </Box>
                </MenuItem>
              ))}
            </TextField>
            
            <Typography variant="subtitle2" gutterBottom>
              Filter by Tags
            </Typography>
            <Autocomplete
              multiple
              options={['sales', 'monthly', 'revenue', 'customers', 'analytics', 'weekly', 'inventory', 'daily', 'operations']}
              value={filterTags}
              onChange={(e, value) => setFilterTags(value)}
              renderInput={(params) => (
                <TextField {...params} size="small" placeholder="Select tags" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    size="small"
                    {...getTagProps({ index })}
                  />
                ))
              }
              sx={{ mb: 2 }}
            />
            
            <Typography variant="subtitle2" gutterBottom>
              Sort By
            </Typography>
            <Grid container spacing={1}>
              <Grid item xs={7}>
                <TextField
                  select
                  fullWidth
                  size="small"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <MenuItem value="name">Name</MenuItem>
                  <MenuItem value="lastRun">Last Run</MenuItem>
                  <MenuItem value="nextRun">Next Run</MenuItem>
                  <MenuItem value="createdAt">Created Date</MenuItem>
                  <MenuItem value="type">Type</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={5}>
                <ToggleButtonGroup
                  value={sortOrder}
                  exclusive
                  onChange={(e, v) => v && setSortOrder(v)}
                  fullWidth
                  size="small"
                >
                  <ToggleButton value="asc">ASC</ToggleButton>
                  <ToggleButton value="desc">DESC</ToggleButton>
                </ToggleButtonGroup>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Button
                size="small"
                onClick={() => {
                  setFilterStatus('all');
                  setFilterFormat('all');
                  setFilterTags([]);
                  setSortBy('name');
                  setSortOrder('asc');
                }}
              >
                Clear All
              </Button>
              <Button
                variant="contained"
                size="small"
                onClick={() => setFilterAnchor(null)}
              >
                Apply
              </Button>
            </Box>
          </Box>
        </Menu>
        
        {/* Content */}
        {loading && !reports.length ? (
          <Grid container spacing={2}>
            {Array.from({ length: 6 }).map((_, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Skeleton variant="rectangular" height={280} sx={{ borderRadius: 1 }} />
              </Grid>
            ))}
          </Grid>
        ) : error ? (
          <Alert severity="error">
            <Typography variant="body1">{error}</Typography>
            <Button size="small" onClick={refetch} sx={{ mt: 1 }}>
              Retry
            </Button>
          </Alert>
        ) : filteredReports.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No reports found
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {searchQuery || filterTags.length > 0 || filterStatus !== 'all' || filterFormat !== 'all'
                ? 'Try adjusting your filters or search query'
                : 'Create your first report to get started'}
            </Typography>
            {!(searchQuery || filterTags.length > 0 || filterStatus !== 'all' || filterFormat !== 'all') && (
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreateReport}
                sx={{ mt: 2 }}
              >
                Create Report
              </Button>
            )}
          </Paper>
        ) : (
          <>
            {selectedTab === 0 && (
              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="reports-list" direction={viewMode === 'grid' ? 'horizontal' : 'vertical'}>
                  {(provided) => (
                    <Box ref={provided.innerRef} {...provided.droppableProps}>
                      {viewMode === 'grid' ? (
                        <Grid container spacing={2}>
                          {paginatedReports.map((report, index) => (
                            <Grid item xs={12} sm={6} md={4} key={report.id}>
                              <ReportCard report={report} index={index} />
                            </Grid>
                          ))}
                          {provided.placeholder}
                        </Grid>
                      ) : (
                        <List>
                          {paginatedReports.map((report, index) => (
                            <ReportListItem key={report.id} report={report} index={index} />
                          ))}
                          {provided.placeholder}
                        </List>
                      )}
                    </Box>
                  )}
                </Droppable>
              </DragDropContext>
            )}
            
            {selectedTab === 1 && (
              <Typography variant="h6" sx={{ textAlign: 'center', py: 4 }}>
                Report Templates - Coming Soon
              </Typography>
            )}
            
            {selectedTab === 2 && (
              <Typography variant="h6" sx={{ textAlign: 'center', py: 4 }}>
                Scheduled Reports - Coming Soon
              </Typography>
            )}
            
            {selectedTab === 3 && (
              <Typography variant="h6" sx={{ textAlign: 'center', py: 4 }}>
                Report History - Coming Soon
              </Typography>
            )}
            
            {selectedTab === 4 && (
              <Typography variant="h6" sx={{ textAlign: 'center', py: 4 }}>
                Report Builder - Coming Soon
              </Typography>
            )}
            
            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={currentPage}
                  onChange={(e, page) => setCurrentPage(page)}
                  color="primary"
                  size={isMobile ? 'small' : 'medium'}
                />
              </Box>
            )}
          </>
        )}
        
        {/* Speed Dial */}
        <SpeedDial
          ariaLabel="Quick Actions"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          icon={<SpeedDialIcon />}
          hidden={isMobile}
        >
          <SpeedDialAction
            icon={<AddIcon />}
            tooltipTitle="New Report"
            onClick={handleCreateReport}
          />
          <SpeedDialAction
            icon={<DashboardIcon />}
            tooltipTitle="Report Builder"
            onClick={() => setBuilderDialogOpen(true)}
          />
          <SpeedDialAction
            icon={<CloudUploadIcon />}
            tooltipTitle="Import Reports"
            onClick={() => setImportDialogOpen(true)}
          />
          <SpeedDialAction
            icon={<ScheduleIcon />}
            tooltipTitle="View Schedules"
            onClick={() => setSelectedTab(2)}
          />
        </SpeedDial>
        
        {/* Dialogs - These would be implemented as separate components in a real application */}
        {/* Create/Edit Dialog */}
        <Dialog
          open={createDialogOpen || editDialogOpen}
          onClose={() => {
            setCreateDialogOpen(false);
            setEditDialogOpen(false);
          }}
          maxWidth="md"
          fullWidth
          fullScreen={isMobile}
        >
          <DialogTitle>
            {createDialogOpen ? 'Create New Report' : 'Edit Report'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Report Name"
                  value={reportForm.name}
                  onChange={(e) => setReportForm({ ...reportForm, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={reportForm.description}
                  onChange={(e) => setReportForm({ ...reportForm, description: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Report Type"
                  value={reportForm.type}
                  onChange={(e) => setReportForm({ ...reportForm, type: e.target.value })}
                >
                  {reportTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Format"
                  value={reportForm.format}
                  onChange={(e) => setReportForm({ ...reportForm, format: e.target.value })}
                >
                  {reportFormats.map((format) => (
                    <MenuItem key={format.value} value={format.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {React.createElement(format.icon, { fontSize: 'small' })}
                        {format.label}
                      </Box>
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Schedule"
                  value={reportForm.schedule}
                  onChange={(e) => setReportForm({ ...reportForm, schedule: e.target.value })}
                >
                  {scheduleOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Autocomplete
                  multiple
                  options={['sales', 'monthly', 'revenue', 'customers', 'analytics', 'weekly', 'inventory', 'daily', 'operations']}
                  value={reportForm.tags}
                  onChange={(e, value) => setReportForm({ ...reportForm, tags: value })}
                  renderInput={(params) => (
                    <TextField {...params} label="Tags" placeholder="Add tags" />
                  )}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        label={option}
                        size="small"
                        {...getTagProps({ index })}
                      />
                    ))
                  }
                />
              </Grid>
              <Grid item xs={12}>
                <Autocomplete
                  multiple
                  freeSolo
                  options={[]}
                  value={reportForm.recipients}
                  onChange={(e, value) => setReportForm({ ...reportForm, recipients: value })}
                  renderInput={(params) => (
                    <TextField {...params} label="Recipients" placeholder="Enter email addresses" />
                  )}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        label={option}
                        size="small"
                        {...getTagProps({ index })}
                      />
                    ))
                  }
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={reportForm.includeCharts}
                      onChange={(e) => setReportForm({ ...reportForm, includeCharts: e.target.checked })}
                    />
                  }
                  label="Include Charts and Visualizations"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={reportForm.autoSend}
                      onChange={(e) => setReportForm({ ...reportForm, autoSend: e.target.checked })}
                    />
                  }
                  label="Automatically Send to Recipients"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
            }}>
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={() => {
                // Save report logic
                showSnackbar(
                  createDialogOpen ? 'Report created successfully' : 'Report updated successfully',
                  'success'
                );
                setCreateDialogOpen(false);
                setEditDialogOpen(false);
              }}
            >
              {createDialogOpen ? 'Create' : 'Save'}
            </Button>
          </DialogActions>
        </Dialog>
        
        {/* Preview Dialog */}
        <Dialog
          open={previewDialogOpen}
          onClose={() => setPreviewDialogOpen(false)}
          maxWidth="lg"
          fullWidth
          fullScreen={isMobile}
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Typography variant="h6">{selectedReport?.name} - Preview</Typography>
              <IconButton onClick={() => setPreviewDialogOpen(false)}>
                <CloseIcon />
              </IconButton>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                Report preview would be displayed here
              </Typography>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button startIcon={<DownloadIcon />}>Download</Button>
            <Button startIcon={<ShareIcon />}>Share</Button>
            <Button startIcon={<SendIcon />}>Send</Button>
            <Button variant="contained" onClick={() => setPreviewDialogOpen(false)}>
              Close
            </Button>
          </DialogActions>
        </Dialog>
        
        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteDialogOpen}
          onClose={() => setDeleteDialogOpen(false)}
        >
          <DialogTitle>Delete Report</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete "{selectedReport?.name}"? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              color="error"
              onClick={() => {
                const updatedReports = reports.filter(r => r.id !== selectedReport.id);
                setReports(updatedReports);
                showSnackbar('Report deleted successfully', 'success');
                setDeleteDialogOpen(false);
              }}
            >
              Delete
            </Button>
          </DialogActions>
        </Dialog>
        
        {/* Snackbar */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            severity={snackbar.severity}
            variant="filled"
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </LocalizationProvider>
  );
};

export default ReportsDashboard;