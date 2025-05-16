import React from 'react';
import { cn } from '@/lib/utils';

/**
 * EmptyState component for showing empty states
 * 
 * @param {object} props - Component props
 * @param {React.ReactNode} props.icon - Icon to display
 * @param {string} props.title - Title text
 * @param {string} props.description - Description text
 * @param {React.ReactNode} props.action - Action button or content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} EmptyState component
 */
const EmptyState = ({ 
  icon,
  title,
  description,
  action,
  className,
  ...props 
}) => {
  return (
    <div 
      className={cn(
        "flex flex-col items-center justify-center py-12 px-4 text-center",
        className
      )}
      {...props}
    >
      {icon && (
        <div className="mb-4 text-muted-foreground">
          {icon}
        </div>
      )}
      {title && (
        <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      )}
      {description && (
        <p className="mb-4 text-sm text-muted-foreground max-w-md">
          {description}
        </p>
      )}
      {action && (
        <div className="mt-4">
          {action}
        </div>
      )}
    </div>
  );
};

export default EmptyState;