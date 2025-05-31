const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:5173';

// Test credentials
const ADMIN_CREDS = { email: 'admin@bdc.com', password: 'Admin123!' };
const STUDENT_CREDS = { email: 'student@bdc.com', password: 'Student123!' };

// Pages to test for each role
const ADMIN_PAGES = [
  { path: '/', name: 'Dashboard' },
  { path: '/users', name: 'Users' },
  { path: '/beneficiaries', name: 'Beneficiaries' },
  { path: '/evaluations', name: 'Evaluations' },
  { path: '/calendar', name: 'Calendar' },
  { path: '/documents', name: 'Documents' },
  { path: '/messaging', name: 'Messaging' },
  { path: '/notifications', name: 'Notifications' },
  { path: '/analytics', name: 'Analytics' },
  { path: '/reports', name: 'Reports' },
  { path: '/programs', name: 'Programs' },
  { path: '/settings', name: 'Settings' },
  { path: '/profile', name: 'Profile' }
];

const STUDENT_PAGES = [
  { path: '/', name: 'Dashboard' },
  { path: '/my-evaluations', name: 'My Evaluations' },
  { path: '/my-documents', name: 'My Documents' },
  { path: '/portal', name: 'Student Portal' },
  { path: '/calendar', name: 'Calendar' },
  { path: '/messaging', name: 'Messaging' },
  { path: '/notifications', name: 'Notifications' },
  { path: '/settings', name: 'Settings' },
  { path: '/profile', name: 'Profile' }
];

async function login(page, credentials) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('input[name="email"]', credentials.email);
  await page.fill('input[name="password"]', credentials.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/^\//, { timeout: 10000 });
}

async function testPage(page, pageInfo) {
  const errors = [];
  
  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  // Listen for page errors
  page.on('pageerror', error => {
    errors.push(error.message);
  });
  
  try {
    await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000); // Wait for any async operations
    
    // Check if page loaded without React errors
    const hasError = await page.locator('.error-boundary, .error-fallback').count();
    if (hasError > 0) {
      errors.push('React Error Boundary triggered');
    }
    
    // Take screenshot
    await page.screenshot({ 
      path: `/Users/mikail/Desktop/BDC/screenshots/${pageInfo.name.replace(/\s+/g, '-').toLowerCase()}.png`,
      fullPage: true 
    });
    
    return {
      page: pageInfo.name,
      path: pageInfo.path,
      status: errors.length === 0 ? 'success' : 'error',
      errors
    };
  } catch (error) {
    return {
      page: pageInfo.name,
      path: pageInfo.path,
      status: 'error',
      errors: [...errors, error.message]
    };
  }
}

async function runTests() {
  // Create screenshots directory
  const fs = require('fs');
  const screenshotsDir = '/Users/mikail/Desktop/BDC/screenshots';
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }
  
  const browser = await chromium.launch({ headless: false });
  const results = [];
  
  // Test Admin Pages
  console.log('\n🔍 Testing Admin Pages...');
  const adminContext = await browser.newContext();
  const adminPage = await adminContext.newPage();
  
  await login(adminPage, ADMIN_CREDS);
  
  for (const pageInfo of ADMIN_PAGES) {
    console.log(`Testing ${pageInfo.name}...`);
    const result = await testPage(adminPage, pageInfo);
    results.push({ role: 'admin', ...result });
    console.log(`  ${result.status === 'success' ? '✅' : '❌'} ${pageInfo.name}`);
    if (result.errors.length > 0) {
      result.errors.forEach(err => console.log(`    - ${err}`));
    }
  }
  
  await adminContext.close();
  
  // Test Student Pages
  console.log('\n🔍 Testing Student Pages...');
  const studentContext = await browser.newContext();
  const studentPage = await studentContext.newPage();
  
  await login(studentPage, STUDENT_CREDS);
  
  for (const pageInfo of STUDENT_PAGES) {
    console.log(`Testing ${pageInfo.name}...`);
    const result = await testPage(studentPage, pageInfo);
    results.push({ role: 'student', ...result });
    console.log(`  ${result.status === 'success' ? '✅' : '❌'} ${pageInfo.name}`);
    if (result.errors.length > 0) {
      result.errors.forEach(err => console.log(`    - ${err}`));
    }
  }
  
  await studentContext.close();
  await browser.close();
  
  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: results.length,
      success: results.filter(r => r.status === 'success').length,
      errors: results.filter(r => r.status === 'error').length
    },
    results
  };
  
  fs.writeFileSync(
    '/Users/mikail/Desktop/BDC/test-results.json',
    JSON.stringify(report, null, 2)
  );
  
  console.log('\n📊 Summary:');
  console.log(`Total pages tested: ${report.summary.total}`);
  console.log(`Successful: ${report.summary.success}`);
  console.log(`Errors: ${report.summary.errors}`);
  
  // Show error details
  const errorPages = results.filter(r => r.status === 'error');
  if (errorPages.length > 0) {
    console.log('\n❌ Pages with errors:');
    errorPages.forEach(page => {
      console.log(`\n${page.role.toUpperCase()} - ${page.page} (${page.path})`);
      page.errors.forEach(err => console.log(`  - ${err}`));
    });
  }
}

runTests().catch(console.error);