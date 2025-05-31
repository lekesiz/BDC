#!/usr/bin/env node

/**
 * Frontend Test Script
 * This script tests all pages in the BDC application
 */

const puppeteer = require('puppeteer');
const chalk = require('chalk');

// Test configurations
const BASE_URL = 'http://localhost:5173';
const USERS = [
  { email: 'admin@bdc.com', password: 'Admin123!', role: 'super_admin' },
  { email: 'tenant@bdc.com', password: 'Tenant123!', role: 'tenant_admin' },
  { email: 'trainer@bdc.com', password: 'Trainer123!', role: 'trainer' },
  { email: 'student@bdc.com', password: 'Student123!', role: 'student' }
];

// Routes to test for each role
const ROUTES = {
  super_admin: [
    '/dashboard',
    '/users',
    '/users/create',
    '/beneficiaries',
    '/beneficiaries/new',
    '/evaluations',
    '/evaluations/create',
    '/calendar',
    '/documents',
    '/documents/upload',
    '/messaging',
    '/notifications',
    '/analytics',
    '/analytics/trainers',
    '/analytics/programs',
    '/analytics/beneficiaries',
    '/reports',
    '/reports/create',
    '/reports/schedules/create',
    '/admin/tenants',
    '/admin/database-optimization',
    '/admin/caching-system',
    '/admin/performance-monitoring',
    '/integrations/google-calendar',
    '/integrations/wedof',
    '/integrations/email',
    '/integrations/webhooks',
    '/programs',
    '/programs/new',
    '/ai/insights',
    '/ai/recommendations',
    '/ai/content-generation',
    '/ai/assistant',
    '/compliance/gdpr',
    '/compliance/backup',
    '/compliance/audit-logs',
    '/assessment',
    '/assessment/create',
    '/settings',
    '/profile'
  ],
  tenant_admin: [
    '/dashboard',
    '/users',
    '/beneficiaries',
    '/evaluations',
    '/calendar',
    '/documents',
    '/messaging',
    '/notifications',
    '/analytics',
    '/reports',
    '/programs',
    '/ai/insights',
    '/compliance/gdpr',
    '/assessment',
    '/settings',
    '/profile'
  ],
  trainer: [
    '/dashboard',
    '/beneficiaries',
    '/evaluations',
    '/calendar',
    '/documents',
    '/messaging',
    '/notifications',
    '/programs',
    '/assessment',
    '/settings',
    '/profile'
  ],
  student: [
    '/dashboard',
    '/my-evaluations',
    '/my-documents',
    '/calendar',
    '/messaging',
    '/notifications',
    '/portal',
    '/portal/courses',
    '/portal/resources',
    '/portal/achievements',
    '/portal/skills',
    '/portal/progress',
    '/portal/assessment',
    '/settings',
    '/profile'
  ]
};

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function login(page, user) {
  console.log(chalk.blue(`\nLogging in as ${user.email} (${user.role})...`));
  
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0' });
  await page.type('input[name="email"]', user.email);
  await page.type('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  
  // Wait for navigation
  await page.waitForNavigation({ waitUntil: 'networkidle0' });
  await delay(1000);
  
  console.log(chalk.green(`✓ Logged in successfully`));
}

async function testRoute(page, route) {
  try {
    console.log(chalk.gray(`  Testing ${route}...`));
    
    const response = await page.goto(`${BASE_URL}${route}`, { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Check for console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await delay(1000);
    
    // Check response status
    const status = response.status();
    if (status >= 400) {
      console.log(chalk.red(`    ✗ ${route} - HTTP ${status}`));
      return { route, status: 'error', message: `HTTP ${status}` };
    }
    
    // Check for React error boundary
    const errorBoundary = await page.$('.error-boundary');
    if (errorBoundary) {
      console.log(chalk.red(`    ✗ ${route} - React Error`));
      return { route, status: 'error', message: 'React Error Boundary triggered' };
    }
    
    // Check if there are console errors
    if (errors.length > 0) {
      console.log(chalk.yellow(`    ⚠ ${route} - Console errors: ${errors.length}`));
      return { route, status: 'warning', message: errors.join('; ') };
    }
    
    console.log(chalk.green(`    ✓ ${route}`));
    return { route, status: 'success' };
    
  } catch (error) {
    console.log(chalk.red(`    ✗ ${route} - ${error.message}`));
    return { route, status: 'error', message: error.message };
  }
}

async function testUserRole(user) {
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Set viewport
  await page.setViewport({ width: 1280, height: 800 });
  
  // Login
  await login(page, user);
  
  // Test routes
  const routes = ROUTES[user.role];
  const results = [];
  
  for (const route of routes) {
    const result = await testRoute(page, route);
    results.push(result);
  }
  
  await browser.close();
  
  return results;
}

async function runTests() {
  console.log(chalk.bold('\n🚀 Starting Frontend Tests\n'));
  
  const allResults = {};
  
  for (const user of USERS) {
    console.log(chalk.bold.blue(`\n━━━ Testing ${user.role.toUpperCase()} Role ━━━`));
    
    try {
      const results = await testUserRole(user);
      allResults[user.role] = results;
      
      // Summary for this role
      const successful = results.filter(r => r.status === 'success').length;
      const warnings = results.filter(r => r.status === 'warning').length;
      const errors = results.filter(r => r.status === 'error').length;
      
      console.log(chalk.bold(`\nSummary for ${user.role}:`));
      console.log(chalk.green(`  ✓ Successful: ${successful}`));
      console.log(chalk.yellow(`  ⚠ Warnings: ${warnings}`));
      console.log(chalk.red(`  ✗ Errors: ${errors}`));
      
    } catch (error) {
      console.log(chalk.red(`\nFailed to test ${user.role}: ${error.message}`));
      allResults[user.role] = [];
    }
  }
  
  // Overall summary
  console.log(chalk.bold('\n\n📊 OVERALL SUMMARY\n'));
  
  for (const [role, results] of Object.entries(allResults)) {
    const successful = results.filter(r => r.status === 'success').length;
    const total = results.length;
    const percentage = total > 0 ? Math.round((successful / total) * 100) : 0;
    
    console.log(chalk.bold(`${role}: ${successful}/${total} (${percentage}%)`);
    
    // Show failed routes
    const failed = results.filter(r => r.status === 'error');
    if (failed.length > 0) {
      console.log(chalk.red(`  Failed routes:`));
      failed.forEach(f => {
        console.log(chalk.red(`    - ${f.route}: ${f.message}`));
      });
    }
  }
  
  // Save results to file
  const fs = require('fs');
  const reportPath = '/Users/mikail/Desktop/BDC/frontend-test-report.json';
  fs.writeFileSync(reportPath, JSON.stringify(allResults, null, 2));
  console.log(chalk.gray(`\nDetailed report saved to: ${reportPath}`));
}

// Run tests
runTests().catch(error => {
  console.error(chalk.red('\nTest suite failed:'), error);
  process.exit(1);
});