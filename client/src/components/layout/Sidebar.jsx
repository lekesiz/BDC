import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home,
  FileText,
  BookOpen,
  Calendar,
  Award,
  User,
  Target,
  BarChart3,
  MessageSquare,
  Bell,
  X,
  Menu,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useBreakpoint, useTouchDevice } from '@/hooks/useMediaQuery';
import { tapTargetClasses } from '@/utils/responsive';
const Sidebar = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();
  const { user } = useAuth();
  const { isMobile, isTablet } = useBreakpoint();
  const isTouch = useTouchDevice();
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  // Student menu items - Portal paths
  const studentMenuItems = [
    { 
      id: 'portal-dashboard', 
      title: 'Dashboard', 
      icon: Home, 
      path: '/portal' 
    },
    { 
      id: 'portal-courses', 
      title: 'My Courses', 
      icon: BookOpen, 
      path: '/portal/courses' 
    },
    { 
      id: 'portal-assessments', 
      title: 'Assessments', 
      icon: FileText, 
      path: '/portal/assessment' 
    },
    { 
      id: 'portal-calendar', 
      title: 'Calendar', 
      icon: Calendar, 
      path: '/portal/calendar' 
    },
    { 
      id: 'portal-progress', 
      title: 'Progress', 
      icon: BarChart3, 
      path: '/portal/progress' 
    },
    { 
      id: 'portal-resources', 
      title: 'Resources', 
      icon: Target, 
      path: '/portal/resources' 
    },
    { 
      id: 'portal-achievements', 
      title: 'Achievements', 
      icon: Award, 
      path: '/portal/achievements' 
    },
    { 
      id: 'portal-profile', 
      title: 'My Profile', 
      icon: User, 
      path: '/portal/profile' 
    },
    { 
      id: 'portal-notifications', 
      title: 'Notifications', 
      icon: Bell, 
      path: '/portal/notifications' 
    },
  ];
  // Admin/Trainer menu items - Dashboard paths
  const defaultMenuItems = [
    { 
      id: 'dashboard', 
      title: 'Dashboard', 
      icon: Home, 
      path: '/' 
    },
    { 
      id: 'beneficiaries', 
      title: 'Beneficiaries', 
      icon: User, 
      path: '/beneficiaries' 
    },
    { 
      id: 'evaluations', 
      title: 'Evaluations', 
      icon: FileText, 
      path: '/evaluations' 
    },
    { 
      id: 'programs', 
      title: 'Programs', 
      icon: BookOpen, 
      path: '/programs' 
    },
    { 
      id: 'calendar', 
      title: 'Calendar', 
      icon: Calendar, 
      path: '/calendar' 
    },
    { 
      id: 'documents', 
      title: 'Documents', 
      icon: FileText, 
      path: '/documents' 
    },
    { 
      id: 'reports', 
      title: 'Reports', 
      icon: BarChart3, 
      path: '/reports' 
    },
    { 
      id: 'messaging', 
      title: 'Messages', 
      icon: MessageSquare, 
      path: '/messaging' 
    },
    { 
      id: 'notifications', 
      title: 'Notifications', 
      icon: Bell, 
      path: '/notifications' 
    },
  ];
  // Choose menu items based on user role with permission filtering
  const menuItems = user?.role === 'student' ? studentMenuItems : defaultMenuItems;
  const isActive = (path) => {
    if (path === '/' && user?.role !== 'student') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };
  // Minimum swipe distance (in px)
  const minSwipeDistance = 50;
  const onTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };
  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };
  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    if (isLeftSwipe && isOpen) {
      toggleSidebar();
    }
  };
  // Close sidebar on route change on mobile
  useEffect(() => {
    if (isMobile && isOpen) {
      toggleSidebar();
    }
  }, [location.pathname]);
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden transition-opacity duration-300"
          onClick={toggleSidebar}
          aria-hidden="true"
        />
      )}
      {/* Sidebar */}
      <aside 
        className={`
          fixed inset-y-0 left-0 z-50 w-64 sm:w-72 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:relative lg:translate-x-0 lg:w-64
        `}
        role="navigation"
        aria-label="Main navigation"
        onTouchStart={isTouch && isMobile ? onTouchStart : undefined}
        onTouchMove={isTouch && isMobile ? onTouchMove : undefined}
        onTouchEnd={isTouch && isMobile ? onTouchEnd : undefined}
      >
        <div className="flex h-full flex-col">
          {/* Logo/Header */}
          <div className="flex h-14 sm:h-16 items-center justify-between px-3 sm:px-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg sm:text-xl font-bold text-primary dark:text-primary-light">
              {user?.role === 'student' ? 'Student Portal' : 'BDC Platform'}
            </h2>
            <button
              onClick={toggleSidebar}
              className={`lg:hidden ${tapTargetClasses.medium} flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary rounded-md`}
              aria-label="Close navigation menu"
            >
              <X className="h-5 w-5 sm:h-6 sm:w-6" aria-hidden="true" />
            </button>
          </div>
          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-3 py-4 sm:p-4" aria-label="Sidebar navigation">
            <ul className="space-y-1" role="list">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.id} role="none">
                    <Link
                      to={item.path}
                      onClick={() => {
                        if (window.innerWidth < 1024) {
                          toggleSidebar();
                        }
                      }}
                      className={`
                        flex items-center gap-3 px-3 py-3 sm:py-2.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${tapTargetClasses.medium}
                        ${isActive(item.path) 
                          ? 'bg-primary text-white hover:bg-primary-dark' 
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }
                      `}
                      aria-current={isActive(item.path) ? 'page' : undefined}
                      role="menuitem"
                    >
                      <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                      <span className="flex-1">{item.title}</span>
                      {isActive(item.path) && (
                        <ChevronRight className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
          {/* User Info */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-3 sm:p-4">
            <div className="flex items-center gap-3">
              <div 
                className="h-10 w-10 rounded-full bg-primary dark:bg-primary-dark flex items-center justify-center text-white flex-shrink-0"
                aria-hidden="true"
              >
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{user?.role}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
export default Sidebar;