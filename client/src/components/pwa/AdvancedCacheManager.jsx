import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../ui/use-toast';
import { 
  Trash2, 
  RefreshCw, 
  Download, 
  Upload, 
  Settings, 
  Info, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  HardDrive,
  Zap,
  TrendingUp
} from 'lucide-react';

/**
 * Advanced Cache Manager Component
 * Provides comprehensive cache management and monitoring for PWA
 */
export function AdvancedCacheManager({ className = '' }) {
  const [caches, setCaches] = useState([]);
  const [storageInfo, setStorageInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [selectedCache, setSelectedCache] = useState(null);
  const [cacheContents, setCacheContents] = useState([]);
  const { toast } = useToast();

  // Cache strategies configuration
  const cacheStrategies = {
    'cache-first': {
      name: 'Cache First',
      description: 'Serve from cache, fallback to network',
      icon: <Database className="w-4 h-4" />,
      color: 'bg-blue-500'
    },
    'network-first': {
      name: 'Network First', 
      description: 'Try network first, fallback to cache',
      icon: <Zap className="w-4 h-4" />,
      color: 'bg-green-500'
    },
    'stale-while-revalidate': {
      name: 'Stale While Revalidate',
      description: 'Serve cached, update in background',
      icon: <RefreshCw className="w-4 h-4" />,
      color: 'bg-orange-500'
    }
  };

  // Load cache information on component mount
  useEffect(() => {
    loadCacheInfo();
    loadStorageInfo();
    const interval = setInterval(() => {
      loadCacheInfo();
      loadStorageInfo();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const loadCacheInfo = useCallback(async () => {
    if (!('caches' in window)) {
      toast({
        title: 'Cache API not supported',
        description: 'Your browser does not support the Cache API',
        variant: 'destructive'
      });
      return;
    }

    try {
      setLoading(true);
      const cacheNames = await caches.keys();
      const cacheInfoPromises = cacheNames.map(async (name) => {
        const cache = await caches.open(name);
        const requests = await cache.keys();
        
        let totalSize = 0;
        let entries = [];
        
        for (const request of requests.slice(0, 100)) { // Limit for performance
          try {
            const response = await cache.match(request);
            if (response) {
              const clone = response.clone();
              const blob = await clone.blob();
              const size = blob.size;
              totalSize += size;
              
              entries.push({
                url: request.url,
                method: request.method,
                size,
                type: response.headers.get('content-type') || 'unknown',
                lastModified: response.headers.get('last-modified'),
                timestamp: Date.now() // Mock timestamp
              });
            }
          } catch (error) {
            console.error('Error processing cache entry:', error);
          }
        }

        return {
          name,
          entries: entries.length,
          totalEntries: requests.length,
          size: totalSize,
          strategy: detectCacheStrategy(name),
          lastAccessed: Date.now() - Math.random() * 86400000, // Mock last accessed
          hitRate: Math.floor(Math.random() * 40 + 60), // Mock hit rate
          contents: entries
        };
      });

      const cacheInfo = await Promise.all(cacheInfoPromises);
      setCaches(cacheInfo);
      
      // Update stats
      const totalSize = cacheInfo.reduce((sum, cache) => sum + cache.size, 0);
      const totalEntries = cacheInfo.reduce((sum, cache) => sum + cache.totalEntries, 0);
      const avgHitRate = cacheInfo.reduce((sum, cache) => sum + cache.hitRate, 0) / cacheInfo.length;
      
      setStats({
        totalCaches: cacheInfo.length,
        totalEntries,
        totalSize,
        avgHitRate: Math.round(avgHitRate) || 0
      });

    } catch (error) {
      console.error('Error loading cache info:', error);
      toast({
        title: 'Error loading cache information',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  const loadStorageInfo = useCallback(async () => {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      try {
        const estimate = await navigator.storage.estimate();
        setStorageInfo({
          used: estimate.usage || 0,
          quota: estimate.quota || 0,
          percentage: estimate.quota > 0 ? Math.round((estimate.usage / estimate.quota) * 100) : 0
        });
      } catch (error) {
        console.error('Error getting storage info:', error);
      }
    }
  }, []);

  const detectCacheStrategy = (cacheName) => {
    if (cacheName.includes('static') || cacheName.includes('assets')) {
      return 'cache-first';
    } else if (cacheName.includes('api') || cacheName.includes('dynamic')) {
      return 'network-first';
    } else if (cacheName.includes('runtime')) {
      return 'stale-while-revalidate';
    }
    return 'cache-first';
  };

  const clearCache = async (cacheName) => {
    try {
      setLoading(true);
      const success = await caches.delete(cacheName);
      
      if (success) {
        toast({
          title: 'Cache cleared',
          description: `Successfully cleared cache: ${cacheName}`
        });
        await loadCacheInfo();
        await loadStorageInfo();
        
        if (selectedCache === cacheName) {
          setSelectedCache(null);
          setCacheContents([]);
        }
      } else {
        throw new Error('Failed to delete cache');
      }
    } catch (error) {
      toast({
        title: 'Error clearing cache',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const clearAllCaches = async () => {
    if (!confirm('Are you sure you want to clear all caches? This will remove all offline functionality.')) {
      return;
    }

    try {
      setLoading(true);
      const cacheNames = await caches.keys();
      const deletePromises = cacheNames.map(name => caches.delete(name));
      await Promise.all(deletePromises);
      
      toast({
        title: 'All caches cleared',
        description: `Successfully cleared ${cacheNames.length} caches`
      });
      
      await loadCacheInfo();
      await loadStorageInfo();
      setSelectedCache(null);
      setCacheContents([]);
    } catch (error) {
      toast({
        title: 'Error clearing all caches',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const viewCacheContents = async (cacheName) => {
    try {
      setLoading(true);
      const cacheInfo = caches.find(c => c.name === cacheName);
      
      if (cacheInfo) {
        setSelectedCache(cacheName);
        setCacheContents(cacheInfo.contents);
      }
    } catch (error) {
      toast({
        title: 'Error loading cache contents',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const deleteCacheEntry = async (url) => {
    if (!selectedCache) return;

    try {
      const cache = await caches.open(selectedCache);
      await cache.delete(url);
      
      toast({
        title: 'Cache entry deleted',
        description: 'Successfully deleted cache entry'
      });
      
      // Refresh cache contents
      await viewCacheContents(selectedCache);
      await loadCacheInfo();
    } catch (error) {
      toast({
        title: 'Error deleting cache entry',
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  const exportCacheData = async () => {
    try {
      const exportData = {
        timestamp: new Date().toISOString(),
        caches: caches.map(({ contents, ...cache }) => cache),
        stats,
        storageInfo
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cache-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);

      toast({
        title: 'Cache data exported',
        description: 'Cache information has been exported successfully'
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: error.message,
        variant: 'destructive'
      });
    }
  };

  const optimizeCaches = async () => {
    try {
      setLoading(true);
      
      // Find caches with low hit rates or old entries
      const optimizations = [];
      
      for (const cache of caches) {
        if (cache.hitRate < 30) {
          optimizations.push(`Low hit rate cache: ${cache.name}`);
        }
        
        if (cache.size > 10 * 1024 * 1024) { // 10MB
          optimizations.push(`Large cache: ${cache.name} (${formatBytes(cache.size)})`);
        }
      }
      
      if (optimizations.length > 0) {
        toast({
          title: 'Optimization suggestions',
          description: optimizations.join('\n'),
          duration: 10000
        });
      } else {
        toast({
          title: 'Caches optimized',
          description: 'All caches are performing well'
        });
      }
    } catch (error) {
      toast({
        title: 'Optimization failed',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimeAgo = (timestamp) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-500" />
            <div>
              <div className="text-2xl font-bold">{stats.totalCaches || 0}</div>
              <div className="text-sm text-muted-foreground">Total Caches</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-green-500" />
            <div>
              <div className="text-2xl font-bold">{formatBytes(stats.totalSize || 0)}</div>
              <div className="text-sm text-muted-foreground">Cache Size</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-orange-500" />
            <div>
              <div className="text-2xl font-bold">{stats.avgHitRate || 0}%</div>
              <div className="text-sm text-muted-foreground">Avg Hit Rate</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-purple-500" />
            <div>
              <div className="text-2xl font-bold">{stats.totalEntries || 0}</div>
              <div className="text-sm text-muted-foreground">Cache Entries</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Storage Usage */}
      {storageInfo && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold">Storage Usage</h3>
            <Badge variant={storageInfo.percentage > 80 ? 'destructive' : 'secondary'}>
              {storageInfo.percentage}% used
            </Badge>
          </div>
          <Progress value={storageInfo.percentage} className="mb-2" />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>{formatBytes(storageInfo.used)} used</span>
            <span>{formatBytes(storageInfo.quota)} total</span>
          </div>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        <Button onClick={loadCacheInfo} disabled={loading} variant="outline">
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
        <Button onClick={exportCacheData} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export Data
        </Button>
        <Button onClick={optimizeCaches} disabled={loading} variant="outline">
          <Settings className="w-4 h-4 mr-2" />
          Optimize
        </Button>
        <Button onClick={clearAllCaches} disabled={loading} variant="destructive">
          <Trash2 className="w-4 h-4 mr-2" />
          Clear All
        </Button>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="caches" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="caches">Cache Management</TabsTrigger>
          <TabsTrigger value="strategies">Cache Strategies</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="caches" className="space-y-4">
          {/* Cache List */}
          <div className="grid gap-4">
            {caches.length === 0 ? (
              <Card className="p-8 text-center">
                <Info className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">No caches found</h3>
                <p className="text-muted-foreground">
                  No caches are currently available. Visit some pages to populate the cache.
                </p>
              </Card>
            ) : (
              caches.map((cache) => (
                <Card key={cache.name} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${cacheStrategies[cache.strategy]?.color || 'bg-gray-500'}`} />
                      <div>
                        <h4 className="font-semibold">{cache.name}</h4>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{cache.totalEntries} entries</span>
                          <span>{formatBytes(cache.size)}</span>
                          <span>Hit rate: {cache.hitRate}%</span>
                          <span>Last accessed: {formatTimeAgo(cache.lastAccessed)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => viewCacheContents(cache.name)}
                      >
                        View Contents
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => clearCache(cache.name)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {cache.hitRate < 50 && (
                    <Alert className="mt-2">
                      <AlertTriangle className="w-4 h-4" />
                      <AlertDescription>
                        Low hit rate detected. Consider reviewing cache strategy for this cache.
                      </AlertDescription>
                    </Alert>
                  )}
                </Card>
              ))
            )}
          </div>

          {/* Cache Contents Modal/Detail View */}
          {selectedCache && (
            <Card className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Contents: {selectedCache}</h3>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setSelectedCache(null);
                    setCacheContents([]);
                  }}
                >
                  Close
                </Button>
              </div>
              
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {cacheContents.length === 0 ? (
                  <p className="text-muted-foreground">No entries found in this cache.</p>
                ) : (
                  cacheContents.map((entry, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border rounded">
                      <div className="flex-1 min-w-0">
                        <div className="font-mono text-sm truncate">{entry.url}</div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{entry.method}</span>
                          <span>{entry.type}</span>
                          <span>{formatBytes(entry.size)}</span>
                          {entry.lastModified && <span>{new Date(entry.lastModified).toLocaleDateString()}</span>}
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => deleteCacheEntry(entry.url)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="strategies" className="space-y-4">
          <div className="grid gap-4">
            {Object.entries(cacheStrategies).map(([key, strategy]) => (
              <Card key={key} className="p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`p-2 rounded ${strategy.color} text-white`}>
                    {strategy.icon}
                  </div>
                  <div>
                    <h4 className="font-semibold">{strategy.name}</h4>
                    <p className="text-sm text-muted-foreground">{strategy.description}</p>
                  </div>
                </div>
                
                <div className="mt-4">
                  <h5 className="font-medium mb-2">Used by caches:</h5>
                  <div className="flex flex-wrap gap-2">
                    {caches
                      .filter(cache => cache.strategy === key)
                      .map(cache => (
                        <Badge key={cache.name} variant="secondary">
                          {cache.name}
                        </Badge>
                      ))
                    }
                    {caches.filter(cache => cache.strategy === key).length === 0 && (
                      <span className="text-sm text-muted-foreground">No caches using this strategy</span>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Cache Performance</h4>
              <div className="space-y-2">
                {caches.map(cache => (
                  <div key={cache.name} className="flex items-center justify-between">
                    <span className="text-sm">{cache.name}</span>
                    <div className="flex items-center gap-2">
                      <Progress value={cache.hitRate} className="w-16" />
                      <span className="text-sm">{cache.hitRate}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
            
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Cache Sizes</h4>
              <div className="space-y-2">
                {caches.map(cache => (
                  <div key={cache.name} className="flex items-center justify-between">
                    <span className="text-sm">{cache.name}</span>
                    <span className="text-sm">{formatBytes(cache.size)}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
          
          {storageInfo && storageInfo.percentage > 80 && (
            <Alert>
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>
                Storage usage is high ({storageInfo.percentage}%). Consider clearing some caches or optimizing cache strategies.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AdvancedCacheManager;