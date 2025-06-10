// TODO: i18n - processed
import React from 'react';
import { cn } from '@/lib/utils';
/**
 * Textarea component for multiline text input
 * 
 * @param {object} props - Component props
 * @param {string} props.label - Textarea label text
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes for the textarea
 * @param {object} props.labelProps - Props for the label element
 * @param {number} props.rows - Number of visible text lines
 * @returns {JSX.Element} Textarea component
 */import { useTranslation } from "react-i18next";
const Textarea = React.forwardRef(({
  className,
  label,
  error,
  labelProps,
  rows = 3,
  ...props
}, ref) => {
  const id = props.id || props.name || React.useId();
  return (
    <div className="w-full space-y-2">
      {label &&
      <label
        htmlFor={id}
        className={cn(
          "block text-sm font-medium text-gray-700",
          error && "text-red-500",
          labelProps?.className
        )}
        {...labelProps}>

          {label}
        </label>
      }
      <textarea
        id={id}
        rows={rows}
        className={cn(
          "flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
          "placeholder:text-muted-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50",
          error && "border-red-500 focus-visible:ring-red-500",
          className
        )}
        ref={ref}
        {...props} />

      {error &&
      <p className="text-sm text-red-500 mt-1">{error}</p>
      }
    </div>);

});
Textarea.displayName = "Textarea";
export { Textarea };