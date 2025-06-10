// TODO: i18n - processed
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  FileText,
  User,
  BarChart3,
  Menu } from
'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';
/**
 * Mobile bottom navigation component
 * Fixed at the bottom of the screen for easy thumb access
 */import { useTranslation } from "react-i18next";
const MobileNav = () => {const { t } = useTranslation();
  const location = useLocation();
  const { user } = useAuth();
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);
  // Main navigation items (most important)
  const mainNavItems = user?.role === 'student' ? [
  { id: 'portal', title: 'Home', icon: Home, path: '/portal' },
  { id: 'courses', title: 'Courses', icon: FileText, path: '/portal/courses' },
  { id: 'progress', title: 'Progress', icon: BarChart3, path: '/portal/progress' },
  { id: 'profile', title: 'Profile', icon: User, path: '/portal/profile' }] :
  [
  { id: 'dashboard', title: 'Home', icon: Home, path: '/' },
  { id: 'beneficiaries', title: 'Beneficiaries', icon: User, path: '/beneficiaries' },
  { id: 'evaluations', title: 'Evaluations', icon: FileText, path: '/evaluations' },
  { id: 'reports', title: 'Reports', icon: BarChart3, path: '/reports' }];

  const isActive = (path) => {
    if (path === '/' && user?.role !== 'student') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 lg:hidden">
      <div className="grid grid-cols-4 h-16">
        {mainNavItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          return (
            <Link
              key={item.id}
              to={item.path}
              className={cn(
                "flex flex-col items-center justify-center space-y-1 relative",
                "transition-colors duration-200",
                active ?
                "text-primary dark:text-primary-light" :
                "text-gray-500 dark:text-gray-400"
              )}
              aria-current={active ? 'page' : undefined}>

              {active &&
              <div className="absolute top-0 left-0 right-0 h-0.5 bg-primary" />
              }
              <Icon className="h-5 w-5" aria-hidden="true" />
              <span className="text-xs font-medium">{item.title}</span>
            </Link>);

        })}
      </div>
    </nav>);

};
export default MobileNav;