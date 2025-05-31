const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: false, // Show browser
    devtools: true
  });
  
  const page = await browser.newPage();
  
  console.log('Going to login page...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle0' });
  
  console.log('\nChecking for input fields...');
  
  // Check various selectors
  const selectors = [
    'input[name="email"]',
    'input[type="email"]',
    'input#email',
    'input[id="email"]',
    'input[placeholder*="@"]',
    'input[placeholder*="example"]'
  ];
  
  for (const selector of selectors) {
    const found = await page.$(selector);
    console.log(`${selector}: ${found ? '✅ FOUND' : '❌ NOT FOUND'}`);
  }
  
  // Get all input elements
  const inputs = await page.evaluate(() => {
    const allInputs = Array.from(document.querySelectorAll('input'));
    return allInputs.map(input => ({
      type: input.type,
      name: input.name,
      id: input.id,
      placeholder: input.placeholder,
      className: input.className
    }));
  });
  
  console.log('\nAll input fields found:');
  inputs.forEach((input, i) => {
    console.log(`Input ${i + 1}:`, input);
  });
  
  // Try to find the form
  const form = await page.$('form');
  console.log(`\nForm found: ${form ? '✅ YES' : '❌ NO'}`);
  
  // Wait for user to check
  console.log('\nBrowser will stay open for inspection. Close it manually when done.');
})();