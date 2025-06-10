// TODO: i18n - processed
import {
  getAssessments,
  getAssessmentById,
  getQuizById,
  getAssessmentResult,
  submitQuizResults } from
'./mockData';
/**
 * Setup mock API handlers for assessments
 */import { useTranslation } from "react-i18next";
export const setupAssessmentMockApi = (api, originalGet, originalPost) => {
  // Store original methods
  const baseGet = originalGet || api.get;
  const basePost = originalPost || api.post;
  // Override get method
  api.get = function (url, config) {
    // Get all assessments
    if (url === '/api/portal/assessments') {
      try {
        const assessmentsData = getAssessments();
        return Promise.resolve({
          data: assessmentsData,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config
        });
      } catch (error) {
        return Promise.reject({
          response: {
            status: 500,
            data: { message: error.message }
          }
        });
      }
    }
    // Get assessment by ID
    const assessmentMatch = url.match(/^\/api\/portal\/assessments\/(\d+)$/);
    if (assessmentMatch) {
      const id = assessmentMatch[1];
      try {
        const assessment = getAssessmentById(id);
        if (!assessment) {
          return Promise.reject({
            response: {
              status: 404,
              data: { message: 'Assessment not found' }
            }
          });
        }
        return Promise.resolve({
          data: assessment,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config
        });
      } catch (error) {
        return Promise.reject({
          response: {
            status: 500,
            data: { message: error.message }
          }
        });
      }
    }
    // Get quiz by assessment and quiz ID
    const quizMatch = url.match(/^\/api\/portal\/assessments\/(\d+)\/quiz\/(\d+)$/);
    if (quizMatch) {
      const assessmentId = quizMatch[1];
      const quizId = quizMatch[2];
      try {
        const quiz = getQuizById(assessmentId, quizId);
        if (!quiz) {
          return Promise.reject({
            response: {
              status: 404,
              data: { message: 'Quiz not found' }
            }
          });
        }
        return Promise.resolve({
          data: quiz,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config
        });
      } catch (error) {
        return Promise.reject({
          response: {
            status: 500,
            data: { message: error.message }
          }
        });
      }
    }
    // Get assessment results
    const resultsMatch = url.match(/^\/api\/portal\/assessments\/(\d+)\/results$/);
    if (resultsMatch) {
      const id = resultsMatch[1];
      try {
        const result = getAssessmentResult(id);
        if (!result) {
          return Promise.reject({
            response: {
              status: 404,
              data: { message: 'Assessment result not found' }
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
      } catch (error) {
        return Promise.reject({
          response: {
            status: 500,
            data: { message: error.message }
          }
        });
      }
    }
    // Fall back to original get method
    return baseGet(url, config);
  };
  // Override post method
  api.post = function (url, data, config) {
    // Submit quiz results
    const submitMatch = url.match(/^\/api\/portal\/assessments\/(\d+)\/quiz\/(\d+)\/submit$/);
    if (submitMatch) {
      const assessmentId = submitMatch[1];
      const quizId = submitMatch[2];
      try {
        const result = submitQuizResults(assessmentId, quizId, data);
        return Promise.resolve({
          data: result,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config
        });
      } catch (error) {
        return Promise.reject({
          response: {
            status: 500,
            data: { message: error.message }
          }
        });
      }
    }
    // Fall back to original post method
    return basePost(url, data, config);
  };
};