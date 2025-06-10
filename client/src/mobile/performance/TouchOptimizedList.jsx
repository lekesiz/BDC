// TODO: i18n - processed
import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { FixedSizeList as List, VariableSizeList } from 'react-window';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { useAdvancedSwipe } from '../gestures/useAdvancedSwipe';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';

/**
 * TouchOptimizedList - High-performance list component optimized for mobile
 * Features virtualization, swipe actions, pull-to-refresh, and infinite scrolling
 */import { useTranslation } from "react-i18next";
export const TouchOptimizedList = ({
  items,
  renderItem,
  itemHeight = 60,
  height = 400,
  width = '100%',
  overscanCount = 5,
  onScroll,
  onItemClick,
  onItemSwipeLeft,
  onItemSwipeRight,
  onPullToRefresh,
  onLoadMore,
  hasNextPage = false,
  isLoading = false,
  loadingComponent,
  emptyComponent,
  swipeThreshold = 80,
  enableVirtualization = true,
  enableInfiniteScroll = false,
  enablePullToRefresh = false,
  className,
  itemClassName,
  ...props
}) => {const { t } = useTranslation();
  const {
    isMobile,
    performance,
    shouldReduceAnimations,
    hapticFeedback: triggerHaptic
  } = useMobile();

  const [pullOffset, setPullOffset] = useState(0);
  const [isPulling, setIsPulling] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const listRef = useRef(null);
  const outerRef = useRef(null);
  const pullStartRef = useRef(0);

  // Disable virtualization on slow devices
  const shouldVirtualize = enableVirtualization && !performance.isSlowDevice && items.length > 50;

  // Handle pull to refresh
  const handleTouchStart = useCallback((e) => {
    if (!enablePullToRefresh || !outerRef.current) return;

    const scrollTop = outerRef.current.scrollTop;
    if (scrollTop === 0) {
      pullStartRef.current = e.touches[0].clientY;
    }
  }, [enablePullToRefresh]);

  const handleTouchMove = useCallback((e) => {
    if (!enablePullToRefresh || !outerRef.current || !pullStartRef.current) return;

    const scrollTop = outerRef.current.scrollTop;
    const currentY = e.touches[0].clientY;
    const deltaY = currentY - pullStartRef.current;

    if (scrollTop === 0 && deltaY > 0) {
      setIsPulling(true);
      setPullOffset(Math.min(deltaY * 0.5, 80)); // Apply resistance
      e.preventDefault();
    }
  }, [enablePullToRefresh]);

  const handleTouchEnd = useCallback(async () => {
    if (!enablePullToRefresh || !isPulling) return;

    setIsPulling(false);

    if (pullOffset > 50 && onPullToRefresh) {
      setIsRefreshing(true);
      triggerHaptic('medium');

      try {
        await onPullToRefresh();
      } finally {
        setIsRefreshing(false);
      }
    }

    setPullOffset(0);
    pullStartRef.current = 0;
  }, [enablePullToRefresh, isPulling, pullOffset, onPullToRefresh, triggerHaptic]);

  // Handle infinite scroll
  const handleScroll = useCallback(({ scrollOffset, scrollUpdateWasRequested }) => {
    if (!scrollUpdateWasRequested && enableInfiniteScroll && hasNextPage && !isLoading) {
      const container = outerRef.current;
      if (container) {
        const { scrollHeight, clientHeight } = container;
        const scrollPercentage = (scrollOffset + clientHeight) / scrollHeight;

        if (scrollPercentage > 0.8) {
          onLoadMore?.();
        }
      }
    }

    onScroll?.({ scrollOffset, scrollUpdateWasRequested });
  }, [enableInfiniteScroll, hasNextPage, isLoading, onLoadMore, onScroll]);

  // Render item with touch optimizations
  const renderOptimizedItem = useCallback(({ index, style, data }) => {
    const item = data[index];
    if (!item) return null;

    return (
      <TouchOptimizedListItem
        key={item.id || index}
        index={index}
        item={item}
        style={style}
        renderItem={renderItem}
        onItemClick={onItemClick}
        onSwipeLeft={onItemSwipeLeft}
        onSwipeRight={onItemSwipeRight}
        swipeThreshold={swipeThreshold}
        className={itemClassName} />);


  }, [renderItem, onItemClick, onItemSwipeLeft, onItemSwipeRight, swipeThreshold, itemClassName]);

  // Render non-virtualized item
  const renderNonVirtualizedItem = useCallback((item, index) => {
    return (
      <TouchOptimizedListItem
        key={item.id || index}
        index={index}
        item={item}
        renderItem={renderItem}
        onItemClick={onItemClick}
        onSwipeLeft={onItemSwipeLeft}
        onSwipeRight={onItemSwipeRight}
        swipeThreshold={swipeThreshold}
        className={itemClassName} />);


  }, [renderItem, onItemClick, onItemSwipeLeft, onItemSwipeRight, swipeThreshold, itemClassName]);

  // Empty state
  if (items.length === 0 && !isLoading) {
    return emptyComponent ||
    <div className="flex items-center justify-center p-8 text-muted-foreground">
        <div className="text-center">
          <div className="text-4xl mb-2">📝</div>
          <p>{t("mobile.no_items_to_display")}</p>
        </div>
      </div>;

  }

  // Non-virtualized list for better compatibility
  if (!shouldVirtualize) {
    return (
      <div
        className={cn('overflow-auto touch-scroll', className)}
        style={{ height, maxHeight: height }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        {...props}>

        {/* Pull to refresh indicator */}
        {enablePullToRefresh && (isPulling || isRefreshing) &&
        <PullToRefreshIndicator
          offset={pullOffset}
          isRefreshing={isRefreshing}
          reducedMotion={shouldReduceAnimations} />

        }
        
        {/* Items */}
        <div style={{ transform: `translateY(${isPulling ? pullOffset : 0}px)` }}>
          {items.map(renderNonVirtualizedItem)}
        </div>
        
        {/* Loading indicator */}
        {isLoading && (
        loadingComponent || <LoadingIndicator reducedMotion={shouldReduceAnimations} />)
        }
      </div>);

  }

  // Virtualized list
  return (
    <div
      className={cn('relative', className)}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      {...props}>

      {/* Pull to refresh indicator */}
      {enablePullToRefresh && (isPulling || isRefreshing) &&
      <PullToRefreshIndicator
        offset={pullOffset}
        isRefreshing={isRefreshing}
        reducedMotion={shouldReduceAnimations} />

      }
      
      <List
        ref={listRef}
        outerRef={outerRef}
        height={height}
        width={width}
        itemCount={items.length}
        itemSize={itemHeight}
        itemData={items}
        overscanCount={overscanCount}
        onScroll={handleScroll}
        style={{
          transform: `translateY(${isPulling ? pullOffset : 0}px)`,
          transition: !isPulling && !shouldReduceAnimations ? 'transform 0.3s ease-out' : 'none'
        }}>

        {renderOptimizedItem}
      </List>
      
      {/* Loading indicator */}
      {isLoading &&
      <div className="absolute bottom-0 left-0 right-0">
          {loadingComponent || <LoadingIndicator reducedMotion={shouldReduceAnimations} />}
        </div>
      }
    </div>);

};

/**
 * TouchOptimizedListItem - Individual list item with touch interactions
 */
const TouchOptimizedListItem = ({
  index,
  item,
  style,
  renderItem,
  onItemClick,
  onSwipeLeft,
  onSwipeRight,
  swipeThreshold,
  className
}) => {const { t } = useTranslation();
  const { hapticFeedback: triggerHaptic, isMobile } = useMobile();
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [isPressed, setIsPressed] = useState(false);

  const swipeHandlers = useAdvancedSwipe({
    onSwipeLeft: onSwipeLeft ? () => {
      triggerHaptic('light');
      onSwipeLeft(item, index);
    } : undefined,
    onSwipeRight: onSwipeRight ? () => {
      triggerHaptic('light');
      onSwipeRight(item, index);
    } : undefined,
    threshold: swipeThreshold,
    direction: 'horizontal',
    enabled: !!(onSwipeLeft || onSwipeRight)
  });

  const handleClick = useCallback(() => {
    if (Math.abs(swipeOffset) < 10) {// Only trigger click if not swiping
      onItemClick?.(item, index);
      if (isMobile) {
        triggerHaptic('light');
      }
    }
  }, [item, index, onItemClick, swipeOffset, isMobile, triggerHaptic]);

  const handleTouchStart = useCallback((e) => {
    setIsPressed(true);
    swipeHandlers.onTouchStart?.(e);
  }, [swipeHandlers]);

  const handleTouchMove = useCallback((e) => {
    setSwipeOffset(swipeHandlers.currentX || 0);
    swipeHandlers.onTouchMove?.(e);
  }, [swipeHandlers]);

  const handleTouchEnd = useCallback((e) => {
    setIsPressed(false);
    setSwipeOffset(0);
    swipeHandlers.onTouchEnd?.(e);
  }, [swipeHandlers]);

  return (
    <div
      style={style}
      className={cn(
        'relative touch-manipulation select-none',
        isPressed && 'bg-accent/50',
        className
      )}
      onClick={handleClick}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      {...swipeHandlers.onTouchStart && { onTouchStart: handleTouchStart }}
      {...swipeHandlers.onTouchMove && { onTouchMove: handleTouchMove }}
      {...swipeHandlers.onTouchEnd && { onTouchEnd: handleTouchEnd }}>

      {/* Swipe background actions */}
      {(onSwipeLeft || onSwipeRight) && Math.abs(swipeOffset) > 10 &&
      <div className="absolute inset-0 flex items-center">
          {swipeOffset > 0 && onSwipeRight &&
        <div className="flex-1 bg-green-500 text-white flex items-center justify-start px-4">
              <span>{t("mobile.swipe_right_action")}</span>
            </div>
        }
          {swipeOffset < 0 && onSwipeLeft &&
        <div className="flex-1 bg-red-500 text-white flex items-center justify-end px-4">
              <span>{t("mobile.swipe_left_action")}</span>
            </div>
        }
        </div>
      }
      
      {/* Item content */}
      <div
        style={{
          transform: `translateX(${swipeOffset}px)`,
          transition: swipeHandlers.isSwiping ? 'none' : 'transform 0.2s ease-out'
        }}
        className="relative z-10 bg-background">

        {renderItem(item, index)}
      </div>
    </div>);

};

/**
 * Pull to refresh indicator
 */
const PullToRefreshIndicator = ({ offset, isRefreshing, reducedMotion }) =>
<div
  className="absolute top-0 left-0 right-0 flex items-center justify-center bg-background z-20"
  style={{
    height: Math.max(0, offset),
    transform: `translateY(-${Math.max(0, 60 - offset)}px)`
  }}>

    {isRefreshing ?
  <div className="flex items-center gap-2 text-primary">
        <div className={cn(
      'w-4 h-4 border-2 border-primary border-t-transparent rounded-full',
      !reducedMotion && 'animate-spin'
    )} />
        <span className="text-sm font-medium">{t("mobile.refreshing")}</span>
      </div> :
  offset > 50 ?
  <div className="text-primary text-sm font-medium">Release to refresh</div> :
  offset > 0 ?
  <div className="text-muted-foreground text-sm">Pull to refresh</div> :
  null}
  </div>;


/**
 * Loading indicator
 */
const LoadingIndicator = ({ reducedMotion }) =>
<div className="flex items-center justify-center p-4">
    <div className={cn(
    'w-6 h-6 border-2 border-primary border-t-transparent rounded-full',
    !reducedMotion && 'animate-spin'
  )} />
  </div>;


/**
 * VariableSizeList wrapper for dynamic item heights
 */
export const TouchOptimizedVariableList = ({
  items,
  getItemHeight,
  estimatedItemHeight = 60,
  ...props
}) => {const { t } = useTranslation();
  const { performance } = useMobile();
  const getItemSize = useCallback((index) => {
    return getItemHeight ? getItemHeight(items[index], index) : estimatedItemHeight;
  }, [items, getItemHeight, estimatedItemHeight]);

  // Fallback to regular list on slow devices
  if (performance.isSlowDevice) {
    return <TouchOptimizedList {...props} items={items} enableVirtualization={false} />;
  }

  return (
    <VariableSizeList
      itemCount={items.length}
      itemSize={getItemSize}
      estimatedItemSize={estimatedItemHeight}
      itemData={items}
      {...props} />);


};

export default TouchOptimizedList;