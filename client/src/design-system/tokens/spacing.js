// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Spacing System - Based on 8px grid
export const spacing = {
  // Base unit
  unit: 8,

  // Spacing scale
  scale: {
    0: '0',
    px: '1px',
    0.5: '0.125rem', // 2px
    1: '0.25rem', // 4px
    1.5: '0.375rem', // 6px
    2: '0.5rem', // 8px
    2.5: '0.625rem', // 10px
    3: '0.75rem', // 12px
    3.5: '0.875rem', // 14px
    4: '1rem', // 16px
    5: '1.25rem', // 20px
    6: '1.5rem', // 24px
    7: '1.75rem', // 28px
    8: '2rem', // 32px
    9: '2.25rem', // 36px
    10: '2.5rem', // 40px
    11: '2.75rem', // 44px
    12: '3rem', // 48px
    14: '3.5rem', // 56px
    16: '4rem', // 64px
    20: '5rem', // 80px
    24: '6rem', // 96px
    28: '7rem', // 112px
    32: '8rem', // 128px
    36: '9rem', // 144px
    40: '10rem', // 160px
    44: '11rem', // 176px
    48: '12rem', // 192px
    52: '13rem', // 208px
    56: '14rem', // 224px
    60: '15rem', // 240px
    64: '16rem', // 256px
    72: '18rem', // 288px
    80: '20rem', // 320px
    96: '24rem' // 384px
  },

  // Component-specific spacing
  component: {
    // Padding
    padding: {
      button: {
        sm: '0.5rem 1rem',
        md: '0.75rem 1.5rem',
        lg: '1rem 2rem'
      },
      card: {
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem'
      },
      input: {
        sm: '0.5rem 0.75rem',
        md: '0.75rem 1rem',
        lg: '1rem 1.25rem'
      },
      modal: {
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem'
      }
    },

    // Margin
    margin: {
      section: {
        sm: '2rem',
        md: '3rem',
        lg: '4rem'
      },
      element: {
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem'
      },
      text: {
        sm: '0.25rem',
        md: '0.5rem',
        lg: '0.75rem'
      }
    },

    // Gap (for flexbox/grid)
    gap: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem',
      '2xl': '3rem'
    }
  },

  // Layout spacing
  layout: {
    container: {
      padding: {
        mobile: '1rem',
        tablet: '2rem',
        desktop: '3rem'
      },
      maxWidth: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px'
      }
    },
    grid: {
      gap: {
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem'
      }
    }
  }
};