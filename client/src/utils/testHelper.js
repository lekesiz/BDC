// Helper functions for frontend testing
export const checkPageHealth = () => {
  const issues = [];
  
  // Check for React error boundaries
  const errorBoundaries = document.querySelectorAll('[data-error-boundary]');
  if (errorBoundaries.length > 0) {
    issues.push('Error boundary triggered');
  }
  
  // Check for infinite loading
  const spinners = document.querySelectorAll('.animate-spin');
  if (spinners.length > 0) {
    // Wait 3 seconds and check again
    setTimeout(() => {
      const stillSpinning = document.querySelectorAll('.animate-spin');
      if (stillSpinning.length > 0) {
        issues.push('Infinite loading detected');
      }
    }, 3000);
  }
  
  // Check for error messages
  const errorMessages = document.querySelectorAll('.text-red-600, .text-red-500, .bg-red-50');
  errorMessages.forEach(el => {
    const text = el.textContent.trim();
    if (text && text.length > 0 && !text.includes('Delete') && !text.includes('Remove')) {
      issues.push(`Error message: ${text.substring(0, 50)}...`);
    }
  });
  
  // Check for empty content
  const mainContent = document.querySelector('main');
  if (mainContent && mainContent.children.length === 0) {
    issues.push('Page has no content');
  }
  
  // Check for network errors
  const networkErrors = [];
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    try {
      const response = await originalFetch(...args);
      if (!response.ok && response.status !== 404) {
        networkErrors.push(`${response.status} ${response.statusText} - ${args[0]}`);
      }
      return response;
    } catch (error) {
      networkErrors.push(`Network error: ${error.message}`);
      throw error;
    }
  };
  
  return { issues, networkErrors };
};

// Auto-navigate and test all pages
export const runAutomatedTest = async () => {
  const pages = [
    '/dashboard',
    '/beneficiaries',
    '/programs',
    '/evaluations',
    '/calendar',
    '/documents',
    '/messages',
    '/analytics',
    '/reports',
    '/settings',
    '/portal'
  ];
  
  const results = [];
  
  for (const page of pages) {
    window.location.href = page;
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const health = checkPageHealth();
    results.push({
      page,
      timestamp: new Date().toISOString(),
      issues: health.issues,
      networkErrors: health.networkErrors
    });
  }
  
  console.table(results);
  return results;
};