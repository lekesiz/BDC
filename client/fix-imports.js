const fs = require('fs');
const path = require('path');

// Function to calculate relative path
function getRelativePath(from, to) {
  // Remove the filename from the 'from' path to get the directory
  const fromDir = path.dirname(from);
  let relative = path.relative(fromDir, to);
  
  // If relative is empty (same directory), use ./
  if (!relative) {
    relative = './';
  } else if (!relative.startsWith('.')) {
    relative = './' + relative;
  }
  
  return relative;
}

// Process a file
function processFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  let updatedContent = content;
  
  // Match all import statements
  const importRegex = /^import\s+(.+?)\s+from\s+['"](@\/|@)(.+?)['"]/gm;
  
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    const fullMatch = match[0];
    const importPart = match[1];
    const aliasPrefix = match[2];
    const importPath = match[3];
    
    // Resolve the absolute path
    let absolutePath;
    if (aliasPrefix === '@/') {
      absolutePath = path.join('/Users/mikail/Desktop/BDC/client/src', importPath);
    } else if (aliasPrefix === '@') {
      // If @ is used alone, it might be followed by a folder alias or just @/
      if (importPath.startsWith('/')) {
        absolutePath = path.join('/Users/mikail/Desktop/BDC/client/src', importPath.slice(1));
      } else {
        // Check for aliases like @components, @hooks, etc.
        const aliasMappings = {
          'components': '/Users/mikail/Desktop/BDC/client/src/components',
          'context': '/Users/mikail/Desktop/BDC/client/src/context',
          'hooks': '/Users/mikail/Desktop/BDC/client/src/hooks',
          'lib': '/Users/mikail/Desktop/BDC/client/src/lib',
          'pages': '/Users/mikail/Desktop/BDC/client/src/pages',
          'store': '/Users/mikail/Desktop/BDC/client/src/store',
          'assets': '/Users/mikail/Desktop/BDC/client/src/assets'
        };
        
        const firstPart = importPath.split('/')[0];
        if (aliasMappings[firstPart]) {
          absolutePath = path.join(aliasMappings[firstPart], importPath.slice(firstPart.length + 1));
        } else {
          absolutePath = path.join('/Users/mikail/Desktop/BDC/client/src', importPath);
        }
      }
    }
    
    // Calculate relative path
    const relativePath = getRelativePath(filePath, absolutePath);
    
    // Replace the import
    const newImport = `import ${importPart} from '${relativePath}'`;
    updatedContent = updatedContent.replace(fullMatch, newImport);
  }
  
  // Also fix imports without @ that aren't from node_modules and don't start with ./ or ../
  const absoluteImportRegex = /^import\s+(.+?)\s+from\s+['"](?![@./])([^'"]+)['"]$/gm;
  
  // Reset the regex
  absoluteImportRegex.lastIndex = 0;
  
  while ((match = absoluteImportRegex.exec(content)) !== null) {
    const fullMatch = match[0];
    const importPart = match[1];
    const importPath = match[2];
    
    // Skip if it's a package import (no slashes or starts with a package name pattern)
    if (!importPath.includes('/') || /^[a-z0-9]([a-z0-9-._])*$/.test(importPath.split('/')[0])) {
      continue;
    }
    
    // This is likely an absolute import that needs to be fixed
    const absolutePath = path.join('/Users/mikail/Desktop/BDC/client/src', importPath);
    const relativePath = getRelativePath(filePath, absolutePath);
    
    const newImport = `import ${importPart} from '${relativePath}'`;
    updatedContent = updatedContent.replace(fullMatch, newImport);
  }
  
  // Write the updated content back if there were changes
  if (updatedContent !== content) {
    fs.writeFileSync(filePath, updatedContent, 'utf8');
    console.log(`Updated: ${filePath}`);
  }
}

// Find all JavaScript/TypeScript files
function findFiles(dir, pattern) {
  const results = [];
  const list = fs.readdirSync(dir);
  
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat && stat.isDirectory()) {
      results.push(...findFiles(filePath, pattern));
    } else if (pattern.test(file)) {
      results.push(filePath);
    }
  });
  
  return results;
}

// Main function
function main() {
  const srcDir = '/Users/mikail/Desktop/BDC/client/src';
  const pattern = /\.(js|jsx|ts|tsx)$/;
  
  const files = findFiles(srcDir, pattern);
  
  console.log(`Found ${files.length} files to process`);
  
  files.forEach(file => {
    processFile(file);
  });
  
  console.log('Done!');
}

main();