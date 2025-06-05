import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Image as ImageIcon, 
  Upload, 
  Download,
  Settings,
  Zap,
  BarChart,
  FolderOpen,
  Filter,
  Check,
  X,
  AlertTriangle,
  HardDrive,
  Maximize2,
  Minimize2,
  RefreshCw,
  Eye,
  Layers,
  FileImage,
  TrendingDown
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';
const formatOptions = [
  { id: 'original', name: 'Original', description: 'Keep original format' },
  { id: 'webp', name: 'WebP', description: 'Modern image format with better compression' },
  { id: 'avif', name: 'AVIF', description: 'Next-gen format with superior compression' },
  { id: 'jpg', name: 'JPEG', description: 'Standard format for photos' },
  { id: 'png', name: 'PNG', description: 'Lossless format for graphics' }
];
const presetSizes = [
  { id: 'thumbnail', width: 150, height: 150, name: 'Thumbnail' },
  { id: 'small', width: 320, height: 240, name: 'Small' },
  { id: 'medium', width: 640, height: 480, name: 'Medium' },
  { id: 'large', width: 1024, height: 768, name: 'Large' },
  { id: 'xlarge', width: 1920, height: 1080, name: 'Extra Large' }
];
const ImageOptimizationPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [images, setImages] = useState([]);
  const [selectedImages, setSelectedImages] = useState([]);
  const [stats, setStats] = useState({
    totalImages: 0,
    totalSize: 0,
    optimizedSize: 0,
    savingsPercent: 0,
    formatsDistribution: {},
    unoptimizedCount: 0
  });
  const [optimizationConfig, setOptimizationConfig] = useState({
    quality: 85,
    format: 'webp',
    resizeEnabled: false,
    maxWidth: 1920,
    maxHeight: 1080,
    generateSizes: ['thumbnail', 'medium', 'large'],
    stripMetadata: true,
    progressive: true,
    lazyLoading: true
  });
  const [batchProgress, setBatchProgress] = useState(null);
  useEffect(() => {
    fetchImages();
    fetchStats();
  }, []);
  const fetchImages = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/images/list', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setImages(data.images || []);
      }
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchStats = async () => {
    try {
      const response = await fetch('/api/admin/images/stats', {
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
  const optimizeImages = async (imageIds) => {
    if (imageIds.length === 0) {
      showToast('Please select images to optimize', 'error');
      return;
    }
    setBatchProgress(0);
    try {
      const response = await fetch('/api/admin/images/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          imageIds,
          config: optimizationConfig
        })
      });
      if (response.ok) {
        // Simulate progress
        const interval = setInterval(() => {
          setBatchProgress(prev => {
            if (prev >= 100) {
              clearInterval(interval);
              showToast('Images optimized successfully', 'success');
              fetchImages();
              fetchStats();
              setSelectedImages([]);
              setBatchProgress(null);
              return 100;
            }
            return prev + 10;
          });
        }, 500);
      } else {
        showToast('Failed to optimize images', 'error');
        setBatchProgress(null);
      }
    } catch (error) {
      showToast('Error optimizing images', 'error');
      setBatchProgress(null);
    }
  };
  const analyzeImage = async (imageId) => {
    try {
      const response = await fetch(`/api/admin/images/${imageId}/analyze`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        return data.analysis;
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
    }
  };
  const updateConfig = async (config) => {
    try {
      const response = await fetch('/api/admin/images/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      });
      if (response.ok) {
        setOptimizationConfig(config);
        showToast('Configuration updated', 'success');
      }
    } catch (error) {
      showToast('Error updating configuration', 'error');
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
  const Spinner = () => (
    <div className="flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  );
  const getFormatBadgeColor = (format) => {
    switch (format) {
      case 'webp':
        return 'bg-green-100 text-green-800';
      case 'avif':
        return 'bg-blue-100 text-blue-800';
      case 'jpg':
      case 'jpeg':
        return 'bg-yellow-100 text-yellow-800';
      case 'png':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Images</p>
              <p className="text-2xl font-bold">{stats.totalImages}</p>
              <p className="text-xs text-gray-500">
                {stats.unoptimizedCount} unoptimized
              </p>
            </div>
            <FileImage className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Size</p>
              <p className="text-2xl font-bold">{formatBytes(stats.totalSize)}</p>
              <p className="text-xs text-gray-500">
                {formatBytes(stats.optimizedSize)} optimized
              </p>
            </div>
            <HardDrive className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Space Saved</p>
              <p className="text-2xl font-bold text-green-600">
                {stats.savingsPercent.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">
                {formatBytes(stats.totalSize - stats.optimizedSize)}
              </p>
            </div>
            <TrendingDown className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Formats</p>
              <div className="flex space-x-1 mt-1">
                {Object.entries(stats.formatsDistribution).map(([format, count]) => (
                  <span key={format} className={`px-2 py-1 rounded text-xs font-medium ${getFormatBadgeColor(format)}`}>
                    {format} ({count})
                  </span>
                ))}
              </div>
            </div>
            <Layers className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>
      {/* Quick Actions */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button
            onClick={() => {
              setSelectedImages(images.filter(img => !img.optimized).map(img => img.id));
              optimizeImages(images.filter(img => !img.optimized).map(img => img.id));
            }}
            disabled={stats.unoptimizedCount === 0}
          >
            <Zap className="w-4 h-4 mr-2" />
            Optimize All
          </Button>
          <Button
            variant="secondary"
            onClick={() => setActiveTab('batch')}
          >
            <FolderOpen className="w-4 h-4 mr-2" />
            Batch Process
          </Button>
          <Button
            variant="secondary"
            onClick={() => setActiveTab('settings')}
          >
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
          <Button
            variant="secondary"
            onClick={fetchImages}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </Card>
      {/* Format Distribution Chart */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Format Distribution</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
          <p className="text-gray-600">Format distribution chart would go here</p>
        </div>
      </Card>
      {/* Recent Images */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Recent Images</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {images.slice(0, 8).map(image => (
            <div key={image.id} className="border rounded-lg overflow-hidden">
              <div className="aspect-square bg-gray-100 relative">
                <img
                  src={image.thumbnail || image.url}
                  alt={image.name}
                  className="w-full h-full object-cover"
                />
                {!image.optimized && (
                  <div className="absolute top-2 right-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  </div>
                )}
              </div>
              <div className="p-3">
                <p className="text-sm font-medium truncate">{image.name}</p>
                <div className="flex justify-between items-center mt-1">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getFormatBadgeColor(image.format)}`}>
                    {image.format}
                  </span>
                  <span className="text-xs text-gray-600">{formatBytes(image.size)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
  const renderGallery = () => (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex space-x-4">
            <select className="p-2 border rounded-lg">
              <option value="">All Formats</option>
              <option value="jpg">JPEG</option>
              <option value="png">PNG</option>
              <option value="webp">WebP</option>
              <option value="avif">AVIF</option>
            </select>
            <select className="p-2 border rounded-lg">
              <option value="">All Statuses</option>
              <option value="optimized">Optimized</option>
              <option value="unoptimized">Unoptimized</option>
            </select>
          </div>
          <div className="flex space-x-2">
            {selectedImages.length > 0 && (
              <>
                <Button
                  onClick={() => optimizeImages(selectedImages)}
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Optimize Selected ({selectedImages.length})
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setSelectedImages([])}
                >
                  Clear Selection
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>
      {/* Image Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {images.map(image => (
            <div
              key={image.id}
              className={`border rounded-lg overflow-hidden cursor-pointer transition-all ${
                selectedImages.includes(image.id) ? 'ring-2 ring-primary' : ''
              }`}
              onClick={() => {
                if (selectedImages.includes(image.id)) {
                  setSelectedImages(selectedImages.filter(id => id !== image.id));
                } else {
                  setSelectedImages([...selectedImages, image.id]);
                }
              }}
            >
              <div className="aspect-square bg-gray-100 relative">
                <img
                  src={image.thumbnail || image.url}
                  alt={image.name}
                  className="w-full h-full object-cover"
                />
                {selectedImages.includes(image.id) && (
                  <div className="absolute top-2 left-2">
                    <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  </div>
                )}
                {!image.optimized && (
                  <div className="absolute top-2 right-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  </div>
                )}
              </div>
              <div className="p-2">
                <p className="text-xs font-medium truncate">{image.name}</p>
                <div className="flex justify-between items-center mt-1">
                  <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${getFormatBadgeColor(image.format)}`}>
                    {image.format}
                  </span>
                  <span className="text-xs text-gray-600">{formatBytes(image.size)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
  const renderBatchOptimization = () => (
    <div className="space-y-6">
      {/* Batch Progress */}
      {batchProgress !== null && (
        <Card>
          <h3 className="font-semibold text-lg mb-4">Optimization Progress</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Processing images...</span>
              <span>{batchProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${batchProgress}%` }}
              />
            </div>
          </div>
        </Card>
      )}
      {/* Batch Settings */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Batch Optimization Settings</h3>
        <div className="space-y-4">
          {/* Quality Slider */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Quality: {optimizationConfig.quality}%
            </label>
            <input
              type="range"
              min="10"
              max="100"
              step="5"
              value={optimizationConfig.quality}
              onChange={(e) => setOptimizationConfig({
                ...optimizationConfig,
                quality: parseInt(e.target.value)
              })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Low (10%)</span>
              <span>Medium (50%)</span>
              <span>High (100%)</span>
            </div>
          </div>
          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Output Format</label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {formatOptions.map(format => (
                <label
                  key={format.id}
                  className={`border rounded-lg p-3 cursor-pointer transition-all ${
                    optimizationConfig.format === format.id
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="format"
                    value={format.id}
                    checked={optimizationConfig.format === format.id}
                    onChange={(e) => setOptimizationConfig({
                      ...optimizationConfig,
                      format: e.target.value
                    })}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <p className="font-medium">{format.name}</p>
                    <p className="text-xs text-gray-600">{format.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
          {/* Resize Options */}
          <div>
            <div className="flex items-center mb-3">
              <input
                type="checkbox"
                id="resize"
                checked={optimizationConfig.resizeEnabled}
                onChange={(e) => setOptimizationConfig({
                  ...optimizationConfig,
                  resizeEnabled: e.target.checked
                })}
                className="mr-2"
              />
              <label htmlFor="resize" className="font-medium">Resize Images</label>
            </div>
            {optimizationConfig.resizeEnabled && (
              <div className="grid grid-cols-2 gap-4 ml-6">
                <div>
                  <label className="block text-sm mb-1">Max Width</label>
                  <input
                    type="number"
                    className="w-full p-2 border rounded-lg"
                    value={optimizationConfig.maxWidth}
                    onChange={(e) => setOptimizationConfig({
                      ...optimizationConfig,
                      maxWidth: parseInt(e.target.value)
                    })}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Max Height</label>
                  <input
                    type="number"
                    className="w-full p-2 border rounded-lg"
                    value={optimizationConfig.maxHeight}
                    onChange={(e) => setOptimizationConfig({
                      ...optimizationConfig,
                      maxHeight: parseInt(e.target.value)
                    })}
                  />
                </div>
              </div>
            )}
          </div>
          {/* Generate Sizes */}
          <div>
            <label className="block text-sm font-medium mb-2">Generate Sizes</label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {presetSizes.map(size => (
                <label key={size.id} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={optimizationConfig.generateSizes.includes(size.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setOptimizationConfig({
                          ...optimizationConfig,
                          generateSizes: [...optimizationConfig.generateSizes, size.id]
                        });
                      } else {
                        setOptimizationConfig({
                          ...optimizationConfig,
                          generateSizes: optimizationConfig.generateSizes.filter(s => s !== size.id)
                        });
                      }
                    }}
                    className="mr-2"
                  />
                  <div>
                    <p className="font-medium">{size.name}</p>
                    <p className="text-xs text-gray-600">{size.width}x{size.height}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
          {/* Additional Options */}
          <div className="space-y-3">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={optimizationConfig.stripMetadata}
                onChange={(e) => setOptimizationConfig({
                  ...optimizationConfig,
                  stripMetadata: e.target.checked
                })}
                className="mr-2"
              />
              <span>Strip metadata (EXIF, IPTC, etc.)</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={optimizationConfig.progressive}
                onChange={(e) => setOptimizationConfig({
                  ...optimizationConfig,
                  progressive: e.target.checked
                })}
                className="mr-2"
              />
              <span>Progressive loading (better perceived performance)</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={optimizationConfig.lazyLoading}
                onChange={(e) => setOptimizationConfig({
                  ...optimizationConfig,
                  lazyLoading: e.target.checked
                })}
                className="mr-2"
              />
              <span>Enable lazy loading for web</span>
            </label>
          </div>
          <div className="flex space-x-2 pt-4">
            <Button
              onClick={() => updateConfig(optimizationConfig)}
            >
              Save Settings
            </Button>
            <Button
              variant="secondary"
              onClick={() => optimizeImages(images.map(img => img.id))}
            >
              Apply to All Images
            </Button>
          </div>
        </div>
      </Card>
      {/* Batch Results */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Recent Optimization Results</h3>
        <div className="space-y-3">
          {[
            { batch: '2023-05-16 10:30', images: 45, before: '125.3 MB', after: '42.1 MB', saved: '66.4%' },
            { batch: '2023-05-15 14:22', images: 32, before: '89.7 MB', after: '31.2 MB', saved: '65.2%' },
            { batch: '2023-05-14 09:15', images: 67, before: '210.5 MB', after: '68.9 MB', saved: '67.3%' },
          ].map((result, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">{result.batch}</p>
                <p className="text-sm text-gray-600">{result.images} images optimized</p>
              </div>
              <div className="text-right">
                <p className="text-sm">
                  {result.before} → {result.after}
                </p>
                <p className="text-sm font-medium text-green-600">
                  {result.saved} saved
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
  const renderSettings = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">Global Image Settings</h3>
        <div className="space-y-4">
          {/* Auto-optimization */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Auto-optimize on upload</p>
              <p className="text-sm text-gray-600">Automatically optimize images when uploaded</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                defaultChecked
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* WebP fallback */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">WebP with fallback</p>
              <p className="text-sm text-gray-600">Serve WebP images with JPEG/PNG fallback</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                defaultChecked
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Responsive images */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Generate responsive sizes</p>
              <p className="text-sm text-gray-600">Create multiple sizes for responsive design</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                defaultChecked
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
          {/* Storage location */}
          <div>
            <label className="block text-sm font-medium mb-2">Storage Location</label>
            <select className="w-full p-2 border rounded-lg">
              <option value="local">Local Storage</option>
              <option value="s3">Amazon S3</option>
              <option value="cloudinary">Cloudinary</option>
              <option value="custom">Custom CDN</option>
            </select>
          </div>
          {/* CDN settings */}
          <div>
            <label className="block text-sm font-medium mb-2">CDN Domain</label>
            <input
              type="text"
              className="w-full p-2 border rounded-lg"
              placeholder="https://cdn.example.com"
              defaultValue="https://cdn.bdc.com"
            />
          </div>
        </div>
      </Card>
      {/* Presets */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Optimization Presets</h3>
        <div className="space-y-3">
          {[
            {
              name: 'High Quality',
              description: 'Minimal compression for best quality',
              quality: 95,
              format: 'original'
            },
            {
              name: 'Balanced',
              description: 'Good balance between quality and size',
              quality: 85,
              format: 'webp'
            },
            {
              name: 'Web Optimized',
              description: 'Optimized for fast web loading',
              quality: 75,
              format: 'webp'
            },
            {
              name: 'Mobile First',
              description: 'Aggressive compression for mobile',
              quality: 65,
              format: 'webp'
            }
          ].map((preset, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">{preset.name}</p>
                  <p className="text-sm text-gray-600">{preset.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Quality: {preset.quality}% | Format: {preset.format}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setOptimizationConfig({
                    ...optimizationConfig,
                    quality: preset.quality,
                    format: preset.format
                  })}
                >
                  Apply
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
      {/* Image Rules */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Image Processing Rules</h3>
        <div className="space-y-3">
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">Avatar Images</h4>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            <p className="text-sm text-gray-600">Square crop, 200x200, high quality</p>
          </div>
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">Document Thumbnails</h4>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            <p className="text-sm text-gray-600">16:9 ratio, 320x180, medium quality</p>
          </div>
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">Content Images</h4>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/10 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            <p className="text-sm text-gray-600">Max 1920px width, responsive sizes, WebP format</p>
          </div>
        </div>
      </Card>
    </div>
  );
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Image Optimization</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary"
        >
          Back to Settings
        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'gallery', 'batch', 'settings'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>
      {/* Tab Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'gallery' && renderGallery()}
      {activeTab === 'batch' && renderBatchOptimization()}
      {activeTab === 'settings' && renderSettings()}
    </div>
  );
};
export default ImageOptimizationPage;