import jsPDF from 'jspdf';
import { format } from 'date-fns';

// Helper function to extract widget data
const extractWidgetData = (widget) => {
  switch (widget.type) {
    case 'kpi':
      return {
        type: 'kpi',
        title: widget.config.title || 'KPI',
        value: `${widget.config.value || 0}${widget.config.unit || ''}`,
        trend: widget.config.trend,
        trendValue: widget.config.trendValue
      };
    
    case 'text':
      return {
        type: 'text',
        content: widget.config.content || ''
      };
    
    case 'table':
      // In a real implementation, this would fetch actual data
      return {
        type: 'table',
        title: widget.config.title || 'Table',
        headers: ['Name', 'Value', 'Status'],
        rows: [
          ['Sample Row 1', '100', 'Active'],
          ['Sample Row 2', '200', 'Active'],
          ['Sample Row 3', '300', 'Inactive']
        ]
      };
    
    case 'chart':
      // In a real implementation, this would fetch actual chart data
      return {
        type: 'chart',
        title: widget.config.title || 'Chart',
        chartType: widget.config.chartType,
        data: [
          { label: 'Jan', value: 100 },
          { label: 'Feb', value: 150 },
          { label: 'Mar', value: 120 },
          { label: 'Apr', value: 180 }
        ]
      };
    
    default:
      return null;
  }
};

// Export to PDF
export const exportToPDF = async (reportData) => {
  const pdf = new jsPDF();
  let yPosition = 20;
  const pageHeight = pdf.internal.pageSize.height;
  const margin = 20;
  
  // Add title
  pdf.setFontSize(20);
  pdf.text(reportData.name || 'Report', margin, yPosition);
  yPosition += 10;
  
  // Add description
  if (reportData.description) {
    pdf.setFontSize(12);
    pdf.text(reportData.description, margin, yPosition);
    yPosition += 10;
  }
  
  // Add metadata
  pdf.setFontSize(10);
  pdf.setTextColor(100);
  pdf.text(`Generated on: ${format(new Date(reportData.generatedAt), 'PPP')}`, margin, yPosition);
  yPosition += 15;
  pdf.setTextColor(0);
  
  // Add sections
  reportData.sections.forEach((section) => {
    // Check if we need a new page
    if (yPosition > pageHeight - 40) {
      pdf.addPage();
      yPosition = 20;
    }
    
    // Section title
    pdf.setFontSize(16);
    pdf.setFont(undefined, 'bold');
    pdf.text(section.title, margin, yPosition);
    pdf.setFont(undefined, 'normal');
    yPosition += 10;
    
    // Process widgets
    section.widgets.forEach((widget) => {
      const widgetData = extractWidgetData(widget);
      if (!widgetData) return;
      
      // Check if we need a new page
      if (yPosition > pageHeight - 60) {
        pdf.addPage();
        yPosition = 20;
      }
      
      switch (widgetData.type) {
        case 'kpi':
          pdf.setFontSize(12);
          pdf.text(widgetData.title, margin, yPosition);
          yPosition += 5;
          pdf.setFontSize(18);
          pdf.setFont(undefined, 'bold');
          pdf.text(widgetData.value, margin, yPosition);
          pdf.setFont(undefined, 'normal');
          if (widgetData.trendValue) {
            pdf.setFontSize(10);
            const trendText = `${widgetData.trend === 'up' ? '↑' : '↓'} ${widgetData.trendValue}%`;
            pdf.text(trendText, margin + 40, yPosition);
          }
          yPosition += 15;
          break;
        
        case 'text':
          pdf.setFontSize(11);
          // Simple HTML stripping
          const cleanText = widgetData.content.replace(/<[^>]*>/g, '');
          const lines = pdf.splitTextToSize(cleanText, 170);
          lines.forEach((line) => {
            if (yPosition > pageHeight - 20) {
              pdf.addPage();
              yPosition = 20;
            }
            pdf.text(line, margin, yPosition);
            yPosition += 5;
          });
          yPosition += 10;
          break;
        
        case 'table':
          pdf.setFontSize(12);
          pdf.text(widgetData.title, margin, yPosition);
          yPosition += 10;
          
          // Simple table rendering
          pdf.setFontSize(10);
          // Headers
          pdf.setFont(undefined, 'bold');
          widgetData.headers.forEach((header, index) => {
            pdf.text(header, margin + (index * 50), yPosition);
          });
          pdf.setFont(undefined, 'normal');
          yPosition += 5;
          
          // Rows
          widgetData.rows.forEach((row) => {
            if (yPosition > pageHeight - 20) {
              pdf.addPage();
              yPosition = 20;
            }
            row.forEach((cell, index) => {
              pdf.text(cell.toString(), margin + (index * 50), yPosition);
            });
            yPosition += 5;
          });
          yPosition += 10;
          break;
        
        case 'chart':
          pdf.setFontSize(12);
          pdf.text(`${widgetData.title} (${widgetData.chartType} chart)`, margin, yPosition);
          yPosition += 5;
          pdf.setFontSize(10);
          pdf.text('[Chart visualization would appear here]', margin, yPosition);
          yPosition += 20;
          break;
      }
    });
    
    yPosition += 10;
  });
  
  // Save the PDF
  pdf.save(`${reportData.name || 'report'}_${format(new Date(), 'yyyy-MM-dd')}.pdf`);
};

// Export to Excel (simplified CSV format that Excel can open)
export const exportToExcel = async (reportData) => {
  let csvContent = 'Report Summary\n';
  csvContent += `Report Name,${reportData.name || 'Report'}\n`;
  csvContent += `Description,${reportData.description || ''}\n`;
  csvContent += `Generated On,${format(new Date(reportData.generatedAt), 'PPP')}\n`;
  csvContent += `Date Range,${reportData.dateRange ? `${reportData.dateRange.start} to ${reportData.dateRange.end}` : 'All time'}\n`;
  csvContent += `\nSections,${reportData.sections.length}\n`;
  csvContent += `Total Widgets,${reportData.sections.reduce((acc, section) => acc + section.widgets.length, 0)}\n\n`;
  
  // Add data from each section
  reportData.sections.forEach((section) => {
    csvContent += `\n${section.title}\n`;
    
    // Extract KPIs
    const kpiWidgets = section.widgets.filter(w => w.type === 'kpi');
    if (kpiWidgets.length > 0) {
      csvContent += 'KPI,Value,Trend,Change %\n';
      kpiWidgets.forEach((widget) => {
        const widgetData = extractWidgetData(widget);
        if (widgetData && widgetData.type === 'kpi') {
          csvContent += `"${widgetData.title}","${widgetData.value}","${widgetData.trend || '-'}","${widgetData.trendValue || '-'}"\n`;
        }
      });
      csvContent += '\n';
    }
    
    // Extract tables
    const tableWidgets = section.widgets.filter(w => w.type === 'table');
    tableWidgets.forEach((widget) => {
      const widgetData = extractWidgetData(widget);
      if (widgetData && widgetData.type === 'table') {
        csvContent += `${widgetData.title}\n`;
        csvContent += widgetData.headers.join(',') + '\n';
        widgetData.rows.forEach(row => {
          csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
        });
        csvContent += '\n';
      }
    });
  });
  
  // Create blob and download with .csv extension (Excel will open it)
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${reportData.name || 'report'}_${format(new Date(), 'yyyy-MM-dd')}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Export to CSV (simplified - exports first table found)
export const exportToCSV = async (reportData) => {
  let csvContent = '';
  
  // Find first table widget
  let tableFound = false;
  
  for (const section of reportData.sections) {
    for (const widget of section.widgets) {
      if (widget.type === 'table' && !tableFound) {
        const widgetData = extractWidgetData(widget);
        if (widgetData && widgetData.type === 'table') {
          // Add headers
          csvContent += widgetData.headers.join(',') + '\n';
          
          // Add rows
          widgetData.rows.forEach(row => {
            csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
          });
          
          tableFound = true;
          break;
        }
      }
    }
    if (tableFound) break;
  }
  
  if (!tableFound) {
    // If no table found, export KPIs
    csvContent = 'KPI,Value,Trend,Change\n';
    
    reportData.sections.forEach(section => {
      section.widgets.forEach(widget => {
        if (widget.type === 'kpi') {
          const widgetData = extractWidgetData(widget);
          if (widgetData) {
            csvContent += `"${widgetData.title}","${widgetData.value}","${widgetData.trend || '-'}","${widgetData.trendValue || '-'}"\n`;
          }
        }
      });
    });
  }
  
  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${reportData.name || 'report'}_${format(new Date(), 'yyyy-MM-dd')}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Helper function to export widget as image (for future use)
export const exportWidgetAsImage = async (widgetElement, filename) => {
  // This would require a library like html2canvas
  // Implementation would go here
  console.log('Export widget as image:', filename);
};

// Helper function to print report
export const printReport = (reportData) => {
  // Create a new window with print-friendly styling
  const printWindow = window.open('', '_blank');
  
  const printContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${reportData.name || 'Report'}</title>
      <style>
        @media print {
          body { margin: 0; font-family: Arial, sans-serif; }
          .page-break { page-break-after: always; }
          h1 { font-size: 24px; margin-bottom: 10px; }
          h2 { font-size: 20px; margin-top: 20px; margin-bottom: 10px; }
          h3 { font-size: 16px; margin-top: 15px; margin-bottom: 8px; }
          .metadata { color: #666; font-size: 12px; margin-bottom: 20px; }
          .kpi { margin: 10px 0; }
          .kpi-value { font-size: 24px; font-weight: bold; }
          .kpi-trend { font-size: 14px; color: #666; }
          table { width: 100%; border-collapse: collapse; margin: 10px 0; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f5f5f5; font-weight: bold; }
        }
      </style>
    </head>
    <body onload="window.print(); window.close();">
      <h1>${reportData.name || 'Report'}</h1>
      ${reportData.description ? `<p>${reportData.description}</p>` : ''}
      <div class="metadata">
        Generated on: ${format(new Date(reportData.generatedAt), 'PPP')}
      </div>
      ${reportData.sections.map(section => `
        <div class="section">
          <h2>${section.title}</h2>
          ${section.widgets.map(widget => {
            const data = extractWidgetData(widget);
            if (!data) return '';
            
            switch (data.type) {
              case 'kpi':
                return `
                  <div class="kpi">
                    <strong>${data.title}:</strong>
                    <span class="kpi-value">${data.value}</span>
                    ${data.trendValue ? `<span class="kpi-trend">${data.trend === 'up' ? '↑' : '↓'} ${data.trendValue}%</span>` : ''}
                  </div>
                `;
              case 'text':
                return `<div>${data.content}</div>`;
              case 'table':
                return `
                  <h3>${data.title}</h3>
                  <table>
                    <thead>
                      <tr>${data.headers.map(h => `<th>${h}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                      ${data.rows.map(row => `
                        <tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>
                      `).join('')}
                    </tbody>
                  </table>
                `;
              default:
                return '';
            }
          }).join('')}
        </div>
      `).join('<div class="page-break"></div>')}
    </body>
    </html>
  `;
  
  printWindow.document.write(printContent);
  printWindow.document.close();
};