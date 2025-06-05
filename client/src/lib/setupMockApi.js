import { setupMockApi as setupEvaluationMockApi } from '@/components/evaluation/mockData';
import { setupDocumentsMockApi } from '@/components/document/setupDocumentsMockApi';
import { setupMessagingMockApi } from '@/components/messaging/setupMessagingMockApi';
import { setupProgramAnalyticsMockApi } from '@/components/analytics/setupProgramAnalyticsMockApi';
import { setupBeneficiaryAnalyticsMockApi } from '@/components/analytics/setupBeneficiaryAnalyticsMockApi';
import { setupReportsMockApi } from '@/components/reports/setupReportsMockApi';
import { setupPortalMockApi } from '@/components/portal/setupPortalMockApi';
import { setupAssessmentMockApi } from '@/components/assessment/setupAssessmentMockApi';
import { setupBeneficiaryMockApi } from '@/components/beneficiary/setupBeneficiaryMockApi';
import { setupDashboardMockApi } from '@/components/dashboard/setupDashboardMockApi';
import { setupCalendarMockApi } from '@/components/calendar/setupCalendarMockApi';
import { setupProgramsMockApi } from '@/components/programs/setupProgramsMockApi';
import { setupSettingsMockApi } from '@/components/settings/setupSettingsMockApi';
import { setupAIMockApi } from '@/components/ai/setupAIMockApi';
import { setupIntegrationsMockApi } from '@/components/integrations/setupIntegrationsMockApi';
import { setupComplianceMockApi } from '@/components/compliance/setupComplianceMockApi';
import { setupNotificationsMockApi } from '@/components/notifications/setupNotificationsMockApi';
import { setupAnalyticsMockApi } from '@/components/analytics/setupAnalyticsMockApi';
import { setupAISettingsMockApi } from '@/components/settings/setupAISettingsMockApi';
import { setupBeneficiariesMockApi } from '@/lib/mockData/setupBeneficiariesMockApi';
import { setupUsersMockApi } from '@/lib/mockData/setupUsersMockApi';
import { setupAuthMockApi } from '@/lib/mockData/setupAuthMockApi';
import { setupQuickMockAPIs } from '@/lib/mockData/quickMockData';
// This function sets up all mock API handlers
export const setupMockApi = (api) => {
  // Store the original methods
  const originalGet = api.get;
  const originalPost = api.post;
  const originalPut = api.put;
  const originalDelete = api.delete;
  // Set up auth mock API first (important: do this before other setups)
  setupAuthMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Create a hybrid approach: some endpoints use mock, others can use real backend
  const hybridGet = (url, config) => {
    // Auth endpoints are now handled by mock API above
    return api.get.call(api, url, config);
  };
  const hybridPost = (url, data, config) => {
    // Auth endpoints are now handled by mock API above
    return api.post.call(api, url, data, config);
  };
  const hybridPut = (url, data, config) => {
    // Auth endpoints are now handled by mock API above
    return api.put.call(api, url, data, config);
  };
  const hybridDelete = (url, config) => {
    // Auth endpoints are now handled by mock API above
    return api.delete.call(api, url, config);
  };
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
  // Set up beneficiary details mock API
  setupBeneficiaryMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up comprehensive beneficiaries mock API
  setupBeneficiariesMockApi(api, hybridGet, hybridPost, hybridPut, hybridDelete);
  // Set up users mock API  
  setupUsersMockApi(api, hybridGet, hybridPost, hybridPut, hybridDelete);
  // Set up dashboard mock API
  setupDashboardMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up calendar/appointments mock API
  setupCalendarMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up programs mock API
  setupProgramsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up settings mock API
  setupSettingsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up AI features mock API
  setupAIMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up integrations mock API
  setupIntegrationsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up compliance mock API
  setupComplianceMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up notifications mock API
  setupNotificationsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up analytics mock API
  setupAnalyticsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up AI settings mock API
  setupAISettingsMockApi(api, originalGet, originalPost, originalPut, originalDelete);
  // Set up quick mock APIs for remaining components
  setupQuickMockAPIs(api, hybridGet, hybridPost, hybridPut, hybridDelete);
};