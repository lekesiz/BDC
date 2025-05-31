import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import MobileNav from '../navigation/MobileNav';
import { useBreakpoint } from '@/hooks/useMediaQuery';

/**
 * Main dashboard layout component
 * Contains sidebar, header, main content area, and footer
 */
const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isMobile, isTablet } = useBreakpoint();
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  // Add skip navigation link on mount
  useEffect(() => {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary text-white px-4 py-2 rounded-md z-50';
    skipLink.textContent = 'Skip to main content';
    skipLink.setAttribute('aria-label', 'Skip to main content');
    
    skipLink.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.getElementById('main-content');
      if (target) {
        target.focus();
        target.scrollIntoView();
      }
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    return () => {
      if (skipLink.parentNode) {
        skipLink.parentNode.removeChild(skipLink);
      }
    };
  }, []);
  
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
      
      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header onToggleSidebar={toggleSidebar} />
        
        {/* Main content area */}
        <main 
          id="main-content"
          className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900"
          role="main"
          tabIndex="-1"
          aria-label="Main content"
        >
          {/* Responsive padding based on device */}
          <div className="p-3 sm:p-4 lg:p-6">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </div>
        </main>
        
        {/* Footer - hide on mobile to save space */}
        <div className="hidden sm:block">
          <Footer />
        </div>
        
        {/* Mobile bottom navigation */}
        {(isMobile || isTablet) && <MobileNav />}
      </div>
    </div>
  );
};

export default DashboardLayout;