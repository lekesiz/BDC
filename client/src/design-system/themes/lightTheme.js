// TODO: i18n - processed
// Light Theme Configuration
import { colors } from '../tokens/colors';import { useTranslation } from "react-i18next";

export const lightTheme = {
  name: 'light',

  // Color mappings
  colors: {
    // Backgrounds
    'bg-primary': colors.neutral[0],
    'bg-secondary': colors.neutral[50],
    'bg-tertiary': colors.neutral[100],
    'bg-elevated': colors.neutral[0],
    'bg-overlay': 'rgba(0, 0, 0, 0.5)',

    // Text
    'text-primary': colors.neutral[900],
    'text-secondary': colors.neutral[600],
    'text-tertiary': colors.neutral[500],
    'text-disabled': colors.neutral[400],
    'text-inverse': colors.neutral[0],

    // Borders
    'border-light': colors.neutral[200],
    'border-default': colors.neutral[300],
    'border-strong': colors.neutral[400],

    // Interactive states
    'interactive-hover': colors.neutral[100],
    'interactive-active': colors.neutral[200],
    'interactive-focus': colors.brand.primary[500],
    'interactive-disabled': colors.neutral[100],

    // Brand colors
    'brand-primary': colors.brand.primary[500],
    'brand-primary-hover': colors.brand.primary[600],
    'brand-primary-active': colors.brand.primary[700],
    'brand-secondary': colors.brand.secondary[500],
    'brand-secondary-hover': colors.brand.secondary[600],
    'brand-secondary-active': colors.brand.secondary[700],

    // Semantic colors
    'semantic-success': colors.semantic.success.main,
    'semantic-warning': colors.semantic.warning.main,
    'semantic-error': colors.semantic.error.main,
    'semantic-info': colors.semantic.info.main,

    // Special effects
    'glass-bg': 'rgba(255, 255, 255, 0.8)',
    'glass-border': 'rgba(255, 255, 255, 0.18)',
    'shadow-color': 'rgba(0, 0, 0, 0.1)'
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
      shadow: 'var(--shadow-card)'
    },

    input: {
      bg: 'var(--color-bg-primary)',
      border: 'var(--color-border-default)',
      placeholder: 'var(--color-text-tertiary)',
      focus: {
        border: 'var(--color-interactive-focus)'
      }
    },

    modal: {
      bg: 'var(--color-bg-elevated)',
      overlay: 'var(--color-bg-overlay)',
      shadow: 'var(--shadow-modal)'
    }
  }
};