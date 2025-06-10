#!/usr/bin/env python
"""Apply i18n migration to replace hardcoded strings with translation functions."""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import shutil
from datetime import datetime

class I18nTransformer(ast.NodeTransformer):
    """AST transformer to replace string literals with translation calls."""
    
    def __init__(self, translations_map: Dict[str, str], file_path: str):
        self.translations_map = translations_map
        self.file_path = file_path
        self.imports_needed = set()
        self.changes_made = []
        
    def visit_Module(self, node):
        """Visit module and add imports if needed."""
        self.generic_visit(node)
        
        # Add i18n imports at the top if we made changes
        if self.changes_made:
            # Check if already has i18n imports
            has_i18n_import = False
            for item in node.body:
                if isinstance(item, ast.ImportFrom):
                    if item.module == 'flask_babel' and any(alias.name == '_' for alias in item.names):
                        has_i18n_import = True
                        break
                        
            if not has_i18n_import:
                # Add import statement
                import_node = ast.ImportFrom(
                    module='flask_babel',
                    names=[ast.alias(name='_', asname=None), ast.alias(name='lazy_gettext', asname='_l')],
                    level=0
                )
                # Insert after the first imports/docstring
                insert_pos = 0
                for i, item in enumerate(node.body):
                    if not isinstance(item, (ast.Import, ast.ImportFrom, ast.Expr)):
                        insert_pos = i
                        break
                    insert_pos = i + 1
                    
                node.body.insert(insert_pos, import_node)
                
        return node
        
    def visit_Str(self, node):
        """Visit string nodes (Python < 3.8)."""
        return self._handle_string(node, node.s)
        
    def visit_Constant(self, node):
        """Visit constant nodes (Python >= 3.8)."""
        if isinstance(node.value, str):
            return self._handle_string(node, node.value)
        return node
        
    def _handle_string(self, node, value):
        """Handle string replacement."""
        # Check if this string should be translated
        if value in self.translations_map:
            translation_key = self.translations_map[value]
            
            # Record the change
            self.changes_made.append({
                'line': node.lineno if hasattr(node, 'lineno') else 0,
                'original': value,
                'key': translation_key
            })
            
            # Create translation call
            return ast.Call(
                func=ast.Name(id='_', ctx=ast.Load()),
                args=[ast.Str(s=translation_key)],
                keywords=[]
            )
            
        return node
        
    def visit_JoinedStr(self, node):
        """Handle f-strings - convert to format strings with translation."""
        # For now, skip f-strings as they need special handling
        return node


def create_translations_map(translation_keys: Dict[str, Dict], extracted_strings: Dict[str, List]) -> Dict[str, str]:
    """Create a mapping from original strings to translation keys."""
    string_to_key = {}
    
    # Flatten translation keys
    for category, keys in translation_keys.items():
        for key, value in keys.items():
            string_to_key[value] = key
            
    return string_to_key


def transform_file(file_path: Path, translations_map: Dict[str, str], backup_dir: Path) -> Dict:
    """Transform a single file to use translations."""
    try:
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        # Create backup
        backup_path = backup_dir / file_path.relative_to(file_path.parent.parent)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
        # Parse AST
        tree = ast.parse(original_content, filename=str(file_path))
        
        # Transform
        transformer = I18nTransformer(translations_map, str(file_path))
        new_tree = transformer.visit(tree)
        
        # Only write if changes were made
        if transformer.changes_made:
            # Convert back to source code
            try:
                import astor
                new_content = astor.to_source(new_tree)
            except ImportError:
                # Fallback: use ast.unparse (Python 3.9+)
                new_content = ast.unparse(new_tree)
                
            # Write transformed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return {
                'file': str(file_path),
                'changes': len(transformer.changes_made),
                'details': transformer.changes_made
            }
            
        return None
        
    except Exception as e:
        print(f"Error transforming {file_path}: {e}")
        return None


def update_translation_files(translation_keys: Dict[str, Dict], locales_dir: Path):
    """Update translation JSON files with new keys."""
    
    # Flatten keys for easier updating
    all_keys = {}
    for category, keys in translation_keys.items():
        all_keys.update(keys)
    
    # Languages to update
    languages = ['en', 'tr', 'ar', 'es', 'fr', 'de', 'ru']
    
    for lang in languages:
        locale_file = locales_dir / f"{lang}.json"
        
        # Load existing translations
        if locale_file.exists():
            with open(locale_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        else:
            translations = {}
            
        # Add new keys (only to English, others need manual translation)
        if lang == 'en':
            # Organize by category
            for category, keys in translation_keys.items():
                if category not in translations:
                    translations[category] = {}
                    
                for key, value in keys.items():
                    # Use simplified key structure
                    key_parts = key.split('.')
                    if len(key_parts) > 2:
                        simple_key = '.'.join(key_parts[-2:])
                    else:
                        simple_key = key
                        
                    translations[category][simple_key] = value
        else:
            # For other languages, add keys with placeholder
            for category, keys in translation_keys.items():
                if category not in translations:
                    translations[category] = {}
                    
                for key, value in keys.items():
                    key_parts = key.split('.')
                    if len(key_parts) > 2:
                        simple_key = '.'.join(key_parts[-2:])
                    else:
                        simple_key = key
                        
                    if simple_key not in translations[category]:
                        # Add placeholder
                        translations[category][simple_key] = f"[{lang.upper()}] {value}"
                        
        # Save updated translations
        with open(locale_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Updated {lang}.json with new translation keys")


def main():
    """Main migration process."""
    project_root = Path(__file__).parent.parent
    migration_dir = project_root / 'i18n_migration'
    
    # Load extraction results
    with open(migration_dir / 'extracted_strings.json', 'r', encoding='utf-8') as f:
        extracted_strings = json.load(f)
        
    with open(migration_dir / 'translation_keys.json', 'r', encoding='utf-8') as f:
        translation_keys = json.load(f)
        
    with open(migration_dir / 'file_priorities.json', 'r', encoding='utf-8') as f:
        file_priorities = json.load(f)
        
    print("🚀 Starting i18n migration...")
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = migration_dir / f'backup_{timestamp}'
    backup_dir.mkdir(exist_ok=True)
    
    # Create translations map
    translations_map = create_translations_map(translation_keys, extracted_strings)
    
    # Update translation files first
    locales_dir = project_root / 'app' / 'locales'
    update_translation_files(translation_keys, locales_dir)
    
    # Transform files (top 20 priority files for now)
    migration_results = []
    files_to_migrate = [fp[0] for fp in file_priorities[:20]]  # Start with top 20 files
    
    print(f"\n📝 Migrating {len(files_to_migrate)} high-priority files...")
    
    for file_path in files_to_migrate:
        full_path = project_root / 'app' / file_path
        if full_path.exists():
            result = transform_file(full_path, translations_map, backup_dir)
            if result:
                migration_results.append(result)
                print(f"   ✅ {file_path}: {result['changes']} strings replaced")
                
    # Generate migration report
    report = {
        'timestamp': timestamp,
        'total_files_analyzed': len(extracted_strings),
        'total_strings_found': sum(len(strings) for strings in extracted_strings.values()),
        'files_migrated': len(migration_results),
        'strings_replaced': sum(r['changes'] for r in migration_results),
        'backup_location': str(backup_dir),
        'migration_details': migration_results
    }
    
    # Save report
    with open(migration_dir / 'migration_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    # Generate readable report
    with open(migration_dir / 'MIGRATION_REPORT.md', 'w', encoding='utf-8') as f:
        f.write("# I18n Migration Report\n\n")
        f.write(f"**Date**: {timestamp}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Total files analyzed: {report['total_files_analyzed']}\n")
        f.write(f"- Total strings found: {report['total_strings_found']}\n")
        f.write(f"- Files migrated: {report['files_migrated']}\n")
        f.write(f"- Strings replaced: {report['strings_replaced']}\n")
        f.write(f"- Backup location: `{report['backup_location']}`\n\n")
        
        f.write("## Files Migrated\n\n")
        for result in migration_results:
            f.write(f"### {result['file']}\n")
            f.write(f"- Changes: {result['changes']}\n")
            f.write("- Sample replacements:\n")
            for detail in result['details'][:5]:  # Show first 5
                f.write(f"  - Line {detail['line']}: `\"{detail['original']}\"` → `_(\"{detail['key']}\")`\n")
            if len(result['details']) > 5:
                f.write(f"  - ... and {len(result['details']) - 5} more\n")
            f.write("\n")
            
        f.write("## Next Steps\n\n")
        f.write("1. Review the migrated files and test functionality\n")
        f.write("2. Translate the new keys in non-English locale files\n")
        f.write("3. Run tests to ensure nothing is broken\n")
        f.write("4. Continue migration for remaining files\n")
        
    print(f"\n✅ Migration complete! Report saved to: {migration_dir}/MIGRATION_REPORT.md")
    

if __name__ == '__main__':
    main()