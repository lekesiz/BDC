// Comprehensive page testing script for BDC frontend
// Run this in the browser console after logging in

const testResults = {
  passed: [],
  failed: [],
  errors: []
};

// Helper function to wait for navigation
const waitForNavigation = (ms = 1000) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to check for console errors
const captureConsoleErrors = () => {
  const errors = [];
  const originalError = console.error;
  console.error = (...args) => {
    errors.push(args.join(' '));
    originalError.apply(console, args);
  };
  return { errors, restore: () => { console.error = originalError; } };
};

// Test a single page
const testPage = async (path, name) => {
  console.log(`\n🧪 Testing: ${name} (${path})`);
  
  const errorCapture = captureConsoleErrors();
  
  try {
    // Navigate to the page
    window.location.href = path;
    await waitForNavigation(2000);
    
    // Check if page loaded
    const hasContent = document.querySelector('main') || document.querySelector('#root');
    if (!hasContent) {
      throw new Error('Page has no content');
    }
    
    // Check for error boundaries
    const errorBoundary = document.querySelector('[data-error-boundary]');
    if (errorBoundary) {
      throw new Error('Error boundary triggered');
    }
    
    // Check for loading states stuck
    const loadingStuck = document.querySelector('.animate-spin');
    if (loadingStuck) {
      await waitForNavigation(3000);
      if (document.querySelector('.animate-spin')) {
        console.warn('⚠️  Loading state persists');
      }
    }
    
    // Check for empty states
    const emptyStates = document.querySelectorAll('[data-empty-state]');
    if (emptyStates.length > 0) {
      console.log('ℹ️  Page shows empty state');
    }
    
    // Capture any console errors
    errorCapture.restore();
    
    if (errorCapture.errors.length > 0) {
      testResults.errors.push({
        page: name,
        path: path,
        errors: errorCapture.errors
      });
      console.log(`❌ ${name} - Console errors detected`);
    } else {
      testResults.passed.push({ page: name, path: path });
      console.log(`✅ ${name} - Passed`);
    }
    
  } catch (error) {
    errorCapture.restore();
    testResults.failed.push({
      page: name,
      path: path,
      error: error.message,
      consoleErrors: errorCapture.errors
    });
    console.log(`❌ ${name} - Failed: ${error.message}`);
  }
};

// Define all pages to test
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
  
  // Portal
  { path: '/portal', name: 'Portal Dashboard' },
  { path: '/portal/courses', name: 'Portal Courses' },
  { path: '/portal/progress', name: 'Portal Progress' },
  { path: '/portal/resources', name: 'Portal Resources' },
  { path: '/portal/achievements', name: 'Portal Achievements' },
  { path: '/portal/skills', name: 'Portal Skills' },
  
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
  { path: '/settings/ai', name: 'AI Settings' },
  
  // Admin Pages (for super admin)
  { path: '/admin/users', name: 'Admin - Users' },
  { path: '/admin/tenants', name: 'Admin - Tenants' },
  { path: '/admin/system', name: 'Admin - System' },
  { path: '/admin/audit', name: 'Admin - Audit Logs' },
  
  // AI Features
  { path: '/ai/assistant', name: 'AI Assistant' },
  { path: '/ai/insights', name: 'AI Insights' },
  { path: '/ai/recommendations', name: 'AI Recommendations' },
  
  // Integrations
  { path: '/integrations', name: 'Integrations' },
  { path: '/integrations/configure', name: 'Configure Integrations' },
  
  // Compliance
  { path: '/compliance', name: 'Compliance Dashboard' },
  { path: '/compliance/audits', name: 'Compliance Audits' },
  { path: '/compliance/certifications', name: 'Certifications' }
];

// Run all tests
const runAllTests = async () => {
  console.log('🚀 Starting comprehensive page tests...');
  console.log(`Testing ${pagesToTest.length} pages\n`);
  
  const startTime = Date.now();
  
  for (const page of pagesToTest) {
    await testPage(page.path, page.name);
    await waitForNavigation(500); // Small delay between tests
  }
  
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  
  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(50));
  console.log(`✅ Passed: ${testResults.passed.length}/${pagesToTest.length}`);
  console.log(`❌ Failed: ${testResults.failed.length}/${pagesToTest.length}`);
  console.log(`⚠️  Pages with console errors: ${testResults.errors.length}`);
  console.log(`⏱️  Duration: ${duration}s`);
  
  if (testResults.failed.length > 0) {
    console.log('\n❌ FAILED PAGES:');
    testResults.failed.forEach(({ page, path, error, consoleErrors }) => {
      console.log(`\n  ${page} (${path})`);
      console.log(`  Error: ${error}`);
      if (consoleErrors.length > 0) {
        console.log(`  Console errors: ${consoleErrors.length}`);
      }
    });
  }
  
  if (testResults.errors.length > 0) {
    console.log('\n⚠️  PAGES WITH CONSOLE ERRORS:');
    testResults.errors.forEach(({ page, path, errors }) => {
      console.log(`\n  ${page} (${path})`);
      errors.forEach(err => console.log(`    - ${err}`));
    });
  }
  
  // Return results for further processing
  return testResults;
};

// Interactive menu for selective testing
const testMenu = () => {
  console.log('\n🎯 BDC Frontend Test Suite');
  console.log('========================\n');
  console.log('Commands:');
  console.log('- runAllTests() : Test all pages');
  console.log('- testPage(path, name) : Test a specific page');
  console.log('- testResults : View last test results');
  console.log('\nExample: testPage("/dashboard", "Dashboard")');
};

// Display menu
testMenu();

// Make functions available globally
window.runAllTests = runAllTests;
window.testPage = testPage;
window.testResults = testResults;