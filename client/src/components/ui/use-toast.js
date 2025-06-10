// Re-export from toast.jsx for backward compatibility
export { useToast } from './toast';
// Simple toast function
export const toast = {
  success: (message) => console.log('Success:', message),
  error: (message) => console.error('Error:', message),
  warning: (message) => console.warn('Warning:', message),
  info: (message) => console.log('Info:', message),
};