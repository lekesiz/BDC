// TODO: i18n - processed
import React from 'react';
import { Calendar } from 'lucide-react';
import { cn } from '@/lib/utils';
/**
 * DatePicker component
 * 
 * @param {object} props - Component props
 * @param {Date} props.value - Selected date
 * @param {function} props.onChange - Callback when date changes
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} DatePicker component
 */import { useTranslation } from "react-i18next";
export const DatePicker = React.forwardRef(({
  value,
  onChange,
  placeholder = "Select date",
  className,
  ...props
}, ref) => {
  return (
    <div className="relative">
      <div className="relative">
        <input
          ref={ref}
          type="date"
          value={value ? value.toISOString().split('T')[0] : ''}
          onChange={(e) => onChange && onChange(new Date(e.target.value))}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
            "file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-muted-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            className
          )}
          placeholder={placeholder}
          {...props} />

        <Calendar className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 opacity-50 pointer-events-none" />
      </div>
    </div>);

});
DatePicker.displayName = "DatePicker";