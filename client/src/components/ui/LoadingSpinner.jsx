// Enhanced LoadingSpinner component - no external dependencies

/**
 * Enhanced loading spinner with multiple sizes and text support
 */
const LoadingSpinner = ({ 
  size = 'md',
  text = 'Loading...',
  message,
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };
  
  const displayText = text || message || 'Loading...';
  
  return (
    <div className={`min-h-[200px] flex items-center justify-center ${className}`} {...props}>
      <div className="text-center">
        <div className={`animate-spin rounded-full border-b-2 border-primary mx-auto ${sizeClasses[size]}`}></div>
        {displayText && (
          <p className="mt-3 text-sm text-muted-foreground">{displayText}</p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;