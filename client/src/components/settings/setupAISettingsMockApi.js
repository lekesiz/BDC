export const setupAISettingsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const originalFunctions = {
    get: originalGet || api.get.bind(api),
    post: originalPost || api.post.bind(api),
    put: originalPut || api.put.bind(api),
    delete: originalDelete || api.delete.bind(api)
  };

  // Mock AI settings data
  const mockAISettings = {
    providers: {
      openai: {
        enabled: false,
        apiKey: '',
        model: 'gpt-4',
        temperature: 0.7,
        maxTokens: 1000
      },
      anthropic: {
        enabled: false,
        apiKey: '',
        model: 'claude-3-opus',
        temperature: 0.7,
        maxTokens: 1000
      },
      google: {
        enabled: false,
        apiKey: '',
        model: 'gemini-pro',
        temperature: 0.7,
        maxTokens: 1000
      },
      huggingface: {
        enabled: false,
        apiKey: '',
        model: '',
        endpoint: ''
      }
    },
    customEndpoints: [],
    features: {
      evaluation_analysis: true,
      recommendations: true,
      content_generation: false,
      chatbot: false
    }
  };

  // Intercept GET requests
  api.get = function(url, ...args) {
    // Get AI settings
    if (url === '/api/settings/ai') {
      console.log('Mock API: Get AI settings');
      return Promise.resolve({
        status: 200,
        data: mockAISettings
      });
    }

    // Pass through to original function for other routes
    return originalFunctions.get.call(this, url, ...args);
  };

  // Intercept PUT requests
  api.put = function(url, data, ...args) {
    // Update AI settings
    if (url === '/api/settings/ai') {
      console.log('Mock API: Update AI settings', data);
      
      // Update mock data
      if (data.providers) {
        Object.assign(mockAISettings.providers, data.providers);
      }
      if (data.customEndpoints) {
        mockAISettings.customEndpoints = data.customEndpoints;
      }
      if (data.features) {
        Object.assign(mockAISettings.features, data.features);
      }
      
      return Promise.resolve({
        status: 200,
        data: {
          message: 'AI settings updated successfully',
          ...mockAISettings
        }
      });
    }

    // Pass through to original function for other routes
    return originalFunctions.put.call(this, url, data, ...args);
  };

  // Intercept POST requests
  api.post = function(url, data, ...args) {
    // Test AI provider connection
    if (url === '/api/settings/ai/test') {
      console.log('Mock API: Test AI provider connection', data);
      
      const { provider, config } = data;
      
      // Simulate API key validation
      if (!config.apiKey) {
        return Promise.reject({
          response: {
            status: 400,
            data: {
              error: 'invalid_api_key',
              message: 'API key is required'
            }
          }
        });
      }
      
      // Simulate successful connection for valid keys
      if (config.apiKey.startsWith('sk-') || config.apiKey.startsWith('AIza')) {
        return Promise.resolve({
          status: 200,
          data: {
            success: true,
            message: `Successfully connected to ${provider}`,
            details: {
              model: config.model,
              available_models: provider === 'openai' 
                ? ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
                : provider === 'anthropic'
                ? ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
                : ['gemini-pro', 'gemini-pro-vision']
            }
          }
        });
      }
      
      // Simulate invalid API key
      return Promise.reject({
        response: {
          status: 401,
          data: {
            error: 'authentication_failed',
            message: 'Invalid API key'
          }
        }
      });
    }

    // Pass through to original function for other routes
    return originalFunctions.post.call(this, url, data, ...args);
  };
};