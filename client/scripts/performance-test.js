/**
 * Performance testing script for BDC application
 */

const puppeteer = require('puppeteer');
const lighthouse = require('lighthouse');
const fs = require('fs');
const path = require('path');

// Test configuration
const config = {
  url: process.env.TEST_URL || 'http://localhost:5173',
  outputDir: path.join(__dirname, '../performance-reports'),
  iterations: 3,
  pages: [
    { name: 'Homepage', path: '/' },
    { name: 'Login', path: '/login' },
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Beneficiaries', path: '/beneficiaries' },
    { name: 'Programs', path: '/programs' },
  ]
};

// Lighthouse configuration
const lighthouseConfig = {
  extends: 'lighthouse:default',
  settings: {
    formFactor: 'desktop',
    throttling: {
      rttMs: 40,
      throughputKbps: 10 * 1024,
      cpuSlowdownMultiplier: 1,
    },
    screenEmulation: {
      mobile: false,
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1,
      disabled: false,
    },
  },
};

// Create output directory
if (!fs.existsSync(config.outputDir)) {
  fs.mkdirSync(config.outputDir, { recursive: true });
}

/**
 * Run Lighthouse test for a page
 */
async function runLighthouseTest(browser, page) {
  const url = `${config.url}${page.path}`;
  console.log(`Testing ${page.name} at ${url}`);

  const results = [];

  for (let i = 0; i < config.iterations; i++) {
    console.log(`  Iteration ${i + 1}/${config.iterations}`);
    
    const { lhr, report } = await lighthouse(url, {
      port: (new URL(browser.wsEndpoint())).port,
      output: 'html',
      logLevel: 'error',
    }, lighthouseConfig);

    results.push({
      performance: lhr.categories.performance.score * 100,
      accessibility: lhr.categories.accessibility.score * 100,
      bestPractices: lhr.categories['best-practices'].score * 100,
      seo: lhr.categories.seo.score * 100,
      metrics: {
        fcp: lhr.audits['first-contentful-paint'].numericValue,
        lcp: lhr.audits['largest-contentful-paint'].numericValue,
        fid: lhr.audits['max-potential-fid'].numericValue,
        cls: lhr.audits['cumulative-layout-shift'].numericValue,
        tti: lhr.audits['interactive'].numericValue,
        speedIndex: lhr.audits['speed-index'].numericValue,
      }
    });

    // Save the last report
    if (i === config.iterations - 1) {
      const reportPath = path.join(config.outputDir, `${page.name.toLowerCase()}-lighthouse.html`);
      fs.writeFileSync(reportPath, report);
    }
  }

  return results;
}

/**
 * Calculate average metrics
 */
function calculateAverages(results) {
  const avg = {
    performance: 0,
    accessibility: 0,
    bestPractices: 0,
    seo: 0,
    metrics: {
      fcp: 0,
      lcp: 0,
      fid: 0,
      cls: 0,
      tti: 0,
      speedIndex: 0,
    }
  };

  results.forEach(result => {
    avg.performance += result.performance;
    avg.accessibility += result.accessibility;
    avg.bestPractices += result.bestPractices;
    avg.seo += result.seo;
    
    Object.keys(result.metrics).forEach(metric => {
      avg.metrics[metric] += result.metrics[metric];
    });
  });

  // Calculate averages
  const count = results.length;
  avg.performance /= count;
  avg.accessibility /= count;
  avg.bestPractices /= count;
  avg.seo /= count;
  
  Object.keys(avg.metrics).forEach(metric => {
    avg.metrics[metric] /= count;
  });

  return avg;
}

/**
 * Generate performance report
 */
function generateReport(allResults) {
  const report = {
    timestamp: new Date().toISOString(),
    url: config.url,
    iterations: config.iterations,
    results: {}
  };

  // Process results for each page
  Object.entries(allResults).forEach(([pageName, results]) => {
    report.results[pageName] = {
      averages: calculateAverages(results),
      allRuns: results
    };
  });

  // Save JSON report
  const reportPath = path.join(config.outputDir, 'performance-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  // Generate markdown summary
  const summaryPath = path.join(config.outputDir, 'performance-summary.md');
  let summary = '# Performance Test Summary\n\n';
  summary += `**Date**: ${new Date().toLocaleDateString()}\n`;
  summary += `**URL**: ${config.url}\n`;
  summary += `**Iterations**: ${config.iterations}\n\n`;

  summary += '## Results by Page\n\n';
  
  Object.entries(report.results).forEach(([pageName, data]) => {
    const avg = data.averages;
    summary += `### ${pageName}\n\n`;
    summary += '| Metric | Score/Value |\n';
    summary += '|--------|------------|\n';
    summary += `| Performance | ${avg.performance.toFixed(1)}% |\n`;
    summary += `| Accessibility | ${avg.accessibility.toFixed(1)}% |\n`;
    summary += `| Best Practices | ${avg.bestPractices.toFixed(1)}% |\n`;
    summary += `| SEO | ${avg.seo.toFixed(1)}% |\n`;
    summary += `| FCP | ${(avg.metrics.fcp / 1000).toFixed(2)}s |\n`;
    summary += `| LCP | ${(avg.metrics.lcp / 1000).toFixed(2)}s |\n`;
    summary += `| FID | ${avg.metrics.fid.toFixed(0)}ms |\n`;
    summary += `| CLS | ${avg.metrics.cls.toFixed(3)} |\n`;
    summary += `| TTI | ${(avg.metrics.tti / 1000).toFixed(2)}s |\n`;
    summary += `| Speed Index | ${(avg.metrics.speedIndex / 1000).toFixed(2)}s |\n\n`;
  });

  // Add Core Web Vitals assessment
  summary += '## Core Web Vitals Assessment\n\n';
  
  Object.entries(report.results).forEach(([pageName, data]) => {
    const avg = data.averages;
    const cwv = {
      lcp: avg.metrics.lcp <= 2500 ? '✅ Good' : avg.metrics.lcp <= 4000 ? '⚠️ Needs Improvement' : '❌ Poor',
      fid: avg.metrics.fid <= 100 ? '✅ Good' : avg.metrics.fid <= 300 ? '⚠️ Needs Improvement' : '❌ Poor',
      cls: avg.metrics.cls <= 0.1 ? '✅ Good' : avg.metrics.cls <= 0.25 ? '⚠️ Needs Improvement' : '❌ Poor',
    };
    
    summary += `### ${pageName}\n`;
    summary += `- LCP: ${cwv.lcp} (${(avg.metrics.lcp / 1000).toFixed(2)}s)\n`;
    summary += `- FID: ${cwv.fid} (${avg.metrics.fid.toFixed(0)}ms)\n`;
    summary += `- CLS: ${cwv.cls} (${avg.metrics.cls.toFixed(3)})\n\n`;
  });

  fs.writeFileSync(summaryPath, summary);

  return report;
}

/**
 * Run performance tests
 */
async function runPerformanceTests() {
  console.log('Starting performance tests...\n');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const allResults = {};

  try {
    for (const page of config.pages) {
      const results = await runLighthouseTest(browser, page);
      allResults[page.name] = results;
      console.log(`✓ Completed testing ${page.name}\n`);
    }

    const report = generateReport(allResults);
    
    console.log('\n📊 Performance Test Summary:');
    console.log('============================\n');
    
    Object.entries(report.results).forEach(([pageName, data]) => {
      const avg = data.averages;
      console.log(`${pageName}:`);
      console.log(`  Performance: ${avg.performance.toFixed(1)}%`);
      console.log(`  LCP: ${(avg.metrics.lcp / 1000).toFixed(2)}s`);
      console.log(`  FID: ${avg.metrics.fid.toFixed(0)}ms`);
      console.log(`  CLS: ${avg.metrics.cls.toFixed(3)}\n`);
    });

    console.log(`✅ Reports saved to: ${config.outputDir}`);
    
  } catch (error) {
    console.error('Error running performance tests:', error);
  } finally {
    await browser.close();
  }
}

// Run the tests
runPerformanceTests().catch(console.error);