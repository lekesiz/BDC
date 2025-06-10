# BDC Advanced Analytics System

A comprehensive analytics and reporting system for the BDC (Business Development Center) platform, featuring real-time data monitoring, customizable dashboards, and advanced visualization capabilities.

## Overview

The BDC Advanced Analytics System provides deep insights into beneficiary progress, trainer effectiveness, system usage patterns, and overall platform performance through an integrated suite of analytics tools and dashboards.

## System Architecture

### Core Components

1. **Analytics Service Layer** (`src/services/analytics.service.js`)
   - Data aggregation and time-series processing
   - Caching mechanisms for improved performance
   - API integration for backend analytics endpoints
   - Support for custom metrics calculation

2. **Real-time Analytics Context** (`src/contexts/AnalyticsContext.jsx`)
   - WebSocket integration for live data streaming
   - Real-time event handling and notifications
   - Subscription management for analytics updates
   - Performance monitoring and alerts

3. **Advanced Charts Library** (`src/components/analytics/charts/ChartLibrary.jsx`)
   - Comprehensive visualization components
   - Interactive charts with drill-down capabilities
   - Support for multiple chart types (line, bar, pie, radar, etc.)
   - Export functionality for charts

4. **Export Service** (`src/services/export.service.js`)
   - Multi-format export capabilities (PDF, Excel, CSV)
   - Customizable export templates
   - Batch export functionality
   - Chart-to-image conversion

## Features

### 🔴 Real-time Dashboards
- **Live Data Streaming**: Real-time updates via WebSocket connections
- **System Health Monitoring**: Live system performance metrics
- **Alert Notifications**: Automatic alerts for critical issues
- **Activity Timeline**: Real-time user and system activity tracking

### 📊 Interactive Charts and Visualizations
- **Drill-down Capabilities**: Click-through data exploration
- **Multiple Chart Types**: Line, bar, pie, radar, and custom charts
- **Responsive Design**: Mobile-optimized visualizations
- **Export Options**: Save charts as images or include in reports

### 🎯 Performance Analytics
- **Beneficiary Progress Tracking**: Individual and cohort analysis
- **Trainer Effectiveness Metrics**: Performance ratings and success rates
- **Program Analytics**: Completion rates and satisfaction scores
- **System Usage Patterns**: User behavior and engagement metrics

### 🛠️ Customizable Dashboards
- **Drag-and-Drop Interface**: Rearrange dashboard widgets
- **Widget Library**: Pre-built components for common metrics
- **Layout Persistence**: Save and share custom dashboard layouts
- **Role-based Access**: Different views for different user roles

### 📄 Advanced Export Capabilities
- **Multiple Formats**: PDF reports, Excel spreadsheets, CSV data
- **Custom Templates**: Branded report templates
- **Scheduled Exports**: Automated report generation
- **Batch Operations**: Export multiple datasets simultaneously

### ⚡ System Health Monitoring
- **Real-time Metrics**: CPU, memory, network, and database monitoring
- **Performance Alerts**: Threshold-based alert system
- **Historical Trending**: Performance data over time
- **Service Status Tracking**: Monitor individual system components

## File Structure

```
src/
├── components/analytics/
│   ├── charts/
│   │   └── ChartLibrary.jsx                 # Advanced charts components
│   ├── CustomizableDashboard.jsx            # Drag-and-drop dashboard builder
│   ├── RealTimeDashboard.jsx                # Live monitoring dashboard
│   ├── SystemHealthMonitoring.jsx          # System health tracking
│   └── TrainerPerformanceDashboard.jsx     # Trainer analytics
├── contexts/
│   └── AnalyticsContext.jsx                # Real-time analytics context
├── pages/analytics/
│   └── AdvancedAnalyticsDashboardPage.jsx  # Main analytics hub
└── services/
    ├── analytics.service.js                # Analytics data service
    └── export.service.js                   # Export functionality
```

## Usage Guide

### Basic Setup

1. **Import the Analytics Provider**:
```jsx
import { AnalyticsProvider } from '@/contexts/AnalyticsContext';

function App() {
  return (
    <AnalyticsProvider>
      {/* Your app components */}
    </AnalyticsProvider>
  );
}
```

2. **Use Analytics in Components**:
```jsx
import { useAnalytics } from '@/contexts/AnalyticsContext';

function MyComponent() {
  const { requestAnalyticsData, realtimeMetrics } = useAnalytics();
  
  useEffect(() => {
    requestAnalyticsData('beneficiaries');
  }, []);
  
  return <div>Active Users: {realtimeMetrics.activeUsers}</div>;
}
```

### Creating Custom Charts

```jsx
import { BaseChart } from '@/components/analytics/charts/ChartLibrary';

function CustomChart() {
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [{
      label: 'Progress',
      data: [65, 59, 80, 81],
      borderColor: '#3B82F6'
    }]
  };

  return (
    <BaseChart
      type="line"
      data={data}
      title="Progress Over Time"
      onDrillDown={(point) => console.log('Drill down:', point)}
      showControls={true}
    />
  );
}
```

### Exporting Data

```jsx
import exportService from '@/services/export.service';

async function exportDashboard() {
  const data = {
    summary: { totalUsers: 150, activePrograms: 12 },
    beneficiaryPerformance: [/* data array */]
  };
  
  await exportService.exportToPDF(data, {
    filename: 'monthly_report',
    includeCharts: true
  });
}
```

### Real-time Subscriptions

```jsx
import { useAnalytics } from '@/contexts/AnalyticsContext';

function RealTimeComponent() {
  const { subscribe } = useAnalytics();
  
  useEffect(() => {
    const unsubscribe = subscribe('beneficiary_progress', (data) => {
      console.log('Progress update:', data);
    });
    
    return unsubscribe;
  }, [subscribe]);
}
```

## API Integration

### Analytics Endpoints

The system integrates with the following backend endpoints:

- `GET /api/analytics/dashboard` - Dashboard overview data
- `GET /api/analytics/beneficiaries` - Beneficiary analytics
- `GET /api/analytics/trainers` - Trainer performance metrics
- `GET /api/analytics/programs` - Program analytics
- `GET /api/analytics/realtime/metrics` - Real-time metrics
- `GET /api/analytics/system/health` - System health status
- `POST /api/analytics/export` - Data export functionality

### WebSocket Events

Real-time updates are handled through WebSocket events:

- `analytics_update` - General analytics data updates
- `beneficiary_progress` - Beneficiary progress changes
- `trainer_activity` - Trainer activity updates
- `system_health_update` - System health changes
- `performance_alert` - Performance threshold alerts

## Configuration

### Environment Variables

```env
VITE_ANALYTICS_API_URL=http://localhost:5001/api/analytics
VITE_WEBSOCKET_URL=ws://localhost:5001
VITE_ANALYTICS_CACHE_TIMEOUT=300000
VITE_EXPORT_MAX_RETRIES=3
```

### Dashboard Configuration

```javascript
// Default dashboard layouts
const dashboardConfig = {
  refreshInterval: 30000,        // 30 seconds
  cacheTimeout: 300000,          // 5 minutes
  maxDataPoints: 100,            // Chart data points
  alertThresholds: {
    cpu: { warning: 70, critical: 85 },
    memory: { warning: 75, critical: 90 }
  }
};
```

## Customization

### Adding New Widget Types

1. Define the widget type in `WIDGET_TYPES`:
```javascript
custom_metric: {
  name: 'Custom Metric',
  icon: Target,
  description: 'Custom metric display',
  defaultSize: { w: 1, h: 1 },
  configurable: ['title', 'metric', 'format']
}
```

2. Add rendering logic in `renderWidgetContent`:
```javascript
case 'custom_metric':
  return <CustomMetricWidget config={config} data={data} />;
```

### Creating Custom Chart Types

Extend the `BaseChart` component:
```jsx
export const CustomChart = ({ data, options, ...props }) => {
  const processedData = useMemo(() => {
    // Custom data processing
    return transformData(data);
  }, [data]);

  return (
    <BaseChart
      type="custom"
      data={processedData}
      options={{ ...defaultOptions, ...options }}
      {...props}
    />
  );
};
```

## Performance Optimization

### Caching Strategy
- In-memory caching for frequently accessed data
- 5-minute cache timeout for dashboard data
- 10-second cache for real-time metrics
- Intelligent cache invalidation

### Real-time Updates
- Efficient WebSocket connection management
- Selective event subscriptions
- Batched updates for improved performance
- Connection retry logic with exponential backoff

### Chart Rendering
- Canvas-based charts for better performance
- Lazy loading for large datasets
- Virtual scrolling for data tables
- Optimized re-rendering with React.memo

## Security Considerations

### Data Access Control
- Role-based access to different analytics views
- API endpoint authentication and authorization
- Secure WebSocket connections with token validation
- Data encryption for sensitive metrics

### Export Security
- Watermarked PDF exports
- Access logging for data exports
- File size limits for exports
- Secure temporary file handling

## Monitoring and Debugging

### Analytics Debugging
```javascript
// Enable debug mode
localStorage.setItem('analytics_debug', 'true');

// View cache statistics
analyticsService.getCacheStats();

// Clear analytics cache
analyticsService.clearCache();
```

### Performance Monitoring
- Real-time performance metrics tracking
- Error boundary implementation
- Comprehensive logging system
- User action analytics

## Dependencies

### Core Dependencies
- `chart.js` - Chart rendering
- `react-chartjs-2` - React Chart.js integration
- `@hello-pangea/dnd` - Drag and drop functionality
- `framer-motion` - Animations
- `date-fns` - Date manipulation
- `jspdf` - PDF generation
- `xlsx` - Excel file generation

### Development Dependencies
- `@testing-library/react` - Component testing
- `vitest` - Test runner
- `cypress` - E2E testing

## Testing

### Unit Tests
```bash
npm run test:analytics
```

### Integration Tests
```bash
npm run test:analytics:integration
```

### E2E Tests
```bash
npm run cy:run -- --spec "cypress/e2e/analytics-*.cy.js"
```

## Deployment

### Build Optimization
```bash
npm run build:analytics
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
COPY . /app
WORKDIR /app
RUN npm install && npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

## Support and Maintenance

### Troubleshooting
- Check browser console for WebSocket connection issues
- Verify API endpoint availability
- Clear browser cache if charts don't load
- Check user permissions for restricted views

### Performance Tuning
- Adjust cache timeouts based on data freshness requirements
- Optimize chart data point limits for large datasets
- Configure WebSocket heartbeat intervals
- Monitor memory usage for long-running sessions

## Contributing

1. Follow the existing component structure
2. Add comprehensive TypeScript types
3. Include unit tests for new features
4. Update documentation for API changes
5. Test on multiple screen sizes and devices

## License

This analytics system is part of the BDC platform and subject to the same licensing terms.

---

For additional support or feature requests, please contact the BDC development team.