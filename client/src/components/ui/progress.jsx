// TODO: i18n - processed
import React from 'react';
import { cn } from '@/lib/utils';
/**
 * Progress component - Shows a progress bar
 * 
 * @param {object} props - Component props
 * @param {number} props.value - Current progress value (0-100)
 * @param {number} props.max - Maximum value (default: 100)
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Progress component
 */import { useTranslation } from "react-i18next";
export const Progress = React.forwardRef(({
  value = 0,
  max = 100,
  className,
  ...props
}, ref) => {
  const percentage = Math.min(Math.max(0, value / max * 100), 100);
  return (
    <div
      ref={ref}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      className={cn(
        "relative w-full overflow-hidden rounded-full bg-secondary h-2",
        className
      )}
      {...props}>

      <div
        className="h-full w-full flex-1 bg-primary transition-all"
        style={{ width: `${percentage}%` }} />

    </div>);

});
Progress.displayName = "Progress";