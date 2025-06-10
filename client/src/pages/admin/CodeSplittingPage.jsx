// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Package,
  Layers,
  Zap,
  BarChart,
  FileCode,
  GitBranch,
  Play,
  Settings,
  Download,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  AlertTriangle,
  Code,
  FolderTree,
  Filter,
  RefreshCw,
  Activity,
  Eye } from
'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';import { useTranslation } from "react-i18next";
const bundleCategories = [
{ id: 'vendor', name: 'Vendor Libraries', color: 'blue' },
{ id: 'core', name: 'Core Components', color: 'green' },
{ id: 'routes', name: 'Route Components', color: 'purple' },
{ id: 'lazy', name: 'Lazy Loaded', color: 'yellow' },
{ id: 'common', name: 'Common Chunks', color: 'gray' }];

const optimizationStrategies = [
{
  id: 'route_splitting',
  name: 'Route-based Splitting',
  description: 'Split code by route for optimal loading',
  impact: 'high',
  status: 'active'
},
{
  id: 'vendor_splitting',
  name: 'Vendor Extraction',
  description: 'Separate vendor libraries from app code',
  impact: 'high',
  status: 'active'
},
{
  id: 'dynamic_imports',
  name: 'Dynamic Imports',
  description: 'Load components on demand',
  impact: 'medium',
  status: 'partial'
},
{
  id: 'common_chunks',
  name: 'Common Chunks',
  description: 'Extract shared code between modules',
  impact: 'medium',
  status: 'active'
}];

const CodeSplittingPage = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [bundles, setBundles] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [stats, setStats] = useState({
    totalSize: 0,
    initialSize: 0,
    lazySizeTotal: 0,
    cacheHit: 0,
    avgLoadTime: 0,
    coverage: 0
  });
  const [config, setConfig] = useState({
    maxAsyncRequests: 6,
    maxInitialRequests: 4,
    minSize: 30000,
    maxSize: 244000,
    cacheGroups: {
      vendor: true,
      common: true,
      default: true
    },
    runtimeChunk: 'single',
    moduleIds: 'deterministic'
  });
  const [analysis, setAnalysis] = useState(null);
  const [selectedBundle, setSelectedBundle] = useState(null);
  useEffect(() => {
    fetchBundles();
    fetchStats();
    fetchRoutes();
  }, []);
  const fetchBundles = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/bundles', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setBundles(data.bundles || []);
      }
    } catch (error) {
      console.error('Error fetching bundles:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchStats = async () => {
    try {
      const response = await fetch('/api/admin/bundles/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };
  const fetchRoutes = async () => {
    try {
      const response = await fetch('/api/admin/routes/analysis', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setRoutes(data.routes || []);
      }
    } catch (error) {
      console.error('Error fetching routes:', error);
    }
  };
  const analyzeBundle = async (bundleId) => {
    try {
      const response = await fetch(`/api/admin/bundles/${bundleId}/analyze`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data.analysis);
        setSelectedBundle(bundleId);
      }
    } catch (error) {
      showToast('Error analyzing bundle', 'error');
    }
  };
  const optimizeBundle = async (bundleId, strategy) => {
    try {
      const response = await fetch(`/api/admin/bundles/${bundleId}/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ strategy })
      });
      if (response.ok) {
        showToast('Bundle optimized successfully', 'success');
        fetchBundles();
        fetchStats();
      }
    } catch (error) {
      showToast('Error optimizing bundle', 'error');
    }
  };
  const updateConfig = async (newConfig) => {
    try {
      const response = await fetch('/api/admin/bundles/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newConfig)
      });
      if (response.ok) {
        setConfig(newConfig);
        showToast('Configuration updated', 'success');
      }
    } catch (error) {
      showToast('Error updating configuration', 'error');
    }
  };
  const generateReport = async () => {
    try {
      const response = await fetch('/api/admin/bundles/report', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bundle-analysis-${Date.now()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      showToast('Error generating report', 'error');
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

  const getCategoryColor = (category) => {
    const cat = bundleCategories.find((c) => c.id === category);
    return cat ? `bg-${cat.color}-100 text-${cat.color}-800` : 'bg-gray-100 text-gray-800';
  };
  const renderOverview = () =>
  <div className="space-y-6">
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.total_bundle_size")}</p>
              <p className="text-2xl font-bold">{formatBytes(stats.totalSize)}</p>
              <p className="text-xs text-gray-500">
                {formatBytes(stats.initialSize)} initial
              </p>
            </div>
            <Package className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.code_coverage")}</p>
              <p className="text-2xl font-bold">{stats.coverage.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">{t("pages.used_on_load")}</p>
            </div>
            <BarChart className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.avg_load_time")}</p>
              <p className="text-2xl font-bold">{stats.avgLoadTime}ms</p>
              <p className="text-xs text-gray-500">{t("pages.first_meaningful_paint")}</p>
            </div>
            <Clock className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.cache_hit_rate")}</p>
              <p className="text-2xl font-bold">{(stats.cacheHit * 100).toFixed(1)}%</p>
              <p className="text-xs text-gray-500">{t("pages.browser_cache")}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>
      {/* Optimization Strategies */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.optimization_strategies")}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {optimizationStrategies.map((strategy) =>
        <div key={strategy.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <h4 className="font-medium">{strategy.name}</h4>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                    ${strategy.status === 'active' ? 'bg-green-100 text-green-800' :
              strategy.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'}`}>
                    {strategy.status}
                  </span>
                </div>
                <span className={`text-sm font-medium
                  ${strategy.impact === 'high' ? 'text-red-600' :
            strategy.impact === 'medium' ? 'text-yellow-600' :
            'text-green-600'}`}>
                  {strategy.impact} impact
                </span>
              </div>
              <p className="text-sm text-gray-600">{strategy.description}</p>
            </div>
        )}
        </div>
      </Card>
      {/* Bundle Distribution */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.bundle_distribution")}</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
          <p className="text-gray-600">{t("pages.bundle_distribution_chart_would_go_here")}</p>
        </div>
      </Card>
      {/* Recent Changes */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.recent_optimizations")}</h3>
        <div className="space-y-3">
          {[
        { date: '2023-05-16 10:30', action: 'Route splitting enabled', impact: '-15% initial load' },
        { date: '2023-05-15 14:22', action: 'Vendor chunk extracted', impact: '-20% cache invalidation' },
        { date: '2023-05-14 09:15', action: 'Dynamic imports added', impact: '-12% total size' }].
        map((change, index) =>
        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <p className="font-medium">{change.action}</p>
                <p className="text-sm text-gray-600">{change.date}</p>
              </div>
              <span className="text-sm font-medium text-green-600">{change.impact}</span>
            </div>
        )}
        </div>
      </Card>
    </div>;

  const renderBundles = () =>
  <div className="space-y-6">
      {/* Filters */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex space-x-4">
            {bundleCategories.map((category) =>
          <label key={category.id} className="flex items-center cursor-pointer">
                <input type="checkbox" className="mr-2" defaultChecked />
                <span className={`px-2 py-1 rounded text-sm font-medium bg-${category.color}-100 text-${category.color}-800`}>
                  {category.name}
                </span>
              </label>
          )}
          </div>
          <Button
          size="sm"
          variant="secondary"
          onClick={generateReport}>

            <Download className="w-4 h-4 mr-2" />{t("pages.generate_report")}

        </Button>
        </div>
      </Card>
      {/* Bundle List */}
      {loading ?
    <div className="flex justify-center py-12">
          <Spinner />
        </div> :

    <div className="space-y-4">
          {bundles.map((bundle) =>
      <Card key={bundle.id}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <FileCode className="w-5 h-5 text-gray-600" />
                    <h4 className="font-medium">{bundle.name}</h4>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getCategoryColor(bundle.category)}`}>
                      {bundle.category}
                    </span>
                  </div>
                  <div className="grid grid-cols-4 gap-4 text-sm mb-3">
                    <div>
                      <p className="text-gray-600">{t("pages.size")}</p>
                      <p className="font-medium">{formatBytes(bundle.size)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">{t("pages.gzipped")}</p>
                      <p className="font-medium">{formatBytes(bundle.gzipSize)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">{t("pages.modules")}</p>
                      <p className="font-medium">{bundle.moduleCount}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">{t("components.load_time")}</p>
                      <p className="font-medium">{bundle.loadTime}ms</p>
                    </div>
                  </div>
                  {/* Module List */}
                  <div className="text-sm">
                    <p className="text-gray-600 mb-1">{t("pages.top_modules")}</p>
                    <div className="flex flex-wrap gap-2">
                      {bundle.modules?.slice(0, 5).map((module, index) =>
                <span key={index} className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {module.name} ({formatBytes(module.size)})
                        </span>
                )}
                      {bundle.modules?.length > 5 &&
                <span className="text-xs text-gray-500">
                          +{bundle.modules.length - 5} more
                        </span>
                }
                    </div>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button
              size="sm"
              variant="secondary"
              onClick={() => analyzeBundle(bundle.id)}>

                    <Eye className="w-4 h-4 mr-2" />{t("pages.analyze")}

            </Button>
                  <Button
              size="sm"
              onClick={() => optimizeBundle(bundle.id, 'auto')}>

                    <Zap className="w-4 h-4 mr-2" />{t("pages.optimize")}

            </Button>
                </div>
              </div>
            </Card>
      )}
        </div>
    }
      {/* Bundle Analysis */}
      {analysis && selectedBundle &&
    <Card>
          <h3 className="font-semibold text-lg mb-4">{t("pages.bundle_analysis")}</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">{t("pages.size_analysis")}</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">{t("pages.parsed_size")}</p>
                  <p className="text-lg font-bold">{formatBytes(analysis.parsedSize)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t("pages.gzipped_size")}</p>
                  <p className="text-lg font-bold">{formatBytes(analysis.gzipSize)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t("pages.brotli_size")}</p>
                  <p className="text-lg font-bold">{formatBytes(analysis.brotliSize)}</p>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">{t("pages.dependencies")}</h4>
              <div className="space-y-2">
                {analysis.dependencies?.map((dep, index) =>
            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-mono">{dep.name}</span>
                    <div className="flex items-center space-x-3">
                      <span className="text-sm">{formatBytes(dep.size)}</span>
                      <span className="text-sm text-gray-600">{dep.version}</span>
                    </div>
                  </div>
            )}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">{t("pages.optimization_suggestions")}</h4>
              <div className="space-y-2">
                {analysis.suggestions?.map((suggestion, index) =>
            <div key={index} className="flex items-start space-x-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                    <p className="text-sm">{suggestion}</p>
                  </div>
            )}
              </div>
            </div>
          </div>
        </Card>
    }
    </div>;

  const renderRoutes = () =>
  <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.route_analysis")}</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.route")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.component")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.bundle_size")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.load_time")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.type")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.status")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.actions")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {routes.map((route) =>
            <tr key={route.id}>
                  <td className="px-4 py-3 text-sm font-mono">{route.path}</td>
                  <td className="px-4 py-3 text-sm">{route.component}</td>
                  <td className="px-4 py-3 text-sm">{formatBytes(route.bundleSize)}</td>
                  <td className="px-4 py-3 text-sm">{route.loadTime}ms</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                      ${route.lazy ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'}`}>
                      {route.lazy ? 'Lazy' : 'Direct'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {route.optimized ?
                <CheckCircle className="w-5 h-5 text-green-500" /> :

                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                }
                  </td>
                  <td className="px-4 py-3">
                    <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => optimizeBundle(route.bundleId, 'route_split')}
                  disabled={route.optimized}>{t("pages.optimize")}


                </Button>
                  </td>
                </tr>
            )}
            </tbody>
          </table>
        </div>
      </Card>
      {/* Route Tree */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.route_hierarchy")}</h3>
        <div className="p-4 bg-gray-50 rounded">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <FolderTree className="w-4 h-4 text-gray-600" />
              <span className="font-mono text-sm">/</span>
              <span className="text-sm text-gray-600">{t("pages.layout_45kb")}</span>
            </div>
            <div className="ml-6 space-y-2">
              <div className="flex items-center space-x-2">
                <GitBranch className="w-4 h-4 text-gray-600" />
                <span className="font-mono text-sm">/dashboard</span>
                <span className="text-sm text-gray-600">{t("pages.15kb_lazy")}</span>
              </div>
              <div className="flex items-center space-x-2">
                <GitBranch className="w-4 h-4 text-gray-600" />
                <span className="font-mono text-sm">/beneficiaries</span>
                <span className="text-sm text-gray-600">{t("pages.22kb_lazy")}</span>
              </div>
              <div className="ml-6 space-y-2">
                <div className="flex items-center space-x-2">
                  <GitBranch className="w-4 h-4 text-gray-600" />
                  <span className="font-mono text-sm">/:id</span>
                  <span className="text-sm text-gray-600">{t("pages.8kb_lazy")}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>;

  const renderSettings = () =>
  <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.webpack_configuration")}</h3>
        <div className="space-y-4">
          {/* Split Chunks Settings */}
          <div>
            <h4 className="font-medium mb-3">{t("pages.split_chunks")}</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">{t("pages.max_async_requests")}</label>
                <input
                type="number"
                className="w-full p-2 border rounded-lg"
                value={config.maxAsyncRequests}
                onChange={(e) => setConfig({
                  ...config,
                  maxAsyncRequests: parseInt(e.target.value)
                })} />

              </div>
              <div>
                <label className="block text-sm font-medium mb-1">{t("pages.max_initial_requests")}</label>
                <input
                type="number"
                className="w-full p-2 border rounded-lg"
                value={config.maxInitialRequests}
                onChange={(e) => setConfig({
                  ...config,
                  maxInitialRequests: parseInt(e.target.value)
                })} />

              </div>
              <div>
                <label className="block text-sm font-medium mb-1">{t("pages.min_size_bytes")}</label>
                <input
                type="number"
                className="w-full p-2 border rounded-lg"
                value={config.minSize}
                onChange={(e) => setConfig({
                  ...config,
                  minSize: parseInt(e.target.value)
                })} />

              </div>
              <div>
                <label className="block text-sm font-medium mb-1">{t("pages.max_size_bytes")}</label>
                <input
                type="number"
                className="w-full p-2 border rounded-lg"
                value={config.maxSize}
                onChange={(e) => setConfig({
                  ...config,
                  maxSize: parseInt(e.target.value)
                })} />

              </div>
            </div>
          </div>
          {/* Cache Groups */}
          <div>
            <h4 className="font-medium mb-3">{t("pages.cache_groups")}</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{t("pages.vendor_chunks")}</p>
                  <p className="text-sm text-gray-600">{t("pages.extract_nodemodules_to_separate_bundle")}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={config.cacheGroups.vendor}
                  onChange={(e) => setConfig({
                    ...config,
                    cacheGroups: {
                      ...config.cacheGroups,
                      vendor: e.target.checked
                    }
                  })} />

                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{t("pages.common_chunks")}</p>
                  <p className="text-sm text-gray-600">{t("pages.extract_shared_code_between_modules")}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={config.cacheGroups.common}
                  onChange={(e) => setConfig({
                    ...config,
                    cacheGroups: {
                      ...config.cacheGroups,
                      common: e.target.checked
                    }
                  })} />

                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
          </div>
          {/* Runtime Options */}
          <div>
            <h4 className="font-medium mb-3">{t("pages.runtime_options")}</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">{t("pages.runtime_chunk")}</label>
                <select
                className="w-full p-2 border rounded-lg"
                value={config.runtimeChunk}
                onChange={(e) => setConfig({
                  ...config,
                  runtimeChunk: e.target.value
                })}>

                  <option value="single">{t("components.single")}</option>
                  <option value="multiple">{t("pages.multiple")}</option>
                  <option value="false">{t("components.disabled")}</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">{t("pages.module_ids")}</label>
                <select
                className="w-full p-2 border rounded-lg"
                value={config.moduleIds}
                onChange={(e) => setConfig({
                  ...config,
                  moduleIds: e.target.value
                })}>

                  <option value="deterministic">{t("pages.deterministic")}</option>
                  <option value="named">{t("pages.named")}</option>
                  <option value="natural">{t("pages.natural")}</option>
                  <option value="size">{t("pages.size")}</option>
                </select>
              </div>
            </div>
          </div>
          <div className="flex space-x-2 pt-4">
            <Button
            onClick={() => updateConfig(config)}>{t("components.save_configuration")}


          </Button>
            <Button
            variant="secondary"
            onClick={fetchStats}>{t("pages.reset_to_default")}


          </Button>
          </div>
        </div>
      </Card>
      {/* Presets */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.optimization_presets")}</h3>
        <div className="space-y-3">
          {[
        {
          name: 'Aggressive Splitting',
          description: 'Maximum code splitting for best caching',
          config: { maxAsyncRequests: 10, maxInitialRequests: 8, minSize: 20000 }
        },
        {
          name: 'Balanced',
          description: 'Good balance between splitting and requests',
          config: { maxAsyncRequests: 6, maxInitialRequests: 4, minSize: 30000 }
        },
        {
          name: 'Minimal Splitting',
          description: 'Fewer chunks for simpler deployment',
          config: { maxAsyncRequests: 3, maxInitialRequests: 3, minSize: 50000 }
        }].
        map((preset, index) =>
        <div key={index} className="border rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">{preset.name}</p>
                  <p className="text-sm text-gray-600">{preset.description}</p>
                </div>
                <Button
              size="sm"
              variant="secondary"
              onClick={() => setConfig({ ...config, ...preset.config })}>{t("pages.apply")}


            </Button>
              </div>
            </div>
        )}
        </div>
      </Card>
    </div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t("pages.code_splitting")}</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary">{t("pages.back_to_settings")}


        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'bundles', 'routes', 'settings'].map((tab) =>
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
      {activeTab === 'bundles' && renderBundles()}
      {activeTab === 'routes' && renderRoutes()}
      {activeTab === 'settings' && renderSettings()}
    </div>);

};
export default CodeSplittingPage;