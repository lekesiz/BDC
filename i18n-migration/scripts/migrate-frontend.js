#!/usr/bin/env node

/**
 * Migrate Frontend Components to use i18n
 * This script replaces hardcoded strings with translation keys
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');

// Configuration
const config = {
  srcPath: path.join(__dirname, '../../client/src'),
  translationsPath: path.join(__dirname, '../translations/frontend-strings.json'),
  outputPath: path.join(__dirname, '../reports/frontend-migration.json'),
  dryRun: process.argv.includes('--dry-run'),
  verbose: process.argv.includes('--verbose'),
  // Files to process (can be limited for testing)
  filePattern: process.argv[2] || '**/*.{js,jsx}',
  // Translation key mapping
  keyMapping: {}
};

// Load string extraction results
let extractionResults = {};
try {
  extractionResults = JSON.parse(fs.readFileSync(config.translationsPath, 'utf8'));
  config.keyMapping = extractionResults.suggestedKeys || {};
} catch (error) {
  console.error('❌ Could not load extraction results. Run extract-hardcoded-strings.js first.');
  process.exit(1);
}

// Track migration stats
const stats = {
  filesProcessed: 0,
  filesModified: 0,
  stringsReplaced: 0,
  errors: [],
  modifications: []
};

/**
 * Check if component already uses translations
 */
function hasTranslationImport(ast) {
  let hasImport = false;
  traverse(ast, {
    ImportDeclaration(path) {
      const source = path.node.source.value;
      if (source.includes('useTranslation') || 
          source.includes('react-i18next') ||
          source.includes('hooks/useTranslations')) {
        hasImport = true;
        path.stop();
      }
    }
  });
  return hasImport;
}

/**
 * Add translation import to file
 */
function addTranslationImport(ast) {
  const importDeclaration = t.importDeclaration(
    [t.importSpecifier(
      t.identifier('useTranslation'),
      t.identifier('useTranslation')
    )],
    t.stringLiteral('react-i18next')
  );
  
  // Find the last import and insert after it
  let lastImportIndex = -1;
  ast.program.body.forEach((node, index) => {
    if (t.isImportDeclaration(node)) {
      lastImportIndex = index;
    }
  });
  
  if (lastImportIndex >= 0) {
    ast.program.body.splice(lastImportIndex + 1, 0, importDeclaration);
  } else {
    ast.program.body.unshift(importDeclaration);
  }
}

/**
 * Check if component uses translation hook
 */
function findTranslationHook(path) {
  let hookName = null;
  
  path.traverse({
    VariableDeclarator(varPath) {
      if (varPath.node.init && 
          t.isCallExpression(varPath.node.init) &&
          varPath.node.init.callee.name === 'useTranslation') {
        if (t.isObjectPattern(varPath.node.id)) {
          // const { t } = useTranslation()
          varPath.node.id.properties.forEach(prop => {
            if (prop.key.name === 't') {
              hookName = prop.value.name;
            }
          });
        }
      }
    }
  });
  
  return hookName;
}

/**
 * Add translation hook to component
 */
function addTranslationHook(path) {
  const hookCall = t.variableDeclaration('const', [
    t.variableDeclarator(
      t.objectPattern([
        t.objectProperty(
          t.identifier('t'),
          t.identifier('t'),
          false,
          true
        )
      ]),
      t.callExpression(t.identifier('useTranslation'), [])
    )
  ]);
  
  // Find the first statement in the component and insert the hook
  const bodyPath = path.get('body');
  if (bodyPath.isBlockStatement()) {
    bodyPath.unshiftContainer('body', hookCall);
  }
}

/**
 * Replace string with translation
 */
function replaceWithTranslation(path, translationKey, tFunction = 't') {
  const translationCall = t.callExpression(
    t.identifier(tFunction),
    [t.stringLiteral(translationKey)]
  );
  
  if (path.isJSXText()) {
    // Replace JSX text with expression container
    const jsxExpressionContainer = t.jsxExpressionContainer(translationCall);
    path.replaceWith(jsxExpressionContainer);
  } else {
    // Replace string literal
    path.replaceWith(translationCall);
  }
}

/**
 * Process a React component
 */
function processComponent(componentPath, filePath) {
  let modified = false;
  let tFunction = findTranslationHook(componentPath);
  
  // If no translation hook found, add it
  if (!tFunction) {
    addTranslationHook(componentPath);
    tFunction = 't';
    modified = true;
  }
  
  // Process all strings in the component
  componentPath.traverse({
    JSXText(path) {
      const text = path.node.value.trim();
      if (text && config.keyMapping[text]) {
        replaceWithTranslation(path, config.keyMapping[text], tFunction);
        stats.stringsReplaced++;
        modified = true;
        
        stats.modifications.push({
          file: filePath,
          text: text,
          key: config.keyMapping[text],
          line: path.node.loc?.start.line
        });
      }
    },
    StringLiteral(path) {
      // Skip if it's a translation key already
      if (path.parent.type === 'CallExpression' && 
          path.parent.callee.name === tFunction) {
        return;
      }
      
      const text = path.node.value;
      if (config.keyMapping[text]) {
        // Check context to ensure it's user-facing text
        const parent = path.parent;
        const isUserFacing = 
          parent.type === 'JSXAttribute' && 
          ['title', 'placeholder', 'alt', 'aria-label'].includes(parent.name?.name) ||
          parent.type === 'CallExpression' && 
          ['alert', 'confirm', 'console.log'].includes(parent.callee?.name) ||
          parent.type === 'JSXExpressionContainer';
        
        if (isUserFacing) {
          replaceWithTranslation(path, config.keyMapping[text], tFunction);
          stats.stringsReplaced++;
          modified = true;
          
          stats.modifications.push({
            file: filePath,
            text: text,
            key: config.keyMapping[text],
            line: path.node.loc?.start.line
          });
        }
      }
    }
  });
  
  return modified;
}

/**
 * Process a file
 */
function processFile(filePath) {
  try {
    const code = fs.readFileSync(filePath, 'utf8');
    
    // Skip if file is already processed (has TODO: i18n comment)
    if (code.includes('// TODO: i18n - processed')) {
      if (config.verbose) {
        console.log(`⏭️  Skipping already processed: ${filePath}`);
      }
      return;
    }
    
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
    
    let fileModified = false;
    
    // Add import if needed
    if (!hasTranslationImport(ast)) {
      addTranslationImport(ast);
      fileModified = true;
    }
    
    // Find and process React components
    traverse(ast, {
      FunctionDeclaration(path) {
        if (path.node.id && /^[A-Z]/.test(path.node.id.name)) {
          if (processComponent(path, filePath)) {
            fileModified = true;
          }
        }
      },
      FunctionExpression(path) {
        if (path.parent.type === 'VariableDeclarator' && 
            path.parent.id && 
            /^[A-Z]/.test(path.parent.id.name)) {
          if (processComponent(path, filePath)) {
            fileModified = true;
          }
        }
      },
      ArrowFunctionExpression(path) {
        if (path.parent.type === 'VariableDeclarator' && 
            path.parent.id && 
            /^[A-Z]/.test(path.parent.id.name)) {
          if (processComponent(path, filePath)) {
            fileModified = true;
          }
        }
      }
    });
    
    // Write modified file
    if (fileModified && !config.dryRun) {
      const output = generate(ast, { 
        retainLines: true,
        retainFunctionParens: true,
        comments: true
      }, code);
      
      // Add processed marker
      const finalCode = `// TODO: i18n - processed\n${output.code}`;
      fs.writeFileSync(filePath, finalCode);
      stats.filesModified++;
    }
    
    stats.filesProcessed++;
    
    if (config.verbose && fileModified) {
      console.log(`✅ Modified: ${path.relative(config.srcPath, filePath)}`);
    }
    
  } catch (error) {
    stats.errors.push({
      file: filePath,
      error: error.message
    });
    if (config.verbose) {
      console.error(`❌ Error processing ${filePath}:`, error.message);
    }
  }
}

/**
 * Main function
 */
async function main() {
  console.log('🔄 Migrating frontend components to use i18n...\n');
  
  if (config.dryRun) {
    console.log('🔍 Running in DRY RUN mode - no files will be modified\n');
  }
  
  // Find files to process
  const files = glob.sync(config.filePattern, {
    cwd: config.srcPath,
    ignore: ['**/node_modules/**', '**/*.test.js', '**/*.spec.js']
  });
  
  console.log(`Found ${files.length} files to process\n`);
  
  // Process each file
  files.forEach((file, index) => {
    if (index % 10 === 0 && !config.verbose) {
      process.stdout.write(`\rProcessing... ${Math.round(index / files.length * 100)}%`);
    }
    const filePath = path.join(config.srcPath, file);
    processFile(filePath);
  });
  
  if (!config.verbose) {
    process.stdout.write('\r');
  }
  
  // Generate report
  const report = {
    summary: {
      filesProcessed: stats.filesProcessed,
      filesModified: stats.filesModified,
      stringsReplaced: stats.stringsReplaced,
      errorsCount: stats.errors.length,
      dryRun: config.dryRun,
      timestamp: new Date().toISOString()
    },
    modifications: stats.modifications,
    errors: stats.errors
  };
  
  // Write report
  fs.writeFileSync(config.outputPath, JSON.stringify(report, null, 2));
  
  // Print summary
  console.log('\n✅ Migration complete!\n');
  console.log('📊 Summary:');
  console.log(`- Files processed: ${stats.filesProcessed}`);
  console.log(`- Files modified: ${stats.filesModified}`);
  console.log(`- Strings replaced: ${stats.stringsReplaced}`);
  console.log(`- Errors: ${stats.errors.length}`);
  console.log(`- Report saved to: ${config.outputPath}`);
  
  if (stats.errors.length > 0) {
    console.log('\n⚠️  Errors encountered:');
    stats.errors.slice(0, 5).forEach(err => {
      console.log(`  - ${path.relative(config.srcPath, err.file)}: ${err.error}`);
    });
    if (stats.errors.length > 5) {
      console.log(`  ... and ${stats.errors.length - 5} more`);
    }
  }
  
  if (config.dryRun) {
    console.log('\n💡 Run without --dry-run to apply changes');
  }
}

// Run the script
main().catch(console.error);