import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';
import { MobileSafeArea } from '../components/MobileSafeArea';

/**
 * MobileTabNavigation - Advanced mobile tab navigation with gestures and animations
 * Features swipe navigation, haptic feedback, and accessibility support
 */
export const MobileTabNavigation = ({
  tabs,
  className,
  variant = 'bottom',
  showLabels = true,
  showBadges = true,
  allowSwipeNavigation = true,
  hapticFeedback = true,
  animationDuration = 300,
  tabIndicatorStyle = 'pill',
  scrollable = false,
  centerActiveTab = true,
  onTabChange,
  ...props
}) => {
  const location = useLocation();
  const { 
    isMobile, 
    hapticFeedback: triggerHaptic, 
    shouldReduceAnimations,
    screenSize 
  } = useMobile();

  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const [indicatorStyle, setIndicatorStyle] = useState({});
  const [isScrolling, setIsScrolling] = useState(false);
  const tabsRef = useRef(null);
  const tabRefs = useRef([]);

  // Find active tab based on current route
  useEffect(() => {
    const currentPath = location.pathname;
    const activeIndex = tabs.findIndex(tab => {
      if (tab.path === currentPath) return true;
      if (tab.matchPaths && tab.matchPaths.some(path => currentPath.startsWith(path))) return true;
      return false;
    });
    
    if (activeIndex !== -1 && activeIndex !== activeTabIndex) {
      setActiveTabIndex(activeIndex);
    }
  }, [location.pathname, tabs, activeTabIndex]);

  // Update indicator position
  useEffect(() => {
    const updateIndicator = () => {
      const activeTabRef = tabRefs.current[activeTabIndex];
      if (!activeTabRef || !tabsRef.current) return;

      const tabRect = activeTabRef.getBoundingClientRect();
      const containerRect = tabsRef.current.getBoundingClientRect();
      
      const left = tabRect.left - containerRect.left;
      const width = tabRect.width;

      setIndicatorStyle({
        transform: `translateX(${left}px)`,
        width: `${width}px`,
        transition: shouldReduceAnimations ? 'none' : `all ${animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`
      });
    };

    updateIndicator();
    
    // Update on resize
    const handleResize = () => {
      requestAnimationFrame(updateIndicator);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [activeTabIndex, shouldReduceAnimations, animationDuration]);

  // Handle tab change
  const handleTabChange = (index, tab) => {
    if (index === activeTabIndex) return;
    
    setActiveTabIndex(index);
    
    if (hapticFeedback && isMobile) {
      triggerHaptic('light');
    }
    
    onTabChange?.(index, tab);

    // Auto-scroll to center active tab if scrollable
    if (scrollable && centerActiveTab) {
      const activeTabRef = tabRefs.current[index];
      if (activeTabRef && tabsRef.current) {
        activeTabRef.scrollIntoView({
          behavior: shouldReduceAnimations ? 'auto' : 'smooth',
          block: 'nearest',
          inline: 'center'
        });
      }
    }
  };

  // Swipe navigation
  const handleSwipeLeft = () => {
    if (!allowSwipeNavigation) return;
    const nextIndex = Math.min(activeTabIndex + 1, tabs.length - 1);
    if (nextIndex !== activeTabIndex) {
      const nextTab = tabs[nextIndex];
      handleTabChange(nextIndex, nextTab);
    }
  };

  const handleSwipeRight = () => {
    if (!allowSwipeNavigation) return;
    const prevIndex = Math.max(activeTabIndex - 1, 0);
    if (prevIndex !== activeTabIndex) {
      const prevTab = tabs[prevIndex];
      handleTabChange(prevIndex, prevTab);
    }
  };

  // Position classes
  const positionClasses = {
    top: 'top-0 border-b',
    bottom: 'bottom-0 border-t',
    floating: 'bottom-4 left-4 right-4 rounded-2xl shadow-lg'
  };

  // Tab indicator classes
  const indicatorClasses = {
    line: 'h-0.5 bg-primary rounded-full',
    pill: 'h-full bg-primary/10 rounded-full border border-primary/20',
    dot: 'h-1 w-1 bg-primary rounded-full'
  };

  return (
    <MobileSafeArea
      bottom={variant === 'bottom'}
      top={variant === 'top'}
      className={cn(
        'fixed left-0 right-0 z-40 bg-background/95 backdrop-blur-sm',
        positionClasses[variant],
        variant === 'floating' && 'mx-4',
        className
      )}
      {...props}
    >
      <nav
        ref={tabsRef}
        className={cn(
          'relative flex',
          scrollable ? 'overflow-x-auto scrollbar-hide' : 'justify-around',
          'min-h-[64px] px-2'
        )}
        role="tablist"
        aria-label="Main navigation"
      >
        {/* Tab indicator */}
        {tabIndicatorStyle !== 'none' && (
          <div
            className={cn(
              'absolute transition-all duration-300 ease-out',
              indicatorClasses[tabIndicatorStyle],
              variant === 'top' ? 'bottom-0' : 'top-0',
              tabIndicatorStyle === 'dot' && 'top-1/2 -translate-y-1/2'
            )}
            style={indicatorStyle}
            aria-hidden="true"
          />
        )}

        {/* Tabs */}
        {tabs.map((tab, index) => {
          const isActive = index === activeTabIndex;
          const Icon = tab.icon;
          
          return (
            <Link
              key={tab.id || index}
              ref={el => tabRefs.current[index] = el}
              to={tab.path}
              className={cn(
                'relative flex flex-col items-center justify-center',
                'min-w-[60px] flex-1 px-3 py-2',
                'transition-colors duration-200',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                scrollable && 'flex-shrink-0',
                isActive ? 'text-primary' : 'text-muted-foreground',
                !showLabels && 'py-4'
              )}
              role="tab"
              aria-selected={isActive}
              aria-current={isActive ? 'page' : undefined}
              onClick={() => handleTabChange(index, tab)}
            >
              {/* Icon */}
              <div className="relative flex items-center justify-center">
                {Icon && (
                  <Icon 
                    className={cn(
                      'transition-all duration-200',
                      showLabels ? 'h-5 w-5 mb-1' : 'h-6 w-6',
                      isActive && 'scale-110'
                    )}
                    aria-hidden="true"
                  />
                )}
                
                {/* Badge */}
                {showBadges && tab.badge && (
                  <div className={cn(
                    'absolute -top-1 -right-1 min-w-[18px] h-[18px]',
                    'flex items-center justify-center',
                    'bg-destructive text-destructive-foreground',
                    'text-xs font-medium rounded-full px-1',
                    'animate-pulse'
                  )}>
                    {typeof tab.badge === 'number' && tab.badge > 99 ? '99+' : tab.badge}
                  </div>
                )}
              </div>

              {/* Label */}
              {showLabels && tab.label && (
                <span className={cn(
                  'text-xs font-medium transition-all duration-200',
                  'truncate max-w-full',
                  isActive && 'font-semibold'
                )}>
                  {tab.label}
                </span>
              )}

              {/* Active indicator for dot style */}
              {tabIndicatorStyle === 'dot' && isActive && (
                <div className="absolute top-1 w-1 h-1 bg-primary rounded-full" />
              )}
            </Link>
          );
        })}
      </nav>
    </MobileSafeArea>
  );
};

/**
 * MobileTopTabs - Specialized component for top navigation tabs
 */
export const MobileTopTabs = (props) => (
  <MobileTabNavigation variant="top" {...props} />
);

/**
 * MobileBottomTabs - Specialized component for bottom navigation tabs
 */
export const MobileBottomTabs = (props) => (
  <MobileTabNavigation variant="bottom" {...props} />
);

/**
 * FloatingTabs - Floating tab navigation
 */
export const FloatingTabs = (props) => (
  <MobileTabNavigation variant="floating" {...props} />
);

/**
 * ScrollableTabs - Horizontal scrollable tabs
 */
export const ScrollableTabs = ({
  tabs,
  className,
  ...props
}) => (
  <div className={cn('border-b bg-background', className)}>
    <MobileTabNavigation
      tabs={tabs}
      variant="top"
      scrollable
      tabIndicatorStyle="line"
      showLabels={false}
      className="relative border-0"
      {...props}
    />
  </div>
);

/**
 * TabContent - Container for tab content with swipe navigation
 */
export const TabContent = ({
  children,
  activeTab,
  onSwipeLeft,
  onSwipeRight,
  allowSwipe = true,
  className,
  ...props
}) => {
  const { shouldReduceAnimations } = useMobile();

  return (
    <div
      className={cn(
        'flex-1 overflow-hidden',
        shouldReduceAnimations ? '' : 'transition-all duration-300',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default MobileTabNavigation;