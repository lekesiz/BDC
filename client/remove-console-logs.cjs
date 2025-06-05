#!/usr/bin/env node
/**
 * Script to remove console.log statements from production code
 * Keeps console.error and console.warn for debugging
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Patterns to match console.log statements
const consoleLogPatterns = [
  /console\.log\s*\([^)]*\)\s*;?/g,
  /console\.debug\s*\([^)]*\)\s*;?/g,
  /console\.info\s*\([^)]*\)\s*;?/g,
];

// Files to exclude from processing
const excludePatterns = [
  '**/node_modules/**',
  '**/dist/**',
  '**/build/**',
  '**/*.test.js',
  '**/*.spec.js',
  '**/remove-console-logs.js',
  '**/vite.config*.js',
  '**/vitest.config.js',
];

function removeConsoleLogs(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    
    consoleLogPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        content = content.replace(pattern, '');
        modified = true;
      }
    });
    
    if (modified) {
      // Clean up empty lines left behind
      content = content.replace(/^\s*\n/gm, '');
      content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
      
      fs.writeFileSync(filePath, content, 'utf8');
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
    return false;
  }
}

function main() {
  console.log('🧹 Removing console.log statements from client code...\n');
  
  // Find all JavaScript and JSX files
  const files = glob.sync('src/**/*.{js,jsx}', {
    ignore: excludePatterns,
    nodir: true,
  });
  
  console.log(`Found ${files.length} files to process\n`);
  
  let processedCount = 0;
  let modifiedCount = 0;
  
  files.forEach(file => {
    processedCount++;
    if (removeConsoleLogs(file)) {
      modifiedCount++;
      console.log(`✅ Cleaned: ${file}`);
    }
  });
  
  console.log(`\n📊 Summary:`);
  console.log(`   Total files processed: ${processedCount}`);
  console.log(`   Files modified: ${modifiedCount}`);
  console.log(`   Files unchanged: ${processedCount - modifiedCount}`);
  
  if (modifiedCount > 0) {
    console.log('\n✨ Console.log statements removed successfully!');
    console.log('💡 Remember to test your application to ensure functionality is intact.');
  } else {
    console.log('\n✨ No console.log statements found. Code is already clean!');
  }
}

// Check if glob is installed
try {
  require.resolve('glob');
  main();
} catch (e) {
  console.error('❌ Please install glob first: npm install --save-dev glob');
  process.exit(1);
}