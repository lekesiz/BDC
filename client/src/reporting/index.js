// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Advanced Reporting System - Main Export
 * 
 * Exports all reporting components, hooks, and utilities
 */

// Components
export { default as ReportBuilder } from './components/ReportBuilder';
export { default as DashboardBuilder } from './components/DashboardBuilder';
export { default as WidgetLibrary } from './components/WidgetLibrary';
export { default as VisualizationPanel } from './components/VisualizationPanel';
export { default as ExportPanel } from './components/ExportPanel';
export { default as RealtimeMonitor } from './components/RealtimeMonitor';

// Widget Components
export { default as ChartWidget } from './components/widgets/ChartWidget';
export { default as MetricWidget } from './components/widgets/MetricWidget';
export { default as TableWidget } from './components/widgets/TableWidget';
export { default as MapWidget } from './components/widgets/MapWidget';
export { default as CalendarWidget } from './components/widgets/CalendarWidget';
export { default as ProgressWidget } from './components/widgets/ProgressWidget';
export { default as TextWidget } from './components/widgets/TextWidget';

// Drag and Drop Components
export { default as DragDropProvider } from './components/dragdrop/DragDropProvider';
export { default as DraggableField } from './components/dragdrop/DraggableField';
export { default as DropZone } from './components/dragdrop/DropZone';
export { default as FieldPalette } from './components/dragdrop/FieldPalette';

// Visualization Components
export { default as ChartRenderer } from './components/visualizations/ChartRenderer';
export { default as MapRenderer } from './components/visualizations/MapRenderer';
export { default as HeatmapRenderer } from './components/visualizations/HeatmapRenderer';

// Pages
export { default as ReportBuilderPage } from './pages/ReportBuilderPage';
export { default as DashboardPage } from './pages/DashboardPage';
export { default as ReportsListPage } from './pages/ReportsListPage';
export { default as ScheduledReportsPage } from './pages/ScheduledReportsPage';

// Hooks
export { default as useReportBuilder } from './hooks/useReportBuilder';
export { default as useDashboard } from './hooks/useDashboard';
export { default as useVisualization } from './hooks/useVisualization';
export { default as useExport } from './hooks/useExport';
export { default as useRealtime } from './hooks/useRealtime';
export { default as useDragDrop } from './hooks/useDragDrop';

// Services
export { default as ReportingAPI } from './services/reportingAPI';
export { default as RealtimeService } from './services/realtimeService';
export { default as ExportService } from './services/exportService';

// Utils
export * from './utils/chartUtils';
export * from './utils/dataUtils';
export * from './utils/exportUtils';
export * from './utils/validationUtils';