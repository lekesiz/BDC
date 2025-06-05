import { 
  generateIntegrationsData, 
  generateIntegrationActivity,
  generateIntegrationStats,
  generateOAuthConfigs 
} from './mockIntegrationsData';
export const setupIntegrationsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };
  // Integration endpoints
  api.get = function(url, ...args) {
    // List all integrations
    if (url === '/api/integrations') {
      const integrationsData = generateIntegrationsData();
      return Promise.resolve({
        status: 200,
        data: {
          integrations: integrationsData.available,
          total: integrationsData.available.length
        }
      });
    }
    // Get specific integration
    if (url.match(/^\/api\/integrations\/[\w-]+$/)) {
      const integrationId = url.split('/').pop();
      const integrationsData = generateIntegrationsData();
      const integration = integrationsData.available.find(i => i.id === integrationId);
      if (integration) {
        return Promise.resolve({
          status: 200,
          data: integration
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Integration not found' }
        });
      }
    }
    // Integration activity
    if (url === '/api/integrations/activity') {
      const activity = generateIntegrationActivity();
      return Promise.resolve({
        status: 200,
        data: {
          activity,
          total: activity.length
        }
      });
    }
    // Integration statistics
    if (url === '/api/integrations/statistics') {
      const stats = generateIntegrationStats();
      return Promise.resolve({
        status: 200,
        data: stats
      });
    }
    // Webhooks list
    if (url === '/api/integrations/webhooks') {
      const integrationsData = generateIntegrationsData();
      return Promise.resolve({
        status: 200,
        data: {
          webhooks: integrationsData.webhooks,
          total: integrationsData.webhooks.length
        }
      });
    }
    // Specific webhook
    if (url.match(/^\/api\/integrations\/webhooks\/\d+$/)) {
      const webhookId = parseInt(url.split('/').pop());
      const integrationsData = generateIntegrationsData();
      const webhook = integrationsData.webhooks.find(w => w.id === webhookId);
      if (webhook) {
        return Promise.resolve({
          status: 200,
          data: webhook
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Webhook not found' }
        });
      }
    }
    // API keys list
    if (url === '/api/integrations/api-keys') {
      const integrationsData = generateIntegrationsData();
      return Promise.resolve({
        status: 200,
        data: {
          apiKeys: integrationsData.apiKeys,
          total: integrationsData.apiKeys.length
        }
      });
    }
    // OAuth configurations
    if (url === '/api/integrations/oauth-configs') {
      const configs = generateOAuthConfigs();
      return Promise.resolve({
        status: 200,
        data: configs
      });
    }
    // Integration settings
    if (url.match(/^\/api\/integrations\/[\w-]+\/settings$/)) {
      const integrationId = url.split('/')[3];
      const integrationsData = generateIntegrationsData();
      const integration = integrationsData.available.find(i => i.id === integrationId);
      if (integration) {
        return Promise.resolve({
          status: 200,
          data: integration.settings
        });
      } else {
        return Promise.resolve({
          status: 404,
          data: { error: 'Integration not found' }
        });
      }
    }
    // Webhook events
    if (url === '/api/integrations/webhook-events') {
      const events = [
        { category: "Enrollment", events: ["enrollment.created", "enrollment.updated", "enrollment.deleted"] },
        { category: "Course", events: ["course.started", "course.completed", "course.abandoned"] },
        { category: "Payment", events: ["payment.success", "payment.failed", "subscription.created", "subscription.cancelled"] },
        { category: "User", events: ["user.created", "user.updated", "user.deleted", "user.login"] },
        { category: "Certificate", events: ["certificate.issued", "certificate.revoked"] }
      ];
      return Promise.resolve({
        status: 200,
        data: events
      });
    }
    // Call original get for other endpoints
    return originalFunctions.get.call(api, url, ...args);
  };
  // Integration POST endpoints
  api.post = function(url, data, ...args) {
    // Connect integration
    if (url.match(/^\/api\/integrations\/[\w-]+\/connect$/)) {
      const integrationId = url.split('/')[3];
      // Simulate OAuth flow
      return Promise.resolve({
        status: 200,
        data: {
          authUrl: `https://oauth.${integrationId}.com/authorize?client_id=xxx&redirect_uri=yyy&state=zzz`,
          state: 'random-state-string'
        }
      });
    }
    // OAuth callback
    if (url.match(/^\/api\/integrations\/[\w-]+\/callback$/)) {
      const integrationId = url.split('/')[3];
      return Promise.resolve({
        status: 200,
        data: {
          connected: true,
          integration: integrationId,
          email: `user@${integrationId}.com`,
          connectedAt: new Date().toISOString()
        }
      });
    }
    // Create webhook
    if (url === '/api/integrations/webhooks') {
      const newWebhook = {
        id: Date.now(),
        ...data,
        active: true,
        createdAt: new Date().toISOString(),
        lastTriggered: null,
        successRate: 0
      };
      return Promise.resolve({
        status: 201,
        data: newWebhook
      });
    }
    // Create API key
    if (url === '/api/integrations/api-keys') {
      const newApiKey = {
        id: Date.now(),
        name: data.name,
        key: `sk_${data.type}_${Math.random().toString(36).substring(2, 15)}`,
        permissions: data.permissions,
        createdAt: new Date().toISOString(),
        lastUsed: null,
        expiresAt: data.expiresAt || null,
        requestCount: 0
      };
      return Promise.resolve({
        status: 201,
        data: newApiKey
      });
    }
    // Test webhook
    if (url.match(/^\/api\/integrations\/webhooks\/\d+\/test$/)) {
      const webhookId = parseInt(url.split('/')[3]);
      return Promise.resolve({
        status: 200,
        data: {
          success: true,
          webhookId,
          response: {
            status: 200,
            body: { message: "Test successful" },
            headers: { "Content-Type": "application/json" }
          },
          timestamp: new Date().toISOString()
        }
      });
    }
    // Sync integration data
    if (url.match(/^\/api\/integrations\/[\w-]+\/sync$/)) {
      const integrationId = url.split('/')[3];
      return Promise.resolve({
        status: 200,
        data: {
          integration: integrationId,
          itemsSynced: Math.floor(Math.random() * 100) + 1,
          lastSync: new Date().toISOString(),
          status: 'success'
        }
      });
    }
    return originalFunctions.post.call(api, url, data, ...args);
  };
  // Integration PUT endpoints
  api.put = function(url, data, ...args) {
    // Update integration settings
    if (url.match(/^\/api\/integrations\/[\w-]+\/settings$/)) {
      const integrationId = url.split('/')[3];
      return Promise.resolve({
        status: 200,
        data: {
          integration: integrationId,
          settings: data,
          updatedAt: new Date().toISOString()
        }
      });
    }
    // Update webhook
    if (url.match(/^\/api\/integrations\/webhooks\/\d+$/)) {
      const webhookId = parseInt(url.split('/').pop());
      const updatedWebhook = {
        ...data,
        id: webhookId,
        updatedAt: new Date().toISOString()
      };
      return Promise.resolve({
        status: 200,
        data: updatedWebhook
      });
    }
    // Toggle webhook status
    if (url.match(/^\/api\/integrations\/webhooks\/\d+\/toggle$/)) {
      const webhookId = parseInt(url.split('/')[3]);
      return Promise.resolve({
        status: 200,
        data: {
          id: webhookId,
          active: data.active,
          updatedAt: new Date().toISOString()
        }
      });
    }
    // Update API key
    if (url.match(/^\/api\/integrations\/api-keys\/\d+$/)) {
      const keyId = parseInt(url.split('/').pop());
      const updatedKey = {
        ...data,
        id: keyId,
        updatedAt: new Date().toISOString()
      };
      return Promise.resolve({
        status: 200,
        data: updatedKey
      });
    }
    // Rotate API key
    if (url.match(/^\/api\/integrations\/api-keys\/\d+\/rotate$/)) {
      const keyId = parseInt(url.split('/')[3]);
      return Promise.resolve({
        status: 200,
        data: {
          id: keyId,
          key: `sk_live_${Math.random().toString(36).substring(2, 15)}`,
          rotatedAt: new Date().toISOString()
        }
      });
    }
    return originalFunctions.put.call(api, url, data, ...args);
  };
  // Integration DELETE endpoints
  api.delete = function(url, ...args) {
    // Disconnect integration
    if (url.match(/^\/api\/integrations\/[\w-]+\/disconnect$/)) {
      const integrationId = url.split('/')[3];
      return Promise.resolve({
        status: 200,
        data: {
          integration: integrationId,
          disconnected: true,
          disconnectedAt: new Date().toISOString()
        }
      });
    }
    // Delete webhook
    if (url.match(/^\/api\/integrations\/webhooks\/\d+$/)) {
      const webhookId = parseInt(url.split('/').pop());
      return Promise.resolve({
        status: 200,
        data: {
          id: webhookId,
          deleted: true
        }
      });
    }
    // Delete API key
    if (url.match(/^\/api\/integrations\/api-keys\/\d+$/)) {
      const keyId = parseInt(url.split('/').pop());
      return Promise.resolve({
        status: 200,
        data: {
          id: keyId,
          deleted: true
        }
      });
    }
    // Clear integration cache
    if (url.match(/^\/api\/integrations\/[\w-]+\/cache$/)) {
      const integrationId = url.split('/')[3];
      return Promise.resolve({
        status: 200,
        data: {
          integration: integrationId,
          cacheCleared: true,
          clearedAt: new Date().toISOString()
        }
      });
    }
    return originalFunctions.delete.call(api, url, ...args);
  };
};