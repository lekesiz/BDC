// TODO: i18n - processed
import { useContext, createContext, useState, useCallback } from 'react';
// Create toast context
import { useTranslation } from "react-i18next";const ToastContext = createContext();
// Toast provider component
export const ToastProvider = ({ children }) => {const { t } = useTranslation();
  const [toasts, setToasts] = useState([]);
  const toast = useCallback((message, type = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { id, message, type };
    setToasts((prev) => [...prev, newToast]);
    // Auto remove after 3 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  }, []);
  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);
  return (
    <ToastContext.Provider value={{ toasts, toast, removeToast }}>
      {children}
    </ToastContext.Provider>);

};
// Hook to use toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
// Simple toast function for direct usage
export const toast = (message, type = 'info') => {
  // If using react-toastify (which is installed)
  if (window.toast) {
    window.toast[type](message);
  }
};
// Export default toast for import { toast } syntax
export default { toast };