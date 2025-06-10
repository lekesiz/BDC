// TODO: i18n - processed
import React from 'react';
import { cn } from '@/lib/utils';
/**
 * Accordion context to manage accordion state
 */import { useTranslation } from "react-i18next";
const AccordionContext = React.createContext(null);
/**
 * Accordion container component that manages the active items
 * 
 * @param {object} props - Component props
 * @param {string|string[]} props.defaultValue - Default active item(s)
 * @param {string|string[]} props.value - Controlled active item(s)
 * @param {function} props.onValueChange - Callback when active item changes
 * @param {boolean} props.collapsible - Whether all items can be collapsed
 * @param {boolean} props.multiple - Whether multiple items can be expanded at once
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Accordion content
 * @returns {JSX.Element} Accordion component
 */
const Accordion = ({
  defaultValue,
  value: controlledValue,
  onValueChange,
  collapsible = false,
  multiple = false,
  className,
  children,
  ...props
}) => {const { t } = useTranslation();
  const getInitialValue = () => {
    if (multiple) {
      return defaultValue || [];
    }
    return defaultValue || null;
  };
  const [value, setValue] = React.useState(getInitialValue);
  const activeValue = controlledValue !== undefined ? controlledValue : value;
  const handleValueChange = React.useCallback((itemValue) => {
    const newValue = calculateNewValue(itemValue);
    if (controlledValue === undefined) {
      setValue(newValue);
    }
    onValueChange?.(newValue);
  }, [activeValue, collapsible, multiple, controlledValue, onValueChange]);
  const calculateNewValue = (itemValue) => {
    if (multiple) {
      // Handle multiple selection
      const currentValues = Array.isArray(activeValue) ? activeValue : [];
      if (currentValues.includes(itemValue)) {
        // If already selected, remove it (if collapsible) or keep it
        return collapsible ?
        currentValues.filter((v) => v !== itemValue) :
        currentValues;
      } else {
        // If not selected, add it
        return [...currentValues, itemValue];
      }
    } else {
      // Handle single selection
      return activeValue === itemValue && collapsible ? null : itemValue;
    }
  };
  const isItemActive = (itemValue) => {
    if (multiple) {
      return Array.isArray(activeValue) && activeValue.includes(itemValue);
    }
    return activeValue === itemValue;
  };
  return (
    <AccordionContext.Provider
      value={{ value: activeValue, onValueChange: handleValueChange, isItemActive }}>

      <div
        className={cn("space-y-1", className)}
        {...props}>

        {children}
      </div>
    </AccordionContext.Provider>);

};
/**
 * Accordion item component that contains a trigger and content
 * 
 * @param {object} props - Component props
 * @param {string} props.value - Unique value for this item
 * @param {boolean} props.disabled - Whether this item is disabled
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Item content (should be AccordionTrigger and AccordionContent)
 * @returns {JSX.Element} AccordionItem component
 */
const AccordionItem = ({
  value,
  disabled = false,
  className,
  children,
  ...props
}) => {const { t } = useTranslation();
  const itemContext = React.useMemo(() => ({ value, disabled }), [value, disabled]);
  const itemContextRef = React.useRef(itemContext);
  itemContextRef.current = itemContext;
  return (
    <div
      data-state={itemContextRef.current.disabled ? "disabled" : "enabled"}
      className={cn(
        "border border-border rounded-md overflow-hidden",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
      {...props}>

      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { itemContext: itemContextRef.current });
        }
        return child;
      })}
    </div>);

};
/**
 * Accordion trigger component that toggles the visibility of content
 * 
 * @param {object} props - Component props
 * @param {object} props.itemContext - Context passed from AccordionItem
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Trigger content
 * @returns {JSX.Element} AccordionTrigger component
 */
const AccordionTrigger = ({
  itemContext,
  className,
  children,
  ...props
}) => {const { t } = useTranslation();
  const { value, disabled } = itemContext || {};
  const { isItemActive, onValueChange } = React.useContext(AccordionContext);
  const isActive = value ? isItemActive(value) : false;
  const handleClick = () => {
    if (!disabled && value) {
      onValueChange(value);
    }
  };
  return (
    <button
      type="button"
      aria-expanded={isActive}
      data-state={isActive ? "open" : "closed"}
      disabled={disabled}
      className={cn(
        "flex w-full justify-between items-center p-4 font-medium text-sm transition-all",
        "hover:bg-muted/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        className
      )}
      onClick={handleClick}
      {...props}>

      {children}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={cn(
          "h-4 w-4 shrink-0 transition-transform duration-200",
          isActive && "rotate-180"
        )}>

        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </button>);

};
/**
 * Accordion content component that is shown when its trigger is active
 * 
 * @param {object} props - Component props
 * @param {object} props.itemContext - Context passed from AccordionItem
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Content to display
 * @returns {JSX.Element|null} AccordionContent component or null if inactive
 */
const AccordionContent = ({
  itemContext,
  className,
  children,
  ...props
}) => {const { t } = useTranslation();
  const { value } = itemContext || {};
  const { isItemActive } = React.useContext(AccordionContext);
  const isActive = value ? isItemActive(value) : false;
  if (!isActive) return null;
  return (
    <div
      data-state={isActive ? "open" : "closed"}
      className={cn(
        "overflow-hidden text-sm transition-all",
        className
      )}
      {...props}>

      <div className="p-4 pt-0">
        {children}
      </div>
    </div>);

};
export { Accordion, AccordionItem, AccordionTrigger, AccordionContent };