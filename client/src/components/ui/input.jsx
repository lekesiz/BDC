import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Input component for text input fields
 * 
 * @param {object} props - Component props
 * @param {string} props.label - Input label text
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes for the input
 * @param {object} props.labelProps - Props for the label element
 * @param {React.ReactNode} props.leftIcon - Icon to display on the left side
 * @param {React.ReactNode} props.rightIcon - Icon to display on the right side
 * @returns {JSX.Element} Input component
 */
const Input = React.forwardRef(({ 
  className, 
  type = "text", 
  label,
  error,
  labelProps,
  leftIcon,
  rightIcon,
  ...props 
}, ref) => {
  const id = props.id || props.name || React.useId();
  
  return (
    <div className="w-full space-y-2">
      {label && (
        <label 
          htmlFor={id}
          className={cn(
            "block text-sm font-medium text-gray-700",
            error && "text-red-500",
            labelProps?.className
          )}
          {...labelProps}
        >
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {leftIcon}
          </div>
        )}
        
        <input
          id={id}
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
            "file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-muted-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            leftIcon && "pl-10",
            rightIcon && "pr-10",
            error && "border-red-500 focus-visible:ring-red-500",
            className
          )}
          ref={ref}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            {rightIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-red-500 mt-1">{error}</p>
      )}
    </div>
  );
});

Input.displayName = "Input";

export { Input };