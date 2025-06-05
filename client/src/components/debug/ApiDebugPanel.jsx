import React, { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
const ApiDebugPanel = () => {
  const [tests, setTests] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [config, setConfig] = useState({});
  useEffect(() => {
    // Get API configuration
    setConfig({
      baseURL: api.defaults.baseURL,
      env: import.meta.env.MODE,
      mockApi: import.meta.env.VITE_USE_MOCK_API,
      apiUrl: import.meta.env.VITE_API_URL,
      withCredentials: api.defaults.withCredentials,
      headers: api.defaults.headers.common
    });
  }, []);
  const runTests = async () => {
    setIsRunning(true);
    setTests([]);
    const testCases = [
      {
        name: 'Basic Connectivity',
        endpoint: '/api/health',
        method: 'GET',
        auth: false
      },
      {
        name: 'Auth Debug',
        endpoint: '/api/auth/debug',
        method: 'GET',
        auth: false
      },
      {
        name: 'Login Test',
        endpoint: '/api/auth/login',
        method: 'POST',
        auth: false,
        data: {
          email: 'admin@bdc.com',
          password: 'admin123',
          remember: true
        }
      },
      {
        name: 'Get Current User',
        endpoint: '/api/users/me',
        method: 'GET',
        auth: true
      },
      {
        name: 'Get Beneficiaries',
        endpoint: '/api/beneficiaries',
        method: 'GET',
        auth: true
      }
    ];
    let token = null;
    for (const test of testCases) {
      const startTime = Date.now();
      let result = {
        name: test.name,
        endpoint: test.endpoint,
        method: test.method,
        status: 'pending',
        time: 0,
        response: null,
        error: null
      };
      try {
        let response;
        const headers = test.auth && token ? { Authorization: `Bearer ${token}` } : {};
        if (test.method === 'GET') {
          response = await api.get(test.endpoint, { headers });
        } else if (test.method === 'POST') {
          response = await api.post(test.endpoint, test.data, { headers });
        }
        result.status = 'success';
        result.response = response.data;
        result.statusCode = response.status;
        result.time = Date.now() - startTime;
        // Store token from login
        if (test.name === 'Login Test' && response.data.access_token) {
          token = response.data.access_token;
          localStorage.setItem('access_token', token);
        }
      } catch (error) {
        result.status = 'error';
        result.error = error.message;
        result.statusCode = error.response?.status;
        result.time = Date.now() - startTime;
        result.response = error.response?.data;
      }
      setTests(prev => [...prev, result]);
      await new Promise(resolve => setTimeout(resolve, 100)); // Small delay between tests
    }
    setIsRunning(false);
  };
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };
  const getStatusBadge = (statusCode) => {
    if (!statusCode) return null;
    const variant = statusCode < 400 ? 'success' : 'destructive';
    return <Badge variant={variant}>{statusCode}</Badge>;
  };
  return (
    <div className="p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>API Debug Panel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Base URL:</div>
              <div className="font-mono">{config.baseURL}</div>
              <div>Environment:</div>
              <div className="font-mono">{config.env}</div>
              <div>Mock API:</div>
              <div className="font-mono">{config.mockApi || 'false'}</div>
              <div>API URL:</div>
              <div className="font-mono">{config.apiUrl}</div>
              <div>With Credentials:</div>
              <div className="font-mono">{String(config.withCredentials)}</div>
            </div>
            <Button 
              onClick={runTests} 
              disabled={isRunning}
              className="w-full"
            >
              {isRunning && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isRunning ? 'Running Tests...' : 'Run Connection Tests'}
            </Button>
            {tests.length > 0 && (
              <div className="space-y-2">
                {tests.map((test, index) => (
                  <Card key={index} className="p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(test.status)}
                        <span className="font-medium">{test.name}</span>
                        <span className="text-sm text-gray-500">
                          {test.method} {test.endpoint}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(test.statusCode)}
                        <span className="text-sm text-gray-500">{test.time}ms</span>
                      </div>
                    </div>
                    {test.error && (
                      <div className="mt-2 text-sm text-red-600">
                        Error: {test.error}
                      </div>
                    )}
                    {test.response && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-sm text-gray-600">
                          Response Data
                        </summary>
                        <pre className="mt-1 text-xs bg-gray-100 p-2 rounded overflow-auto">
                          {JSON.stringify(test.response, null, 2)}
                        </pre>
                      </details>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
export default ApiDebugPanel;