const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false,
    devtools: true 
  });
  const page = await browser.newPage();
  
  const errors = [];
  const warnings = [];
  const logs = [];
  
  // Capture ALL console messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      errors.push(text);
      console.log('🔴 ERROR:', text);
    } else if (type === 'warning') {
      warnings.push(text);
      console.log('🟡 WARNING:', text);
    } else {
      logs.push(text);
      console.log('🔵 LOG:', text);
    }
  });
  
  // Capture page errors
  page.on('pageerror', error => {
    console.log('💥 PAGE ERROR:', error.message);
  });
  
  // Capture response errors
  page.on('response', response => {
    if (!response.ok() && response.url().includes('localhost:5173')) {
      console.log(`❌ Response ${response.status()} for ${response.url()}`);
    }
  });
  
  console.log('Loading app...');
  await page.goto('http://localhost:5173', { 
    waitUntil: 'domcontentloaded',
    timeout: 30000 
  });
  
  // Wait for potential React rendering
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Check what's rendered
  const pageInfo = await page.evaluate(() => {
    const root = document.getElementById('root');
    return {
      title: document.title,
      url: window.location.href,
      rootExists: !!root,
      rootHTML: root ? root.innerHTML : 'No root',
      rootChildren: root ? root.children.length : 0,
      hasReactFiber: !!document.querySelector('[data-reactroot]') || 
                     !!(root && root._reactRootContainer),
      scripts: Array.from(document.scripts).map(s => s.src || 'inline'),
    };
  });
  
  console.log('\n📊 Page Analysis:');
  console.log('Title:', pageInfo.title);
  console.log('URL:', pageInfo.url);
  console.log('Root exists:', pageInfo.rootExists);
  console.log('Root children:', pageInfo.rootChildren);
  console.log('React detected:', pageInfo.hasReactFiber);
  console.log('\nScripts loaded:');
  pageInfo.scripts.forEach(s => console.log(' -', s));
  
  console.log('\n🔍 Summary:');
  console.log(`Errors: ${errors.length}`);
  console.log(`Warnings: ${warnings.length}`);
  console.log(`Logs: ${logs.length}`);
  
  console.log('\nKeeping browser open for inspection...');
  console.log('Check the DevTools console for more details.');
})();