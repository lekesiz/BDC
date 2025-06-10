import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Menu, 
  X, 
  Home,
  Users,
  Calendar,
  FileText,
  ClipboardList,
  BarChart3,
  Settings,
  LogOut,
  ChevronRight,
  Search
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export const MobileMenu = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  // Close menu on route change
  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Beneficiaries', href: '/beneficiaries', icon: Users },
    { name: 'Appointments', href: '/appointments', icon: Calendar },
    { name: 'Evaluations', href: '/evaluations', icon: ClipboardList },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (path) => {
    return location.pathname === path || 
      (path !== '/' && location.pathname.startsWith(path));
  };

  return (
    <>
      {/* Menu Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden p-2 rounded-md hover:bg-gray-100"
        aria-label="Toggle menu"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <Menu className="h-6 w-6" />
        )}
      </button>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
              onClick={() => setIsOpen(false)}
            />

            {/* Menu Panel */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="fixed top-0 left-0 bottom-0 z-50 w-80 max-w-[85vw] bg-white shadow-xl lg:hidden"
            >
              <div className="flex flex-col h-full">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b">
                  <h2 className="text-xl font-semibold text-primary">BDC Platform</h2>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 rounded-md hover:bg-gray-100"
                    aria-label="Close menu"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {/* Search Bar */}
                <div className="p-4 border-b">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search..."
                      className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto p-4">
                  <ul className="space-y-1">
                    {navigation.map((item) => {
                      const Icon = item.icon;
                      const active = isActive(item.href);
                      
                      return (
                        <li key={item.name}>
                          <Link
                            to={item.href}
                            className={cn(
                              "flex items-center justify-between px-4 py-3 rounded-lg transition-colors",
                              active 
                                ? "bg-primary text-white" 
                                : "text-gray-700 hover:bg-gray-100"
                            )}
                          >
                            <div className="flex items-center">
                              <Icon className={cn(
                                "h-5 w-5 mr-3",
                                active ? "text-white" : "text-gray-400"
                              )} />
                              <span className="font-medium">{item.name}</span>
                            </div>
                            <ChevronRight className={cn(
                              "h-4 w-4",
                              active ? "text-white" : "text-gray-400"
                            )} />
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </nav>

                {/* User Section */}
                <div className="border-t p-4">
                  <div className="flex items-center mb-4">
                    <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
                      </span>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                    </div>
                  </div>
                  
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={onLogout}
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign out
                  </Button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

/**
 * Bottom navigation for mobile devices
 */
export const BottomNavigation = ({ className }) => {
  const location = useLocation();
  
  const navItems = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Beneficiaries', href: '/beneficiaries', icon: Users },
    { name: 'Calendar', href: '/appointments', icon: Calendar },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'More', href: '/settings', icon: Menu },
  ];

  const isActive = (path) => {
    return location.pathname === path || 
      (path !== '/' && location.pathname.startsWith(path));
  };

  return (
    <nav className={cn(
      "fixed bottom-0 left-0 right-0 bg-white border-t z-30 lg:hidden",
      className
    )}>
      <div className="grid grid-cols-5 h-16">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex flex-col items-center justify-center space-y-1",
                active ? "text-primary" : "text-gray-500"
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="text-xs">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};