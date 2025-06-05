import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useBreakpoint } from '@/hooks/useMediaQuery';
import RealTimeNotifications from '../notifications/RealTimeNotifications';
import ThemeToggle from '../common/ThemeToggle';
import LanguageSelector from '../common/LanguageSelector';
import { tapTargetClasses } from '@/utils/responsive';
import { 
  Menu, 
  Bell, 
  User, 
  LogOut, 
  Settings, 
  ChevronDown,
  AlignJustify
} from 'lucide-react';
/**
 * Header component for the dashboard layout
 */
const Header = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { isMobile, isTablet } = useBreakpoint();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const toggleUserMenu = () => {
    setUserMenuOpen(!userMenuOpen);
    if (notificationsOpen) setNotificationsOpen(false);
  };
  const toggleNotifications = () => {
    setNotificationsOpen(!notificationsOpen);
    if (userMenuOpen) setUserMenuOpen(false);
  };
  const handleLogout = () => {
    logout();
  };
  // Handle escape key for dropdown menus
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        if (userMenuOpen) setUserMenuOpen(false);
        if (notificationsOpen) setNotificationsOpen(false);
        if (mobileMenuOpen) setMobileMenuOpen(false);
      }
    };
    const handleClickOutside = (e) => {
      if (userMenuOpen || notificationsOpen) {
        const isClickInsideMenu = e.target.closest('[data-dropdown-menu]');
        if (!isClickInsideMenu) {
          setUserMenuOpen(false);
          setNotificationsOpen(false);
        }
      }
    };
    if (userMenuOpen || notificationsOpen || mobileMenuOpen) {
      document.addEventListener('keydown', handleEscape);
      document.addEventListener('click', handleClickOutside);
      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.removeEventListener('click', handleClickOutside);
      };
    }
  }, [userMenuOpen, notificationsOpen, mobileMenuOpen]);
  return (
    <header 
      className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-10 transition-colors"
      role="banner"
    >
      <div className="px-3 sm:px-4 lg:px-6">
        <div className="flex items-center justify-between h-14 sm:h-16">
          {/* Left section */}
          <div className="flex items-center">
            <button
              onClick={onToggleSidebar}
              className={`${tapTargetClasses.medium} flex items-center justify-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary rounded-md lg:hidden`}
              aria-label="Toggle navigation menu"
              aria-expanded="false"
            >
              <AlignJustify className="w-5 h-5 sm:w-6 sm:h-6" aria-hidden="true" />
            </button>
            {/* Logo for mobile */}
            <div className="ml-2 sm:ml-4 lg:hidden">
              <Link 
                to="/" 
                className="text-lg sm:text-xl font-bold text-primary dark:text-primary-light"
                aria-label="BDC Home"
              >
                BDC
              </Link>
            </div>
          </div>
          {/* Right section */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Language selector - hide on small mobile */}
            <div className="hidden xs:block">
              <LanguageSelector />
            </div>
            {/* Theme toggle */}
            <ThemeToggle />
            {/* Real-time notifications */}
            <RealTimeNotifications />
            {/* User dropdown */}
            <div className="relative" data-dropdown-menu>
              <button
                onClick={toggleUserMenu}
                className={`flex items-center space-x-1 sm:space-x-2 ${tapTargetClasses.medium} rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary`}
                aria-label="User menu"
                aria-expanded={userMenuOpen}
                aria-haspopup="true"
              >
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-300">
                  <User className="w-4 h-4 sm:w-5 sm:h-5" aria-hidden="true" />
                </div>
                <span className="hidden lg:inline-block text-sm font-medium text-gray-700 dark:text-gray-200">
                  {user?.first_name} {user?.last_name}
                </span>
                <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4 text-gray-500 dark:text-gray-400 hidden sm:block" aria-hidden="true" />
              </button>
              {userMenuOpen && (
                <div 
                  className="absolute right-0 mt-2 w-56 sm:w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg py-1 z-50"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu-button"
                >
                  <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{user?.first_name} {user?.last_name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                    <p className="text-xs font-medium text-primary dark:text-primary-light mt-1 capitalize">{user?.role}</p>
                  </div>
                  <Link 
                    to="/profile" 
                    className="block px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center"
                    role="menuitem"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <User className="w-4 h-4 mr-3" aria-hidden="true" />
                    Profile
                  </Link>
                  <Link 
                    to="/settings" 
                    className="block px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center"
                    role="menuitem"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <Settings className="w-4 h-4 mr-3" aria-hidden="true" />
                    Settings
                  </Link>
                  {/* Language selector for mobile */}
                  <div className="xs:hidden px-4 py-3 border-t border-gray-200 dark:border-gray-700">
                    <LanguageSelector mobile />
                  </div>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center border-t border-gray-200 dark:border-gray-700"
                    role="menuitem"
                  >
                    <LogOut className="w-4 h-4 mr-3" aria-hidden="true" />
                    Log out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
export default Header;