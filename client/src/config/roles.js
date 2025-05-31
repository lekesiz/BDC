/**
 * Centralized role and permission configuration
 */

// Role constants
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  TENANT_ADMIN: 'tenant_admin', 
  TRAINER: 'trainer',
  STUDENT: 'student',
  TRAINEE: 'trainee' // Alias for student
};

// Role groups for easy access control
export const ROLE_GROUPS = {
  ADMIN: [ROLES.SUPER_ADMIN, ROLES.TENANT_ADMIN],
  MANAGEMENT: [ROLES.SUPER_ADMIN, ROLES.TENANT_ADMIN, ROLES.TRAINER],
  ALL_USERS: [ROLES.SUPER_ADMIN, ROLES.TENANT_ADMIN, ROLES.TRAINER, ROLES.STUDENT],
  STUDENTS: [ROLES.STUDENT, ROLES.TRAINEE]
};

// Permission constants
export const PERMISSIONS = {
  // User management
  MANAGE_USERS: 'manage_users',
  VIEW_USERS: 'view_users',
  CREATE_USERS: 'create_users',
  EDIT_USERS: 'edit_users',
  DELETE_USERS: 'delete_users',
  
  // Beneficiary management
  MANAGE_BENEFICIARIES: 'manage_beneficiaries',
  VIEW_BENEFICIARIES: 'view_beneficiaries',
  CREATE_BENEFICIARIES: 'create_beneficiaries',
  EDIT_BENEFICIARIES: 'edit_beneficiaries',
  ASSIGN_TRAINERS: 'assign_trainers',
  
  // Evaluation system
  MANAGE_EVALUATIONS: 'manage_evaluations',
  CREATE_EVALUATIONS: 'create_evaluations',
  GRADE_EVALUATIONS: 'grade_evaluations',
  VIEW_ALL_RESULTS: 'view_all_results',
  TAKE_EVALUATIONS: 'take_evaluations',
  
  // Documents
  MANAGE_DOCUMENTS: 'manage_documents',
  UPLOAD_DOCUMENTS: 'upload_documents',
  SHARE_DOCUMENTS: 'share_documents',
  VIEW_ALL_DOCUMENTS: 'view_all_documents',
  VIEW_OWN_DOCUMENTS: 'view_own_documents',
  
  // System administration
  MANAGE_TENANTS: 'manage_tenants',
  SYSTEM_CONFIG: 'system_config',
  VIEW_ANALYTICS: 'view_analytics',
  MANAGE_INTEGRATIONS: 'manage_integrations',
  
  // Program management
  MANAGE_PROGRAMS: 'manage_programs',
  ASSIGN_PROGRAMS: 'assign_programs',
  VIEW_PROGRAMS: 'view_programs',
  
  // Calendar and appointments
  MANAGE_CALENDAR: 'manage_calendar',
  SCHEDULE_APPOINTMENTS: 'schedule_appointments',
  VIEW_CALENDAR: 'view_calendar'
};

// Role-based permissions mapping
export const ROLE_PERMISSIONS = {
  [ROLES.SUPER_ADMIN]: [
    // All permissions for super admin
    ...Object.values(PERMISSIONS)
  ],
  
  [ROLES.TENANT_ADMIN]: [
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.CREATE_USERS,
    PERMISSIONS.EDIT_USERS,
    PERMISSIONS.MANAGE_BENEFICIARIES,
    PERMISSIONS.VIEW_BENEFICIARIES,
    PERMISSIONS.CREATE_BENEFICIARIES,
    PERMISSIONS.EDIT_BENEFICIARIES,
    PERMISSIONS.ASSIGN_TRAINERS,
    PERMISSIONS.MANAGE_EVALUATIONS,
    PERMISSIONS.CREATE_EVALUATIONS,
    PERMISSIONS.GRADE_EVALUATIONS,
    PERMISSIONS.VIEW_ALL_RESULTS,
    PERMISSIONS.MANAGE_DOCUMENTS,
    PERMISSIONS.UPLOAD_DOCUMENTS,
    PERMISSIONS.SHARE_DOCUMENTS,
    PERMISSIONS.VIEW_ALL_DOCUMENTS,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.MANAGE_INTEGRATIONS,
    PERMISSIONS.MANAGE_PROGRAMS,
    PERMISSIONS.ASSIGN_PROGRAMS,
    PERMISSIONS.VIEW_PROGRAMS,
    PERMISSIONS.MANAGE_CALENDAR,
    PERMISSIONS.SCHEDULE_APPOINTMENTS,
    PERMISSIONS.VIEW_CALENDAR
  ],
  
  [ROLES.TRAINER]: [
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.MANAGE_BENEFICIARIES,
    PERMISSIONS.VIEW_BENEFICIARIES,
    PERMISSIONS.EDIT_BENEFICIARIES,
    PERMISSIONS.MANAGE_EVALUATIONS,
    PERMISSIONS.CREATE_EVALUATIONS,
    PERMISSIONS.GRADE_EVALUATIONS,
    PERMISSIONS.VIEW_ALL_RESULTS,
    PERMISSIONS.UPLOAD_DOCUMENTS,
    PERMISSIONS.SHARE_DOCUMENTS,
    PERMISSIONS.VIEW_ALL_DOCUMENTS,
    PERMISSIONS.VIEW_PROGRAMS,
    PERMISSIONS.ASSIGN_PROGRAMS,
    PERMISSIONS.SCHEDULE_APPOINTMENTS,
    PERMISSIONS.VIEW_CALENDAR
  ],
  
  [ROLES.STUDENT]: [
    PERMISSIONS.TAKE_EVALUATIONS,
    PERMISSIONS.VIEW_OWN_DOCUMENTS,
    PERMISSIONS.VIEW_PROGRAMS,
    PERMISSIONS.VIEW_CALENDAR
  ],
  
  [ROLES.TRAINEE]: [
    // Same as student
    PERMISSIONS.TAKE_EVALUATIONS,
    PERMISSIONS.VIEW_OWN_DOCUMENTS,
    PERMISSIONS.VIEW_PROGRAMS,
    PERMISSIONS.VIEW_CALENDAR
  ]
};

// Route access configuration
export const ROUTE_ACCESS = {
  // Admin-only routes
  ADMIN_ONLY: {
    roles: ROLE_GROUPS.ADMIN,
    permissions: [PERMISSIONS.SYSTEM_CONFIG]
  },
  
  // Management routes (admin + trainer)
  MANAGEMENT: {
    roles: ROLE_GROUPS.MANAGEMENT,
    permissions: [PERMISSIONS.MANAGE_BENEFICIARIES]
  },
  
  // Student-only routes
  STUDENT_ONLY: {
    roles: ROLE_GROUPS.STUDENTS,
    permissions: [PERMISSIONS.TAKE_EVALUATIONS]
  },
  
  // Common routes (all authenticated users)
  AUTHENTICATED: {
    roles: ROLE_GROUPS.ALL_USERS,
    permissions: []
  }
};

/**
 * Check if user has specific role
 */
export const hasRole = (userRole, requiredRoles) => {
  if (!userRole || !requiredRoles) return false;
  
  if (Array.isArray(requiredRoles)) {
    return requiredRoles.includes(userRole);
  }
  
  return userRole === requiredRoles;
};

/**
 * Check if user has specific permission
 */
export const hasPermission = (userRole, requiredPermission) => {
  if (!userRole || !requiredPermission) return false;
  
  // Super admin has all permissions
  if (userRole === ROLES.SUPER_ADMIN) return true;
  
  const userPermissions = ROLE_PERMISSIONS[userRole] || [];
  return userPermissions.includes(requiredPermission);
};

/**
 * Check if user can access specific route
 */
export const canAccessRoute = (userRole, routeAccess) => {
  if (!userRole || !routeAccess) return false;
  
  const { roles, permissions } = routeAccess;
  
  // Check role access
  if (!hasRole(userRole, roles)) return false;
  
  // Check permission access (if any permissions specified)
  if (permissions && permissions.length > 0) {
    return permissions.some(permission => hasPermission(userRole, permission));
  }
  
  return true;
};

/**
 * Get user permissions by role
 */
export const getUserPermissions = (userRole) => {
  return ROLE_PERMISSIONS[userRole] || [];
};

/**
 * Check if role is admin level
 */
export const isAdmin = (userRole) => {
  return ROLE_GROUPS.ADMIN.includes(userRole);
};

/**
 * Check if role is student level
 */
export const isStudent = (userRole) => {
  return ROLE_GROUPS.STUDENTS.includes(userRole);
};

/**
 * Get role display name
 */
export const getRoleDisplayName = (role) => {
  const displayNames = {
    [ROLES.SUPER_ADMIN]: 'Super Administrator',
    [ROLES.TENANT_ADMIN]: 'Tenant Administrator', 
    [ROLES.TRAINER]: 'Trainer',
    [ROLES.STUDENT]: 'Student',
    [ROLES.TRAINEE]: 'Trainee'
  };
  
  return displayNames[role] || role;
};