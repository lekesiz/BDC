import React, { useState, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  FormControlLabel,
  Switch,
  Chip,
  IconButton,
  Typography,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Divider,
  Alert,
  AlertTitle,
  Autocomplete,
  ToggleButton,
  ToggleButtonGroup,
  FormControl,
  InputLabel,
  Select,
  OutlinedInput,
  InputAdornment,
  Tooltip,
  Badge,
  Collapse,
  FormGroup,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  CardActions,
  useTheme,
  useMediaQuery,
  alpha,
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  AccessTime as TimeIcon,
  CalendarToday as CalendarIcon,
  Email as EmailIcon,
  CloudUpload as CloudUploadIcon,
  Folder as FolderIcon,
  Group as GroupIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ContentCopy as CopyIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon,
  NotificationsActive as NotificationIcon,
  Send as SendIcon,
  AttachFile as AttachIcon,
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Code as JsonIcon,
  Image as ImageIcon,
  Archive as ZipIcon,
  Language as WebhookIcon,
  Storage as DatabaseIcon,
  CloudQueue as CloudIcon,
  Security as SecurityIcon,
  VpnKey as KeyIcon,
  Timer as TimerIcon,
  DateRange as DateRangeIcon,
  Repeat as RepeatIcon,
  EventNote as EventIcon,
  Today as TodayIcon,
  Update as UpdateIcon,
  Autorenew as AutorenewIcon,
  Block as BlockIcon,
  CheckBox as CheckBoxIcon,
  CheckBoxOutlineBlank as CheckBoxBlankIcon,
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  format,
  addDays,
  addWeeks,
  addMonths,
  addYears,
  startOfDay,
  endOfDay,
  isAfter,
  isBefore,
  parseISO,
  getDay,
  setHours,
  setMinutes,
} from 'date-fns';
import cronstrue from 'cronstrue';

// Schedule frequency options
const frequencyOptions = [
  { value: 'once', label: 'One Time', icon: EventIcon },
  { value: 'daily', label: 'Daily', icon: TodayIcon },
  { value: 'weekly', label: 'Weekly', icon: CalendarIcon },
  { value: 'monthly', label: 'Monthly', icon: DateRangeIcon },
  { value: 'quarterly', label: 'Quarterly', icon: UpdateIcon },
  { value: 'yearly', label: 'Yearly', icon: AutorenewIcon },
  { value: 'custom', label: 'Custom (Cron)', icon: SettingsIcon },
];

// Delivery methods
const deliveryMethods = [
  { value: 'email', label: 'Email', icon: EmailIcon, color: '#4CAF50' },
  { value: 'cloud', label: 'Cloud Storage', icon: CloudIcon, color: '#2196F3' },
  { value: 'ftp', label: 'FTP/SFTP', icon: FolderIcon, color: '#FF9800' },
  { value: 'webhook', label: 'Webhook', icon: WebhookIcon, color: '#9C27B0' },
  { value: 'database', label: 'Database', icon: DatabaseIcon, color: '#607D8B' },
];

// File formats
const fileFormats = [
  { value: 'pdf', label: 'PDF', icon: PdfIcon },
  { value: 'excel', label: 'Excel', icon: ExcelIcon },
  { value: 'csv', label: 'CSV', icon: TableIcon },
  { value: 'json', label: 'JSON', icon: JsonIcon },
  { value: 'png', label: 'Image (PNG)', icon: ImageIcon },
  { value: 'zip', label: 'ZIP Archive', icon: ZipIcon },
];

// Mock scheduled reports
const mockScheduledReports = [
  {
    id: '1',
    reportId: 'report-1',
    reportName: 'Monthly Sales Report',
    frequency: 'monthly',
    nextRun: addDays(new Date(), 5).toISOString(),
    lastRun: addDays(new Date(), -25).toISOString(),
    status: 'active',
    deliveryMethods: ['email', 'cloud'],
    recipients: ['john@example.com', 'jane@example.com'],
    format: 'pdf',
    createdBy: 'John Doe',
    createdAt: addMonths(new Date(), -3).toISOString(),
  },
  {
    id: '2',
    reportId: 'report-2',
    reportName: 'Weekly Analytics Dashboard',
    frequency: 'weekly',
    nextRun: addDays(new Date(), 2).toISOString(),
    lastRun: addDays(new Date(), -5).toISOString(),
    status: 'active',
    deliveryMethods: ['email'],
    recipients: ['analytics@example.com'],
    format: 'excel',
    createdBy: 'Jane Smith',
    createdAt: addMonths(new Date(), -1).toISOString(),
  },
];

const ReportScheduler = ({ open, onClose, report, onSchedule }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // State
  const [activeStep, setActiveStep] = useState(0);
  const [scheduleConfig, setScheduleConfig] = useState({
    frequency: 'once',
    startDate: new Date(),
    endDate: null,
    time: setHours(setMinutes(new Date(), 0), 9),
    dayOfWeek: 1, // Monday
    dayOfMonth: 1,
    monthOfQuarter: 1,
    customCron: '0 9 * * 1',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    enabled: true,
  });
  
  const [deliveryConfig, setDeliveryConfig] = useState({
    methods: ['email'],
    format: 'pdf',
    recipients: [],
    emailSubject: `${report?.name || 'Report'} - {{date}}`,
    emailBody: 'Please find the attached report for {{date}}.',
    includeLink: true,
    linkExpiry: 7, // days
    password: '',
    cloudProvider: 'google-drive',
    cloudPath: '/Reports/{{year}}/{{month}}/',
    ftpHost: '',
    ftpPort: 21,
    ftpUsername: '',
    ftpPassword: '',
    ftpPath: '/',
    webhookUrl: '',
    webhookMethod: 'POST',
    webhookHeaders: {},
    databaseConnection: '',
    databaseTable: '',
  });
  
  const [notificationConfig, setNotificationConfig] = useState({
    onSuccess: true,
    onFailure: true,
    notifyRecipients: false,
    includePreview: true,
  });
  
  const [advancedConfig, setAdvancedConfig] = useState({
    retryOnFailure: true,
    maxRetries: 3,
    retryDelay: 300, // seconds
    timeout: 1800, // seconds (30 minutes)
    priority: 'normal',
    compression: false,
    encryption: false,
    watermark: false,
    includeMetadata: true,
    filters: {},
    parameters: {},
  });
  
  const [scheduledReports, setScheduledReports] = useState(mockScheduledReports);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  // Calculate next run date based on frequency
  const calculateNextRun = () => {
    const { frequency, startDate, time, dayOfWeek, dayOfMonth } = scheduleConfig;
    let nextRun = new Date(startDate);
    
    // Set time
    nextRun.setHours(time.getHours());
    nextRun.setMinutes(time.getMinutes());
    nextRun.setSeconds(0);
    
    // If start date is in the past, calculate from today
    if (isBefore(nextRun, new Date())) {
      nextRun = new Date();
    }
    
    switch (frequency) {
      case 'daily':
        nextRun = addDays(nextRun, 1);
        break;
      case 'weekly':
        // Find next occurrence of selected day
        while (getDay(nextRun) !== dayOfWeek) {
          nextRun = addDays(nextRun, 1);
        }
        break;
      case 'monthly':
        nextRun.setDate(dayOfMonth);
        if (isBefore(nextRun, new Date())) {
          nextRun = addMonths(nextRun, 1);
        }
        break;
      case 'quarterly':
        // Calculate next quarter
        const currentMonth = nextRun.getMonth();
        const quarterStartMonth = Math.floor(currentMonth / 3) * 3;
        nextRun.setMonth(quarterStartMonth + monthOfQuarter - 1);
        nextRun.setDate(dayOfMonth);
        if (isBefore(nextRun, new Date())) {
          nextRun = addMonths(nextRun, 3);
        }
        break;
      case 'yearly':
        if (isBefore(nextRun, new Date())) {
          nextRun = addYears(nextRun, 1);
        }
        break;
    }
    
    return nextRun;
  };
  
  // Get cron expression
  const getCronExpression = () => {
    const { frequency, time, dayOfWeek, dayOfMonth, customCron } = scheduleConfig;
    const hours = time.getHours();
    const minutes = time.getMinutes();
    
    switch (frequency) {
      case 'once':
        return null;
      case 'daily':
        return `${minutes} ${hours} * * *`;
      case 'weekly':
        return `${minutes} ${hours} * * ${dayOfWeek}`;
      case 'monthly':
        return `${minutes} ${hours} ${dayOfMonth} * *`;
      case 'quarterly':
        return `${minutes} ${hours} ${dayOfMonth} */3 *`;
      case 'yearly':
        return `${minutes} ${hours} ${dayOfMonth} ${scheduleConfig.startDate.getMonth() + 1} *`;
      case 'custom':
        return customCron;
      default:
        return null;
    }
  };
  
  // Get human-readable schedule description
  const getScheduleDescription = () => {
    const cron = getCronExpression();
    if (!cron) return 'One-time execution';
    
    try {
      return cronstrue.toString(cron);
    } catch (error) {
      return 'Invalid cron expression';
    }
  };
  
  // Validate configuration
  const validateConfig = () => {
    const errors = {};
    
    // Validate schedule
    if (scheduleConfig.frequency === 'custom' && !scheduleConfig.customCron) {
      errors.customCron = 'Cron expression is required';
    }
    
    if (scheduleConfig.endDate && isBefore(scheduleConfig.endDate, scheduleConfig.startDate)) {
      errors.endDate = 'End date must be after start date';
    }
    
    // Validate delivery
    if (deliveryConfig.methods.length === 0) {
      errors.methods = 'At least one delivery method is required';
    }
    
    if (deliveryConfig.methods.includes('email') && deliveryConfig.recipients.length === 0) {
      errors.recipients = 'At least one recipient is required for email delivery';
    }
    
    if (deliveryConfig.methods.includes('ftp') && !deliveryConfig.ftpHost) {
      errors.ftpHost = 'FTP host is required';
    }
    
    if (deliveryConfig.methods.includes('webhook') && !deliveryConfig.webhookUrl) {
      errors.webhookUrl = 'Webhook URL is required';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  // Handle schedule save
  const handleSave = async () => {
    if (!validateConfig()) {
      return;
    }
    
    setIsLoading(true);
    
    const scheduleData = {
      reportId: report.id,
      reportName: report.name,
      frequency: scheduleConfig.frequency,
      cronExpression: getCronExpression(),
      nextRun: calculateNextRun().toISOString(),
      startDate: scheduleConfig.startDate.toISOString(),
      endDate: scheduleConfig.endDate?.toISOString(),
      timezone: scheduleConfig.timezone,
      enabled: scheduleConfig.enabled,
      delivery: deliveryConfig,
      notifications: notificationConfig,
      advanced: advancedConfig,
      createdAt: new Date().toISOString(),
      createdBy: 'Current User', // Replace with actual user
    };
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (selectedSchedule) {
        // Update existing schedule
        setScheduledReports(prev => prev.map(s => 
          s.id === selectedSchedule.id ? { ...s, ...scheduleData } : s
        ));
      } else {
        // Create new schedule
        const newSchedule = {
          id: Date.now().toString(),
          ...scheduleData,
          status: 'active',
          lastRun: null,
        };
        setScheduledReports(prev => [...prev, newSchedule]);
      }
      
      onSchedule?.(scheduleData);
      handleClose();
    } catch (error) {
      console.error('Failed to save schedule:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle close
  const handleClose = () => {
    setActiveStep(0);
    setScheduleConfig({
      frequency: 'once',
      startDate: new Date(),
      endDate: null,
      time: setHours(setMinutes(new Date(), 0), 9),
      dayOfWeek: 1,
      dayOfMonth: 1,
      monthOfQuarter: 1,
      customCron: '0 9 * * 1',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      enabled: true,
    });
    setDeliveryConfig({
      methods: ['email'],
      format: 'pdf',
      recipients: [],
      emailSubject: `${report?.name || 'Report'} - {{date}}`,
      emailBody: 'Please find the attached report for {{date}}.',
      includeLink: true,
      linkExpiry: 7,
      password: '',
      cloudProvider: 'google-drive',
      cloudPath: '/Reports/{{year}}/{{month}}/',
      ftpHost: '',
      ftpPort: 21,
      ftpUsername: '',
      ftpPassword: '',
      ftpPath: '/',
      webhookUrl: '',
      webhookMethod: 'POST',
      webhookHeaders: {},
      databaseConnection: '',
      databaseTable: '',
    });
    setValidationErrors({});
    setSelectedSchedule(null);
    onClose();
  };
  
  // Steps
  const steps = [
    { label: 'Schedule', icon: ScheduleIcon },
    { label: 'Delivery', icon: SendIcon },
    { label: 'Notifications', icon: NotificationIcon },
    { label: 'Advanced', icon: SettingsIcon },
    { label: 'Review', icon: CheckIcon },
  ];
  
  const renderStepContent = (step) => {
    switch (step) {
      case 0: // Schedule
        return (
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Frequency</InputLabel>
                  <Select
                    value={scheduleConfig.frequency}
                    onChange={(e) => setScheduleConfig({ ...scheduleConfig, frequency: e.target.value })}
                    label="Frequency"
                  >
                    {frequencyOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {React.createElement(option.icon, { fontSize: 'small' })}
                          {option.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              {scheduleConfig.frequency !== 'once' && (
                <Grid item xs={12} sm={6}>
                  <TimePicker
                    label="Time"
                    value={scheduleConfig.time}
                    onChange={(newValue) => setScheduleConfig({ ...scheduleConfig, time: newValue })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>
              )}
              
              {scheduleConfig.frequency === 'once' && (
                <Grid item xs={12}>
                  <DateTimePicker
                    label="Run Date & Time"
                    value={scheduleConfig.startDate}
                    onChange={(newValue) => setScheduleConfig({ ...scheduleConfig, startDate: newValue })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                    minDateTime={new Date()}
                  />
                </Grid>
              )}
              
              {scheduleConfig.frequency === 'weekly' && (
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Day of Week</InputLabel>
                    <Select
                      value={scheduleConfig.dayOfWeek}
                      onChange={(e) => setScheduleConfig({ ...scheduleConfig, dayOfWeek: e.target.value })}
                      label="Day of Week"
                    >
                      <MenuItem value={0}>Sunday</MenuItem>
                      <MenuItem value={1}>Monday</MenuItem>
                      <MenuItem value={2}>Tuesday</MenuItem>
                      <MenuItem value={3}>Wednesday</MenuItem>
                      <MenuItem value={4}>Thursday</MenuItem>
                      <MenuItem value={5}>Friday</MenuItem>
                      <MenuItem value={6}>Saturday</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              )}
              
              {(scheduleConfig.frequency === 'monthly' || 
                scheduleConfig.frequency === 'quarterly' || 
                scheduleConfig.frequency === 'yearly') && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Day of Month"
                    value={scheduleConfig.dayOfMonth}
                    onChange={(e) => setScheduleConfig({ ...scheduleConfig, dayOfMonth: parseInt(e.target.value) })}
                    InputProps={{
                      inputProps: { min: 1, max: 31 }
                    }}
                  />
                </Grid>
              )}
              
              {scheduleConfig.frequency === 'custom' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Cron Expression"
                    value={scheduleConfig.customCron}
                    onChange={(e) => setScheduleConfig({ ...scheduleConfig, customCron: e.target.value })}
                    error={!!validationErrors.customCron}
                    helperText={validationErrors.customCron || getScheduleDescription()}
                  />
                </Grid>
              )}
              
              {scheduleConfig.frequency !== 'once' && (
                <>
                  <Grid item xs={12} sm={6}>
                    <DateTimePicker
                      label="Start Date"
                      value={scheduleConfig.startDate}
                      onChange={(newValue) => setScheduleConfig({ ...scheduleConfig, startDate: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <DateTimePicker
                      label="End Date (Optional)"
                      value={scheduleConfig.endDate}
                      onChange={(newValue) => setScheduleConfig({ ...scheduleConfig, endDate: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                      minDateTime={scheduleConfig.startDate}
                      error={!!validationErrors.endDate}
                      helperText={validationErrors.endDate}
                    />
                  </Grid>
                </>
              )}
              
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Timezone</InputLabel>
                  <Select
                    value={scheduleConfig.timezone}
                    onChange={(e) => setScheduleConfig({ ...scheduleConfig, timezone: e.target.value })}
                    label="Timezone"
                  >
                    <MenuItem value={Intl.DateTimeFormat().resolvedOptions().timeZone}>
                      {Intl.DateTimeFormat().resolvedOptions().timeZone} (Local)
                    </MenuItem>
                    <MenuItem value="UTC">UTC</MenuItem>
                    <MenuItem value="America/New_York">America/New_York</MenuItem>
                    <MenuItem value="America/Chicago">America/Chicago</MenuItem>
                    <MenuItem value="America/Los_Angeles">America/Los_Angeles</MenuItem>
                    <MenuItem value="Europe/London">Europe/London</MenuItem>
                    <MenuItem value="Europe/Paris">Europe/Paris</MenuItem>
                    <MenuItem value="Asia/Tokyo">Asia/Tokyo</MenuItem>
                    <MenuItem value="Asia/Shanghai">Asia/Shanghai</MenuItem>
                    <MenuItem value="Australia/Sydney">Australia/Sydney</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <Alert severity="info">
                  <AlertTitle>Next Run</AlertTitle>
                  {scheduleConfig.frequency === 'once' 
                    ? format(scheduleConfig.startDate, 'PPpp')
                    : `${getScheduleDescription()} starting ${format(calculateNextRun(), 'PPpp')}`
                  }
                </Alert>
              </Grid>
            </Grid>
          </Box>
        );
      
      case 1: // Delivery
        return (
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Delivery Methods
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {deliveryMethods.map((method) => (
                    <Chip
                      key={method.value}
                      label={method.label}
                      icon={React.createElement(method.icon)}
                      onClick={() => {
                        const methods = deliveryConfig.methods.includes(method.value)
                          ? deliveryConfig.methods.filter(m => m !== method.value)
                          : [...deliveryConfig.methods, method.value];
                        setDeliveryConfig({ ...deliveryConfig, methods });
                      }}
                      color={deliveryConfig.methods.includes(method.value) ? 'primary' : 'default'}
                      variant={deliveryConfig.methods.includes(method.value) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
                {validationErrors.methods && (
                  <Typography variant="caption" color="error">
                    {validationErrors.methods}
                  </Typography>
                )}
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Format</InputLabel>
                  <Select
                    value={deliveryConfig.format}
                    onChange={(e) => setDeliveryConfig({ ...deliveryConfig, format: e.target.value })}
                    label="Format"
                  >
                    {fileFormats.map((format) => (
                      <MenuItem key={format.value} value={format.value}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {React.createElement(format.icon, { fontSize: 'small' })}
                          {format.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              {deliveryConfig.methods.includes('email') && (
                <>
                  <Grid item xs={12}>
                    <Autocomplete
                      multiple
                      freeSolo
                      options={[]}
                      value={deliveryConfig.recipients}
                      onChange={(e, value) => setDeliveryConfig({ ...deliveryConfig, recipients: value })}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Email Recipients"
                          placeholder="Enter email addresses"
                          error={!!validationErrors.recipients}
                          helperText={validationErrors.recipients}
                        />
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
                    <TextField
                      fullWidth
                      label="Email Subject"
                      value={deliveryConfig.emailSubject}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, emailSubject: e.target.value })}
                      helperText="Use {{date}}, {{reportName}}, {{time}} as placeholders"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Email Body"
                      value={deliveryConfig.emailBody}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, emailBody: e.target.value })}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={deliveryConfig.includeLink}
                          onChange={(e) => setDeliveryConfig({ ...deliveryConfig, includeLink: e.target.checked })}
                        />
                      }
                      label="Include Download Link"
                    />
                  </Grid>
                  {deliveryConfig.includeLink && (
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Link Expiry (days)"
                        value={deliveryConfig.linkExpiry}
                        onChange={(e) => setDeliveryConfig({ ...deliveryConfig, linkExpiry: parseInt(e.target.value) })}
                        InputProps={{
                          inputProps: { min: 1, max: 30 }
                        }}
                      />
                    </Grid>
                  )}
                </>
              )}
              
              {deliveryConfig.methods.includes('cloud') && (
                <>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Cloud Provider</InputLabel>
                      <Select
                        value={deliveryConfig.cloudProvider}
                        onChange={(e) => setDeliveryConfig({ ...deliveryConfig, cloudProvider: e.target.value })}
                        label="Cloud Provider"
                      >
                        <MenuItem value="google-drive">Google Drive</MenuItem>
                        <MenuItem value="dropbox">Dropbox</MenuItem>
                        <MenuItem value="onedrive">OneDrive</MenuItem>
                        <MenuItem value="aws-s3">AWS S3</MenuItem>
                        <MenuItem value="azure-blob">Azure Blob Storage</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Cloud Path"
                      value={deliveryConfig.cloudPath}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, cloudPath: e.target.value })}
                      helperText="Use {{year}}, {{month}}, {{day}} as placeholders"
                    />
                  </Grid>
                </>
              )}
              
              {deliveryConfig.methods.includes('ftp') && (
                <>
                  <Grid item xs={12} sm={8}>
                    <TextField
                      fullWidth
                      label="FTP Host"
                      value={deliveryConfig.ftpHost}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, ftpHost: e.target.value })}
                      error={!!validationErrors.ftpHost}
                      helperText={validationErrors.ftpHost}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Port"
                      value={deliveryConfig.ftpPort}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, ftpPort: parseInt(e.target.value) })}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Username"
                      value={deliveryConfig.ftpUsername}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, ftpUsername: e.target.value })}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="password"
                      label="Password"
                      value={deliveryConfig.ftpPassword}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, ftpPassword: e.target.value })}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Remote Path"
                      value={deliveryConfig.ftpPath}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, ftpPath: e.target.value })}
                    />
                  </Grid>
                </>
              )}
              
              {deliveryConfig.methods.includes('webhook') && (
                <>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Webhook URL"
                      value={deliveryConfig.webhookUrl}
                      onChange={(e) => setDeliveryConfig({ ...deliveryConfig, webhookUrl: e.target.value })}
                      error={!!validationErrors.webhookUrl}
                      helperText={validationErrors.webhookUrl}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>HTTP Method</InputLabel>
                      <Select
                        value={deliveryConfig.webhookMethod}
                        onChange={(e) => setDeliveryConfig({ ...deliveryConfig, webhookMethod: e.target.value })}
                        label="HTTP Method"
                      >
                        <MenuItem value="POST">POST</MenuItem>
                        <MenuItem value="PUT">PUT</MenuItem>
                        <MenuItem value="PATCH">PATCH</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </>
              )}
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Password Protection (Optional)"
                  type="password"
                  value={deliveryConfig.password}
                  onChange={(e) => setDeliveryConfig({ ...deliveryConfig, password: e.target.value })}
                  helperText="Set a password to protect the report file"
                />
              </Grid>
            </Grid>
          </Box>
        );
      
      case 2: // Notifications
        return (
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Notification Settings
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationConfig.onSuccess}
                      onChange={(e) => setNotificationConfig({ ...notificationConfig, onSuccess: e.target.checked })}
                    />
                  }
                  label="Notify on successful delivery"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationConfig.onFailure}
                      onChange={(e) => setNotificationConfig({ ...notificationConfig, onFailure: e.target.checked })}
                    />
                  }
                  label="Notify on delivery failure"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationConfig.notifyRecipients}
                      onChange={(e) => setNotificationConfig({ ...notificationConfig, notifyRecipients: e.target.checked })}
                    />
                  }
                  label="Send confirmation to report recipients"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationConfig.includePreview}
                      onChange={(e) => setNotificationConfig({ ...notificationConfig, includePreview: e.target.checked })}
                    />
                  }
                  label="Include report preview in notifications"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Alert severity="info">
                  <AlertTitle>Notification Channels</AlertTitle>
                  Notifications will be sent via:
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <EmailIcon />
                      </ListItemIcon>
                      <ListItemText primary="Email" secondary="To your registered email address" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <NotificationIcon />
                      </ListItemIcon>
                      <ListItemText primary="In-app notifications" secondary="Visible in the notification center" />
                    </ListItem>
                  </List>
                </Alert>
              </Grid>
            </Grid>
          </Box>
        );
      
      case 3: // Advanced
        return (
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Retry Configuration
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.retryOnFailure}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, retryOnFailure: e.target.checked })}
                    />
                  }
                  label="Retry on failure"
                />
              </Grid>
              
              {advancedConfig.retryOnFailure && (
                <>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Max Retries"
                      value={advancedConfig.maxRetries}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, maxRetries: parseInt(e.target.value) })}
                      InputProps={{
                        inputProps: { min: 1, max: 10 }
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Retry Delay (seconds)"
                      value={advancedConfig.retryDelay}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, retryDelay: parseInt(e.target.value) })}
                      InputProps={{
                        inputProps: { min: 60, max: 3600 }
                      }}
                    />
                  </Grid>
                </>
              )}
              
              <Grid item xs={12}>
                <Divider />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Performance & Security
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Timeout (seconds)"
                  value={advancedConfig.timeout}
                  onChange={(e) => setAdvancedConfig({ ...advancedConfig, timeout: parseInt(e.target.value) })}
                  InputProps={{
                    inputProps: { min: 300, max: 7200 }
                  }}
                  helperText="Maximum time allowed for report generation"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={advancedConfig.priority}
                    onChange={(e) => setAdvancedConfig({ ...advancedConfig, priority: e.target.value })}
                    label="Priority"
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="normal">Normal</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.compression}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, compression: e.target.checked })}
                    />
                  }
                  label="Enable compression"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.encryption}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, encryption: e.target.checked })}
                    />
                  }
                  label="Enable encryption"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.watermark}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, watermark: e.target.checked })}
                    />
                  }
                  label="Add watermark"
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.includeMetadata}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, includeMetadata: e.target.checked })}
                    />
                  }
                  label="Include metadata"
                />
              </Grid>
            </Grid>
          </Box>
        );
      
      case 4: // Review
        return (
          <Box sx={{ pt: 2 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              <AlertTitle>Schedule Summary</AlertTitle>
              Please review your schedule configuration before saving.
            </Alert>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <ScheduleIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Schedule"
                  secondary={getScheduleDescription()}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <CalendarIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Next Run"
                  secondary={format(calculateNextRun(), 'PPpp')}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <SendIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Delivery Methods"
                  secondary={deliveryConfig.methods.map(m => 
                    deliveryMethods.find(dm => dm.value === m)?.label
                  ).join(', ')}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  {React.createElement(fileFormats.find(f => f.value === deliveryConfig.format)?.icon || PdfIcon)}
                </ListItemIcon>
                <ListItemText
                  primary="Format"
                  secondary={fileFormats.find(f => f.value === deliveryConfig.format)?.label}
                />
              </ListItem>
              
              {deliveryConfig.methods.includes('email') && (
                <ListItem>
                  <ListItemIcon>
                    <EmailIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Recipients"
                    secondary={deliveryConfig.recipients.join(', ')}
                  />
                </ListItem>
              )}
              
              <ListItem>
                <ListItemIcon>
                  <NotificationIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Notifications"
                  secondary={
                    <Box>
                      {notificationConfig.onSuccess && <Chip label="On Success" size="small" sx={{ mr: 0.5 }} />}
                      {notificationConfig.onFailure && <Chip label="On Failure" size="small" color="error" />}
                    </Box>
                  }
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <SettingsIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Advanced Settings"
                  secondary={
                    <Box>
                      {advancedConfig.retryOnFailure && <Chip label={`Retry ${advancedConfig.maxRetries}x`} size="small" sx={{ mr: 0.5 }} />}
                      {advancedConfig.compression && <Chip label="Compressed" size="small" sx={{ mr: 0.5 }} />}
                      {advancedConfig.encryption && <Chip label="Encrypted" size="small" sx={{ mr: 0.5 }} />}
                      {advancedConfig.watermark && <Chip label="Watermark" size="small" />}
                    </Box>
                  }
                />
              </ListItem>
            </List>
            
            <Box sx={{ mt: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={scheduleConfig.enabled}
                    onChange={(e) => setScheduleConfig({ ...scheduleConfig, enabled: e.target.checked })}
                  />
                }
                label="Enable schedule immediately"
              />
            </Box>
          </Box>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <ScheduleIcon />
              <Typography variant="h6">
                {selectedSchedule ? 'Edit Schedule' : 'Schedule Report'}
              </Typography>
            </Box>
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Stepper activeStep={activeStep} orientation={isMobile ? 'vertical' : 'horizontal'}>
              {steps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel
                    icon={React.createElement(step.icon)}
                    onClick={() => setActiveStep(index)}
                    sx={{ cursor: 'pointer' }}
                  >
                    {step.label}
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>
          
          {renderStepContent(activeStep)}
        </DialogContent>
        
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          {activeStep > 0 && (
            <Button
              onClick={() => setActiveStep(activeStep - 1)}
              disabled={isLoading}
            >
              Back
            </Button>
          )}
          {activeStep < steps.length - 1 && (
            <Button
              variant="contained"
              onClick={() => setActiveStep(activeStep + 1)}
              disabled={isLoading}
            >
              Next
            </Button>
          )}
          {activeStep === steps.length - 1 && (
            <Button
              variant="contained"
              onClick={handleSave}
              disabled={isLoading}
              startIcon={isLoading ? <CircularProgress size={20} /> : <CheckIcon />}
            >
              {isLoading ? 'Saving...' : 'Save Schedule'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default ReportScheduler;