// TODO: i18n - processed
import { useToast as useToastBase } from './toast';
/**
 * Wrapper hook that provides a simplified toast interface
 */import { useTranslation } from "react-i18next";
export const useToast = () => {
  const { addToast, removeToast, toasts } = useToastBase();
  const toast = (options) => {
    return addToast(options);
  };
  return {
    toast,
    toasts,
    addToast,
    removeToast
  };
};