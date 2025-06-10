import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Brain,
  Key,
  Save,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle,
  Info,
  ExternalLink,
  Plus,
  Trash2,
  Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAsync } from '@/hooks/useAsync';
import AsyncBoundary from '@/components/common/AsyncBoundary';
import { CardLoader } from '@/components/common/LoadingStates';
import api from '@/lib/api';
const AISettingsPage = () => {
  const { t } = useTranslation();
  const { addToast } = useToast();
  // State for AI providers and their settings
  const [aiProviders, setAiProviders] = useState({
    openai: {
      enabled: false,
      apiKey: '',
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 1000,
      showKey: false
    },
    anthropic: {
      enabled: false,
      apiKey: '',
      model: 'claude-3-opus',
      temperature: 0.7,
      maxTokens: 1000,
      showKey: false
    },
    google: {
      enabled: false,
      apiKey: '',
      model: 'gemini-pro',
      temperature: 0.7,
      maxTokens: 1000,
      showKey: false
    },
    huggingface: {
      enabled: false,
      apiKey: '',
      model: '',
      endpoint: '',
      showKey: false
    }
  });
  // Custom endpoints for specific AI features
  const [customEndpoints, setCustomEndpoints] = useState([]);
  const [newEndpoint, setNewEndpoint] = useState({ name: '', url: '', apiKey: '' });
  // Load settings
  const settingsAsync = useAsync(async () => {
    const response = await api.get('/api/settings/ai');
    return response.data;
  }, [], true);
  // Apply loaded settings
  useEffect(() => {
    if (settingsAsync.data) {
      setAiProviders(settingsAsync.data.providers || aiProviders);
      setCustomEndpoints(settingsAsync.data.customEndpoints || []);
    }
  }, [settingsAsync.data]);
  // Save settings
  const handleSave = async () => {
    try {
      // Mask API keys before sending
      const maskedProviders = Object.entries(aiProviders).reduce((acc, [key, value]) => {
        acc[key] = {
          ...value,
          apiKey: value.apiKey ? maskApiKey(value.apiKey) : ''
        };
        return acc;
      }, {});
      const response = await api.put('/api/settings/ai', {
        providers: aiProviders,
        customEndpoints
      });
      addToast({
        type: 'success',
        title: t('settings.messages.saveSuccess'),
        message: t('settings.ai.messages.saveSuccess')
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: t('common.error'),
        message: error.response?.data?.message || t('settings.ai.messages.saveFailed')
      });
    }
  };
  // Test API connection
  const testConnection = async (provider) => {
    try {
      const response = await api.post('/api/settings/ai/test', {
        provider,
        config: aiProviders[provider]
      });
      addToast({
        type: 'success',
        title: t('common.success'),
        message: t('settings.ai.messages.connectionSuccess', { provider })
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: t('common.error'),
        message: error.response?.data?.message || t('settings.ai.messages.connectionFailed', { provider })
      });
    }
  };
  // Toggle API key visibility
  const toggleKeyVisibility = (provider) => {
    setAiProviders(prev => ({
      ...prev,
      [provider]: {
        ...prev[provider],
        showKey: !prev[provider].showKey
      }
    }));
  };
  // Update provider settings
  const updateProvider = (provider, field, value) => {
    setAiProviders(prev => ({
      ...prev,
      [provider]: {
        ...prev[provider],
        [field]: value
      }
    }));
  };
  // Add custom endpoint
  const addCustomEndpoint = () => {
    if (newEndpoint.name && newEndpoint.url) {
      setCustomEndpoints(prev => [...prev, { ...newEndpoint, id: Date.now() }]);
      setNewEndpoint({ name: '', url: '', apiKey: '' });
    }
  };
  // Remove custom endpoint
  const removeCustomEndpoint = (id) => {
    setCustomEndpoints(prev => prev.filter(endpoint => endpoint.id !== id));
  };
  // Mask API key for display
  const maskApiKey = (key) => {
    if (!key) return '';
    const visibleChars = 4;
    if (key.length <= visibleChars * 2) return key;
    return key.substring(0, visibleChars) + '...' + key.substring(key.length - visibleChars);
  };
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('settings.ai.title')}</h1>
        <p className="mt-1 text-sm text-gray-700">
          {t('settings.ai.subtitle')}
        </p>
      </div>
      <AsyncBoundary
        loading={settingsAsync.loading}
        error={settingsAsync.error}
        loadingComponent={<CardLoader />}
      >
        {/* AI Providers */}
        <div className="space-y-6">
          {/* OpenAI */}
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Brain className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{t('settings.ai.providers.openai.name')}</h3>
                    <p className="text-sm text-gray-500">{t('settings.ai.providers.openai.description')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={aiProviders.openai.enabled}
                      onChange={(e) => updateProvider('openai', 'enabled', e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
              {aiProviders.openai.enabled && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('settings.ai.providers.openai.apiKey')}
                    </label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          type={aiProviders.openai.showKey ? 'text' : 'password'}
                          value={aiProviders.openai.apiKey}
                          onChange={(e) => updateProvider('openai', 'apiKey', e.target.value)}
                          placeholder={t('settings.ai.providers.openai.apiKeyPlaceholder')}
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => toggleKeyVisibility('openai')}
                          className="absolute inset-y-0 right-0 px-3 flex items-center"
                        >
                          {aiProviders.openai.showKey ? (
                            <EyeOff className="h-4 w-4 text-gray-400" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => testConnection('openai')}
                      >
                        {t('settings.ai.actions.test')}
                      </Button>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      {t('settings.ai.providers.openai.getApiKey')}{' '}
                      <a
                        href="https://platform.openai.com/api-keys"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline inline-flex items-center gap-1"
                      >
                        {t('settings.ai.providers.openai.platform')}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('settings.ai.providers.openai.model')}
                      </label>
                      <select
                        value={aiProviders.openai.model}
                        onChange={(e) => updateProvider('openai', 'model', e.target.value)}
                        className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                      >
                        <option value="gpt-4">{t('settings.ai.providers.openai.models.gpt4')}</option>
                        <option value="gpt-4-turbo">{t('settings.ai.providers.openai.models.gpt4Turbo')}</option>
                        <option value="gpt-3.5-turbo">{t('settings.ai.providers.openai.models.gpt35Turbo')}</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('settings.ai.providers.openai.temperature')}
                      </label>
                      <Input
                        type="number"
                        min="0"
                        max="2"
                        step="0.1"
                        value={aiProviders.openai.temperature}
                        onChange={(e) => updateProvider('openai', 'temperature', parseFloat(e.target.value))}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('settings.ai.providers.openai.maxTokens')}
                    </label>
                    <Input
                      type="number"
                      min="1"
                      max="4000"
                      value={aiProviders.openai.maxTokens}
                      onChange={(e) => updateProvider('openai', 'maxTokens', parseInt(e.target.value))}
                    />
                  </div>
                </div>
              )}
            </div>
          </Card>
          {/* Anthropic Claude */}
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Brain className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{t('settings.ai.providers.anthropic.name')}</h3>
                    <p className="text-sm text-gray-500">{t('settings.ai.providers.anthropic.description')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={aiProviders.anthropic.enabled}
                      onChange={(e) => updateProvider('anthropic', 'enabled', e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
              {aiProviders.anthropic.enabled && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('settings.ai.providers.anthropic.apiKey')}
                    </label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          type={aiProviders.anthropic.showKey ? 'text' : 'password'}
                          value={aiProviders.anthropic.apiKey}
                          onChange={(e) => updateProvider('anthropic', 'apiKey', e.target.value)}
                          placeholder={t('settings.ai.providers.anthropic.apiKeyPlaceholder')}
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => toggleKeyVisibility('anthropic')}
                          className="absolute inset-y-0 right-0 px-3 flex items-center"
                        >
                          {aiProviders.anthropic.showKey ? (
                            <EyeOff className="h-4 w-4 text-gray-400" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => testConnection('anthropic')}
                      >
                        {t('settings.ai.actions.test')}
                      </Button>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      {t('settings.ai.providers.anthropic.getApiKey')}{' '}
                      <a
                        href="https://console.anthropic.com/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline inline-flex items-center gap-1"
                      >
                        {t('settings.ai.providers.anthropic.platform')}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('settings.ai.providers.anthropic.model')}
                      </label>
                      <select
                        value={aiProviders.anthropic.model}
                        onChange={(e) => updateProvider('anthropic', 'model', e.target.value)}
                        className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                      >
                        <option value="claude-3-opus">{t('settings.ai.providers.anthropic.models.claude3Opus')}</option>
                        <option value="claude-3-sonnet">{t('settings.ai.providers.anthropic.models.claude3Sonnet')}</option>
                        <option value="claude-3-haiku">{t('settings.ai.providers.anthropic.models.claude3Haiku')}</option>
                        <option value="claude-2.1">{t('settings.ai.providers.anthropic.models.claude21')}</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('settings.ai.providers.openai.temperature')}
                      </label>
                      <Input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={aiProviders.anthropic.temperature}
                        onChange={(e) => updateProvider('anthropic', 'temperature', parseFloat(e.target.value))}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>
          {/* Google AI */}
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Brain className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{t('settings.ai.providers.google.name')}</h3>
                    <p className="text-sm text-gray-500">{t('settings.ai.providers.google.description')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={aiProviders.google.enabled}
                      onChange={(e) => updateProvider('google', 'enabled', e.target.checked)}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
              {aiProviders.google.enabled && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('settings.ai.providers.google.apiKey')}
                    </label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          type={aiProviders.google.showKey ? 'text' : 'password'}
                          value={aiProviders.google.apiKey}
                          onChange={(e) => updateProvider('google', 'apiKey', e.target.value)}
                          placeholder={t('settings.ai.providers.google.apiKeyPlaceholder')}
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => toggleKeyVisibility('google')}
                          className="absolute inset-y-0 right-0 px-3 flex items-center"
                        >
                          {aiProviders.google.showKey ? (
                            <EyeOff className="h-4 w-4 text-gray-400" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => testConnection('google')}
                      >
                        {t('settings.ai.actions.test')}
                      </Button>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      {t('settings.ai.providers.google.getApiKey')}{' '}
                      <a
                        href="https://makersuite.google.com/app/apikey"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline inline-flex items-center gap-1"
                      >
                        {t('settings.ai.providers.google.platform')}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('settings.ai.providers.google.model')}
                      </label>
                      <select
                        value={aiProviders.google.model}
                        onChange={(e) => updateProvider('google', 'model', e.target.value)}
                        className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                      >
                        <option value="gemini-pro">{t('settings.ai.providers.google.models.geminiPro')}</option>
                        <option value="gemini-pro-vision">{t('settings.ai.providers.google.models.geminiProVision')}</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('settings.ai.providers.openai.temperature')}
                      </label>
                      <Input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={aiProviders.google.temperature}
                        onChange={(e) => updateProvider('google', 'temperature', parseFloat(e.target.value))}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>
          {/* Custom Endpoints */}
          <Card>
            <div className="p-6">
              <div className="mb-4">
                <h3 className="text-lg font-medium text-gray-900">{t('settings.ai.customEndpoints.title')}</h3>
                <p className="text-sm text-gray-500">{t('settings.ai.customEndpoints.description')}</p>
              </div>
              <div className="space-y-4">
                {customEndpoints.map((endpoint) => (
                  <div key={endpoint.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{endpoint.name}</p>
                      <p className="text-sm text-gray-500">{endpoint.url}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeCustomEndpoint(endpoint.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <div className="border-t pt-4">
                  <div className="grid grid-cols-3 gap-3">
                    <Input
                      placeholder={t('settings.ai.customEndpoints.namePlaceholder')}
                      value={newEndpoint.name}
                      onChange={(e) => setNewEndpoint(prev => ({ ...prev, name: e.target.value }))}
                    />
                    <Input
                      placeholder={t('settings.ai.customEndpoints.urlPlaceholder')}
                      value={newEndpoint.url}
                      onChange={(e) => setNewEndpoint(prev => ({ ...prev, url: e.target.value }))}
                    />
                    <Input
                      placeholder={t('settings.ai.customEndpoints.apiKeyPlaceholder')}
                      value={newEndpoint.apiKey}
                      onChange={(e) => setNewEndpoint(prev => ({ ...prev, apiKey: e.target.value }))}
                    />
                  </div>
                  <Button
                    variant="outline"
                    className="mt-3"
                    onClick={addCustomEndpoint}
                    disabled={!newEndpoint.name || !newEndpoint.url}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    {t('settings.ai.customEndpoints.addEndpoint')}
                  </Button>
                </div>
              </div>
            </div>
          </Card>
          {/* AI Features Configuration */}
          <Card>
            <div className="p-6">
              <div className="mb-4">
                <h3 className="text-lg font-medium text-gray-900">{t('settings.ai.features.title')}</h3>
                <p className="text-sm text-gray-500">{t('settings.ai.features.description')}</p>
              </div>
              <div className="space-y-3">
                <label className="flex items-center space-x-3">
                  <input type="checkbox" className="rounded border-gray-300 text-primary focus:ring-primary" />
                  <span className="text-sm font-medium text-gray-700">{t('settings.ai.features.evaluationAnalysis')}</span>
                </label>
                <label className="flex items-center space-x-3">
                  <input type="checkbox" className="rounded border-gray-300 text-primary focus:ring-primary" />
                  <span className="text-sm font-medium text-gray-700">{t('settings.ai.features.recommendations')}</span>
                </label>
                <label className="flex items-center space-x-3">
                  <input type="checkbox" className="rounded border-gray-300 text-primary focus:ring-primary" />
                  <span className="text-sm font-medium text-gray-700">{t('settings.ai.features.contentGeneration')}</span>
                </label>
                <label className="flex items-center space-x-3">
                  <input type="checkbox" className="rounded border-gray-300 text-primary focus:ring-primary" />
                  <span className="text-sm font-medium text-gray-700">{t('settings.ai.features.chatbotAssistance')}</span>
                </label>
              </div>
            </div>
          </Card>
          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              {t('settings.ai.actions.save')}
            </Button>
          </div>
        </div>
      </AsyncBoundary>
    </div>
  );
};
export default AISettingsPage;