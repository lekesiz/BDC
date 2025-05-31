#!/usr/bin/env python3
"""Script to generate tests for uncovered code areas."""

import os
import subprocess
import re


def get_coverage_report():
    """Run pytest with coverage and get detailed report."""
    cmd = ['python', '-m', 'pytest', '--cov=app', '--cov-report=term-missing', '-q']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def parse_coverage_report(report):
    """Parse coverage report to find files with low coverage."""
    lines = report.split('\n')
    low_coverage_files = []
    
    for line in lines:
        # Match lines with coverage percentage
        match = re.match(r'app/(.*?)\s+\d+\s+\d+\s+(\d+)%', line)
        if match:
            file_path = match.group(1)
            coverage = int(match.group(2))
            if coverage < 50:  # Files with less than 50% coverage
                low_coverage_files.append((file_path, coverage))
    
    return sorted(low_coverage_files, key=lambda x: x[1])


def generate_test_template(file_path):
    """Generate test template for a given file."""
    module_path = file_path.replace('/', '.').replace('.py', '')
    module_name = file_path.split('/')[-1].replace('.py', '')
    
    test_content = f'''"""Tests for {module_path} to increase coverage."""

import pytest
from unittest.mock import Mock, patch
from app.{module_path} import *  # Import all from the module


class Test{module_name.title().replace("_", "")}:
    """Test {module_name} functions and classes."""
    
    def test_imports(self):
        """Test that module can be imported."""
        from app.{module_path} import *
        assert True  # Module imported successfully
    
    # TODO: Add specific tests for functions and classes in this module
    # Use the coverage report to identify untested lines and methods


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''
    
    return test_content


def main():
    """Main function to generate tests."""
    print("Running coverage analysis...")
    report = get_coverage_report()
    
    print("\nParsing coverage report...")
    low_coverage_files = parse_coverage_report(report)
    
    print(f"\nFound {len(low_coverage_files)} files with low coverage:")
    for file_path, coverage in low_coverage_files[:10]:  # Show top 10
        print(f"  - {file_path}: {coverage}%")
    
    # Generate tests for the lowest coverage files
    test_dir = '/Users/mikail/Desktop/BDC/server/tests/generated'
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"\nGenerating test templates in {test_dir}...")
    for file_path, coverage in low_coverage_files[:5]:  # Generate for top 5
        if not file_path.endswith('.py'):
            continue
        
        test_name = f"test_{file_path.replace('/', '_')}"
        test_path = os.path.join(test_dir, test_name)
        
        if not os.path.exists(test_path):
            content = generate_test_template(file_path)
            with open(test_path, 'w') as f:
                f.write(content)
            print(f"  Created: {test_name}")
    
    print("\nDone! Review the generated test templates and implement specific tests.")


if __name__ == '__main__':
    main()