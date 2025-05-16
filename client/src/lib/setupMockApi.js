import { setupMockApi as setupEvaluationMockApi } from '@/components/evaluation/mockData';
import { setupDocumentsMockApi } from '@/components/document/setupDocumentsMockApi';
import { setupMessagingMockApi } from '@/components/messaging/setupMessagingMockApi';
import { setupProgramAnalyticsMockApi } from '@/components/analytics/setupProgramAnalyticsMockApi';
import { setupBeneficiaryAnalyticsMockApi } from '@/components/analytics/setupBeneficiaryAnalyticsMockApi';
import { setupReportsMockApi } from '@/components/reports/setupReportsMockApi';
import { setupPortalMockApi } from '@/components/portal/setupPortalMockApi';
import { setupAssessmentMockApi } from '@/components/assessment/setupAssessmentMockApi';

// This function sets up all mock API handlers
export const setupMockApi = (api) => {
  // Store the original methods
  const originalGet = api.get;
  const originalPost = api.post;
  const originalPut = api.put;
  const originalDelete = api.delete;
  
  // Set up evaluation mock API
  setupEvaluationMockApi(api);
  
  // Set up documents mock API
  setupDocumentsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  
  // Set up messaging and notifications mock API
  setupMessagingMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  
  // Set up program analytics mock API
  setupProgramAnalyticsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  
  // Set up beneficiary analytics mock API
  setupBeneficiaryAnalyticsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  
  // Set up reports mock API
  setupReportsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  
  // Set up portal mock API (includes portal assessment mock API)
  setupPortalMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  
  // Set up trainer assessment mock API
  setupAssessmentMockApi(api, originalGet, originalPost, originalPut, originalDelete);
};