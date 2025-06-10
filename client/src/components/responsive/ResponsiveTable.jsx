import React from 'react';
import { cn } from '@/lib/utils';
import { ChevronRight, MoreVertical } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

/**
 * Responsive table that switches between table and card view on mobile
 */
export const ResponsiveTable = ({ 
  columns, 
  data, 
  onRowClick,
  actions,
  className,
  mobileBreakpoint = 'md' // When to switch to mobile view
}) => {
  // Mobile card view
  const MobileCard = ({ row, index }) => {
    return (
      <div 
        className={cn(
          "bg-white p-4 rounded-lg border mb-3 cursor-pointer hover:shadow-md transition-shadow",
          onRowClick && "active:scale-[0.98]"
        )}
        onClick={() => onRowClick?.(row)}
      >
        <div className="space-y-2">
          {columns.map((column) => {
            const value = column.accessor ? row[column.accessor] : null;
            const cellContent = column.cell ? column.cell({ row, value }) : value;
            
            // Skip if column is marked as hidden on mobile
            if (column.hideOnMobile) return null;
            
            return (
              <div key={column.key || column.accessor} className="flex justify-between items-start">
                <span className="text-sm text-gray-500">{column.header}:</span>
                <span className="text-sm font-medium text-right ml-2">
                  {cellContent}
                </span>
              </div>
            );
          })}
        </div>
        
        {/* Actions */}
        {actions && (
          <div className="mt-3 pt-3 border-t flex justify-end">
            {actions.length === 1 ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  actions[0].onClick(row);
                }}
                className="text-sm text-primary hover:underline"
              >
                {actions[0].label}
              </button>
            ) : (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button 
                    className="p-1 hover:bg-gray-100 rounded"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {actions.map((action, idx) => (
                    <DropdownMenuItem
                      key={idx}
                      onClick={() => action.onClick(row)}
                    >
                      {action.icon && <action.icon className="h-4 w-4 mr-2" />}
                      {action.label}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        )}
      </div>
    );
  };

  // Desktop table view
  const DesktopTable = () => {
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key || column.accessor}
                  className={cn(
                    "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                    column.className
                  )}
                >
                  {column.header}
                </th>
              ))}
              {actions && (
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className={cn(
                  "hover:bg-gray-50",
                  onRowClick && "cursor-pointer"
                )}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => {
                  const value = column.accessor ? row[column.accessor] : null;
                  const cellContent = column.cell ? column.cell({ row, value }) : value;
                  
                  return (
                    <td
                      key={column.key || column.accessor}
                      className={cn(
                        "px-6 py-4 whitespace-nowrap text-sm",
                        column.className
                      )}
                    >
                      {cellContent}
                    </td>
                  );
                })}
                {actions && (
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {actions.length === 1 ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          actions[0].onClick(row);
                        }}
                        className="text-primary hover:text-primary/80"
                      >
                        {actions[0].label}
                      </button>
                    ) : (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button 
                            className="p-1 hover:bg-gray-100 rounded"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreVertical className="h-4 w-4" />
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {actions.map((action, idx) => (
                            <DropdownMenuItem
                              key={idx}
                              onClick={() => action.onClick(row)}
                            >
                              {action.icon && <action.icon className="h-4 w-4 mr-2" />}
                              {action.label}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className={className}>
      {/* Mobile view */}
      <div className={`${mobileBreakpoint}:hidden`}>
        {data.map((row, index) => (
          <MobileCard key={index} row={row} index={index} />
        ))}
      </div>
      
      {/* Desktop view */}
      <div className={`hidden ${mobileBreakpoint}:block`}>
        <DesktopTable />
      </div>
    </div>
  );
};

/**
 * Responsive data list with horizontal scroll on mobile
 */
export const ResponsiveDataList = ({ 
  items, 
  renderItem,
  className,
  emptyMessage = "No items found" 
}) => {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={cn("space-y-4 md:space-y-0 md:grid md:grid-cols-2 lg:grid-cols-3 md:gap-4", className)}>
      {items.map((item, index) => (
        <div key={index}>
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  );
};

/**
 * Responsive key-value display
 */
export const ResponsiveDetails = ({ data, className }) => {
  return (
    <dl className={cn("space-y-4 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-4", className)}>
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="sm:col-span-1">
          <dt className="text-sm font-medium text-gray-500">{key}</dt>
          <dd className="mt-1 text-sm text-gray-900">{value || '-'}</dd>
        </div>
      ))}
    </dl>
  );
};