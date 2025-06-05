#!/usr/bin/env python3
"""
Replace print statements with proper logging in Python files
"""

import os
import re
import sys
from pathlib import Path

# Logging template
LOGGING_TEMPLATE = """import logging

logger = logging.getLogger(__name__)
"""

def add_logger_import(content):
    """Add logger import if not present"""
    if 'import logging' not in content and 'from app.utils.logging import logger' not in content:
        # Check if there's already an import block
        import_match = re.search(r'^(import .*|from .* import .*)', content, re.MULTILINE)
        if import_match:
            # Add after the last import
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    last_import_idx = i
            
            # Insert logger import after last import
            lines.insert(last_import_idx + 1, '')
            lines.insert(last_import_idx + 2, 'from app.utils.logging import logger')
            content = '\n'.join(lines)
        else:
            # Add at the beginning
            content = 'from app.utils.logging import logger\n\n' + content
    
    return content

def replace_print_statements(file_path):
    """Replace print statements with logger calls"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Skip test files and migration files
        if ('test_' in str(file_path) or 
            '/tests/' in str(file_path) or
            '/migrations/' in str(file_path) or
            'create_' in str(file_path) or
            'seed_' in str(file_path) or
            'debug_' in str(file_path)):
            return False
        
        # Pattern to match print statements
        patterns = [
            # print("message")
            (r'print\s*\(\s*"([^"]+)"\s*\)', r'logger.info("\1")'),
            (r"print\s*\(\s*'([^']+)'\s*\)", r'logger.info("\1")'),
            
            # print(f"message {var}")
            (r'print\s*\(\s*f"([^"]+)"\s*\)', r'logger.info(f"\1")'),
            (r"print\s*\(\s*f'([^']+)'\s*\)", r'logger.info(f"\1")'),
            
            # print("Error:", error)
            (r'print\s*\(\s*"([^"]+error[^"]*)"[,\s]+([^)]+)\)', r'logger.error("\1: %s", \2)'),
            (r"print\s*\(\s*'([^']+error[^']*)'[,\s]+([^)]+)\)", r'logger.error("\1: %s", \2)'),
            
            # print("Warning:", something)
            (r'print\s*\(\s*"([^"]+warning[^"]*)"[,\s]+([^)]+)\)', r'logger.warning("\1: %s", \2)'),
            (r"print\s*\(\s*'([^']+warning[^']*)'[,\s]+([^)]+)\)", r'logger.warning("\1: %s", \2)'),
            
            # print("Debug:", something)  
            (r'print\s*\(\s*"([^"]+debug[^"]*)"[,\s]+([^)]+)\)', r'logger.debug("\1: %s", \2)'),
            
            # Generic print with multiple args
            (r'print\s*\(([^)]+)\)', lambda m: f'logger.info({m.group(1)})'),
        ]
        
        modified = False
        for pattern, replacement in patterns:
            if callable(replacement):
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            else:
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            if new_content != content:
                content = new_content
                modified = True
        
        # If we made changes, ensure logger is imported
        if modified:
            content = add_logger_import(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("🧹 Replacing print statements with proper logging...\n")
    
    # Find all Python files
    server_path = Path('.')
    py_files = list(server_path.rglob('*.py'))
    
    print(f"Found {len(py_files)} Python files\n")
    
    processed = 0
    modified = 0
    
    for file_path in py_files:
        # Skip certain directories
        if any(skip in str(file_path) for skip in [
            '__pycache__', 
            'venv/', 
            'env/', 
            '.env/',
            'node_modules/',
            'htmlcov/',
            'replace-print-statements.py'
        ]):
            continue
        
        processed += 1
        if replace_print_statements(file_path):
            modified += 1
            print(f"✅ Updated: {file_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {processed}")
    print(f"   Files modified: {modified}")
    print(f"   Files unchanged: {processed - modified}")
    
    if modified > 0:
        print("\n✨ Print statements replaced with logging!")
        print("💡 Remember to test the application to ensure functionality is intact.")
    else:
        print("\n✨ No print statements found that need replacing!")

if __name__ == '__main__':
    main()