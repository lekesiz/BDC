const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:5001';

// Test users
const USERS = [
  { email: 'admin@bdc.com', password: 'Admin123!', role: 'admin' },
  { email: 'student@bdc.com', password: 'Student123!', role: 'student' }
];

// Pages to test
const ADMIN_PAGES = [
  '/dashboard', '/users', '/beneficiaries', '/evaluations', '/calendar',
  '/documents', '/messaging', '/notifications', '/analytics', '/reports',
  '/programs', '/settings', '/profile'
];

const STUDENT_PAGES = [
  '/dashboard', '/my-evaluations', '/my-documents', '/portal', '/calendar',
  '/messaging', '/notifications', '/settings', '/profile'
];

class PageTester {
  constructor() {
    this.results = [];
  }

  async init() {
    this.browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }

  async login(email, password) {
    const page = await this.browser.newPage();
    
    // Set up error tracking
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    page.on('pageerror', error => {
      errors.push(`PAGE ERROR: ${error.message}`);
    });

    try {
      // Go to login page
      await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0' });
      
      // Fill login form
      await page.type('input[id="email"]', email);
      await page.type('input[id="password"]', password);
      await page.click('button[type="submit"]');
      
      // Wait for navigation
      await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 });
      
      // Check if login was successful
      const currentUrl = page.url();
      if (currentUrl.includes('/login')) {
        throw new Error('Login failed - still on login page');
      }
      
      return { page, errors };
    } catch (error) {
      await page.close();
      throw error;
    }
  }

  async testPage(page, path, role) {
    const errors = [];
    const warnings = [];
    
    // Set up error tracking
    page.removeAllListeners('console');
    page.removeAllListeners('pageerror');
    page.removeAllListeners('requestfailed');
    
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      
      if (type === 'error' && !text.includes('ERR_CONNECTION_REFUSED')) {
        errors.push(text);
      } else if (type === 'warning') {
        warnings.push(text);
      }
    });
    
    page.on('pageerror', error => {
      errors.push(`PAGE ERROR: ${error.message}`);
    });
    
    page.on('requestfailed', request => {
      const url = request.url();
      // Ignore WebSocket failures
      if (!url.includes('9888') && !url.includes('ws://')) {
        errors.push(`REQUEST FAILED: ${url}`);
      }
    });

    const startTime = Date.now();
    
    try {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle0', timeout: 30000 });
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const title = await page.title();
      const url = page.url();
      const loadTime = Date.now() - startTime;
      
      // Check for React errors
      const hasReactError = await page.evaluate(() => {
        return document.querySelector('.error-boundary, .error-fallback, [data-error]') !== null;
      });
      
      if (hasReactError) {
        errors.push('React Error Boundary triggered');
      }
      
      // Take screenshot
      const screenshotPath = `/Users/mikail/Desktop/BDC/screenshots/${role}-${path.replace(/\//g, '-')}.png`;
      await page.screenshot({ path: screenshotPath, fullPage: true });
      
      return {
        path,
        url,
        title,
        loadTime,
        errors,
        warnings,
        screenshot: screenshotPath,
        status: errors.length === 0 ? 'success' : 'error'
      };
      
    } catch (error) {
      return {
        path,
        url: page.url(),
        title: 'Failed to load',
        loadTime: Date.now() - startTime,
        errors: [...errors, error.message],
        warnings,
        status: 'error'
      };
    }
  }

  async testUserFlow(user, pages) {
    console.log(`\n🔍 Testing ${user.role.toUpperCase()} pages...`);
    
    try {
      const { page, errors: loginErrors } = await this.login(user.email, user.password);
      
      if (loginErrors.length > 0) {
        console.log(`  ⚠️  Login had console errors: ${loginErrors.length}`);
      }
      
      const results = [];
      
      for (const pagePath of pages) {
        console.log(`  Testing ${pagePath}...`);
        const result = await this.testPage(page, pagePath, user.role);
        results.push(result);
        
        const status = result.status === 'success' ? '✅' : '❌';
        console.log(`    ${status} ${result.title} (${result.loadTime}ms)`);
        
        if (result.errors.length > 0) {
          result.errors.forEach(err => console.log(`      - ${err}`));
        }
      }
      
      await page.close();
      
      return {
        user: user.role,
        results
      };
      
    } catch (error) {
      console.log(`  ❌ Failed to test ${user.role}: ${error.message}`);
      return {
        user: user.role,
        error: error.message,
        results: []
      };
    }
  }

  async runTests() {
    await this.init();
    
    // Create screenshots directory
    const screenshotsDir = '/Users/mikail/Desktop/BDC/screenshots';
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
    
    console.log('🚀 BDC Frontend Comprehensive Test');
    console.log('=====================================');
    
    // Test admin pages
    const adminResults = await this.testUserFlow(USERS[0], ADMIN_PAGES);
    this.results.push(adminResults);
    
    // Test student pages
    const studentResults = await this.testUserFlow(USERS[1], STUDENT_PAGES);
    this.results.push(studentResults);
    
    await this.browser.close();
    
    // Generate report
    this.generateReport();
  }

  generateReport() {
    console.log('\n📊 TEST SUMMARY');
    console.log('================');
    
    let totalPages = 0;
    let successPages = 0;
    let errorPages = 0;
    
    this.results.forEach(userResult => {
      if (userResult.error) {
        console.log(`\n${userResult.user.toUpperCase()}: Failed to test - ${userResult.error}`);
        return;
      }
      
      const results = userResult.results;
      const success = results.filter(r => r.status === 'success').length;
      const errors = results.filter(r => r.status === 'error').length;
      
      totalPages += results.length;
      successPages += success;
      errorPages += errors;
      
      console.log(`\n${userResult.user.toUpperCase()}:`);
      console.log(`  Total: ${results.length}`);
      console.log(`  ✅ Success: ${success}`);
      console.log(`  ❌ Errors: ${errors}`);
      
      // Show error details
      const errorResults = results.filter(r => r.status === 'error');
      if (errorResults.length > 0) {
        console.log('\n  Pages with errors:');
        errorResults.forEach(result => {
          console.log(`    ${result.path}:`);
          result.errors.forEach(err => console.log(`      - ${err}`));
        });
      }
    });
    
    console.log('\n🎯 OVERALL:');
    console.log(`  Total pages tested: ${totalPages}`);
    console.log(`  ✅ Successful: ${successPages} (${Math.round(successPages/totalPages*100)}%)`);
    console.log(`  ❌ With errors: ${errorPages} (${Math.round(errorPages/totalPages*100)}%)`);
    
    // Save detailed report
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: totalPages,
        success: successPages,
        errors: errorPages
      },
      results: this.results
    };
    
    fs.writeFileSync(
      '/Users/mikail/Desktop/BDC/frontend-test-report.json',
      JSON.stringify(report, null, 2)
    );
    
    console.log('\n💾 Detailed report saved to: frontend-test-report.json');
    console.log('📸 Screenshots saved to: screenshots/');
  }
}

// Run tests
const tester = new PageTester();
tester.runTests().catch(console.error);