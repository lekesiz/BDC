/**
 * setupAssessmentMockApi.js
 * 
 * This file sets up mock API handlers for the assessment management system.
 * It provides Axios interceptors for the trainer-facing assessment functionality.
 */
import { 
  getAssessmentTemplates,
  getAssessmentTemplateById,
  createAssessmentTemplate,
  updateAssessmentTemplate,
  getAssignedAssessments,
  getAssignedAssessmentById,
  assignAssessment,
  getSubmissionsByAssessment,
  getSubmissionById,
  gradeSubmission,
  getAssessmentAnalytics,
  getAssessmentAnalyticsByAssessment,
  getAssessmentAnalyticsByCohort
} from './mockData';
import { statisticsEndpoints } from './assessmentStatsMockData';

export const setupAssessmentMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Templates
  
  // Get all assessment templates
  api.get = async function(url, config) {
    if (url === '/api/assessment/templates' || url.startsWith('/api/assessment/templates?')) {
      try {
        // Extract status from query parameters if present
        let status = null;
        if (url.includes('?status=')) {
          status = url.split('?status=')[1];
        }
        
        const templates = await getAssessmentTemplates(status);
        return {
          data: templates,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Get assessment template by ID
    if (url.match(/\/api\/assessment\/templates\/[^/?]+$/)) {
      try {
        const id = url.split('/api/assessment/templates/')[1];
        const template = await getAssessmentTemplateById(id);
        return {
          data: template,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: 'Assessment template not found' },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Assigned Assessments
    
    // Get all assigned assessments
    if (url === '/api/assessment/assigned' || url.startsWith('/api/assessment/assigned?')) {
      try {
        // Extract status from query parameters if present
        let status = null;
        if (url.includes('?status=')) {
          status = url.split('?status=')[1];
        }
        
        const assessments = await getAssignedAssessments(status);
        return {
          data: assessments,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Get assigned assessment by ID
    if (url.match(/\/api\/assessment\/assigned\/[^/?]+$/)) {
      try {
        const id = url.split('/api/assessment/assigned/')[1];
        const assessment = await getAssignedAssessmentById(id);
        return {
          data: assessment,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: 'Assigned assessment not found' },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Get submissions for an assessment
    if (url.match(/\/api\/assessment\/assigned\/[^/?]+\/submissions$/)) {
      try {
        const id = url.split('/api/assessment/assigned/')[1].split('/submissions')[0];
        const submissions = await getSubmissionsByAssessment(id);
        return {
          data: submissions,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Get submission by ID
    if (url.match(/\/api\/assessment\/submissions\/[^/?]+$/)) {
      try {
        const id = url.split('/api/assessment/submissions/')[1];
        const submission = await getSubmissionById(id);
        return {
          data: submission,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: 'Submission not found' },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Analytics
    
    // Get overall assessment analytics
    if (url === '/api/assessment/analytics') {
      try {
        const analytics = await getAssessmentAnalytics();
        return {
          data: analytics,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Get assessment-specific analytics
    if (url.match(/\/api\/assessment\/analytics\/assignments\/[^/?]+$/)) {
      try {
        const id = url.split('/api/assessment/analytics/assignments/')[1];
        const analytics = await getAssessmentAnalyticsByAssessment(id);
        return {
          data: analytics,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: 'Assessment analytics not found' },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Get cohort-specific analytics
    if (url.match(/\/api\/assessment\/analytics\/cohorts\/[^/?]+$/)) {
      try {
        const id = url.split('/api/assessment/analytics/cohorts/')[1];
        const analytics = await getAssessmentAnalyticsByCohort(id);
        return {
          data: analytics,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: 'Cohort analytics not found' },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Statistics endpoints
    if (url === '/api/assessment/statistics/overview' || url.startsWith('/api/assessment/statistics/overview?')) {
      try {
        const response = statisticsEndpoints.overview({ url });
        const data = await response.json();
        return {
          data: data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    if (url === '/api/assessment/statistics/performance' || url.startsWith('/api/assessment/statistics/performance?')) {
      try {
        const response = statisticsEndpoints.performance({ url });
        const data = await response.json();
        return {
          data: data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    if (url === '/api/assessment/statistics/completion' || url.startsWith('/api/assessment/statistics/completion?')) {
      try {
        const response = statisticsEndpoints.completion({ url });
        const data = await response.json();
        return {
          data: data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    if (url === '/api/assessment/statistics/assessments' || url.startsWith('/api/assessment/statistics/assessments?')) {
      try {
        const response = statisticsEndpoints.assessments({ url });
        const data = await response.json();
        return {
          data: data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    if (url === '/api/assessment/statistics/students' || url.startsWith('/api/assessment/statistics/students?')) {
      try {
        const response = statisticsEndpoints.students({ url });
        const data = await response.json();
        return {
          data: data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    if (url === '/api/assessment/statistics/questions' || url.startsWith('/api/assessment/statistics/questions?')) {
      try {
        const response = statisticsEndpoints.questions({ url });
        const data = await response.json();
        return {
          data: data,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Pass through to original GET method if not handled
    return originalGet.apply(this, [url, config]);
  };
  
  // POST Requests
  api.post = async function(url, data, config) {
    // Create assessment template
    if (url === '/api/assessment/templates') {
      try {
        const newTemplate = await createAssessmentTemplate(data);
        return {
          data: newTemplate,
          status: 201,
          statusText: 'Created',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Assign assessment
    if (url === '/api/assessment/assign') {
      try {
        const newAssignment = await assignAssessment(data);
        return {
          data: newAssignment,
          status: 201,
          statusText: 'Created',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 500,
            statusText: 'Server Error',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Grade submission
    if (url.match(/\/api\/assessment\/submissions\/[^/?]+\/grade$/)) {
      try {
        const id = url.split('/api/assessment/submissions/')[1].split('/grade')[0];
        const gradedSubmission = await gradeSubmission(id, data);
        return {
          data: gradedSubmission,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Pass through to original POST method if not handled
    return originalPost.apply(this, [url, data, config]);
  };
  
  // PUT Requests
  api.put = async function(url, data, config) {
    // Update assessment template
    if (url.match(/\/api\/assessment\/templates\/[^/?]+$/)) {
      try {
        const id = url.split('/api/assessment/templates/')[1];
        const updatedTemplate = await updateAssessmentTemplate(id, data);
        return {
          data: updatedTemplate,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
          request: {}
        };
      } catch (error) {
        return Promise.reject({
          response: {
            data: { message: error.message },
            status: 404,
            statusText: 'Not Found',
            headers: {},
            config: config,
            request: {}
          }
        });
      }
    }
    
    // Pass through to original PUT method if not handled
    return originalPut.apply(this, [url, data, config]);
  };
  
  // Leave DELETE as is, we're not handling it for now
};

export default setupAssessmentMockApi;