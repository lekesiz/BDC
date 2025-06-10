// TODO: i18n - processed
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
 */import { useTranslation } from "react-i18next";
const Input = React.forwardRef(({
  className,
  type = "text",
  label,
  error,
  labelProps,
  leftIcon,
  rightIcon,
  required = false,
  helpText,
  size = 'default',
  fullWidth = true,
  ...props
}, ref) => {
  const id = props.id || props.name || React.useId();
  const errorId = error ? `${id}-error` : undefined;
  const helpTextId = helpText ? `${id}-help` : undefined;
  return (
    <div className="w-full space-y-2">
      {label &&
      <label
        htmlFor={id}
        className={cn(
          "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1",
          error && "text-red-500 dark:text-red-400",
          labelProps?.className
        )}
        {...labelProps}>

          {label}
          {required && <span className="text-red-500 dark:text-red-400 ml-1" aria-label="required">*</span>}
        </label>
      }
      <div className="relative">
        {leftIcon &&
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none" aria-hidden="true">
            {leftIcon}
          </div>
        }
        <input
          id={id}
          type={type}
          className={cn(
            "flex rounded-md border bg-white dark:bg-gray-800 ring-offset-background",
            "file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-gray-500 dark:placeholder:text-gray-400",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "transition-colors",
            // Size variants
            size === 'small' && "h-9 px-2.5 py-1.5 text-sm",
            size === 'default' && "h-10 sm:h-11 px-3 py-2 text-base sm:text-sm",
            size === 'large' && "h-12 px-4 py-3 text-base",
            // Touch-friendly minimum height
            "min-h-[44px] sm:min-h-0",
            // Icon padding
            leftIcon && (size === 'small' ? "pl-8" : "pl-10"),
            rightIcon && (size === 'small' ? "pr-8" : "pr-10"),
            // Width
            fullWidth && "w-full",
            // Border and error states
            error ?
            "border-red-500 dark:border-red-400 focus-visible:ring-red-500 dark:focus-visible:ring-red-400" :
            "border-gray-300 dark:border-gray-600",
            className
          )}
          ref={ref}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={[errorId, helpTextId].filter(Boolean).join(' ') || undefined}
          aria-required={required}
          {...props} />

        {rightIcon &&
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center" aria-hidden="true">
            {rightIcon}
          </div>
        }
      </div>
      {helpText && !error &&
      <p id={helpTextId} className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1">{helpText}</p>
      }
      {error &&
      <p id={errorId} className="text-xs sm:text-sm text-red-500 dark:text-red-400 mt-1" role="alert">{error}</p>
      }
    </div>);

});
Input.displayName = "Input";
export { Input };