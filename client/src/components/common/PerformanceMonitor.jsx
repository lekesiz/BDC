import { useEffect, useState } from 'react';
import { BarChart3, Activity, Zap } from 'lucide-react';

const PerformanceMonitor = () => {
  const [metrics, setMetrics] = useState({
    fps: 0,
    memory: 0,
    loadTime: 0,
    renderCount: 0
  });

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    let animationId;

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        const fps = Math.round(frameCount * 1000 / (currentTime - lastTime));
        
        setMetrics(prev => ({
          ...prev,
          fps,
          memory: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1048576) : 0,
          renderCount: prev.renderCount + 1
        }));
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      animationId = requestAnimationFrame(measureFPS);
    };

    measureFPS();

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, []);

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const getFPSColor = (fps) => {
    if (fps >= 55) return 'text-green-500';
    if (fps >= 30) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="fixed bottom-4 right-4 bg-black bg-opacity-80 text-white p-4 rounded-lg shadow-lg text-xs font-mono z-50">
      <div className="flex items-center mb-2">
        <BarChart3 className="w-4 h-4 mr-2" />
        <span>Performance Monitor</span>
      </div>
      
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="flex items-center">
            <Activity className="w-3 h-3 mr-1" />
            FPS:
          </span>
          <span className={getFPSColor(metrics.fps)}>{metrics.fps}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="flex items-center">
            <Zap className="w-3 h-3 mr-1" />
            Memory:
          </span>
          <span>{metrics.memory} MB</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span>Renders:</span>
          <span>{metrics.renderCount}</span>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitor;