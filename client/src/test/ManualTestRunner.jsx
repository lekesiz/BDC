import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, AlertCircle, Play, RefreshCw } from 'lucide-react';

const pagesToTest = [
  // Dashboard
  { path: '/dashboard', name: 'Dashboard' },
  
  // Beneficiaries
  { path: '/beneficiaries', name: 'Beneficiaries List' },
  { path: '/beneficiaries/create', name: 'Create Beneficiary' },
  
  // Programs
  { path: '/programs', name: 'Programs List' },
  { path: '/programs/create', name: 'Create Program' },
  
  // Evaluations
  { path: '/evaluations', name: 'Evaluations' },
  { path: '/evaluations/templates', name: 'Evaluation Templates' },
  { path: '/evaluations/create', name: 'Create Evaluation' },
  
  // Calendar
  { path: '/calendar', name: 'Calendar' },
  { path: '/appointments', name: 'Appointments' },
  
  // Documents
  { path: '/documents', name: 'Documents' },
  { path: '/documents/upload', name: 'Upload Document' },
  { path: '/documents/templates', name: 'Document Templates' },
  
  // Messages
  { path: '/messages', name: 'Messages' },
  { path: '/notifications', name: 'Notifications' },
  
  // Analytics
  { path: '/analytics', name: 'Analytics Dashboard' },
  { path: '/analytics/beneficiaries', name: 'Beneficiary Analytics' },
  { path: '/analytics/programs', name: 'Program Analytics' },
  { path: '/analytics/performance', name: 'Performance Analytics' },
  
  // Reports
  { path: '/reports', name: 'Reports' },
  { path: '/reports/create', name: 'Create Report' },
  { path: '/reports/scheduled', name: 'Scheduled Reports' },
  
  // Settings
  { path: '/settings', name: 'Settings' },
  { path: '/settings/profile', name: 'Profile Settings' },
  { path: '/settings/security', name: 'Security Settings' },
  { path: '/settings/notifications', name: 'Notification Settings' },
  { path: '/settings/ai', name: 'AI Settings' }
];

const ManualTestRunner = () => {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [testResults, setTestResults] = useState({});
  const [isRunning, setIsRunning] = useState(false);
  const [errors, setErrors] = useState([]);

  // Capture console errors
  useEffect(() => {
    const originalError = console.error;
    const capturedErrors = [];
    
    console.error = (...args) => {
      capturedErrors.push({
        timestamp: new Date().toISOString(),
        message: args.join(' ')
      });
      originalError.apply(console, args);
    };

    const interval = setInterval(() => {
      if (capturedErrors.length > 0) {
        setErrors(prev => [...prev, ...capturedErrors]);
        capturedErrors.length = 0;
      }
    }, 1000);

    return () => {
      console.error = originalError;
      clearInterval(interval);
    };
  }, []);

  const testCurrentPage = () => {
    const currentPage = pagesToTest[currentIndex];
    navigate(currentPage.path);
    
    // Mark as tested after navigation
    setTestResults(prev => ({
      ...prev,
      [currentPage.path]: {
        name: currentPage.name,
        status: 'tested',
        timestamp: new Date().toISOString()
      }
    }));
  };

  const nextPage = () => {
    if (currentIndex < pagesToTest.length - 1) {
      setCurrentIndex(currentIndex + 1);
      testCurrentPage();
    } else {
      setIsRunning(false);
    }
  };

  const startTesting = () => {
    setIsRunning(true);
    setCurrentIndex(0);
    setTestResults({});
    setErrors([]);
    testCurrentPage();
  };

  const markCurrent = (status) => {
    const currentPage = pagesToTest[currentIndex];
    setTestResults(prev => ({
      ...prev,
      [currentPage.path]: {
        ...prev[currentPage.path],
        status,
        errors: errors.filter(e => 
          new Date(e.timestamp).getTime() > new Date(prev[currentPage.path]?.timestamp || 0).getTime()
        )
      }
    }));
    setErrors([]);
  };

  const getStats = () => {
    const results = Object.values(testResults);
    return {
      total: pagesToTest.length,
      tested: results.length,
      passed: results.filter(r => r.status === 'passed').length,
      failed: results.filter(r => r.status === 'failed').length,
      warnings: results.filter(r => r.status === 'warning').length
    };
  };

  const stats = getStats();

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-2xl border border-gray-200 z-50">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Play className="w-5 h-5" />
          Frontend Test Runner
        </h3>
        <div className="mt-2 text-sm text-gray-600">
          Progress: {stats.tested}/{stats.total} pages
        </div>
      </div>

      <div className="p-4 space-y-3">
        {isRunning && (
          <div className="bg-blue-50 p-3 rounded">
            <div className="font-medium text-blue-900">
              Testing: {pagesToTest[currentIndex].name}
            </div>
            <div className="text-sm text-blue-700 mt-1">
              {pagesToTest[currentIndex].path}
            </div>
            {errors.length > 0 && (
              <div className="mt-2 text-xs text-red-600">
                {errors.length} console error(s) detected
              </div>
            )}
          </div>
        )}

        <div className="flex gap-2">
          {!isRunning ? (
            <button
              onClick={startTesting}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4" />
              Start Testing
            </button>
          ) : (
            <>
              <button
                onClick={() => { markCurrent('passed'); nextPage(); }}
                className="flex-1 bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700 flex items-center justify-center gap-1"
              >
                <CheckCircle className="w-4 h-4" />
                Pass
              </button>
              <button
                onClick={() => { markCurrent('warning'); nextPage(); }}
                className="flex-1 bg-yellow-600 text-white px-3 py-2 rounded hover:bg-yellow-700 flex items-center justify-center gap-1"
              >
                <AlertCircle className="w-4 h-4" />
                Warning
              </button>
              <button
                onClick={() => { markCurrent('failed'); nextPage(); }}
                className="flex-1 bg-red-600 text-white px-3 py-2 rounded hover:bg-red-700 flex items-center justify-center gap-1"
              >
                <XCircle className="w-4 h-4" />
                Fail
              </button>
              <button
                onClick={nextPage}
                className="px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Skip
              </button>
            </>
          )}
        </div>

        <div className="grid grid-cols-4 gap-2 text-center text-sm">
          <div className="bg-green-50 p-2 rounded">
            <div className="font-semibold text-green-700">{stats.passed}</div>
            <div className="text-xs text-green-600">Passed</div>
          </div>
          <div className="bg-yellow-50 p-2 rounded">
            <div className="font-semibold text-yellow-700">{stats.warnings}</div>
            <div className="text-xs text-yellow-600">Warnings</div>
          </div>
          <div className="bg-red-50 p-2 rounded">
            <div className="font-semibold text-red-700">{stats.failed}</div>
            <div className="text-xs text-red-600">Failed</div>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <div className="font-semibold text-gray-700">{stats.total - stats.tested}</div>
            <div className="text-xs text-gray-600">Remaining</div>
          </div>
        </div>

        {Object.entries(testResults).length > 0 && (
          <div className="max-h-40 overflow-y-auto border-t pt-2">
            <div className="text-xs font-medium text-gray-600 mb-1">Test Results:</div>
            {Object.entries(testResults).map(([path, result]) => (
              <div key={path} className="flex items-center gap-2 text-xs py-1">
                {result.status === 'passed' && <CheckCircle className="w-3 h-3 text-green-600" />}
                {result.status === 'warning' && <AlertCircle className="w-3 h-3 text-yellow-600" />}
                {result.status === 'failed' && <XCircle className="w-3 h-3 text-red-600" />}
                <span className={
                  result.status === 'passed' ? 'text-green-700' :
                  result.status === 'warning' ? 'text-yellow-700' :
                  result.status === 'failed' ? 'text-red-700' :
                  'text-gray-600'
                }>
                  {result.name}
                </span>
                {result.errors?.length > 0 && (
                  <span className="text-red-500 text-xs">({result.errors.length} errors)</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManualTestRunner;