// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Database,
  Zap,
  RefreshCw,
  Trash2,
  Settings,
  Activity,
  BarChart,
  Clock,
  CheckCircle,
  AlertTriangle,
  Hash,
  Server,
  HardDrive,
  CloudLightning,
  Gauge,
  TrendingUp,
  TrendingDown } from
'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';import { useTranslation } from "react-i18next";
const cacheTypes = [
{
  id: 'redis',
  name: 'Redis Cache',
  icon: Database,
  status: 'active',
  memory: { used: 245, total: 512 },
  hitRate: 0.89,
  connections: 12,
  enabled: true
},
{
  id: 'memcache',
  name: 'Memcached',
  icon: Server,
  status: 'inactive',
  memory: { used: 0, total: 256 },
  hitRate: 0,
  connections: 0,
  enabled: false
},
{
  id: 'browser',
  name: 'Browser Cache',
  icon: HardDrive,
  status: 'active',
  hitRate: 0.76,
  enabled: true
},
{
  id: 'cdn',
  name: 'CDN Cache',
  icon: CloudLightning,
  status: 'active',
  hitRate: 0.92,
  enabled: true
}];

const CachingSystemPage = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [cacheStats, setCacheStats] = useState({
    totalHits: 0,
    totalMisses: 0,
    hitRate: 0,
    avgResponseTime: 0,
    memorySaved: 0,
    bandwidthSaved: 0
  });
  const [cacheMetrics, setCacheMetrics] = useState([]);
  const [cacheKeys, setCacheKeys] = useState([]);
  const [selectedCache, setSelectedCache] = useState('redis');
  const [cacheConfig, setCacheConfig] = useState({
    ttl: 3600,
    maxSize: 512,
    evictionPolicy: 'lru',
    compression: true,
    warmupEnabled: false,
    preloadEnabled: true
  });
  useEffect(() => {
    fetchCacheStats();
    fetchCacheMetrics();
    fetchCacheKeys();
  }, [selectedCache]);
  const fetchCacheStats = async () => {
    try {
      const response = await fetch('/api/admin/cache/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCacheStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching cache stats:', error);
    }
  };
  const fetchCacheMetrics = async () => {
    try {
      const response = await fetch(`/api/admin/cache/${selectedCache}/metrics`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCacheMetrics(data.metrics || []);
      }
    } catch (error) {
      console.error('Error fetching cache metrics:', error);
    }
  };
  const fetchCacheKeys = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/admin/cache/${selectedCache}/keys`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCacheKeys(data.keys || []);
      }
    } catch (error) {
      console.error('Error fetching cache keys:', error);
    } finally {
      setLoading(false);
    }
  };
  const clearCache = async (cacheType = null) => {
    if (!confirm(`Are you sure you want to clear ${cacheType || 'all'} cache?`)) {
      return;
    }
    try {
      const response = await fetch('/api/admin/cache/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ cacheType })
      });
      if (response.ok) {
        showToast(`${cacheType || 'All'} cache cleared successfully`, 'success');
        fetchCacheStats();
        fetchCacheKeys();
      }
    } catch (error) {
      showToast('Error clearing cache', 'error');
    }
  };
  const invalidateKey = async (key) => {
    try {
      const response = await fetch(`/api/admin/cache/${selectedCache}/invalidate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ key })
      });
      if (response.ok) {
        showToast('Cache key invalidated', 'success');
        fetchCacheKeys();
      }
    } catch (error) {
      showToast('Error invalidating key', 'error');
    }
  };
  const updateCacheConfig = async (config) => {
    try {
      const response = await fetch(`/api/admin/cache/${selectedCache}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      });
      if (response.ok) {
        setCacheConfig(config);
        showToast('Cache configuration updated', 'success');
      }
    } catch (error) {
      showToast('Error updating configuration', 'error');
    }
  };
  const warmupCache = async () => {
    try {
      const response = await fetch('/api/admin/cache/warmup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        showToast('Cache warmup initiated', 'success');
      }
    } catch (error) {
      showToast('Error warming up cache', 'error');
    }
  };
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  // Spinner component definition
  const Spinner = () =>
  <div className="flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>;

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'inactive':
        return 'text-gray-600 bg-gray-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-yellow-600 bg-yellow-100';
    }
  };
  const renderOverview = () =>
  <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("components.hit_rate")}</p>
              <p className="text-2xl font-bold text-green-600">
                {(cacheStats.hitRate * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">
                {cacheStats.totalHits.toLocaleString()} hits
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("components.avg_response_time")}</p>
              <p className="text-2xl font-bold">
                {cacheStats.avgResponseTime}ms
              </p>
              <p className="text-xs text-gray-500">
                vs {cacheStats.avgResponseTime * 3}{t("pages.ms_uncached")}
            </p>
            </div>
            <Clock className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.memory_saved")}</p>
              <p className="text-2xl font-bold">
                {formatBytes(cacheStats.memorySaved)}
              </p>
              <p className="text-xs text-gray-500">{t("pages.this_month")}</p>
            </div>
            <Database className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Bandwidth Saved</p>
              <p className="text-2xl font-bold">
                {formatBytes(cacheStats.bandwidthSaved)}
              </p>
              <p className="text-xs text-gray-500">{t("pages.this_month")}</p>
            </div>
            <Activity className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>
      {/* Cache Systems */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {cacheTypes.map((cache) =>
      <Card key={cache.id}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <cache.icon className="w-6 h-6 text-gray-600" />
                <div>
                  <h3 className="font-medium">{cache.name}</h3>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(cache.status)}`}>
                    {cache.status}
                  </span>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
              type="checkbox"
              className="sr-only peer"
              checked={cache.enabled}
              disabled={cache.status === 'inactive'}
              onChange={() => {

                // Toggle cache enable/disable
              }} />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            {cache.memory &&
        <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>{t("components.memory_usage")}</span>
                  <span>{cache.memory.used}{t("components.mb_")}{cache.memory.total}MB</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
              className="bg-primary h-2 rounded-full"
              style={{ width: `${cache.memory.used / cache.memory.total * 100}%` }} />

                </div>
              </div>
        }
            <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
              <div>
                <p className="text-gray-600">{t("components.hit_rate")}</p>
                <p className="font-medium">{(cache.hitRate * 100).toFixed(1)}%</p>
              </div>
              {cache.connections !== undefined &&
          <div>
                  <p className="text-gray-600">{t("pages.connections")}</p>
                  <p className="font-medium">{cache.connections}</p>
                </div>
          }
            </div>
            <div className="flex space-x-2 mt-4">
              <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              setSelectedCache(cache.id);
              setActiveTab('details');
            }}>{t("pages.details")}


          </Button>
              <Button
            size="sm"
            variant="secondary"
            onClick={() => clearCache(cache.id)}
            disabled={cache.status === 'inactive'}>

                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </Card>
      )}
      </div>
      {/* Performance Chart */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("components.cache_performance")}</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
          <p className="text-gray-600">{t("pages.cache_performance_chart_would_go_here")}</p>
        </div>
      </Card>
    </div>;

  const renderDetails = () =>
  <div className="space-y-6">
      {/* Cache Selection */}
      <div className="flex space-x-4 mb-4">
        {cacheTypes.map((cache) =>
      <Button
        key={cache.id}
        variant={selectedCache === cache.id ? 'primary' : 'secondary'}
        onClick={() => setSelectedCache(cache.id)}>

            <cache.icon className="w-4 h-4 mr-2" />
            {cache.name}
          </Button>
      )}
      </div>
      {/* Cache Keys */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">{t("pages.cache_keys")}</h3>
          <div className="flex space-x-2">
            <Button
            size="sm"
            variant="secondary"
            onClick={() => fetchCacheKeys()}>

              <RefreshCw className="w-4 h-4 mr-2" />{t("components.refresh")}

          </Button>
            <Button
            size="sm"
            onClick={() => clearCache(selectedCache)}>

              <Trash2 className="w-4 h-4 mr-2" />{t("pages.clear_all")}

          </Button>
          </div>
        </div>
        {loading ?
      <div className="flex justify-center py-8">
            <Spinner />
          </div> :
      cacheKeys.length === 0 ?
      <p className="text-gray-600 text-center py-8">No cache keys found</p> :

      <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.key")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.value_size")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">TTL</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.hits")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.last_access")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.actions")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {cacheKeys.map((key) =>
            <tr key={key.key}>
                    <td className="px-4 py-3 text-sm font-mono">{key.key}</td>
                    <td className="px-4 py-3 text-sm">{formatBytes(key.size)}</td>
                    <td className="px-4 py-3 text-sm">
                      {key.ttl > 0 ? `${key.ttl}s` : 'No expiry'}
                    </td>
                    <td className="px-4 py-3 text-sm">{key.hits}</td>
                    <td className="px-4 py-3 text-sm">
                      {new Date(key.lastAccess).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3">
                      <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => invalidateKey(key.key)}>

                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </td>
                  </tr>
            )}
              </tbody>
            </table>
          </div>
      }
      </Card>
    </div>;

  const renderConfiguration = () =>
  <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.cache_configuration")}</h3>
        <div className="space-y-4">
          {/* TTL Setting */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.default_ttl_seconds")}</label>
            <input
            type="number"
            className="w-full p-2 border rounded-lg"
            value={cacheConfig.ttl}
            onChange={(e) => setCacheConfig({
              ...cacheConfig,
              ttl: parseInt(e.target.value)
            })} />

          </div>
          {/* Max Size */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.max_cache_size_mb")}</label>
            <input
            type="number"
            className="w-full p-2 border rounded-lg"
            value={cacheConfig.maxSize}
            onChange={(e) => setCacheConfig({
              ...cacheConfig,
              maxSize: parseInt(e.target.value)
            })} />

          </div>
          {/* Eviction Policy */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.eviction_policy")}</label>
            <select
            className="w-full p-2 border rounded-lg"
            value={cacheConfig.evictionPolicy}
            onChange={(e) => setCacheConfig({
              ...cacheConfig,
              evictionPolicy: e.target.value
            })}>

              <option value="lru">{t("pages.least_recently_used_lru")}</option>
              <option value="lfu">{t("pages.least_frequently_used_lfu")}</option>
              <option value="fifo">{t("pages.first_in_first_out_fifo")}</option>
              <option value="random">{t("pages.random")}</option>
            </select>
          </div>
          {/* Compression */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t("pages.enable_compression")}</p>
              <p className="text-sm text-gray-600">Compress cached values to save memory</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
              type="checkbox"
              className="sr-only peer"
              checked={cacheConfig.compression}
              onChange={(e) => setCacheConfig({
                ...cacheConfig,
                compression: e.target.checked
              })} />

              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Cache Warmup */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t("pages.cache_warmup")}</p>
              <p className="text-sm text-gray-600">{t("pages.prepopulate_cache_on_startup")}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
              type="checkbox"
              className="sr-only peer"
              checked={cacheConfig.warmupEnabled}
              onChange={(e) => setCacheConfig({
                ...cacheConfig,
                warmupEnabled: e.target.checked
              })} />

              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Preload */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t("pages.preload_critical_data")}</p>
              <p className="text-sm text-gray-600">{t("pages.load_frequently_accessed_data_on_demand")}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
              type="checkbox"
              className="sr-only peer"
              checked={cacheConfig.preloadEnabled}
              onChange={(e) => setCacheConfig({
                ...cacheConfig,
                preloadEnabled: e.target.checked
              })} />

              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          <div className="flex space-x-2 pt-4">
            <Button
            onClick={() => updateCacheConfig(cacheConfig)}>{t("components.save_configuration")}


          </Button>
            <Button
            variant="secondary"
            onClick={fetchCacheStats}>{t("pages.reset_to_default")}


          </Button>
          </div>
        </div>
      </Card>
      {/* Cache Strategies */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.cache_strategies")}</h3>
        <div className="space-y-4">
          {[
        {
          name: 'Page Cache',
          description: 'Cache entire pages for static content',
          pattern: '/static/*',
          ttl: 86400,
          enabled: true
        },
        {
          name: 'API Response Cache',
          description: 'Cache API responses for faster access',
          pattern: '/api/public/*',
          ttl: 300,
          enabled: true
        },
        {
          name: 'Database Query Cache',
          description: 'Cache frequently accessed database queries',
          pattern: 'db:*',
          ttl: 600,
          enabled: true
        },
        {
          name: 'Session Cache',
          description: 'Cache user session data',
          pattern: 'session:*',
          ttl: 1800,
          enabled: true
        }].
        map((strategy, index) =>
        <div key={index} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-medium">{strategy.name}</h4>
                    <span className="text-xs text-gray-500">({strategy.pattern})</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{strategy.description}</p>
                  <p className="text-sm">TTL: {strategy.ttl} seconds</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                type="checkbox"
                className="sr-only peer"
                checked={strategy.enabled}
                onChange={() => {

                  // Toggle strategy
                }} />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
        )}
        </div>
      </Card>
    </div>;

  const renderOptimization = () =>
  <div className="space-y-6">
      {/* Optimization Suggestions */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.optimization_suggestions")}</h3>
        <div className="space-y-3">
          {[
        {
          title: 'Increase Cache Hit Rate',
          description: 'Current hit rate is below optimal. Consider caching more frequently accessed data.',
          impact: 'high',
          action: 'Review top queries and add caching'
        },
        {
          title: 'Optimize TTL Settings',
          description: 'Some cache entries have sub-optimal TTL values causing unnecessary misses.',
          impact: 'medium',
          action: 'Adjust TTL based on access patterns'
        },
        {
          title: 'Enable Compression',
          description: 'Enable compression to reduce memory usage by approximately 30%.',
          impact: 'medium',
          action: 'Enable compression in settings'
        },
        {
          title: 'Implement Cache Warming',
          description: 'Pre-populate cache with critical data to improve initial response times.',
          impact: 'low',
          action: 'Configure cache warmup strategy'
        }].
        map((suggestion, index) =>
        <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start space-x-3">
                {suggestion.impact === 'high' ?
            <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" /> :
            suggestion.impact === 'medium' ?
            <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" /> :

            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            }
                <div className="flex-1">
                  <h4 className="font-medium mb-1">{suggestion.title}</h4>
                  <p className="text-sm text-gray-600 mb-2">{suggestion.description}</p>
                  <p className="text-sm text-gray-500">{t("pages.suggested_action")}{suggestion.action}</p>
                </div>
                <Button size="sm">{t("pages.implement")}

            </Button>
              </div>
            </div>
        )}
        </div>
      </Card>
      {/* Cache Analysis */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.cache_analysis")}</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">{t("pages.top_cached_items")}</h4>
            <div className="space-y-2">
              {[
            { key: 'user:preferences:*', hits: 45320, size: '2.3 MB' },
            { key: 'api:products:*', hits: 38920, size: '5.1 MB' },
            { key: 'session:*', hits: 28450, size: '1.8 MB' },
            { key: 'page:home', hits: 18200, size: '450 KB' },
            { key: 'query:popular:*', hits: 12890, size: '3.2 MB' }].
            map((item, index) =>
            <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-mono">{item.key}</span>
                  <div className="flex items-center space-x-3 text-sm">
                    <span>{item.hits.toLocaleString()} hits</span>
                    <span className="text-gray-500">{item.size}</span>
                  </div>
                </div>
            )}
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">{t("pages.cache_misses")}</h4>
            <div className="space-y-2">
              {[
            { pattern: 'api:user:*', misses: 3420, reason: 'TTL expired' },
            { pattern: 'db:report:*', misses: 2180, reason: 'Not cached' },
            { pattern: 'page:dynamic:*', misses: 1890, reason: 'Invalidated' },
            { pattern: 'query:complex:*', misses: 980, reason: 'Too large' }].
            map((item, index) =>
            <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-mono">{item.pattern}</span>
                  <div className="flex items-center space-x-3 text-sm">
                    <span>{item.misses.toLocaleString()} misses</span>
                    <span className="text-gray-500">{item.reason}</span>
                  </div>
                </div>
            )}
            </div>
          </div>
        </div>
      </Card>
      {/* Actions */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.cache_operations")}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button
          onClick={warmupCache}
          variant="secondary">

            <Zap className="w-4 h-4 mr-2" />{t("pages.warmup_cache")}

        </Button>
          <Button
          onClick={() => clearCache()}
          variant="secondary">

            <Trash2 className="w-4 h-4 mr-2" />{t("components.clear_all_caches")}

        </Button>
          <Button
          onClick={fetchCacheStats}
          variant="secondary">

            <RefreshCw className="w-4 h-4 mr-2" />{t("pages.refresh_stats")}

        </Button>
          <Button
          onClick={() => navigate('/admin/database-optimization')}
          variant="secondary">

            <Database className="w-4 h-4 mr-2" />{t("pages.database_tools")}

        </Button>
        </div>
      </Card>
    </div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t("pages.caching_system")}</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary">{t("pages.back_to_settings")}


        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'details', 'configuration', 'optimization'].map((tab) =>
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab ?
            'border-primary text-primary' :
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`
            }>

              {tab}
            </button>
          )}
        </nav>
      </div>
      {/* Tab Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'details' && renderDetails()}
      {activeTab === 'configuration' && renderConfiguration()}
      {activeTab === 'optimization' && renderOptimization()}
    </div>);

};
export default CachingSystemPage;