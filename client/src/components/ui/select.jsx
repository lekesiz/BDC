// TODO: i18n - processed
import React from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
/**
 * Select component - A custom dropdown select element
 * 
 * @param {object} props - Component props
 * @param {array} props.options - Array of options {value, label}
 * @param {string} props.value - Currently selected value
 * @param {function} props.onValueChange - Callback when value changes
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Select component
 */import { useTranslation } from "react-i18next";
export const Select = React.forwardRef(({
  options = [],
  value,
  onValueChange,
  placeholder = 'Select an option',
  className,
  ...props
}, ref) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const selectedOption = options.find((opt) => opt.value === value);
  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
          "placeholder:text-muted-foreground",
          "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        {...props}>

        <span className={!selectedOption ? 'text-muted-foreground' : ''}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown className="h-4 w-4 opacity-50" />
      </button>
      {isOpen &&
      <div className="absolute z-50 mt-1 w-full rounded-md border bg-background shadow-lg">
          {options.map((option) =>
        <button
          key={option.value}
          type="button"
          onClick={() => {
            onValueChange(option.value);
            setIsOpen(false);
          }}
          className={cn(
            "relative flex w-full cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none",
            "hover:bg-accent hover:text-accent-foreground",
            value === option.value && "bg-accent text-accent-foreground"
          )}>

              {option.label}
            </button>
        )}
        </div>
      }
    </div>);

});
Select.displayName = "Select";
export default Select;