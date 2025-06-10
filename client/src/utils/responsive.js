// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Responsive utility classes for mobile-first design
 */
// Touch-friendly tap target sizes (minimum 44px as per iOS guidelines)
export const tapTargetClasses = {
  small: 'min-h-[36px] min-w-[36px] p-2',
  medium: 'min-h-[44px] min-w-[44px] p-3',
  large: 'min-h-[48px] min-w-[48px] p-4'
};
// Responsive padding classes
export const responsivePadding = {
  none: 'p-0',
  small: 'p-2 sm:p-3 lg:p-4',
  medium: 'p-3 sm:p-4 lg:p-6',
  large: 'p-4 sm:p-6 lg:p-8',
  xlarge: 'p-6 sm:p-8 lg:p-10'
};
// Responsive margin classes
export const responsiveMargin = {
  none: 'm-0',
  small: 'm-2 sm:m-3 lg:m-4',
  medium: 'm-3 sm:m-4 lg:m-6',
  large: 'm-4 sm:m-6 lg:m-8',
  xlarge: 'm-6 sm:m-8 lg:m-10'
};
// Responsive text sizes
export const responsiveText = {
  xs: 'text-xs sm:text-sm',
  sm: 'text-sm sm:text-base',
  base: 'text-base sm:text-lg',
  lg: 'text-lg sm:text-xl lg:text-2xl',
  xl: 'text-xl sm:text-2xl lg:text-3xl',
  '2xl': 'text-2xl sm:text-3xl lg:text-4xl',
  '3xl': 'text-3xl sm:text-4xl lg:text-5xl'
};
// Responsive grid layouts
export const responsiveGrid = {
  cols1: 'grid grid-cols-1',
  cols2: 'grid grid-cols-1 sm:grid-cols-2',
  cols3: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  cols4: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  cols6: 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6'
};
// Responsive flex layouts
export const responsiveFlex = {
  stackMobile: 'flex flex-col sm:flex-row',
  wrapMobile: 'flex flex-wrap',
  centerMobile: 'flex flex-col items-center sm:flex-row sm:items-start',
  spaceBetween: 'flex flex-col sm:flex-row sm:justify-between'
};
// Mobile-specific utility classes
export const mobileUtils = {
  hideOnMobile: 'hidden sm:block',
  showOnMobile: 'block sm:hidden',
  stackOnMobile: 'flex flex-col sm:flex-row',
  fullWidthMobile: 'w-full sm:w-auto',
  textCenterMobile: 'text-center sm:text-left',
  noPaddingMobile: 'p-0 sm:p-4',
  smallPaddingMobile: 'p-2 sm:p-4'
};
// Responsive modal sizes
export const responsiveModal = {
  small: 'w-full max-w-sm',
  medium: 'w-full max-w-md',
  large: 'w-full max-w-lg',
  fullMobile: 'w-full h-full sm:h-auto sm:max-h-[90vh] sm:max-w-lg',
  drawer: 'fixed inset-0 sm:relative sm:inset-auto'
};
// Helper function to combine responsive classes
export const combineClasses = (...classes) => {
  return classes.filter(Boolean).join(' ');
};