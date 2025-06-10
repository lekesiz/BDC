// TODO: i18n - processed
import React, { forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { useMobile } from './MobileProvider';

/**
 * ResponsiveContainer - Adaptive container that adjusts based on device type
 * Provides consistent spacing, safe areas, and responsive behavior
 */import { useTranslation } from "react-i18next";
export const ResponsiveContainer = forwardRef(({
  children,
  className,
  variant = 'default',
  padding = 'responsive',
  maxWidth = 'responsive',
  safeArea = true,
  fullHeight = false,
  centerContent = false,
  scrollable = false,
  maintainAspectRatio,
  backgroundBlur = false,
  ...props
}, ref) => {
  const {
    isMobile,
    isTablet,
    isDesktop,
    orientation,
    capabilities
  } = useMobile();

  // Determine padding based on device and preference
  const getPadding = () => {
    if (padding === 'none') return '';
    if (padding === 'responsive') {
      if (isMobile) return 'p-4';
      if (isTablet) return 'p-6';
      return 'p-8';
    }
    return padding;
  };

  // Determine max width based on device and preference
  const getMaxWidth = () => {
    if (maxWidth === 'responsive') {
      if (isMobile) return 'max-w-full';
      if (isTablet) return 'max-w-3xl';
      return 'max-w-6xl';
    }
    if (maxWidth === 'full') return 'max-w-full';
    return maxWidth;
  };

  // Variant styles
  const variantStyles = {
    default: 'bg-background',
    card: 'bg-card rounded-lg shadow-sm border',
    elevated: 'bg-card rounded-lg shadow-lg border',
    glass: 'bg-background/80 backdrop-blur-sm rounded-lg border',
    sidebar: 'bg-card border-r',
    modal: 'bg-card rounded-t-lg shadow-xl border-t',
    fullscreen: 'bg-background min-h-screen',
    section: 'bg-muted/50 rounded-lg'
  };

  // Safe area classes
  const safeAreaClasses = safeArea ? {
    top: capabilities.isStandalone ? 'pt-safe' : '',
    bottom: capabilities.isStandalone ? 'pb-safe' : '',
    left: 'pl-safe',
    right: 'pr-safe'
  } : {};

  // Aspect ratio utility
  const aspectRatioClass = maintainAspectRatio ? {
    '16:9': 'aspect-video',
    '4:3': 'aspect-[4/3]',
    '1:1': 'aspect-square',
    '3:2': 'aspect-[3/2]',
    '21:9': 'aspect-[21/9]'
  }[maintainAspectRatio] : '';

  const containerClasses = cn(
    // Base styles
    'relative w-full mx-auto',

    // Variant
    variantStyles[variant],

    // Responsive padding
    getPadding(),

    // Max width
    getMaxWidth(),

    // Height
    fullHeight && 'min-h-screen',

    // Center content
    centerContent && 'flex items-center justify-center',

    // Scrollable
    scrollable && 'overflow-auto touch-scroll',

    // Safe areas
    Object.values(safeAreaClasses).join(' '),

    // Aspect ratio
    aspectRatioClass,

    // Background blur
    backgroundBlur && 'backdrop-blur-sm',

    // Mobile-specific optimizations
    isMobile && [
    'mobile-optimized',
    orientation === 'landscape' && 'landscape-optimized'],


    // Custom className
    className
  );

  return (
    <div
      ref={ref}
      className={containerClasses}
      {...props}>

      {children}
    </div>);

});

ResponsiveContainer.displayName = 'ResponsiveContainer';

/**
 * ResponsiveGrid - Grid that adapts columns based on screen size
 */
export const ResponsiveGrid = forwardRef(({
  children,
  className,
  columns = { mobile: 1, tablet: 2, desktop: 3 },
  gap = 'responsive',
  minItemWidth,
  autoFit = false,
  ...props
}, ref) => {
  const { isMobile, isTablet, isDesktop } = useMobile();

  const getGridColumns = () => {
    if (autoFit && minItemWidth) {
      return `repeat(auto-fit, minmax(${minItemWidth}, 1fr))`;
    }

    if (isMobile) return `repeat(${columns.mobile}, 1fr)`;
    if (isTablet) return `repeat(${columns.tablet}, 1fr)`;
    return `repeat(${columns.desktop}, 1fr)`;
  };

  const getGap = () => {
    if (gap === 'responsive') {
      if (isMobile) return 'gap-4';
      if (isTablet) return 'gap-6';
      return 'gap-8';
    }
    return gap;
  };

  const gridClasses = cn(
    'grid',
    getGap(),
    className
  );

  const gridStyle = autoFit && minItemWidth ? {
    gridTemplateColumns: getGridColumns()
  } : {};

  return (
    <div
      ref={ref}
      className={gridClasses}
      style={{
        ...gridStyle,
        ...((!autoFit || !minItemWidth) && {
          gridTemplateColumns: getGridColumns()
        })
      }}
      {...props}>

      {children}
    </div>);

});

ResponsiveGrid.displayName = 'ResponsiveGrid';

/**
 * ResponsiveFlex - Flexible container that adapts direction and alignment
 */
export const ResponsiveFlex = forwardRef(({
  children,
  className,
  direction = { mobile: 'column', desktop: 'row' },
  align = 'center',
  justify = 'start',
  gap = 'responsive',
  wrap = true,
  ...props
}, ref) => {
  const { isMobile, isTablet, isDesktop } = useMobile();

  const getDirection = () => {
    if (typeof direction === 'string') return direction;
    if (isMobile && direction.mobile) return direction.mobile;
    if (isTablet && direction.tablet) return direction.tablet;
    if (isDesktop && direction.desktop) return direction.desktop;
    return 'row';
  };

  const getGap = () => {
    if (gap === 'responsive') {
      if (isMobile) return 'gap-3';
      if (isTablet) return 'gap-4';
      return 'gap-6';
    }
    return gap;
  };

  const directionClass = {
    row: 'flex-row',
    column: 'flex-col',
    'row-reverse': 'flex-row-reverse',
    'column-reverse': 'flex-col-reverse'
  }[getDirection()];

  const alignClass = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
    baseline: 'items-baseline'
  }[align];

  const justifyClass = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly'
  }[justify];

  const flexClasses = cn(
    'flex',
    directionClass,
    alignClass,
    justifyClass,
    getGap(),
    wrap && 'flex-wrap',
    className
  );

  return (
    <div
      ref={ref}
      className={flexClasses}
      {...props}>

      {children}
    </div>);

});

ResponsiveFlex.displayName = 'ResponsiveFlex';

export default ResponsiveContainer;