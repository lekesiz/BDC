import React from 'react';
import { cn } from '@/lib/utils';
import { useBreakpoint } from '@/hooks/useMediaQuery';

/**
 * Table component
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Table content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Table component
 */
export const Table = ({ 
  children, 
  className = '', 
  caption,
  summary,
  'aria-label': ariaLabel,
  responsive = true,
  ...props 
}) => {
  return (
    <div className={cn(
      responsive && "overflow-x-auto -mx-3 sm:-mx-4 lg:mx-0",
      "rounded-lg"
    )} role="region" aria-label={ariaLabel || "Data table"}>
      <div className={responsive && "inline-block min-w-full align-middle"}>
        <table
          className={cn(
            'min-w-full divide-y divide-gray-200 dark:divide-gray-700',
            responsive && "sm:rounded-lg",
            className
          )}
          role="table"
          aria-label={ariaLabel}
          {...props}
        >
          {caption && (
            <caption className="sr-only">{caption}</caption>
          )}
          {summary && (
            <caption className="text-sm text-gray-500 dark:text-gray-400 text-left py-2 px-3 sm:px-6">{summary}</caption>
          )}
          {children}
        </table>
      </div>
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
    <thead className={cn('bg-gray-50 dark:bg-gray-800', className)} {...props}>
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
    <tbody className={cn('bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700', className)} {...props}>
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
        isHeader ? 'bg-gray-50 dark:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800',
        'transition-colors',
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
  scope,
  colSpan,
  rowSpan,
  'aria-sort': ariaSort,
  mobileLabel,
  hideOnMobile = false,
  ...props 
}) => {
  const Component = isHeader ? 'th' : 'td';
  const { isMobile } = useBreakpoint();
  
  // Determine scope for header cells
  const cellScope = scope || (isHeader ? 'col' : undefined);
  
  if (hideOnMobile && isMobile) {
    return null;
  }
  
  return (
    <Component
      className={cn(
        isHeader
          ? 'px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider'
          : 'px-3 sm:px-6 py-3 sm:py-4 text-sm text-gray-900 dark:text-gray-100',
        !isHeader && 'relative',
        className
      )}
      scope={cellScope}
      colSpan={colSpan}
      rowSpan={rowSpan}
      aria-sort={ariaSort}
      {...props}
    >
      {/* Mobile label for better context */}
      {mobileLabel && !isHeader && (
        <span className="font-medium text-gray-700 dark:text-gray-300 sm:hidden block mb-1">
          {mobileLabel}:
        </span>
      )}
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
  const { isMobile } = useBreakpoint();
  
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
      className={cn(
        'flex items-center justify-between px-3 sm:px-6 py-3 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700',
        className
      )}
    >
      <div className="flex justify-between flex-1 sm:hidden">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="relative inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Go to previous page"
        >
          Previous
        </button>
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {currentPage} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="relative inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Go to next page"
        >
          Next
        </button>
      </div>
      
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-gray-700 dark:text-gray-300">
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
              className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              aria-label="Go to previous page"
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
                    'relative inline-flex items-center px-3 sm:px-4 py-2 border text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors',
                    currentPage === page
                      ? 'z-10 bg-primary border-primary text-white'
                      : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                  )}
                  aria-label={`Go to page ${page}`}
                  aria-current={currentPage === page ? 'page' : undefined}
                >
                  {page}
                </button>
              )
            ))}
            
            {/* Next button */}
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              aria-label="Go to next page"
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