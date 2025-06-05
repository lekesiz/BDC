import { useEffect, useRef, useCallback } from 'react';
const usePerformanceMonitor = (componentName, options = {}) => {
  const {
    enableLogging = process.env.NODE_ENV === 'development',
    thresholds = {
      renderTime: 16, // 60fps = 16ms per frame
      updateTime: 100,
      mountTime: 200
    },
    onPerformanceIssue
  } = options;
  const renderCount = useRef(0);
  const mountTime = useRef(0);
  const lastRenderTime = useRef(0);
  const performanceData = useRef({
    renders: [],
    slowRenders: 0,
    averageRenderTime: 0
  });
  const logPerformance = useCallback((metric, value, threshold) => {
    if (!enableLogging) return;
    const isSlowOperation = value > threshold;
    const logMethod = isSlowOperation ? 'warn' : 'log';
    console[logMethod](
      `[Performance] ${componentName} - ${metric}: ${value.toFixed(2)}ms`,
      isSlowOperation ? `(exceeds ${threshold}ms threshold)` : ''
    );
    if (isSlowOperation && onPerformanceIssue) {
      onPerformanceIssue({
        component: componentName,
        metric,
        value,
        threshold
      });
    }
  }, [componentName, enableLogging, onPerformanceIssue]);
  // Monitor component mount time
  useEffect(() => {
    const startTime = performance.now();
    return () => {
      mountTime.current = performance.now() - startTime;
      logPerformance('Mount time', mountTime.current, thresholds.mountTime);
    };
  }, []);
  // Monitor render performance
  useEffect(() => {
    const currentRenderTime = performance.now();
    if (lastRenderTime.current > 0) {
      const renderDuration = currentRenderTime - lastRenderTime.current;
      performanceData.current.renders.push(renderDuration);
      if (renderDuration > thresholds.renderTime) {
        performanceData.current.slowRenders++;
      }
      // Calculate running average
      const totalRenderTime = performanceData.current.renders.reduce((a, b) => a + b, 0);
      performanceData.current.averageRenderTime = totalRenderTime / performanceData.current.renders.length;
      logPerformance('Render time', renderDuration, thresholds.renderTime);
    }
    lastRenderTime.current = currentRenderTime;
    renderCount.current++;
  });
  const measureOperation = useCallback(async (operationName, operation) => {
    const startTime = performance.now();
    try {
      const result = await operation();
      const duration = performance.now() - startTime;
      logPerformance(`${operationName} time`, duration, thresholds.updateTime);
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      logPerformance(`${operationName} time (failed)`, duration, thresholds.updateTime);
      throw error;
    }
  }, [logPerformance, thresholds.updateTime]);
  const getPerformanceReport = useCallback(() => {
    return {
      component: componentName,
      renderCount: renderCount.current,
      mountTime: mountTime.current,
      averageRenderTime: performanceData.current.averageRenderTime,
      slowRenders: performanceData.current.slowRenders,
      slowRenderPercentage: (performanceData.current.slowRenders / renderCount.current) * 100
    };
  }, [componentName]);
  return {
    measureOperation,
    getPerformanceReport,
    renderCount: renderCount.current
  };
};
export default usePerformanceMonitor;