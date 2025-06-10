// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Responsive Breakpoints
export const breakpoints = {
  // Breakpoint values
  values: {
    xs: 0,
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536
  },

  // Media queries
  up: {
    xs: '@media (min-width: 0px)',
    sm: '@media (min-width: 640px)',
    md: '@media (min-width: 768px)',
    lg: '@media (min-width: 1024px)',
    xl: '@media (min-width: 1280px)',
    '2xl': '@media (min-width: 1536px)'
  },

  down: {
    xs: '@media (max-width: 639px)',
    sm: '@media (max-width: 767px)',
    md: '@media (max-width: 1023px)',
    lg: '@media (max-width: 1279px)',
    xl: '@media (max-width: 1535px)',
    '2xl': '@media (max-width: 9999px)'
  },

  between: {
    'xs-sm': '@media (min-width: 0px) and (max-width: 639px)',
    'sm-md': '@media (min-width: 640px) and (max-width: 767px)',
    'md-lg': '@media (min-width: 768px) and (max-width: 1023px)',
    'lg-xl': '@media (min-width: 1024px) and (max-width: 1279px)',
    'xl-2xl': '@media (min-width: 1280px) and (max-width: 1535px)'
  },

  // Device-specific queries
  device: {
    mobile: '@media (max-width: 767px)',
    tablet: '@media (min-width: 768px) and (max-width: 1023px)',
    desktop: '@media (min-width: 1024px)',
    touch: '@media (hover: none) and (pointer: coarse)',
    mouse: '@media (hover: hover) and (pointer: fine)'
  },

  // Orientation queries
  orientation: {
    portrait: '@media (orientation: portrait)',
    landscape: '@media (orientation: landscape)'
  },

  // High resolution screens
  retina: {
    '2x': '@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)',
    '3x': '@media (-webkit-min-device-pixel-ratio: 3), (min-resolution: 288dpi)'
  }
};