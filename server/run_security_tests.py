#!/usr/bin/env python
"""Run security-specific tests for the BDC application."""

import pytest
import os
import sys
import shutil


def enable_security_tests():
    """Enable disabled security test files by removing .disabled extension."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    tests_dir = os.path.join(project_root, 'tests')
    
    # List of disabled security test files
    disabled_files = [
        os.path.join(tests_dir, 'test_security_encryption.py.disabled')
    ]
    
    for disabled_file in disabled_files:
        if os.path.exists(disabled_file):
            enabled_file = disabled_file.replace('.disabled', '')
            shutil.copy(disabled_file, enabled_file)
            print(f"Enabled test file: {enabled_file}")


def main():
    """Run security tests."""
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    
    # Enable disabled security tests
    enable_security_tests()
    
    # Run pytest with specified args
    args = [
        '-xvs',
        '--cov=app',
        '--cov-report=term',
        '--cov-report=html:security_coverage_html',
        'tests/test_security*.py',
        'tests/test_security_*.py',
    ]
    
    exit_code = pytest.main(args)
    
    # Clean up - remove temporary enabled files
    tests_dir = os.path.join(project_root, 'tests')
    if os.path.exists(os.path.join(tests_dir, 'test_security_encryption.py')):
        os.remove(os.path.join(tests_dir, 'test_security_encryption.py'))
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()