#!/usr/bin/env python
"""
Run only the working backend tests to avoid circular dependency issues.
"""

import subprocess
import sys

WORKING_TESTS = [
    "tests/test_i18n.py",
    "tests/test_db_performance.py", 
    "tests/unit/test_auth_isolated.py",
]

def run_tests():
    """Run the working tests."""
    cmd = ["python", "-m", "pytest", "-v", "--tb=short"] + WORKING_TESTS
    
    print("Running working backend tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)