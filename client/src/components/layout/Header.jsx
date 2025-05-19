import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import RealTimeNotifications from '../notifications/RealTimeNotifications';
import ThemeToggle from '../common/ThemeToggle';
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
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  
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
  
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-10 transition-colors">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left section */}
          <div className="flex items-center">
            <button
              onClick={onToggleSidebar}
              className="text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary lg:hidden"
            >
              <AlignJustify className="w-6 h-6" />
            </button>
            
            {/* Logo for mobile */}
            <div className="ml-4 lg:hidden">
              <Link to="/" className="text-xl font-bold text-primary">BDC</Link>
            </div>
          </div>
          
          {/* Right section */}
          <div className="flex items-center space-x-4">
            {/* Theme toggle */}
            <ThemeToggle />
            
            {/* Real-time notifications */}
            <RealTimeNotifications />
            
            {/* User dropdown */}
            <div className="relative">
              <button
                onClick={toggleUserMenu}
                className="flex items-center space-x-2 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
                  <User className="w-5 h-5" />
                </div>
                <span className="hidden md:inline-block text-sm font-medium text-gray-700">
                  {user?.first_name} {user?.last_name}
                </span>
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </button>
              
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg py-1 z-10">
                  <div className="px-4 py-2 border-b border-gray-200">
                    <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                    <p className="text-xs font-medium text-primary mt-1 capitalize">{user?.role}</p>
                  </div>
                  <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
                    <User className="w-4 h-4 mr-2" />
                    Profile
                  </Link>
                  <Link to="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
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