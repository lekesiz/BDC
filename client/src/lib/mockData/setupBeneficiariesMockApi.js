// TODO: i18n - processed
/**
 * Beneficiaries Mock API Setup
 */
import { mockBeneficiaries, beneficiaryStats, generateBeneficiary } from './beneficiariesMockData.js';import { useTranslation } from "react-i18next";
export const setupBeneficiariesMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Store original methods if not provided
  const get = originalGet || api.get;
  const post = originalPost || api.post;
  const put = originalPut || api.put;
  const del = originalDelete || api.delete;
  // GET /api/beneficiaries - List beneficiaries with filtering, pagination, search
  api.get = function (url, config) {
    if (url.includes('/api/beneficiaries') && !url.includes('/api/beneficiaries/')) {
      return new Promise((resolve) => {
        // Parse query parameters
        const urlObj = new URL(url, 'http://localhost');
        const params = new URLSearchParams(urlObj.search);
        const page = parseInt(params.get('page')) || 1;
        const limit = parseInt(params.get('limit')) || 10;
        const search = params.get('search') || '';
        const status = params.get('status') || '';
        const program = params.get('program') || '';
        const city = params.get('city') || '';
        const sortBy = params.get('sortBy') || 'personalInfo.firstName';
        const sortOrder = params.get('sortOrder') || 'asc';
        let filteredBeneficiaries = [...mockBeneficiaries];
        // Apply search filter
        if (search) {
          filteredBeneficiaries = filteredBeneficiaries.filter((b) =>
          b.personalInfo.firstName.toLowerCase().includes(search.toLowerCase()) ||
          b.personalInfo.lastName.toLowerCase().includes(search.toLowerCase()) ||
          b.personalInfo.email.toLowerCase().includes(search.toLowerCase()) ||
          b.personalInfo.phone.includes(search)
          );
        }
        // Apply status filter
        if (status) {
          filteredBeneficiaries = filteredBeneficiaries.filter((b) =>
          b.programInfo.status === status
          );
        }
        // Apply program filter  
        if (program) {
          filteredBeneficiaries = filteredBeneficiaries.filter((b) =>
          b.programInfo.currentProgram === program
          );
        }
        // Apply city filter
        if (city) {
          filteredBeneficiaries = filteredBeneficiaries.filter((b) =>
          b.contactInfo.city === city
          );
        }
        // Apply sorting
        filteredBeneficiaries.sort((a, b) => {
          const getValue = (obj, path) => {
            return path.split('.').reduce((current, key) => current && current[key], obj);
          };
          const aVal = getValue(a, sortBy);
          const bVal = getValue(b, sortBy);
          if (sortOrder === 'desc') {
            return bVal > aVal ? 1 : -1;
          }
          return aVal > bVal ? 1 : -1;
        });
        // Calculate pagination
        const startIndex = (page - 1) * limit;
        const endIndex = startIndex + limit;
        const paginatedBeneficiaries = filteredBeneficiaries.slice(startIndex, endIndex);
        // Simulate API response delay
        setTimeout(() => {
          resolve({
            data: {
              beneficiaries: paginatedBeneficiaries,
              pagination: {
                page,
                limit,
                total: filteredBeneficiaries.length,
                totalPages: Math.ceil(filteredBeneficiaries.length / limit),
                hasNext: endIndex < filteredBeneficiaries.length,
                hasPrev: page > 1
              },
              filters: {
                search,
                status,
                program,
                city,
                sortBy,
                sortOrder
              },
              stats: beneficiaryStats
            }
          });
        }, 300); // 300ms delay to simulate real API
      });
    }
    // GET /api/beneficiaries/:id - Get single beneficiary
    if (url.match(/\/api\/beneficiaries\/\d+$/) && !url.includes('?')) {
      const id = parseInt(url.split('/').pop());
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const beneficiary = mockBeneficiaries.find((b) => b.id === id);
          if (beneficiary) {
            resolve({
              data: {
                beneficiary: {
                  ...beneficiary,
                  // Add additional detailed info for single beneficiary view
                  recentActivities: [
                  {
                    id: 1,
                    date: new Date().toISOString().split('T')[0],
                    type: 'assessment',
                    description: 'Genel Yetenek değerlendirmesi tamamlandı',
                    score: 85
                  },
                  {
                    id: 2,
                    date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    type: 'attendance',
                    description: 'Derse katılım sağlandı',
                    score: null
                  },
                  {
                    id: 3,
                    date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    type: 'document',
                    description: 'CV güncellendi',
                    score: null
                  }],

                  upcomingEvents: [
                  {
                    id: 1,
                    date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
                    type: 'assessment',
                    title: 'Mesleki Bilgi Değerlendirmesi',
                    description: 'Final sınavı'
                  },
                  {
                    id: 2,
                    date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
                    type: 'meeting',
                    title: 'Bireysel Görüşme',
                    description: 'Trainer ile ilerleme değerlendirmesi'
                  }]

                }
              }
            });
          } else {
            reject({
              response: {
                status: 404,
                data: { message: 'Beneficiary not found' }
              }
            });
          }
        }, 200);
      });
    }
    // GET /api/beneficiaries/stats - Get beneficiary statistics
    if (url.includes('/api/beneficiaries/stats')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              ...beneficiaryStats,
              charts: {
                ageDistribution: [
                { range: '18-25', count: mockBeneficiaries.filter((b) => b.personalInfo.age >= 18 && b.personalInfo.age <= 25).length },
                { range: '26-35', count: mockBeneficiaries.filter((b) => b.personalInfo.age >= 26 && b.personalInfo.age <= 35).length },
                { range: '36-45', count: mockBeneficiaries.filter((b) => b.personalInfo.age >= 36 && b.personalInfo.age <= 45).length },
                { range: '46+', count: mockBeneficiaries.filter((b) => b.personalInfo.age >= 46).length }],

                progressDistribution: [
                { range: '0-25%', count: mockBeneficiaries.filter((b) => b.programInfo.progress >= 0 && b.programInfo.progress <= 25).length },
                { range: '26-50%', count: mockBeneficiaries.filter((b) => b.programInfo.progress >= 26 && b.programInfo.progress <= 50).length },
                { range: '51-75%', count: mockBeneficiaries.filter((b) => b.programInfo.progress >= 51 && b.programInfo.progress <= 75).length },
                { range: '76-100%', count: mockBeneficiaries.filter((b) => b.programInfo.progress >= 76).length }]

              }
            }
          });
        }, 200);
      });
    }
    // Default: call original get method
    return get.call(this, url, config);
  };
  // POST /api/beneficiaries - Create new beneficiary
  api.post = function (url, data, config) {
    if (url === '/api/beneficiaries') {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          try {
            const newId = Math.max(...mockBeneficiaries.map((b) => b.id)) + 1;
            const newBeneficiary = {
              id: newId,
              ...data,
              metadata: {
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                lastLogin: null,
                source: 'Website',
                tags: ['Yeni'],
                assignedTrainer: null
              }
            };
            mockBeneficiaries.push(newBeneficiary);
            resolve({
              data: {
                beneficiary: newBeneficiary,
                message: 'Beneficiary created successfully'
              }
            });
          } catch (error) {
            reject({
              response: {
                status: 400,
                data: { message: 'Invalid beneficiary data' }
              }
            });
          }
        }, 500);
      });
    }
    // Default: call original post method
    return post.call(this, url, data, config);
  };
  // PUT /api/beneficiaries/:id - Update beneficiary
  api.put = function (url, data, config) {
    if (url.match(/\/api\/beneficiaries\/\d+$/)) {
      const id = parseInt(url.split('/').pop());
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = mockBeneficiaries.findIndex((b) => b.id === id);
          if (index !== -1) {
            mockBeneficiaries[index] = {
              ...mockBeneficiaries[index],
              ...data,
              metadata: {
                ...mockBeneficiaries[index].metadata,
                updatedAt: new Date().toISOString()
              }
            };
            resolve({
              data: {
                beneficiary: mockBeneficiaries[index],
                message: 'Beneficiary updated successfully'
              }
            });
          } else {
            reject({
              response: {
                status: 404,
                data: { message: 'Beneficiary not found' }
              }
            });
          }
        }, 400);
      });
    }
    // Default: call original put method
    return put.call(this, url, data, config);
  };
  // DELETE /api/beneficiaries/:id - Delete beneficiary
  api.delete = function (url, config) {
    if (url.match(/\/api\/beneficiaries\/\d+$/)) {
      const id = parseInt(url.split('/').pop());
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = mockBeneficiaries.findIndex((b) => b.id === id);
          if (index !== -1) {
            const deletedBeneficiary = mockBeneficiaries.splice(index, 1)[0];
            resolve({
              data: {
                message: 'Beneficiary deleted successfully',
                beneficiary: deletedBeneficiary
              }
            });
          } else {
            reject({
              response: {
                status: 404,
                data: { message: 'Beneficiary not found' }
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