import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { resourcePreloader, codeSplitter } from '../../utils/pwaOptimizations';
/**
 * Route Preloader Component
 * Preloads routes and their dependencies for faster navigation
 */
export function RoutePreloader({ 
  routes = [],
  preloadOnHover = true,
  preloadOnVisible = true,
  preloadDelay = 100,
  children 
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const hoverTimerRef = useRef(null);
  const preloadedRoutes = useRef(new Set());
  useEffect(() => {
    // Preload current route dependencies
    preloadRoute(location.pathname);
  }, [location.pathname]);
  const preloadRoute = async (routePath) => {
    if (preloadedRoutes.current.has(routePath)) {
      return;
    }
    try {
      // Find route configuration
      const route = routes.find(r => r.path === routePath);
      if (!route) return;
      // Preload route component
      if (route.component) {
        await codeSplitter.preloadModule(route.component);
      }
      // Preload route-specific resources
      await resourcePreloader.preloadRoute(routePath);
      // Preload API endpoints
      if (route.api) {
        await Promise.allSettled(
          route.api.map(endpoint => 
            fetch(endpoint).catch(() => {}) // Ignore errors for preloading
          )
        );
      }
      preloadedRoutes.current.add(routePath);
    } catch (error) {
      console.warn(`Failed to preload route ${routePath}:`, error);
    }
  };
  const handleLinkHover = (href) => {
    if (!preloadOnHover || preloadedRoutes.current.has(href)) {
      return;
    }
    // Clear any existing timer
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
    }
    // Start preload timer
    hoverTimerRef.current = setTimeout(() => {
      preloadRoute(href);
    }, preloadDelay);
  };
  const handleLinkLeave = () => {
    // Cancel preload if user stops hovering
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = null;
    }
  };
  // Enhanced children with preload capabilities
  const enhancedChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      // Check if it's a link-like component
      if (child.props.to || child.props.href) {
        const href = child.props.to || child.props.href;
        return React.cloneElement(child, {
          onMouseEnter: (e) => {
            handleLinkHover(href);
            child.props.onMouseEnter?.(e);
          },
          onMouseLeave: (e) => {
            handleLinkLeave();
            child.props.onMouseLeave?.(e);
          }
        });
      }
    }
    return child;
  });
  return <>{enhancedChildren}</>;
}
/**
 * Link component with built-in preloading
 */
export function PreloadLink({ 
  to, 
  children, 
  preloadOnHover = true,
  preloadOnVisible = false,
  className = '',
  ...props 
}) {
  const navigate = useNavigate();
  const linkRef = useRef(null);
  const hoverTimerRef = useRef(null);
  const hasPreloaded = useRef(false);
  useEffect(() => {
    if (preloadOnVisible && linkRef.current) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting && !hasPreloaded.current) {
              preloadRoute();
            }
          });
        },
        { threshold: 0.1 }
      );
      observer.observe(linkRef.current);
      return () => observer.disconnect();
    }
  }, [preloadOnVisible, to]);
  const preloadRoute = async () => {
    if (hasPreloaded.current) return;
    try {
      await resourcePreloader.preloadRoute(to);
      hasPreloaded.current = true;
    } catch (error) {
      console.warn('Route preload failed:', error);
    }
  };
  const handleMouseEnter = (e) => {
    if (preloadOnHover && !hasPreloaded.current) {
      hoverTimerRef.current = setTimeout(() => {
        preloadRoute();
      }, 100);
    }
    props.onMouseEnter?.(e);
  };
  const handleMouseLeave = (e) => {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
    }
    props.onMouseLeave?.(e);
  };
  const handleClick = (e) => {
    // Ensure route is preloaded before navigation
    if (!hasPreloaded.current) {
      e.preventDefault();
      preloadRoute().then(() => {
        navigate(to);
      });
    }
    props.onClick?.(e);
  };
  return (
    <a
      ref={linkRef}
      href={to}
      className={className}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      {...props}
    >
      {children}
    </a>
  );
}
/**
 * Navigation component with smart preloading
 */
export function SmartNavigation({ 
  routes, 
  currentPath,
  onNavigate,
  className = '' 
}) {
  const preloadAdjacentRoutes = () => {
    const currentIndex = routes.findIndex(route => route.path === currentPath);
    // Preload previous and next routes
    const adjacentIndices = [currentIndex - 1, currentIndex + 1].filter(
      index => index >= 0 && index < routes.length
    );
    adjacentIndices.forEach(index => {
      const route = routes[index];
      setTimeout(() => {
        resourcePreloader.preloadRoute(route.path);
      }, 1000); // Delay to not interfere with current page loading
    });
  };
  useEffect(() => {
    preloadAdjacentRoutes();
  }, [currentPath]);
  return (
    <nav className={className}>
      <RoutePreloader routes={routes}>
        {routes.map((route) => (
          <PreloadLink
            key={route.path}
            to={route.path}
            className={`
              px-4 py-2 rounded-md transition-colors
              ${currentPath === route.path 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }
            `}
            onClick={() => onNavigate?.(route.path)}
          >
            {route.label}
          </PreloadLink>
        ))}
      </RoutePreloader>
    </nav>
  );
}
/**
 * Route transition component with preloading
 */
export function RouteTransition({ 
  children, 
  isLoading = false,
  route,
  onRouteChange 
}) {
  const [isTransitioning, setIsTransitioning] = React.useState(false);
  useEffect(() => {
    if (route) {
      setIsTransitioning(true);
      // Preload next route
      resourcePreloader.preloadRoute(route).finally(() => {
        setIsTransitioning(false);
        onRouteChange?.(route);
      });
    }
  }, [route, onRouteChange]);
  if (isLoading || isTransitioning) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }
  return (
    <div className="animate-in fade-in duration-200">
      {children}
    </div>
  );
}
/**
 * Prefetch on scroll component
 */
export function PrefetchOnScroll({ 
  routes = [],
  threshold = 0.8,
  enabled = true 
}) {
  const hasTriggered = useRef(false);
  useEffect(() => {
    if (!enabled || hasTriggered.current) return;
    const handleScroll = () => {
      const scrollTop = window.pageYOffset;
      const documentHeight = document.documentElement.scrollHeight;
      const windowHeight = window.innerHeight;
      const scrollPercent = scrollTop / (documentHeight - windowHeight);
      if (scrollPercent >= threshold && !hasTriggered.current) {
        hasTriggered.current = true;
        // Prefetch likely next routes
        routes.forEach((route, index) => {
          setTimeout(() => {
            resourcePreloader.preloadRoute(route.path);
          }, index * 100); // Stagger the preloading
        });
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [routes, threshold, enabled]);
  return null; // This component doesn't render anything
}
export default RoutePreloader;