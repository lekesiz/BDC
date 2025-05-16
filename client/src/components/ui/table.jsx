import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Table component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Table content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table component
 */
export const Table = ({ children, className = '', ...props }) => {
  return (
    <div className="overflow-x-auto">
      <table
        className={cn('min-w-full divide-y divide-gray-200', className)}
        {...props}
      >
        {children}
      </table>
    </div>
  );
};

/**
 * Table Header component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Table header content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table header component
 */
export const TableHeader = ({ children, className = '', ...props }) => {
  return (
    <thead className={cn('bg-gray-50', className)} {...props}>
      {children}
    </thead>
  );
};

/**
 * Table Body component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Table body content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table body component
 */
export const TableBody = ({ children, className = '', ...props }) => {
  return (
    <tbody className={cn('bg-white divide-y divide-gray-200', className)} {...props}>
      {children}
    </tbody>
  );
};

/**
 * Table Row component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Table row content
 * @param {boolean} props.isHeader - Whether this is a header row
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table row component
 */
export const TableRow = ({ 
  children, 
  isHeader = false,
  className = '', 
  ...props 
}) => {
  return (
    <tr 
      className={cn(
        isHeader ? 'bg-gray-50' : 'hover:bg-gray-50',
        className
      )} 
      {...props}
    >
      {children}
    </tr>
  );
};

/**
 * Table Cell component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Table cell content
 * @param {boolean} props.isHeader - Whether this is a header cell
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table cell component
 */
export const TableCell = ({ 
  children, 
  isHeader = false,
  className = '', 
  ...props 
}) => {
  const Component = isHeader ? 'th' : 'td';
  
  return (
    <Component
      className={cn(
        isHeader
          ? 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
          : 'px-6 py-4 whitespace-nowrap text-sm text-gray-500',
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
};

/**
 * Table Pagination component
 * 
 * @param {object} props - Component props
 * @param {number} props.totalItems - Total number of items
 * @param {number} props.itemsPerPage - Number of items per page
 * @param {number} props.currentPage - Current page number
 * @param {function} props.onPageChange - Page change handler
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table pagination component
 */
export const TablePagination = ({
  totalItems,
  itemsPerPage,
  currentPage,
  onPageChange,
  className = '',
  totalPages: propTotalPages,
  pageSize,
  pageSizeOptions,
  onPageSizeChange
}) => {
  const totalPages = propTotalPages || Math.ceil(totalItems / itemsPerPage) || 0;
  
  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5; // Adjust as needed
    
    // Always show first page
    pages.push(1);
    
    // Calculate range around current page
    let startPage = Math.max(2, currentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(totalPages - 1, startPage + maxVisiblePages - 3);
    
    // Add ellipsis after first page if needed
    if (startPage > 2) {
      pages.push('...');
    }
    
    // Add pages around current page
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    // Add ellipsis before last page if needed
    if (endPage < totalPages - 1) {
      pages.push('...');
    }
    
    // Always show last page if there's more than one page
    if (totalPages > 1) {
      pages.push(totalPages);
    }
    
    return pages;
  };
  
  return (
    <div
      className={cn('flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6', className)}
    >
      <div className="flex justify-between flex-1 sm:hidden">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="relative inline-flex items-center px-4 py-2 ml-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
      
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-gray-700">
            Showing{' '}
            <span className="font-medium">
              {Math.min((currentPage - 1) * (itemsPerPage || pageSize || 10) + 1, totalItems || 0)}
            </span>{' '}
            to{' '}
            <span className="font-medium">
              {Math.min(currentPage * (itemsPerPage || pageSize || 10), totalItems || 0)}
            </span>{' '}
            of <span className="font-medium">{totalItems || 0}</span> results
          </p>
        </div>
        
        <div>
          <nav className="inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            {/* Previous button */}
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Previous</span>
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </button>
            
            {/* Page numbers */}
            {getPageNumbers().map((page, index) => (
              page === '...' ? (
                <span key={`ellipsis-${index}`} className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                  ...
                </span>
              ) : (
                <button
                  key={`page-${page}`}
                  onClick={() => onPageChange(page)}
                  className={cn(
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    currentPage === page
                      ? 'z-10 bg-primary border-primary text-white'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  )}
                >
                  {page}
                </button>
              )
            ))}
            
            {/* Next button */}
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="sr-only">Next</span>
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
};