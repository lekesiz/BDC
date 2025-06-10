// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Typography System
export const typography = {
  // Font families
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    serif: 'Georgia, Cambria, "Times New Roman", Times, serif',
    mono: 'Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    display: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },

  // Font sizes with responsive scaling
  fontSize: {
    xs: 'clamp(0.75rem, 1.5vw, 0.875rem)',
    sm: 'clamp(0.875rem, 1.75vw, 1rem)',
    base: 'clamp(1rem, 2vw, 1.125rem)',
    lg: 'clamp(1.125rem, 2.25vw, 1.25rem)',
    xl: 'clamp(1.25rem, 2.5vw, 1.5rem)',
    '2xl': 'clamp(1.5rem, 3vw, 1.875rem)',
    '3xl': 'clamp(1.875rem, 3.75vw, 2.25rem)',
    '4xl': 'clamp(2.25rem, 4.5vw, 3rem)',
    '5xl': 'clamp(3rem, 6vw, 3.75rem)',
    '6xl': 'clamp(3.75rem, 7.5vw, 4.5rem)'
  },

  // Font weights
  fontWeight: {
    thin: 100,
    extralight: 200,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900
  },

  // Line heights
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2
  },

  // Letter spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em'
  },

  // Text styles (composite styles)
  textStyles: {
    // Headings
    h1: {
      fontSize: 'var(--font-size-5xl)',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.025em'
    },
    h2: {
      fontSize: 'var(--font-size-4xl)',
      fontWeight: 700,
      lineHeight: 1.25,
      letterSpacing: '-0.025em'
    },
    h3: {
      fontSize: 'var(--font-size-3xl)',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.025em'
    },
    h4: {
      fontSize: 'var(--font-size-2xl)',
      fontWeight: 600,
      lineHeight: 1.4,
      letterSpacing: '-0.025em'
    },
    h5: {
      fontSize: 'var(--font-size-xl)',
      fontWeight: 600,
      lineHeight: 1.5,
      letterSpacing: '-0.025em'
    },
    h6: {
      fontSize: 'var(--font-size-lg)',
      fontWeight: 600,
      lineHeight: 1.5,
      letterSpacing: '-0.025em'
    },

    // Body text
    body: {
      fontSize: 'var(--font-size-base)',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0'
    },
    bodySmall: {
      fontSize: 'var(--font-size-sm)',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0'
    },
    bodyLarge: {
      fontSize: 'var(--font-size-lg)',
      fontWeight: 400,
      lineHeight: 1.6,
      letterSpacing: '0'
    },

    // Special text
    caption: {
      fontSize: 'var(--font-size-xs)',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0.025em'
    },
    overline: {
      fontSize: 'var(--font-size-xs)',
      fontWeight: 600,
      lineHeight: 1.5,
      letterSpacing: '0.1em',
      textTransform: 'uppercase'
    },
    button: {
      fontSize: 'var(--font-size-sm)',
      fontWeight: 500,
      lineHeight: 1.5,
      letterSpacing: '0.025em'
    },
    code: {
      fontFamily: 'var(--font-family-mono)',
      fontSize: '0.875em',
      fontWeight: 400,
      lineHeight: 1.5
    }
  }
};