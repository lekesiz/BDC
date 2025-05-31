const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('Console Error:', msg.text());
    }
  });
  
  console.log('Loading login page...');
  await page.goto('http://localhost:5173/login', { 
    waitUntil: 'networkidle0',
    timeout: 30000 
  });
  
  // Wait a bit for React to render
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log('\nChecking page content...');
  
  // Check page title
  const title = await page.title();
  console.log('Page title:', title);
  
  // Check if React rendered
  const reactRoot = await page.$('#root');
  console.log('React root found:', reactRoot ? '✅' : '❌');
  
  // Check for various input selectors
  const selectors = [
    'input[type="email"]',
    'input[id="email"]',
    'input[type="password"]',
    'input[id="password"]',
    'button[type="submit"]',
    'form',
    // Try data attributes that might be used
    '[data-testid="email-input"]',
    '[data-testid="password-input"]',
    // Try class-based selectors
    '.input',
    '.form-input',
    // General input
    'input'
  ];
  
  console.log('\nChecking for form elements:');
  for (const selector of selectors) {
    const element = await page.$(selector);
    console.log(`${selector}: ${element ? '✅ FOUND' : '❌ NOT FOUND'}`);
  }
  
  // Get page content info
  const content = await page.evaluate(() => {
    const root = document.getElementById('root');
    return {
      rootHTML: root ? root.innerHTML.substring(0, 200) : 'No root element',
      bodyHTML: document.body.innerHTML.substring(0, 200),
      hasReactRoot: !!window.React || !!document.querySelector('[data-reactroot]'),
      url: window.location.href
    };
  });
  
  console.log('\nPage analysis:');
  console.log('URL:', content.url);
  console.log('Has React:', content.hasReactRoot);
  console.log('Root HTML preview:', content.rootHTML);
  
  // Try to fill the form if inputs exist
  const emailInput = await page.$('input[type="email"], input[id="email"]');
  const passwordInput = await page.$('input[type="password"], input[id="password"]');
  
  if (emailInput && passwordInput) {
    console.log('\n✅ Login form found! Attempting to fill...');
    await emailInput.type('admin@bdc.com');
    await passwordInput.type('Admin123!');
    
    // Find and click submit button
    const submitButton = await page.$('button[type="submit"]');
    if (submitButton) {
      console.log('Submit button found, clicking...');
      await submitButton.click();
      
      // Wait for navigation
      try {
        await page.waitForNavigation({ timeout: 5000 });
        console.log('✅ Login successful! Redirected to:', page.url());
      } catch (e) {
        console.log('❌ Login might have failed or no navigation occurred');
      }
    }
  } else {
    console.log('\n❌ Could not find email or password inputs');
  }
  
  await browser.close();
})();