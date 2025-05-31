"""Script to run refactored auth tests and show coverage improvement."""

import subprocess
import sys
import pytest; pytest.skip("Refactored tests runner – skip in CI", allow_module_level=True)


def run_coverage_report():
    """Run coverage report for refactored auth components."""
    print("Running tests for refactored auth components...")
    print("=" * 50)
    
    # Run tests with coverage
    test_files = [
        "tests/test_auth_service_refactored.py",
        "tests/test_auth_api_refactored.py"
    ]
    
    coverage_modules = [
        "app.services.auth_service_refactored",
        "app.api.auth_refactored",
        "app.container",
        "app.repositories.user_repository"
    ]
    
    # Run pytest with coverage
    cmd = [
        "coverage", "run", "-m", "pytest", "-v"
    ] + test_files
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\nTests failed!")
        return
    
    print("\n" + "=" * 50)
    print("Coverage Report for Refactored Components:")
    print("=" * 50)
    
    # Generate coverage report
    coverage_cmd = ["coverage", "report", "--include=" + ",".join(coverage_modules)]
    subprocess.run(coverage_cmd)
    
    print("\n" + "=" * 50)
    print("Key Improvements:")
    print("=" * 50)
    print("1. Dependency Injection enables easy mocking")
    print("2. Repository pattern separates data access from business logic")
    print("3. Service interfaces define clear contracts")
    print("4. All components are independently testable")
    print("5. No need for database fixtures or complex setup")
    print("\nThis architecture makes it easier to achieve 70%+ test coverage!")


if __name__ == "__main__":
    try:
        run_coverage_report()
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)