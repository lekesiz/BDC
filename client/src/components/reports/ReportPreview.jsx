import React from 'react';
import { format } from 'date-fns';
import { FileText, Calendar, User, Building } from 'lucide-react';
import { ScrollArea } from '../ui/scroll-area';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';

const ReportPreview = ({ reportName, reportDescription, sections, darkMode }) => {
  // Simulate report metadata
  const metadata = {
    generatedBy: 'Admin User',
    organization: 'BDC Organization',
    generatedAt: new Date(),
    totalPages: Math.ceil(sections.length * 1.5),
  };

  const renderWidgetPreview = (widget) => {
    switch (widget.type) {
      case 'chart':
        return (
          <div className="bg-gray-100 dark:bg-gray-700 rounded p-4 h-32 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {widget.config.chartType || 'Chart'} - {widget.config.title || 'Untitled'}
            </p>
          </div>
        );
      
      case 'kpi':
        return (
          <div className="bg-gray-100 dark:bg-gray-700 rounded p-4">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {widget.config.title || 'KPI'}
            </p>
            <p className="text-2xl font-bold mt-1">
              {widget.config.value || 0}{widget.config.unit || ''}
            </p>
          </div>
        );
      
      case 'table':
        return (
          <div className="bg-gray-100 dark:bg-gray-700 rounded p-4 h-32 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Table - {widget.config.title || 'Data Table'}
            </p>
          </div>
        );
      
      case 'text':
        return (
          <div className="bg-gray-100 dark:bg-gray-700 rounded p-4">
            <div 
              className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3"
              dangerouslySetInnerHTML={{ 
                __html: widget.config.content || '<p>Text content...</p>' 
              }}
            />
          </div>
        );
      
      case 'image':
        return (
          <div className="bg-gray-100 dark:bg-gray-700 rounded p-4 h-32 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Image - {widget.config.alt || 'Image placeholder'}
            </p>
          </div>
        );
      
      default:
        return (
          <div className="bg-gray-100 dark:bg-gray-700 rounded p-4 h-20 flex items-center justify-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {widget.type} widget
            </p>
          </div>
        );
    }
  };

  const getLayoutClass = (layout) => {
    switch (layout) {
      case 'two-column':
        return 'grid grid-cols-2 gap-2';
      case 'grid':
        return 'grid grid-cols-3 gap-2';
      default:
        return 'space-y-2';
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="text-center space-y-2">
        <FileText className="w-8 h-8 mx-auto text-gray-400" />
        <h2 className="text-lg font-bold">{reportName || 'Untitled Report'}</h2>
        {reportDescription && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {reportDescription}
          </p>
        )}
      </div>

      <Separator />

      {/* Metadata */}
      <div className="space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
            <User className="w-3 h-3" />
            <span>{metadata.generatedBy}</span>
          </div>
          <Badge variant="outline" className="text-xs">
            Draft
          </Badge>
        </div>
        <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
          <Building className="w-3 h-3" />
          <span>{metadata.organization}</span>
        </div>
        <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
          <Calendar className="w-3 h-3" />
          <span>{format(metadata.generatedAt, 'PPP')}</span>
        </div>
      </div>

      <Separator />

      {/* Sections Preview */}
      <ScrollArea className="h-[calc(100vh-400px)]">
        <div className="space-y-4">
          {sections.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No sections added yet. Start building your report by adding sections and widgets.
              </p>
            </div>
          ) : (
            sections.map((section, sectionIndex) => (
              <div 
                key={section.id} 
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
              >
                <h3 className="text-sm font-semibold mb-2">
                  {sectionIndex + 1}. {section.title}
                </h3>
                {section.widgets.length === 0 ? (
                  <div className="text-xs text-gray-500 dark:text-gray-400 text-center py-4">
                    Empty section
                  </div>
                ) : (
                  <div className={getLayoutClass(section.layout)}>
                    {section.widgets.map((widget) => (
                      <div key={widget.id}>
                        {renderWidgetPreview(widget)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      <Separator />

      {/* Footer */}
      <div className="text-center text-xs text-gray-500 dark:text-gray-400">
        <p>Preview • {metadata.totalPages} estimated pages</p>
      </div>
    </div>
  );
};

export default ReportPreview;