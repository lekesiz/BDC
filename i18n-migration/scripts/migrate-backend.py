#!/usr/bin/env python3

"""
Migrate Backend Code to use i18n
This script replaces hardcoded strings with translation keys
"""

import os
import re
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import astor

# Configuration
CONFIG = {
    'src_path': Path(__file__).parent.parent.parent / 'server' / 'app',
    'translations_path': Path(__file__).parent.parent / 'translations' / 'backend-strings.json',
    'output_path': Path(__file__).parent.parent / 'reports' / 'backend-migration.json',
    'dry_run': False,
    'verbose': False,
    'key_mapping': {}
}

# Track migration stats
stats = {
    'files_processed': 0,
    'files_modified': 0,
    'strings_replaced': 0,
    'errors': [],
    'modifications': []
}


class TranslationTransformer(ast.NodeTransformer):
    """AST transformer to replace strings with translation calls"""
    
    def __init__(self, key_mapping: Dict[str, str], filepath: str):
        self.key_mapping = key_mapping
        self.filepath = filepath
        self.modified = False
        self.has_i18n_import = False
        self.i18n_service_name = None
        
    def visit_ImportFrom(self, node):
        """Check for existing i18n imports"""
        if node.module and 'i18n' in node.module:
            self.has_i18n_import = True
            # Try to find the service name
            for alias in node.names:
                if 'I18nManager' in str(alias.name) or 'translation' in str(alias.name).lower():
                    self.i18n_service_name = alias.asname or alias.name
        return node
        
    def visit_Str(self, node):
        """Replace string literals (Python < 3.8)"""
        if hasattr(node, 's') and node.s in self.key_mapping:
            return self._create_translation_call(node.s)
        return node
        
    def visit_Constant(self, node):
        """Replace string constants (Python >= 3.8)"""
        if isinstance(node.value, str) and node.value in self.key_mapping:
            return self._create_translation_call(node.value)
        return node
        
    def visit_Call(self, node):
        """Handle specific function calls like flash(), jsonify(), etc."""
        self.generic_visit(node)
        
        # Handle flash messages
        if (isinstance(node.func, ast.Name) and node.func.id == 'flash' and 
            node.args and isinstance(node.args[0], (ast.Str, ast.Constant))):
            text = node.args[0].s if hasattr(node.args[0], 's') else node.args[0].value
            if text in self.key_mapping:
                node.args[0] = self._create_translation_call(text)
                self.modified = True
                
        # Handle jsonify with message
        elif (isinstance(node.func, ast.Name) and node.func.id == 'jsonify' and 
              node.keywords):
            for keyword in node.keywords:
                if keyword.arg in ['message', 'error', 'success']:
                    if isinstance(keyword.value, (ast.Str, ast.Constant)):
                        text = keyword.value.s if hasattr(keyword.value, 's') else keyword.value.value
                        if text in self.key_mapping:
                            keyword.value = self._create_translation_call(text)
                            self.modified = True
                            
        return node
        
    def visit_Raise(self, node):
        """Handle exception messages"""
        self.generic_visit(node)
        
        if node.exc and isinstance(node.exc, ast.Call) and node.exc.args:
            first_arg = node.exc.args[0]
            if isinstance(first_arg, (ast.Str, ast.Constant)):
                text = first_arg.s if hasattr(first_arg, 's') else first_arg.value
                if text in self.key_mapping:
                    node.exc.args[0] = self._create_translation_call(text)
                    self.modified = True
                    
        return node
        
    def _create_translation_call(self, text: str) -> ast.Call:
        """Create a translation function call"""
        translation_key = self.key_mapping[text]
        
        # Record modification
        stats['strings_replaced'] += 1
        stats['modifications'].append({
            'file': str(self.filepath),
            'text': text,
            'key': translation_key,
            'line': None  # Would need more complex tracking for line numbers
        })
        
        # Create the translation call
        # Using a simple _() function call pattern
        return ast.Call(
            func=ast.Name(id='_', ctx=ast.Load()),
            args=[ast.Str(s=translation_key) if hasattr(ast, 'Str') else ast.Constant(value=translation_key)],
            keywords=[]
        )


def add_i18n_import(tree: ast.Module) -> bool:
    """Add i18n import to the module"""
    # Check if already has translation import
    has_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and ('i18n' in node.module or 'gettext' in node.module):
                has_import = True
                break
                
    if not has_import:
        # Add import at the beginning
        import_node = ast.ImportFrom(
            module='flask_babel',
            names=[ast.alias(name='gettext', asname='_')],
            level=0
        )
        
        # Find position after other imports
        insert_pos = 0
        for i, node in enumerate(tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                insert_pos = i + 1
            else:
                break
                
        tree.body.insert(insert_pos, import_node)
        return True
        
    return False


def process_file(filepath: Path) -> bool:
    """Process a single Python file"""
    try:
        # Skip if already processed
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '# TODO: i18n - processed' in content:
            if CONFIG['verbose']:
                print(f"⏭️  Skipping already processed: {filepath}")
            return False
            
        # Parse the file
        tree = ast.parse(content, filename=str(filepath))
        
        # Transform the AST
        transformer = TranslationTransformer(CONFIG['key_mapping'], filepath)
        new_tree = transformer.visit(tree)
        
        modified = transformer.modified
        
        # Add import if strings were replaced
        if modified:
            if add_i18n_import(new_tree):
                modified = True
                
        # Write back if modified and not dry run
        if modified and not CONFIG['dry_run']:
            # Generate code
            new_code = astor.to_source(new_tree)
            
            # Add processed marker
            final_code = f"# TODO: i18n - processed\n{new_code}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_code)
                
            stats['files_modified'] += 1
            
        stats['files_processed'] += 1
        
        if CONFIG['verbose'] and modified:
            print(f"✅ Modified: {filepath.relative_to(CONFIG['src_path'])}")
            
        return modified
        
    except Exception as e:
        stats['errors'].append({
            'file': str(filepath),
            'error': str(e)
        })
        if CONFIG['verbose']:
            print(f"❌ Error processing {filepath}: {e}")
        return False


def process_api_responses(filepath: Path) -> bool:
    """Special handling for API response patterns"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        modified = False
        
        # Pattern replacements for common API responses
        patterns = [
            # jsonify with message
            (r'jsonify\(\{[\'"](message|error|success)[\'"]:\s*[\'"]([^\'\"]+)[\'"]\}',
             lambda m: f'jsonify({{"{m.group(1)}": _("{CONFIG["key_mapping"].get(m.group(2), m.group(2))}")}}'),
            # return with message dict
            (r'return\s+\{[\'"](message|error|success)[\'"]:\s*[\'"]([^\'\"]+)[\'"]\}',
             lambda m: f'return {{"{m.group(1)}": _("{CONFIG["key_mapping"].get(m.group(2), m.group(2))}")}'),
            # flash messages
            (r'flash\([\'"]([^\'\"]+)[\'"]',
             lambda m: f'flash(_("{CONFIG["key_mapping"].get(m.group(1), m.group(1))}")')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
            
        if content != original_content:
            modified = True
            
            # Add import if needed
            if 'from flask_babel import gettext as _' not in content:
                # Find import section
                import_section_end = 0
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_section_end = i + 1
                        
                lines.insert(import_section_end, 'from flask_babel import gettext as _')
                content = '\n'.join(lines)
                
            if not CONFIG['dry_run']:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        return modified
        
    except Exception as e:
        if CONFIG['verbose']:
            print(f"Error in API response processing for {filepath}: {e}")
        return False


def update_translation_files():
    """Update translation files with new keys"""
    translation_files_path = CONFIG['src_path'].parent / 'app' / 'locales'
    
    # Get all unique keys
    all_keys = set(CONFIG['key_mapping'].values())
    
    # Load existing translations
    for lang_file in translation_files_path.glob('*.json'):
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                
            # Add missing keys
            modified = False
            for key in all_keys:
                parts = key.split('.')
                current = translations
                
                # Navigate/create nested structure
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                        modified = True
                    current = current[part]
                    
                # Add the final key if missing
                final_key = parts[-1]
                if final_key not in current:
                    # Find the original text for this key
                    original_text = None
                    for text, mapped_key in CONFIG['key_mapping'].items():
                        if mapped_key == key:
                            original_text = text
                            break
                            
                    current[final_key] = original_text or f"TODO: Translate {key}"
                    modified = True
                    
            # Write back if modified
            if modified and not CONFIG['dry_run']:
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(translations, f, indent=2, ensure_ascii=False)
                    
                print(f"✅ Updated translation file: {lang_file.name}")
                
        except Exception as e:
            print(f"Error updating {lang_file}: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Migrate backend code to use i18n')
    parser.add_argument('--dry-run', action='store_true', help='Run without modifying files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('pattern', nargs='?', default='**/*.py', help='File pattern to process')
    
    args = parser.parse_args()
    CONFIG['dry_run'] = args.dry_run
    CONFIG['verbose'] = args.verbose
    
    print("🔄 Migrating backend code to use i18n...\n")
    
    if CONFIG['dry_run']:
        print("🔍 Running in DRY RUN mode - no files will be modified\n")
        
    # Load extraction results
    try:
        with open(CONFIG['translations_path'], 'r', encoding='utf-8') as f:
            extraction_results = json.load(f)
            CONFIG['key_mapping'] = extraction_results.get('suggestedKeys', {})
    except Exception as e:
        print(f"❌ Could not load extraction results: {e}")
        print("Run extract-backend-strings.py first.")
        return 1
        
    # Find files to process
    files = list(CONFIG['src_path'].rglob(args.pattern))
    files = [f for f in files if '__pycache__' not in str(f) and f.suffix == '.py']
    
    print(f"Found {len(files)} files to process\n")
    
    # Process each file
    for i, filepath in enumerate(files):
        if i % 20 == 0 and not CONFIG['verbose']:
            print(f"\rProcessing... {round(i / len(files) * 100)}%", end='', flush=True)
            
        # Special handling for API files
        if 'api' in str(filepath):
            process_api_responses(filepath)
        else:
            process_file(filepath)
            
    if not CONFIG['verbose']:
        print("\r", end='')
        
    # Update translation files
    print("\n📝 Updating translation files...")
    update_translation_files()
    
    # Generate report
    report = {
        'summary': {
            'files_processed': stats['files_processed'],
            'files_modified': stats['files_modified'],
            'strings_replaced': stats['strings_replaced'],
            'errors_count': len(stats['errors']),
            'dry_run': CONFIG['dry_run'],
            'timestamp': str(Path.ctime(Path(__file__)))
        },
        'modifications': stats['modifications'],
        'errors': stats['errors']
    }
    
    # Write report
    CONFIG['output_path'].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG['output_path'], 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    # Print summary
    print("\n✅ Migration complete!\n")
    print("📊 Summary:")
    print(f"- Files processed: {stats['files_processed']}")
    print(f"- Files modified: {stats['files_modified']}")
    print(f"- Strings replaced: {stats['strings_replaced']}")
    print(f"- Errors: {len(stats['errors'])}")
    print(f"- Report saved to: {CONFIG['output_path']}")
    
    if stats['errors']:
        print("\n⚠️  Errors encountered:")
        for err in stats['errors'][:5]:
            print(f"  - {Path(err['file']).name}: {err['error']}")
        if len(stats['errors']) > 5:
            print(f"  ... and {len(stats['errors']) - 5} more")
            
    if CONFIG['dry_run']:
        print("\n💡 Run without --dry-run to apply changes")
        
    return 0


if __name__ == '__main__':
    exit(main())