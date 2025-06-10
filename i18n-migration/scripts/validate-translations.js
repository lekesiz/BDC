#!/usr/bin/env node

/**
 * Validate Translation Implementation
 * This script checks that all translations are properly implemented
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

// Configuration
const config = {
  srcPath: path.join(__dirname, '../../../client/src'),
  backendPath: path.join(__dirname, '../../../server/app'),
  frontendLocalesPath: path.join(__dirname, '../../../client/src/locales'),
  backendLocalesPath: path.join(__dirname, '../../../server/app/locales'),
  reportPath: path.join(__dirname, '../reports/validation-report.json'),
  languages: ['en', 'tr', 'ar', 'es', 'fr', 'de', 'ru']
};

// Validation results
const results = {
  frontend: {
    totalFiles: 0,
    filesWithTranslations: 0,
    unusedKeys: [],
    missingKeys: [],
    invalidKeys: [],
    hardcodedStrings: []
  },
  backend: {
    totalFiles: 0,
    filesWithTranslations: 0,
    unusedKeys: [],
    missingKeys: [],
    invalidKeys: [],
    hardcodedStrings: []
  },
  translations: {
    consistency: {},
    duplicates: {},
    quality: {}
  },
  summary: {
    passed: true,
    errors: 0,
    warnings: 0
  }
};

/**
 * Load all translation files
 */
function loadTranslations() {
  const translations = {};
  
  // Load frontend translations
  config.languages.forEach(lang => {
    const filePath = path.join(config.frontendLocalesPath, `${lang}.json`);
    if (fs.existsSync(filePath)) {
      try {
        translations[`frontend_${lang}`] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      } catch (error) {
        console.error(`Error loading ${filePath}:`, error.message);
      }
    }
  });
  
  // Load backend translations
  config.languages.forEach(lang => {
    const filePath = path.join(config.backendLocalesPath, `${lang}.json`);
    if (fs.existsSync(filePath)) {
      try {
        translations[`backend_${lang}`] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      } catch (error) {
        console.error(`Error loading ${filePath}:`, error.message);
      }
    }
  });
  
  return translations;
}

/**
 * Extract all keys from translations
 */
function extractAllKeys(translations) {
  const keys = new Set();
  
  function traverse(obj, prefix = '') {
    for (const [key, value] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      if (typeof value === 'object' && value !== null) {
        traverse(value, fullKey);
      } else {
        keys.add(fullKey);
      }
    }
  }
  
  traverse(translations);
  return keys;
}

/**
 * Check if string looks like it should be translated
 */
function shouldBeTranslated(str) {
  // Patterns that indicate a string should be translated
  const patterns = [
    /^[A-Z][a-z]+[\s\w]*$/,  // Starts with capital
    /\w+\s+\w+/,  // Multiple words
    /[.!?]$/  // Ends with punctuation
  ];
  
  // Exclude patterns
  const excludePatterns = [
    /^[A-Z_]+$/,  // All caps
    /^[a-z]+$/,  // Single word lowercase
    /^[0-9]+$/,  // Numbers
    /^https?:\/\//,  // URLs
    /^\//,  // Paths
    /^#[0-9a-fA-F]{6}$/  // Colors
  ];
  
  if (excludePatterns.some(p => p.test(str))) return false;
  return patterns.some(p => p.test(str)) || str.length > 10;
}

/**
 * Validate frontend file
 */
function validateFrontendFile(filePath, usedKeys, availableKeys) {
  try {
    const code = fs.readFileSync(filePath, 'utf8');
    const ast = parser.parse(code, {
      sourceType: 'module',
      plugins: ['jsx', 'typescript']
    });
    
    let hasTranslations = false;
    const fileKeys = new Set();
    const hardcodedStrings = [];
    
    traverse(ast, {
      // Check for translation usage
      CallExpression(path) {
        if (path.node.callee.name === 't' || 
            (path.node.callee.property && path.node.callee.property.name === 't')) {
          hasTranslations = true;
          
          // Extract translation key
          if (path.node.arguments[0] && path.node.arguments[0].value) {
            const key = path.node.arguments[0].value;
            fileKeys.add(key);
            usedKeys.add(key);
            
            // Check if key exists
            if (!availableKeys.has(key)) {
              results.frontend.missingKeys.push({
                key,
                file: path.relative(config.srcPath, filePath),
                line: path.node.loc?.start.line
              });
            }
          }
        }
      },
      
      // Check for hardcoded strings
      JSXText(path) {
        const text = path.node.value.trim();
        if (text && shouldBeTranslated(text)) {
          hardcodedStrings.push({
            text,
            file: path.relative(config.srcPath, filePath),
            line: path.node.loc?.start.line
          });
        }
      },
      
      StringLiteral(path) {
        // Skip translation keys
        if (path.parent.type === 'CallExpression' && 
            path.parent.callee.name === 't') {
          return;
        }
        
        const text = path.node.value;
        if (shouldBeTranslated(text)) {
          // Check if it's user-facing
          const parent = path.parent;
          if (parent.type === 'JSXAttribute' && 
              ['title', 'placeholder', 'alt'].includes(parent.name?.name)) {
            hardcodedStrings.push({
              text,
              file: path.relative(config.srcPath, filePath),
              line: path.node.loc?.start.line
            });
          }
        }
      }
    });
    
    if (hasTranslations) {
      results.frontend.filesWithTranslations++;
    }
    
    if (hardcodedStrings.length > 0) {
      results.frontend.hardcodedStrings.push(...hardcodedStrings);
    }
    
    results.frontend.totalFiles++;
    
  } catch (error) {
    console.error(`Error validating ${filePath}:`, error.message);
  }
}

/**
 * Validate backend file
 */
function validateBackendFile(filePath, usedKeys, availableKeys) {
  try {
    const code = fs.readFileSync(filePath, 'utf8');
    
    let hasTranslations = false;
    const hardcodedStrings = [];
    
    // Check for translation function usage
    const translationPatterns = [
      /_\(['"]([^'"]+)['"]\)/g,
      /gettext\(['"]([^'"]+)['"]\)/g,
      /ngettext\(['"]([^'"]+)['"]/g
    ];
    
    translationPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(code)) !== null) {
        hasTranslations = true;
        const key = match[1];
        usedKeys.add(key);
        
        if (!availableKeys.has(key)) {
          results.backend.missingKeys.push({
            key,
            file: path.relative(config.backendPath, filePath),
            line: code.substring(0, match.index).split('\n').length
          });
        }
      }
    });
    
    // Check for hardcoded strings in common patterns
    const hardcodedPatterns = [
      /flash\(['"]([^'"]+)['"]/g,
      /jsonify\(\{['"]message['"]:\s*['"]([^'"]+)['"]/g,
      /return\s+['"]([A-Z][^'"]+)['"]/g,
      /raise\s+\w+\(['"]([^'"]+)['"]/g
    ];
    
    hardcodedPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(code)) !== null) {
        const text = match[1];
        if (shouldBeTranslated(text) && !hasTranslations) {
          hardcodedStrings.push({
            text,
            file: path.relative(config.backendPath, filePath),
            line: code.substring(0, match.index).split('\n').length
          });
        }
      }
    });
    
    if (hasTranslations) {
      results.backend.filesWithTranslations++;
    }
    
    if (hardcodedStrings.length > 0) {
      results.backend.hardcodedStrings.push(...hardcodedStrings);
    }
    
    results.backend.totalFiles++;
    
  } catch (error) {
    console.error(`Error validating ${filePath}:`, error.message);
  }
}

/**
 * Check translation consistency
 */
function checkTranslationConsistency(translations) {
  const baseLanguage = 'en';
  const baseKeys = {
    frontend: extractAllKeys(translations[`frontend_${baseLanguage}`] || {}),
    backend: extractAllKeys(translations[`backend_${baseLanguage}`] || {})
  };
  
  // Check each language against base
  config.languages.forEach(lang => {
    if (lang === baseLanguage) return;
    
    results.translations.consistency[lang] = {
      frontend: { missing: [], extra: [] },
      backend: { missing: [], extra: [] }
    };
    
    // Check frontend
    const frontendKeys = extractAllKeys(translations[`frontend_${lang}`] || {});
    baseKeys.frontend.forEach(key => {
      if (!frontendKeys.has(key)) {
        results.translations.consistency[lang].frontend.missing.push(key);
      }
    });
    frontendKeys.forEach(key => {
      if (!baseKeys.frontend.has(key)) {
        results.translations.consistency[lang].frontend.extra.push(key);
      }
    });
    
    // Check backend
    const backendKeys = extractAllKeys(translations[`backend_${lang}`] || {});
    baseKeys.backend.forEach(key => {
      if (!backendKeys.has(key)) {
        results.translations.consistency[lang].backend.missing.push(key);
      }
    });
    backendKeys.forEach(key => {
      if (!baseKeys.backend.has(key)) {
        results.translations.consistency[lang].backend.extra.push(key);
      }
    });
  });
}

/**
 * Check for duplicate translations
 */
function checkDuplicateTranslations(translations) {
  Object.entries(translations).forEach(([langKey, trans]) => {
    const valueToKeys = {};
    
    function traverse(obj, prefix = '') {
      for (const [key, value] of Object.entries(obj)) {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        if (typeof value === 'string') {
          if (!valueToKeys[value]) {
            valueToKeys[value] = [];
          }
          valueToKeys[value].push(fullKey);
        } else if (typeof value === 'object' && value !== null) {
          traverse(value, fullKey);
        }
      }
    }
    
    traverse(trans);
    
    // Find duplicates
    const duplicates = {};
    Object.entries(valueToKeys).forEach(([value, keys]) => {
      if (keys.length > 1 && value.length > 5) {  // Ignore short common words
        duplicates[value] = keys;
      }
    });
    
    if (Object.keys(duplicates).length > 0) {
      results.translations.duplicates[langKey] = duplicates;
    }
  });
}

/**
 * Check translation quality
 */
function checkTranslationQuality(translations) {
  config.languages.forEach(lang => {
    if (lang === 'en') return;
    
    results.translations.quality[lang] = {
      untranslated: [],
      placeholders: [],
      tooLong: []
    };
    
    // Check frontend translations
    const frontendTrans = translations[`frontend_${lang}`] || {};
    const frontendBase = translations['frontend_en'] || {};
    
    function checkQuality(trans, base, prefix = '') {
      Object.entries(trans).forEach(([key, value]) => {
        const fullKey = prefix ? `${prefix}.${key}` : key;
        const baseValue = base[key];
        
        if (typeof value === 'string' && typeof baseValue === 'string') {
          // Check for untranslated (same as English)
          if (value === baseValue && lang !== 'en') {
            results.translations.quality[lang].untranslated.push(fullKey);
          }
          
          // Check for placeholder translations
          if (value.startsWith(`[${lang.toUpperCase()}]`)) {
            results.translations.quality[lang].placeholders.push(fullKey);
          }
          
          // Check if translation is too long compared to original
          if (value.length > baseValue.length * 2) {
            results.translations.quality[lang].tooLong.push({
              key: fullKey,
              original: baseValue.length,
              translated: value.length
            });
          }
        } else if (typeof value === 'object' && value !== null) {
          checkQuality(value, base[key] || {}, fullKey);
        }
      });
    }
    
    checkQuality(frontendTrans, frontendBase);
    
    // Same for backend
    const backendTrans = translations[`backend_${lang}`] || {};
    const backendBase = translations['backend_en'] || {};
    checkQuality(backendTrans, backendBase);
  });
}

/**
 * Generate summary
 */
function generateSummary() {
  // Count errors and warnings
  results.summary.errors = 
    results.frontend.missingKeys.length +
    results.backend.missingKeys.length +
    results.frontend.invalidKeys.length +
    results.backend.invalidKeys.length;
    
  results.summary.warnings = 
    results.frontend.hardcodedStrings.length +
    results.backend.hardcodedStrings.length;
    
  // Check consistency issues
  Object.values(results.translations.consistency).forEach(lang => {
    results.summary.errors += lang.frontend.missing.length + lang.backend.missing.length;
    results.summary.warnings += lang.frontend.extra.length + lang.backend.extra.length;
  });
  
  // Check quality issues
  Object.values(results.translations.quality).forEach(lang => {
    results.summary.warnings += 
      lang.untranslated.length + 
      lang.placeholders.length;
  });
  
  results.summary.passed = results.summary.errors === 0;
}

/**
 * Main validation function
 */
async function main() {
  console.log('🔍 Validating i18n implementation...\n');
  
  // Load all translations
  console.log('📚 Loading translation files...');
  const translations = loadTranslations();
  const availableKeys = {
    frontend: extractAllKeys(translations['frontend_en'] || {}),
    backend: extractAllKeys(translations['backend_en'] || {})
  };
  
  // Track used keys
  const usedKeys = {
    frontend: new Set(),
    backend: new Set()
  };
  
  // Validate frontend files
  console.log('\n🔍 Validating frontend files...');
  const frontendFiles = glob.sync('**/*.{js,jsx}', {
    cwd: config.srcPath,
    ignore: ['**/node_modules/**', '**/*.test.js', '**/*.spec.js']
  });
  
  frontendFiles.forEach(file => {
    validateFrontendFile(
      path.join(config.srcPath, file),
      usedKeys.frontend,
      availableKeys.frontend
    );
  });
  
  // Validate backend files
  console.log('🔍 Validating backend files...');
  const backendFiles = glob.sync('**/*.py', {
    cwd: config.backendPath,
    ignore: ['**/__pycache__/**', '**/migrations/**', '**/tests/**']
  });
  
  backendFiles.forEach(file => {
    validateBackendFile(
      path.join(config.backendPath, file),
      usedKeys.backend,
      availableKeys.backend
    );
  });
  
  // Find unused keys
  availableKeys.frontend.forEach(key => {
    if (!usedKeys.frontend.has(key)) {
      results.frontend.unusedKeys.push(key);
    }
  });
  
  availableKeys.backend.forEach(key => {
    if (!usedKeys.backend.has(key)) {
      results.backend.unusedKeys.push(key);
    }
  });
  
  // Check translation consistency
  console.log('🔍 Checking translation consistency...');
  checkTranslationConsistency(translations);
  
  // Check for duplicates
  console.log('🔍 Checking for duplicate translations...');
  checkDuplicateTranslations(translations);
  
  // Check translation quality
  console.log('🔍 Checking translation quality...');
  checkTranslationQuality(translations);
  
  // Generate summary
  generateSummary();
  
  // Save report
  fs.writeFileSync(config.reportPath, JSON.stringify(results, null, 2));
  
  // Print results
  console.log('\n📊 Validation Results:\n');
  
  console.log('Frontend:');
  console.log(`  Files: ${results.frontend.totalFiles} total, ${results.frontend.filesWithTranslations} with translations`);
  console.log(`  Missing keys: ${results.frontend.missingKeys.length}`);
  console.log(`  Unused keys: ${results.frontend.unusedKeys.length}`);
  console.log(`  Hardcoded strings: ${results.frontend.hardcodedStrings.length}`);
  
  console.log('\nBackend:');
  console.log(`  Files: ${results.backend.totalFiles} total, ${results.backend.filesWithTranslations} with translations`);
  console.log(`  Missing keys: ${results.backend.missingKeys.length}`);
  console.log(`  Unused keys: ${results.backend.unusedKeys.length}`);
  console.log(`  Hardcoded strings: ${results.backend.hardcodedStrings.length}`);
  
  // Show consistency issues
  let hasConsistencyIssues = false;
  Object.entries(results.translations.consistency).forEach(([lang, data]) => {
    const totalIssues = 
      data.frontend.missing.length + data.frontend.extra.length +
      data.backend.missing.length + data.backend.extra.length;
      
    if (totalIssues > 0) {
      if (!hasConsistencyIssues) {
        console.log('\n⚠️  Translation Consistency Issues:');
        hasConsistencyIssues = true;
      }
      console.log(`  ${lang}: ${totalIssues} issues`);
    }
  });
  
  // Show quality issues
  let hasQualityIssues = false;
  Object.entries(results.translations.quality).forEach(([lang, data]) => {
    const totalIssues = 
      data.untranslated.length + data.placeholders.length + data.tooLong.length;
      
    if (totalIssues > 0) {
      if (!hasQualityIssues) {
        console.log('\n⚠️  Translation Quality Issues:');
        hasQualityIssues = true;
      }
      console.log(`  ${lang}: ${data.untranslated.length} untranslated, ${data.placeholders.length} placeholders`);
    }
  });
  
  // Final status
  console.log('\n' + '='.repeat(50));
  if (results.summary.passed) {
    console.log('✅ Validation PASSED!');
  } else {
    console.log('❌ Validation FAILED!');
  }
  console.log(`   Errors: ${results.summary.errors}`);
  console.log(`   Warnings: ${results.summary.warnings}`);
  console.log('='.repeat(50));
  
  console.log(`\nDetailed report saved to: ${config.reportPath}`);
  
  // Exit with error code if failed
  if (!results.summary.passed) {
    process.exit(1);
  }
}

// Run validation
main().catch(console.error);