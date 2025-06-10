// TODO: i18n - processed
// Theme creation utility
import { lightTheme } from './lightTheme';
import { darkTheme } from './darkTheme';import { useTranslation } from "react-i18next";

export const createTheme = (customTheme = {}) => {
  const baseTheme = customTheme.name === 'dark' ? darkTheme : lightTheme;

  return {
    ...baseTheme,
    ...customTheme,
    colors: {
      ...baseTheme.colors,
      ...(customTheme.colors || {})
    },
    components: {
      ...baseTheme.components,
      ...(customTheme.components || {})
    }
  };
};

// Utility to generate CSS variables from theme
export const generateCSSVariables = (theme) => {
  const cssVars = {};

  // Generate color variables
  Object.entries(theme.colors).forEach(([key, value]) => {
    cssVars[`--color-${key}`] = value;
  });

  // Generate component variables
  const generateComponentVars = (obj, prefix = '') => {
    Object.entries(obj).forEach(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        generateComponentVars(value, `${prefix}${key}-`);
      } else {
        cssVars[`--${prefix}${key}`] = value;
      }
    });
  };

  Object.entries(theme.components).forEach(([component, styles]) => {
    generateComponentVars(styles, `component-${component}-`);
  });

  return cssVars;
};

// Predefined theme variants
export const themes = {
  light: lightTheme,
  dark: darkTheme,

  // High contrast theme for accessibility
  highContrast: createTheme({
    name: 'high-contrast',
    colors: {
      'bg-primary': '#ffffff',
      'bg-secondary': '#f0f0f0',
      'text-primary': '#000000',
      'text-secondary': '#1a1a1a',
      'border-default': '#000000',
      'brand-primary': '#0066cc',
      'semantic-error': '#cc0000',
      'semantic-success': '#008800'
    }
  }),

  // Blue theme
  blue: createTheme({
    name: 'blue',
    colors: {
      'brand-primary': '#0066cc',
      'brand-primary-hover': '#0052a3',
      'brand-primary-active': '#004080'
    }
  })
};