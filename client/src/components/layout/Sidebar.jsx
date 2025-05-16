import { NavLink } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import {
  Home,
  Users,
  ClipboardList,
  FileText,
  BarChart2,
  Settings,
  User,
  Building2,
  X,
  LogOut
} from 'lucide-react';

// Navigation items based on user roles
const getNavItems = (role) => {
  // Common items for all users
  const commonItems = [
    { name: 'Dashboard', path: '/', icon: <Home className="w-5 h-5" /> },
    { name: 'Evaluations', path: '/evaluations', icon: <ClipboardList className="w-5 h-5" /> },
    { name: 'Profile', path: '/profile', icon: <User className="w-5 h-5" /> },
    { name: 'Settings', path: '/settings', icon: <Settings className="w-5 h-5" /> },
  ];
  
  // Role-specific items
  const roleItems = {
    super_admin: [
      { name: 'Users', path: '/admin/users', icon: <Users className="w-5 h-5" /> },
      { name: 'Tenants', path: '/admin/tenants', icon: <Building2 className="w-5 h-5" /> },
      { name: 'Beneficiaries', path: '/beneficiaries', icon: <Users className="w-5 h-5" /> },
      { name: 'Reports', path: '/reports', icon: <BarChart2 className="w-5 h-5" /> },
      { name: 'Documents', path: '/documents', icon: <FileText className="w-5 h-5" /> },
    ],
    tenant_admin: [
      { name: 'Users', path: '/admin/users', icon: <Users className="w-5 h-5" /> },
      { name: 'Beneficiaries', path: '/beneficiaries', icon: <Users className="w-5 h-5" /> },
      { name: 'Reports', path: '/reports', icon: <BarChart2 className="w-5 h-5" /> },
      { name: 'Documents', path: '/documents', icon: <FileText className="w-5 h-5" /> },
    ],
    trainer: [
      { name: 'Beneficiaries', path: '/beneficiaries', icon: <Users className="w-5 h-5" /> },
      { name: 'Documents', path: '/documents', icon: <FileText className="w-5 h-5" /> },
    ],
    student: [
      { name: 'My Evaluations', path: '/my-evaluations', icon: <ClipboardList className="w-5 h-5" /> },
      { name: 'My Documents', path: '/my-documents', icon: <FileText className="w-5 h-5" /> },
    ],
  };
  
  return [...commonItems, ...(roleItems[role] || [])];
};

/**
 * Sidebar component for the dashboard layout
 */
const Sidebar = ({ open, onClose }) => {
  const { user, logout } = useAuth();
  const navItems = getNavItems(user?.role);
  
  const handleLogout = () => {
    logout();
  };
  
  return (
    <>
      {/* Mobile sidebar backdrop */}
      {open && (
        <div 
          className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        ></div>
      )}
      
      {/* Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200 transform ${
          open ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:inset-0 transition-transform duration-300 ease-in-out`}
      >
        {/* Sidebar header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          <NavLink to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-xl">B</span>
            </div>
            <span className="text-xl font-bold text-gray-900">BDC</span>
          </NavLink>
          
          {/* Close button (mobile only) */}
          <button 
            className="lg:hidden text-gray-500 hover:text-gray-700"
            onClick={onClose}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Navigation */}
        <nav className="mt-4 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              {item.icon}
              <span className="ml-3">{item.name}</span>
            </NavLink>
          ))}
        </nav>
        
        {/* Sidebar footer */}
        <div className="absolute bottom-0 w-full border-t border-gray-200 p-4">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
              <User className="w-5 h-5" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-2 py-2 text-sm font-medium text-red-600 rounded-md hover:bg-red-50"
          >
            <LogOut className="w-5 h-5" />
            <span className="ml-3">Log out</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;