#!/usr/bin/env node

/**
 * Update Translation Files with Missing Keys
 * This script adds missing translation keys to all language files
 */

const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  // Translation file locations
  backendLocalesPath: path.join(__dirname, '../../server/app/locales'),
  frontendLocalesPath: path.join(__dirname, '../../client/src/i18n/locales'),
  // Extracted strings
  frontendStringsPath: path.join(__dirname, '../translations/frontend-strings.json'),
  backendStringsPath: path.join(__dirname, '../translations/backend-strings.json'),
  // Output
  missingKeysPath: path.join(__dirname, '../translations/missing-keys.json'),
  // Languages to update
  languages: ['en', 'tr', 'ar', 'es', 'fr', 'de', 'ru'],
  // Default language for base translations
  defaultLanguage: 'en'
};

// Track statistics
const stats = {
  keysAdded: 0,
  filesUpdated: 0,
  errors: []
};

/**
 * Load JSON file safely
 */
function loadJsonFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }
  } catch (error) {
    console.error(`Error loading ${filePath}:`, error.message);
  }
  return null;
}

/**
 * Save JSON file with proper formatting
 */
function saveJsonFile(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
    return true;
  } catch (error) {
    console.error(`Error saving ${filePath}:`, error.message);
    return false;
  }
}

/**
 * Get nested object value using dot notation
 */
function getNestedValue(obj, path) {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}

/**
 * Set nested object value using dot notation
 */
function setNestedValue(obj, path, value) {
  const keys = path.split('.');
  const lastKey = keys.pop();
  const target = keys.reduce((current, key) => {
    if (!current[key]) current[key] = {};
    return current[key];
  }, obj);
  target[lastKey] = value;
}

/**
 * Extract all translation keys from existing files
 */
function extractExistingKeys(translations) {
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
 * Generate translation key from text
 */
function generateKey(text, context = '') {
  // Clean the text
  let key = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '_')
    .substring(0, 40);
  
  // Add context prefix
  if (context) {
    // Extract meaningful context from file path
    const parts = context.split('/');
    let prefix = 'common';
    
    if (parts.includes('components')) {
      const compIndex = parts.indexOf('components');
      if (parts[compIndex + 1]) {
        prefix = parts[compIndex + 1].replace('.jsx', '').replace('.js', '');
      }
    } else if (parts.includes('pages')) {
      prefix = 'pages';
    } else if (parts.includes('api')) {
      prefix = 'api';
    }
    
    key = `${prefix}.${key}`;
  }
  
  return key;
}

/**
 * Process extracted strings and generate missing keys
 */
function processMissingKeys() {
  const missingKeys = {
    frontend: {},
    backend: {},
    summary: {
      totalMissing: 0,
      byLanguage: {}
    }
  };
  
  // Load extracted strings
  const frontendStrings = loadJsonFile(config.frontendStringsPath);
  const backendStrings = loadJsonFile(config.backendStringsPath);
  
  if (!frontendStrings && !backendStrings) {
    console.error('❌ No extracted strings found. Run extraction scripts first.');
    return null;
  }
  
  // Process each language
  config.languages.forEach(lang => {
    missingKeys.summary.byLanguage[lang] = {
      frontend: 0,
      backend: 0
    };
    
    // Check frontend translations
    if (frontendStrings) {
      const translationFile = path.join(config.frontendLocalesPath, `${lang}.json`);
      const translations = loadJsonFile(translationFile) || {};
      const existingKeys = extractExistingKeys(translations);
      
      Object.entries(frontendStrings.strings || {}).forEach(([text, data]) => {
        const suggestedKey = frontendStrings.suggestedKeys?.[text] || generateKey(text);
        
        if (!existingKeys.has(suggestedKey)) {
          if (!missingKeys.frontend[suggestedKey]) {
            missingKeys.frontend[suggestedKey] = {
              text,
              languages: [],
              occurrences: data.occurrences,
              locations: data.locations
            };
          }
          missingKeys.frontend[suggestedKey].languages.push(lang);
          missingKeys.summary.byLanguage[lang].frontend++;
        }
      });
    }
    
    // Check backend translations
    if (backendStrings) {
      const translationFile = path.join(config.backendLocalesPath, `${lang}.json`);
      const translations = loadJsonFile(translationFile) || {};
      const existingKeys = extractExistingKeys(translations);
      
      Object.entries(backendStrings.strings || {}).forEach(([text, data]) => {
        const suggestedKey = backendStrings.suggestedKeys?.[text] || generateKey(text);
        
        if (!existingKeys.has(suggestedKey)) {
          if (!missingKeys.backend[suggestedKey]) {
            missingKeys.backend[suggestedKey] = {
              text,
              languages: [],
              occurrences: data.occurrences,
              locations: data.locations
            };
          }
          missingKeys.backend[suggestedKey].languages.push(lang);
          missingKeys.summary.byLanguage[lang].backend++;
        }
      });
    }
  });
  
  // Calculate totals
  missingKeys.summary.totalMissing = 
    Object.keys(missingKeys.frontend).length + 
    Object.keys(missingKeys.backend).length;
  
  return missingKeys;
}

/**
 * Add missing keys to translation files
 */
function updateTranslationFiles(missingKeys) {
  // Update frontend translations
  console.log('\n📝 Updating frontend translation files...');
  
  config.languages.forEach(lang => {
    const filePath = path.join(config.frontendLocalesPath, `${lang}.json`);
    let translations = loadJsonFile(filePath) || {};
    let modified = false;
    
    Object.entries(missingKeys.frontend).forEach(([key, data]) => {
      if (data.languages.includes(lang)) {
        // Use original text for default language, placeholder for others
        const value = lang === config.defaultLanguage 
          ? data.text 
          : `[${lang.toUpperCase()}] ${data.text}`;
        
        setNestedValue(translations, key, value);
        modified = true;
        stats.keysAdded++;
      }
    });
    
    if (modified) {
      // Ensure directory exists
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      if (saveJsonFile(filePath, translations)) {
        stats.filesUpdated++;
        console.log(`  ✅ Updated ${lang}.json (frontend) - ${stats.keysAdded} keys added`);
      }
    }
  });
  
  // Update backend translations
  console.log('\n📝 Updating backend translation files...');
  
  config.languages.forEach(lang => {
    const filePath = path.join(config.backendLocalesPath, `${lang}.json`);
    let translations = loadJsonFile(filePath) || {};
    let modified = false;
    let keysAdded = 0;
    
    Object.entries(missingKeys.backend).forEach(([key, data]) => {
      if (data.languages.includes(lang)) {
        // Use original text for default language, placeholder for others
        const value = lang === config.defaultLanguage 
          ? data.text 
          : `[${lang.toUpperCase()}] ${data.text}`;
        
        setNestedValue(translations, key, value);
        modified = true;
        keysAdded++;
      }
    });
    
    if (modified) {
      if (saveJsonFile(filePath, translations)) {
        stats.filesUpdated++;
        console.log(`  ✅ Updated ${lang}.json (backend) - ${keysAdded} keys added`);
      }
    }
  });
}

/**
 * Generate translation coverage report
 */
function generateCoverageReport() {
  const report = {
    timestamp: new Date().toISOString(),
    languages: {},
    overall: {
      totalKeys: 0,
      translated: 0,
      missing: 0,
      coverage: 0
    }
  };
  
  // Analyze each language
  config.languages.forEach(lang => {
    const frontendFile = path.join(config.frontendLocalesPath, `${lang}.json`);
    const backendFile = path.join(config.backendLocalesPath, `${lang}.json`);
    
    const frontendTranslations = loadJsonFile(frontendFile) || {};
    const backendTranslations = loadJsonFile(backendFile) || {};
    
    const frontendKeys = extractExistingKeys(frontendTranslations);
    const backendKeys = extractExistingKeys(backendTranslations);
    
    // Count placeholders (untranslated)
    let untranslated = 0;
    
    function countUntranslated(obj) {
      for (const value of Object.values(obj)) {
        if (typeof value === 'string' && value.startsWith(`[${lang.toUpperCase()}]`)) {
          untranslated++;
        } else if (typeof value === 'object' && value !== null) {
          countUntranslated(value);
        }
      }
    }
    
    countUntranslated(frontendTranslations);
    countUntranslated(backendTranslations);
    
    const totalKeys = frontendKeys.size + backendKeys.size;
    const translated = totalKeys - untranslated;
    
    report.languages[lang] = {
      totalKeys,
      translated,
      untranslated,
      coverage: totalKeys > 0 ? Math.round((translated / totalKeys) * 100) : 0,
      frontend: {
        keys: frontendKeys.size,
        translated: frontendKeys.size - Math.floor(untranslated * (frontendKeys.size / totalKeys))
      },
      backend: {
        keys: backendKeys.size,
        translated: backendKeys.size - Math.ceil(untranslated * (backendKeys.size / totalKeys))
      }
    };
    
    report.overall.totalKeys += totalKeys;
    report.overall.translated += translated;
    report.overall.missing += untranslated;
  });
  
  report.overall.coverage = report.overall.totalKeys > 0 
    ? Math.round((report.overall.translated / report.overall.totalKeys) * 100)
    : 0;
  
  return report;
}

/**
 * Main function
 */
async function main() {
  console.log('🌐 Updating translation files with missing keys...\n');
  
  // Process missing keys
  console.log('🔍 Analyzing missing translation keys...');
  const missingKeys = processMissingKeys();
  
  if (!missingKeys) {
    return;
  }
  
  // Save missing keys report
  saveJsonFile(config.missingKeysPath, missingKeys);
  
  // Print summary
  console.log('\n📊 Missing Keys Summary:');
  console.log(`- Frontend: ${Object.keys(missingKeys.frontend).length} keys`);
  console.log(`- Backend: ${Object.keys(missingKeys.backend).length} keys`);
  console.log(`- Total: ${missingKeys.summary.totalMissing} keys\n`);
  
  // Show by language
  console.log('By Language:');
  Object.entries(missingKeys.summary.byLanguage).forEach(([lang, counts]) => {
    console.log(`  ${lang}: ${counts.frontend + counts.backend} missing (frontend: ${counts.frontend}, backend: ${counts.backend})`);
  });
  
  // Update translation files
  updateTranslationFiles(missingKeys);
  
  // Generate coverage report
  console.log('\n📈 Generating coverage report...');
  const coverageReport = generateCoverageReport();
  saveJsonFile(
    path.join(__dirname, '../reports/coverage-report.json'),
    coverageReport
  );
  
  // Print coverage summary
  console.log('\n📊 Translation Coverage:');
  Object.entries(coverageReport.languages).forEach(([lang, data]) => {
    console.log(`  ${lang}: ${data.coverage}% (${data.translated}/${data.totalKeys} keys)`);
  });
  console.log(`\n  Overall: ${coverageReport.overall.coverage}% coverage`);
  
  // Final summary
  console.log('\n✅ Update complete!');
  console.log(`- Keys added: ${stats.keysAdded}`);
  console.log(`- Files updated: ${stats.filesUpdated}`);
  
  if (stats.errors.length > 0) {
    console.log(`\n⚠️  Errors: ${stats.errors.length}`);
    stats.errors.forEach(err => console.log(`  - ${err}`));
  }
  
  // Next steps
  console.log('\n📋 Next steps:');
  console.log('1. Review the updated translation files');
  console.log('2. Translate placeholder entries (marked with [LANG])');
  console.log('3. Run migration scripts to update the code');
  console.log('4. Test with different languages');
}

// Run the script
main().catch(console.error);