// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';
import { MobileSafeArea } from '../components/MobileSafeArea';
import { MobileTabNavigation } from '../navigation/MobileTabNavigation';
import { MobileSidebar } from '../navigation/MobileSidebar';
import { BreadcrumbNavigation } from '../navigation/BreadcrumbNavigation';

/**
 * MobileLayout - Comprehensive layout component for mobile applications
 * Features responsive header, navigation, and content areas with safe area support
 */import { useTranslation } from "react-i18next";
export const MobileLayout = ({
  children,
  header,
  navigation,
  sidebar,
  breadcrumbs,
  footer,
  showTabNavigation = true,
  showSidebar = false,
  showBreadcrumbs = false,
  variant = 'standard', // standard, fullscreen, modal
  className,
  headerClassName,
  contentClassName,
  footerClassName,
  ...props
}) => {const { t } = useTranslation();
  const {
    isMobile,
    capabilities,
    orientation,
    screenSize
  } = useMobile();

  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Auto-close sidebar on orientation change or screen resize
  useEffect(() => {
    setSidebarOpen(false);
  }, [orientation, screenSize.width]);

  const layoutClasses = {
    standard: 'flex flex-col min-h-screen',
    fullscreen: 'flex flex-col h-screen overflow-hidden',
    modal: 'flex flex-col max-h-screen'
  };

  return (
    <MobileSafeArea
      className={cn(
        layoutClasses[variant],
        'bg-background',
        className
      )}
      {...props}>

      {/* Header */}
      {header &&
      <header className={cn(
        'sticky top-0 z-30 bg-background/95 backdrop-blur-sm',
        'border-b border-border',
        capabilities.isStandalone && 'pt-safe',
        headerClassName
      )}>
          {header}
          
          {/* Breadcrumbs */}
          {showBreadcrumbs && breadcrumbs &&
        <div className="border-t border-border/50">
              {breadcrumbs}
            </div>
        }
        </header>
      }

      {/* Main Content Area */}
      <main className={cn(
        'flex-1 overflow-hidden',
        variant === 'fullscreen' ? 'flex flex-col' : 'min-h-0',
        contentClassName
      )}>
        {children}
      </main>

      {/* Footer */}
      {footer &&
      <footer className={cn(
        'border-t border-border bg-background',
        capabilities.isStandalone && 'pb-safe',
        footerClassName
      )}>
          {footer}
        </footer>
      }

      {/* Tab Navigation */}
      {showTabNavigation && navigation && isMobile &&
      <MobileTabNavigation {...navigation} />
      }

      {/* Sidebar */}
      {showSidebar && sidebar &&
      <MobileSidebar
        {...sidebar}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)} />

      }
    </MobileSafeArea>);

};

/**
 * MobilePageLayout - Layout for individual pages
 */
export const MobilePageLayout = ({
  children,
  title,
  subtitle,
  actions,
  backButton,
  showHeader = true,
  headerClassName,
  contentClassName,
  padding = 'responsive',
  scrollable = true,
  ...props
}) => {const { t } = useTranslation();
  const { isMobile } = useMobile();

  const getPadding = () => {
    if (padding === 'none') return '';
    if (padding === 'responsive') {
      return isMobile ? 'p-4' : 'p-6';
    }
    return padding;
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Page Header */}
      {showHeader && (title || subtitle || actions || backButton) &&
      <header className={cn(
        'sticky top-0 z-20 bg-background/95 backdrop-blur-sm',
        'border-b border-border',
        'flex items-center gap-4 p-4',
        headerClassName
      )}>
          {/* Back Button */}
          {backButton}
          
          {/* Title Section */}
          <div className="flex-1 min-w-0">
            {title &&
          <h1 className="text-lg font-semibold truncate">
                {title}
              </h1>
          }
            {subtitle &&
          <p className="text-sm text-muted-foreground truncate">
                {subtitle}
              </p>
          }
          </div>
          
          {/* Actions */}
          {actions &&
        <div className="flex items-center gap-2">
              {actions}
            </div>
        }
        </header>
      }

      {/* Page Content */}
      <main className={cn(
        'flex-1',
        scrollable ? 'overflow-auto' : 'overflow-hidden',
        getPadding(),
        contentClassName
      )}>
        {children}
      </main>
    </div>);

};

/**
 * MobileCardLayout - Card-based layout for content
 */
export const MobileCardLayout = ({
  children,
  cards = [],
  columns = { mobile: 1, tablet: 2, desktop: 3 },
  gap = 'responsive',
  className,
  cardClassName,
  ...props
}) => {const { t } = useTranslation();
  const { isMobile, isTablet, isDesktop } = useMobile();

  const getColumns = () => {
    if (isMobile) return columns.mobile || 1;
    if (isTablet) return columns.tablet || 2;
    return columns.desktop || 3;
  };

  const getGap = () => {
    if (gap === 'responsive') {
      if (isMobile) return 'gap-4';
      if (isTablet) return 'gap-6';
      return 'gap-8';
    }
    return gap;
  };

  return (
    <div
      className={cn(
        'grid',
        `grid-cols-${getColumns()}`,
        getGap(),
        className
      )}
      {...props}>

      {cards.map((card, index) =>
      <div
        key={card.id || index}
        className={cn(
          'bg-card rounded-lg border shadow-sm',
          cardClassName
        )}>

          {card.content || card}
        </div>
      )}
      {children}
    </div>);

};

/**
 * MobileListLayout - Layout optimized for lists
 */
export const MobileListLayout = ({
  children,
  items = [],
  renderItem,
  emptyState,
  loading = false,
  loadingComponent,
  className,
  itemClassName,
  dividers = true,
  ...props
}) => {const { t } = useTranslation();
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        {loadingComponent ||
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        }
      </div>);

  }

  if (items.length === 0) {
    return emptyState ||
    <div className="flex items-center justify-center p-8 text-muted-foreground">
        <div className="text-center">
          <div className="text-4xl mb-2">📋</div>
          <p>{t("mobile.no_items_to_display")}</p>
        </div>
      </div>;

  }

  return (
    <div className={cn('space-y-0', className)} {...props}>
      {items.map((item, index) =>
      <div key={item.id || index}>
          <div className={cn(
          'p-4',
          itemClassName
        )}>
            {renderItem ? renderItem(item, index) : item}
          </div>
          
          {dividers && index < items.length - 1 &&
        <div className="border-b border-border mx-4" />
        }
        </div>
      )}
      {children}
    </div>);

};

/**
 * MobileFormLayout - Layout for forms with proper spacing and structure
 */
export const MobileFormLayout = ({
  children,
  title,
  description,
  onSubmit,
  submitLabel = 'Submit',
  cancelLabel = 'Cancel',
  onCancel,
  loading = false,
  disabled = false,
  className,
  ...props
}) => {const { t } = useTranslation();
  return (
    <form
      onSubmit={onSubmit}
      className={cn('space-y-6', className)}
      {...props}>

      {/* Form Header */}
      {(title || description) &&
      <div className="space-y-2">
          {title &&
        <h2 className="text-xl font-semibold">{title}</h2>
        }
          {description &&
        <p className="text-muted-foreground">{description}</p>
        }
        </div>
      }

      {/* Form Fields */}
      <div className="space-y-4">
        {children}
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4">
        {onCancel &&
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 px-4 py-2 border border-border rounded-lg text-center font-medium hover:bg-accent transition-colors disabled:opacity-50">

            {cancelLabel}
          </button>
        }
        
        <button
          type="submit"
          disabled={loading || disabled}
          className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-center font-medium hover:bg-primary/90 transition-colors disabled:opacity-50">

          {loading ? 'Loading...' : submitLabel}
        </button>
      </div>
    </form>);

};

export default MobileLayout;