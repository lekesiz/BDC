#!/usr/bin/env python
"""Extract hardcoded strings from Python files for i18n migration."""

import os
import ast
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class StringExtractor(ast.NodeVisitor):
    """AST visitor to extract string literals from Python code."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.strings = []
        self.skip_patterns = [
            r'^$',  # Empty strings
            r'^\s+$',  # Whitespace only
            r'^[0-9]+$',  # Numbers only
            r'^[A-Z_]+$',  # Uppercase constants
            r'^/.*',  # URL paths
            r'^\.',  # File extensions
            r'^[a-z_]+$',  # Snake case identifiers
            r'^[a-zA-Z]+\.[a-zA-Z]+$',  # Module paths
            r'^__.*__$',  # Python magic strings
            r'^application/.*',  # MIME types
            r'^text/.*',  # MIME types
            r'^Bearer',  # Auth headers
            r'^Basic',  # Auth headers
            r'^UTF-8',  # Encodings
            r'^utf-8',  # Encodings
        ]
        
    def should_skip(self, string: str) -> bool:
        """Check if string should be skipped."""
        # Skip very short strings
        if len(string) < 3:
            return True
            
        # Skip strings that match skip patterns
        for pattern in self.skip_patterns:
            if re.match(pattern, string):
                return True
                
        # Skip SQL queries
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE']
        if any(keyword in string.upper() for keyword in sql_keywords):
            return True
            
        return False
        
    def visit_Str(self, node):
        """Visit string nodes (Python < 3.8)."""
        if not self.should_skip(node.s):
            self.strings.append({
                'value': node.s,
                'line': node.lineno,
                'type': 'message'
            })
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        """Visit constant nodes (Python >= 3.8)."""
        if isinstance(node.value, str) and not self.should_skip(node.value):
            # Determine string type based on content
            string_type = self.categorize_string(node.value)
            self.strings.append({
                'value': node.value,
                'line': node.lineno,
                'type': string_type
            })
        self.generic_visit(node)
        
    def visit_JoinedStr(self, node):
        """Visit f-string nodes."""
        # Extract the template parts
        template_parts = []
        for value in node.values:
            if isinstance(value, ast.Str):
                template_parts.append(value.s)
            elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                template_parts.append(value.value)
        
        # Join template parts
        if template_parts:
            template = ''.join(template_parts)
            if not self.should_skip(template):
                self.strings.append({
                    'value': template,
                    'line': node.lineno,
                    'type': 'template',
                    'is_fstring': True
                })
        self.generic_visit(node)
        
    def categorize_string(self, value: str) -> str:
        """Categorize string by its likely usage."""
        # Error messages
        if any(word in value.lower() for word in ['error', 'fail', 'invalid', 'wrong', 'cannot', 'unable']):
            return 'error'
            
        # Success messages
        if any(word in value.lower() for word in ['success', 'complete', 'created', 'updated', 'deleted', 'saved']):
            return 'success'
            
        # Validation messages
        if any(word in value.lower() for word in ['required', 'must', 'should', 'valid', 'format']):
            return 'validation'
            
        # Labels/UI text
        if len(value.split()) <= 3 and value[0].isupper():
            return 'label'
            
        # General messages
        return 'message'


def extract_strings_from_file(filepath: Path) -> List[Dict]:
    """Extract strings from a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content, filename=str(filepath))
        extractor = StringExtractor(str(filepath))
        extractor.visit(tree)
        
        return extractor.strings
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def extract_strings_from_directory(directory: Path, exclude_dirs: Set[str] = None) -> Dict[str, List[Dict]]:
    """Extract strings from all Python files in directory."""
    if exclude_dirs is None:
        exclude_dirs = {'venv', '__pycache__', '.git', 'htmlcov', 'migrations', 'tests'}
        
    results = defaultdict(list)
    
    for filepath in directory.rglob('*.py'):
        # Skip excluded directories
        if any(excluded in filepath.parts for excluded in exclude_dirs):
            continue
            
        rel_path = filepath.relative_to(directory)
        strings = extract_strings_from_file(filepath)
        
        if strings:
            results[str(rel_path)] = strings
            
    return dict(results)


def generate_translation_keys(strings_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    """Generate translation keys from extracted strings."""
    translations = defaultdict(lambda: defaultdict(dict))
    key_counter = defaultdict(int)
    
    for filepath, strings in strings_data.items():
        # Extract module path from filepath
        module_parts = filepath.replace('.py', '').split('/')
        
        for string_info in strings:
            value = string_info['value']
            string_type = string_info['type']
            
            # Generate key based on module and string type
            module_key = '_'.join(module_parts[-2:]) if len(module_parts) > 1 else module_parts[0]
            
            # Create a simplified key from the string value
            value_key = re.sub(r'[^a-zA-Z0-9]+', '_', value[:30]).strip('_').lower()
            
            # Handle duplicates
            base_key = f"{module_key}.{string_type}.{value_key}"
            key = base_key
            
            if key in key_counter:
                key_counter[key] += 1
                key = f"{base_key}_{key_counter[key]}"
            else:
                key_counter[key] = 0
                
            # Store translation
            translations[string_type][key] = value
            
    return dict(translations)


def main():
    """Main extraction process."""
    # Project root
    project_root = Path(__file__).parent.parent
    app_dir = project_root / 'app'
    
    print("🔍 Extracting hardcoded strings from BDC project...")
    print(f"   Scanning directory: {app_dir}")
    
    # Extract strings
    strings_data = extract_strings_from_directory(app_dir)
    
    # Generate statistics
    total_files = len(strings_data)
    total_strings = sum(len(strings) for strings in strings_data.values())
    
    print(f"\n📊 Extraction Summary:")
    print(f"   Files scanned: {total_files}")
    print(f"   Strings found: {total_strings}")
    
    # Count by type
    type_counts = defaultdict(int)
    for strings in strings_data.values():
        for string_info in strings:
            type_counts[string_info['type']] += 1
            
    print(f"\n📈 String Categories:")
    for string_type, count in sorted(type_counts.items()):
        print(f"   {string_type}: {count}")
    
    # Generate translation keys
    translations = generate_translation_keys(strings_data)
    
    # Save extraction results
    output_dir = project_root / 'i18n_migration'
    output_dir.mkdir(exist_ok=True)
    
    # Save raw extraction data
    with open(output_dir / 'extracted_strings.json', 'w', encoding='utf-8') as f:
        json.dump(strings_data, f, indent=2, ensure_ascii=False)
        
    # Save translation keys
    with open(output_dir / 'translation_keys.json', 'w', encoding='utf-8') as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)
        
    # Generate priority files list (most strings first)
    file_priorities = sorted(
        [(filepath, len(strings)) for filepath, strings in strings_data.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    print(f"\n🎯 Top 10 files with most strings:")
    for filepath, count in file_priorities[:10]:
        print(f"   {filepath}: {count} strings")
        
    # Save priority list
    with open(output_dir / 'file_priorities.json', 'w', encoding='utf-8') as f:
        json.dump(file_priorities, f, indent=2)
        
    print(f"\n✅ Extraction complete! Results saved to: {output_dir}")
    

if __name__ == '__main__':
    main()