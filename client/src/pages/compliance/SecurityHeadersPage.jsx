// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Settings,
  Copy,
  ExternalLink,
  FileText,
  Lock,
  Globe,
  Eye,
  Code } from
'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../components/ui/use-toast';import { useTranslation } from "react-i18next";
const securityHeaders = [
{
  name: 'Content-Security-Policy',
  description: 'Prevents XSS attacks by controlling resources the browser can load',
  recommended: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;",
  level: 'critical',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP'
},
{
  name: 'X-Frame-Options',
  description: 'Prevents clickjacking by controlling if the page can be embedded in frames',
  recommended: 'DENY',
  level: 'high',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options'
},
{
  name: 'X-Content-Type-Options',
  description: 'Prevents MIME type sniffing',
  recommended: 'nosniff',
  level: 'high',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options'
},
{
  name: 'Strict-Transport-Security',
  description: 'Forces HTTPS connections',
  recommended: 'max-age=31536000; includeSubDomains; preload',
  level: 'critical',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security'
},
{
  name: 'X-XSS-Protection',
  description: 'Enables browser XSS filtering (legacy, but still recommended)',
  recommended: '1; mode=block',
  level: 'medium',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection'
},
{
  name: 'Referrer-Policy',
  description: 'Controls how much referrer information is sent',
  recommended: 'strict-origin-when-cross-origin',
  level: 'medium',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy'
},
{
  name: 'Permissions-Policy',
  description: 'Controls which browser features can be used',
  recommended: 'camera=(), microphone=(), geolocation=()',
  level: 'high',
  docs: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Feature-Policy'
}];

const SecurityHeadersPage = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [currentHeaders, setCurrentHeaders] = useState({});
  const [headerConfig, setHeaderConfig] = useState({});
  const [testResults, setTestResults] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedHeader, setSelectedHeader] = useState(null);
  useEffect(() => {
    fetchCurrentHeaders();
    fetchHeaderConfig();
  }, []);
  const fetchCurrentHeaders = async () => {
    try {
      const response = await fetch('/api/admin/security/headers', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentHeaders(data.headers || {});
      }
    } catch (error) {
      console.error('Error fetching headers:', error);
    }
  };
  const fetchHeaderConfig = async () => {
    try {
      const response = await fetch('/api/admin/security/headers/config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setHeaderConfig(data.config || {});
      }
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };
  const updateHeaderConfig = async (headerName, value) => {
    try {
      const response = await fetch('/api/admin/security/headers/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...headerConfig,
          [headerName]: value
        })
      });
      if (response.ok) {
        setHeaderConfig({ ...headerConfig, [headerName]: value });
        showToast('Header configuration updated', 'success');
      }
    } catch (error) {
      showToast('Error updating configuration', 'error');
    }
  };
  const testHeaders = async (url = window.location.origin) => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/security/headers/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ url })
      });
      if (response.ok) {
        const data = await response.json();
        setTestResults(data.results);
        showToast('Security test completed', 'success');
      }
    } catch (error) {
      showToast('Error running security test', 'error');
    } finally {
      setLoading(false);
    }
  };
  const applyRecommendedSettings = async () => {
    const recommendedConfig = {};
    securityHeaders.forEach((header) => {
      recommendedConfig[header.name] = header.recommended;
    });
    try {
      const response = await fetch('/api/admin/security/headers/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(recommendedConfig)
      });
      if (response.ok) {
        setHeaderConfig(recommendedConfig);
        showToast('Applied recommended security settings', 'success');
      }
    } catch (error) {
      showToast('Error applying settings', 'error');
    }
  };
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showToast('Copied to clipboard', 'success');
  };
  // Spinner component definition
  const Spinner = () =>
  <div className="flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>;

  const getStatusIcon = (header) => {
    const current = currentHeaders[header.name];
    const configured = headerConfig[header.name];
    if (!current && !configured) {
      return <XCircle className="w-5 h-5 text-red-500" />;
    } else if (current === header.recommended || configured === header.recommended) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else {
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };
  const getSeverityColor = (level) => {
    switch (level) {
      case 'critical':
        return 'text-red-600 bg-red-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };
  const renderOverview = () =>
  <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.security_score")}</p>
              <p className="text-2xl font-bold">
                {Math.round(Object.keys(currentHeaders).length / securityHeaders.length * 100)}%
              </p>
            </div>
            <Shield className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.active_headers")}</p>
              <p className="text-2xl font-bold">{Object.keys(currentHeaders).length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.missing_headers")}</p>
              <p className="text-2xl font-bold">
                {securityHeaders.length - Object.keys(currentHeaders).length}
              </p>
            </div>
            <XCircle className="w-8 h-8 text-red-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t("pages.last_test")}</p>
              <p className="text-sm font-medium">
                {testResults ? new Date(testResults.timestamp).toLocaleDateString() : 'Never'}
              </p>
            </div>
            <Clock className="w-8 h-8 text-gray-600" />
          </div>
        </Card>
      </div>
      {/* Headers List */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-lg">{t("pages.security_headers")}</h3>
          <div className="space-x-2">
            <Button
            onClick={() => testHeaders()}
            disabled={loading}
            size="sm">

              <Shield className="w-4 h-4 mr-2" />{t("pages.test_security")}

          </Button>
            <Button
            onClick={applyRecommendedSettings}
            variant="secondary"
            size="sm">{t("pages.apply_recommended")}


          </Button>
          </div>
        </div>
        <div className="space-y-4">
          {securityHeaders.map((header) =>
        <div key={header.name} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(header)}
                    <h4 className="font-medium">{header.name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(header.level)}`}>
                      {header.level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{header.description}</p>
                  {/* Current Value */}
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs font-medium text-gray-500">{t("pages.current_value")}</p>
                      <p className="text-sm font-mono bg-gray-50 p-2 rounded">
                        {currentHeaders[header.name] || 'Not set'}
                      </p>
                    </div>
                    {/* Recommended Value */}
                    <div>
                      <p className="text-xs font-medium text-gray-500">{t("pages.recommended")}</p>
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-mono bg-green-50 p-2 rounded flex-1">
                          {header.recommended}
                        </p>
                        <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(header.recommended)}>

                          <Copy className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="ml-4 space-x-2">
                  <Button
                size="sm"
                variant="ghost"
                onClick={() => setSelectedHeader(header)}>

                    <Settings className="w-4 h-4" />
                  </Button>
                  <Button
                size="sm"
                variant="ghost"
                onClick={() => window.open(header.docs, '_blank')}>

                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
        )}
        </div>
      </Card>
    </div>;

  const renderConfiguration = () =>
  <div className="space-y-6">
      <Card>
        <h3 className="font-semibold text-lg mb-4">{t("pages.header_configuration")}</h3>
        <div className="space-y-4">
          {securityHeaders.map((header) =>
        <div key={header.name} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{header.name}</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(header.level)}`}>
                  {header.level}
                </span>
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium">{t("components.value")}</label>
                <textarea
              className="w-full p-2 border rounded-lg font-mono text-sm"
              rows="3"
              value={headerConfig[header.name] || ''}
              onChange={(e) => updateHeaderConfig(header.name, e.target.value)}
              placeholder={header.recommended} />

                <div className="flex justify-between items-center">
                  <Button
                size="sm"
                variant="secondary"
                onClick={() => updateHeaderConfig(header.name, header.recommended)}>{t("pages.use_recommended")}


              </Button>
                  <Button
                size="sm"
                variant="ghost"
                onClick={() => window.open(header.docs, '_blank')}>

                    <ExternalLink className="w-4 h-4 mr-2" />{t("components.documentation")}

              </Button>
                </div>
              </div>
            </div>
        )}
        </div>
      </Card>
      {/* Implementation Guide */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Implementation Guide</h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">{t("pages.nginx_configuration")}</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`# Add to your nginx server block
${securityHeaders.map((header) =>
              `add_header ${header.name} "${headerConfig[header.name] || header.recommended}";`
              ).join('\n')}`}</code>
            </pre>
            <Button
            size="sm"
            variant="secondary"
            className="mt-2"
            onClick={() => copyToClipboard(
              securityHeaders.map((header) =>
              `add_header ${header.name} "${headerConfig[header.name] || header.recommended}";`
              ).join('\n')
            )}>

              <Copy className="w-4 h-4 mr-2" />{t("pages.copy_nginx_config")}

          </Button>
          </div>
          <div>
            <h4 className="font-medium mb-2">{t("pages.apache_configuration")}</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`# Add to your .htaccess or Apache config
${securityHeaders.map((header) =>
              `Header set ${header.name} "${headerConfig[header.name] || header.recommended}"`
              ).join('\n')}`}</code>
            </pre>
            <Button
            size="sm"
            variant="secondary"
            className="mt-2"
            onClick={() => copyToClipboard(
              securityHeaders.map((header) =>
              `Header set ${header.name} "${headerConfig[header.name] || header.recommended}"`
              ).join('\n')
            )}>

              <Copy className="w-4 h-4 mr-2" />{t("pages.copy_apache_config")}

          </Button>
          </div>
          <div>
            <h4 className="font-medium mb-2">Express.js Middleware</h4>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
              <code>{`// Add to your Express app
app.use((req, res, next) => {
${securityHeaders.map((header) =>
              `  res.setHeader('${header.name}', '${headerConfig[header.name] || header.recommended}');`
              ).join('\n')}
  next();
});`}</code>
            </pre>
            <Button
            size="sm"
            variant="secondary"
            className="mt-2"
            onClick={() => copyToClipboard(
              `app.use((req, res, next) => {\n${securityHeaders.map((header) =>
              `  res.setHeader('${header.name}', '${headerConfig[header.name] || header.recommended}');`
              ).join('\n')}\n  next();\n});`
            )}>

              <Copy className="w-4 h-4 mr-2" />{t("pages.copy_express_config")}

          </Button>
          </div>
        </div>
      </Card>
    </div>;

  const renderTestResults = () =>
  <div className="space-y-6">
      {testResults ?
    <>
          <Card>
            <h3 className="font-semibold text-lg mb-4">{t("pages.latest_security_test_results")}</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">{t("pages.test_date")}</p>
                  <p className="font-medium">{new Date(testResults.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t("pages.url_tested")}</p>
                  <p className="font-medium">{testResults.url}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t("pages.overall_score")}</p>
                  <p className="text-2xl font-bold">{testResults.score}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t("pages.grade")}</p>
                  <p className="text-2xl font-bold">{testResults.grade}</p>
                </div>
              </div>
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">{t("pages.header_analysis")}</h4>
                <div className="space-y-3">
                  {testResults.headers.map((result, index) =>
              <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {result.present ?
                  <CheckCircle className="w-5 h-5 text-green-500" /> :

                  <XCircle className="w-5 h-5 text-red-500" />
                  }
                        <span className="font-medium">{result.name}</span>
                      </div>
                      <span className={`text-sm ${result.valid ? 'text-green-600' : 'text-red-600'}`}>
                        {result.present ? result.valid ? 'Valid' : 'Invalid' : 'Missing'}
                      </span>
                    </div>
              )}
                </div>
              </div>
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">{t("components.recommendations")}</h4>
                <ul className="space-y-2">
                  {testResults.recommendations.map((rec, index) =>
              <li key={index} className="flex items-start space-x-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                      <span className="text-sm">{rec}</span>
                    </li>
              )}
                </ul>
              </div>
            </div>
          </Card>
        </> :

    <Card>
          <div className="text-center py-12">
            <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">{t("pages.no_security_test_results_available")}</p>
            <Button
          onClick={() => testHeaders()}
          className="mt-4"
          disabled={loading}>{t("pages.run_security_test")}


        </Button>
          </div>
        </Card>
    }
    </div>;

  const renderSelectedHeader = () =>
  selectedHeader &&
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-semibold text-lg">{selectedHeader.name}</h3>
            <Button
          size="sm"
          variant="ghost"
          onClick={() => setSelectedHeader(null)}>

              <XCircle className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-4">
            <div>
              <p className="font-medium mb-1">{t("components.description")}</p>
              <p className="text-sm text-gray-600">{selectedHeader.description}</p>
            </div>
            <div>
              <p className="font-medium mb-1">{t("pages.security_level")}</p>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(selectedHeader.level)}`}>
                {selectedHeader.level}
              </span>
            </div>
            <div>
              <p className="font-medium mb-1">{t("pages.current_value")}</p>
              <pre className="bg-gray-50 p-3 rounded text-sm">
                {currentHeaders[selectedHeader.name] || 'Not set'}
              </pre>
            </div>
            <div>
              <p className="font-medium mb-1">{t("pages.recommended_value")}</p>
              <pre className="bg-green-50 p-3 rounded text-sm">
                {selectedHeader.recommended}
              </pre>
            </div>
            <div>
              <p className="font-medium mb-1">{t("components.documentation")}</p>
              <a
            href={selectedHeader.docs}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-primary hover:underline">{t("pages.read_more")}

            <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            </div>
            <div className="pt-4 border-t space-x-2">
              <Button
            onClick={() => {
              updateHeaderConfig(selectedHeader.name, selectedHeader.recommended);
              setSelectedHeader(null);
            }}>{t("pages.apply_recommended")}


          </Button>
              <Button
            variant="secondary"
            onClick={() => setSelectedHeader(null)}>{t("components.close")}


          </Button>
            </div>
          </div>
        </Card>
      </div>;


  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t("pages.security_headers")}</h1>
        <Button
          onClick={() => navigate('/settings')}
          variant="secondary">{t("pages.back_to_settings")}


        </Button>
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'configuration', 'test-results'].map((tab) =>
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab ?
            'border-primary text-primary' :
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`
            }>

              {tab.replace('-', ' ')}
            </button>
          )}
        </nav>
      </div>
      {/* Tab Content */}
      {loading ?
      <div className="flex justify-center py-12">
          <Spinner />
        </div> :

      <>
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'configuration' && renderConfiguration()}
          {activeTab === 'test-results' && renderTestResults()}
        </>
      }
      {renderSelectedHeader()}
    </div>);

};
export default SecurityHeadersPage;