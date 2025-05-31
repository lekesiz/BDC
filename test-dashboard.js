const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false,
    devtools: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Enable request interception to see API calls
  await page.setRequestInterception(true);
  
  page.on('request', request => {
    const url = request.url();
    if (url.includes('/api/')) {
      console.log(`🔄 API Request: ${request.method()} ${url}`);
    }
    request.continue();
  });
  
  page.on('response', response => {
    const url = response.url();
    if (url.includes('/api/') && !response.ok()) {
      console.log(`❌ API Error: ${response.status()} ${url}`);
    }
  });
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`🔴 Console Error: ${msg.text()}`);
    }
  });
  
  try {
    // Login
    console.log('1. Logging in...');
    await page.goto('http://localhost:5173/login');
    await page.waitForSelector('#email', { timeout: 5000 });
    
    await page.type('#email', 'admin@bdc.com');
    await page.type('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    
    // Wait for redirect
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    console.log('✅ Login successful');
    console.log(`   Current URL: ${page.url()}`);
    
    // Wait a bit for dashboard to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check what's on the page
    const pageContent = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        hasRoot: !!document.getElementById('root'),
        bodyText: document.body.innerText.substring(0, 200)
      };
    });
    
    console.log('\n2. Page Analysis:');
    console.log(`   Title: ${pageContent.title}`);
    console.log(`   URL: ${pageContent.url}`);
    console.log(`   Has React Root: ${pageContent.hasRoot}`);
    console.log(`   Body preview: ${pageContent.bodyText}`);
    
    // Try to navigate to specific pages
    console.log('\n3. Testing navigation...');
    
    // Navigate to users page
    await page.goto('http://localhost:5173/users');
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log(`   Users page: ${page.url()}`);
    
    // Navigate to beneficiaries page
    await page.goto('http://localhost:5173/beneficiaries');
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log(`   Beneficiaries page: ${page.url()}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
  
  console.log('\nTest complete. Browser will stay open for inspection.');
})();