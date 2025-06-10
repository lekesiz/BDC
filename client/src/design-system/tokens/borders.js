// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Border System
export const borders = {
  // Border widths
  width: {
    none: '0',
    thin: '1px',
    medium: '2px',
    thick: '4px',
    heavy: '8px'
  },

  // Border radius
  radius: {
    none: '0',
    sm: '0.125rem', // 2px
    base: '0.25rem', // 4px
    md: '0.375rem', // 6px
    lg: '0.5rem', // 8px
    xl: '0.75rem', // 12px
    '2xl': '1rem', // 16px
    '3xl': '1.5rem', // 24px
    full: '9999px',
    circle: '50%'
  },

  // Border styles
  style: {
    solid: 'solid',
    dashed: 'dashed',
    dotted: 'dotted',
    double: 'double',
    none: 'none'
  },

  // Component-specific borders
  component: {
    button: {
      default: '1px solid var(--color-border-default)',
      hover: '1px solid var(--color-border-strong)',
      focus: '2px solid var(--color-interactive-focus)'
    },
    input: {
      default: '1px solid var(--color-border-default)',
      hover: '1px solid var(--color-border-strong)',
      focus: '2px solid var(--color-interactive-focus)',
      error: '2px solid var(--color-semantic-error)'
    },
    card: {
      default: '1px solid var(--color-border-light)',
      hover: '1px solid var(--color-border-default)'
    },
    divider: {
      horizontal: '1px solid var(--color-border-light)',
      vertical: '1px solid var(--color-border-light)'
    }
  },

  // Decorative borders
  decorative: {
    gradient: {
      primary: '2px solid transparent',
      backgroundImage: 'linear-gradient(white, white), linear-gradient(to right, #667eea, #764ba2)',
      backgroundOrigin: 'border-box',
      backgroundClip: 'padding-box, border-box'
    },
    animated: {
      border: '2px solid transparent',
      backgroundImage: 'linear-gradient(45deg, #667eea, #764ba2, #667eea)',
      backgroundSize: '400% 400%',
      animation: 'gradient 3s ease infinite'
    }
  }
};