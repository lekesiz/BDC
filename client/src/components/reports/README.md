# Report Builder Component

A comprehensive, drag-and-drop report builder for the BDC client application that allows non-technical users to create professional reports with ease.

## Features

### Core Features
- **Drag-and-Drop Interface**: Intuitive drag-and-drop functionality for adding and arranging report sections and widgets
- **Multiple Report Templates**: Pre-built templates including:
  - Executive Summary
  - Detailed Analysis
  - Progress Report
  - Trainer Evaluation
  - Financial Summary
  - Attendance Report
  - Custom Blank Template

### Data Sources
- Beneficiaries
- Evaluations
- Programs
- Trainers
- Analytics
- Performance Metrics

### Widget Library
- **Charts**: Bar, Line, Pie, Donut, Area, Radar charts (powered by Recharts)
- **Tables**: Sortable, filterable tables with pagination
- **KPI Cards**: Display key metrics with trends and progress indicators
- **Text Blocks**: Rich text content with formatting options
- **Images**: Support for logos and images with alignment options

### Layout Options
- Single column
- Two-column layout
- Grid layout (3 columns)
- Customizable per section

### Export Options
- PDF export with formatted layout
- Excel/CSV export for data tables
- Print-friendly format

### Additional Features
- Real-time preview
- Auto-save functionality
- Dark mode support
- Mobile responsive design
- Save as template functionality
- Custom filters and date ranges
- Conditional formatting

## Usage

### Basic Usage
```jsx
import { ReportBuilder } from '../components/reports';

function App() {
  return <ReportBuilder />;
}
```

### Component Structure

#### Main Components
1. **ReportBuilder**: The main container component that orchestrates the entire report building experience
2. **WidgetLibrary**: Sidebar component containing all available widgets organized by category
3. **ReportSection**: Container for widgets with layout options
4. **ReportWidget**: Individual widget component (chart, table, KPI, etc.)
5. **ReportPreview**: Real-time preview of the report

### Creating a Report

1. **Start with a Template or Blank Report**
   - Choose from pre-built templates
   - Or start with a blank canvas

2. **Add Sections**
   - Click "Add Section" to create a new section
   - Name your sections appropriately
   - Choose layout (single, two-column, or grid)

3. **Add Widgets**
   - Drag widgets from the library to sections
   - Or use the "Add Widget" button within sections

4. **Configure Widgets**
   - Click the settings icon on any widget
   - Configure data source, appearance, and behavior
   - Add titles and descriptions

5. **Arrange Content**
   - Drag sections to reorder
   - Drag widgets within or between sections
   - Use layout options for better organization

6. **Set Data Parameters**
   - Select data sources in the Data tab
   - Set date ranges
   - Apply filters

7. **Export or Save**
   - Save your report
   - Save as a template for future use
   - Export to PDF, Excel, or CSV

### Widget Configuration

Each widget type has specific configuration options:

#### Chart Widgets
- Chart type selection
- Title and labels
- Color schemes
- Legend and grid options
- Data source mapping

#### KPI Widgets
- Title and value
- Unit of measurement
- Trend indicators (up/down/neutral)
- Progress bars
- Custom colors

#### Table Widgets
- Column selection
- Sorting options
- Filtering capabilities
- Pagination settings
- Export options

#### Text Widgets
- Rich text editing
- Font size options
- Text alignment
- HTML content support

### Keyboard Shortcuts
- `Ctrl/Cmd + S`: Save report
- `Ctrl/Cmd + P`: Print preview
- `Delete`: Remove selected widget/section
- `Escape`: Cancel current operation

### Best Practices

1. **Organization**
   - Group related widgets in sections
   - Use clear, descriptive section titles
   - Maintain consistent layouts

2. **Performance**
   - Limit the number of widgets per section
   - Use pagination for large tables
   - Optimize image sizes

3. **Accessibility**
   - Add descriptive titles to all widgets
   - Use appropriate color contrasts
   - Include alt text for images

4. **Data Accuracy**
   - Verify data sources before exporting
   - Use appropriate date ranges
   - Apply relevant filters

## Customization

### Adding New Widget Types

To add a new widget type:

1. Add the widget definition to `WidgetLibrary.jsx`
2. Implement the widget rendering in `ReportWidget.jsx`
3. Add configuration options
4. Update export utilities if needed

### Creating Custom Templates

Templates are defined in `reportTemplates.js`. To add a new template:

```javascript
{
  id: 'template-id',
  name: 'Template Name',
  description: 'Template description',
  category: 'Category',
  sections: [
    {
      id: 'section-1',
      title: 'Section Title',
      layout: 'single',
      widgets: [
        // Widget definitions
      ]
    }
  ],
  dataSources: ['source1', 'source2'],
  layout: 'single'
}
```

## API Integration

The report builder is designed to work with your backend API. Update the data fetching logic in:
- Widget data loading
- Export utilities
- Real-time data updates

## Troubleshooting

### Common Issues

1. **Widgets not dragging**: Ensure the drag handle is being used
2. **Export failing**: Check browser permissions for downloads
3. **Preview not updating**: Toggle preview off and on
4. **Auto-save not working**: Check localStorage availability

### Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 13+)
- IE11: Not supported

## Future Enhancements

- Collaborative editing
- Version history
- Scheduled report generation
- Email distribution
- Advanced data visualizations
- Custom branding options