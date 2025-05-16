import React from 'react';
import { cn } from '@/lib/utils';

/**
 * A simple DatePicker component that allows selecting a date
 * 
 * @param {object} props - Component props
 * @param {Date} props.value - Selected date
 * @param {function} props.onChange - Callback when date changes
 * @param {Date} props.minDate - Minimum selectable date
 * @param {Date} props.maxDate - Maximum selectable date
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.disabled - Whether the datepicker is disabled
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} DatePicker component
 */
const DatePicker = ({
  value,
  onChange,
  minDate,
  maxDate,
  placeholder = "Select date",
  disabled = false,
  className,
  ...props
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [currentMonth, setCurrentMonth] = React.useState(() => {
    if (value) return new Date(value.getFullYear(), value.getMonth(), 1);
    return new Date(new Date().getFullYear(), new Date().getMonth(), 1);
  });
  
  const containerRef = React.useRef(null);
  
  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleOutsideClick);
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, []);
  
  // Get formatted month name
  const getMonthName = (date) => {
    return date.toLocaleString('default', { month: 'long', year: 'numeric' });
  };
  
  // Get days in month
  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };
  
  // Get day of week of first day of month (0 = Sunday, 6 = Saturday)
  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };
  
  // Check if a date is today
  const isToday = (date) => {
    const today = new Date();
    return date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear();
  };
  
  // Check if a date is selected
  const isSelected = (date) => {
    if (!value) return false;
    return date.getDate() === value.getDate() &&
      date.getMonth() === value.getMonth() &&
      date.getFullYear() === value.getFullYear();
  };
  
  // Check if a date is disabled
  const isDisabled = (date) => {
    if (disabled) return true;
    if (minDate && date < new Date(minDate.setHours(0, 0, 0, 0))) return true;
    if (maxDate && date > new Date(maxDate.setHours(23, 59, 59, 999))) return true;
    return false;
  };
  
  // Navigate to previous month
  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };
  
  // Navigate to next month
  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };
  
  // Handle date selection
  const handleSelectDate = (day) => {
    const selectedDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
    if (!isDisabled(selectedDate)) {
      onChange(selectedDate);
      setIsOpen(false);
    }
  };
  
  // Format date for display
  const formatDate = (date) => {
    if (!date) return '';
    return date.toLocaleDateString('default', { day: 'numeric', month: 'short', year: 'numeric' });
  };
  
  // Generate calendar grid
  const renderCalendarDays = () => {
    const daysInMonth = getDaysInMonth(currentMonth);
    const firstDayOfMonth = getFirstDayOfMonth(currentMonth);
    const days = [];
    
    // Add empty cells for days before first day of month
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="h-8 w-8"></div>);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      const disabled = isDisabled(date);
      
      days.push(
        <button
          key={`day-${day}`}
          type="button"
          onClick={() => handleSelectDate(day)}
          disabled={disabled}
          className={cn(
            "h-8 w-8 rounded-full text-sm flex items-center justify-center",
            isToday(date) && "border border-primary",
            isSelected(date) && "bg-primary text-primary-foreground",
            !isSelected(date) && !disabled && "hover:bg-muted",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          {day}
        </button>
      );
    }
    
    return days;
  };
  
  return (
    <div className={cn("relative w-full", className)} ref={containerRef} {...props}>
      {/* Date display/input */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "text-left"
        )}
        disabled={disabled}
      >
        {value ? formatDate(value) : <span className="text-muted-foreground">{placeholder}</span>}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 ml-auto self-center"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </button>
      
      {/* Calendar dropdown */}
      {isOpen && (
        <div className="absolute left-0 z-10 mt-1 w-full p-2 bg-background rounded-md border border-input shadow-md">
          {/* Calendar header */}
          <div className="flex justify-between items-center mb-2">
            <button
              type="button"
              onClick={prevMonth}
              className="p-1 rounded-full hover:bg-muted"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            
            <div className="font-medium">{getMonthName(currentMonth)}</div>
            
            <button
              type="button"
              onClick={nextMonth}
              className="p-1 rounded-full hover:bg-muted"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
          
          {/* Weekdays header */}
          <div className="grid grid-cols-7 gap-1 text-center text-xs text-muted-foreground mb-1">
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
              <div key={day} className="h-6 flex items-center justify-center">
                {day}
              </div>
            ))}
          </div>
          
          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-1">
            {renderCalendarDays()}
          </div>
          
          {/* Calendar footer */}
          <div className="mt-3 border-t pt-2 flex justify-between">
            <button
              type="button"
              onClick={() => {
                onChange(null);
                setIsOpen(false);
              }}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={() => {
                onChange(new Date());
                setIsOpen(false);
              }}
              className="text-xs text-primary hover:underline"
            >
              Today
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export { DatePicker };