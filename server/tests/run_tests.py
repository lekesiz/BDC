#!/usr/bin/env python3
"""Consolidated test runner for BDC project."""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests(test_type=None, verbose=False, coverage=False, parallel=False):
    """Run tests based on type and options."""
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    # Add coverage if requested
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    # Add parallel execution if requested
    if parallel:
        cmd.extend(['-n', 'auto'])  # Requires pytest-xdist
    
    # Select test type
    if test_type == 'unit':
        cmd.append('tests/unit/')
        cmd.extend(['-m', 'unit'])
    elif test_type == 'integration':
        cmd.append('tests/integration/')
        cmd.extend(['-m', 'integration'])
    elif test_type == 'e2e':
        cmd.append('tests/e2e/')
        cmd.extend(['-m', 'e2e'])
    elif test_type == 'performance':
        cmd.append('tests/performance/')
        cmd.extend(['-m', 'performance'])
    elif test_type == 'security':
        cmd.append('tests/security/')
        cmd.extend(['-m', 'security'])
    elif test_type == 'auth':
        cmd.extend(['-m', 'auth'])
    elif test_type == 'api':
        cmd.extend(['-m', 'api'])
    elif test_type == 'fast':
        cmd.extend(['-m', 'not slow'])
    elif test_type == 'slow':
        cmd.extend(['-m', 'slow'])
    else:
        # Run all tests
        cmd.append('tests/')
    
    # Add common options
    cmd.extend(['--tb=short', '--color=yes'])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Execute tests
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def list_test_structure():
    """List the current test structure."""
    tests_dir = Path(__file__).parent
    
    print("Current Test Structure:")
    print("=" * 50)
    
    for root, dirs, files in os.walk(tests_dir):
        # Skip archive and __pycache__ directories
        dirs[:] = [d for d in dirs if d not in ['archive', '__pycache__', '.pytest_cache']]
        
        level = root.replace(str(tests_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                print(f"{subindent}{file}")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='BDC Test Runner')
    
    parser.add_argument(
        'test_type',
        nargs='?',
        choices=['unit', 'integration', 'e2e', 'performance', 'security', 
                'auth', 'api', 'fast', 'slow', 'all'],
        default='all',
        help='Type of tests to run'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='Run with coverage analysis'
    )
    
    parser.add_argument(
        '-p', '--parallel',
        action='store_true',
        help='Run tests in parallel (requires pytest-xdist)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List test structure'
    )
    
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install test dependencies'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_test_structure()
        return 0
    
    if args.install_deps:
        print("Installing test dependencies...")
        deps = [
            'pytest>=6.0',
            'pytest-cov',
            'pytest-xdist',
            'pytest-mock',
            'pytest-flask'
        ]
        
        for dep in deps:
            try:
                subprocess.run(['pip', 'install', dep], check=True)
                print(f"✓ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {dep}")
        
        return 0
    
    # Check if we're in the right directory
    if not (project_root / 'app').exists():
        print("Error: Run this script from the server directory")
        return 1
    
    # Run tests
    test_type = args.test_type if args.test_type != 'all' else None
    return run_tests(
        test_type=test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )


if __name__ == '__main__':
    sys.exit(main())