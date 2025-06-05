/**
 * Application constants
 */
// User roles
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  TENANT_ADMIN: 'tenant_admin',
  TRAINER: 'trainer',
  STUDENT: 'student'
};
// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    RESET_REQUEST: '/api/auth/reset-password/request',
    RESET: '/api/auth/reset-password',
    CHANGE_PASSWORD: '/api/auth/change-password',
  },
  USERS: {
    BASE: '/api/users',
    ME: '/api/users/me',
    PROFILE: '/api/users/me/profile',
  },
  BENEFICIARIES: {
    BASE: '/api/beneficiaries',
    NOTES: id => `/api/beneficiaries/${id}/notes`,
    ASSIGN_TRAINER: id => `/api/beneficiaries/${id}/assign-trainer`,
    NOTE: id => `/api/beneficiaries/notes/${id}`,
  },
  EVALUATIONS: {
    BASE: '/api/evaluations',
    DETAIL: id => `/api/evaluations/${id}`,
    QUESTIONS: id => `/api/evaluations/${id}/questions`,
    QUESTION: id => `/api/evaluations/questions/${id}`,
    SESSIONS: '/api/evaluations/sessions',
    SESSION: id => `/api/evaluations/sessions/${id}`,
    RESPONSES: id => `/api/evaluations/sessions/${id}/responses`,
    RESPONSE: id => `/api/evaluations/responses/${id}`,
    FEEDBACK: id => `/api/evaluations/sessions/${id}/feedback`,
  },
  CALENDAR: {
    EVENTS: '/api/calendar/events',
    EVENT: id => `/api/calendar/events/${id}`,
  },
  MESSAGES: {
    THREADS: '/api/messages/threads',
    THREAD: id => `/api/messages/threads/${id}`,
    THREAD_MESSAGES: id => `/api/messages/threads/${id}/messages`,
    MESSAGE: id => `/api/messages/messages/${id}`,
  },
  ANALYTICS: {
    DASHBOARD: '/api/analytics/dashboard',
    BENEFICIARIES: '/api/analytics/beneficiaries',
    TRAINERS: '/api/analytics/trainers',
    PROGRAMS: '/api/analytics/programs',
  },
  REPORTS: {
    RECENT: '/api/reports/recent',
    SAVED: '/api/reports/saved',
    SCHEDULED: '/api/reports/scheduled',
    DOWNLOAD: id => `/api/reports/${id}/download`,
  },
  DOCUMENTS: {
    BASE: '/api/documents',
    DOCUMENT: id => `/api/documents/${id}`,
    FOLDERS: '/api/documents/folders',
    FOLDER: id => `/api/documents/folders/${id}`,
    UPLOAD: '/api/documents/upload',
    DOWNLOAD: id => `/api/documents/${id}/download`,
  },
  NOTIFICATIONS: {
    BASE: '/api/notifications',
    UNREAD_COUNT: '/api/notifications/unread-count',
    MARK_READ: id => `/api/notifications/${id}/read`,
  },
  FOLDERS: {
    BASE: '/api/folders',
    FOLDER: id => `/api/folders/${id}`,
  }
};
// Local storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
};
// App routes
export const ROUTES = {
  // Auth routes
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  // Dashboard routes
  DASHBOARD: '/',
  // User management routes
  USERS: '/admin/users',
  USER_DETAIL: id => `/admin/users/${id}`,
  USER_CREATE: '/admin/users/create',
  // Beneficiary routes
  BENEFICIARIES: '/beneficiaries',
  BENEFICIARY_DETAIL: id => `/beneficiaries/${id}`,
  BENEFICIARY_CREATE: '/beneficiaries/create',
  // Evaluation routes
  EVALUATIONS: '/evaluations',
  EVALUATION_DETAIL: id => `/evaluations/${id}`,
  EVALUATION_CREATE: '/evaluations/create',
  EVALUATION_EDIT: id => `/evaluations/${id}/edit`,
  // Test routes
  TEST_SESSION: id => `/tests/${id}`,
  TEST_RESULTS: id => `/evaluations/${id}/results`,
  // Settings routes
  PROFILE: '/profile',
  SETTINGS: '/settings',
  // Error routes
  UNAUTHORIZED: '/unauthorized',
  NOT_FOUND: '*',
};
// Notification types
export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
};
// Test question types
export const QUESTION_TYPES = {
  MULTIPLE_CHOICE: 'multiple_choice',
  TEXT: 'text',
  TRUE_FALSE: 'true_false',
  MATCHING: 'matching',
  ORDERING: 'ordering',
};
// Test status
export const TEST_STATUS = {
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  ABANDONED: 'abandoned',
};
// Evaluation status
export const EVALUATION_STATUS = {
  DRAFT: 'draft',
  ACTIVE: 'active',
  ARCHIVED: 'archived',
};
// AI Feedback status
export const FEEDBACK_STATUS = {
  DRAFT: 'draft',
  APPROVED: 'approved',
  REJECTED: 'rejected',
};