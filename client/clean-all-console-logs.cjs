#!/usr/bin/env node
/**
 * More aggressive console.log cleanup script
 * Handles multi-line console.log statements
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

function removeConsoleLogs(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Remove single-line console statements
    content = content.replace(/console\.(log|debug|info)\s*\([^)]*\)\s*;?/g, '');
    
    // Remove multi-line console statements (more aggressive)
    content = content.replace(/console\.(log|debug|info)\s*\([^)]*\)[^;]*;?/gs, '');
    
    // Handle console statements with template literals and complex expressions
    content = content.replace(/console\.(log|debug|info)\s*\(\s*`[^`]*`[^)]*\)\s*;?/gs, '');
    
    // Remove console statements in JSX
    content = content.replace(/\{console\.(log|debug|info)\s*\([^}]*\)\}/g, '{}');
    
    // Clean up conditional console logs
    content = content.replace(/[^{]*&&\s*console\.(log|debug|info)\s*\([^)]*\)\s*;?/g, '');
    
    // Clean up if statements that only contain console.log
    content = content.replace(/if\s*\([^)]*\)\s*{\s*console\.(log|debug|info)\s*\([^}]*\);\?\s*}/g, '');
    
    // Remove empty lines and clean up spacing
    content = content.replace(/^\s*\n/gm, '');
    content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    // Fix any broken syntax from aggressive removal
    content = content.replace(/;;\+/g, ';');
    content = content.replace(/,\s*,/g, ',');
    content = content.replace(/{\s*}/g, '{}');
    
    if (content !== originalContent) {
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
  console.log('🧹 Running aggressive console.log cleanup...\n');
  
  // Find all JavaScript and JSX files
  const srcFiles = glob.sync('src/**/*.{js,jsx}', {
    ignore: ['**/node_modules/**', '**/dist/**', '**/build/**'],
    nodir: true,
  });
  
  // Also check lib directory
  const libFiles = glob.sync('lib/**/*.{js,jsx}', {
    ignore: ['**/node_modules/**'],
    nodir: true,
  });
  
  // Also check contexts directory  
  const contextFiles = glob.sync('contexts/**/*.{js,jsx}', {
    ignore: ['**/node_modules/**'],
    nodir: true,
  });
  
  // Also check pages directory
  const pageFiles = glob.sync('pages/**/*.{js,jsx}', {
    ignore: ['**/node_modules/**'],
    nodir: true,
  });
  
  const allFiles = [...srcFiles, ...libFiles, ...contextFiles, ...pageFiles];
  
  console.log(`Found ${allFiles.length} files to process\n`);
  
  let processedCount = 0;
  let modifiedCount = 0;
  
  allFiles.forEach(file => {
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
}

main();