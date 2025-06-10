import fs from 'fs';
import path from 'path';
import { glob } from 'glob';

// Function to find corresponding test file for a component
function findTestFile(componentPath) {
  const baseName = path.basename(componentPath, path.extname(componentPath));
  const dirName = path.dirname(componentPath);
  
  // Possible test locations
  const testPaths = [
    // Same directory
    path.join(dirName, `${baseName}.test.jsx`),
    path.join(dirName, `${baseName}.test.js`),
    // __tests__ subfolder
    path.join(dirName, '__tests__', `${baseName}.test.jsx`),
    path.join(dirName, '__tests__', `${baseName}.test.js`),
    // tests folder structure
    componentPath.replace('/src/', '/src/tests/').replace('.jsx', '.test.jsx'),
    componentPath.replace('/src/', '/src/tests/').replace('.js', '.test.js'),
  ];
  
  for (const testPath of testPaths) {
    if (fs.existsSync(testPath)) {
      return testPath;
    }
  }
  return null;
}

async function analyzeTestCoverage() {
  const srcDir = '/Users/mikail/Desktop/BDC/client/src';
  
  // Get all component files
  const componentFiles = await glob('**/*.{js,jsx}', {
    cwd: srcDir,
    ignore: [
      '**/*.test.{js,jsx}',
      '**/*.stories.{js,jsx}',
      '**/tests/**',
      '**/__tests__/**',
      '**/test/**',
      '**/__mocks__/**',
      '**/mockData/**',
      '**/mock*.{js,jsx}',
      '**/setup*.{js,jsx}',
      'main.jsx',
      'validate.js',
      '**/*.config.{js,jsx}',
      '**/index.{js,jsx}',
      '**/*.css',
      '**/node_modules/**'
    ]
  });
  
  // Categorize files
  const categories = {
    pages: [],
    components: [],
    hooks: [],
    services: [],
    contexts: [],
    utils: [],
    other: []
  };
  
  const untested = {
    pages: [],
    components: [],
    hooks: [],
    services: [],
    contexts: [],
    utils: [],
    other: []
  };
  
  for (const file of componentFiles) {
    const fullPath = path.join(srcDir, file);
    const hasTest = findTestFile(fullPath) !== null;
    
    let category = 'other';
    if (file.startsWith('pages/')) category = 'pages';
    else if (file.startsWith('components/')) category = 'components';
    else if (file.includes('hooks/') || file.includes('use')) category = 'hooks';
    else if (file.startsWith('services/') || file.includes('service') || file.includes('api')) category = 'services';
    else if (file.startsWith('contexts/')) category = 'contexts';
    else if (file.includes('utils/') || file.startsWith('lib/')) category = 'utils';
    
    categories[category].push(file);
    if (!hasTest) {
      untested[category].push(file);
    }
  }
  
  // Generate report
  console.log('=== BDC Client Test Coverage Analysis ===\n');
  
  console.log('Summary:');
  console.log(`Total component files: ${componentFiles.length}`);
  console.log(`Total files with tests: ${componentFiles.length - Object.values(untested).flat().length}`);
  console.log(`Coverage percentage: ${((componentFiles.length - Object.values(untested).flat().length) / componentFiles.length * 100).toFixed(1)}%\n`);
  
  console.log('Coverage by Category:');
  for (const [category, files] of Object.entries(categories)) {
    const tested = files.length - untested[category].length;
    const percentage = files.length > 0 ? (tested / files.length * 100).toFixed(1) : 0;
    console.log(`${category.padEnd(12)}: ${tested}/${files.length} (${percentage}%)`);
  }
  
  console.log('\n=== Top Priority Files Needing Tests ===\n');
  
  // Priority 1: Critical pages
  console.log('1. Critical Pages (High Priority):');
  const criticalPages = untested.pages.filter(f => 
    f.includes('Login') || 
    f.includes('Dashboard') || 
    f.includes('Beneficiaries') ||
    f.includes('Evaluation') ||
    f.includes('Program')
  ).slice(0, 10);
  criticalPages.forEach(f => console.log(`   - ${f}`));
  
  // Priority 2: Core components
  console.log('\n2. Core Components (High Priority):');
  const coreComponents = untested.components.filter(f => 
    f.includes('common/') ||
    f.includes('layout/') ||
    f.includes('forms/') ||
    f.includes('ui/')
  ).slice(0, 10);
  coreComponents.forEach(f => console.log(`   - ${f}`));
  
  // Priority 3: Hooks and Services
  console.log('\n3. Hooks & Services (Medium Priority):');
  const hooksAndServices = [...untested.hooks, ...untested.services].slice(0, 10);
  hooksAndServices.forEach(f => console.log(`   - ${f}`));
  
  // Priority 4: Contexts
  console.log('\n4. Contexts (Medium Priority):');
  untested.contexts.forEach(f => console.log(`   - ${f}`));
  
  // Priority 5: Utils
  console.log('\n5. Utilities (Low Priority):');
  untested.utils.slice(0, 5).forEach(f => console.log(`   - ${f}`));
  
  console.log('\n=== Top 10 Files Needing Test Coverage ===');
  const top10 = [
    ...criticalPages.slice(0, 3),
    ...coreComponents.slice(0, 3),
    ...hooksAndServices.slice(0, 2),
    ...untested.contexts.slice(0, 2)
  ].slice(0, 10);
  
  console.log('\nRecommended order for test implementation:');
  top10.forEach((f, i) => console.log(`${i + 1}. ${f}`));
}

analyzeTestCoverage().catch(console.error);