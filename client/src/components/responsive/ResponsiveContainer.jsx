import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Responsive container component with breakpoint-based padding and max-width
 */
export const ResponsiveContainer = ({ 
  children, 
  className,
  noPadding = false,
  fluid = false
}) => {
  return (
    <div className={cn(
      "w-full",
      !fluid && "mx-auto max-w-7xl",
      !noPadding && "px-4 sm:px-6 lg:px-8",
      className
    )}>
      {children}
    </div>
  );
};

/**
 * Responsive grid component with automatic column adjustment
 */
export const ResponsiveGrid = ({ 
  children, 
  cols = {
    default: 1,
    sm: 2,
    md: 3,
    lg: 4
  },
  gap = 4,
  className 
}) => {
  const getGridCols = () => {
    const classes = ['grid'];
    
    if (cols.default) classes.push(`grid-cols-${cols.default}`);
    if (cols.sm) classes.push(`sm:grid-cols-${cols.sm}`);
    if (cols.md) classes.push(`md:grid-cols-${cols.md}`);
    if (cols.lg) classes.push(`lg:grid-cols-${cols.lg}`);
    if (cols.xl) classes.push(`xl:grid-cols-${cols.xl}`);
    
    classes.push(`gap-${gap}`);
    
    return classes.join(' ');
  };
  
  return (
    <div className={cn(getGridCols(), className)}>
      {children}
    </div>
  );
};

/**
 * Responsive stack component for vertical layouts
 */
export const ResponsiveStack = ({ 
  children, 
  spacing = 4,
  direction = {
    default: 'vertical',
    sm: 'vertical',
    md: 'horizontal'
  },
  className 
}) => {
  const getStackClasses = () => {
    const classes = ['flex'];
    
    // Default direction
    if (direction.default === 'horizontal') {
      classes.push('flex-row', `space-x-${spacing}`);
    } else {
      classes.push('flex-col', `space-y-${spacing}`);
    }
    
    // Responsive directions
    if (direction.sm === 'horizontal') {
      classes.push('sm:flex-row', `sm:space-x-${spacing}`, 'sm:space-y-0');
    } else if (direction.sm === 'vertical') {
      classes.push('sm:flex-col', `sm:space-y-${spacing}`, 'sm:space-x-0');
    }
    
    if (direction.md === 'horizontal') {
      classes.push('md:flex-row', `md:space-x-${spacing}`, 'md:space-y-0');
    } else if (direction.md === 'vertical') {
      classes.push('md:flex-col', `md:space-y-${spacing}`, 'md:space-x-0');
    }
    
    return classes.join(' ');
  };
  
  return (
    <div className={cn(getStackClasses(), className)}>
      {children}
    </div>
  );
};

/**
 * Responsive card component with adaptive padding
 */
export const ResponsiveCard = ({ 
  children, 
  noPadding = false,
  className,
  ...props 
}) => {
  return (
    <div 
      className={cn(
        "bg-white rounded-lg shadow-sm border border-gray-200",
        !noPadding && "p-4 sm:p-6",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

/**
 * Hide/show elements based on breakpoints
 */
export const HideOn = ({ breakpoint, children }) => {
  const hideClasses = {
    sm: 'sm:hidden',
    md: 'md:hidden',
    lg: 'lg:hidden',
    xl: 'xl:hidden'
  };
  
  return (
    <div className={hideClasses[breakpoint]}>
      {children}
    </div>
  );
};

export const ShowOn = ({ breakpoint, children }) => {
  const showClasses = {
    sm: 'hidden sm:block',
    md: 'hidden md:block',
    lg: 'hidden lg:block',
    xl: 'hidden xl:block'
  };
  
  return (
    <div className={showClasses[breakpoint]}>
      {children}
    </div>
  );
};

/**
 * Responsive table wrapper for horizontal scrolling
 */
export const ResponsiveTable = ({ children, className }) => {
  return (
    <div className={cn("w-full overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0", className)}>
      <div className="inline-block min-w-full align-middle">
        {children}
      </div>
    </div>
  );
};

/**
 * Responsive text component with size adjustments
 */
export const ResponsiveText = ({ 
  as: Component = 'p',
  size = {
    default: 'base',
    sm: 'lg',
    md: 'xl'
  },
  className,
  children,
  ...props
}) => {
  const sizeClasses = {
    xs: 'text-xs',
    sm: 'text-sm',
    base: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
    '2xl': 'text-2xl',
    '3xl': 'text-3xl',
    '4xl': 'text-4xl'
  };
  
  const getTextClasses = () => {
    const classes = [];
    
    if (size.default) classes.push(sizeClasses[size.default]);
    if (size.sm) classes.push(`sm:${sizeClasses[size.sm]}`);
    if (size.md) classes.push(`md:${sizeClasses[size.md]}`);
    if (size.lg) classes.push(`lg:${sizeClasses[size.lg]}`);
    
    return classes.join(' ');
  };
  
  return (
    <Component className={cn(getTextClasses(), className)} {...props}>
      {children}
    </Component>
  );
};