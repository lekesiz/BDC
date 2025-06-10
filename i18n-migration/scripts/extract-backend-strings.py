#!/usr/bin/env python3

"""
Extract Hardcoded Strings from Python Backend Files
This script identifies potential hardcoded strings that should be translated
"""

import os
import re
import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Configuration
CONFIG = {
    'src_path': Path(__file__).parent.parent.parent / 'server' / 'app',
    'output_path': Path(__file__).parent.parent / 'translations' / 'backend-strings.json',
    'exclude_patterns': [
        '__pycache__',
        '.pyc',
        'migrations',
        'tests',
        'test_',
        '_test.py',
        'conftest.py'
    ],
    # Patterns that indicate a string should be translated
    'translate_patterns': [
        r'^[A-Z][a-z]+[\s\w]*$',  # Starts with capital letter
        r'^[a-z]+[\s\w]*[.!?]$',  # Sentence ending with punctuation
        r'\w+\s+\w+',  # Multiple words
    ],
    # Patterns to exclude from translation
    'exclude_string_patterns': [
        r'^[A-Z_]+$',  # All caps (likely constants)
        r'^[a-z]+$',  # Single lowercase word (likely identifier)
        r'^[0-9]+$',  # Numbers
        r'^https?://',  # URLs
        r'^/',  # Paths
        r'^\s*$',  # Empty or whitespace
        r'^[a-z]+/[a-z]+$',  # MIME types
        r'^#[0-9a-fA-F]{3,6}$',  # Hex colors
        r'^(true|false|null|none|True|False|None)$',  # Keywords
        r'^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$',  # HTTP methods
        r'^(id|name|email|password|username|token|key|value|type|status)$',  # Common fields
        r'^application/json$',  # Content types
        r'^\w+\.\w+$',  # Module paths
        r'^__\w+__$',  # Python magic methods
    ]
}


class StringExtractor(ast.NodeVisitor):
    """AST visitor to extract string literals from Python code"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.strings: List[Tuple[str, int, int]] = []
        self.current_function = None
        self.current_class = None
        
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Str(self, node):
        # For Python < 3.8
        if hasattr(node, 's'):
            self._process_string(node.s, node.lineno, node.col_offset)
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        # For Python >= 3.8
        if isinstance(node.value, str):
            self._process_string(node.value, node.lineno, node.col_offset)
        self.generic_visit(node)
        
    def _process_string(self, text: str, line: int, col: int):
        if should_translate(text):
            context = []
            if self.current_class:
                context.append(f"class:{self.current_class}")
            if self.current_function:
                context.append(f"func:{self.current_function}")
            self.strings.append((text, line, col, ' '.join(context)))


def should_translate(text: str) -> bool:
    """Check if a string should be translated"""
    # Check exclusion patterns first
    for pattern in CONFIG['exclude_string_patterns']:
        if re.match(pattern, text):
            return False
    
    # Check if it matches translation patterns
    for pattern in CONFIG['translate_patterns']:
        if re.search(pattern, text):
            return True
    
    # Additional heuristics
    if len(text) > 3 and ' ' in text:
        return True
    if len(text) > 10:
        return True
    
    return False


def extract_strings_from_file(filepath: Path) -> List[Dict]:
    """Extract translatable strings from a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content, filename=str(filepath))
        extractor = StringExtractor(str(filepath))
        extractor.visit(tree)
        
        # Also look for specific patterns that AST might miss
        additional_strings = extract_patterns_from_content(content, filepath)
        
        results = []
        for text, line, col, context in extractor.strings:
            results.append({
                'text': text,
                'file': str(filepath.relative_to(CONFIG['src_path'])),
                'line': line,
                'column': col,
                'context': context
            })
            
        results.extend(additional_strings)
        return results
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def extract_patterns_from_content(content: str, filepath: Path) -> List[Dict]:
    """Extract strings using regex patterns"""
    results = []
    
    # Patterns to look for
    patterns = [
        # Flash messages
        (r'flash\([\'"]([^\'\"]+)[\'"]', 'flash_message'),
        # JSON responses with messages
        (r'[\'"]message[\'"]\s*:\s*[\'"]([^\'\"]+)[\'"]', 'api_message'),
        # Error messages
        (r'[\'"]error[\'"]\s*:\s*[\'"]([^\'\"]+)[\'"]', 'error_message'),
        # Return statements with strings
        (r'return\s+[\'"]([A-Z][^\'\"]+)[\'"]', 'return_message'),
        # Raise statements
        (r'raise\s+\w+\([\'"]([^\'\"]+)[\'"]', 'exception_message'),
        # Log messages
        (r'log(?:ger)?\.(?:info|warning|error|debug)\([\'"]([^\'\"]+)[\'"]', 'log_message'),
    ]
    
    lines = content.split('\n')
    for pattern, context_type in patterns:
        for match in re.finditer(pattern, content):
            text = match.group(1)
            if should_translate(text):
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                
                results.append({
                    'text': text,
                    'file': str(filepath.relative_to(CONFIG['src_path'])),
                    'line': line_num,
                    'column': match.start() - content.rfind('\n', 0, match.start()),
                    'context': context_type
                })
    
    return results


def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped"""
    filepath_str = str(filepath)
    for pattern in CONFIG['exclude_patterns']:
        if pattern in filepath_str:
            return True
    return False


def generate_translation_key(text: str, context: str = '') -> str:
    """Generate a suggested translation key"""
    # Clean the text for key generation
    key = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    key = key.lower().replace(' ', '_')[:50]
    
    # Add context prefix if available
    if context:
        if 'api' in context or 'api/' in context:
            prefix = 'api'
        elif 'error' in context or 'exception' in context:
            prefix = 'errors'
        elif 'flash' in context:
            prefix = 'messages'
        elif 'log' in context:
            prefix = 'logs'
        else:
            prefix = 'backend'
        key = f"{prefix}.{key}"
    
    return key


def main():
    """Main function"""
    print("🔍 Extracting hardcoded strings from backend...\n")
    
    # Ensure output directory exists
    CONFIG['output_path'].parent.mkdir(parents=True, exist_ok=True)
    
    # Find all Python files
    all_strings = defaultdict(list)
    strings_by_file = defaultdict(set)
    
    python_files = list(CONFIG['src_path'].rglob('*.py'))
    python_files = [f for f in python_files if not should_skip_file(f)]
    
    print(f"Found {len(python_files)} files to analyze\n")
    
    # Process each file
    for i, filepath in enumerate(python_files):
        if i % 20 == 0:
            print(f"Processing... {round(i / len(python_files) * 100)}%")
            
        strings = extract_strings_from_file(filepath)
        for string_data in strings:
            text = string_data['text']
            all_strings[text].append({
                'file': string_data['file'],
                'line': string_data['line'],
                'column': string_data['column'],
                'context': string_data.get('context', '')
            })
            strings_by_file[string_data['file']].add(text)
    
    print("\n✅ Analysis complete!\n")
    
    # Generate report
    report = {
        'summary': {
            'totalStrings': len(all_strings),
            'totalFiles': len(strings_by_file),
            'timestamp': str(Path(__file__).stat().st_ctime),
        },
        'strings': {},
        'byFile': {},
        'suggestedKeys': {}
    }
    
    # Add strings with their locations
    for text, locations in all_strings.items():
        report['strings'][text] = {
            'occurrences': len(locations),
            'locations': locations
        }
        
        # Generate suggested key
        first_location = locations[0]
        report['suggestedKeys'][text] = generate_translation_key(
            text, 
            first_location.get('context', '')
        )
    
    # Add file summary
    for filepath, strings in strings_by_file.items():
        report['byFile'][filepath] = list(strings)
    
    # Sort strings by occurrence count
    sorted_strings = sorted(
        report['strings'].items(),
        key=lambda x: x[1]['occurrences'],
        reverse=True
    )
    
    # Write report
    with open(CONFIG['output_path'], 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("📊 Summary:")
    print(f"- Total unique strings found: {len(all_strings)}")
    print(f"- Files with hardcoded strings: {len(strings_by_file)}")
    print(f"- Report saved to: {CONFIG['output_path']}\n")
    
    # Show top 10 most common strings
    print("🔝 Top 10 most common strings:")
    for text, data in sorted_strings[:10]:
        print(f'  "{text}" - {data["occurrences"]} occurrences')
    
    # Show files with most strings
    files_sorted = sorted(
        strings_by_file.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:10]
    
    print("\n📁 Files with most hardcoded strings:")
    for filepath, strings in files_sorted:
        print(f"  {filepath} - {len(strings)} strings")


if __name__ == '__main__':
    main()