import React, { useState, useRef, useCallback, useEffect, memo } from 'react';
import { useVirtualScroll } from '@/utils/reactOptimizations';
/**
 * Virtual list component for efficiently rendering large lists
 */
export const VirtualList = memo(({
  items,
  itemHeight,
  height,
  renderItem,
  className = '',
  overscan = 5,
  onScroll,
  getItemKey,
  estimatedItemHeight,
  loadMore,
  hasMore = false,
  loadMoreThreshold = 100,
  emptyComponent,
  ...props
}) => {
  const containerRef = useRef(null);
  const scrollingRef = useRef(false);
  const [dynamicHeights, setDynamicHeights] = useState({});
  // Use dynamic heights if available, otherwise fixed height
  const getHeight = useCallback((index) => {
    return dynamicHeights[index] || itemHeight || estimatedItemHeight || 50;
  }, [dynamicHeights, itemHeight, estimatedItemHeight]);
  // Calculate positions based on dynamic heights
  const positions = React.useMemo(() => {
    const positions = [];
    let totalHeight = 0;
    for (let i = 0; i < items.length; i++) {
      positions.push(totalHeight);
      totalHeight += getHeight(i);
    }
    return positions;
  }, [items.length, getHeight]);
  const totalHeight = positions[positions.length - 1] + getHeight(items.length - 1);
  const {
    visibleItems,
    offsetY,
    handleScroll: virtualHandleScroll,
    startIndex,
    endIndex
  } = useVirtualScroll({
    items,
    itemHeight: itemHeight || estimatedItemHeight || 50,
    containerHeight: height,
    overscan
  });
  // Handle scroll with infinite loading
  const handleScroll = useCallback((e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    virtualHandleScroll(e);
    if (onScroll) {
      onScroll(e);
    }
    // Check if we need to load more
    if (loadMore && hasMore) {
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
      if (distanceFromBottom < loadMoreThreshold && !scrollingRef.current) {
        scrollingRef.current = true;
        loadMore().finally(() => {
          scrollingRef.current = false;
        });
      }
    }
  }, [virtualHandleScroll, onScroll, loadMore, hasMore, loadMoreThreshold]);
  // Measure item heights for dynamic sizing
  const measureItem = useCallback((index, element) => {
    if (element && !itemHeight) {
      const height = element.getBoundingClientRect().height;
      if (height !== dynamicHeights[index]) {
        setDynamicHeights(prev => ({
          ...prev,
          [index]: height
        }));
      }
    }
  }, [itemHeight, dynamicHeights]);
  // Handle empty state
  if (items.length === 0 && emptyComponent) {
    return (
      <div className={className} style={{ height }} {...props}>
        {emptyComponent}
      </div>
    );
  }
  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height }}
      onScroll={handleScroll}
      {...props}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map((item, relativeIndex) => {
          const index = startIndex + relativeIndex;
          const key = getItemKey ? getItemKey(item, index) : index;
          const position = positions[index] || 0;
          return (
            <div
              key={key}
              style={{
                position: 'absolute',
                top: position,
                left: 0,
                right: 0,
                height: itemHeight || 'auto'
              }}
              ref={(el) => measureItem(index, el)}
            >
              {renderItem(item, index)}
            </div>
          );
        })}
      </div>
    </div>
  );
});
VirtualList.displayName = 'VirtualList';
/**
 * Dynamic virtual list with variable item heights
 */
export const DynamicVirtualList = memo(({
  items,
  estimatedItemHeight = 50,
  height,
  renderItem,
  className = '',
  overscan = 5,
  getItemKey,
  ...props
}) => {
  const [itemHeights, setItemHeights] = useState({});
  const scrollPositionRef = useRef(0);
  const containerRef = useRef(null);
  // Calculate actual positions based on measured heights
  const { positions, totalHeight } = React.useMemo(() => {
    const positions = [];
    let totalHeight = 0;
    for (let i = 0; i < items.length; i++) {
      positions.push(totalHeight);
      totalHeight += itemHeights[i] || estimatedItemHeight;
    }
    return { positions, totalHeight };
  }, [items.length, itemHeights, estimatedItemHeight]);
  // Find visible range
  const visibleRange = React.useMemo(() => {
    const scrollTop = scrollPositionRef.current;
    const scrollBottom = scrollTop + height;
    let startIndex = 0;
    let endIndex = items.length - 1;
    // Binary search for start index
    let low = 0;
    let high = positions.length - 1;
    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      const position = positions[mid];
      if (position < scrollTop) {
        startIndex = mid;
        low = mid + 1;
      } else {
        high = mid - 1;
      }
    }
    // Find end index
    for (let i = startIndex; i < positions.length; i++) {
      if (positions[i] > scrollBottom) {
        endIndex = i;
        break;
      }
    }
    // Add overscan
    startIndex = Math.max(0, startIndex - overscan);
    endIndex = Math.min(items.length - 1, endIndex + overscan);
    return { startIndex, endIndex };
  }, [positions, height, items.length, overscan]);
  // Handle item height measurement
  const measureItem = useCallback((index, element) => {
    if (element) {
      const height = element.getBoundingClientRect().height;
      if (height !== itemHeights[index]) {
        setItemHeights(prev => ({
          ...prev,
          [index]: height
        }));
      }
    }
  }, [itemHeights]);
  // Handle scroll
  const handleScroll = useCallback((e) => {
    scrollPositionRef.current = e.target.scrollTop;
    // Force re-render to update visible range
    setItemHeights(prev => ({ ...prev }));
  }, []);
  const visibleItems = items.slice(
    visibleRange.startIndex,
    visibleRange.endIndex + 1
  );
  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height }}
      onScroll={handleScroll}
      {...props}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map((item, relativeIndex) => {
          const index = visibleRange.startIndex + relativeIndex;
          const key = getItemKey ? getItemKey(item, index) : index;
          const position = positions[index] || 0;
          return (
            <div
              key={key}
              style={{
                position: 'absolute',
                top: position,
                left: 0,
                right: 0
              }}
              ref={(el) => measureItem(index, el)}
            >
              {renderItem(item, index)}
            </div>
          );
        })}
      </div>
    </div>
  );
});
DynamicVirtualList.displayName = 'DynamicVirtualList';
/**
 * Virtual grid component for 2D virtualization
 */
export const VirtualGrid = memo(({
  items,
  itemWidth,
  itemHeight,
  height,
  renderItem,
  className = '',
  gap = 0,
  overscan = 5,
  getItemKey,
  ...props
}) => {
  const containerRef = useRef(null);
  const [containerWidth, setContainerWidth] = useState(0);
  const [scrollTop, setScrollTop] = useState(0);
  // Calculate grid dimensions
  const columns = Math.floor((containerWidth + gap) / (itemWidth + gap));
  const rows = Math.ceil(items.length / columns);
  const totalHeight = rows * (itemHeight + gap) - gap;
  // Calculate visible range
  const visibleRange = React.useMemo(() => {
    const startRow = Math.max(0, Math.floor(scrollTop / (itemHeight + gap)) - overscan);
    const endRow = Math.min(
      rows - 1,
      Math.ceil((scrollTop + height) / (itemHeight + gap)) + overscan
    );
    const startIndex = startRow * columns;
    const endIndex = Math.min(items.length - 1, (endRow + 1) * columns - 1);
    return { startIndex, endIndex, startRow, endRow };
  }, [scrollTop, height, itemHeight, gap, overscan, rows, columns, items.length]);
  // Handle container resize
  useEffect(() => {
    const resizeObserver = new ResizeObserver(entries => {
      for (let entry of entries) {
        setContainerWidth(entry.contentRect.width);
      }
    });
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    return () => resizeObserver.disconnect();
  }, []);
  // Handle scroll
  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);
  const visibleItems = items.slice(
    visibleRange.startIndex,
    visibleRange.endIndex + 1
  );
  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height }}
      onScroll={handleScroll}
      {...props}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map((item, relativeIndex) => {
          const index = visibleRange.startIndex + relativeIndex;
          const row = Math.floor(index / columns);
          const col = index % columns;
          const key = getItemKey ? getItemKey(item, index) : index;
          return (
            <div
              key={key}
              style={{
                position: 'absolute',
                top: row * (itemHeight + gap),
                left: col * (itemWidth + gap),
                width: itemWidth,
                height: itemHeight
              }}
            >
              {renderItem(item, index)}
            </div>
          );
        })}
      </div>
    </div>
  );
});
VirtualGrid.displayName = 'VirtualGrid';