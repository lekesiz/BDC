// Simple script to check console errors in BDC frontend

const puppeteer = require('puppeteer');

const PAGES_TO_TEST = [
  { url: 'http://localhost:5173/login', name: 'Login Page' },
  { url: 'http://localhost:5173/', name: 'Root (should redirect)' },
];

async function checkPage(browser, pageInfo) {
  const page = await browser.newPage();
  const errors = [];
  const warnings = [];
  const logs = [];
  
  // Capture console messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      errors.push(text);
    } else if (type === 'warning') {
      warnings.push(text);
    } else if (type === 'log' && text.includes('error')) {
      logs.push(text);
    }
  });
  
  // Capture page errors
  page.on('pageerror', error => {
    errors.push(`PAGE ERROR: ${error.message}`);
  });
  
  // Capture failed requests
  page.on('requestfailed', request => {
    errors.push(`REQUEST FAILED: ${request.url()} - ${request.failure().errorText}`);
  });
  
  try {
    console.log(`\nChecking ${pageInfo.name}...`);
    await page.goto(pageInfo.url, { waitUntil: 'networkidle0', timeout: 30000 });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check for React error boundaries
    const hasErrorBoundary = await page.evaluate(() => {
      return document.querySelector('.error-boundary, .error-fallback, [data-error="true"]') !== null;
    });
    
    if (hasErrorBoundary) {
      errors.push('React Error Boundary detected');
    }
    
    // Get page title
    const title = await page.title();
    console.log(`  Title: ${title}`);
    console.log(`  URL: ${page.url()}`);
    
    // Report findings
    if (errors.length > 0) {
      console.log(`  ❌ Errors (${errors.length}):`);
      errors.forEach(err => console.log(`     - ${err}`));
    }
    
    if (warnings.length > 0) {
      console.log(`  ⚠️  Warnings (${warnings.length}):`);
      warnings.forEach(warn => console.log(`     - ${warn}`));
    }
    
    if (errors.length === 0 && warnings.length === 0) {
      console.log(`  ✅ No console errors or warnings`);
    }
    
  } catch (error) {
    console.log(`  ❌ Failed to load page: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function main() {
  console.log('🔍 BDC Frontend Console Error Check');
  console.log('=====================================\n');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  for (const pageInfo of PAGES_TO_TEST) {
    await checkPage(browser, pageInfo);
  }
  
  await browser.close();
  console.log('\n✅ Check complete!');
}

main().catch(console.error);