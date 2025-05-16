import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Tabs context to manage tab state
 */
const TabsContext = React.createContext(null);

/**
 * Tabs container component that manages the active tab state
 * 
 * @param {object} props - Component props
 * @param {string} props.defaultValue - Default active tab value
 * @param {function} props.onValueChange - Callback when tab changes
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Tabs content
 * @returns {JSX.Element} Tabs component
 */
const Tabs = ({ 
  defaultValue, 
  value: controlledValue,
  onValueChange,
  className, 
  children, 
  ...props 
}) => {
  const [value, setValue] = React.useState(defaultValue);
  const activeValue = controlledValue !== undefined ? controlledValue : value;
  
  const handleValueChange = React.useCallback((newValue) => {
    if (controlledValue === undefined) {
      setValue(newValue);
    }
    onValueChange?.(newValue);
  }, [controlledValue, onValueChange]);

  return (
    <TabsContext.Provider value={{ value: activeValue, onValueChange: handleValueChange }}>
      <div className={cn("w-full", className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

/**
 * Tab list component that contains the tab triggers
 * 
 * @param {object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Tab triggers
 * @returns {JSX.Element} TabsList component
 */
const TabsList = ({ className, children, ...props }) => {
  return (
    <div 
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground",
        className
      )} 
      role="tablist"
      {...props}
    >
      {children}
    </div>
  );
};

/**
 * Tab trigger button that activates its associated content
 * 
 * @param {object} props - Component props
 * @param {string} props.value - Value associated with this tab
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.disabled - Whether the tab is disabled
 * @param {React.ReactNode} props.children - Tab content
 * @returns {JSX.Element} TabTrigger component
 */
const TabTrigger = ({ value, className, disabled, children, ...props }) => {
  const { value: activeValue, onValueChange } = React.useContext(TabsContext);
  const isActive = activeValue === value;
  
  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-controls={`panel-${value}`}
      data-state={isActive ? "active" : "inactive"}
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        isActive ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground",
        className
      )}
      onClick={() => onValueChange(value)}
      {...props}
    >
      {children}
    </button>
  );
};

/**
 * Tab content panel that displays when its associated trigger is active
 * 
 * @param {object} props - Component props
 * @param {string} props.value - Value associated with this panel
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Panel content
 * @returns {JSX.Element|null} TabContent component or null if inactive
 */
const TabContent = ({ value, className, children, ...props }) => {
  const { value: activeValue } = React.useContext(TabsContext);
  const isActive = activeValue === value;
  
  if (!isActive) return null;
  
  return (
    <div
      role="tabpanel"
      id={`panel-${value}`}
      aria-labelledby={`trigger-${value}`}
      data-state={isActive ? "active" : "inactive"}
      className={cn(
        "mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export { Tabs, TabsList, TabTrigger, TabContent };