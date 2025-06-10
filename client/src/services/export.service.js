// Advanced Export Service
// Comprehensive export functionality for PDF, Excel, and CSV formats

import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { utils, writeFile } from 'xlsx';
import { format } from 'date-fns';

class ExportService {
  constructor() {
    this.defaultOptions = {
      filename: 'bdc_analytics_export',
      timestamp: true,
      includeCharts: true,
      includeMetadata: true
    };
  }

  // Generate filename with timestamp
  generateFilename(baseFilename, extension, includeTimestamp = true) {
    const timestamp = includeTimestamp ? `_${format(new Date(), 'yyyy-MM-dd_HH-mm-ss')}` : '';
    return `${baseFilename}${timestamp}.${extension}`;
  }

  // Export to PDF
  async exportToPDF(data, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    const doc = new jsPDF();
    
    try {
      // Set up document properties
      doc.setProperties({
        title: 'BDC Analytics Report',
        subject: 'Analytics Export',
        author: 'BDC System',
        keywords: 'analytics, report, bdc',
        creator: 'BDC Analytics System'
      });

      let yPosition = 20;

      // Header
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text('BDC Analytics Report', 20, yPosition);
      yPosition += 10;

      // Metadata
      if (config.includeMetadata) {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(`Generated on: ${format(new Date(), 'PPP p')}`, 20, yPosition);
        yPosition += 5;
        
        if (data.dateRange) {
          doc.text(`Date Range: ${data.dateRange.start} to ${data.dateRange.end}`, 20, yPosition);
          yPosition += 5;
        }
        
        if (data.filters) {
          doc.text(`Filters Applied: ${JSON.stringify(data.filters)}`, 20, yPosition);
          yPosition += 10;
        }
      }

      // Executive Summary
      if (data.summary) {
        yPosition += 5;
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Executive Summary', 20, yPosition);
        yPosition += 10;

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        
        const summaryItems = [
          { label: 'Total Beneficiaries', value: data.summary.totalBeneficiaries },
          { label: 'Active Programs', value: data.summary.activePrograms },
          { label: 'Completion Rate', value: `${data.summary.completionRate}%` },
          { label: 'System Uptime', value: `${data.summary.systemUptime}%` }
        ];

        summaryItems.forEach(item => {
          doc.text(`${item.label}: ${item.value}`, 30, yPosition);
          yPosition += 5;
        });
      }

      // Key Metrics Table
      if (data.metrics) {
        yPosition += 10;
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Key Metrics', 20, yPosition);
        yPosition += 5;

        const metricsData = Object.entries(data.metrics).map(([key, value]) => [
          key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
          typeof value === 'number' ? value.toLocaleString() : value
        ]);

        doc.autoTable({
          startY: yPosition,
          head: [['Metric', 'Value']],
          body: metricsData,
          theme: 'grid',
          styles: { fontSize: 9 },
          headStyles: { fillColor: [59, 130, 246] }
        });

        yPosition = doc.lastAutoTable.finalY + 10;
      }

      // Beneficiary Performance Table
      if (data.beneficiaryPerformance) {
        if (yPosition > 250) {
          doc.addPage();
          yPosition = 20;
        }

        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Beneficiary Performance', 20, yPosition);
        yPosition += 5;

        const beneficiaryData = data.beneficiaryPerformance.map(b => [
          b.name,
          b.program,
          `${b.progress}%`,
          `${b.attendanceRate}%`,
          b.status
        ]);

        doc.autoTable({
          startY: yPosition,
          head: [['Name', 'Program', 'Progress', 'Attendance', 'Status']],
          body: beneficiaryData,
          theme: 'grid',
          styles: { fontSize: 8 },
          headStyles: { fillColor: [59, 130, 246] },
          columnStyles: {
            2: { halign: 'center' },
            3: { halign: 'center' }
          }
        });

        yPosition = doc.lastAutoTable.finalY + 10;
      }

      // Trainer Performance Table
      if (data.trainerPerformance) {
        if (yPosition > 250) {
          doc.addPage();
          yPosition = 20;
        }

        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Trainer Performance', 20, yPosition);
        yPosition += 5;

        const trainerData = data.trainerPerformance.map(t => [
          t.name,
          t.assignedBeneficiaries,
          t.sessionsConducted,
          `${t.avgRating}/5`,
          `${t.successRate}%`
        ]);

        doc.autoTable({
          startY: yPosition,
          head: [['Name', 'Beneficiaries', 'Sessions', 'Rating', 'Success Rate']],
          body: trainerData,
          theme: 'grid',
          styles: { fontSize: 8 },
          headStyles: { fillColor: [16, 185, 129] },
          columnStyles: {
            1: { halign: 'center' },
            2: { halign: 'center' },
            3: { halign: 'center' },
            4: { halign: 'center' }
          }
        });

        yPosition = doc.lastAutoTable.finalY + 10;
      }

      // Program Performance Table
      if (data.programPerformance) {
        if (yPosition > 250) {
          doc.addPage();
          yPosition = 20;
        }

        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Program Performance', 20, yPosition);
        yPosition += 5;

        const programData = data.programPerformance.map(p => [
          p.name,
          p.beneficiaries,
          `${p.completionRate}%`,
          `${p.avgSatisfaction}/5`,
          p.status
        ]);

        doc.autoTable({
          startY: yPosition,
          head: [['Program', 'Beneficiaries', 'Completion Rate', 'Satisfaction', 'Status']],
          body: programData,
          theme: 'grid',
          styles: { fontSize: 8 },
          headStyles: { fillColor: [139, 92, 246] },
          columnStyles: {
            1: { halign: 'center' },
            2: { halign: 'center' },
            3: { halign: 'center' }
          }
        });
      }

      // Add charts if available and requested
      if (config.includeCharts && data.charts) {
        doc.addPage();
        yPosition = 20;

        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Charts and Visualizations', 20, yPosition);
        yPosition += 10;

        // Note about charts
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text('Note: Chart images are exported as static snapshots', 20, yPosition);
        
        // Here you would add chart images if available
        // This would require converting canvas elements to images
      }

      // Footer on each page
      const pageCount = doc.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setFont('helvetica', 'normal');
        doc.text(
          `Page ${i} of ${pageCount} | Generated by BDC Analytics System`,
          20,
          doc.internal.pageSize.height - 10
        );
      }

      // Save the PDF
      const filename = this.generateFilename(config.filename, 'pdf', config.timestamp);
      doc.save(filename);

      return { success: true, filename };
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw new Error('Failed to generate PDF export');
    }
  }

  // Export to Excel
  async exportToExcel(data, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    
    try {
      const workbook = utils.book_new();

      // Summary sheet
      if (data.summary) {
        const summaryData = [
          ['Metric', 'Value'],
          ['Total Beneficiaries', data.summary.totalBeneficiaries],
          ['Active Programs', data.summary.activePrograms],
          ['Completion Rate', `${data.summary.completionRate}%`],
          ['System Uptime', `${data.summary.systemUptime}%`],
          ['Generated On', format(new Date(), 'PPP p')]
        ];

        const summarySheet = utils.aoa_to_sheet(summaryData);
        
        // Style the header row
        summarySheet['A1'].s = { font: { bold: true }, fill: { fgColor: { rgb: "3B82F6" } } };
        summarySheet['B1'].s = { font: { bold: true }, fill: { fgColor: { rgb: "3B82F6" } } };

        utils.book_append_sheet(workbook, summarySheet, 'Summary');
      }

      // Beneficiary Performance sheet
      if (data.beneficiaryPerformance) {
        const beneficiaryData = [
          ['Name', 'Email', 'Program', 'Progress (%)', 'Attendance Rate (%)', 'Status'],
          ...data.beneficiaryPerformance.map(b => [
            b.name,
            b.email,
            b.program,
            b.progress,
            b.attendanceRate,
            b.status
          ])
        ];

        const beneficiarySheet = utils.aoa_to_sheet(beneficiaryData);
        
        // Auto-size columns
        const beneficiaryColWidths = [
          { wch: 20 }, // Name
          { wch: 25 }, // Email
          { wch: 20 }, // Program
          { wch: 12 }, // Progress
          { wch: 15 }, // Attendance
          { wch: 12 }  // Status
        ];
        beneficiarySheet['!cols'] = beneficiaryColWidths;

        utils.book_append_sheet(workbook, beneficiarySheet, 'Beneficiary Performance');
      }

      // Trainer Performance sheet
      if (data.trainerPerformance) {
        const trainerData = [
          ['Name', 'Specialization', 'Assigned Beneficiaries', 'Sessions Conducted', 'Average Rating', 'Success Rate (%)'],
          ...data.trainerPerformance.map(t => [
            t.name,
            t.specialization,
            t.assignedBeneficiaries,
            t.sessionsConducted,
            t.avgRating,
            t.successRate
          ])
        ];

        const trainerSheet = utils.aoa_to_sheet(trainerData);
        
        // Auto-size columns
        const trainerColWidths = [
          { wch: 20 }, // Name
          { wch: 15 }, // Specialization
          { wch: 18 }, // Assigned Beneficiaries
          { wch: 16 }, // Sessions Conducted
          { wch: 14 }, // Average Rating
          { wch: 15 }  // Success Rate
        ];
        trainerSheet['!cols'] = trainerColWidths;

        utils.book_append_sheet(workbook, trainerSheet, 'Trainer Performance');
      }

      // Program Performance sheet
      if (data.programPerformance) {
        const programData = [
          ['Program Name', 'Beneficiaries', 'Completion Rate (%)', 'Average Satisfaction', 'Status'],
          ...data.programPerformance.map(p => [
            p.name,
            p.beneficiaries,
            p.completionRate,
            p.avgSatisfaction,
            p.status
          ])
        ];

        const programSheet = utils.aoa_to_sheet(programData);
        
        // Auto-size columns
        const programColWidths = [
          { wch: 25 }, // Program Name
          { wch: 15 }, // Beneficiaries
          { wch: 18 }, // Completion Rate
          { wch: 18 }, // Average Satisfaction
          { wch: 12 }  // Status
        ];
        programSheet['!cols'] = programColWidths;

        utils.book_append_sheet(workbook, programSheet, 'Program Performance');
      }

      // Time Series Data sheet
      if (data.timeSeriesData) {
        const timeSeriesData = [
          ['Date', 'Active Users', 'Sessions', 'Completion Rate'],
          ...data.timeSeriesData.map(d => [
            d.date,
            d.activeUsers,
            d.sessions,
            d.completionRate
          ])
        ];

        const timeSeriesSheet = utils.aoa_to_sheet(timeSeriesData);
        utils.book_append_sheet(workbook, timeSeriesSheet, 'Time Series Data');
      }

      // Metrics sheet
      if (data.metrics) {
        const metricsData = [
          ['Metric', 'Value', 'Change', 'Period'],
          ...Object.entries(data.metrics).map(([key, value]) => [
            key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
            typeof value === 'object' ? value.current : value,
            typeof value === 'object' ? value.change : 'N/A',
            typeof value === 'object' ? value.period : 'Current'
          ])
        ];

        const metricsSheet = utils.aoa_to_sheet(metricsData);
        utils.book_append_sheet(workbook, metricsSheet, 'Metrics');
      }

      // Save the Excel file
      const filename = this.generateFilename(config.filename, 'xlsx', config.timestamp);
      writeFile(workbook, filename);

      return { success: true, filename };
    } catch (error) {
      console.error('Error generating Excel:', error);
      throw new Error('Failed to generate Excel export');
    }
  }

  // Export to CSV
  async exportToCSV(data, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    
    try {
      let csvContent = '';

      // Add metadata header if requested
      if (config.includeMetadata) {
        csvContent += `# BDC Analytics Export\n`;
        csvContent += `# Generated on: ${format(new Date(), 'PPP p')}\n`;
        if (data.dateRange) {
          csvContent += `# Date Range: ${data.dateRange.start} to ${data.dateRange.end}\n`;
        }
        csvContent += `\n`;
      }

      // Determine which data to export based on options or available data
      if (options.dataType === 'beneficiaries' && data.beneficiaryPerformance) {
        csvContent += this.arrayToCSV([
          ['Name', 'Email', 'Program', 'Progress (%)', 'Attendance Rate (%)', 'Status'],
          ...data.beneficiaryPerformance.map(b => [
            b.name,
            b.email,
            b.program,
            b.progress,
            b.attendanceRate,
            b.status
          ])
        ]);
      } else if (options.dataType === 'trainers' && data.trainerPerformance) {
        csvContent += this.arrayToCSV([
          ['Name', 'Specialization', 'Assigned Beneficiaries', 'Sessions Conducted', 'Average Rating', 'Success Rate (%)'],
          ...data.trainerPerformance.map(t => [
            t.name,
            t.specialization,
            t.assignedBeneficiaries,
            t.sessionsConducted,
            t.avgRating,
            t.successRate
          ])
        ]);
      } else if (options.dataType === 'programs' && data.programPerformance) {
        csvContent += this.arrayToCSV([
          ['Program Name', 'Beneficiaries', 'Completion Rate (%)', 'Average Satisfaction', 'Status'],
          ...data.programPerformance.map(p => [
            p.name,
            p.beneficiaries,
            p.completionRate,
            p.avgSatisfaction,
            p.status
          ])
        ]);
      } else {
        // Export all data in a combined format
        if (data.summary) {
          csvContent += '# Summary\n';
          csvContent += this.arrayToCSV([
            ['Metric', 'Value'],
            ['Total Beneficiaries', data.summary.totalBeneficiaries],
            ['Active Programs', data.summary.activePrograms],
            ['Completion Rate', `${data.summary.completionRate}%`],
            ['System Uptime', `${data.summary.systemUptime}%`]
          ]);
          csvContent += '\n';
        }

        if (data.beneficiaryPerformance) {
          csvContent += '# Beneficiary Performance\n';
          csvContent += this.arrayToCSV([
            ['Name', 'Email', 'Program', 'Progress (%)', 'Attendance Rate (%)', 'Status'],
            ...data.beneficiaryPerformance.map(b => [
              b.name, b.email, b.program, b.progress, b.attendanceRate, b.status
            ])
          ]);
          csvContent += '\n';
        }
      }

      // Create and download the CSV file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', this.generateFilename(config.filename, 'csv', config.timestamp));
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      return { success: true, filename: this.generateFilename(config.filename, 'csv', config.timestamp) };
    } catch (error) {
      console.error('Error generating CSV:', error);
      throw new Error('Failed to generate CSV export');
    }
  }

  // Helper function to convert array to CSV
  arrayToCSV(data) {
    return data.map(row => 
      row.map(field => {
        // Escape quotes and wrap in quotes if necessary
        if (typeof field === 'string' && (field.includes(',') || field.includes('"') || field.includes('\n'))) {
          return `"${field.replace(/"/g, '""')}"`;
        }
        return field;
      }).join(',')
    ).join('\n') + '\n';
  }

  // Export chart as image
  async exportChartAsImage(chartRef, filename = 'chart', format = 'png') {
    try {
      if (!chartRef || !chartRef.current) {
        throw new Error('Chart reference not available');
      }

      const canvas = chartRef.current.canvas;
      const url = canvas.toDataURL(`image/${format}`);
      
      const link = document.createElement('a');
      link.download = this.generateFilename(filename, format, true);
      link.href = url;
      link.click();

      return { success: true, filename: this.generateFilename(filename, format, true) };
    } catch (error) {
      console.error('Error exporting chart:', error);
      throw new Error('Failed to export chart as image');
    }
  }

  // Batch export multiple formats
  async batchExport(data, formats = ['pdf', 'excel'], options = {}) {
    const results = [];
    
    for (const format of formats) {
      try {
        let result;
        switch (format) {
          case 'pdf':
            result = await this.exportToPDF(data, options);
            break;
          case 'excel':
            result = await this.exportToExcel(data, options);
            break;
          case 'csv':
            result = await this.exportToCSV(data, options);
            break;
          default:
            throw new Error(`Unsupported format: ${format}`);
        }
        results.push({ format, ...result });
      } catch (error) {
        results.push({ format, success: false, error: error.message });
      }
    }

    return results;
  }
}

export default new ExportService();