// TODO: i18n - processed
import {
  getPortalDashboard,
  getPortalCourses,
  getPortalModuleDetail,
  completeLesson,
  getPortalCalendar,
  downloadResource,
  getSessionDetail,
  getPortalResources,
  getPortalAchievements,
  downloadCertificate,
  getPortalProfile,
  updatePortalProfile,
  getPortalSkills,
  getPortalProgress,
  getPortalNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  updateNotificationSettings } from
'./mockPortalData';
// Import assessment mock API
import { setupAssessmentMockApi } from './assessment/setupAssessmentMockApi';
/**
 * Setup mock API handlers for student portal
 */import { useTranslation } from "react-i18next";
export const setupPortalMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Setup assessment mock API
  setupAssessmentMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Override API methods with mock implementations
  const baseGet = api.get;
  const basePost = api.post;
  const basePut = api.put;
  const baseDelete = api.delete;
  api.get = function (url, config) {
    // Portal Dashboard
    if (url === '/api/portal/dashboard') {
      const dashboard = getPortalDashboard();
      return Promise.resolve({
        data: dashboard,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Courses
    if (url === '/api/portal/courses') {
      const courses = getPortalCourses();
      return Promise.resolve({
        data: courses,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Module Detail
    const moduleMatch = url.match(/^\/api\/portal\/courses\/modules\/(\d+)$/);
    if (moduleMatch) {
      const moduleId = moduleMatch[1];
      const moduleDetail = getPortalModuleDetail(moduleId);
      if (!moduleDetail) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Module not found' }
          }
        });
      }
      return Promise.resolve({
        data: moduleDetail,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Calendar
    if (url.startsWith('/api/portal/calendar')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const month = params.get('month');
      const year = params.get('year');
      const calendar = getPortalCalendar(month, year);
      return Promise.resolve({
        data: calendar,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Session Detail
    const sessionMatch = url.match(/^\/api\/portal\/sessions\/(\d+)$/);
    if (sessionMatch) {
      const sessionId = sessionMatch[1];
      const session = getSessionDetail(sessionId);
      if (!session) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Session not found' }
          }
        });
      }
      return Promise.resolve({
        data: session,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Resources
    if (url === '/api/portal/resources') {
      const resources = getPortalResources();
      return Promise.resolve({
        data: resources,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Achievements
    if (url === '/api/portal/achievements') {
      const achievements = getPortalAchievements();
      return Promise.resolve({
        data: achievements,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Profile
    if (url === '/api/portal/profile') {
      const profile = getPortalProfile();
      return Promise.resolve({
        data: profile,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Skills
    if (url === '/api/portal/skills') {
      const skills = getPortalSkills();
      return Promise.resolve({
        data: skills,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Progress
    if (url === '/api/portal/progress') {
      const progress = getPortalProgress();
      return Promise.resolve({
        data: progress,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Portal Notifications
    if (url.startsWith('/api/portal/notifications')) {
      const queryString = url.split('?')[1] || '';
      const params = new URLSearchParams(queryString);
      const filter = params.get('filter') || 'all';
      const page = parseInt(params.get('page') || '1');
      const limit = parseInt(params.get('limit') || '10');
      const notifications = getPortalNotifications(filter, page, limit);
      return Promise.resolve({
        data: notifications,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Fall back to base get method (which includes assessment endpoints)
    return baseGet(url, config);
  };
  api.post = function (url, data, config) {
    // Complete Lesson
    const completeMatch = url.match(/^\/api\/portal\/lessons\/(\d+)\/complete$/);
    if (completeMatch) {
      const lessonId = completeMatch[1];
      const result = completeLesson(lessonId);
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Download Resource
    const downloadMatch = url.match(/^\/api\/portal\/resources\/(\d+)\/download$/);
    if (downloadMatch) {
      const resourceId = downloadMatch[1];
      const result = downloadResource(resourceId);
      if (!result) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Resource not found' }
          }
        });
      }
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Download Certificate
    const certificateMatch = url.match(/^\/api\/portal\/certificates\/(\d+)\/download$/);
    if (certificateMatch) {
      const certificateId = certificateMatch[1];
      const result = downloadCertificate(certificateId);
      if (!result) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Certificate not found' }
          }
        });
      }
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Mark Notification as Read
    const readMatch = url.match(/^\/api\/portal\/notifications\/(\d+)\/read$/);
    if (readMatch) {
      const notificationId = readMatch[1];
      const result = markNotificationAsRead(notificationId);
      if (!result) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Notification not found' }
          }
        });
      }
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Mark All Notifications as Read
    if (url === '/api/portal/notifications/read-all') {
      const result = markAllNotificationsAsRead();
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Fall back to base post method (which includes assessment endpoints)
    return basePost(url, data, config);
  };
  api.put = function (url, data, config) {
    // Update Profile
    if (url === '/api/portal/profile') {
      const result = updatePortalProfile(data);
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Update Notification Settings
    if (url === '/api/portal/notifications/settings') {
      const result = updateNotificationSettings(data);
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Fall back to base put method
    return basePut(url, data, config);
  };
  api.delete = function (url, config) {
    // Delete Notification
    const deleteMatch = url.match(/^\/api\/portal\/notifications\/(\d+)$/);
    if (deleteMatch) {
      const notificationId = deleteMatch[1];
      const result = deleteNotification(notificationId);
      if (!result) {
        return Promise.reject({
          response: {
            status: 404,
            data: { message: 'Notification not found' }
          }
        });
      }
      return Promise.resolve({
        data: result,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: config
      });
    }
    // Fall back to base delete method
    return baseDelete(url, config);
  };
};