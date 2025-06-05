import React from "react";
import { 
  CheckCircle, 
  AlertCircle, 
  Info, 
  AlertTriangle, 
  X 
} from "lucide-react";
import { cn } from "@/lib/utils";
/**
 * Toast container for displaying toast notifications
 */
const ToastContainer = ({ className, ...props }) => {
  return (
    <>
      {/* Screen reader announcements */}
      <div 
        className="sr-only" 
        role="region" 
        aria-live="polite" 
        aria-atomic="true"
        aria-label="Notifications"
      />
      {/* Visual toasts */}
      <div
        className={cn(
          "fixed top-0 right-0 z-50 flex flex-col p-4 space-y-4 sm:p-6",
          className
        )}
        aria-label="Toast notifications"
        {...props}
      />
    </>
  );
};
/**
 * Types of toast notifications with corresponding icons and styles
 */
const TOAST_TYPES = {
  success: {
    icon: <CheckCircle className="w-5 h-5" aria-hidden="true" />,
    className: "bg-green-50 border-green-100 text-green-800",
    ariaLive: "polite",
  },
  error: {
    icon: <AlertCircle className="w-5 h-5" aria-hidden="true" />,
    className: "bg-red-50 border-red-100 text-red-800",
    ariaLive: "assertive",
  },
  info: {
    icon: <Info className="w-5 h-5" aria-hidden="true" />,
    className: "bg-blue-50 border-blue-100 text-blue-800",
    ariaLive: "polite",
  },
  warning: {
    icon: <AlertTriangle className="w-5 h-5" aria-hidden="true" />,
    className: "bg-yellow-50 border-yellow-100 text-yellow-800",
    ariaLive: "polite",
  },
};
/**
 * Toast component for displaying notifications
 * 
 * @param {object} props - Component props
 * @param {string} props.id - Unique identifier for the toast
 * @param {string} props.type - Type of toast: success, error, info, warning
 * @param {string} props.title - Toast title
 * @param {string} props.message - Toast message
 * @param {Function} props.onClose - Function called when toast is closed
 * @param {number} props.duration - Duration in milliseconds
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Toast component
 */
const Toast = ({
  id,
  type = "info",
  title,
  message,
  onClose,
  duration = 5000,
  className,
  ...props
}) => {
  const { icon, className: typeClassName, ariaLive } = TOAST_TYPES[type] || TOAST_TYPES.info;
  const toastRef = React.useRef(null);
  // Auto-close toast after duration and announce to screen readers
  React.useEffect(() => {
    // Announce to screen readers
    const announcement = document.querySelector('[role="region"][aria-live]');
    if (announcement) {
      const announcementText = `${type} notification: ${title || ''} ${message || ''}`;
      announcement.setAttribute('aria-live', ariaLive);
      announcement.textContent = announcementText;
      // Clear announcement after a delay
      setTimeout(() => {
        announcement.textContent = '';
      }, 1000);
    }
    if (duration) {
      const timer = setTimeout(() => {
        onClose && onClose(id);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, id, onClose, type, title, message, ariaLive]);
  return (
    <div
      ref={toastRef}
      role="alert"
      aria-live={ariaLive}
      aria-atomic="true"
      className={cn(
        "flex w-full max-w-sm overflow-hidden rounded-lg shadow-lg border",
        "transform transition-all duration-500 ease-in-out",
        "animate-enter",
        typeClassName,
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-center w-12">
        {icon}
      </div>
      <div className="px-4 py-3 w-full">
        {title && (
          <div className="font-semibold">{title}</div>
        )}
        {message && (
          <div className="text-sm">{message}</div>
        )}
      </div>
      <div className="flex items-center">
        <button
          onClick={() => onClose && onClose(id)}
          className={cn(
            "p-1 rounded-full",
            "hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-primary",
            "transition-colors"
          )}
          aria-label="Close notification"
        >
          <X className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
};
/**
 * Create a toast context for managing toast notifications
 */
const ToastContext = React.createContext({
  toasts: [],
  addToast: () => {},
  removeToast: () => {},
});
/**
 * Provider component for managing toast notifications
 */
const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = React.useState([]);
  const addToast = React.useCallback((toast) => {
    const id = toast.id || Date.now().toString();
    setToasts((prevToasts) => [...prevToasts, { ...toast, id }]);
    return id;
  }, []);
  const removeToast = React.useCallback((id) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  }, []);
  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            id={toast.id}
            type={toast.type}
            title={toast.title}
            message={toast.message}
            duration={toast.duration}
            onClose={removeToast}
          />
        ))}
      </ToastContainer>
    </ToastContext.Provider>
  );
};
/**
 * Hook for using toast notifications
 */
const useToast = () => {
  try {
    const context = React.useContext(ToastContext);
    if (!context || context === undefined) {
      console.warn("useToast used outside ToastProvider, returning mock functions");
      return {
        addToast: () => {},
        removeToast: () => {},
        toast: () => {},
        toasts: []
      };
    }
    // Provide a toast method for simplified API
    const toast = (options) => {
      return context.addToast(options);
    };
    return {
      ...context,
      toast
    };
  } catch (error) {
    console.warn("Error in useToast:", error);
    return {
      addToast: () => {},
      removeToast: () => {},
      toast: () => {},
      toasts: []
    };
  }
};
export { 
  ToastProvider, 
  useToast,
  Toast, 
  ToastContainer 
};