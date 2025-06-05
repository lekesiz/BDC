#!/usr/bin/env node

/**
 * Authentication Setup Verification Script
 * 
 * This script verifies that the authentication setup is complete and ready for testing
 * without needing to start the development server.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Colors for console output
const colors = {
  success: '\x1b[32m',
  error: '\x1b[31m',
  warning: '\x1b[33m',
  info: '\x1b[36m',
  reset: '\x1b[0m'
};

const log = (message, type = 'info') => {
  console.log(`${colors[type]}${message}${colors.reset}`);
};

const checkFile = (filePath, description) => {
  const exists = fs.existsSync(filePath);
  log(`${exists ? '✅' : '❌'} ${description}`, exists ? 'success' : 'error');
  return exists;
};

const checkFileContent = (filePath, searchStrings, description) => {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const allFound = searchStrings.every(str => content.includes(str));
    log(`${allFound ? '✅' : '❌'} ${description}`, allFound ? 'success' : 'error');
    return allFound;
  } catch (error) {
    log(`❌ ${description} (file not readable)`, 'error');
    return false;
  }
};

log('🔍 BDC Authentication Setup Verification', 'info');
log('=' .repeat(50), 'info');

let allChecks = 0;
let passedChecks = 0;

const check = (condition) => {
  allChecks++;
  if (condition) passedChecks++;
  return condition;
};

// 1. Check core mock data files
log('\n📁 Core Files Check:', 'info');
check(checkFile(path.join(__dirname, 'src/lib/mockData/usersMockData.js'), 'Users mock data file'));
check(checkFile(path.join(__dirname, 'src/lib/mockData/setupAuthMockApi.js'), 'Auth mock API setup file'));
check(checkFile(path.join(__dirname, 'src/lib/setupMockApi.js'), 'Main mock API setup file'));
check(checkFile(path.join(__dirname, 'src/lib/api.js'), 'API configuration file'));

// 2. Check authentication components
log('\n🔐 Authentication Components:', 'info');
check(checkFile(path.join(__dirname, 'src/contexts/AuthContext.jsx'), 'Authentication context'));
check(checkFile(path.join(__dirname, 'src/pages/auth/LoginPage.jsx'), 'Login page component'));
check(checkFile(path.join(__dirname, 'src/hooks/useAuth.js'), 'useAuth hook'));

// 3. Check environment configuration
log('\n⚙️  Environment Configuration:', 'info');
const envFile = path.join(__dirname, '.env');
if (checkFile(envFile, 'Environment configuration file')) {
  check(checkFileContent(envFile, ['VITE_USE_MOCK_API=true'], 'Mock API enabled in .env'));
} else {
  allChecks++;
}

// 4. Check mock data content
log('\n👥 Mock Users Data:', 'info');
const usersFile = path.join(__dirname, 'src/lib/mockData/usersMockData.js');
if (fs.existsSync(usersFile)) {
  check(checkFileContent(usersFile, ['admin@bdc.com'], 'Super admin user exists'));
  check(checkFileContent(usersFile, ['tenant@bdc.com'], 'Tenant admin user exists'));
  check(checkFileContent(usersFile, ['trainer@bdc.com'], 'Trainer user exists'));
  check(checkFileContent(usersFile, ['student@bdc.com'], 'Student user exists'));
  check(checkFileContent(usersFile, ['USER_ROLES'], 'User roles defined'));
}

// 5. Check mock API integration
log('\n🔧 Mock API Integration:', 'info');
const setupFile = path.join(__dirname, 'src/lib/setupMockApi.js');
if (fs.existsSync(setupFile)) {
  check(checkFileContent(setupFile, ['setupAuthMockApi'], 'Auth mock API imported'));
  check(checkFileContent(setupFile, ['setupAuthMockApi(api'], 'Auth mock API initialized'));
}

const apiFile = path.join(__dirname, 'src/lib/api.js');
if (fs.existsSync(apiFile)) {
  check(checkFileContent(apiFile, ['VITE_USE_MOCK_API'], 'Mock API conditional check'));
  check(checkFileContent(apiFile, ['setupMockApi(api)'], 'Mock API setup called'));
}

// 6. Check authentication mock API content
log('\n🔑 Authentication Mock API:', 'info');
const authMockFile = path.join(__dirname, 'src/lib/mockData/setupAuthMockApi.js');
if (fs.existsSync(authMockFile)) {
  check(checkFileContent(authMockFile, ['/api/auth/login'], 'Login endpoint implemented'));
  check(checkFileContent(authMockFile, ['/api/users/me'], 'User data endpoint implemented'));
  check(checkFileContent(authMockFile, ['generateMockToken'], 'JWT token generation'));
  check(checkFileContent(authMockFile, ['mockCredentials'], 'Test credentials defined'));
}

// 7. Check test files
log('\n🧪 Test Files:', 'info');
check(checkFile(path.join(__dirname, 'test-auth-functionality.js'), 'Static auth test script'));
check(checkFile(path.join(__dirname, 'test-auth-live.js'), 'Live auth test script'));
check(checkFile(path.join(__dirname, 'public/auth-test.html'), 'Manual browser test interface'));

// 8. Check login page redirect logic
log('\n🧭 Login Redirect Logic:', 'info');
const loginFile = path.join(__dirname, 'src/pages/auth/LoginPage.jsx');
if (fs.existsSync(loginFile)) {
  check(checkFileContent(loginFile, ['getRedirectPath'], 'Redirect function exists'));
  check(checkFileContent(loginFile, ["case 'student':", '/portal'], 'Student redirect to portal'));
  check(checkFileContent(loginFile, ["case 'super_admin':"], 'Admin redirect logic'));
}

// 9. Display test credentials
log('\n📋 Available Test Credentials:', 'info');
const credentials = [
  { role: 'Super Admin', email: 'admin@bdc.com', password: 'admin123' },
  { role: 'Tenant Admin', email: 'tenant@bdc.com', password: 'tenant123' },
  { role: 'Trainer', email: 'trainer@bdc.com', password: 'trainer123' },
  { role: 'Student', email: 'student@bdc.com', password: 'student123' }
];

credentials.forEach(cred => {
  log(`   ${cred.role}: ${cred.email} / ${cred.password}`, 'info');
});

// Summary
log('\n📊 Verification Summary:', 'info');
log('=' .repeat(50), 'info');

const successRate = Math.round((passedChecks / allChecks) * 100);
log(`Total Checks: ${allChecks}`, 'info');
log(`Passed: ${passedChecks}`, passedChecks === allChecks ? 'success' : 'warning');
log(`Failed: ${allChecks - passedChecks}`, allChecks === passedChecks ? 'success' : 'error');
log(`Success Rate: ${successRate}%`, successRate >= 90 ? 'success' : 'warning');

if (successRate >= 90) {
  log('\n🎉 Authentication setup is ready for testing!', 'success');
  log('\nHow to test:', 'info');
  log('1. Start development server: npm run dev', 'info');
  log('2. Visit: http://localhost:5173/auth-test.html', 'info');
  log('3. Or go to login page: http://localhost:5173/login', 'info');
  log('4. Use the credentials listed above', 'info');
} else {
  log('\n⚠️  Authentication setup needs attention!', 'warning');
  log('Please check the failed items above.', 'warning');
}

process.exit(successRate >= 90 ? 0 : 1);