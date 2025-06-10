// TODO: i18n - processed
import React, { useState, useEffect, Suspense, lazy } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layers,
  FileCode,
  PlayCircle,
  PauseCircle,
  BarChart,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  Eye,
  EyeOff,
  Image as ImageIcon,
  Code,
  Package,
  AlertTriangle,
  Settings,
  Download,
  Zap,
  Activity,
  TrendingDown } from
'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';
// Example of lazy loaded component
import { useTranslation } from "react-i18next";const LazyComponentExample = lazy(() => import('../../components/examples/LazyExample'));
// Spinner component definition
const Spinner = () =>
<div className="flex justify-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
  </div>;

const componentTypes = [
{ id: 'routes', name: 'Route Components', icon: FileCode, count: 0 },
{ id: 'modals', name: 'Modal Components', icon: Layers, count: 0 },
{ id: 'heavy', name: 'Heavy Components', icon: Package, count: 0 },
{ id: 'images', name: 'Image Components', icon: ImageIcon, count: 0 }];

const loadingStrategies = [
{
  id: 'on_demand',
  name: 'On Demand',
  description: 'Load component when user navigates to it',
  recommended: ['routes', 'modals']
},
{
  id: 'on_interaction',
  name: 'On Interaction',
  description: 'Load when user interacts with trigger',
  recommended: ['modals', 'heavy']
},
{
  id: 'on_visibility',
  name: 'On Visibility',
  description: 'Load when component becomes visible',
  recommended: ['images', 'heavy']
},
{
  id: 'prefetch',
  name: 'Prefetch',
  description: 'Load in background when browser is idle',
  recommended: ['routes']
}];

const LazyLoadingPage = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [components, setComponents] = useState([]);
  const [metrics, setMetrics] = useState({
    totalComponents: 0,
    lazyComponents: 0,
    avgLoadTime: 0,
    bundleReduction: 0,
    ttfb: 0,
    fcp: 0,
    lcp: 0
  });
  const [config, setConfig] = useState({
    enableLazyLoading: true,
    preloadStrategy: 'on_visibility',
    errorBoundary: true,
    retryAttempts: 3,
    loadingTimeout: 5000,
    suspenseFallback: 'spinner',
    imageLoading: 'lazy',
    preloadLinks: true
  });
  const [lazyLoadingEnabled, setLazyLoadingEnabled] = useState(false);
  const [showExample, setShowExample] = useState(false);
  const [performance, setPerformance] = useState({
    withoutLazy: { size: 0, loadTime: 0 },
    withLazy: { size: 0, loadTime: 0 }
  });
  useEffect(() => {
    fetchComponents();
    fetchMetrics();
    fetchPerformance();
  }, []);
  const fetchComponents = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/components/analysis', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setComponents(data.components || []);
      }
    } catch (error) {
      console.error('Error fetching components:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/admin/lazy-loading/metrics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };
  const fetchPerformance = async () => {
    try {
      const response = await fetch('/api/admin/lazy-loading/performance', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPerformance(data.performance);
      }
    } catch (error) {
      console.error('Error fetching performance:', error);
    }
  };
  const enableLazyLoading = async (componentId, strategy) => {
    try {
      const response = await fetch(`/api/admin/components/${componentId}/lazy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ strategy })
      });
      if (response.ok) {
        showToast('Lazy loading enabled successfully', 'success');
        fetchComponents();
        fetchMetrics();
      }
    } catch (error) {
      showToast('Error enabling lazy loading', 'error');
    }
  };
  const updateConfig = async (newConfig) => {
    try {
      const response = await fetch('/api/admin/lazy-loading/config', {
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
      const response = await fetch('/api/admin/lazy-loading/report', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lazy-loading-report-${Date.now()}.pdf`;
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
  const renderOverview = () =>
  <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("components.components")}</p>
              <p className="text-2xl font-bold">{metrics.totalComponents}</p>
              <p className="text-xs text-gray-500">
                {metrics.lazyComponents}{t("pages.lazy_loaded")}
            </p>
            </div>
            <Layers className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.bundle_reduction")}</p>
              <p className="text-2xl font-bold text-green-600">
                {metrics.bundleReduction.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">{t("pages.initial_bundle_size")}</p>
            </div>
            <TrendingDown className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("components.load_time")}</p>
              <p className="text-2xl font-bold">{metrics.avgLoadTime}ms</p>
              <p className="text-xs text-gray-500">{t("pages.average_component")}</p>
            </div>
            <Clock className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.coverage")}</p>
              <p className="text-2xl font-bold">
                {(metrics.lazyComponents / metrics.totalComponents * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">{t("pages.lazy_loading_coverage")}</p>
            </div>
            <Activity className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>
      {/* Performance Comparison */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.performance_impact")}</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">{t("pages.without_lazy_loading")}</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">{t("pages.initial_bundle_size")}</span>
                <span className="font-medium">{formatBytes(performance.withoutLazy.size)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">{t("components.first_contentful_paint")}</span>
                <span className="font-medium">{performance.withoutLazy.loadTime}ms</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">{t("pages.with_lazy_loading")}</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">{t("pages.initial_bundle_size")}</span>
                <span className="font-medium text-green-600">
                  {formatBytes(performance.withLazy.size)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">{t("components.first_contentful_paint")}</span>
                <span className="font-medium text-green-600">
                  {performance.withLazy.loadTime}ms
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <p className="text-green-800 font-medium">
            {((1 - performance.withLazy.size / performance.withoutLazy.size) * 100).toFixed(1)}{t("pages._reduction_in_initial_bundle_size")}
        </p>
          <p className="text-green-700 text-sm">
            {((1 - performance.withLazy.loadTime / performance.withoutLazy.loadTime) * 100).toFixed(1)}{t("pages._faster_initial_load")}
        </p>
        </div>
      </Card>
      {/* Live Demo */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.live_demo")}</h3>
        <div className="space-y-4">
          <p className="text-gray-600">{t("pages.click_the_button_below_to_see_lazy_loading_in_acti")}

        </p>
          <div className="flex space-x-4">
            <Button
            onClick={() => setShowExample(!showExample)}
            variant={showExample ? 'secondary' : 'primary'}>

              {showExample ?
            <>
                  <EyeOff className="w-4 h-4 mr-2" />
                  Hide Example
                </> :

            <>
                  <Eye className="w-4 h-4 mr-2" />{t("pages.load_example")}

            </>
            }
            </Button>
            {showExample &&
          <Button
            variant="secondary"
            onClick={() => setShowExample(false)}>

                <RefreshCw className="w-4 h-4 mr-2" />{t("components.reset")}

          </Button>
          }
          </div>
          {showExample &&
        <Suspense fallback={
        <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-center space-x-2">
                  <Spinner />
                  <span>{t("pages.loading_component")}</span>
                </div>
              </div>
        }>
              <div className="border rounded-lg">
                <LazyComponentExample />
              </div>
            </Suspense>
        }
        </div>
      </Card>
      {/* Top Components */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.components_for_lazy_loading")}</h3>
        <div className="space-y-3">
          {components.filter((c) => !c.lazy).slice(0, 5).map((component) =>
        <div key={component.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex items-center space-x-3">
                <FileCode className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium">{component.name}</p>
                  <p className="text-sm text-gray-600">
                    {formatBytes(component.size)} • {component.type}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">{component.loads} loads</span>
                <Button
              size="sm"
              onClick={() => enableLazyLoading(component.id, 'on_demand')}>{t("pages.enable_lazy")}


            </Button>
              </div>
            </div>
        )}
        </div>
      </Card>
    </div>;

  const renderComponents = () =>
  <div className="space-y-6">
      {/* Component Types */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {componentTypes.map((type) =>
      <Card key={type.id}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{type.name}</p>
                <p className="text-sm text-gray-600">
                  {components.filter((c) => c.type === type.id).length} components
                </p>
              </div>
              <type.icon className="w-6 h-6 text-gray-600" />
            </div>
          </Card>
      )}
      </div>
      {/* Component List */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">{t("pages.all_components")}</h3>
          <div className="flex space-x-2">
            <Button
            size="sm"
            variant="secondary"
            onClick={fetchComponents}>

              <RefreshCw className="w-4 h-4 mr-2" />{t("components.refresh")}

          </Button>
            <Button
            size="sm"
            onClick={generateReport}>

              <Download className="w-4 h-4 mr-2" />{t("components.report")}

          </Button>
          </div>
        </div>
        {loading ?
      <div className="flex justify-center py-8">
            <Spinner />
          </div> :

      <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.component")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.type")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.size")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.status")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("pages.strategy")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.load_time")}</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t("components.actions")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {components.map((component) =>
            <tr key={component.id}>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <FileCode className="w-4 h-4 text-gray-600" />
                        <span className="font-medium">{component.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">{component.type}</td>
                    <td className="px-4 py-3 text-sm">{formatBytes(component.size)}</td>
                    <td className="px-4 py-3">
                      {component.lazy ?
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />{t("pages.lazy")}

                </span> :

                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          <XCircle className="w-3 h-3 mr-1" />{t("pages.eager")}

                </span>
                }
                    </td>
                    <td className="px-4 py-3 text-sm">{component.strategy || '-'}</td>
                    <td className="px-4 py-3 text-sm">{component.loadTime ? `${component.loadTime}ms` : '-'}</td>
                    <td className="px-4 py-3">
                      {!component.lazy ?
                <Button
                  size="sm"
                  onClick={() => enableLazyLoading(component.id, 'on_demand')}>{t("pages.enable")}


                </Button> :

                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setSelectedComponent(component)}>{t("components.configure")}


                </Button>
                }
                    </td>
                  </tr>
            )}
              </tbody>
            </table>
          </div>
      }
      </Card>
    </div>;

  const renderStrategies = () =>
  <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.loading_strategies")}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {loadingStrategies.map((strategy) =>
        <div key={strategy.id} className="border rounded-lg p-4">
              <h4 className="font-medium mb-2">{strategy.name}</h4>
              <p className="text-sm text-gray-600 mb-3">{strategy.description}</p>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">{t("pages.recommended_for")}</p>
                <div className="flex flex-wrap gap-2">
                  {strategy.recommended.map((type) =>
              <span key={type} className="px-2 py-1 bg-gray-100 rounded text-xs">
                      {type}
                    </span>
              )}
                </div>
              </div>
            </div>
        )}
        </div>
      </Card>
      {/* Implementation Examples */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.implementation_examples")}</h3>
        <div className="space-y-6">
          {/* Route-based Lazy Loading */}
          <div>
            <h4 className="font-medium mb-2">{t("pages.routebased_lazy_loading")}</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`import React, { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
// Lazy load route components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}`}</code>
            </pre>
          </div>
          {/* Component-based Lazy Loading */}
          <div>
            <h4 className="font-medium mb-2">{t("pages.componentbased_lazy_loading")}</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`import React, { lazy, Suspense, useState } from 'react';
const HeavyComponent = lazy(() => import('./HeavyComponent'));
function MyComponent() {
  const [showHeavy, setShowHeavy] = useState(false);
  return (
    <div>
      <button onClick={() => setShowHeavy(true)}>
        Load Heavy Component
      </button>
      {showHeavy && (
        <Suspense fallback={<div>Loading...</div>}>
          <HeavyComponent />
        </Suspense>
      )}
    </div>
  );
}`}</code>
            </pre>
          </div>
          {/* Intersection Observer */}
          <div>
            <h4 className="font-medium mb-2">{t("pages.intersection_observer_for_visibility")}</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`import React, { useEffect, useRef, useState } from 'react';
const LazyImage = ({ src, alt }) => {
  const [isVisible, setIsVisible] = useState(false);
  const imgRef = useRef();
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    return () => observer.disconnect();
  }, []);
  return (
    <div ref={imgRef}>
      {isVisible ? (
        <img src={src} alt={alt} loading="lazy" />
      ) : (
        <div className="placeholder" />
      )}
    </div>
  );
};`}</code>
            </pre>
          </div>
          {/* Error Boundary */}
          <div>
            <h4 className="font-medium mb-2">{t("pages.error_boundary_for_lazy_components")}</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong.</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}`}</code>
            </pre>
          </div>
        </div>
      </Card>
    </div>;

  const renderSettings = () =>
  <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.lazy_loading_configuration")}</h3>
        <div className="space-y-4">
          {/* Global Enable/Disable */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t("pages.enable_lazy_loading")}</p>
              <p className="text-sm text-gray-600">{t("pages.turn_on_lazy_loading_for_all_configured_components")}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
              type="checkbox"
              className="sr-only peer"
              checked={config.enableLazyLoading}
              onChange={(e) => setConfig({
                ...config,
                enableLazyLoading: e.target.checked
              })} />

              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Default Strategy */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.default_loading_strategy")}</label>
            <select
            className="w-full p-2 border rounded-lg"
            value={config.preloadStrategy}
            onChange={(e) => setConfig({
              ...config,
              preloadStrategy: e.target.value
            })}>

              {loadingStrategies.map((strategy) =>
            <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
            )}
            </select>
          </div>
          {/* Loading Timeout */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.loading_timeout_ms")}</label>
            <input
            type="number"
            className="w-full p-2 border rounded-lg"
            value={config.loadingTimeout}
            onChange={(e) => setConfig({
              ...config,
              loadingTimeout: parseInt(e.target.value)
            })} />

          </div>
          {/* Retry Attempts */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("components.retry_attempts")}</label>
            <input
            type="number"
            className="w-full p-2 border rounded-lg"
            value={config.retryAttempts}
            onChange={(e) => setConfig({
              ...config,
              retryAttempts: parseInt(e.target.value)
            })}
            min="0"
            max="5" />

          </div>
          {/* Error Boundary */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t("pages.use_error_boundary")}</p>
              <p className="text-sm text-gray-600">{t("pages.catch_and_handle_loading_errors_gracefully")}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
              type="checkbox"
              className="sr-only peer"
              checked={config.errorBoundary}
              onChange={(e) => setConfig({
                ...config,
                errorBoundary: e.target.checked
              })} />

              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Suspense Fallback */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.loading_fallback")}</label>
            <select
            className="w-full p-2 border rounded-lg"
            value={config.suspenseFallback}
            onChange={(e) => setConfig({
              ...config,
              suspenseFallback: e.target.value
            })}>

              <option value="spinner">{t("pages.spinner")}</option>
              <option value="skeleton">{t("pages.skeleton_screen")}</option>
              <option value="blur">{t("pages.blur_effect")}</option>
              <option value="custom">{t("pages.custom_component")}</option>
            </select>
          </div>
          {/* Image Loading */}
          <div>
            <label className="block text-sm font-medium mb-1">{t("pages.image_loading")}</label>
            <select
            className="w-full p-2 border rounded-lg"
            value={config.imageLoading}
            onChange={(e) => setConfig({
              ...config,
              imageLoading: e.target.value
            })}>

              <option value="eager">{t("pages.eager")}</option>
              <option value="lazy">{t("pages.lazy")}</option>
              <option value="auto">{t("pages.auto")}</option>
            </select>
          </div>
          {/* Preload Links */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{t("pages.preload_links")}</p>
              <p className="text-sm text-gray-600">{t("pages.add_preload_hints_for_critical_resources")}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
              type="checkbox"
              className="sr-only peer"
              checked={config.preloadLinks}
              onChange={(e) => setConfig({
                ...config,
                preloadLinks: e.target.checked
              })} />

              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          <div className="flex space-x-2 pt-4">
            <Button
            onClick={() => updateConfig(config)}>{t("components.save_configuration")}


          </Button>
            <Button
            variant="secondary"
            onClick={fetchMetrics}>{t("pages.reset_to_default")}


          </Button>
          </div>
        </div>
      </Card>
      {/* Performance Metrics */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("components.performance_metrics")}</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">{t("pages.time_to_first_byte_ttfb")}</p>
            <p className="text-lg font-bold">{metrics.ttfb}ms</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">{t("pages.first_contentful_paint_fcp")}</p>
            <p className="text-lg font-bold">{metrics.fcp}ms</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">{t("components.largest_contentful_paint_lcp")}</p>
            <p className="text-lg font-bold">{metrics.lcp}ms</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">{t("pages.average_load_time")}</p>
            <p className="text-lg font-bold">{metrics.avgLoadTime}ms</p>
          </div>
        </div>
      </Card>
    </div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t("pages.lazy_loading")}</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary">{t("pages.back_to_settings")}


        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'components', 'strategies', 'settings'].map((tab) =>
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
      {activeTab === 'components' && renderComponents()}
      {activeTab === 'strategies' && renderStrategies()}
      {activeTab === 'settings' && renderSettings()}
    </div>);

};
export default LazyLoadingPage;