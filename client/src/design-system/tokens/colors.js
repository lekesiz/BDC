// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Color System with semantic naming and dark mode support
export const colors = {
  // Brand colors
  brand: {
    primary: {
      50: '#e6f7ff',
      100: '#bae7ff',
      200: '#91d5ff',
      300: '#69c0ff',
      400: '#40a9ff',
      500: '#1890ff',
      600: '#096dd9',
      700: '#0050b3',
      800: '#003a8c',
      900: '#002766'
    },
    secondary: {
      50: '#f0f5ff',
      100: '#d6e4ff',
      200: '#adc6ff',
      300: '#85a5ff',
      400: '#597ef7',
      500: '#2f54eb',
      600: '#1d39c4',
      700: '#10239e',
      800: '#061178',
      900: '#030852'
    },
    accent: {
      50: '#fff1f0',
      100: '#ffccc7',
      200: '#ffa39e',
      300: '#ff7875',
      400: '#ff4d4f',
      500: '#f5222d',
      600: '#cf1322',
      700: '#a8071a',
      800: '#820014',
      900: '#5c0011'
    }
  },

  // Semantic colors
  semantic: {
    success: {
      light: '#f6ffed',
      main: '#52c41a',
      dark: '#389e0d',
      contrast: '#ffffff'
    },
    warning: {
      light: '#fffbe6',
      main: '#faad14',
      dark: '#d48806',
      contrast: '#000000'
    },
    error: {
      light: '#fff2f0',
      main: '#ff4d4f',
      dark: '#cf1322',
      contrast: '#ffffff'
    },
    info: {
      light: '#e6f7ff',
      main: '#1890ff',
      dark: '#0050b3',
      contrast: '#ffffff'
    }
  },

  // Neutral colors
  neutral: {
    0: '#ffffff',
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e8e8e8',
    300: '#d9d9d9',
    400: '#bfbfbf',
    500: '#8c8c8c',
    600: '#595959',
    700: '#434343',
    800: '#262626',
    900: '#1f1f1f',
    1000: '#000000'
  },

  // Functional colors
  functional: {
    background: {
      primary: 'var(--color-bg-primary)',
      secondary: 'var(--color-bg-secondary)',
      tertiary: 'var(--color-bg-tertiary)',
      elevated: 'var(--color-bg-elevated)',
      overlay: 'var(--color-bg-overlay)'
    },
    text: {
      primary: 'var(--color-text-primary)',
      secondary: 'var(--color-text-secondary)',
      tertiary: 'var(--color-text-tertiary)',
      disabled: 'var(--color-text-disabled)',
      inverse: 'var(--color-text-inverse)'
    },
    border: {
      light: 'var(--color-border-light)',
      default: 'var(--color-border-default)',
      strong: 'var(--color-border-strong)'
    },
    interactive: {
      hover: 'var(--color-interactive-hover)',
      active: 'var(--color-interactive-active)',
      focus: 'var(--color-interactive-focus)',
      disabled: 'var(--color-interactive-disabled)'
    }
  },

  // Special effects
  effects: {
    gradient: {
      primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      success: 'linear-gradient(135deg, #96fbc4 0%, #f9f586 100%)',
      danger: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    },
    glass: {
      light: 'rgba(255, 255, 255, 0.1)',
      dark: 'rgba(0, 0, 0, 0.1)'
    }
  }
};