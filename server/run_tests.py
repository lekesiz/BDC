#!/usr/bin/env python
"""Run all tests for the BDC application."""

import pytest
import os
import sys


def main():
    """Run all tests."""
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    
    # Run pytest with specified args
    args = [
        '-xvs',  # verbose, stop on first failure
        '--cov=app',  # coverage for app directory
        '--cov-report=term',  # terminal coverage report
        '--cov-report=html:coverage_html',  # HTML coverage report
        'tests'  # test directory
    ]
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()