import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Globe, 
  Zap, 
  Shield, 
  BarChart3,
  Server,
  MapPin,
  Activity,
  Settings,
  FileText,
  Image,
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Code
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CDNSetupPage = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [cdnProviders, setCdnProviders] = useState([]);
  const [currentProvider, setCurrentProvider] = useState(null);
  const [cdnStats, setCdnStats] = useState({
    hitRate: 89,
    bandwidth: '12.5 TB',
    requests: '145M',
    avgLatency: '45ms'
  });

  useEffect(() => {
    const mockProviders = [
      { name: 'CloudFlare', status: 'active', price: '$20/month', features: ['DDoS Protection', 'SSL', 'Analytics'] },
      { name: 'AWS CloudFront', status: 'available', price: '$0.085/GB', features: ['AWS Integration', 'Edge Functions'] },
      { name: 'Fastly', status: 'available', price: '$0.12/GB', features: ['Real-time Analytics', 'Instant Purge'] },
      { name: 'Akamai', status: 'enterprise', price: 'Custom', features: ['Enterprise Support', 'Advanced Security'] }
    ];
    setCdnProviders(mockProviders);
    setCurrentProvider(mockProviders[0]);
  }, []);

  const performanceData = [
    { time: '00:00', cdn: 45, origin: 250 },
    { time: '04:00', cdn: 38, origin: 220 },
    { time: '08:00', cdn: 52, origin: 380 },
    { time: '12:00', cdn: 65, origin: 450 },
    { time: '16:00', cdn: 58, origin: 420 },
    { time: '20:00', cdn: 48, origin: 280 },
    { time: '24:00', cdn: 42, origin: 240 }
  ];

  const edgeLocations = [
    { region: 'North America', servers: 45, coverage: 98 },
    { region: 'Europe', servers: 38, coverage: 95 },
    { region: 'Asia Pacific', servers: 52, coverage: 92 },
    { region: 'South America', servers: 15, coverage: 85 },
    { region: 'Africa', servers: 8, coverage: 70 },
    { region: 'Middle East', servers: 12, coverage: 80 }
  ];

  const contentTypes = [
    { type: 'Images', size: '5.8GB', percentage: 45 },
    { type: 'JavaScript', size: '2.1GB', percentage: 18 },
    { type: 'CSS', size: '1.2GB', percentage: 10 },
    { type: 'Videos', size: '3.1GB', percentage: 25 },
    { type: 'Others', size: '0.3GB', percentage: 2 }
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'providers', label: 'CDN Providers', icon: Globe },
    { id: 'configuration', label: 'Configuration', icon: Settings },
    { id: 'performance', label: 'Performance', icon: Zap },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'implementation', label: 'Implementation', icon: Code }
  ];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">CDN Setup & Management</h1>
        <Button variant="primary">
          <Settings className="w-4 h-4 mr-2" />
          Configure CDN
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
                    <p className="text-sm text-gray-600">Cache Hit Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{cdnStats.hitRate}%</p>
                  </div>
                  <Activity className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Bandwidth Served</p>
                    <p className="text-2xl font-bold text-gray-900">{cdnStats.bandwidth}</p>
                  </div>
                  <Server className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Requests</p>
                    <p className="text-2xl font-bold text-gray-900">{cdnStats.requests}</p>
                  </div>
                  <Globe className="w-8 h-8 text-purple-500" />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Avg Latency</p>
                    <p className="text-2xl font-bold text-gray-900">{cdnStats.avgLatency}</p>
                  </div>
                  <Zap className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">CDN vs Origin Response Time</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="cdn" stroke="#22c55e" name="CDN (ms)" />
                      <Line type="monotone" dataKey="origin" stroke="#ef4444" name="Origin (ms)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Content Type Distribution</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={contentTypes}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ type, percentage }) => `${type} (${percentage}%)`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="percentage"
                      >
                        {contentTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Card>
          </div>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Edge Server Locations</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Region</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Edge Servers</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coverage</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {edgeLocations.map((location) => (
                      <tr key={location.region}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          <div className="flex items-center">
                            <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                            {location.region}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{location.servers}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                              <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${location.coverage}%` }}></div>
                            </div>
                            <span className="text-sm text-gray-900">{location.coverage}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Active
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

      {activeTab === 'providers' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Available CDN Providers</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {cdnProviders.map((provider) => (
                  <div key={provider.name} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-lg font-medium">{provider.name}</h4>
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                        ${provider.status === 'active' ? 'bg-green-100 text-green-800' : 
                          provider.status === 'available' ? 'bg-gray-100 text-gray-800' :
                          'bg-purple-100 text-purple-800'}`}>
                        {provider.status}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-3">{provider.price}</p>
                    <div className="space-y-1">
                      {provider.features.map((feature, index) => (
                        <div key={index} className="flex items-center text-sm">
                          <CheckCircle className="w-4 h-4 mr-1 text-green-500" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4">
                      <Button 
                        variant={provider.status === 'active' ? 'secondary' : 'primary'}
                        size="sm"
                        className="w-full"
                      >
                        {provider.status === 'active' ? 'Current Provider' : 'Select Provider'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'configuration' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">CDN Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    CDN URL
                  </label>
                  <Input type="text" defaultValue="cdn.yourdomain.com" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Origin Server
                  </label>
                  <Input type="text" defaultValue="origin.yourdomain.com" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cache TTL (seconds)
                  </label>
                  <Input type="number" defaultValue="3600" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    File Types to Cache
                  </label>
                  <Input type="text" defaultValue="jpg,png,webp,css,js,woff2" />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Purge Cache</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Purge Type
                  </label>
                  <select className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                    <option>Purge Everything</option>
                    <option>Purge by URL</option>
                    <option>Purge by Tag</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL Pattern (optional)
                  </label>
                  <Input type="text" placeholder="/assets/images/*" />
                </div>

                <Button variant="danger">
                  Purge Cache
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'performance' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Analytics</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="cdn" stackId="1" stroke="#3B82F6" fill="#3B82F6" />
                    <Area type="monotone" dataKey="origin" stackId="1" stroke="#EF4444" fill="#EF4444" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="p-6">
                <h4 className="text-sm font-medium text-gray-600">Cache Status</h4>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">HIT</span>
                    <span className="text-sm font-medium">89%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">MISS</span>
                    <span className="text-sm font-medium">8%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">BYPASS</span>
                    <span className="text-sm font-medium">3%</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h4 className="text-sm font-medium text-gray-600">Bandwidth Usage</h4>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Cached</span>
                    <span className="text-sm font-medium">10.2 TB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Uncached</span>
                    <span className="text-sm font-medium">2.3 TB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Saved</span>
                    <span className="text-sm font-medium text-green-600">81.6%</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h4 className="text-sm font-medium text-gray-600">Request Statistics</h4>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total</span>
                    <span className="text-sm font-medium">145M</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Unique Visitors</span>
                    <span className="text-sm font-medium">2.1M</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Page Views</span>
                    <span className="text-sm font-medium">8.5M</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm font-medium text-gray-700">Enable DDoS Protection</span>
                  </label>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm font-medium text-gray-700">Always Use HTTPS</span>
                  </label>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm font-medium text-gray-700">Enable Web Application Firewall (WAF)</span>
                  </label>
                </div>

                <div>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm font-medium text-gray-700">Block Traffic from Specific Countries</span>
                  </label>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">SSL/TLS Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SSL Mode
                  </label>
                  <select className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                    <option>Full (strict)</option>
                    <option>Full</option>
                    <option>Flexible</option>
                    <option>Off</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum TLS Version
                  </label>
                  <select className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                    <option>TLS 1.3</option>
                    <option>TLS 1.2</option>
                    <option>TLS 1.1</option>
                  </select>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'implementation' && (
        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">CloudFlare Setup</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`# DNS Configuration
cdn.yourdomain.com  CNAME  yourdomain.cdn.cloudflare.com

# Page Rules
*.css -> Cache Everything, Edge Cache TTL: 1 month
*.js -> Cache Everything, Edge Cache TTL: 1 month
*.jpg|*.png|*.webp -> Cache Everything, Edge Cache TTL: 1 year
/api/* -> Cache Bypass

# Cloudflare Workers Script
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  const newHeaders = new Headers(response.headers)
  
  // Add security headers
  newHeaders.set('X-Content-Type-Options', 'nosniff')
  newHeaders.set('X-Frame-Options', 'DENY')
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  })
}`}</code>
              </pre>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">AWS CloudFront Setup</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`# CloudFormation Template
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Distribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: origin.yourdomain.com
            Id: myOrigin
            CustomOriginConfig:
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: myOrigin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
        PriceClass: PriceClass_100
        ViewerCertificate:
          CloudFrontDefaultCertificate: true`}</code>
              </pre>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">React CDN Integration</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <code>{`// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      }
    }
  },
  base: process.env.NODE_ENV === 'production' 
    ? 'https://cdn.yourdomain.com/' 
    : '/'
}

// .env.production
VITE_CDN_URL=https://cdn.yourdomain.com

// Asset helper
export const getCDNUrl = (path) => {
  const baseUrl = import.meta.env.VITE_CDN_URL || ''
  return \`\${baseUrl}\${path}\`
}`}</code>
              </pre>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default CDNSetupPage;