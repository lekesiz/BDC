/**
 * Custom script for Lighthouse CI to authenticate before running audits
 */
module.exports = async (browser) => {
  const page = await browser.newPage();
  
  // Navigate to the login page
  await page.goto('http://localhost:4173/login');
  
  // Wait for the page to load
  await page.waitForSelector('input[name="email"]');
  
  // Fill in login credentials
  await page.type('input[name="email"]', 'admin@bdc.com');
  await page.type('input[name="password"]', 'Admin123!');
  
  // Submit the form
  await page.click('button[type="submit"]');
  
  // Wait for navigation to complete
  await page.waitForNavigation({ waitUntil: 'networkidle0' });
  
  // Close the page - Lighthouse will open a new one
  await page.close();
};