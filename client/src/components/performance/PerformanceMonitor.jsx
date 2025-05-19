import React, { useEffect, useState } from 'react';
import { BarChart3, Zap, Clock, TrendingUp } from 'lucide-react';

/**
 * Performance monitoring component that tracks Core Web Vitals
 */
export const PerformanceMonitor = ({ 
  showInProduction = false, 
  position = 'bottom-right',
  autoHide = true,
  hideDelay = 5000
}) => {
  const [metrics, setMetrics] = useState({
    lcp: null,
    fid: null,
    cls: null,
    fcp: null,
    ttfb: null
  });
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (process.env.NODE_ENV === 'production' && !showInProduction) {
      return;
    }

    // Track Largest Contentful Paint
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      setMetrics(prev => ({ ...prev, lcp: Math.round(lastEntry.renderTime || lastEntry.loadTime) }));
    });
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

    // Track First Input Delay
    const fidObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const firstEntry = entries[0];
      setMetrics(prev => ({ ...prev, fid: Math.round(firstEntry.processingStart - firstEntry.startTime) }));
    });
    fidObserver.observe({ entryTypes: ['first-input'] });

    // Track Cumulative Layout Shift
    let clsValue = 0;
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
          setMetrics(prev => ({ ...prev, cls: Math.round(clsValue * 1000) / 1000 }));
        }
      }
    });
    clsObserver.observe({ entryTypes: ['layout-shift'] });

    // Track First Contentful Paint
    const fcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
      if (fcpEntry) {
        setMetrics(prev => ({ ...prev, fcp: Math.round(fcpEntry.startTime) }));
      }
    });
    fcpObserver.observe({ entryTypes: ['paint'] });

    // Track Time to First Byte
    const navigationEntry = performance.getEntriesByType('navigation')[0];
    if (navigationEntry) {
      setMetrics(prev => ({ ...prev, ttfb: Math.round(navigationEntry.responseStart - navigationEntry.requestStart) }));
    }

    // Auto-hide after delay
    if (autoHide) {
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, hideDelay);
      return () => clearTimeout(timer);
    }

    return () => {
      lcpObserver.disconnect();
      fidObserver.disconnect();
      clsObserver.disconnect();
      fcpObserver.disconnect();
    };
  }, [showInProduction, autoHide, hideDelay]);

  if (process.env.NODE_ENV === 'production' && !showInProduction) {
    return null;
  }

  if (!isVisible) {
    return null;
  }

  const getMetricColor = (metric, value) => {
    if (value === null) return 'text-gray-500';
    
    switch (metric) {
      case 'lcp':
        return value <= 2500 ? 'text-green-500' : value <= 4000 ? 'text-yellow-500' : 'text-red-500';
      case 'fid':
        return value <= 100 ? 'text-green-500' : value <= 300 ? 'text-yellow-500' : 'text-red-500';
      case 'cls':
        return value <= 0.1 ? 'text-green-500' : value <= 0.25 ? 'text-yellow-500' : 'text-red-500';
      case 'fcp':
        return value <= 1800 ? 'text-green-500' : value <= 3000 ? 'text-yellow-500' : 'text-red-500';
      case 'ttfb':
        return value <= 800 ? 'text-green-500' : value <= 1800 ? 'text-yellow-500' : 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  };

  return (
    <div className={`fixed ${positionClasses[position]} z-50`}>
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-[250px]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-700">Core Web Vitals</h3>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>
        
        <div className="space-y-2">
          <MetricRow
            icon={<TrendingUp className="w-4 h-4" />}
            label="LCP"
            value={metrics.lcp}
            unit="ms"
            color={getMetricColor('lcp', metrics.lcp)}
            tooltip="Largest Contentful Paint"
          />
          
          <MetricRow
            icon={<Zap className="w-4 h-4" />}
            label="FID"
            value={metrics.fid}
            unit="ms"
            color={getMetricColor('fid', metrics.fid)}
            tooltip="First Input Delay"
          />
          
          <MetricRow
            icon={<BarChart3 className="w-4 h-4" />}
            label="CLS"
            value={metrics.cls}
            unit=""
            color={getMetricColor('cls', metrics.cls)}
            tooltip="Cumulative Layout Shift"
          />
          
          <MetricRow
            icon={<Clock className="w-4 h-4" />}
            label="FCP"
            value={metrics.fcp}
            unit="ms"
            color={getMetricColor('fcp', metrics.fcp)}
            tooltip="First Contentful Paint"
          />
          
          <MetricRow
            icon={<Clock className="w-4 h-4" />}
            label="TTFB"
            value={metrics.ttfb}
            unit="ms"
            color={getMetricColor('ttfb', metrics.ttfb)}
            tooltip="Time to First Byte"
          />
        </div>
      </div>
    </div>
  );
};

const MetricRow = ({ icon, label, value, unit, color, tooltip }) => (
  <div className="flex items-center justify-between" title={tooltip}>
    <div className="flex items-center gap-2">
      <span className={color}>{icon}</span>
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </div>
    <span className={`text-sm font-mono ${color}`}>
      {value !== null ? `${value}${unit}` : '-'}
    </span>
  </div>
);

/**
 * Hook to track performance metrics
 */
export const usePerformanceMetrics = () => {
  const [metrics, setMetrics] = useState({
    renderTime: null,
    componentLoadTime: null,
    dataFetchTime: null
  });

  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = Math.round(endTime - startTime);
      setMetrics(prev => ({ ...prev, renderTime }));
    };
  }, []);

  const trackDataFetch = async (fetchFunction) => {
    const startTime = performance.now();
    try {
      const result = await fetchFunction();
      const endTime = performance.now();
      const dataFetchTime = Math.round(endTime - startTime);
      setMetrics(prev => ({ ...prev, dataFetchTime }));
      return result;
    } catch (error) {
      throw error;
    }
  };

  return { metrics, trackDataFetch };
};

/**
 * Performance boundary to catch performance issues
 */
export class PerformanceBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasPerformanceIssue: false };
  }

  componentDidCatch(error, errorInfo) {
    // Log performance issues
    if (error.message.includes('performance')) {
      console.warn('Performance issue detected:', error, errorInfo);
      this.setState({ hasPerformanceIssue: true });
    }
  }

  render() {
    if (this.state.hasPerformanceIssue) {
      return (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h3 className="text-yellow-800 font-semibold">Performance Issue Detected</h3>
          <p className="text-yellow-700 mt-1">
            This component is experiencing performance issues. We're working on optimizing it.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}