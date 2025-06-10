// TODO: i18n - processed
import React, { memo, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';

/**
 * Optimized List Item component
 */import { useTranslation } from "react-i18next";
const ListItem = memo(({ item, onItemClick, renderItem, isSelected = false }) => {
  const handleClick = useCallback(() => {
    if (onItemClick) {
      onItemClick(item);
    }
  }, [item, onItemClick]);

  return (
    <div
      className={cn(
        'p-3 cursor-pointer transition-colors',
        isSelected ? 'bg-primary/10' : 'hover:bg-gray-100'
      )}
      onClick={handleClick}>

      {renderItem(item)}
    </div>);

});

ListItem.displayName = 'ListItem';

/**
 * Optimized List component with virtualization support
 * Uses React.memo and useMemo for performance
 */
const OptimizedList = memo(({
  items = [],
  renderItem,
  onItemClick,
  selectedId,
  className,
  emptyMessage = 'No items found',
  loading = false,
  keyExtractor = (item) => item.id
}) => {
  // Memoize the list of items to prevent unnecessary re-renders
  const memoizedItems = useMemo(() => items, [items]);

  // Memoize the empty state
  const emptyState = useMemo(() =>
  <div className="text-center py-8 text-gray-500">
      {emptyMessage}
    </div>,
  [emptyMessage]);

  // Memoize the loading state
  const loadingState = useMemo(() =>
  <div className="text-center py-8">
      <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
      <p className="mt-2 text-gray-500">Loading...</p>
    </div>,
  []);

  if (loading) {
    return loadingState;
  }

  if (memoizedItems.length === 0) {
    return emptyState;
  }

  return (
    <div className={cn('divide-y divide-gray-200', className)}>
      {memoizedItems.map((item) => {
        const key = keyExtractor(item);
        return (
          <ListItem
            key={key}
            item={item}
            onItemClick={onItemClick}
            renderItem={renderItem}
            isSelected={selectedId === key} />);


      })}
    </div>);

});

OptimizedList.displayName = 'OptimizedList';

/**
 * Virtualized List for large datasets
 * Only renders visible items
 */
export const VirtualizedList = memo(({
  items = [],
  itemHeight = 60,
  containerHeight = 400,
  renderItem,
  onItemClick,
  selectedId,
  className,
  keyExtractor = (item) => item.id
}) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  const scrollRef = React.useRef(null);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const end = Math.ceil((scrollTop + containerHeight) / itemHeight);
    return { start, end };
  }, [scrollTop, itemHeight, containerHeight]);

  // Get visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end + 1);
  }, [items, visibleRange]);

  // Handle scroll
  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  // Calculate total height
  const totalHeight = items.length * itemHeight;

  return (
    <div
      ref={scrollRef}
      className={cn('overflow-auto', className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}>

      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${visibleRange.start * itemHeight}px)`
          }}>

          {visibleItems.map((item) => {
            const key = keyExtractor(item);
            return (
              <div
                key={key}
                style={{ height: itemHeight }}
                className={cn(
                  'flex items-center px-4 cursor-pointer transition-colors',
                  selectedId === key ? 'bg-primary/10' : 'hover:bg-gray-100'
                )}
                onClick={() => onItemClick && onItemClick(item)}>

                {renderItem(item)}
              </div>);

          })}
        </div>
      </div>
    </div>);

});

VirtualizedList.displayName = 'VirtualizedList';

export default OptimizedList;