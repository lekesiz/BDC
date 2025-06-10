// TODO: i18n - processed
// Dark Theme Configuration
import { colors } from '../tokens/colors';import { useTranslation } from "react-i18next";

export const darkTheme = {
  name: 'dark',

  // Color mappings
  colors: {
    // Backgrounds
    'bg-primary': colors.neutral[900],
    'bg-secondary': colors.neutral[800],
    'bg-tertiary': colors.neutral[700],
    'bg-elevated': colors.neutral[800],
    'bg-overlay': 'rgba(0, 0, 0, 0.7)',

    // Text
    'text-primary': colors.neutral[50],
    'text-secondary': colors.neutral[300],
    'text-tertiary': colors.neutral[400],
    'text-disabled': colors.neutral[600],
    'text-inverse': colors.neutral[900],

    // Borders
    'border-light': colors.neutral[700],
    'border-default': colors.neutral[600],
    'border-strong': colors.neutral[500],

    // Interactive states
    'interactive-hover': colors.neutral[800],
    'interactive-active': colors.neutral[700],
    'interactive-focus': colors.brand.primary[400],
    'interactive-disabled': colors.neutral[800],

    // Brand colors (adjusted for dark mode)
    'brand-primary': colors.brand.primary[400],
    'brand-primary-hover': colors.brand.primary[300],
    'brand-primary-active': colors.brand.primary[500],
    'brand-secondary': colors.brand.secondary[400],
    'brand-secondary-hover': colors.brand.secondary[300],
    'brand-secondary-active': colors.brand.secondary[500],

    // Semantic colors (adjusted for dark mode)
    'semantic-success': colors.semantic.success.main,
    'semantic-warning': colors.semantic.warning.main,
    'semantic-error': colors.semantic.error.main,
    'semantic-info': colors.semantic.info.main,

    // Special effects
    'glass-bg': 'rgba(0, 0, 0, 0.5)',
    'glass-border': 'rgba(255, 255, 255, 0.1)',
    'shadow-color': 'rgba(0, 0, 0, 0.3)'
  },

  // Component-specific theming
  components: {
    button: {
      primary: {
        bg: 'var(--color-brand-primary)',
        color: 'var(--color-text-inverse)',
        border: 'transparent',
        hover: {
          bg: 'var(--color-brand-primary-hover)',
          border: 'transparent'
        },
        active: {
          bg: 'var(--color-brand-primary-active)',
          border: 'transparent'
        }
      },
      secondary: {
        bg: 'transparent',
        color: 'var(--color-brand-primary)',
        border: 'var(--color-brand-primary)',
        hover: {
          bg: 'var(--color-brand-primary)',
          color: 'var(--color-text-inverse)',
          border: 'var(--color-brand-primary)'
        }
      },
      ghost: {
        bg: 'transparent',
        color: 'var(--color-text-primary)',
        border: 'transparent',
        hover: {
          bg: 'var(--color-interactive-hover)',
          border: 'transparent'
        }
      }
    },

    card: {
      bg: 'var(--color-bg-elevated)',
      border: 'var(--color-border-light)',
      shadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
    },

    input: {
      bg: 'var(--color-bg-tertiary)',
      border: 'var(--color-border-default)',
      placeholder: 'var(--color-text-tertiary)',
      focus: {
        border: 'var(--color-interactive-focus)'
      }
    },

    modal: {
      bg: 'var(--color-bg-elevated)',
      overlay: 'var(--color-bg-overlay)',
      shadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
    }
  }
};