import React, { useState, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { X, Menu, ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { MobileDrawer } from '../components/MobileDrawer';
import { TouchOptimizedButton } from '../components/TouchOptimizedButton';
import { MobileSafeArea } from '../components/MobileSafeArea';

/**
 * MobileSidebar - Responsive sidebar navigation with collapsible groups
 * Features smooth animations, search, and touch-optimized interactions
 */
export const MobileSidebar = ({
  navigation = [],
  isOpen,
  onClose,
  title = 'Navigation',
  showSearch = false,
  searchPlaceholder = 'Search...',
  allowGroupCollapse = true,
  showUserProfile = false,
  userProfile,
  footer,
  className,
  contentClassName,
  ...props
}) => {
  const location = useLocation();
  const { 
    isMobile, 
    hapticFeedback: triggerHaptic, 
    shouldReduceAnimations 
  } = useMobile();

  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedGroups, setCollapsedGroups] = useState(new Set());
  const [filteredNavigation, setFilteredNavigation] = useState(navigation);

  // Filter navigation based on search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredNavigation(navigation);
      return;
    }

    const filterItems = (items) => {
      return items.reduce((acc, item) => {
        if (item.type === 'group') {
          const filteredChildren = filterItems(item.children || []);
          if (filteredChildren.length > 0 || 
              item.title.toLowerCase().includes(searchQuery.toLowerCase())) {
            acc.push({
              ...item,
              children: filteredChildren
            });
          }
        } else {
          if (item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
              item.description?.toLowerCase().includes(searchQuery.toLowerCase())) {
            acc.push(item);
          }
        }
        return acc;
      }, []);
    };

    setFilteredNavigation(filterItems(navigation));
  }, [searchQuery, navigation]);

  // Toggle group collapse
  const toggleGroup = useCallback((groupId) => {
    if (!allowGroupCollapse) return;
    
    setCollapsedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });

    triggerHaptic('light');
  }, [allowGroupCollapse, triggerHaptic]);

  // Handle navigation item click
  const handleItemClick = useCallback((item) => {
    if (item.onClick) {
      item.onClick();
    }
    
    // Close sidebar on mobile after navigation
    if (isMobile && item.path) {
      setTimeout(() => onClose?.(), 150);
    }
    
    triggerHaptic('light');
  }, [isMobile, onClose, triggerHaptic]);

  // Check if item is active
  const isItemActive = useCallback((item) => {
    if (!item.path) return false;
    
    if (item.exact) {
      return location.pathname === item.path;
    }
    
    return location.pathname.startsWith(item.path);
  }, [location.pathname]);

  // Render navigation item
  const renderNavItem = useCallback((item, depth = 0) => {
    const isActive = isItemActive(item);
    const Icon = item.icon;
    const hasChildren = item.children && item.children.length > 0;

    if (item.type === 'divider') {
      return (
        <div 
          key={item.id || `divider-${depth}`}
          className="my-2 border-t border-border/50"
        />
      );
    }

    if (item.type === 'group') {
      const isCollapsed = collapsedGroups.has(item.id);
      
      return (
        <div key={item.id} className="mb-2">
          {/* Group Header */}
          <TouchOptimizedButton
            variant="ghost"
            className={cn(
              'w-full justify-between h-auto p-3 text-left',
              'hover:bg-accent/50 rounded-lg'
            )}
            onClick={() => allowGroupCollapse && toggleGroup(item.id)}
            disabled={!allowGroupCollapse}
          >
            <div className="flex items-center gap-3">
              {item.icon && (
                <item.icon className="h-4 w-4 text-muted-foreground" />
              )}
              <span className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
                {item.title}
              </span>
            </div>
            
            {allowGroupCollapse && (
              <ChevronDown 
                className={cn(
                  'h-4 w-4 text-muted-foreground transition-transform duration-200',
                  isCollapsed && 'rotate-180'
                )}
              />
            )}
          </TouchOptimizedButton>

          {/* Group Items */}
          <div className={cn(
            'overflow-hidden transition-all duration-300',
            isCollapsed ? 'max-h-0 opacity-0' : 'max-h-[1000px] opacity-100'
          )}>
            <div className="pl-4 space-y-1 mt-1">
              {item.children?.map(child => renderNavItem(child, depth + 1))}
            </div>
          </div>
        </div>
      );
    }

    // Regular navigation item
    const ItemComponent = item.path ? Link : 'button';
    const itemProps = item.path 
      ? { to: item.path }
      : { onClick: () => handleItemClick(item) };

    return (
      <ItemComponent
        key={item.id || item.path}
        {...itemProps}
        className={cn(
          'flex items-center gap-3 w-full p-3 rounded-lg',
          'transition-colors duration-200 text-left',
          'hover:bg-accent/50 focus-visible:bg-accent/50',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
          isActive ? 'bg-primary/10 text-primary border border-primary/20' : 'text-foreground',
          depth > 0 && 'ml-4',
          item.disabled && 'opacity-50 cursor-not-allowed'
        )}
        disabled={item.disabled}
        aria-current={isActive ? 'page' : undefined}
      >
        {/* Icon */}
        {Icon && (
          <Icon 
            className={cn(
              'h-5 w-5 flex-shrink-0',
              isActive ? 'text-primary' : 'text-muted-foreground'
            )} 
          />
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className={cn(
              'font-medium truncate',
              isActive && 'font-semibold'
            )}>
              {item.title}
            </span>
            
            {/* Badge */}
            {item.badge && (
              <span className={cn(
                'ml-2 px-2 py-0.5 text-xs font-medium rounded-full',
                'bg-destructive text-destructive-foreground',
                isActive && 'bg-primary text-primary-foreground'
              )}>
                {item.badge}
              </span>
            )}

            {/* Arrow for expandable items */}
            {hasChildren && (
              <ChevronRight className="h-4 w-4 text-muted-foreground ml-2" />
            )}
          </div>
          
          {/* Description */}
          {item.description && (
            <p className="text-xs text-muted-foreground mt-0.5 truncate">
              {item.description}
            </p>
          )}
        </div>
      </ItemComponent>
    );
  }, [
    isItemActive,
    collapsedGroups,
    allowGroupCollapse,
    toggleGroup,
    handleItemClick
  ]);

  return (
    <MobileDrawer
      isOpen={isOpen}
      onClose={onClose}
      position="left"
      size="md"
      title={title}
      className={className}
      contentClassName={cn('flex flex-col h-full', contentClassName)}
      {...props}
    >
      <MobileSafeArea className="flex flex-col h-full">
        {/* Header with Search */}
        {showSearch && (
          <div className="p-4 border-b">
            <div className="relative">
              <input
                type="text"
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={cn(
                  'w-full pl-3 pr-3 py-2 text-sm',
                  'bg-muted border border-border rounded-lg',
                  'focus:outline-none focus:ring-2 focus:ring-primary',
                  'placeholder:text-muted-foreground'
                )}
              />
            </div>
          </div>
        )}

        {/* User Profile */}
        {showUserProfile && userProfile && (
          <div className="p-4 border-b">
            <div className="flex items-center gap-3">
              {userProfile.avatar && (
                <img
                  src={userProfile.avatar}
                  alt={userProfile.name}
                  className="w-10 h-10 rounded-full object-cover"
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{userProfile.name}</p>
                {userProfile.email && (
                  <p className="text-sm text-muted-foreground truncate">
                    {userProfile.email}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto p-4">
          <nav className="space-y-1">
            {filteredNavigation.map(item => renderNavItem(item))}
            
            {/* No results */}
            {searchQuery && filteredNavigation.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <p>No navigation items found</p>
                <p className="text-sm mt-1">Try adjusting your search</p>
              </div>
            )}
          </nav>
        </div>

        {/* Footer */}
        {footer && (
          <div className="border-t p-4">
            {footer}
          </div>
        )}
      </MobileSafeArea>
    </MobileDrawer>
  );
};

/**
 * SidebarTrigger - Button to open the mobile sidebar
 */
export const SidebarTrigger = ({
  onClick,
  className,
  ...props
}) => {
  const { hapticFeedback: triggerHaptic, isMobile } = useMobile();

  const handleClick = () => {
    if (isMobile) {
      triggerHaptic('light');
    }
    onClick?.();
  };

  return (
    <TouchOptimizedButton
      variant="ghost"
      size="icon"
      onClick={handleClick}
      className={cn('lg:hidden', className)}
      aria-label="Open navigation menu"
      {...props}
    >
      <Menu className="h-5 w-5" />
    </TouchOptimizedButton>
  );
};

export default MobileSidebar;