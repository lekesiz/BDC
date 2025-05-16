import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { 
  FileArchive, 
  Activity, 
  Settings, 
  Download,
  Upload,
  BarChart,
  Code,
  Shield,
  Zap,
  Server,
  Globe,
  Monitor
} from 'lucide-react';
import { LineChart, Line, BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CompressionPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [endpoints, setEndpoints] = useState([]);
  const [compressionStats, setCompressionStats] = useState({
    avgCompression: 71,
    totalSaved: '2.8GB',
    responseTime: -32,
    requestsPerDay: 145000
  });

  useEffect(() => {
    const mockEndpoints = [
      { path: '/api/users', compression: 'gzip', ratio: 82, size: '342KB', compressed: '62KB' },
      { path: '/api/beneficiaries', compression: 'brotli', ratio: 87, size: '1.2MB', compressed: '156KB' },
      { path: '/api/reports/data', compression: 'gzip', ratio: 91, size: '4.5MB', compressed: '405KB' },
      { path: '/api/documents/list', compression: 'brotli', ratio: 76, size: '856KB', compressed: '205KB' },
      { path: '/api/analytics', compression: 'gzip', ratio: 68, size: '2.1MB', compressed: '672KB' }
    ];
    setEndpoints(mockEndpoints);
  }, []);

  const performanceData = [
    { time: '00:00', uncompressed: 450, compressed: 120 },
    { time: '04:00', uncompressed: 380, compressed: 95 },
    { time: '08:00', uncompressed: 620, compressed: 165 },
    { time: '12:00', uncompressed: 820, compressed: 210 },
    { time: '16:00', uncompressed: 750, compressed: 185 },
    { time: '20:00', uncompressed: 540, compressed: 140 },
    { time: '24:00', uncompressed: 410, compressed: 105 }
  ];

  const compressionMethods = [
    { name: 'Gzip', ratio: 72, browser: '95%', speed: 'Fast' },
    { name: 'Brotli', ratio: 85, browser: '93%', speed: 'Medium' },
    { name: 'Deflate', ratio: 68, browser: '99%', speed: 'Very Fast' },
    { name: 'Zstd', ratio: 88, browser: '45%', speed: 'Slow' }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart },
    { id: 'endpoints', label: 'Endpoints', icon: Globe },
    { id: 'configuration', label: 'Configuration', icon: Settings },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'implementation', label: 'Implementation', icon: Code }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">API Response Compression</h1>
        <Button variant="primary">
          <Settings className="w-4 h-4 mr-2" />
          Configure Compression
        </Button>
      </div>

      <div className="bg-white border-b">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Average Compression</p>
                    <p className="text-2xl font-bold text-gray-900">{compressionStats.avgCompression}%</p>
                  </div>
                  <FileArchive className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Bandwidth Saved</p>
                    <p className="text-2xl font-bold text-gray-900">{compressionStats.totalSaved}</p>
                  </div>
                  <Download className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Response Time</p>
                    <p className="text-2xl font-bold text-gray-900">{compressionStats.responseTime}%</p>
                  </div>
                  <Zap className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Requests/Day</p>
                    <p className="text-2xl font-bold text-gray-900">{compressionStats.requestsPerDay.toLocaleString()}</p>
                  </div>
                  <Activity className="w-8 h-8 text-purple-500" />
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Response Time Comparison</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="uncompressed" stroke="#ef4444" name="Uncompressed (ms)" />
                    <Line type="monotone" dataKey="compressed" stroke="#22c55e" name="Compressed (ms)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Compression Methods</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compression Ratio</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Browser Support</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Speed</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {compressionMethods.map((method) => (
                      <tr key={method.name}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{method.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                              <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${method.ratio}%` }}></div>
                            </div>
                            <span className="text-sm text-gray-900">{method.ratio}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{method.browser}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            method.speed === 'Very Fast' ? 'bg-green-100 text-green-800' :
                            method.speed === 'Fast' ? 'bg-blue-100 text-blue-800' :
                            method.speed === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {method.speed}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'endpoints' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Endpoint Compression Status</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Endpoint</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ratio</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Original Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compressed Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {endpoints.map((endpoint, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{endpoint.path}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                            {endpoint.compression}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                              <div className="bg-green-600 h-2 rounded-full" style={{ width: `${endpoint.ratio}%` }}></div>
                            </div>
                            <span className="text-sm text-gray-900">{endpoint.ratio}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.size}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.compressed}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <Button variant="ghost" size="sm">
                            <Settings className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'configuration' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Compression Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Compression Method
                  </label>
                  <select className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                    <option>Gzip</option>
                    <option>Brotli</option>
                    <option>Deflate</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Compression Level (1-9)
                  </label>
                  <Input type="number" min="1" max="9" defaultValue="6" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Response Size (bytes)
                  </label>
                  <Input type="number" defaultValue="1024" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Excluded Content Types
                  </label>
                  <Input type="text" placeholder="image/jpeg, video/mp4" />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm font-medium text-gray-700">Enable Dynamic Compression</span>
                  </label>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm font-medium text-gray-700">Cache Compressed Responses</span>
                  </label>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm font-medium text-gray-700">Enable Compression for Localhost</span>
                  </label>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'performance' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Real-time Performance Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">CPU Usage</p>
                      <p className="text-xl font-bold text-gray-900">12%</p>
                    </div>
                    <Monitor className="w-6 h-6 text-blue-500" />
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Memory Usage</p>
                      <p className="text-xl font-bold text-gray-900">185MB</p>
                    </div>
                    <Server className="w-6 h-6 text-green-500" />
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Network I/O</p>
                      <p className="text-xl font-bold text-gray-900">2.4MB/s</p>
                    </div>
                    <Activity className="w-6 h-6 text-purple-500" />
                  </div>
                </div>
              </div>

              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsBarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="uncompressed" fill="#f59e0b" name="Uncompressed" />
                    <Bar dataKey="compressed" fill="#06b6d4" name="Compressed" />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'implementation' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Flask Implementation</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`from flask import Flask, jsonify
from flask_compress import Compress

app = Flask(__name__)

# Initialize Flask-Compress
compress = Compress()
compress.init_app(app)

# Configuration
app.config['COMPRESS_ALGORITHM'] = 'gzip'
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml',
    'application/json', 'application/javascript'
]`}</code>
              </pre>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Express.js Implementation</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`const express = require('express');
const compression = require('compression');

const app = express();

// Use compression middleware
app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
  level: 6,
  threshold: 1024,
  memLevel: 8
}));`}</code>
              </pre>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Nginx Configuration</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`# Enable gzip compression
gzip on;
gzip_types text/plain text/css text/xml text/javascript 
           application/javascript application/xml+rss 
           application/json;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_min_length 1000;
gzip_disable "msie6";

# Enable Brotli compression
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css text/xml text/javascript 
             application/javascript application/json;`}</code>
              </pre>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default CompressionPage;