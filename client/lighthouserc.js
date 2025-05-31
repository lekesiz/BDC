module.exports = {
  ci: {
    collect: {
      // Run Lighthouse on the local development server
      startServerCommand: 'npm run preview',
      url: ['http://localhost:4173/'],
      numberOfRuns: 3,
      // Use puppeteer to run Lighthouse in headless mode
      puppeteerScript: 'lighthouse-puppeteer.js',
      // Wait for the app to be fully loaded
      settings: {
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
        skipAudits: ['uses-http2'],
      },
    },
    upload: {
      // Don't upload the results to a server, just store them locally
      target: 'filesystem',
      outputDir: './lighthouse-results',
      reportFilenamePattern: '%%PATHNAME%%-%%DATETIME%%-report.%%EXTENSION%%',
    },
    assert: {
      // Set the performance score thresholds
      // These are relatively lenient for development
      assertions: {
        'categories:performance': ['warn', { minScore: 0.7 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.85 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 3000 }],
        'interactive': ['warn', { maxNumericValue: 5000 }],
        'resource-summary:script:size': ['warn', { maxNumericValue: 500000 }], // 500KB
        'resource-summary:total:size': ['warn', { maxNumericValue: 1000000 }], // 1MB
      },
    },
  },
};