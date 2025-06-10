#!/usr/bin/env node

/**
 * Extract Hardcoded Strings from React/JSX Files
 * This script identifies potential hardcoded strings that should be translated
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

// Configuration
const config = {
  srcPath: path.join(__dirname, '../../client/src'),
  outputPath: path.join(__dirname, '../translations/frontend-strings.json'),
  excludePatterns: [
    '**/node_modules/**',
    '**/*.test.js',
    '**/*.test.jsx',
    '**/*.spec.js',
    '**/*.spec.jsx',
    '**/test/**',
    '**/tests/**',
    '**/__tests__/**',
    '**/__mocks__/**'
  ],
  // Patterns that indicate a string should be translated
  translatePatterns: [
    /^[A-Z][a-z]+[\s\w]*$/, // Starts with capital letter
    /^[a-z]+[\s\w]*[.!?]$/, // Sentence ending with punctuation
    /\w+\s+\w+/, // Multiple words
  ],
  // Patterns to exclude from translation
  excludeStringPatterns: [
    /^[A-Z_]+$/, // All caps (likely constants)
    /^[a-z]+$/, // Single lowercase word (likely identifier)
    /^[0-9]+$/, // Numbers
    /^https?:\/\//, // URLs
    /^\//, // Paths
    /^\s*$/, // Empty or whitespace
    /^[a-z]+\/[a-z]+$/, // MIME types
    /^#[0-9a-fA-F]{3,6}$/, // Hex colors
    /^(true|false|null|undefined)$/, // Keywords
    /^(px|em|rem|%|vh|vw)$/, // CSS units
    /className|style|key|id|ref|type|name|value|onChange|onClick|onSubmit/, // Common props
    /^(GET|POST|PUT|DELETE|PATCH)$/, // HTTP methods
  ]
};

// Track found strings
const foundStrings = new Map();
const stringsByFile = new Map();

/**
 * Check if a string should be translated
 */
function shouldTranslate(str) {
  // Check exclusion patterns first
  for (const pattern of config.excludeStringPatterns) {
    if (pattern.test(str)) return false;
  }
  
  // Check if it matches translation patterns
  for (const pattern of config.translatePatterns) {
    if (pattern.test(str)) return true;
  }
  
  // Additional heuristics
  if (str.length > 3 && str.includes(' ')) return true;
  if (str.length > 10) return true;
  
  return false;
}

/**
 * Extract string location info
 */
function getLocationInfo(node, filePath) {
  return {
    file: path.relative(config.srcPath, filePath),
    line: node.loc ? node.loc.start.line : null,
    column: node.loc ? node.loc.start.column : null
  };
}

/**
 * Process JSX text
 */
function processJSXText(node, filePath) {
  const text = node.value.trim();
  if (text && shouldTranslate(text)) {
    if (!foundStrings.has(text)) {
      foundStrings.set(text, []);
    }
    foundStrings.get(text).push(getLocationInfo(node, filePath));
    
    if (!stringsByFile.has(filePath)) {
      stringsByFile.set(filePath, new Set());
    }
    stringsByFile.get(filePath).add(text);
  }
}

/**
 * Process string literals
 */
function processStringLiteral(node, filePath, parent) {
  // Skip if it's a key in an object
  if (parent && parent.type === 'ObjectProperty' && parent.key === node) {
    return;
  }
  
  // Skip if it's an import/require
  if (parent && (parent.type === 'ImportDeclaration' || parent.type === 'CallExpression' && parent.callee.name === 'require')) {
    return;
  }
  
  const text = node.value;
  if (typeof text === 'string' && shouldTranslate(text)) {
    if (!foundStrings.has(text)) {
      foundStrings.set(text, []);
    }
    foundStrings.get(text).push(getLocationInfo(node, filePath));
    
    if (!stringsByFile.has(filePath)) {
      stringsByFile.set(filePath, new Set());
    }
    stringsByFile.get(filePath).add(text);
  }
}

/**
 * Process template literals
 */
function processTemplateLiteral(node, filePath) {
  // Only process template literals without expressions
  if (node.expressions.length === 0 && node.quasis.length === 1) {
    const text = node.quasis[0].value.raw;
    if (shouldTranslate(text)) {
      if (!foundStrings.has(text)) {
        foundStrings.set(text, []);
      }
      foundStrings.get(text).push(getLocationInfo(node, filePath));
      
      if (!stringsByFile.has(filePath)) {
        stringsByFile.set(filePath, new Set());
      }
      stringsByFile.get(filePath).add(text);
    }
  }
}

/**
 * Parse and analyze a file
 */
function analyzeFile(filePath) {
  try {
    const code = fs.readFileSync(filePath, 'utf8');
    
    const ast = parser.parse(code, {
      sourceType: 'module',
      plugins: [
        'jsx',
        'typescript',
        'decorators-legacy',
        'classProperties',
        'dynamicImport',
        'exportDefaultFrom',
        'exportNamespaceFrom',
        'optionalChaining',
        'nullishCoalescingOperator'
      ]
    });
    
    traverse(ast, {
      JSXText(path) {
        processJSXText(path.node, filePath);
      },
      StringLiteral(path) {
        processStringLiteral(path.node, filePath, path.parent);
      },
      TemplateLiteral(path) {
        processTemplateLiteral(path.node, filePath);
      }
    });
    
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
  }
}

/**
 * Generate suggested translation keys
 */
function generateTranslationKey(text, context) {
  // Clean the text for key generation
  let key = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '_')
    .substring(0, 50);
  
  // Add context prefix if available
  if (context) {
    const prefix = context.split('/')[0].replace('.jsx', '').replace('.js', '');
    key = `${prefix}.${key}`;
  }
  
  return key;
}

/**
 * Main function
 */
async function main() {
  console.log('🔍 Extracting hardcoded strings from frontend...\n');
  
  // Find all JS/JSX files
  const files = glob.sync('**/*.{js,jsx,ts,tsx}', {
    cwd: config.srcPath,
    ignore: config.excludePatterns
  });
  
  console.log(`Found ${files.length} files to analyze\n`);
  
  // Process each file
  files.forEach((file, index) => {
    if (index % 50 === 0) {
      console.log(`Processing... ${Math.round(index / files.length * 100)}%`);
    }
    const filePath = path.join(config.srcPath, file);
    analyzeFile(filePath);
  });
  
  console.log('\n✅ Analysis complete!\n');
  
  // Generate report
  const report = {
    summary: {
      totalStrings: foundStrings.size,
      totalFiles: stringsByFile.size,
      timestamp: new Date().toISOString()
    },
    strings: {},
    byFile: {},
    suggestedKeys: {}
  };
  
  // Add strings with their locations
  foundStrings.forEach((locations, text) => {
    report.strings[text] = {
      occurrences: locations.length,
      locations: locations
    };
    
    // Generate suggested key
    const firstLocation = locations[0];
    report.suggestedKeys[text] = generateTranslationKey(text, firstLocation.file);
  });
  
  // Add file summary
  stringsByFile.forEach((strings, file) => {
    report.byFile[path.relative(config.srcPath, file)] = Array.from(strings);
  });
  
  // Sort strings by occurrence count
  const sortedStrings = Object.entries(report.strings)
    .sort((a, b) => b[1].occurrences - a[1].occurrences);
  
  // Write report
  fs.writeFileSync(
    config.outputPath,
    JSON.stringify(report, null, 2)
  );
  
  // Print summary
  console.log('📊 Summary:');
  console.log(`- Total unique strings found: ${foundStrings.size}`);
  console.log(`- Files with hardcoded strings: ${stringsByFile.size}`);
  console.log(`- Report saved to: ${config.outputPath}\n`);
  
  // Show top 10 most common strings
  console.log('🔝 Top 10 most common strings:');
  sortedStrings.slice(0, 10).forEach(([text, data]) => {
    console.log(`  "${text}" - ${data.occurrences} occurrences`);
  });
  
  // Show files with most strings
  const filesSorted = Array.from(stringsByFile.entries())
    .sort((a, b) => b[1].size - a[1].size)
    .slice(0, 10);
  
  console.log('\n📁 Files with most hardcoded strings:');
  filesSorted.forEach(([file, strings]) => {
    console.log(`  ${path.relative(config.srcPath, file)} - ${strings.size} strings`);
  });
}

// Run the script
main().catch(console.error);