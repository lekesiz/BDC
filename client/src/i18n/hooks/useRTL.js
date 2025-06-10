// TODO: i18n - processed
/**
 * useRTL Hook
 * Access RTL context and helper functions
 */

import { useContext, useCallback, useMemo } from 'react';
import { RTLContext } from '../providers/RTLProvider';import { useTranslation } from "react-i18next";

const useRTL = () => {
  const context = useContext(RTLContext);

  if (!context) {
    throw new Error('useRTL must be used within an RTLProvider');
  }

  const {
    isRTL,
    direction,
    alignment,
    getMargin,
    getPadding,
    getBorder,
    getPosition,
    getTransform,
    getTextAlign
  } = context;

  // Get className based on RTL
  const getRTLClassName = useCallback((ltrClass, rtlClass) => {
    return isRTL ? rtlClass : ltrClass;
  }, [isRTL]);

  // Get style object with RTL support
  const getRTLStyle = useCallback((style) => {
    if (!isRTL || !style) return style;

    const rtlStyle = { ...style };

    // Convert margin
    if ('marginLeft' in style || 'marginRight' in style) {
      const { marginLeft, marginRight } = style;
      if (marginLeft !== undefined) rtlStyle.marginRight = marginLeft;
      if (marginRight !== undefined) rtlStyle.marginLeft = marginRight;
      delete rtlStyle.marginLeft;
      delete rtlStyle.marginRight;
    }

    // Convert padding
    if ('paddingLeft' in style || 'paddingRight' in style) {
      const { paddingLeft, paddingRight } = style;
      if (paddingLeft !== undefined) rtlStyle.paddingRight = paddingLeft;
      if (paddingRight !== undefined) rtlStyle.paddingLeft = paddingRight;
      delete rtlStyle.paddingLeft;
      delete rtlStyle.paddingRight;
    }

    // Convert position
    if ('left' in style || 'right' in style) {
      const { left, right } = style;
      if (left !== undefined) rtlStyle.right = left;
      if (right !== undefined) rtlStyle.left = right;
      delete rtlStyle.left;
      delete rtlStyle.right;
    }

    // Convert border
    if ('borderLeft' in style || 'borderRight' in style) {
      const { borderLeft, borderRight } = style;
      if (borderLeft !== undefined) rtlStyle.borderRight = borderLeft;
      if (borderRight !== undefined) rtlStyle.borderLeft = borderRight;
      delete rtlStyle.borderLeft;
      delete rtlStyle.borderRight;
    }

    // Convert text alignment
    if ('textAlign' in style) {
      rtlStyle.textAlign = getTextAlign(style.textAlign);
    }

    // Convert transform
    if ('transform' in style && style.transform.includes('translateX')) {
      rtlStyle.transform = style.transform.replace(
        /translateX\(([-\d.]+)([a-z%]*)\)/g,
        (match, value, unit) => `translateX(${-parseFloat(value)}${unit})`
      );
    }

    return rtlStyle;
  }, [isRTL, getTextAlign]);

  // Get flex direction
  const getFlexDirection = useCallback((direction) => {
    if (!isRTL) return direction;

    switch (direction) {
      case 'row':
        return 'row-reverse';
      case 'row-reverse':
        return 'row';
      default:
        return direction;
    }
  }, [isRTL]);

  // Get icon position
  const getIconPosition = useCallback((position = 'left') => {
    if (!isRTL) return position;
    return position === 'left' ? 'right' : 'left';
  }, [isRTL]);

  // Get float direction
  const getFloat = useCallback((float) => {
    if (!isRTL) return float;
    return float === 'left' ? 'right' : float === 'right' ? 'left' : float;
  }, [isRTL]);

  // Get clear direction
  const getClear = useCallback((clear) => {
    if (!isRTL) return clear;
    return clear === 'left' ? 'right' : clear === 'right' ? 'left' : clear;
  }, [isRTL]);

  // Get border radius
  const getBorderRadius = useCallback((topLeft, topRight, bottomRight, bottomLeft) => {
    if (!isRTL) {
      return {
        borderTopLeftRadius: topLeft,
        borderTopRightRadius: topRight,
        borderBottomRightRadius: bottomRight,
        borderBottomLeftRadius: bottomLeft
      };
    }

    return {
      borderTopLeftRadius: topRight,
      borderTopRightRadius: topLeft,
      borderBottomRightRadius: bottomLeft,
      borderBottomLeftRadius: bottomRight
    };
  }, [isRTL]);

  // Get logical properties
  const getLogicalStyle = useCallback((style) => {
    const logicalStyle = {};

    // Margin
    if ('marginStart' in style) {
      Object.assign(logicalStyle, getMargin(style.marginStart, style.marginEnd));
    }

    // Padding
    if ('paddingStart' in style) {
      Object.assign(logicalStyle, getPadding(style.paddingStart, style.paddingEnd));
    }

    // Border
    if ('borderStart' in style) {
      Object.assign(logicalStyle, getBorder(style.borderStart, style.borderEnd));
    }

    // Position
    if ('insetStart' in style) {
      Object.assign(logicalStyle, getPosition(style.insetStart, style.insetEnd));
    }

    return logicalStyle;
  }, [getMargin, getPadding, getBorder, getPosition]);

  // Animation direction
  const getAnimationDirection = useCallback((animationName) => {
    if (!isRTL) return animationName;

    const rtlAnimations = {
      'slideInLeft': 'slideInRight',
      'slideInRight': 'slideInLeft',
      'slideOutLeft': 'slideOutRight',
      'slideOutRight': 'slideOutLeft',
      'fadeInLeft': 'fadeInRight',
      'fadeInRight': 'fadeInLeft',
      'fadeOutLeft': 'fadeOutRight',
      'fadeOutRight': 'fadeOutLeft'
    };

    return rtlAnimations[animationName] || animationName;
  }, [isRTL]);

  // Get swipe direction
  const getSwipeDirection = useCallback((direction) => {
    if (!isRTL) return direction;

    switch (direction) {
      case 'left':
        return 'right';
      case 'right':
        return 'left';
      default:
        return direction;
    }
  }, [isRTL]);

  // Memoized return value
  const memoizedReturn = useMemo(() => ({
    // State
    isRTL,
    direction,
    alignment,

    // Style helpers
    getMargin,
    getPadding,
    getBorder,
    getPosition,
    getTransform,
    getTextAlign,
    getRTLStyle,
    getLogicalStyle,
    getBorderRadius,

    // Layout helpers
    getFlexDirection,
    getFloat,
    getClear,

    // Component helpers
    getRTLClassName,
    getIconPosition,
    getAnimationDirection,
    getSwipeDirection,

    // Constants
    start: isRTL ? 'right' : 'left',
    end: isRTL ? 'left' : 'right'
  }), [
  isRTL,
  direction,
  alignment,
  getMargin,
  getPadding,
  getBorder,
  getPosition,
  getTransform,
  getTextAlign,
  getRTLStyle,
  getLogicalStyle,
  getBorderRadius,
  getFlexDirection,
  getFloat,
  getClear,
  getRTLClassName,
  getIconPosition,
  getAnimationDirection,
  getSwipeDirection]
  );

  return memoizedReturn;
};

export default useRTL;