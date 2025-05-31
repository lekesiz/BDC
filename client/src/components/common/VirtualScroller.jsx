import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';

const VirtualScroller = ({
  items,
  itemHeight,
  height,
  renderItem,
  overscan = 3,
  className = '',
  getItemHeight,
  estimatedItemHeight = 50,
  onScroll
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef(null);
  const isVariableHeight = typeof getItemHeight === 'function';
  
  // Calculate item positions for variable height items
  const itemPositions = useMemo(() => {
    if (!isVariableHeight) return null;
    
    const positions = [];
    let offset = 0;
    
    for (let i = 0; i < items.length; i++) {
      positions.push({
        index: i,
        offset,
        height: getItemHeight(i) || estimatedItemHeight
      });
      offset += positions[i].height;
    }
    
    return positions;
  }, [items, isVariableHeight, getItemHeight, estimatedItemHeight]);

  const totalHeight = useMemo(() => {
    if (isVariableHeight && itemPositions) {
      return itemPositions[itemPositions.length - 1]?.offset + 
             itemPositions[itemPositions.length - 1]?.height || 0;
    }
    return items.length * itemHeight;
  }, [items.length, itemHeight, isVariableHeight, itemPositions]);

  const getItemOffset = useCallback((index) => {
    if (isVariableHeight && itemPositions) {
      return itemPositions[index]?.offset || 0;
    }
    return index * itemHeight;
  }, [isVariableHeight, itemPositions, itemHeight]);

  const getItemHeightAt = useCallback((index) => {
    if (isVariableHeight && itemPositions) {
      return itemPositions[index]?.height || estimatedItemHeight;
    }
    return itemHeight;
  }, [isVariableHeight, itemPositions, itemHeight, estimatedItemHeight]);

  const visibleRange = useMemo(() => {
    const startIndex = isVariableHeight
      ? itemPositions?.findIndex(item => item.offset + item.height > scrollTop) || 0
      : Math.floor(scrollTop / itemHeight);
    
    let endIndex = startIndex;
    let accumulatedHeight = 0;
    
    if (isVariableHeight && itemPositions) {
      for (let i = startIndex; i < items.length && accumulatedHeight < height; i++) {
        accumulatedHeight += itemPositions[i].height;
        endIndex = i;
      }
    } else {
      endIndex = Math.ceil((scrollTop + height) / itemHeight);
    }
    
    return {
      start: Math.max(0, startIndex - overscan),
      end: Math.min(items.length - 1, endIndex + overscan)
    };
  }, [scrollTop, height, itemHeight, items.length, overscan, isVariableHeight, itemPositions]);

  const visibleItems = useMemo(() => {
    const visibleItemsList = [];
    
    for (let i = visibleRange.start; i <= visibleRange.end; i++) {
      visibleItemsList.push({
        index: i,
        item: items[i],
        offset: getItemOffset(i),
        height: getItemHeightAt(i)
      });
    }
    
    return visibleItemsList;
  }, [items, visibleRange, getItemOffset, getItemHeightAt]);

  const handleScroll = useCallback((e) => {
    const newScrollTop = e.target.scrollTop;
    setScrollTop(newScrollTop);
    onScroll?.(e);
  }, [onScroll]);

  useEffect(() => {
    const scrollElement = scrollElementRef.current;
    if (scrollElement) {
      scrollElement.addEventListener('scroll', handleScroll, { passive: true });
      return () => scrollElement.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  return (
    <div
      ref={scrollElementRef}
      className={`overflow-auto ${className}`}
      style={{ height }}
    >
      <div
        style={{
          height: totalHeight,
          position: 'relative'
        }}
      >
        {visibleItems.map(({ index, item, offset, height: itemHeightValue }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: offset,
              left: 0,
              right: 0,
              height: itemHeightValue
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
};

export default React.memo(VirtualScroller);