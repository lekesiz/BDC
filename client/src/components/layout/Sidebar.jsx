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
  Menu
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();
  const { user } = useAuth();

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

  // Choose menu items based on user role
  const menuItems = user?.role === 'student' ? studentMenuItems : defaultMenuItems;

  const isActive = (path) => {
    if (path === '/' && user?.role !== 'student') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-200 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0
      `}>
        <div className="flex h-full flex-col">
          {/* Logo/Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b">
            <h2 className="text-xl font-bold text-primary">
              {user?.role === 'student' ? 'Student Portal' : 'BDC Platform'}
            </h2>
            <button
              onClick={toggleSidebar}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <ul className="space-y-1">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.id}>
                    <Link
                      to={item.path}
                      onClick={() => {
                        if (window.innerWidth < 1024) {
                          toggleSidebar();
                        }
                      }}
                      className={`
                        flex items-center gap-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors
                        ${isActive(item.path) ? 'bg-primary text-white hover:bg-primary-dark' : ''}
                      `}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.title}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* User Info */}
          <div className="border-t p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500">{user?.role}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;