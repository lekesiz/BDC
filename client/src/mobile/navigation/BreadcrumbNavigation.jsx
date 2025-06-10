import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Home, MoreHorizontal } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';
import { MobileDrawer } from '../components/MobileDrawer';

/**
 * BreadcrumbNavigation - Mobile-optimized breadcrumb component
 * Features overflow handling, touch interactions, and contextual actions
 */
export const BreadcrumbNavigation = ({
  items = [],
  className,
  maxVisibleItems = 3,
  showHomeButton = true,
  homeIcon = Home,
  homePath = '/',
  separator = ChevronRight,
  collapsedLabel = 'Show more',
  allowOverflow = true,
  contextActions,
  compact = false,
  scrollable = false,
  ...props
}) => {
  const location = useLocation();
  const { 
    isMobile, 
    hapticFeedback: triggerHaptic, 
    shouldReduceAnimations,
    screenSize 
  } = useMobile();

  const [showOverflow, setShowOverflow] = useState(false);
  const [isOverflowing, setIsOverflowing] = useState(false);
  const containerRef = useRef(null);
  const SeparatorIcon = separator;
  const HomeIcon = homeIcon;

  // Check if breadcrumbs are overflowing
  useEffect(() => {
    const checkOverflow = () => {
      if (!containerRef.current || !allowOverflow) return;
      
      const container = containerRef.current;
      const isOverflowing = container.scrollWidth > container.clientWidth;
      setIsOverflowing(isOverflowing);
    };

    checkOverflow();
    window.addEventListener('resize', checkOverflow);
    return () => window.removeEventListener('resize', checkOverflow);
  }, [items, allowOverflow]);

  // Auto-generate breadcrumbs from current path if no items provided
  const breadcrumbItems = items.length > 0 ? items : generateBreadcrumbsFromPath(location.pathname);

  // Determine visible items based on overflow strategy
  const getVisibleItems = () => {
    if (!allowOverflow || breadcrumbItems.length <= maxVisibleItems) {
      return breadcrumbItems;
    }

    // Show first item, ellipsis, and last few items
    const firstItem = breadcrumbItems[0];
    const lastItems = breadcrumbItems.slice(-Math.max(1, maxVisibleItems - 2));
    const hiddenItems = breadcrumbItems.slice(1, -Math.max(1, maxVisibleItems - 2));

    if (hiddenItems.length === 0) {
      return breadcrumbItems;
    }

    return [
      firstItem,
      { 
        id: 'overflow', 
        label: '...', 
        isOverflow: true, 
        hiddenItems,
        onClick: () => setShowOverflow(true)
      },
      ...lastItems
    ];
  };

  const visibleItems = getVisibleItems();

  // Handle breadcrumb click
  const handleBreadcrumbClick = (item) => {
    if (item.onClick) {
      item.onClick();
    }
    
    if (isMobile) {
      triggerHaptic('light');
    }
  };

  return (
    <>
      <nav
        ref={containerRef}
        className={cn(
          'flex items-center',
          scrollable ? 'overflow-x-auto scrollbar-hide' : 'overflow-hidden',
          compact ? 'py-1 px-2' : 'py-2 px-4',
          'bg-background border-b',
          className
        )}
        aria-label="Breadcrumb"
        {...props}
      >
        <ol className={cn(
          'flex items-center',
          scrollable ? 'flex-nowrap min-w-full' : 'flex-wrap',
          'text-sm space-x-1'
        )}>
          {/* Home button */}
          {showHomeButton && (
            <li className="flex items-center">
              <Link
                to={homePath}
                className={cn(
                  'flex items-center justify-center',
                  'p-1.5 rounded-md transition-colors',
                  'hover:bg-accent text-muted-foreground hover:text-foreground',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
                )}
                aria-label="Home"
                onClick={() => handleBreadcrumbClick({ path: homePath })}
              >
                <HomeIcon className="h-4 w-4" />
              </Link>
              
              {breadcrumbItems.length > 0 && (
                <SeparatorIcon className="h-3 w-3 text-muted-foreground mx-1" />
              )}
            </li>
          )}

          {/* Breadcrumb items */}
          {visibleItems.map((item, index) => {
            const isLast = index === visibleItems.length - 1;
            const isOverflowItem = item.isOverflow;

            return (
              <li key={item.id || index} className="flex items-center">
                {/* Breadcrumb item */}
                {isOverflowItem ? (
                  <TouchOptimizedButton
                    variant="ghost"
                    size="sm"
                    className="h-auto p-1 min-w-0"
                    onClick={() => handleBreadcrumbClick(item)}
                    aria-label={collapsedLabel}
                  >
                    <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
                  </TouchOptimizedButton>
                ) : item.path ? (
                  <Link
                    to={item.path}
                    className={cn(
                      'px-2 py-1 rounded-md transition-colors min-w-0',
                      'hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                      isLast 
                        ? 'text-foreground font-medium cursor-default pointer-events-none' 
                        : 'text-muted-foreground hover:text-foreground',
                      compact && 'px-1 py-0.5'
                    )}
                    aria-current={isLast ? 'page' : undefined}
                    onClick={() => handleBreadcrumbClick(item)}
                  >
                    <span className="truncate block max-w-[120px] md:max-w-none">
                      {item.label}
                    </span>
                  </Link>
                ) : (
                  <span className={cn(
                    'px-2 py-1 min-w-0',
                    isLast ? 'text-foreground font-medium' : 'text-muted-foreground',
                    compact && 'px-1 py-0.5'
                  )}>
                    <span className="truncate block max-w-[120px] md:max-w-none">
                      {item.label}
                    </span>
                  </span>
                )}

                {/* Separator */}
                {!isLast && (
                  <SeparatorIcon className="h-3 w-3 text-muted-foreground mx-1 flex-shrink-0" />
                )}
              </li>
            );
          })}
        </ol>

        {/* Context actions */}
        {contextActions && (
          <div className="ml-auto flex items-center gap-1">
            {contextActions}
          </div>
        )}
      </nav>

      {/* Overflow drawer */}
      <MobileDrawer
        isOpen={showOverflow}
        onClose={() => setShowOverflow(false)}
        title="Navigation Path"
        position="bottom"
        size="auto"
      >
        <div className="p-4">
          <div className="space-y-2">
            {breadcrumbItems.map((item, index) => (
              <Link
                key={item.id || index}
                to={item.path || '#'}
                className={cn(
                  'flex items-center gap-3 p-3 rounded-lg',
                  'hover:bg-accent transition-colors',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                  index === breadcrumbItems.length - 1 && 'bg-primary/10 text-primary'
                )}
                onClick={() => {
                  handleBreadcrumbClick(item);
                  setShowOverflow(false);
                }}
              >
                {item.icon && <item.icon className="h-5 w-5" />}
                <div className="flex-1">
                  <p className="font-medium">{item.label}</p>
                  {item.description && (
                    <p className="text-sm text-muted-foreground">
                      {item.description}
                    </p>
                  )}
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
            ))}
          </div>
        </div>
      </MobileDrawer>
    </>
  );
};

/**
 * Generate breadcrumbs from current pathname
 */
function generateBreadcrumbsFromPath(pathname) {
  const segments = pathname.split('/').filter(Boolean);
  
  return segments.map((segment, index) => {
    const path = '/' + segments.slice(0, index + 1).join('/');
    const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
    
    return {
      id: path,
      label,
      path: index === segments.length - 1 ? undefined : path // Don't make last item clickable
    };
  });
}

/**
 * CompactBreadcrumb - Minimal breadcrumb for tight spaces
 */
export const CompactBreadcrumb = (props) => (
  <BreadcrumbNavigation
    compact
    maxVisibleItems={2}
    showHomeButton={false}
    {...props}
  />
);

/**
 * ScrollableBreadcrumb - Horizontal scrolling breadcrumb
 */
export const ScrollableBreadcrumb = (props) => (
  <BreadcrumbNavigation
    scrollable
    allowOverflow={false}
    {...props}
  />
);

/**
 * useBreadcrumbs - Hook for managing breadcrumb state
 */
export const useBreadcrumbs = (initialItems = []) => {
  const [items, setItems] = useState(initialItems);

  const addBreadcrumb = (item) => {
    setItems(prev => [...prev, item]);
  };

  const removeBreadcrumb = (id) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  const updateBreadcrumb = (id, updates) => {
    setItems(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ));
  };

  const clearBreadcrumbs = () => {
    setItems([]);
  };

  const setBreadcrumbs = (newItems) => {
    setItems(newItems);
  };

  return {
    items,
    addBreadcrumb,
    removeBreadcrumb,
    updateBreadcrumb,
    clearBreadcrumbs,
    setBreadcrumbs
  };
};

export default BreadcrumbNavigation;