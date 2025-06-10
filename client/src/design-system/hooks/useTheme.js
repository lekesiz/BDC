// TODO: i18n - processed
// Theme Hook
import { useContext } from 'react';
import { ThemeContext } from '../themes/ThemeProvider';import { useTranslation } from "react-i18next";

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};