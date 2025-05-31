const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture console errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🔴 Console Error:', msg.text());
      errors.push(msg.text());
    }
  });
  
  page.on('pageerror', error => {
    console.log('💥 Page Error:', error.message);
    errors.push(error.message);
  });
  
  // Login
  console.log('Logging in...');
  await page.goto('http://localhost:5173/login');
  await page.type('#email', 'admin@bdc.com');
  await page.type('#password', 'Admin123!');
  await page.click('button[type="submit"]');
  
  // Wait for navigation
  await page.waitForNavigation({ waitUntil: 'networkidle0' });
  console.log('Logged in successfully');
  
  // Test dashboard
  console.log('\nTesting dashboard...');
  await page.goto('http://localhost:5173/dashboard');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  console.log('\nCurrent URL:', page.url());
  console.log('Page title:', await page.title());
  console.log('Total errors:', errors.length);
  
  // Keep browser open
  console.log('\nBrowser will stay open for inspection...');
})();