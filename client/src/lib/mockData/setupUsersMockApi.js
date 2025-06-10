// TODO: i18n - processed
/**
 * Users Mock API Setup
 */
import { mockUsers, userStats } from './usersMockData.js';import { useTranslation } from "react-i18next";
export const setupUsersMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Store original methods if not provided
  const get = originalGet || api.get;
  const post = originalPost || api.post;
  const put = originalPut || api.put;
  const del = originalDelete || api.delete;
  // GET /api/users - List users with filtering, pagination, search
  api.get = function (url, config) {
    if (url.includes('/api/users') && !url.includes('/api/users/')) {
      return new Promise((resolve) => {
        // Parse query parameters
        const urlObj = new URL(url, 'http://localhost');
        const params = new URLSearchParams(urlObj.search);
        const page = parseInt(params.get('page')) || 1;
        const limit = parseInt(params.get('limit')) || 10;
        const search = params.get('search') || '';
        const role = params.get('role') || '';
        const status = params.get('status') || '';
        const sortBy = params.get('sortBy') || 'firstName';
        const sortOrder = params.get('sortOrder') || 'asc';
        let filteredUsers = [...mockUsers];
        // Apply search filter
        if (search) {
          filteredUsers = filteredUsers.filter((u) =>
          u.firstName.toLowerCase().includes(search.toLowerCase()) ||
          u.lastName.toLowerCase().includes(search.toLowerCase()) ||
          u.email.toLowerCase().includes(search.toLowerCase()) ||
          u.username.toLowerCase().includes(search.toLowerCase())
          );
        }
        // Apply role filter
        if (role) {
          filteredUsers = filteredUsers.filter((u) => u.role === role);
        }
        // Apply status filter  
        if (status) {
          filteredUsers = filteredUsers.filter((u) => u.status === status);
        }
        // Apply sorting
        filteredUsers.sort((a, b) => {
          const aVal = a[sortBy];
          const bVal = b[sortBy];
          if (sortOrder === 'desc') {
            return bVal > aVal ? 1 : -1;
          }
          return aVal > bVal ? 1 : -1;
        });
        // Calculate pagination
        const startIndex = (page - 1) * limit;
        const endIndex = startIndex + limit;
        const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
        // Remove sensitive data
        const sanitizedUsers = paginatedUsers.map((user) => {
          const { ...sanitized } = user;
          return sanitized;
        });
        // Simulate API response delay
        setTimeout(() => {
          resolve({
            data: {
              users: sanitizedUsers,
              pagination: {
                page,
                limit,
                total: filteredUsers.length,
                totalPages: Math.ceil(filteredUsers.length / limit),
                hasNext: endIndex < filteredUsers.length,
                hasPrev: page > 1
              },
              filters: {
                search,
                role,
                status,
                sortBy,
                sortOrder
              },
              stats: userStats
            }
          });
        }, 300);
      });
    }
    // GET /api/users/:id - Get single user
    if (url.match(/\/api\/users\/\d+$/) && !url.includes('?')) {
      const id = parseInt(url.split('/').pop());
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const user = mockUsers.find((u) => u.id === id);
          if (user) {
            resolve({
              data: {
                user: {
                  ...user,
                  // Add additional detailed info for single user view
                  loginHistory: [
                  {
                    id: 1,
                    loginTime: new Date().toISOString(),
                    ip: '192.168.1.100',
                    userAgent: 'Mozilla/5.0...',
                    location: 'Istanbul, Turkey'
                  },
                  {
                    id: 2,
                    loginTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
                    ip: '192.168.1.100',
                    userAgent: 'Mozilla/5.0...',
                    location: 'Istanbul, Turkey'
                  }],

                  activityLog: [
                  {
                    id: 1,
                    action: 'profile_update',
                    timestamp: new Date().toISOString(),
                    description: 'Profile information updated'
                  },
                  {
                    id: 2,
                    action: 'login',
                    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                    description: 'User logged in'
                  }]

                }
              }
            });
          } else {
            reject({
              response: {
                status: 404,
                data: { message: 'User not found' }
              }
            });
          }
        }, 200);
      });
    }
    // GET /api/users/me - Get current user profile (use real backend)
    if (url.includes('/api/users/me')) {
      return get.call(this, url, config);
    }
    // GET /api/users/stats - Get user statistics
    if (url.includes('/api/users/stats')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              ...userStats,
              charts: {
                roleDistribution: Object.entries(userStats.byRole).map(([role, count]) => ({
                  role,
                  count,
                  percentage: Math.round(count / userStats.total * 100)
                })),
                registrationTrend: [
                { month: 'Jan', count: 5 },
                { month: 'Feb', count: 8 },
                { month: 'Mar', count: 12 },
                { month: 'Apr', count: 7 },
                { month: 'May', count: 10 },
                { month: 'Jun', count: 15 }]

              }
            }
          });
        }, 200);
      });
    }
    // Default: call original get method
    return get.call(this, url, config);
  };
  // POST /api/users - Create new user
  api.post = function (url, data, config) {
    if (url === '/api/users') {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          try {
            const newId = Math.max(...mockUsers.map((u) => u.id)) + 1;
            const newUser = {
              id: newId,
              ...data,
              avatar: `https://i.pravatar.cc/150?u=${newId}`,
              joinDate: new Date().toISOString().split('T')[0],
              lastLogin: null,
              status: 'active'
            };
            mockUsers.push(newUser);
            resolve({
              data: {
                user: newUser,
                message: 'User created successfully'
              }
            });
          } catch (error) {
            reject({
              response: {
                status: 400,
                data: { message: 'Invalid user data' }
              }
            });
          }
        }, 500);
      });
    }
    // Default: call original post method
    return post.call(this, url, data, config);
  };
  // PUT /api/users/:id - Update user
  api.put = function (url, data, config) {
    if (url.match(/\/api\/users\/\d+$/)) {
      const id = parseInt(url.split('/').pop());
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = mockUsers.findIndex((u) => u.id === id);
          if (index !== -1) {
            mockUsers[index] = {
              ...mockUsers[index],
              ...data,
              updatedAt: new Date().toISOString()
            };
            resolve({
              data: {
                user: mockUsers[index],
                message: 'User updated successfully'
              }
            });
          } else {
            reject({
              response: {
                status: 404,
                data: { message: 'User not found' }
              }
            });
          }
        }, 400);
      });
    }
    // Default: call original put method
    return put.call(this, url, data, config);
  };
  // DELETE /api/users/:id - Delete user
  api.delete = function (url, config) {
    if (url.match(/\/api\/users\/\d+$/)) {
      const id = parseInt(url.split('/').pop());
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = mockUsers.findIndex((u) => u.id === id);
          if (index !== -1) {
            const deletedUser = mockUsers.splice(index, 1)[0];
            resolve({
              data: {
                message: 'User deleted successfully',
                user: deletedUser
              }
            });
          } else {
            reject({
              response: {
                status: 404,
                data: { message: 'User not found' }
              }
            });
          }
        }, 300);
      });
    }
    // Default: call original delete method
    return del.call(this, url, config);
  };
};