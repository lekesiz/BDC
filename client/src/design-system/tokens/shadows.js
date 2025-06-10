// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Shadow System
export const shadows = {
  // Elevation levels
  elevation: {
    0: 'none',
    1: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
    2: '0 3px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12)',
    3: '0 10px 20px rgba(0, 0, 0, 0.15), 0 3px 6px rgba(0, 0, 0, 0.10)',
    4: '0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22)',
    5: '0 19px 38px rgba(0, 0, 0, 0.30), 0 15px 12px rgba(0, 0, 0, 0.22)'
  },

  // Functional shadows
  functional: {
    focus: '0 0 0 3px rgba(24, 144, 255, 0.3)',
    focusError: '0 0 0 3px rgba(245, 34, 45, 0.3)',
    focusSuccess: '0 0 0 3px rgba(82, 196, 26, 0.3)',
    inset: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    card: '0 2px 8px rgba(0, 0, 0, 0.1)',
    dropdown: '0 4px 12px rgba(0, 0, 0, 0.15)',
    modal: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
  },

  // Colored shadows
  colored: {
    primary: '0 4px 14px 0 rgba(24, 144, 255, 0.35)',
    secondary: '0 4px 14px 0 rgba(47, 84, 235, 0.35)',
    success: '0 4px 14px 0 rgba(82, 196, 26, 0.35)',
    warning: '0 4px 14px 0 rgba(250, 173, 20, 0.35)',
    error: '0 4px 14px 0 rgba(245, 34, 45, 0.35)'
  },

  // Neumorphic shadows (for modern UI)
  neumorphic: {
    flat: {
      light: '-5px -5px 20px #ffffff, 5px 5px 20px #d1d9e6',
      dark: '-5px -5px 20px #2c2c2c, 5px 5px 20px #1a1a1a'
    },
    concave: {
      light: 'inset -5px -5px 20px #ffffff, inset 5px 5px 20px #d1d9e6',
      dark: 'inset -5px -5px 20px #2c2c2c, inset 5px 5px 20px #1a1a1a'
    },
    convex: {
      light: '-10px -10px 30px #ffffff, 10px 10px 30px #d1d9e6',
      dark: '-10px -10px 30px #2c2c2c, 10px 10px 30px #1a1a1a'
    }
  },

  // Glass morphism shadows
  glass: {
    light: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
    dark: '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
  }
};